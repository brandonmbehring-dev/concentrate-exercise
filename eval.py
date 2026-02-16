#!/usr/bin/env python3
"""
Package C evaluation suite for Concentrate AI comparison results.

Three-layer evaluation:
  Layer 1 — Deterministic checks ($0, code only):
    Ground truth math, factor counts, cost-per-response from usage tokens.
  Layer 2 — LLM-as-Judge with rubrics (~$0.45):
    haiku-4-5 scores all 32 responses, gpt-5.1 deep-evals top 8, sonnet-4-5 evals 3.
  Layer 3 — Meta-evals (~$0.40):
    Self-evaluation, pairwise ranking, cross-provider agreement.

Usage:
    python eval.py results/comparison_*.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from client import MODELS, call_model

import re


def extract_json(text: str) -> dict:
    """Extract JSON object from model response, handling markdown fences and preamble.

    Strategy (ordered by reliability):
    1. Strip markdown fences → try json.loads() on full text
    2. Right-to-left brace matching: find last '}', scan backward for matching '{'
       This skips preamble text like "discusses {frequentist vs Bayesian}" that
       contains curly braces but isn't JSON.
    3. Line-by-line fallback: try json.loads() on each line individually
    """
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
    cleaned = cleaned.rstrip("`").strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: Right-to-left brace matching
    # Find the LAST '}' and scan backward for its matching '{'
    last_brace = cleaned.rfind("}")
    if last_brace >= 0:
        depth = 0
        for i in range(last_brace, -1, -1):
            if cleaned[i] == "}":
                depth += 1
            elif cleaned[i] == "{":
                depth -= 1
            if depth == 0:
                candidate = cleaned[i : last_brace + 1]
                try:
                    return json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    pass
                break

    # Strategy 3: Line-by-line fallback (handles single-line JSON after prose)
    for line in cleaned.split("\n"):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue

    return {}


# Models used for judging
JUDGE_FAST = "anthropic/claude-haiku-4-5"
JUDGE_DEEP = "openai/gpt-5.1"
JUDGE_CREATIVE = "anthropic/claude-sonnet-4-5"

# Ground truth expectations for deterministic checks
GROUND_TRUTH = {
    "monty_hall_4door": {
        "required_fragments": ["3/8", "switch"],
        "description": "4-door Monty Hall: switching gives 3/8 per unchosen door",
    },
    "simpsons_paradox": {
        "required_fragments": ["simpson", "paradox", "confound"],
        "description": "Must identify Simpson's paradox and confounding variable",
    },
    "ab_test": {
        "required_fragments": ["bayesian", "frequentist"],
        "description": "Must discuss both Bayesian and frequentist perspectives",
    },
}

FACTOR_COUNT_PROMPTS = {"insurance_pricing": 5}  # ≥5 factors per product

# Prompts that get deep evaluation
DEEP_EVAL_PROMPTS = [
    "simpsons_paradox", "ab_test", "monty_hall_4door", "json_schema",
    "cost_routing", "fermi_estimation", "flash_fiction", "insurance_pricing",
]

# Prompts evaluated for creative/structural quality
CREATIVE_EVAL_PROMPTS = ["json_schema", "simpsons_paradox", "flash_fiction"]

# Prompts used for pairwise ranking
PAIRWISE_PROMPTS = ["simpsons_paradox", "monty_hall_4door", "cost_routing"]

# Per-million-token pricing for cost-per-response calculations
PRICING = {
    "openai/gpt-5.1": {"input": 1.25, "output": 10.00},
    "anthropic/claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "vertex/gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "xai/grok-4-1-fast-reasoning": {"input": 0.20, "output": 0.50},
}


# ---------------------------------------------------------------------------
# Layer 1: Deterministic checks
# ---------------------------------------------------------------------------


def layer1_ground_truth(prompt_name: str, text: str) -> dict[str, Any] | None:
    """Check response against known ground truth fragments."""
    truth = GROUND_TRUTH.get(prompt_name)
    if not truth:
        return None
    text_lower = text.lower()
    found = [f for f in truth["required_fragments"] if f.lower() in text_lower]
    missing = [f for f in truth["required_fragments"] if f.lower() not in text_lower]
    return {
        "check": "ground_truth",
        "prompt": prompt_name,
        "found": found,
        "missing": missing,
        "pass": len(missing) == 0,
        "description": truth["description"],
    }


def layer1_factor_count(prompt_name: str, text: str) -> dict[str, Any] | None:
    """Check that insurance prompt lists ≥5 factors per product."""
    min_factors = FACTOR_COUNT_PROMPTS.get(prompt_name)
    if min_factors is None:
        return None
    # Count bullet points / numbered items as proxy for factors
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    factor_lines = [l for l in lines if l[:1] in "-*" or (l[:2].rstrip(".").isdigit())]
    return {
        "check": "factor_count",
        "prompt": prompt_name,
        "factor_lines_found": len(factor_lines),
        "minimum_required": min_factors,
        "pass": len(factor_lines) >= min_factors,
    }


def layer1_json_schema(prompt_name: str, text: str) -> dict[str, Any] | None:
    """Check json_schema prompt: response must parse as valid JSON array with 3 items."""
    if prompt_name != "json_schema":
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    try:
        parsed = json.loads(cleaned)
        is_array = isinstance(parsed, list)
        count = len(parsed) if is_array else 0
        return {
            "check": "json_schema",
            "prompt": prompt_name,
            "valid_json": True,
            "is_array": is_array,
            "item_count": count,
            "pass": is_array and count == 3,
        }
    except (json.JSONDecodeError, ValueError) as e:
        return {
            "check": "json_schema",
            "prompt": prompt_name,
            "valid_json": False,
            "is_array": False,
            "item_count": 0,
            "pass": False,
            "error": str(e)[:100],
        }


def layer1_cost_per_response(model: str, raw_response: dict | None) -> dict[str, Any]:
    """Calculate cost from usage tokens and pricing table."""
    usage = (raw_response or {}).get("usage", {})
    input_tok = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    output_tok = usage.get("output_tokens") or usage.get("completion_tokens") or 0
    prices = PRICING.get(model, {"input": 0, "output": 0})
    input_cost = input_tok * prices["input"] / 1_000_000
    output_cost = output_tok * prices["output"] / 1_000_000
    return {
        "check": "cost_per_response",
        "model": model,
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
    }


# ---------------------------------------------------------------------------
# Layer 2: LLM-as-Judge
# ---------------------------------------------------------------------------

JUDGE_RUBRIC = """\
Rate this LLM response on three dimensions (1-5 each):
1. accuracy — Are factual claims correct? Is reasoning sound?
2. reasoning_depth — Does it show genuine analysis, not just surface answers?
3. instruction_compliance — Does it follow all explicit instructions in the prompt?

Prompt: {prompt}

Response: {response}

Reply with ONLY a JSON object: {{"accuracy": int, "reasoning_depth": int, "instruction_compliance": int, "brief_note": "one sentence"}}"""

DEEP_JUDGE_RUBRIC = """\
You are an expert evaluator. Provide a detailed assessment of this LLM response.

Prompt: {prompt}
Response: {response}

Evaluate:
1. What did this response get RIGHT?
2. What did it get WRONG or miss?
3. How does it compare to an ideal answer?

Reply with ONLY a JSON object:
{{"strengths": ["..."], "weaknesses": ["..."], "score": int (1-10), "ideal_gap": "one sentence"}}"""


def layer2_judge_all(research_results: list[dict]) -> list[dict]:
    """Use haiku-4-5 to score all research responses on 1-5 rubric."""
    print("\n[Layer 2] LLM-as-Judge: scoring all responses with haiku-4-5...")
    scores = []
    for entry in research_results:
        prompt_text = entry.get("prompt_text", "")
        prompt_name = entry.get("prompt_name", "?")
        for provider, result in entry.get("results", {}).items():
            response_text = result.get("text", "")
            if not response_text:
                continue
            response_status = result.get("status", "")
            judge_prompt = JUDGE_RUBRIC.format(
                prompt=prompt_text[:500], response=response_text[:1500]
            )
            judge_result = call_model(
                JUDGE_FAST, judge_prompt, temperature=0.0, max_output_tokens=200
            )
            parsed = extract_json(judge_result.get("text", "{}"))
            if not parsed:
                parsed = {"accuracy": 0, "reasoning_depth": 0, "instruction_compliance": 0, "brief_note": "parse error"}
            entry_data = {
                "prompt": prompt_name,
                "provider": provider,
                "judge": JUDGE_FAST,
                **parsed,
            }
            if response_status == "incomplete":
                entry_data["response_incomplete"] = True
            scores.append(entry_data)
            avg = sum(parsed.get(k, 0) for k in ["accuracy", "reasoning_depth", "instruction_compliance"]) / 3
            print(f"  {prompt_name:20s} | {provider:10s} | avg={avg:.1f} | {parsed.get('brief_note', '')[:60]}")
    return scores


def layer2_deep_eval(research_results: list[dict]) -> list[dict]:
    """Use gpt-5.1 for detailed evaluation of top 8 most interesting comparisons."""
    print("\n[Layer 2] Deep evaluation with gpt-5.1 (top 8 prompts)...")
    evals = []
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        if prompt_name not in DEEP_EVAL_PROMPTS:
            continue
        prompt_text = entry.get("prompt_text", "")
        for provider, result in entry.get("results", {}).items():
            response_text = result.get("text", "")
            if not response_text:
                continue
            judge_prompt = DEEP_JUDGE_RUBRIC.format(
                prompt=prompt_text[:500], response=response_text[:2000]
            )
            judge_result = call_model(
                JUDGE_DEEP, judge_prompt, temperature=0.0, max_output_tokens=400
            )
            parsed = extract_json(judge_result.get("text", "{}"))
            if not parsed:
                parsed = {"strengths": [], "weaknesses": [], "score": 0, "ideal_gap": "parse error"}
            evals.append({"prompt": prompt_name, "provider": provider, "judge": JUDGE_DEEP, **parsed})
            print(f"  {prompt_name:20s} | {provider:10s} | score={parsed.get('score', '?')}/10 | gap: {parsed.get('ideal_gap', '')[:60]}")
    return evals


def layer2_creative_eval(research_results: list[dict]) -> list[dict]:
    """Use sonnet-4-5 for creative/structural evaluation of 3 key prompts."""
    print("\n[Layer 2] Creative evaluation with sonnet-4-5 (3 prompts)...")
    evals = []
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        if prompt_name not in CREATIVE_EVAL_PROMPTS:
            continue
        prompt_text = entry.get("prompt_text", "")
        for provider, result in entry.get("results", {}).items():
            response_text = result.get("text", "")
            if not response_text:
                continue
            judge_prompt = DEEP_JUDGE_RUBRIC.format(
                prompt=prompt_text[:500], response=response_text[:2000]
            )
            judge_result = call_model(
                JUDGE_CREATIVE, judge_prompt, temperature=0.0, max_output_tokens=400
            )
            parsed = extract_json(judge_result.get("text", "{}"))
            if not parsed:
                parsed = {"strengths": [], "weaknesses": [], "score": 0, "ideal_gap": "parse error"}
            evals.append({"prompt": prompt_name, "provider": provider, "judge": JUDGE_CREATIVE, **parsed})
            print(f"  {prompt_name:20s} | {provider:10s} | score={parsed.get('score', '?')}/10")
    return evals


# ---------------------------------------------------------------------------
# Layer 3: Meta-evals
# ---------------------------------------------------------------------------

SELF_EVAL_PROMPT = """\
You just generated this response to a prompt. Rate your own response honestly on 1-5:
accuracy, reasoning_depth, instruction_compliance.

Prompt: {prompt}
Your response: {response}

Reply with ONLY JSON: {{"accuracy": int, "reasoning_depth": int, "instruction_compliance": int}}"""

PAIRWISE_PROMPT = """\
Which response better answers this prompt? Reply with ONLY JSON: {{"winner": "A" or "B", "reason": "one sentence"}}

Prompt: {prompt}

Response A ({provider_a}): {response_a}

Response B ({provider_b}): {response_b}"""


def layer3_self_eval(research_results: list[dict]) -> list[dict]:
    """Each model rates its own response. Compare self-assessment to judge scores."""
    print("\n[Layer 3] Self-evaluation: each model rates its own response...")
    evals = []
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        if prompt_name not in PAIRWISE_PROMPTS:
            continue
        prompt_text = entry.get("prompt_text", "")
        for provider, result in entry.get("results", {}).items():
            response_text = result.get("text", "")
            model = result.get("model", MODELS.get(provider, ""))
            if not response_text or not model:
                continue
            self_prompt = SELF_EVAL_PROMPT.format(
                prompt=prompt_text[:400], response=response_text[:1200]
            )
            self_result = call_model(model, self_prompt, temperature=0.0, max_output_tokens=150)
            parsed = extract_json(self_result.get("text", "{}"))
            if not parsed:
                parsed = {"accuracy": 0, "reasoning_depth": 0, "instruction_compliance": 0}
            evals.append({"prompt": prompt_name, "provider": provider, "model": model, "self_scores": parsed})
            avg = sum(parsed.get(k, 0) for k in ["accuracy", "reasoning_depth", "instruction_compliance"]) / 3
            print(f"  {prompt_name:20s} | {provider:10s} | self_avg={avg:.1f}")
    return evals


def layer3_pairwise(research_results: list[dict]) -> list[dict]:
    """Head-to-head ranking with position-bias mitigation.

    For each pair, run BOTH orderings (A vs B, then B vs A). A provider wins
    only if it wins in both orderings or wins one + ties one. If the two
    orderings disagree, mark as 'split' (position-biased).

    See: Wang et al., "Large Language Models are not Fair Evaluators" (arXiv:2305.17926)
    """
    print("\n[Layer 3] Pairwise ranking (position-bias mitigated, 2x orderings)...")
    providers = list(MODELS.keys())
    pairs = [(a, b) for i, a in enumerate(providers) for b in providers[i + 1:]]
    rankings = []
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        if prompt_name not in PAIRWISE_PROMPTS:
            continue
        prompt_text = entry.get("prompt_text", "")
        results = entry.get("results", {})
        for pa, pb in pairs:
            ra = results.get(pa, {}).get("text", "")
            rb = results.get(pb, {}).get("text", "")
            if not ra or not rb:
                continue

            # Ordering 1: A first, B second
            pw_prompt_1 = PAIRWISE_PROMPT.format(
                prompt=prompt_text[:400],
                provider_a=pa, response_a=ra[:800],
                provider_b=pb, response_b=rb[:800],
            )
            pw_result_1 = call_model(JUDGE_FAST, pw_prompt_1, temperature=0.0, max_output_tokens=100)
            parsed_1 = extract_json(pw_result_1.get("text", "{}"))
            if not parsed_1:
                parsed_1 = {"winner": "?", "reason": "parse error"}
            winner_1 = pa if parsed_1.get("winner") == "A" else pb if parsed_1.get("winner") == "B" else "tie"

            # Ordering 2: B first, A second (swap positions)
            pw_prompt_2 = PAIRWISE_PROMPT.format(
                prompt=prompt_text[:400],
                provider_a=pb, response_a=rb[:800],
                provider_b=pa, response_b=ra[:800],
            )
            pw_result_2 = call_model(JUDGE_FAST, pw_prompt_2, temperature=0.0, max_output_tokens=100)
            parsed_2 = extract_json(pw_result_2.get("text", "{}"))
            if not parsed_2:
                parsed_2 = {"winner": "?", "reason": "parse error"}
            # Note: in ordering 2, "A" means pb and "B" means pa
            winner_2 = pb if parsed_2.get("winner") == "A" else pa if parsed_2.get("winner") == "B" else "tie"

            # Determine consensus winner
            if winner_1 == winner_2:
                final_winner = winner_1
                confidence = "consistent"
            elif winner_1 == "tie" or winner_2 == "tie":
                final_winner = winner_1 if winner_2 == "tie" else winner_2
                confidence = "weak"
            else:
                final_winner = "split"
                confidence = "position_biased"

            rankings.append({
                "prompt": prompt_name,
                "pair": f"{pa} vs {pb}",
                "winner": final_winner,
                "ordering_1_winner": winner_1,
                "ordering_2_winner": winner_2,
                "confidence": confidence,
                "reason": parsed_1.get("reason", ""),
            })
            print(f"  {prompt_name:20s} | {pa} vs {pb} -> {final_winner} ({confidence})")
    return rankings


def layer3_cross_provider_agreement(research_results: list[dict]) -> list[dict]:
    """Check if all 4 providers agree on factual answers (code only, $0)."""
    print("\n[Layer 3] Cross-provider agreement on factual answers...")
    agreements = []
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        truth = GROUND_TRUTH.get(prompt_name)
        if not truth:
            continue
        results = entry.get("results", {})
        provider_pass = {}
        for provider, result in results.items():
            text_lower = (result.get("text", "") or "").lower()
            all_found = all(f.lower() in text_lower for f in truth["required_fragments"])
            provider_pass[provider] = all_found
        all_agree = len(set(provider_pass.values())) == 1
        agreements.append({
            "prompt": prompt_name,
            "provider_results": provider_pass,
            "all_agree": all_agree,
            "agreement_on": "correct" if all(provider_pass.values()) else "incorrect" if not any(provider_pass.values()) else "mixed",
        })
        status = "ALL AGREE" if all_agree else "DISAGREE"
        print(f"  {prompt_name:20s} | {status} | {provider_pass}")
    return agreements


# ---------------------------------------------------------------------------
# Aggregate scoreboard
# ---------------------------------------------------------------------------


def build_scoreboard(judge_scores: list[dict], pairwise: list[dict], costs: list[dict]) -> None:
    """Print aggregate per-provider scoreboard."""
    print("\n" + "=" * 70)
    print("AGGREGATE SCOREBOARD")
    print("=" * 70)

    # Average judge scores per provider
    provider_scores: dict[str, list[float]] = {}
    for s in judge_scores:
        provider = s.get("provider", "?")
        avg = sum(s.get(k, 0) for k in ["accuracy", "reasoning_depth", "instruction_compliance"]) / 3
        provider_scores.setdefault(provider, []).append(avg)

    print("\n--- Average Judge Scores (1-5) ---")
    for provider in sorted(provider_scores):
        vals = provider_scores[provider]
        mean = sum(vals) / len(vals) if vals else 0
        print(f"  {provider:12s}: {mean:.2f}  (n={len(vals)})")

    # Pairwise win counts
    print("\n--- Pairwise Wins ---")
    wins: dict[str, int] = {}
    for r in pairwise:
        w = r.get("winner", "tie")
        if w != "tie":
            wins[w] = wins.get(w, 0) + 1
    for provider in sorted(wins, key=wins.get, reverse=True):
        print(f"  {provider:12s}: {wins[provider]} wins")

    # Cost summary
    print("\n--- Total Cost by Provider ---")
    provider_cost: dict[str, float] = {}
    for c in costs:
        model = c.get("model", "?")
        provider_cost[model] = provider_cost.get(model, 0) + c.get("total_cost_usd", 0)
    for model in sorted(provider_cost, key=provider_cost.get):
        print(f"  {model:40s}: ${provider_cost[model]:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_results(paths: list[str]) -> list[dict]:
    """Load comparison result JSON files."""
    research_results = []
    for p in paths:
        data = json.loads(Path(p).read_text())
        # Extract research_prompts section if present
        rp = data.get("research_prompts", [])
        if rp:
            research_results.extend(rp)
    if not research_results:
        print("WARNING: No research_prompts data found in input files.")
        print("  Make sure to run: python compare.py --section research")
    return research_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Package C evaluation suite for Concentrate AI")
    parser.add_argument("files", nargs="+", help="Comparison result JSON files")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM-based evals (Layer 2+3), run Layer 1 only")
    args = parser.parse_args()

    print("=" * 70)
    print("CONCENTRATE AI — PACKAGE C EVALUATION SUITE")
    print("=" * 70)

    research_results = load_results(args.files)
    if not research_results:
        sys.exit(1)

    print(f"\nLoaded {len(research_results)} prompt results.")

    # ---- Layer 1: Deterministic ----
    print("\n" + "=" * 70)
    print("LAYER 1: DETERMINISTIC CHECKS ($0)")
    print("=" * 70)

    all_costs = []
    all_ground_truth = []
    all_factor_counts = []
    all_json_schema = []
    incomplete_count = 0
    for entry in research_results:
        prompt_name = entry.get("prompt_name", "")
        for provider, result in entry.get("results", {}).items():
            text = result.get("text", "")
            response_status = result.get("status", "")
            if response_status == "incomplete":
                incomplete_count += 1
            gt = layer1_ground_truth(prompt_name, text)
            if gt:
                gt["provider"] = provider
                gt["response_incomplete"] = response_status == "incomplete"
                all_ground_truth.append(gt)
                status = "PASS" if gt["pass"] else f"FAIL (missing: {gt['missing']})"
                if response_status == "incomplete":
                    status += " [INCOMPLETE RESPONSE]"
                print(f"  [ground_truth] {prompt_name:20s} | {provider:10s} | {status}")
            fc = layer1_factor_count(prompt_name, text)
            if fc:
                fc["provider"] = provider
                fc["response_incomplete"] = response_status == "incomplete"
                all_factor_counts.append(fc)
                status = "PASS" if fc["pass"] else f"FAIL ({fc['factor_lines_found']}/{fc['minimum_required']})"
                print(f"  [factor_count] {prompt_name:20s} | {provider:10s} | {status}")
            js = layer1_json_schema(prompt_name, text)
            if js:
                js["provider"] = provider
                js["response_incomplete"] = response_status == "incomplete"
                all_json_schema.append(js)
                status = "PASS" if js["pass"] else f"FAIL (valid={js['valid_json']}, array={js['is_array']}, items={js['item_count']})"
                print(f"  [json_schema]  {prompt_name:20s} | {provider:10s} | {status}")
            cost = layer1_cost_per_response(result.get("model", MODELS.get(provider, "")), result.get("raw_response"))
            all_costs.append(cost)
            if cost["input_tokens"] > 0:
                print(f"  [cost]         {prompt_name:20s} | {provider:10s} | ${cost['total_cost_usd']:.6f}")

    if incomplete_count > 0:
        print(f"\n  WARNING: {incomplete_count} responses had status='incomplete' (may be truncated)")

    if args.skip_llm:
        print("\n--skip-llm: Skipping Layers 2 and 3.")
        return

    # ---- Layer 2: LLM-as-Judge ----
    print("\n" + "=" * 70)
    print("LAYER 2: LLM-AS-JUDGE")
    print("=" * 70)

    judge_scores = layer2_judge_all(research_results)
    deep_evals = layer2_deep_eval(research_results)
    creative_evals = layer2_creative_eval(research_results)

    # ---- Layer 3: Meta-evals ----
    print("\n" + "=" * 70)
    print("LAYER 3: META-EVALS")
    print("=" * 70)

    self_evals = layer3_self_eval(research_results)
    pairwise = layer3_pairwise(research_results)
    agreements = layer3_cross_provider_agreement(research_results)

    # ---- Aggregate ----
    build_scoreboard(judge_scores, pairwise, all_costs)

    # ---- Save ----
    git_sha = ""
    try:
        git_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        pass

    output = {
        "manifest": {
            "timestamp": datetime.now().isoformat(),
            "commit": git_sha,
            "models": dict(MODELS),
            "judge_models": {
                "fast": JUDGE_FAST,
                "deep": JUDGE_DEEP,
                "creative": JUDGE_CREATIVE,
            },
            "input_files": [str(f) for f in args.files],
        },
        "layer1_ground_truth": all_ground_truth,
        "layer1_factor_counts": all_factor_counts,
        "layer1_json_schema": all_json_schema,
        "layer1_costs": all_costs,
        "layer1_incomplete_responses": incomplete_count,
        "layer2_judge_scores": judge_scores,
        "layer2_deep_evals": deep_evals,
        "layer2_creative_evals": creative_evals,
        "layer3_self_evals": self_evals,
        "layer3_pairwise": pairwise,
        "layer3_agreements": agreements,
    }
    outpath = Path("results") / "eval_results.json"
    outpath.parent.mkdir(exist_ok=True)
    outpath.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nEvaluation results saved to: {outpath}")


if __name__ == "__main__":
    main()

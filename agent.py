#!/usr/bin/env python3
"""
Multi-step tool-calling agent using the Concentrate AI unified API.

Demonstrates a research agent that routes each step to a different provider:
1. PLAN     (Anthropic) — structured planning, strong instruction following
2. RESEARCH (xAI)       — cheapest provider ($0.20/$0.50), shows cost optimization
3. COMPARE  (OpenAI)    — strong at structured comparison
4. SYNTHESIZE (Google)   — capable synthesis and summarization

This 4-provider routing is the core value prop: each step uses the provider
best-suited to that task type, all through a single API.

Usage:
    python agent.py
    python agent.py --question "Compare Python and Rust for ML systems"
    python agent.py --all-questions   # Run both default questions
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from client import MODELS, call_model

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Route different agent steps to different providers
# Each role assigned to a different provider to demonstrate cross-provider routing
PLANNER_MODEL = MODELS["anthropic"]     # Best at structured planning
RESEARCHER_MODEL = MODELS["xai"]        # Cheapest — $0.20/$0.50 per 1M tokens
COMPARATOR_MODEL = MODELS["openai"]     # Strong at structured comparison
SYNTHESIZER_MODEL = MODELS["google"]    # Capable synthesis

# Default questions — chosen to produce interesting multi-step results
DEFAULT_QUESTIONS = [
    (
        "Compare strategies for reducing LLM costs in production without "
        "sacrificing quality. Include routing optimization, prompt engineering, "
        "caching, and model selection."
    ),
    (
        "Design a framework for validating LLM outputs in financial services, "
        "where errors could cause regulatory penalties. Include quality metrics, "
        "human-in-the-loop design, and failure modes."
    ),
]


# ---------------------------------------------------------------------------
# Tools the agent can use
# ---------------------------------------------------------------------------

AGENT_TOOLS = [
    {
        "type": "function",
        "strict": False,
        "name": "analyze_topic",
        "description": (
            "Analyze a specific sub-topic and return structured findings. "
            "Use this to research individual aspects of a complex question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific sub-topic to analyze",
                },
                "aspects": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific aspects to cover",
                },
            },
            "required": ["topic"],
        },
    },
    {
        "type": "function",
        "strict": False,
        "name": "compare_options",
        "description": "Compare two or more options along specified dimensions.",
        "parameters": {
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Options to compare",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to compare along (e.g., 'performance', 'ease of use')",
                },
            },
            "required": ["options", "dimensions"],
        },
    },
]


def execute_tool(name: str, arguments: str) -> str:
    """
    Execute a tool call by routing to a different provider (OpenAI).

    In a real agent, these would call external APIs or databases. Here we
    use a second LLM call routed to a DIFFERENT provider than the planner,
    demonstrating Concentrate's cross-provider routing capability.
    """
    try:
        args = json.loads(arguments)
    except (json.JSONDecodeError, ValueError) as e:
        return f"[Error parsing tool arguments: {e}]"

    if name == "analyze_topic":
        topic = args["topic"]
        aspects = args.get("aspects", ["key points", "tradeoffs"])
        prompt = (
            f"Provide a concise, factual analysis of: {topic}\n"
            f"Cover these aspects: {', '.join(aspects)}\n"
            f"Be specific and quantitative where possible. Max 3 bullet points per aspect."
        )
        result = call_model(RESEARCHER_MODEL, prompt, max_output_tokens=500, temperature=0.4)
        return result.get("text", f"[Error analyzing {topic}]")

    elif name == "compare_options":
        options = args["options"]
        dimensions = args["dimensions"]
        prompt = (
            f"Compare {' vs '.join(options)} along these dimensions: "
            f"{', '.join(dimensions)}.\n"
            f"Give a brief verdict for each dimension. Be specific."
        )
        # Comparisons routed to OpenAI (different provider than research)
        result = call_model(COMPARATOR_MODEL, prompt, max_output_tokens=500, temperature=0.4)
        return result.get("text", "[Error comparing options]")

    return f"[Unknown tool: {name}]"


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


def run_agent(question: str) -> dict[str, Any]:
    """
    Three-step agent loop using 4 different providers:
      1. PLAN     (Anthropic) — break question into sub-tasks + decide tools
      2. EXECUTE  (xAI for research, OpenAI for comparison) — run each tool call
      3. SYNTHESIZE (Google) — combine findings into final answer
    """
    trace: list[dict] = []
    total_start = time.perf_counter()

    # Step 1: Plan
    print("\n[STEP 1] PLANNING (via Anthropic)...")
    plan_prompt = (
        f'You are a research assistant. The user asks: "{question}"\n\n'
        f"Break this into 2-3 research sub-tasks. For each, call the appropriate tool:\n"
        f"- analyze_topic: for researching a specific sub-topic\n"
        f"- compare_options: for comparing alternatives\n\n"
        f"Call the tools now. Do NOT answer the question directly."
    )
    plan_result = call_model(PLANNER_MODEL, plan_prompt, tools=AGENT_TOOLS, temperature=0.4)

    print(f"  Model: {plan_result['model']}")
    print(f"  Latency: {plan_result['latency_ms']:.0f}ms")
    print(f"  Tool calls: {len(plan_result.get('tool_calls', []))}")

    trace.append({"step": "plan", **{k: v for k, v in plan_result.items() if k != "raw_response"}})

    tool_calls = plan_result.get("tool_calls", [])

    if not tool_calls:
        # Model answered directly without using tools
        print("  (Model answered directly without using tools)")
        trace.append({"step": "direct_answer", "text": plan_result.get("text", "")})
        return {
            "question": question,
            "answer": plan_result.get("text", ""),
            "trace": trace,
            "total_ms": (time.perf_counter() - total_start) * 1000,
        }

    # Step 2: Execute tool calls
    print(f"\n[STEP 2] EXECUTING {len(tool_calls)} tool calls (via xAI/OpenAI)...")
    tool_results = []
    for i, tc in enumerate(tool_calls):
        name = tc["name"]
        args_str = tc.get("arguments", "{}")
        print(f"  Tool {i + 1}: {name}({args_str[:80]}{'...' if len(args_str) > 80 else ''})")

        output = execute_tool(name, args_str)
        tool_results.append({"name": name, "arguments": args_str, "output": output})
        print(f"    -> {len(output)} chars returned")

    trace.append({"step": "execute", "tool_results": tool_results})

    # Step 3: Synthesize
    print("\n[STEP 3] SYNTHESIZING (via Google)...")
    findings_text = "\n\n".join(
        f"## {tr['name']}({tr['arguments'][:60]})\n{tr['output']}" for tr in tool_results
    )
    synth_prompt = (
        f'Original question: "{question}"\n\n'
        f"Research findings:\n{findings_text}\n\n"
        f"Synthesize these findings into a clear, concise answer. "
        f"Highlight key tradeoffs and give a recommendation if appropriate."
    )
    synth_result = call_model(SYNTHESIZER_MODEL, synth_prompt, max_output_tokens=600, temperature=0.4)

    print(f"  Model: {synth_result['model']}")
    print(f"  Latency: {synth_result['latency_ms']:.0f}ms")

    trace.append({"step": "synthesize", **{k: v for k, v in synth_result.items() if k != "raw_response"}})

    total_ms = (time.perf_counter() - total_start) * 1000

    return {
        "question": question,
        "answer": synth_result.get("text", ""),
        "trace": trace,
        "total_ms": total_ms,
        "providers_used": {
            "planner": PLANNER_MODEL,
            "researcher": RESEARCHER_MODEL,
            "comparator": COMPARATOR_MODEL,
            "synthesizer": SYNTHESIZER_MODEL,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-step research agent via Concentrate AI")
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTIONS[0],
        help="Question for the agent to research",
    )
    parser.add_argument(
        "--all-questions",
        action="store_true",
        help="Run both default questions sequentially",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("CONCENTRATE AI — MULTI-STEP RESEARCH AGENT (4 PROVIDERS)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Planner:     {PLANNER_MODEL} (Anthropic)")
    print(f"Researcher:  {RESEARCHER_MODEL} (xAI)")
    print(f"Comparator:  {COMPARATOR_MODEL} (OpenAI)")
    print(f"Synthesizer: {SYNTHESIZER_MODEL} (Google)")
    print("=" * 70)

    questions = DEFAULT_QUESTIONS if args.all_questions else [args.question]
    all_results = []

    for i, question in enumerate(questions):
        if len(questions) > 1:
            print(f"\n{'#' * 70}")
            print(f"# QUESTION {i + 1} of {len(questions)}")
            print(f"{'#' * 70}")

        print(f"\nQuestion: {question}")
        result = run_agent(question)

        print("\n" + "=" * 70)
        print("FINAL ANSWER")
        print("=" * 70)
        print(result["answer"])
        print(f"\nTotal time: {result['total_ms']:.0f}ms")
        print(f"Steps: {len(result['trace'])}")

        all_results.append(result)

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data = all_results[0] if len(all_results) == 1 else {"questions": all_results}
    filepath = RESULTS_DIR / f"agent_{ts}.json"
    with open(filepath, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\nResults saved to: {filepath}")


if __name__ == "__main__":
    main()

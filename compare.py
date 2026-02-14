#!/usr/bin/env python3
"""
Multi-provider comparison tool using the Concentrate AI unified API.

Sends identical prompts to OpenAI and Anthropic models via Concentrate,
compares response quality, latency, and cost. Tests auto-routing strategies,
tool calling, streaming, multi-turn conversations, and cost estimation.

Usage:
    python compare.py                      # Run all comparisons
    python compare.py --section basic      # Run only basic comparison
    python compare.py --section routing    # Run only auto-routing tests
    python compare.py --section tools      # Run only tool calling tests
    python compare.py --section edge       # Run only edge case tests
    python compare.py --section streaming  # Run only streaming comparison
    python compare.py --section multiturn  # Run only multi-turn test
    python compare.py --section cost       # Run only cost estimation
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tabulate import tabulate

from client import MODELS, call_model, extract_text, fetch_models

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Auto-routing strategies
ROUTING_STRATEGIES = [
    {"strategy": "min", "metric": "cost"},
    {"strategy": "max", "metric": "performance"},
    {"strategy": "min", "metric": "latency"},
]

# Test prompts — chosen to surface provider differences
PROMPTS = {
    "reasoning": (
        "A farmer has 17 sheep. All but 9 die. How many sheep are left? "
        "Explain your reasoning step by step."
    ),
    "creative": "Write a haiku about debugging code at 3am.",
    "technical": (
        "Explain the difference between L1 and L2 regularization in "
        "gradient boosted trees. When would you prefer each?"
    ),
    "structured": (
        "List exactly 5 common Python antipatterns. For each, give the "
        "antipattern name, a one-line code example, and the fix. "
        "Format as a numbered list."
    ),
}


# ---------------------------------------------------------------------------
# Section 1: Basic multi-provider comparison
# ---------------------------------------------------------------------------


def run_basic_comparison() -> list[dict]:
    """Compare OpenAI vs Anthropic on identical prompts."""
    print("\n" + "=" * 70)
    print("SECTION 1: MULTI-PROVIDER COMPARISON (OpenAI vs Anthropic)")
    print("=" * 70)

    all_results = []

    for prompt_name, prompt_text in PROMPTS.items():
        print(f"\n--- Prompt: {prompt_name} ---")
        display = f'  "{prompt_text[:80]}..."' if len(prompt_text) > 80 else f'  "{prompt_text}"'
        print(display)

        row_results = {}
        for provider, model in MODELS.items():
            result = call_model(model, prompt_text)
            row_results[provider] = result

            status = "OK" if result["status"] == "completed" else result["status"]
            print(f"  {provider:12s} | {result['latency_ms']:7.0f}ms | {status}")

        # Display comparison table
        table_data = [
            [
                provider,
                result["model"],
                f"{result['latency_ms']:.0f}ms",
                result["status"],
                extract_text(result),
            ]
            for provider, result in row_results.items()
        ]

        print()
        print(
            tabulate(
                table_data,
                headers=["Provider", "Model Used", "Latency", "Status", "Response (truncated)"],
                tablefmt="simple",
            )
        )

        all_results.append({
            "prompt_name": prompt_name,
            "prompt_text": prompt_text,
            "results": {k: {**v, "raw_response": None} for k, v in row_results.items()},
        })

    return all_results


# ---------------------------------------------------------------------------
# Section 2: Auto-routing strategies
# ---------------------------------------------------------------------------


def run_routing_comparison() -> list[dict]:
    """Test auto-routing with min-cost, max-performance, min-latency."""
    print("\n" + "=" * 70)
    print("SECTION 2: AUTO-ROUTING STRATEGIES")
    print("=" * 70)

    test_prompt = PROMPTS["technical"]
    print(f'\nUsing prompt: "{test_prompt[:80]}..."')

    all_results = []

    for routing_config in ROUTING_STRATEGIES:
        label = f"{routing_config['strategy']}_{routing_config['metric']}"
        print(f"\n--- Strategy: {label} ---")

        result = call_model("auto", test_prompt, routing=routing_config)

        status = "OK" if result["status"] == "completed" else result["status"]
        print(f"  Model selected: {result['model']}")
        print(f"  Latency:        {result['latency_ms']:.0f}ms")
        print(f"  Status:         {status}")
        print(f"  Response:       {extract_text(result, 120)}")

        all_results.append({
            "strategy": label,
            "routing_config": routing_config,
            "result": {**result, "raw_response": None},
        })

    # Summary table
    print("\n--- Auto-Routing Summary ---")
    table_data = [
        [r["strategy"], r["result"]["model"], f"{r['result']['latency_ms']:.0f}ms", r["result"]["status"]]
        for r in all_results
    ]
    print(tabulate(table_data, headers=["Strategy", "Model Selected", "Latency", "Status"], tablefmt="simple"))

    return all_results


# ---------------------------------------------------------------------------
# Section 3: Tool calling across providers
# ---------------------------------------------------------------------------

WEATHER_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "Get the current weather for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name (e.g., 'New York')"},
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit",
            },
        },
        "required": ["city"],
    },
}

CALCULATOR_TOOL = {
    "type": "function",
    "name": "calculate",
    "description": "Evaluate a mathematical expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '2 + 2')",
            },
        },
        "required": ["expression"],
    },
}


def run_tool_calling_comparison() -> list[dict]:
    """Test tool calling across OpenAI and Anthropic via Concentrate."""
    print("\n" + "=" * 70)
    print("SECTION 3: TOOL CALLING ACROSS PROVIDERS")
    print("=" * 70)

    tool_prompt = (
        "What's the weather in New York and San Francisco? "
        "Also calculate 17 * 23 + 42."
    )
    tools = [WEATHER_TOOL, CALCULATOR_TOOL]

    print(f'\nPrompt: "{tool_prompt}"')
    print(f"Tools provided: {[t['name'] for t in tools]}")

    all_results = []

    for provider, model in MODELS.items():
        print(f"\n--- Provider: {provider} ---")

        result = call_model(model, tool_prompt, tools=tools)

        status = "OK" if result["status"] == "completed" else result["status"]
        print(f"  Model:    {result['model']}")
        print(f"  Status:   {status}")
        print(f"  Latency:  {result['latency_ms']:.0f}ms")

        tool_calls = result.get("tool_calls", [])
        if tool_calls:
            print(f"  Tool calls ({len(tool_calls)}):")
            for tc in tool_calls:
                print(f"    - {tc['name']}({tc.get('arguments', '')})")
        else:
            print("  Tool calls: NONE (model responded with text instead)")
            if result["text"]:
                print(f"  Text: {extract_text(result, 120)}")

        all_results.append({
            "provider": provider,
            "model": result["model"],
            "tool_calls": tool_calls,
            "text": result["text"],
            "latency_ms": result["latency_ms"],
            "status": result["status"],
        })

    return all_results


# ---------------------------------------------------------------------------
# Section 4: Edge cases & error handling
# ---------------------------------------------------------------------------


def run_edge_cases() -> list[dict]:
    """Test edge cases: empty input, extreme parameters, invalid model, etc."""
    print("\n" + "=" * 70)
    print("SECTION 4: EDGE CASES & ERROR HANDLING")
    print("=" * 70)

    test_cases = [
        {
            "name": "empty_input",
            "desc": "Empty string input",
            "model": MODELS["openai"],
            "prompt": "",
            "kwargs": {},
        },
        {
            "name": "max_temperature",
            "desc": "Temperature = 2.0 (maximum creativity)",
            "model": MODELS["openai"],
            "prompt": "Write one sentence about data science.",
            "kwargs": {"temperature": 2.0},
        },
        {
            "name": "zero_temperature",
            "desc": "Temperature = 0.0 (deterministic)",
            "model": MODELS["anthropic"],
            "prompt": "What is 2 + 2?",
            "kwargs": {"temperature": 0.0},
        },
        {
            "name": "tiny_max_tokens",
            "desc": "max_output_tokens = 5 (forced truncation)",
            "model": MODELS["openai"],
            "prompt": "Explain machine learning in detail.",
            "kwargs": {"max_output_tokens": 5},
        },
        {
            "name": "invalid_model",
            "desc": "Non-existent model name",
            "model": "openai/gpt-99-turbo-nonexistent",
            "prompt": "Hello",
            "kwargs": {},
        },
        {
            "name": "very_long_input",
            "desc": "Long input (5000 chars of repeated text)",
            "model": MODELS["anthropic"],
            "prompt": "Summarize the following text: " + "The quick brown fox jumps over the lazy dog. " * 120,
            "kwargs": {"max_output_tokens": 100},
        },
    ]

    all_results = []

    for tc in test_cases:
        print(f"\n--- {tc['name']}: {tc['desc']} ---")

        result = call_model(tc["model"], tc["prompt"], **tc["kwargs"])

        status_display = result["status"]
        if result["error"]:
            status_display = f"ERROR: {result['error'][:100]}"
        elif result["status"] == "completed":
            status_display = "OK"

        print(f"  Status:      {status_display}")
        print(f"  Latency:     {result['latency_ms']:.0f}ms")
        print(f"  Stop reason: {result.get('stop_reason', 'N/A')}")
        if result["text"]:
            print(f"  Response:    {extract_text(result, 120)}")

        all_results.append({
            "name": tc["name"],
            "description": tc["desc"],
            "model": tc["model"],
            "status": result["status"],
            "stop_reason": result.get("stop_reason"),
            "error": result.get("error"),
            "latency_ms": result["latency_ms"],
            "text_length": len(result.get("text", "")),
            "text_preview": extract_text(result)[:200],
        })

    # Summary
    print("\n--- Edge Case Summary ---")
    table_data = [
        [
            r["name"],
            r["status"],
            f"{r['latency_ms']:.0f}ms",
            r.get("stop_reason", ""),
            (r.get("error", "")[:50] if r.get("error") else ""),
        ]
        for r in all_results
    ]
    print(tabulate(table_data, headers=["Test", "Status", "Latency", "Stop Reason", "Error"], tablefmt="simple"))

    return all_results


# ---------------------------------------------------------------------------
# Section 5: Streaming comparison
# ---------------------------------------------------------------------------


def run_streaming_comparison() -> list[dict]:
    """
    Test SSE streaming: measure time-to-first-token, total latency,
    and event count. Compare streaming vs non-streaming for same prompt.
    """
    print("\n" + "=" * 70)
    print("SECTION 5: STREAMING COMPARISON")
    print("=" * 70)

    test_prompt = "Explain gradient descent in 3 sentences."
    test_model = MODELS["openai"]

    print(f'\nModel: {test_model}')
    print(f'Prompt: "{test_prompt}"')

    all_results = []

    # Non-streaming baseline
    print("\n--- Non-streaming (baseline) ---")
    baseline = call_model(test_model, test_prompt, stream=False)
    print(f"  Latency:    {baseline['latency_ms']:.0f}ms")
    print(f"  Status:     {baseline['status']}")
    print(f"  Response:   {extract_text(baseline, 120)}")
    all_results.append({"mode": "non-streaming", **{k: v for k, v in baseline.items() if k != "raw_response"}})

    # Streaming
    print("\n--- Streaming ---")
    streamed = call_model(test_model, test_prompt, stream=True)
    ttft = streamed.get("time_to_first_token_ms", 0)
    events = streamed.get("stream_events", 0)
    print(f"  Time to first token: {ttft:.0f}ms")
    print(f"  Total latency:       {streamed['latency_ms']:.0f}ms")
    print(f"  SSE events:          {events}")
    print(f"  Response:            {extract_text(streamed, 120)}")
    all_results.append({"mode": "streaming", **{k: v for k, v in streamed.items() if k != "raw_response"}})

    # Also test streaming with Anthropic
    print("\n--- Streaming (Anthropic) ---")
    streamed_anth = call_model(MODELS["anthropic"], test_prompt, stream=True)
    ttft_a = streamed_anth.get("time_to_first_token_ms", 0)
    events_a = streamed_anth.get("stream_events", 0)
    print(f"  Time to first token: {ttft_a:.0f}ms")
    print(f"  Total latency:       {streamed_anth['latency_ms']:.0f}ms")
    print(f"  SSE events:          {events_a}")
    print(f"  Response:            {extract_text(streamed_anth, 120)}")
    all_results.append({
        "mode": "streaming_anthropic",
        **{k: v for k, v in streamed_anth.items() if k != "raw_response"},
    })

    # Summary
    print("\n--- Streaming Summary ---")
    table_data = [
        [
            r["mode"],
            r.get("model", "—"),
            f"{r.get('time_to_first_token_ms', r.get('latency_ms', 0)):.0f}ms",
            f"{r.get('latency_ms', 0):.0f}ms",
            str(r.get("stream_events", "—")),
        ]
        for r in all_results
    ]
    print(tabulate(table_data, headers=["Mode", "Model", "TTFT", "Total", "Events"], tablefmt="simple"))

    return all_results


# ---------------------------------------------------------------------------
# Section 6: Multi-turn conversation
# ---------------------------------------------------------------------------


def run_multiturn_comparison() -> list[dict]:
    """
    Test multi-turn conversations using message arrays.

    The Concentrate API accepts input as a list of message objects.
    This tests whether both providers handle conversational context correctly.
    """
    print("\n" + "=" * 70)
    print("SECTION 6: MULTI-TURN CONVERSATION")
    print("=" * 70)

    # A 2-turn conversation that requires context from turn 1
    messages = [
        {"type": "message", "role": "user", "content": "What is 2 + 2?"},
        {"type": "message", "role": "assistant", "content": "4"},
        {"type": "message", "role": "user", "content": "Multiply that by 3, then subtract 1. What's the result?"},
    ]

    print("\nConversation:")
    for msg in messages:
        role_display = "USER" if msg["role"] == "user" else "ASST"
        print(f"  [{role_display}] {msg['content']}")

    print(f"\nExpected answer: 11  (4 * 3 - 1 = 11)")

    all_results = []

    for provider, model in MODELS.items():
        print(f"\n--- Provider: {provider} ---")
        result = call_model(model, messages, temperature=0.0, max_output_tokens=100)

        print(f"  Model:    {result['model']}")
        print(f"  Latency:  {result['latency_ms']:.0f}ms")
        print(f"  Status:   {result['status']}")
        print(f"  Response: {extract_text(result, 200)}")

        # Check if the answer contains "11"
        has_correct_answer = "11" in (result.get("text", "") or "")
        print(f"  Correct:  {'YES' if has_correct_answer else 'NO (expected 11)'}")

        all_results.append({
            "provider": provider,
            "model": result["model"],
            "response": result.get("text", ""),
            "correct": has_correct_answer,
            "latency_ms": result["latency_ms"],
            "status": result["status"],
        })

    # Summary
    print("\n--- Multi-Turn Summary ---")
    table_data = [
        [r["provider"], r["model"], "PASS" if r["correct"] else "FAIL", f"{r['latency_ms']:.0f}ms"]
        for r in all_results
    ]
    print(tabulate(table_data, headers=["Provider", "Model", "Correct", "Latency"], tablefmt="simple"))

    return all_results


# ---------------------------------------------------------------------------
# Section 7: Cost estimation
# ---------------------------------------------------------------------------


def run_cost_estimation() -> list[dict]:
    """
    Fetch model pricing from /v1/models/ and estimate per-request costs.

    Shows what auto-routing cost optimization actually saves by comparing
    the cheapest vs most expensive model for the same prompt.
    """
    print("\n" + "=" * 70)
    print("SECTION 7: COST ESTIMATION")
    print("=" * 70)

    # Fetch pricing data
    print("\nFetching model pricing...")
    catalog = fetch_models()

    if catalog.get("error"):
        print(f"  WARNING: Could not fetch model catalog: {catalog['error']}")
        print("  Falling back to hardcoded estimates.")
        # Fallback: reasonable estimates if catalog unavailable
        pricing = {
            MODELS["openai"]: {"input": 2.00 / 1_000_000, "output": 8.00 / 1_000_000},
            MODELS["anthropic"]: {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
        }
    else:
        # Extract pricing from catalog
        pricing = {}
        models_data = catalog.get("data", catalog.get("models", []))
        for m in models_data:
            mid = m.get("id", "")
            p = m.get("pricing", {})
            if p:
                pricing[mid] = {
                    "input": p.get("input") or p.get("prompt") or 0,
                    "output": p.get("output") or p.get("completion") or 0,
                }
        print(f"  Found pricing for {len(pricing)} models.")

    # Run a test prompt and measure tokens
    test_prompt = PROMPTS["technical"]
    print(f'\nTest prompt: "{test_prompt[:60]}..."')

    all_results = []

    for provider, model in MODELS.items():
        print(f"\n--- {provider}: {model} ---")
        result = call_model(model, test_prompt)

        # Try to get token counts from raw response
        raw = result.get("raw_response", {}) or {}
        usage = raw.get("usage", {})
        input_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        output_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0

        # Estimate tokens from text length if usage not available
        if not input_tokens:
            input_tokens = len(test_prompt) // 4  # rough estimate
        if not output_tokens:
            output_tokens = len(result.get("text", "")) // 4

        # Look up pricing
        model_pricing = pricing.get(model, {"input": 0, "output": 0})
        input_cost = input_tokens * model_pricing["input"]
        output_cost = output_tokens * model_pricing["output"]
        total_cost = input_cost + output_cost

        print(f"  Input tokens:  {input_tokens:,}")
        print(f"  Output tokens: {output_tokens:,}")
        print(f"  Input cost:    ${input_cost:.6f}")
        print(f"  Output cost:   ${output_cost:.6f}")
        print(f"  Total cost:    ${total_cost:.6f}")
        print(f"  Latency:       {result['latency_ms']:.0f}ms")

        all_results.append({
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "latency_ms": result["latency_ms"],
        })

    # Cost comparison summary
    if len(all_results) >= 2:
        costs = [r["total_cost"] for r in all_results]
        cheapest = min(all_results, key=lambda r: r["total_cost"])
        most_expensive = max(all_results, key=lambda r: r["total_cost"])

        print("\n--- Cost Summary ---")
        table_data = [
            [
                r["provider"],
                r["model"],
                f"${r['total_cost']:.6f}",
                f"{r['latency_ms']:.0f}ms",
                f"{r['input_tokens'] + r['output_tokens']:,} tok",
            ]
            for r in all_results
        ]
        print(tabulate(table_data, headers=["Provider", "Model", "Est. Cost", "Latency", "Tokens"], tablefmt="simple"))

        if most_expensive["total_cost"] > 0:
            savings_pct = (1 - cheapest["total_cost"] / most_expensive["total_cost"]) * 100
            print(
                f"\nAuto-routing to cheapest provider saves "
                f"~{savings_pct:.0f}% per request "
                f"(${most_expensive['total_cost'] - cheapest['total_cost']:.6f}/request)"
            )

    return all_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def save_results(results: dict[str, Any], filename: str) -> Path:
    """Save results to JSON file."""
    filepath = RESULTS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {filepath}")
    return filepath


def main() -> None:
    """Run all comparison sections."""
    parser = argparse.ArgumentParser(description="Concentrate AI multi-provider comparison tool")
    parser.add_argument(
        "--section",
        choices=["basic", "routing", "tools", "edge", "streaming", "multiturn", "cost", "all"],
        default="all",
        help="Which section to run (default: all)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("CONCENTRATE AI — MULTI-PROVIDER COMPARISON TOOL")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Models: {list(MODELS.values())}")
    print("=" * 70)

    all_results: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models": MODELS,
    }

    sections = {
        "basic": ("basic_comparison", run_basic_comparison),
        "routing": ("auto_routing", run_routing_comparison),
        "tools": ("tool_calling", run_tool_calling_comparison),
        "edge": ("edge_cases", run_edge_cases),
        "streaming": ("streaming", run_streaming_comparison),
        "multiturn": ("multiturn", run_multiturn_comparison),
        "cost": ("cost_estimation", run_cost_estimation),
    }

    if args.section == "all":
        for key, (result_key, func) in sections.items():
            all_results[result_key] = func()
    else:
        result_key, func = sections[args.section]
        all_results[result_key] = func()

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_results(all_results, f"comparison_{ts}.json")

    print("\n" + "=" * 70)
    print("DONE. All sections complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()

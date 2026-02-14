#!/usr/bin/env python3
"""
Multi-provider comparison tool using the Concentrate AI unified API.

Sends identical prompts to OpenAI and Anthropic models via Concentrate,
compares response quality, latency, and cost. Tests auto-routing strategies
and tool calling across providers.

Usage:
    python compare.py                  # Run all comparisons
    python compare.py --section basic  # Run only basic comparison
    python compare.py --section routing  # Run only auto-routing tests
    python compare.py --section tools  # Run only tool calling tests
    python compare.py --section edge   # Run only edge case tests
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://api.concentrate.ai/v1/responses/"
API_KEY = os.getenv("CONCENTRATE_API_KEY", "")

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Models to compare (provider-prefixed for clarity)
MODELS = {
    "openai": "openai/gpt-4.1",
    "anthropic": "anthropic/claude-sonnet-4-5-20250929",
}

# Auto-routing strategies
ROUTING_STRATEGIES = [
    {"strategy": "min", "metric": "cost"},
    {"strategy": "max", "metric": "performance"},
    {"strategy": "min", "metric": "latency"},
]

# Test prompts — chosen to surface provider differences
PROMPTS = {
    "reasoning": "A farmer has 17 sheep. All but 9 die. How many sheep are left? "
    "Explain your reasoning step by step.",
    "creative": "Write a haiku about debugging code at 3am.",
    "technical": "Explain the difference between L1 and L2 regularization in "
    "gradient boosted trees. When would you prefer each?",
    "structured": "List exactly 5 common Python antipatterns. For each, give the "
    "antipattern name, a one-line code example, and the fix. "
    "Format as a numbered list.",
}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def _headers() -> dict[str, str]:
    """Build request headers."""
    if not API_KEY:
        print("ERROR: CONCENTRATE_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def call_model(
    model: str,
    prompt: str,
    *,
    temperature: float = 0.7,
    max_output_tokens: int = 500,
    tools: list[dict] | None = None,
    routing: dict | None = None,
) -> dict[str, Any]:
    """
    Send a request to Concentrate and return enriched result dict.

    Returns dict with keys: model, text, latency_ms, status, stop_reason,
    tokens_estimate, raw_response, error.
    """
    payload: dict[str, Any] = {
        "model": model if not routing else "auto",
        "input": prompt,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if tools:
        payload["tools"] = tools
    if routing:
        payload["routing"] = routing

    start = time.perf_counter()
    try:
        resp = requests.post(BASE_URL, headers=_headers(), json=payload, timeout=60)
        elapsed_ms = (time.perf_counter() - start) * 1000
    except requests.RequestException as e:
        return {
            "model": model,
            "text": "",
            "latency_ms": 0,
            "status": "error",
            "stop_reason": None,
            "error": str(e),
            "raw_response": None,
        }

    if resp.status_code != 200:
        return {
            "model": model,
            "text": "",
            "latency_ms": elapsed_ms,
            "status": f"http_{resp.status_code}",
            "stop_reason": None,
            "error": resp.text[:500],
            "raw_response": None,
        }

    data = resp.json()
    # Extract text from output
    text = ""
    tool_calls = []
    for output_item in data.get("output", []):
        if output_item.get("type") == "message":
            for content in output_item.get("content", []):
                if content.get("type") == "output_text":
                    text += content.get("text", "")
        elif output_item.get("type") == "function_call":
            tool_calls.append(
                {
                    "name": output_item.get("name"),
                    "arguments": output_item.get("arguments"),
                    "call_id": output_item.get("call_id"),
                }
            )

    return {
        "model": data.get("model", model),
        "text": text,
        "tool_calls": tool_calls,
        "latency_ms": elapsed_ms,
        "status": data.get("status", "unknown"),
        "stop_reason": data.get("stop_reason"),
        "error": None,
        "raw_response": data,
    }


def extract_text(result: dict) -> str:
    """Get display-safe text from result (truncated)."""
    text = result.get("text", "") or ""
    if len(text) > 200:
        return text[:197] + "..."
    return text


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
        print(f"  \"{prompt_text[:80]}...\"" if len(prompt_text) > 80 else f"  \"{prompt_text}\"")

        row_results = {}
        for provider, model in MODELS.items():
            result = call_model(model, prompt_text)
            row_results[provider] = result

            status = "OK" if result["status"] == "completed" else result["status"]
            print(f"  {provider:12s} | {result['latency_ms']:7.0f}ms | {status}")

        # Display comparison table
        table_data = []
        for provider, result in row_results.items():
            table_data.append(
                [
                    provider,
                    result["model"],
                    f"{result['latency_ms']:.0f}ms",
                    result["status"],
                    extract_text(result),
                ]
            )

        print()
        print(
            tabulate(
                table_data,
                headers=["Provider", "Model Used", "Latency", "Status", "Response (truncated)"],
                tablefmt="simple",
            )
        )

        all_results.append(
            {
                "prompt_name": prompt_name,
                "prompt_text": prompt_text,
                "results": {k: {**v, "raw_response": None} for k, v in row_results.items()},
            }
        )

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
    print(f"\nUsing prompt: \"{test_prompt[:80]}...\"")

    all_results = []

    for routing_config in ROUTING_STRATEGIES:
        label = f"{routing_config['strategy']}_{routing_config['metric']}"
        print(f"\n--- Strategy: {label} ---")

        result = call_model("auto", test_prompt, routing=routing_config)

        status = "OK" if result["status"] == "completed" else result["status"]
        print(f"  Model selected: {result['model']}")
        print(f"  Latency:        {result['latency_ms']:.0f}ms")
        print(f"  Status:         {status}")
        print(f"  Response:       {extract_text(result)[:120]}")

        all_results.append(
            {
                "strategy": label,
                "routing_config": routing_config,
                "result": {**result, "raw_response": None},
            }
        )

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

    print(f"\nPrompt: \"{tool_prompt}\"")
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
                print(f"  Text: {extract_text(result)[:120]}")

        all_results.append(
            {
                "provider": provider,
                "model": result["model"],
                "tool_calls": tool_calls,
                "text": result["text"],
                "latency_ms": result["latency_ms"],
                "status": result["status"],
            }
        )

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
            "prompt": ("Summarize the following text: " + "The quick brown fox jumps over the lazy dog. " * 120),
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
            print(f"  Response:    {extract_text(result)[:120]}")

        all_results.append(
            {
                "name": tc["name"],
                "description": tc["desc"],
                "model": tc["model"],
                "status": result["status"],
                "stop_reason": result.get("stop_reason"),
                "error": result.get("error"),
                "latency_ms": result["latency_ms"],
                "text_length": len(result.get("text", "")),
                "text_preview": extract_text(result)[:200],
            }
        )

    # Summary
    print("\n--- Edge Case Summary ---")
    table_data = [
        [r["name"], r["status"], f"{r['latency_ms']:.0f}ms", r.get("stop_reason", ""), r.get("error", "")[:50] if r.get("error") else ""]
        for r in all_results
    ]
    print(tabulate(table_data, headers=["Test", "Status", "Latency", "Stop Reason", "Error"], tablefmt="simple"))

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
        choices=["basic", "routing", "tools", "edge", "all"],
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

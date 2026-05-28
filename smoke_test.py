#!/usr/bin/env python3
"""
Smoke test for Concentrate AI setup verification.

Validates API key, model catalog, per-provider calls, and streaming
before running the full (expensive) comparison suite.

Usage:
    python smoke_test.py
"""

import sys

import requests

from client import API_KEY, MODELS, call_model, fetch_models

HEALTH_URL = "https://api.concentrate.ai/v1/responses/health"


def check(label: str, passed: bool, detail: str = "") -> bool:
    """Print PASS/FAIL for a single check."""
    status = "PASS" if passed else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return passed


def main() -> None:
    print("=" * 60)
    print("CONCENTRATE AI — SMOKE TEST")
    print("=" * 60)

    results: list[bool] = []

    # 0. API health (no auth required — pre-flight check)
    try:
        health = requests.get(HEALTH_URL, timeout=5)
        results.append(check("API health", health.status_code == 200,
            f"status={health.status_code}"))
    except Exception as e:
        results.append(check("API health", False, str(e)))

    # 1. API key present
    results.append(check("API key configured", bool(API_KEY)))
    if not API_KEY:
        print("\n  ABORT: Set CONCENTRATE_API_KEY in .env")
        sys.exit(1)

    # 2. Model catalog
    catalog = fetch_models()
    if isinstance(catalog, list):
        models_data = catalog
        catalog_error = None
    else:
        models_data = catalog.get("data", catalog.get("models", []))
        catalog_error = catalog.get("error")
    results.append(check(
        "Model catalog",
        len(models_data) > 0 and not catalog_error,
        f"{len(models_data)} models found" if models_data else (catalog_error or "empty"),
    ))

    # 3. One call per provider — prints token counts for margin analysis
    for provider, model in MODELS.items():
        result = call_model(model, "Say 'hello' in one word.", max_output_tokens=10, temperature=0.0)
        raw = result.get("raw_response") or {}
        usage = raw.get("usage", {})
        inp = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        out = usage.get("output_tokens") or usage.get("completion_tokens") or 0
        ok = result["status"] == "completed"
        results.append(check(
            f"{model}",
            ok,
            f"completed, {inp} input + {out} output tokens" if ok else f"status={result['status']}, error={result.get('error', 'N/A')}",
        ))
        # Print full token details for reproducibility (C5 evidence: Gemini max_output_tokens behavior)
        print(f"    raw usage: input_tokens={inp}, output_tokens={out}, model_returned={result.get('model', 'N/A')}")
        if out > 10:
            print(f"    NOTE: Requested max_output_tokens=10, received {out} — parameter may be advisory for this provider")

    # 4. Tool calling (verifies strict: false works)
    tool_def = {
        "type": "function",
        "strict": False,
        "name": "get_weather",
        "description": "Get weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
    tool_result = call_model(
        MODELS["openai"],
        "What's the weather in Paris?",
        tools=[tool_def],
        max_output_tokens=100,
        temperature=0.0,
    )
    has_tool_call = len(tool_result.get("tool_calls", [])) > 0
    tool_ok = tool_result["status"] == "completed"
    results.append(check(
        "Tool calling",
        tool_ok,
        f"tool_calls={len(tool_result.get('tool_calls', []))}" if tool_ok
        else f"status={tool_result['status']}, error={tool_result.get('error', 'N/A')}",
    ))

    # 5. Streaming call
    stream_result = call_model(
        MODELS["openai"], "Count to 3.", max_output_tokens=20, stream=True,
    )
    events = stream_result.get("stream_events", 0)
    ttft = stream_result.get("time_to_first_token_ms", 0)
    results.append(check(
        "Streaming",
        events > 0,
        f"{events} events, TTFT={ttft:.0f}ms" if events > 0 else "no events received",
    ))

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    if passed == total:
        print(f"ALL {total} CHECKS PASSED — ready to run full suite")
    else:
        print(f"{passed}/{total} checks passed — fix failures before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()

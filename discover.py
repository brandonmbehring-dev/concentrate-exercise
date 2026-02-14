#!/usr/bin/env python3
"""
Model discovery tool for the Concentrate AI API.

Hits GET /v1/models/ and displays available models grouped by provider,
including pricing, capabilities, and context window sizes. Good first
script to run — validates your API key and shows what's available.

Usage:
    python discover.py              # Display all models
    python discover.py --json       # Output raw JSON
    python discover.py --provider openai  # Filter by provider
"""

import argparse
import json
import sys
from typing import Any

from tabulate import tabulate

from client import fetch_models


def format_price(price: float | None) -> str:
    """Format per-token price as $/1M tokens for readability."""
    if price is None:
        return "—"
    per_million = price * 1_000_000
    if per_million < 0.01:
        return f"${per_million:.4f}/1M"
    return f"${per_million:.2f}/1M"


def group_by_provider(models: list[dict]) -> dict[str, list[dict]]:
    """Group models by provider prefix (e.g., openai/, anthropic/)."""
    groups: dict[str, list[dict]] = {}
    for m in models:
        model_id = m.get("id", "")
        provider = model_id.split("/")[0] if "/" in model_id else "unknown"
        groups.setdefault(provider, []).append(m)
    return groups


def display_models(data: dict[str, Any], provider_filter: str | None = None) -> None:
    """Pretty-print the model catalog."""
    models = data.get("data", data.get("models", []))
    if not models:
        print("No models returned. Response:")
        print(json.dumps(data, indent=2))
        return

    grouped = group_by_provider(models)

    if provider_filter:
        provider_filter = provider_filter.lower()
        if provider_filter not in grouped:
            print(f"No models found for provider '{provider_filter}'.")
            print(f"Available providers: {', '.join(sorted(grouped.keys()))}")
            return
        grouped = {provider_filter: grouped[provider_filter]}

    total_models = sum(len(v) for v in grouped.values())
    print(f"\nConcentrate AI Model Catalog — {total_models} models across {len(grouped)} providers\n")

    for provider, provider_models in sorted(grouped.items()):
        print(f"{'=' * 70}")
        print(f"  {provider.upper()} ({len(provider_models)} models)")
        print(f"{'=' * 70}")

        table_data = []
        for m in sorted(provider_models, key=lambda x: x.get("id", "")):
            model_id = m.get("id", "?")
            # Try common field names for pricing
            pricing = m.get("pricing", {})
            input_price = pricing.get("input") or pricing.get("prompt") or m.get("input_price")
            output_price = pricing.get("output") or pricing.get("completion") or m.get("output_price")

            # Capabilities
            caps = m.get("capabilities", {})
            cap_flags = []
            if caps.get("supports_tools") or caps.get("tool_use"):
                cap_flags.append("tools")
            if caps.get("supports_streaming") or caps.get("streaming"):
                cap_flags.append("stream")
            if caps.get("supports_vision") or caps.get("vision"):
                cap_flags.append("vision")
            if caps.get("supports_json_mode") or caps.get("json_mode"):
                cap_flags.append("json")

            ctx_window = m.get("context_window") or m.get("context_length") or m.get("max_tokens")

            table_data.append([
                model_id,
                format_price(input_price),
                format_price(output_price),
                f"{ctx_window:,}" if ctx_window else "—",
                ", ".join(cap_flags) if cap_flags else "—",
            ])

        print(tabulate(
            table_data,
            headers=["Model", "Input $/1M tok", "Output $/1M tok", "Context", "Capabilities"],
            tablefmt="simple",
        ))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover models available via Concentrate AI")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    parser.add_argument("--provider", type=str, help="Filter by provider (e.g., openai, anthropic)")
    args = parser.parse_args()

    print("Fetching model catalog from Concentrate AI...")
    data = fetch_models()

    if "error" in data and data["error"]:
        print(f"ERROR: {data['error']}")
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    display_models(data, provider_filter=args.provider)

    # Print a note about what models we're using in our scripts
    print("-" * 70)
    print("Models used in this exercise:")
    print(f"  compare.py: openai/gpt-4.1 vs anthropic/claude-sonnet-4-5-20250929")
    print(f"  agent.py:   Planner=Anthropic, Researcher=OpenAI, Synthesizer=Anthropic")
    print("-" * 70)


if __name__ == "__main__":
    main()

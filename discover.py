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
    """Format per-million-token USD price for display."""
    if price is None:
        return "—"
    if price < 0.01:
        return f"${price:.4f}/1M"
    return f"${price:.2f}/1M"


def extract_pricing(model: dict) -> tuple[float | None, float | None]:
    """Extract per-million-token USD pricing from nested providers structure.

    The /v1/models/ response nests pricing under:
        providers.{key}.pricing.tokens.input.price.USD
    Price units are per-million tokens (confirmed by units field).
    """
    for prov_data in model.get("providers", {}).values():
        tokens = prov_data.get("pricing", {}).get("tokens", {})
        inp_obj = tokens.get("input", {})
        out_obj = tokens.get("output", {})
        inp_price = inp_obj.get("price", {}).get("USD")
        out_price = out_obj.get("price", {}).get("USD")
        if inp_price is not None:
            return inp_price, out_price
    return None, None


def extract_capabilities(model: dict) -> tuple[list[str], int | None]:
    """Extract capability flags and context window from providers structure.

    Capabilities live under providers.{key}.supports, not at model top level.
    """
    caps: list[str] = []
    ctx: int | None = None
    for prov_data in model.get("providers", {}).values():
        supports = prov_data.get("supports", {})
        tools = supports.get("tools", {})
        if tools.get("function_calling"):
            caps.append("tools")
        if tools.get("web_search"):
            caps.append("web")
        if supports.get("streaming"):
            caps.append("stream")
        if supports.get("reasoning"):
            caps.append("reasoning")
        ctx = ctx or prov_data.get("context_window")
    return caps, ctx


def group_by_provider(models: list[dict]) -> dict[str, list[dict]]:
    """Group models by author slug (e.g., openai, anthropic, google)."""
    groups: dict[str, list[dict]] = {}
    for m in models:
        author = m.get("author", {}).get("slug", "unknown")
        groups.setdefault(author, []).append(m)
    return groups


def display_models(data: list | dict, provider_filter: str | None = None) -> None:
    """Pretty-print the model catalog.

    Handles both list (raw array) and dict (wrapped) responses from /v1/models/.
    """
    # Handle both list and dict catalog responses
    if isinstance(data, list):
        models = data
    else:
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
        for m in sorted(provider_models, key=lambda x: x.get("slug", "")):
            slug = m.get("slug", "?")
            # Build provider/model display IDs
            prov_slugs = list(m.get("providers", {}).keys())
            model_ids = [f"{ps}/{slug}" for ps in prov_slugs] if prov_slugs else [slug]

            inp_price, out_price = extract_pricing(m)
            cap_flags, ctx_window = extract_capabilities(m)

            table_data.append([
                ", ".join(model_ids),
                format_price(inp_price),
                format_price(out_price),
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

    # Handle both list and dict responses; detect errors
    if isinstance(data, dict) and data.get("error"):
        print(f"ERROR: {data['error']}")
        sys.exit(1)
    if isinstance(data, list) and not data:
        print("ERROR: Empty model catalog")
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    display_models(data, provider_filter=args.provider)

    # Print a note about what models we're using in our scripts
    from client import MODELS
    print("-" * 70)
    print("Models used in this exercise:")
    for provider, model_id in MODELS.items():
        print(f"  {provider:12s} → {model_id}")
    print(f"\n  agent.py roles: Planner=Anthropic, Researcher=xAI, "
          f"Comparator=OpenAI, Synthesizer=Google")
    print("-" * 70)


if __name__ == "__main__":
    main()

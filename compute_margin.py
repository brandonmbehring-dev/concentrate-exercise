#!/usr/bin/env python3
"""
Compute platform margin by comparing token-level costs against dashboard billing.

Reads all JSON result files from results/, extracts every usage.input_tokens and
usage.output_tokens entry, maps each to its provider using the model field,
multiplies by provider_info prices, and outputs the full breakdown.

The dashboard delta (before - after) must be entered manually from screenshots.

Usage:
    python compute_margin.py
    python compute_margin.py --dashboard-delta 1.30   # Enter known dashboard spend
"""

import argparse
import json
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(__file__).parent / "results"
PROVIDER_INFO_DIR = RESULTS_DIR / "provider_info"


def load_provider_pricing() -> dict[str, dict[str, float]]:
    """Load per-million-token pricing from provider_info JSON files.

    Returns:
        Dict mapping "provider/model" -> {"input": price_per_M, "output": price_per_M}
    """
    pricing: dict[str, dict[str, float]] = {}

    for info_file in PROVIDER_INFO_DIR.glob("*.json"):
        data = json.loads(info_file.read_text())
        provider_slug = data.get("provider_slug", "")
        # Derive model slug from filename: "gpt-5.1_openai.json" -> "gpt-5.1"
        model_slug = info_file.stem.rsplit("_", 1)[0]
        model_key = f"{provider_slug}/{model_slug}"

        tokens = data.get("pricing", {}).get("tokens", {})
        inp_price = tokens.get("input", {}).get("price", {}).get("USD", 0)
        out_price = tokens.get("output", {}).get("price", {}).get("USD", 0)
        inp_units = tokens.get("input", {}).get("units", 1_000_000)
        out_units = tokens.get("output", {}).get("units", 1_000_000)

        # Normalize to per-million-token pricing
        pricing[model_key] = {
            "input_per_M": inp_price * (1_000_000 / inp_units),
            "output_per_M": out_price * (1_000_000 / out_units),
        }

    return pricing


def extract_usage_from_results() -> list[dict[str, Any]]:
    """Walk all JSON result files in results/ and extract usage data.

    Looks for usage.input_tokens and usage.output_tokens at any nesting depth.
    Returns list of {model, input_tokens, output_tokens, source_file, context}.
    """
    entries: list[dict[str, Any]] = []

    for json_file in sorted(RESULTS_DIR.glob("*.json")):
        if json_file.name == "margin_analysis.json":
            continue  # Skip our own output
        data = json.loads(json_file.read_text())
        _walk_for_usage(data, str(json_file.name), [], entries)

    return entries


def _walk_for_usage(
    obj: Any,
    source_file: str,
    path: list[str],
    entries: list[dict[str, Any]],
) -> None:
    """Recursively walk a JSON structure looking for usage data next to model fields."""
    if isinstance(obj, dict):
        # Check if this dict has usage data
        usage = obj.get("raw_response", {})
        if isinstance(usage, dict):
            usage = usage.get("usage", {})
        else:
            usage = obj.get("usage", {})

        if isinstance(usage, dict):
            inp = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
            out = usage.get("output_tokens") or usage.get("completion_tokens") or 0
            if inp > 0 or out > 0:
                model = obj.get("model", "")
                entries.append({
                    "model": model,
                    "input_tokens": inp,
                    "output_tokens": out,
                    "source_file": source_file,
                    "context": ".".join(path[-3:]) if path else "root",
                })

        # Recurse into all values
        for key, val in obj.items():
            _walk_for_usage(val, source_file, path + [key], entries)

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_for_usage(item, source_file, path + [str(i)], entries)


def compute_costs(
    entries: list[dict[str, Any]],
    pricing: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """Compute token-level costs for all usage entries.

    Returns full breakdown by model and totals.
    """
    per_model: dict[str, dict[str, float | int]] = {}

    for e in entries:
        model = e["model"]
        prices = pricing.get(model)
        if not prices:
            # Try matching by slug suffix (e.g., "gpt-5.1" matches "openai/gpt-5.1")
            for key, val in pricing.items():
                if key.endswith("/" + model) or model.endswith(key.split("/")[-1]):
                    prices = val
                    break
        if not prices:
            prices = {"input_per_M": 0, "output_per_M": 0}

        inp_cost = e["input_tokens"] * prices["input_per_M"] / 1_000_000
        out_cost = e["output_tokens"] * prices["output_per_M"] / 1_000_000

        bucket = per_model.setdefault(model, {
            "input_tokens": 0,
            "output_tokens": 0,
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
            "call_count": 0,
            "input_price_per_M": prices["input_per_M"],
            "output_price_per_M": prices["output_per_M"],
        })
        bucket["input_tokens"] += e["input_tokens"]
        bucket["output_tokens"] += e["output_tokens"]
        bucket["input_cost"] += inp_cost
        bucket["output_cost"] += out_cost
        bucket["total_cost"] += inp_cost + out_cost
        bucket["call_count"] += 1

    total_computed = sum(m["total_cost"] for m in per_model.values())
    total_calls = sum(m["call_count"] for m in per_model.values())

    return {
        "per_model": per_model,
        "total_computed_cost": round(total_computed, 6),
        "total_calls": total_calls,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Concentrate platform margin")
    parser.add_argument(
        "--dashboard-delta",
        type=float,
        default=None,
        help="Dashboard spend (before - after) in USD. Enter from screenshots.",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("CONCENTRATE AI — MARGIN ANALYSIS")
    print("=" * 70)

    # Load pricing
    pricing = load_provider_pricing()
    print(f"\nLoaded pricing for {len(pricing)} models:")
    for model, prices in sorted(pricing.items()):
        print(f"  {model:40s}  in=${prices['input_per_M']:.2f}/M  out=${prices['output_per_M']:.2f}/M")

    # Extract usage
    entries = extract_usage_from_results()
    print(f"\nFound {len(entries)} usage entries across result files.")

    if not entries:
        print("\nWARNING: No usage data found in results/*.json")
        print("  Run the test suite first, then re-run this script.")
        return

    # Compute costs
    costs = compute_costs(entries, pricing)

    # Display per-model breakdown
    print(f"\n{'=' * 70}")
    print("PER-MODEL BREAKDOWN")
    print(f"{'=' * 70}")

    for model, data in sorted(costs["per_model"].items()):
        print(f"\n  {model}")
        print(f"    Calls:         {data['call_count']}")
        print(f"    Input tokens:  {data['input_tokens']:,}")
        print(f"    Output tokens: {data['output_tokens']:,}")
        print(f"    Input cost:    ${data['input_cost']:.6f}  (@${data['input_price_per_M']:.2f}/M)")
        print(f"    Output cost:   ${data['output_cost']:.6f}  (@${data['output_price_per_M']:.2f}/M)")
        print(f"    Total cost:    ${data['total_cost']:.6f}")

    print(f"\n{'=' * 70}")
    print(f"TOTAL COMPUTED TOKEN COST: ${costs['total_computed_cost']:.6f}")
    print(f"TOTAL API CALLS:          {costs['total_calls']}")
    print(f"{'=' * 70}")

    # Margin computation
    margin_data: dict[str, Any] = {
        "dashboard_delta": None,
        "margin_pct": None,
        "margin_note": "Enter --dashboard-delta from screenshots to compute margin",
    }

    if args.dashboard_delta is not None:
        delta = args.dashboard_delta
        computed = costs["total_computed_cost"]
        if computed > 0:
            margin_pct = ((delta - computed) / computed) * 100
        else:
            margin_pct = None

        margin_data = {
            "dashboard_delta": delta,
            "computed_token_cost": computed,
            "margin_usd": round(delta - computed, 6),
            "margin_pct": round(margin_pct, 1) if margin_pct is not None else None,
        }

        print(f"\nDashboard delta:     ${delta:.2f}")
        print(f"Computed token cost: ${computed:.6f}")
        print(f"Margin (absolute):   ${delta - computed:.6f}")
        if margin_pct is not None:
            print(f"Margin (percentage): {margin_pct:.1f}%")
    else:
        print("\nTIP: Re-run with --dashboard-delta <amount> to compute margin.")
        print("     amount = (dashboard_before - dashboard_after)")

    # Save full analysis
    output = {
        "pricing_source": {model: prices for model, prices in sorted(pricing.items())},
        "usage_entries": entries,
        "per_model_breakdown": {
            model: {k: round(v, 6) if isinstance(v, float) else v for k, v in data.items()}
            for model, data in costs["per_model"].items()
        },
        "totals": {
            "computed_token_cost": costs["total_computed_cost"],
            "total_calls": costs["total_calls"],
        },
        "margin": margin_data,
    }

    outpath = RESULTS_DIR / "margin_analysis.json"
    outpath.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nFull analysis saved to: {outpath}")


if __name__ == "__main__":
    main()

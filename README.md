# Concentrate AI — API Exploration Exercise

> **Note**: This README is 100% human-written per exercise requirements.

## What I Built

<!-- Describe what you built and why. What questions did you set out to answer? -->

## Setup

```bash
# Clone
git clone <repo-url>
cd concentrate-exercise

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your Concentrate API key from https://app.concentrate.ai
```

## How to Run

```bash
# 0. Verify setup (run this first)
python smoke_test.py

# 1. Discover available models and pricing
python discover.py

# 2. Run all comparisons (9 sections: basic, routing, tools, edge, streaming, multi-turn, cost, research, websearch)
python compare.py
python compare.py --section all

# Run a specific section
python compare.py --section basic
python compare.py --section streaming
python compare.py --section cost
python compare.py --section research
python compare.py --section websearch

# 3. Run the multi-step research agent (4-provider routing)
python agent.py
python agent.py --question "Your custom question here"
python agent.py --all-questions

# 4. Run Package C evaluation suite
python eval.py results/comparison_*.json
python eval.py results/comparison_*.json --skip-llm  # Layer 1 only (deterministic, $0)

# 5. Test PII redaction guardrails
python guardrails.py
```

Results are saved as JSON in `results/`.

## Scripts Overview

| Script | Purpose | API Calls |
|--------|---------|-----------|
| `smoke_test.py` | Setup verification (API key, providers, streaming) | ~5 |
| `discover.py` | Model catalog + pricing exploration | 1 (GET /v1/models/) |
| `compare.py` | 9-section provider comparison suite | ~76 |
| `agent.py` | Multi-step research agent (plan/execute/synthesize) | ~10 |
| `eval.py` | Package C evaluation (deterministic + LLM-judge + meta-eval) | ~70 |
| `guardrails.py` | PII redaction test (streaming vs non-streaming) | 2 |
| `client.py` | Shared API client with retry logic (not run directly) | -- |

## Findings

See `research/FINDINGS.md` for the complete log of 20+ empirical findings, documentation
inconsistencies, and behavioral observations. A Tufte handout writeup will be submitted
separately.

## Friction / API Feedback

See `research/FINDINGS.md` — Categories A (doc inconsistencies) and C (behavioral findings)
document specific DX friction points with severity ratings and reproduction steps.

## Screenshots

Dashboard screenshots are in `research/docs/dashboard/`:
- `billing_final.png` — $8.27 remaining of $10 budget
- `guardrails_enabled.png` — SSN/EMAIL/PHONE guardrails enabled

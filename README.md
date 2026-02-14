# Concentrate AI — API Exploration Exercise

> **Note**: This README is 100% human-written per exercise requirements.

## What I Built

<!-- Describe what you built and why. What questions did you set out to answer? -->

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/concentrate-exercise.git
cd concentrate-exercise

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your Concentrate API key from https://app.concentrate.ai
```

## How to Run

```bash
# Discover available models and pricing
python discover.py

# Run all comparisons (basic, routing, tools, edge cases, streaming, multi-turn, cost)
python compare.py

# Run a specific section
python compare.py --section basic
python compare.py --section streaming
python compare.py --section cost

# Run the multi-step research agent
python agent.py
python agent.py --question "Your custom question here"
```

Results are saved as JSON in `results/`.

## Scripts Overview

| Script | Purpose | API Calls |
|--------|---------|-----------|
| `discover.py` | Model catalog + pricing exploration | 1 (GET /v1/models/) |
| `compare.py` | 7-section provider comparison suite | ~20 |
| `agent.py` | Multi-step research agent (plan/execute/synthesize) | 4-6 |
| `client.py` | Shared API client (not run directly) | — |

## Findings

<!-- What did you learn? How do providers compare on latency, cost, quality? -->

## Friction / API Feedback

<!-- What was confusing? What would you improve about the API/docs? -->

## Screenshots

<!-- Add screenshots from results/ or terminal output -->

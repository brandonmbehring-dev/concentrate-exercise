# Provider Analysis — 4 Providers Selected

## Decision: OpenAI + Anthropic + Google Gemini + xAI

### Models Configuration
```python
MODELS = {
    "openai": "openai/gpt-5.1",
    "anthropic": "anthropic/claude-sonnet-4-5",
    "google": "vertex/gemini-2.5-pro",
    "xai": "xai/grok-4-1-fast-reasoning",
}
```

---

## Defensible: Token Pricing (from Get Provider Info)

All prices sourced from `results/provider_info/*.json` — Concentrate's published per-token rates.

| Provider | Input/M | Output/M | Cache Read/M | Web Search/1K |
|----------|---------|----------|-------------|---------------|
| xAI/grok-4-1-fast-reasoning | $0.20 | $0.50 | $0.05 | $5.00 |
| OpenAI/gpt-5.1 | $1.25 | $10.00 | $0.125 | $10.00 |
| Vertex/gemini-2.5-pro | $1.25 | $10.00 | — | $35.00 |
| Anthropic/claude-sonnet-4-5 | $3.00 | $15.00 | $0.30 | $10.00 |

**Input spread**: 15x (xAI $0.20 vs Anthropic $3.00)
**Output spread**: 30x (xAI $0.50 vs Anthropic $15.00)
**Web search spread**: 7x (xAI $5 vs Vertex $35)

### Context Windows

| Provider | Context Window | Max Output |
|----------|---------------|------------|
| xAI | 2,000,000 | 131,072 |
| Vertex | 1,000,000 | 65,536 |
| OpenAI | 400,000 | 128,000 |
| Anthropic | 200,000 | 64,000 |

**Source**: `results/provider_info/*.json`

---

## Defensible: Capability Matrix (Empirical)

Tested via `compare.py` Section 3 and `smoke_test.py`.

| Capability | OpenAI | Anthropic | Vertex | xAI |
|------------|--------|-----------|--------|-----|
| Tool calling (3 tools) | 3/3 | 3/3 | 3/3 | 3/3 |
| Multi-turn context | PASS | PASS | PASS | PASS |
| Streaming (SSE events) | 3 | 3 | — | — |
| max_output_tokens respected | ~Yes (11) | Yes (4) | **No (429)** | No (116) |
| Web search triggered | Yes | Yes | No | Yes |
| JSON schema compliance | PASS | PASS | PASS | PASS |
| Ground truth (3 factual) | 2/3 | 3/3 | 3/3 | 3/3 |

- `function_calling: false` in metadata for ALL providers, but all succeed empirically
- **Evidence**: `results/compare_output.txt`, `results/smoke_test_output.txt`

---

## Exploratory: Quality Observations (n=32, Illustrative Only)

> **Statistical caveat**: 8 prompts × 4 providers = 32 responses. This is too small for robust conclusions. These observations test the *models*, not the *platform*.

### Judge Scores (Haiku 4.5 fast judge, 1-5 scale)

| Provider | Avg Score | Best Prompt | Worst Prompt |
|----------|-----------|------------|-------------|
| xAI | 4.12 | monty_hall (5.0) | insurance (3.0) |
| Anthropic | 4.04 | monty_hall (5.0) | fermi (3.0) |
| OpenAI | 3.88 | simpsons (4.7) | fermi (1.7) |
| Google | 3.29 | json_schema (4.7) | simpsons (1.7) |

### Pairwise Wins (Consistent Across Both Orderings)
- xAI: 6 wins (best overall)
- Anthropic: 4 wins
- OpenAI: 1 win
- 7 splits (39% position bias rate)

### Cost Efficiency (Eval Run)
| Provider | Total Cost | Cost/Response |
|----------|-----------|---------------|
| xAI | $0.008 | $0.001 |
| OpenAI | $0.051 | $0.006 |
| Anthropic | $0.065 | $0.008 |
| Google | $0.264 | $0.033 |

xAI won the most pairwise comparisons at **33x lower cost** than Google.

**Evidence**: `results/eval_output.txt:196-214`, `results/eval_results.json`

---

## Provider Profiles

### OpenAI (`openai/gpt-5.1`) — Comparator
- **Strengths**: Best structured output, strong tool calling, massive ecosystem
- **Weakness**: Only provider to miss Monty Hall ground truth (2/3 factual)
- **Pricing**: Mid-range ($1.25/$10)
- **Note**: 5 of 8 research prompts returned `incomplete` (max_output_tokens=800 truncation)

### Anthropic (`anthropic/claude-sonnet-4-5`) — Planner
- **Strengths**: Only provider with 0/8 incomplete responses, strong reasoning
- **Weakness**: Premium pricing ($3/$15), 200K context (smallest)
- **Unique**: Only provider with cache.write pricing (ephemeral 5m + 1h tiers)

### Google Gemini (`vertex/gemini-2.5-pro`) — Synthesizer
- **Strengths**: 1M context, verbose comprehensive answers
- **Weakness**: Ignores max_output_tokens (inflates costs), slowest latency, lowest judge scores
- **Unique**: Web search NOT triggered despite `web_search` tool being passed
- **Note**: Prefix must be `vertex/`, not `google/` (catalog author ≠ API prefix)

### xAI (`xai/grok-4-1-fast-reasoning`) — Researcher
- **Strengths**: Best cost/quality ratio, won 6 pairwise, 2M context window
- **Weakness**: 4 of 8 research prompts returned `incomplete` (reasoning tokens inflate count)
- **Pricing**: 15x cheaper input, 30x cheaper output than Anthropic
- **Note**: 164 input tokens for 7-word prompt — reasoning tokens likely included in count

---

## Why These 4?

The selection creates a **cost-quality spectrum** that IS Concentrate's value proposition:

```
xAI (cheapest)     → OpenAI (mid)     → Google (mid)        → Anthropic (premium)
$0.20/M input        $1.25/M            $1.25/M               $3.00/M
$0.50/M output       $10.00/M           $10.00/M              $15.00/M
```

Smart routing across this spectrum = Concentrate's core product story.

### Why Not Others?
| Provider | Why Excluded |
|----------|-------------|
| DeepSeek | xAI strictly cheaper ($0.20 vs $0.27+) with stronger reasoning |
| Mistral | Overlaps with xAI cost category, less interesting spread |
| Cohere | Niche (RAG-focused), doesn't add to core comparison narrative |

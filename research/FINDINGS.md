# Concentrate AI — API Discrepancy & Findings Log

> Compiled: 2026-02-16
> Method: Playwright-based documentation audit + code audit + empirical testing
> Pages audited: 12 of 17 (see research/docs/ for verbatim captures)

---

## Category A: Documentation Inconsistencies (Bug-Generating)

### A1. Tool Calling `strict` Default is `true` — Quick Start Omits It

**Severity**: HIGH — will cause 400 errors for unprepared callers

- **Doc source**: Tool Calling page states `strict` defaults to `true`
- **Quick Start**: Shows tool calling example WITHOUT `strict` field
- **Effect**: Any tool definition that lacks `strict: false` will be validated against JSON Schema strictly. If the model produces arguments not perfectly matching the schema, the request fails.
- **Our fix**: Added `"strict": False` to all 4 tool definitions (compare.py, agent.py)
- **Writeup angle**: Real DX friction — the docs contradict themselves across pages

### A2. Catalog Field Names: `slug` Not `id`, Nested Pricing

**Severity**: HIGH — catalog parsing crashes silently (no `id` field exists)

- **Doc source**: List Models page, OpenAPI schema
- **Actual structure**: `model.slug`, `model.author.slug`, `model.providers.{key}.pricing.tokens.{input|output}.price.USD`
- **Our code assumed**: `model.id`, `model.pricing.input`, `model.capabilities.supports_tools`
- **Our fix**: Rewrote discover.py parsing and compare.py cost section to use correct nested paths
- **Writeup angle**: No SDK means you parse raw JSON — schema documentation is critical

### A3. Provider Slug Mismatch for Google/Gemini

**Severity**: MEDIUM — wrong model name in research docs

- **Catalog lists author as**: `google`
- **API requires provider prefix**: `vertex/` (e.g., `vertex/gemini-2.5-pro`)
- **Affected file**: `research/INDEX.md` line 17 said `google/gemini-2.5-pro`
- **Our fix**: Updated to `vertex/gemini-2.5-pro` everywhere
- **Writeup angle**: `google/` vs `vertex/` — real confusion source, verified empirically

---

## Category B: Concentrate Normalization Findings

### B1. Streaming Events Are Normalized

- **Docs describe**: Rich SSE protocol with 10+ event types (response.created, response.in_progress, response.output_text.delta, etc.)
- **Our parser**: Uses standard `data: ` prefix parsing, extracts text from nested `output[].content[].text`
- **Both work**: Concentrate normalizes the streaming format. Our simpler parser works because the normalization handles provider-specific protocols.
- **Decision**: Keep our parser as-is. "Normalization is the value prop."

### B2. Multi-turn `type: "message"` Is Optional

- **Docs state**: `type` field in messages defaults to `"message"` — it's optional
- **Our code had**: Explicit `"type": "message"` on every message object
- **Fix**: Removed for cleanliness. Not a bug, but matches documented minimal format.

---

## Category C: Behavioral Findings (Empirical)

### C1. Gemini Ignores `max_output_tokens`

- **Observed**: Sent `max_output_tokens=10`, received 441 output tokens
- **Provider**: `vertex/gemini-2.5-pro`
- **Hypothesis**: Gemini may treat this as advisory, or Concentrate doesn't enforce it for Vertex
- **Writeup angle**: Cross-provider parameter parity is not guaranteed

### C2. xAI Token Counting Anomaly

- **Observed**: 164 input tokens for a 7-word prompt ("Say 'hello' in one word.")
- **Provider**: `xai/grok-4-1-fast-reasoning`
- **Hypothesis**: May include reasoning/chain-of-thought tokens in input count
- **Writeup angle**: Token-based cost estimation is model-dependent

### C3. Quickstart Default Is `gpt-5.2`

- **Docs quickstart**: Shows `openai/gpt-5.2` as the default model
- **Our code uses**: `openai/gpt-5.1`
- **Impact**: None (5.1 works fine), but docs are ahead of our model selection
- **Note**: GPT-4.1 retirement (Feb 13-19, 2026) is documented

### C4. Auto-Routing `min_latency` Requires Percentile Format

- **Observed**: `auto_routing` with `"metric": "latency"` returns 400 error ("Invalid percentile metric format")
- **API expects**: Percentile format like `p50`, `p90`, `p99` — not raw string `latency`
- **2 of 3 strategies worked**: `min_cost` and `max_performance` succeeded
- **Doc source**: Auto-routing page doesn't explicitly list valid metric values
- **Writeup angle**: Undocumented API constraint — valid strategies are discoverable only by trial

### C5. ~55% Platform Margin on Token Costs

- **Observed**: compare.py billed $0.87, but token-level cost computation yields $0.56
- **Margin**: ($0.87 - $0.56) / $0.56 = ~55% platform markup over raw provider pricing
- **Per-provider token costs (pre-margin)**: Google $0.40 (73%), Anthropic $0.088, OpenAI $0.056, xAI $0.010
- **Dashboard shows**: vertex 46%, anthropic 28%, openai 22%, xai 4% — consistent ranking
- **Total spend**: $1.73 of $10.00 budget (331 requests)
- **Writeup angle**: Platform margin is implicit — not documented. The "up to 20% off" claim on homepage likely refers to volume discounts vs direct provider pricing, not the base markup.

### C6. Guardrails Default State + Streaming Caveat

- **Default**: Guardrails disabled on new API keys. No redaction occurs.
- **When disabled**: Model self-censorship is **non-deterministic** — SSN self-redacted, email/phone exposed on first run, all self-censored on second run (same prompt, same model)
- **When enabled (SSN/EMAIL/PHONE)**: Platform replaces PII with typed tokens `[SSN]`, `[EMAIL]`, `[PHONE]` in non-streaming mode
- **Streaming caveat confirmed**: Dashboard warns "Output will not be redacted if the response is streamed" — streaming returned empty content in both states
- **Writeup angle**: Model self-censorship ≠ platform guardrails. Stochastic vs deterministic safety is the key distinction.

### C7. LLM Judge Responses Wrapped in Markdown Fences

- **Observed**: All haiku-4-5 and sonnet-4-5 judge responses returned JSON inside `` ```json ``` `` fences
- **Impact**: `json.loads()` fails on fenced JSON — required adding `extract_json()` helper
- **Affected models**: claude-haiku-4-5 (100% fenced), claude-sonnet-4-5 (100% fenced), gpt-5.1 (~40% fenced)
- **Writeup angle**: "Reply with ONLY JSON" prompt instruction is insufficient — always parse defensively

### C8. Eval Scoreboard — xAI Best Value, Google Most Expensive

- **Judge scores (haiku, 1-5 avg)**: OpenAI 3.92, xAI 3.75, Anthropic 3.71, Google 3.29
- **Pairwise wins**: xAI 7, OpenAI 5, Anthropic 4, Google 1
- **Cost per response**: xAI $0.008 total, Google $0.319 total (40x more expensive)
- **GPT-5.1 missed ground truth**: Failed to include "3/8" on 4-door Monty Hall (3/4 providers correct)
- **Cross-provider agreement**: 2/3 factual prompts unanimous, 1 disagreement (Monty Hall)
- **Writeup angle**: Price/performance ratio — cheapest model (xAI) won the most pairwise comparisons

---

## Category D: Untested Features (Writeup Material)

These features are documented but we did not test them:

| Feature | Why Untested | Writeup Mention |
|---------|-------------|-----------------|
| Web search `filters.allowed_domains` | Would add complexity without core insight | "What I'd build next" |
| Auto-routing p50/p90/p99 metrics | Need sustained traffic to be meaningful | Mention metrics exist |
| Prompt caching (`cache_control`) | Anthropic-only, 5m/1h TTL | "Cross-provider parity gap" |
| Reasoning effort levels | Need to verify which models support it | "What I'd build next" |
| `function_call_output` round-trip | Multi-turn tool use flow | "What I'd build next" |
| `user_location` for web search | Geolocation-aware search | Mention it exists |
| Messages API (`/v1/messages/`) | Beta, minimal docs | "DX feature worth watching" |

---

## Not Bugs (Audit Corrections)

| Flagged Issue | Why It's Fine |
|---|---|
| Multi-turn `"type": "message"` | Docs say `type` is optional, defaults to "message". Redundant but valid. Removed for cleanliness. |
| No retry/backoff | `client.py:108-134` HAS exponential backoff + `Retry-After` header support |
| eval.py missing raw_response tokens | `compare.py:112,837` preserves `usage` in saved JSON. Works. |
| Streaming parser wrong per docs | Works via Concentrate normalization. Intentional "don't change" decision. |

---

## Summary Statistics

- **Pages audited**: 12 / 17
- **Code issues found**: 16 (10 crash, 4 400-error, 2 incomplete data)
- **Code issues fixed**: 16/16 + 1 new fix (JSON extraction in eval.py)
- **Research doc issues**: 2 (both fixed)
- **Not-bugs correctly identified**: 4
- **Empirical findings**: 8 (C1–C8)
- **Total API spend**: $1.73 of $10.00 budget (83% remaining)
- **Total API calls**: ~400 across all scripts
- **Scripts executed**: 8/8 (smoke_test, discover, compare, agent, eval, guardrails ×2)
- **Eval results**: 15/16 ground truth pass, xAI best value, Google most expensive

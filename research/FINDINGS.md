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
- **Code issues fixed**: 16/16
- **Research doc issues**: 2 (both fixed)
- **Not-bugs correctly identified**: 4

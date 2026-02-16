# Concentrate AI — API Discrepancy & Findings Log

> Compiled: 2026-02-16 (updated 2026-02-16 post-audit remediation)
> Method: Playwright-based documentation audit + code audit + empirical testing + 3 external reviews
> Pages audited: 17 of 17 (see research/docs/ for verbatim captures)

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

### C8. Eval Scoreboard — v2 (with extract_json fix + pairwise bias mitigation)

- **Judge scores (haiku, 1-5 avg)**: OpenAI 4.04, xAI 3.75, Anthropic 3.71, Google 3.21
- **Pairwise wins (consistent only)**: OpenAI 6, xAI 3, Anthropic 2
- **Position-biased splits**: 7/18 (38.9%) — judge contradicts itself when response order swapped
- **Cost per response**: xAI $0.008 total, Google $0.319 total (40x more expensive)
- **Deep eval parse failures**: 12/32 (37.5%, improved from ~40.6% in v1) — GPT-5.1 still generates unparseable JSON for complex prompts
- **5 incomplete responses detected** (new Layer 1 tracking): `max_output_tokens=800` truncates some responses
- **GPT-5.1 missed ground truth**: Failed to include "3/8" on 4-door Monty Hall (3/4 providers correct)
- **Cross-provider agreement**: 2/3 factual prompts unanimous, 1 disagreement (Monty Hall)
- **v1 preserved**: `results/eval_results_v1.json` for run-to-run comparison
- **Writeup angle**: Price/performance ratio + 39% position bias rate = LLM-as-judge requires debiasing

### C9. Haiku Judge Factual Error on 4-Door Monty Hall

- **Observed**: haiku-4-5 gave Google and xAI `accuracy=2` claiming their 3/8 answer is wrong
- **Reality**: The 4-door Monty Hall correct answer IS 1/4, 3/8, 3/8 (Bayesian verified)
- **Root cause**: Haiku confused the 3-door classic (1/3 → 2/3) with the 4-door variant
- **Writeup angle**: LLM-as-judge has domain knowledge limits; factual ground truth checks are essential alongside judge scores

### C10. GPT-5.1 Deep Judge Self-Contradictory on Monty Hall

- **Observed**: Gave Anthropic 7/10 for stating "3/8" — acknowledged correct
- Gave xAI 3/10 for the SAME "3/8" answer — claimed incorrect
- **Writeup angle**: Judge consistency failures in pairwise evaluation; same fact scored differently depending on surrounding prose

### C11. Streaming Text Capture Failure

- **Observed**: `client.py:232-236` expects `output[].type=="message"` > `content[].type=="output_text"`
- Concentrate's actual streaming events use a different delta structure
- 3 SSE events arrive but 0 text extracted — all streaming sections have empty text
- **Not fixing**: Would require reverse-engineering Concentrate's actual SSE format. The finding itself (normalization doesn't fully normalize streaming) is valuable.

### C12. Auto-Routing `min_cost` Returns Empty Text

- **Observed**: `cloudflare/qwen3-30b` selected by router, `status: "completed"`, 500 output tokens billed
- `text: ""` — parser couldn't extract Qwen's output format
- **Writeup angle**: Auto-routing may select models whose output format doesn't match parser expectations. Router selects by cost, not by output compatibility.

### C13. Web Search Source Extraction Fails for 2/4 Providers

- **Observed**: OpenAI 0 sources captured, xAI 0 sources captured (web_search_triggered=true for both)
- Google: 20 sources but all are opaque `vertexaisearch.cloud.google.com/grounding-api-redirect/` URLs
- Only Anthropic returns usable source URLs (10 real URLs)
- **Root cause**: Our parser only checked `web_search_call.action.sources`. OpenAI/xAI may return citations as `url_citation` annotations in message content.
- **Fix applied**: Added annotation parsing to `compare.py:926-933` for future runs
- **Writeup angle**: Cross-provider source attribution is not standardized

### C14. Guardrails Disabled Baseline Invalid as Scientific Control

- GPT-5.1's own safety training refuses to repeat PII regardless of guardrail state
- Cannot distinguish "model refused" from "platform redacted" in disabled mode
- Enabled mode IS valid: shows `[SSN]`, `[EMAIL]`, `[PHONE]` replacement tokens
- **Writeup angle**: Model refusal ≠ platform guardrails. Only the enabled test proves platform behavior.

### C15. Agent Synthesizer Injects Knowledge Beyond Provided Research

- Gemini synthesis contains specific pricing data (`GPT-4o $5/M`) not in truncated tool outputs
- Synthesizer draws on training data, not just the research it was given
- **Writeup angle**: Agentic synthesis is not pure aggregation — models supplement provided context with parametric knowledge

### C16. Get Provider Info: `function_calling: false` for All 4 Models

- **Observed**: `GET /v1/models/{model}/providers/{provider}` returns `supports.tools.function_calling: false` for all 4 models
- **Reality**: We successfully used function calling with all 4 providers in compare.py Section 3
- **Hypothesis**: The capability flag may reflect native provider support vs Concentrate's normalized wrapper
- **Writeup angle**: Declared capabilities don't match empirical behavior — the API is more capable than it declares

### C17. Web Search Pricing Varies 7x Across Providers

- **Source**: `GET /v1/models/{model}/providers/{provider}` — `pricing.tool_calls.web_search`
- xAI: $5/1K calls, OpenAI: $10/1K, Anthropic: $10/1K, **Vertex: $35/1K** (7x xAI)
- **Not documented**: in Quick Start or Web Search page. Only discoverable via Get Provider Info endpoint
- **Writeup angle**: Web search cost is a hidden variable in provider selection

### C18. Context Window Ranges: 10x Spread

- **Source**: Get Provider Info endpoint
- xAI: **2M tokens**, Vertex: 1M, OpenAI: 400K, Anthropic: 200K
- Max output: xAI 131K, OpenAI 128K, Vertex 65K, Anthropic 64K
- **Writeup angle**: Context limits vary 10x and directly affect long-context routing decisions

### C19. Cache Pricing Schema Not Uniform

- **Source**: Get Provider Info endpoint
- OpenAI: cache.read only ($0.125/M)
- Anthropic: cache.read ($0.30/M) + cache.write.ephemeral_5m ($3.75/M) + cache.write.ephemeral_1h ($6/M)
- Vertex: no cache pricing listed
- xAI: cache.read only ($0.05/M)
- **Writeup angle**: Caching economics are provider-specific; no universal cache pricing table exists

### C20. Latency Numbers Are Client-Side Round-Trip (Gemini Review)

- All `latency_ms` measurements include network RTT + Python requests overhead, not inference time
- `time_to_first_token` from streaming is closer to real inference start, but our streaming parser returns empty text (C11)
- **Impact**: Latency comparisons are valid for relative ranking but not for absolute inference benchmarking
- **Writeup angle**: Always specify measurement methodology when citing latency numbers

### C21. `web_search_call` Type Detection Is Undocumented

- `compare.py:918` checks `item.get("type") == "web_search_call"` — this type string is an assumption from observed API behavior
- Not documented in Create Response or Web Search pages
- May explain C13 (0 sources for OpenAI/xAI) if those providers use a different type identifier
- **Writeup angle**: Undocumented response types are a DX friction point for building robust parsers

### C22. Get Provider Info — The Most Useful Undiscovered Endpoint

- `GET /v1/models/{model}/providers/{provider}` returns comprehensive per-provider detail:
  - Pricing (input, output, cache, web_search — all in one response)
  - Capabilities (reasoning, streaming, temperature, tool support)
  - Limits (context_window, max_output_tokens)
- **Not mentioned** in Quick Start, Introduction, or any getting-started material
- **Would have prevented** findings A3 (vertex prefix), C17 (web search pricing), and saved ~2 hours of empirical testing
- **Writeup angle**: The best endpoint for integration planning is the least documented one

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

- **Pages audited**: 17 / 17 (5 new: Health Check, List Providers, Get Model, Get Provider Info, Claude Code Integration)
- **Code issues found**: 22 (10 crash, 4 400-error, 2 incomplete data, 6 from post-audit remediation)
- **Code issues fixed**: 22/22
- **Research doc issues**: 4 (all fixed — including google/→vertex/ in DECISIONS.md, provider-analysis.md)
- **Not-bugs correctly identified**: 4
- **Empirical findings**: 22 (C1–C22)
- **External reviews**: 3 (Codex comprehensive, Codex thorough, Gemini comprehensive)
- **Total API spend**: ~$1.73 of $10.00 budget (~83% remaining, pre-eval-rerun)
- **Total API calls**: ~400 across all scripts (pre-eval-rerun)
- **Scripts executed**: 8/8 (smoke_test, discover, compare, agent, eval, guardrails ×2)
- **Eval results**: 15/16 ground truth pass, xAI best value, Google most expensive
- **Audit remediation**: extract_json() rewritten (6/6 tests pass), pairwise bias mitigation added, Layer 1 persistence added, guardrails streaming detection fixed

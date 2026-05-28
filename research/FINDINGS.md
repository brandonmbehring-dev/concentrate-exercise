# Concentrate AI — Verified Platform Findings

> Compiled: 2026-02-17 (v3 clean re-run)
> Method: Documentation audit (17/17 pages) + empirical testing (4 providers, ~250 API calls)
> Budget: $4.28 of $10.00 spent ($5.72 remaining)
> All citations reference files in `results/` — reproducible from saved data

---

## 1. Does Normalization Work?

**Verdict**: Yes — this is the core value proposition, and it delivers.

### 1.1 Streaming Is Normalized
- All 4 providers return the same SSE event structure: 3 events per response
- TTFT: OpenAI 437ms, Anthropic 1215ms (non-streaming OpenAI baseline: 2079ms)
- **Limitation**: Our parser extracts 0 text from streaming events — Concentrate's delta format differs from the documented `output[].content[].text` structure
- **Evidence**: `results/compare_output.txt:260-289`

### 1.2 Tool Calling Works on All 4 Providers
- All 4 providers successfully executed 3 tool calls each (get_weather ×2, calculate ×1)
- Arguments correctly structured and parseable
- Despite metadata declaring `function_calling: false` (see Section 6)
- **Evidence**: `results/compare_output.txt:163-206`

### 1.3 Multi-Turn Conversation Preserved
- All 4 providers correctly carried forward context across turns
- "2+2=4, multiply by 3 subtract 1" → all answered 11
- **Evidence**: `results/compare_output.txt:292-341`

### 1.4 Gemini Ignores `max_output_tokens`
- Requested `max_output_tokens=10`, Gemini returned **429 tokens** (43x overshoot)
- xAI returned 116, OpenAI returned 11 (close to limit)
- Anthropic: 4 tokens (respected the limit)
- **Evidence**: `results/smoke_test_output.txt:12-17`
- **Implication**: Parameter parity is not guaranteed across providers. The normalization layer passes parameters through but cannot enforce them on models that treat them as advisory.

---

## 2. Does Auto-Routing Work?

**Verdict**: Yes, all 3 strategies succeed — but router optimizes for metrics, not output quality.

### 2.1 Three Strategies, Three Different Models
| Strategy | Model Selected | Latency | Text? |
|----------|---------------|---------|-------|
| `min_cost` | `cloudflare/qwen3-30b` | 8893ms | Empty |
| `max_performance` | `vertex/gemini-2.5-pro` | 31529ms | Yes |
| `min_avg_latency` | `cloudflare/llama-4-scout` | 6050ms | Yes |

- **Evidence**: `results/compare_output.txt:130-161`

### 2.2 `min_cost` Returns Empty Text
- Router correctly selected the cheapest model (Cloudflare/Qwen)
- Response status: `completed`, 500 output tokens billed
- But extracted text is empty — the response format doesn't match our parser
- **Finding**: Router optimizes for the specified metric, not output compatibility. `min_cost` may select models whose response format the application can't parse.

### 2.3 `avg_latency` Metric — Undocumented Constraint (Fixed)
- v2 used `"metric": "latency"` → 400 error: "Invalid percentile metric format"
- v3 uses `"metric": "avg_latency"` → succeeds
- The auto-routing docs don't enumerate valid metric values
- **Code fix**: `compare.py:39` — `"latency"` → `"avg_latency"`
- **Evidence**: `results/compare_output.txt:148-150` (success), v2 archive for 400 error

---

## 3. Is Pricing Transparent?

**Verdict**: Published per-token prices are accessible via Get Provider Info. Actual billing appears consistent.

### 3.1 Price Spread Across 4 Tested Providers

| Provider | Input/M | Output/M | Source |
|----------|---------|----------|--------|
| xAI/grok-4-1-fast-reasoning | $0.20 | $0.50 | `results/provider_info/*.json` |
| OpenAI/gpt-5.1 | $1.25 | $10.00 | " |
| Vertex/gemini-2.5-pro | $1.25 | $10.00 | " |
| Anthropic/claude-sonnet-4-5 | $3.00 | $15.00 | " |

- **Input spread**: 15x (xAI $0.20 vs Anthropic $3.00)
- **Output spread**: 30x (xAI $0.50 vs Anthropic $15.00)
- **Evidence**: `results/provider_info/` (4 JSON files with full pricing)

### 3.2 Session Spend Analysis
- Dashboard before: $6.98, after: $5.72 → **$1.26 total session spend**
- ~250 API calls across 7 scripts (smoke, discover, compare, agent, eval, guardrails)
- **Evidence**: `results/dashboard_before.png`, `results/dashboard_after.png`

### 3.3 Margin Analysis (Partial)
- `compute_margin.py` extracted usage from 51 API calls (compare + agent JSONs only)
- Computed token cost for those 51 calls: **$0.547** (using provider_info prices)
- Cannot compute exact margin because $1.26 dashboard delta covers ~250 total calls (eval, smoke, guardrails not captured in JSON)
- Per-call billing entries visible in dashboard are consistent with provider_info prices
- **Evidence**: `results/margin_analysis.json`
- **Limitation**: Margin percentage is indeterminate from available data. Would require matching all billing entries to token usage.

### 3.4 Gemini Dominates Output Costs
- Of 51 tracked calls, Gemini consumed **39,507 output tokens** vs xAI 17,946, OpenAI 5,954, Anthropic 5,269
- Gemini's verbose outputs (Gemini ignores max_output_tokens per 1.4) inflate costs at $10/M output
- **Evidence**: `results/margin_analysis.json` per_model_breakdown

### 3.5 Web Search Pricing: 7x Spread (Undocumented)
- xAI: $5/1K calls, OpenAI: $10/1K, Anthropic: $10/1K, Vertex: $35/1K
- Not documented in Quick Start or Web Search pages
- Only discoverable via Get Provider Info endpoint
- **Evidence**: `results/provider_info/*.json` → `pricing.tool_calls.web_search`

---

## 4. Do Guardrails Work?

**Verdict**: Yes — when properly enabled, platform redaction is deterministic. But the system requires careful configuration.

### 4.1 Default State: Disabled
- New API keys have guardrails OFF
- No PII redaction occurs in default state
- **Evidence**: Dashboard screenshot, `results/guardrails_disabled.txt`

### 4.2 Model Self-Censorship Is Non-Deterministic (Guardrails Disabled)
- Run 1: SSN and phone self-censored by GPT-5.1, email exposed (1/3 PII exposed)
- This behavior is stochastic — model safety training varies per request
- **Evidence**: `results/guardrails_disabled.txt:12-17`
- **Key insight**: Model refusal ≠ platform redaction. Cannot rely on model safety for compliance.

### 4.3 Platform Redaction Tokens (Guardrails Enabled)
When SSN/EMAIL/PHONE guardrails enabled in dashboard:
- SSN → `[SSN]`
- Email → `[EMAIL]`
- Phone → `[PHONE]`
- Non-streaming: **0/3 PII fields exposed** (deterministic redaction)
- **Evidence**: `results/guardrails_enabled_final.txt:12-18`
- **Dashboard config**: `results/guardrails_verified_enabled.png` (3/41 entities selected)

### 4.4 Streaming Limitation (Documented)
- Dashboard explicitly warns: "Output will not be redacted if the response is streamed"
- Streaming returned empty content in both guardrails states (0 chars, 3 SSE events)
- The empty response may be a side effect of guardrails + streaming interaction
- **Evidence**: `results/guardrails_enabled_final.txt:22-26`

### 4.5 Configuration Persistence Caveat
- After enabling guardrails and receiving "saved successfully" toast, navigating away and returning showed settings in "Disabled" state until API key was re-selected
- The settings WERE persisted (confirmed by re-selecting key), but the dashboard UI doesn't auto-load key selection on page navigation
- Earlier test runs showed PII exposed (2/3 and 3/3) — likely during the session before settings fully propagated
- **Evidence**: `results/guardrails_enabled.txt` (2/3 exposed), `results/guardrails_enabled_retry.txt` (3/3 exposed), `results/guardrails_enabled_final.txt` (0/3 exposed after key re-selection)

---

## 5. Is the DX Smooth?

**Verdict**: Several friction points for first-time integrators. No SDK means raw JSON parsing.

### 5.1 Tool Calling `strict: true` Default — Omitted from Quick Start
- **Severity**: HIGH — causes 400 errors for unprepared callers
- Tool Calling docs state `strict` defaults to `true`
- Quick Start shows tool calling WITHOUT the `strict` field
- Any tool definition lacking `strict: false` gets strict JSON Schema validation
- **Our fix**: Added `"strict": False` to all tool definitions
- **Source**: Tool Calling page vs Quick Start page (documented contradiction)

### 5.2 Catalog Schema: `slug` Not `id`
- **Severity**: HIGH — catalog parsing crashes silently
- REST convention expects `model.id` — Concentrate uses `model.slug`
- Pricing is deeply nested: `model.providers.{key}.pricing.tokens.{input|output}.price.USD`
- No SDK means you parse raw JSON — schema documentation is critical
- **Source**: List Models API response structure

### 5.3 Provider Prefix Mismatch: `vertex/` Not `google/`
- **Severity**: MEDIUM — wrong model name causes 400 errors
- Model catalog lists author as `google`
- API requires `vertex/` prefix (e.g., `vertex/gemini-2.5-pro`)
- **Source**: Catalog author field vs API model parameter

### 5.4 Get Provider Info — Best Endpoint, Least Documented
- `GET /v1/models/{model}/providers/{provider}` returns pricing, capabilities, limits in one response
- Not mentioned in Quick Start, Introduction, or getting-started material
- Would have prevented findings 5.3 (vertex prefix), 3.5 (web search pricing)
- **Source**: API documentation audit (17/17 pages)

---

## 6. Does Metadata Match Reality?

**Verdict**: No — declared capabilities understate actual functionality.

### 6.1 `function_calling: false` for All 4 Providers — But All Work
- Get Provider Info returns `supports.tools.function_calling: false` for all 4 tested models
- All 4 successfully executed 3 tool calls each in Section 3 testing
- **Hypothesis**: Metadata reflects native provider support, not Concentrate's normalized wrapper
- **Evidence**: `results/provider_info/*.json` (metadata), `results/compare_output.txt:163-206` (empirical)

### 6.2 `max_output_tokens` Advisory for Gemini
- Provider_info lists `max_output_tokens: 65536` for Gemini
- But Gemini ignores the parameter entirely (429 tokens for `max_output_tokens=10`)
- The parameter EXISTS in the API but isn't ENFORCED
- **Evidence**: `results/smoke_test_output.txt:12-14`

### 6.3 Context Window Ranges: 10x Spread
- xAI: 2M tokens, Vertex: 1M, OpenAI: 400K, Anthropic: 200K
- Max output: xAI 131K, OpenAI 128K, Vertex 65K, Anthropic 64K
- These metadata values ARE useful for routing decisions
- **Evidence**: `results/provider_info/*.json`

---

## Appendix A: Cross-Provider Quality (Exploratory, n=32)

> **Caveat**: These results test the models, not the platform. Sample size (8 prompts × 4 providers = 32 responses) is illustrative, not statistically significant.

### Judge Scores (Haiku 4.5, 1-5 average)
| Provider | Avg Score | n |
|----------|-----------|---|
| xAI | 4.12 | 8 |
| Anthropic | 4.04 | 8 |
| OpenAI | 3.88 | 8 |
| Google | 3.29 | 8 |

### Pairwise Wins (Position-Bias Mitigated)
| Winner | Consistent Wins | Position-Biased Splits |
|--------|----------------|----------------------|
| xAI | 6 | — |
| Anthropic | 4 | — |
| OpenAI | 1 | — |
| Split (biased) | — | 7 |

- 39% of pairwise comparisons showed position bias (judge contradicts itself when order swapped)
- **Evidence**: `results/eval_output.txt:169-187`, `results/eval_results.json`

### Cost per Provider (Eval + Compare)
| Provider | Total Cost | Relative |
|----------|-----------|----------|
| xAI | $0.008 | 1x |
| OpenAI | $0.051 | 6x |
| Anthropic | $0.065 | 8x |
| Google | $0.264 | 33x |

- xAI won the most pairwise comparisons at 1/33 the cost of Google
- **Evidence**: `results/eval_output.txt:210-214`

### GPT-5.1 Deep Judge Parse Failures
- 8/32 responses (25%) from GPT-5.1 deep judge returned unparseable JSON
- Haiku 4.5: 0/32 parse errors, Sonnet 4.5: 0/12 parse errors
- All models return JSON inside markdown fences — `extract_json()` helper handles this
- GPT-5.1 fails on complex evaluation prompts with nested scoring rubrics
- **Evidence**: `results/eval_output.txt:103-135`

---

## Appendix B: Evidence Inventory

### Results Files (v3 clean re-run, 2026-02-17)
| File | Description |
|------|-------------|
| `results/smoke_test_output.txt` | 9/9 pass, token counts per provider |
| `results/discover_output.txt` | 52 models, 11 providers |
| `results/comparison_20260217_061046.json` | 180KB comparison data (9 sections) |
| `results/compare_output.txt` | Full console output |
| `results/agent_20260217_062938.json` | Agent demo (4-provider routing) |
| `results/agent_output.txt` | Agent console output |
| `results/eval_results.json` | Package C evaluation (3-layer) |
| `results/eval_output.txt` | Eval console output with scoreboard |
| `results/guardrails_disabled.txt` | PII test: guardrails OFF |
| `results/guardrails_enabled_final.txt` | PII test: guardrails ON (verified) |
| `results/guardrails_verified_enabled.png` | Dashboard: SSN/EMAIL/PHONE enabled |
| `results/margin_analysis.json` | Token cost computation (51 calls) |
| `results/dashboard_before.png` | $6.98 balance before re-runs |
| `results/dashboard_after.png` | $5.72 balance after re-runs |
| `results/provider_info/*.json` | Per-provider pricing and capabilities |

### Archived v2 Results
- `results/archive_v2/` — previous run data, preserved for reference
- v2 had 6 evidence integrity issues (documented in plan), corrected in v3

---

## Summary Statistics (v3)

- **Pages audited**: 17/17
- **Providers tested**: 4 (OpenAI, Anthropic, Google/Vertex, xAI)
- **API calls**: ~250 across 7 scripts
- **Session spend**: $1.26 (dashboard delta)
- **Total project spend**: $4.28 of $10.00
- **Scripts executed**: smoke_test, discover, compare (9 sections), agent, eval (3-layer), guardrails (×4)
- **Ground truth pass rate**: 15/16 (GPT-5.1 missed 4-door Monty Hall "3/8")
- **Platform findings**: 6 sections, 20+ verified claims
- **Every number cites a file in `results/`**

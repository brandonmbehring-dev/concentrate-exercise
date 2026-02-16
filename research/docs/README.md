# Concentrate AI — Documentation Captures

> Fetched: 2026-02-16 (updated: 5 new pages added post-audit)
> Method: Playwright browser_snapshot (Claude Code) — full accessibility tree + clean markdown
> Purpose: Verbatim documentation for quoting API inconsistencies in writeup
> Coverage: **17/17 pages** — complete

## Contents

### Original Captures (01-11): Playwright raw accessibility trees
| File | Source Page | Key Content |
|------|-----------|-------------|
| `00-llms-index.md` | `/llms.txt` | Full 17-page index |
| `01-introduction.md` | `/api-reference/introduction` | Auth, base URL, model selection |
| `02-quickstart.md` | `/getting-started/quickstart` | First API call, default model (gpt-5.2) |
| `03-create-response.md` | `/api-reference/endpoint/create-response` | Main endpoint, response structure |
| `04-request-parameters.md` | `/api-reference/endpoint/request-parameters` | COMPLETE parameter reference |
| `05-tool-calling.md` | `/api-reference/endpoint/tool-calling` | FunctionTool schema, strict default |
| `06-list-models.md` | `/api-reference/endpoint/list-models` | OpenAPI schema (CRITICAL for parsing) |
| `07-web-search.md` | `/api-reference/endpoint/web-search` | Filters, user_location, limitations |
| `08-streaming.md` | `/api-reference/endpoint/streaming` | SSE event types, lifecycle |
| `09-auto-routing.md` | `/api-reference/endpoint/auto-routing` | Metrics, strategy, interval |
| `10-errors.md` | `/api-reference/endpoint/errors` | Error format, HTTP codes |
| `11-prompt-caching.md` | `/api-reference/endpoint/prompt-caching` | Anthropic-only, TTL, pricing |

### New Captures (12-17): Clean markdown summaries
| File | Source Page | Key Content |
|------|-----------|-------------|
| `12-health-check.md` | `/api-reference/endpoint/health` | No-auth health ping, monitoring patterns |
| `13-list-providers.md` | `/api-reference/endpoint/list-providers` | 10 providers, canonical slugs + aliases |
| `14-get-model.md` | `/api-reference/endpoint/get-model` | Single-model lookup, author vs provider slug |
| `15-get-provider-info.md` | `/api-reference/endpoint/get-provider-info` | **Most valuable**: capabilities, pricing, limits |
| `16-claude-code.md` | `/integrations/claude-code` | Beta, Messages API, config |
| `17-create-message.md` | `/api-reference/endpoint/create-message` | Beta Messages API, proper stop_reason enum |

### API Response Data
| File | Description |
|------|-------------|
| `../results/provider_info/gpt-5.1_openai.json` | Get Provider Info raw response |
| `../results/provider_info/claude-sonnet-4-5_anthropic.json` | Get Provider Info raw response |
| `../results/provider_info/gemini-2.5-pro_vertex.json` | Get Provider Info raw response |
| `../results/provider_info/grok-4-1-fast-reasoning_xai.json` | Get Provider Info raw response |

## Usage

These files are reference artifacts. Quote from them when citing documentation
inconsistencies in the writeup. See `../FINDINGS.md` for the discrepancy log.

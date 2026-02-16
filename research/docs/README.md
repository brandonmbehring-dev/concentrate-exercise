# Concentrate AI — Documentation Captures

> Fetched: 2026-02-16
> Method: Playwright browser_snapshot (Claude Code) — full accessibility tree capture
> Purpose: Verbatim documentation for quoting API inconsistencies in writeup

## Contents

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

## Pages NOT Captured (Low Priority)

- Create Message (Anthropic compat, beta)
- Get Model / Get Provider Info (single-model lookups)
- List Providers (provider directory)
- Health Check (simple ping)
- Claude Code integration (beta)

## Usage

These files are reference artifacts. Quote from them when citing documentation
inconsistencies in the writeup. See `../FINDINGS.md` for the discrepancy log.

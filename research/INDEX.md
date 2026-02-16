# Concentrate AI Exercise — Research Index

> **Quick Reference**: Read this first. Everything else is deep context.

## Quick Reference (10 Key Facts for Code Decisions)

| # | Fact | Value |
|---|------|-------|
| 1 | API Base URL | `https://api.concentrate.ai` |
| 2 | Auth Header | `Authorization: Bearer sk-cn-v1-...` |
| 3 | Main Endpoint | `POST /v1/responses/` |
| 4 | Models Endpoint | `GET /v1/models/` |
| 5 | OpenAI Model | `openai/gpt-5.1` |
| 6 | Anthropic Model | `anthropic/claude-sonnet-4-5` |
| 7 | Google Model | `vertex/gemini-2.5-pro` |
| 8 | xAI Model | `xai/grok-4-1-fast-reasoning` |
| 9 | Streaming | SSE via `stream: true` |
| 10 | No SDK | HTTP requests only (requests, fetch, curl) |

## File Map

| File | Contents | Plan Sections |
|------|----------|---------------|
| [`api-reference.md`](api-reference.md) | Complete API docs, endpoints, params, streaming, errors, caching, tools | 3, 4, 14, 16 |
| [`provider-analysis.md`](provider-analysis.md) | 4 providers: pricing, capabilities, decision matrix | 10, 17 |
| [`prompt-strategy.md`](prompt-strategy.md) | 8 research-backed prompts + 3-tier eval approach | 18, 19 |
| [`exercise-strategy.md`](exercise-strategy.md) | D-Lite structure, writeup format, agent Qs, execution sequence | 20, 21, 22 |
| [`company-and-role.md`](company-and-role.md) | JD decode, company background, culture signals | 1, 2 |
| [`brainstorm-archive.md`](brainstorm-archive.md) | All 30 prompts, 7 agent Qs, 4 structures, 3 writeup formats | 6, 7, 8, 9 |
| [`DECISIONS.md`](DECISIONS.md) | ADR-style decision log (shareable — can go in production repo) | 22 |
| [`PREP_CHECKLIST.md`](PREP_CHECKLIST.md) | Interview prep checklist (private — research repo only) | 22 |
| [`FINDINGS.md`](FINDINGS.md) | API discrepancy log from doc audit (16 issues, 4 categories) | Writeup |
| [`docs/`](docs/) | Verbatim Playwright captures of 12 API documentation pages | Reference |

## Critical Reminders

- **GPT-4.1 is RETIRED** — using `openai/gpt-5.1`
- **Run `smoke_test.py` FIRST** to confirm setup, then `discover.py` for catalog
- **Writeup is 60% of evaluation** — budget 60 min minimum
- **Zach offered unlimited credits** — no cost constraint
- **Deadline**: Feb 18, 2026 (Tuesday)

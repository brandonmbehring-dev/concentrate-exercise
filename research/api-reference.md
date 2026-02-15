# Concentrate API — Complete Reference

## Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/v1/responses/` | POST | Yes | Main completion endpoint |
| `/v1/messages/` | POST | Yes | Anthropic Messages API compat (beta) |
| `/v1/models/` | GET | No | Model catalog with pricing |
| `/v1/models/{model}` | GET | No | Specific model details |
| `/v1/models/{model}/providers/{provider}` | GET | No | Provider-specific info |
| `/v1/models/providers` | GET | No | List all providers |
| `/v1/responses/health/` | GET | No | Health check |

---

## Request Parameters (POST /v1/responses/)

### Required
- `model` (string) — provider/model format, e.g. `openai/gpt-5`
- `input` (string | array) — prompt text or array of message objects

### Sampling
- `temperature` (0–2)
- `top_p` (0–1)
- `max_output_tokens` (int)

### Features
- `stream` (bool) — SSE streaming
- `tools` (array) — function / web_search / custom
- `tool_choice` — `"none"` | `"auto"` | `"required"` | specific
- `parallel_tool_calls` (bool)
- `routing` — `{strategy: "min"|"max", metric, interval}`
- `reasoning` — `{effort: "low"|"medium"|"high", summary}`
- `cache_control` — `{type: "ephemeral", ttl: "5m"|"1h"}`
- `metadata`, `user`, `store`

### Multi-turn Input Format
```python
input=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "Paris."},
    {"role": "user", "content": "And what language do they speak?"}
]
```

---

## Auto-Routing

### Metrics
cost, performance, avg_latency, min/max_latency, p50/p90/p99_latency, avg/min/max_e2e_latency, uptime, throughput, total_requests, input/output/total_tokens

### Example
```python
routing={"strategy": "min", "metric": "cost", "interval": "24h"}
```

---

## Streaming (SSE)

### Event Lifecycle
`response.created` → `response.in_progress` → `response.output_item.added` → `response.content_part.added` → `response.output_text.delta` (repeated) → `response.output_text.done` → `response.content_part.done` → `response.output_item.done` → `response.completed`

### Error Events
- `response.failed` — provider or server error
- `response.incomplete` — length, content filter, turn limit

### Tool Calling Events
`response.function_call_arguments.delta` → `response.function_call_arguments.done`

### Reasoning Events
`response.reasoning_summary_text.delta` — for models with `reasoning` param

### Best Practices
- Reconnect on network errors
- Set appropriate timeouts
- Buffer partial events
- Handle `[DONE]` signal for stream end
- Client disconnect: `disconnect_on_done: true` or close connection

---

## Tool Types

### Function Calling
```python
{"type": "function", "name": "get_weather", "description": "...", "parameters": {...}, "strict": True}
```

### Web Search
```python
{"type": "web_search", "search_context_size": "medium", "filters": {"allowed_domains": [...]}, "user_location": {...}}
```
- **Supported**: OpenAI, Anthropic, xAI, Vertex (limited), Mistral (limited)
- **Limitation**: Gemini/Mistral can't combine web search + function tools
- **Options**: `search_context_size` (low/medium/high), `filters.allowed_domains`, `user_location`

### Custom
```python
{"type": "custom", "name": "...", "description": "...", "format": "..."}
```

---

## Prompt Caching

- **Supported**: Anthropic, AWS Bedrock (Claude only)
- **Write cost**: ~1.25x input cost
- **Read cost**: ~90% cheaper than input
- **Break-even**: 2–3 requests with same prefix
- **TTL options**: `"5m"` or `"1h"`

```python
cache_control={"type": "ephemeral", "ttl": "5m"}
```

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error type or message",
  "message": "Detailed explanation (optional)",
  "model": "provider/model (for provider errors only)"
}
```

### Status Codes

| Code | Type | Causes | Solutions |
|------|------|--------|-----------|
| 400 | Bad Request | Invalid model name, missing fields, invalid params | Fix request payload |
| 401 | Unauthorized | Missing/invalid/revoked key, wrong header format | Check `Authorization: Bearer sk-cn-...` |
| 402 | Payment Required | Low balance, would exceed limit, free tier exhausted | Add credits, cheaper models, min-cost routing |
| 424 | Failed Dependency | Provider outage, model unavailable, regional restrictions | Retry with backoff, use `model: "auto"` |
| 429 | Too Many Requests | RPM/TPM/burst limit exceeded | Rate limit, exponential backoff, batch requests |
| 500 | Internal Server Error | Temporary server issue, provider internal error | Retry after delay |

**429 detail**: Response includes `retry_after` field (seconds) and `Retry-After` header.

---

## Claude Code Integration (Beta)

- **Setup**: `ANTHROPIC_BASE_URL=https://api.concentrate.ai`
- **VS Code**: `"claude-code.apiKeyHelper": "echo sk-cn-v1-YOUR_KEY"`
- **Supported models**: Claude Sonnet 4.5, Claude Haiku 3.5, GPT-4o, GPT-5, Gemini 2.5 Pro
- **Limitations**: No multi-modal support (images/audio not passed through)
- Worth mentioning in writeup as DX feature

---

## Model Retirement (CRITICAL)

**GPT-4o, GPT-4.1, GPT-4.1 mini, o4-mini retiring Feb 13–19, 2026.**
- Current code uses `openai/gpt-4.1` → MUST update to `openai/gpt-5`
- Docs quickstart default: `gpt-5.2`
- Run `discover.py` first to confirm available models

---

## Documentation Gaps (Test Empirically)

1. **Rate limits**: No specific RPM/TPM numbers documented
2. **Model catalog freshness**: How quickly are new models added?
3. **Messages API (Beta)**: Minimal docs — what's exact parity with Anthropic?
4. **Reasoning params**: Which models support `reasoning.effort`?
5. **Web search**: Does it work with all claimed providers?
6. **`store` param**: What does `store: true` do exactly?

## Potential Friction Points (Document in Writeup)

1. No official SDK — manual HTTP only
2. GPT-4.1 retirement timing vs documentation freshness
3. Claude Code integration is "Beta"
4. Prompt caching only for Anthropic — cross-provider parity gap
5. Web search + function tools can't be combined on some providers
6. No WebSocket streaming (SSE only)

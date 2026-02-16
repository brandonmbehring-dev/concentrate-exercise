# Get Provider Info — `GET /v1/models/{model}/providers/{provider}`

> Source: https://docs.concentrate.ai/api-reference/endpoint/get-provider-info
> Captured: 2026-02-16 (with live API verification)

## Overview

Returns per-provider capabilities, pricing, and limits for a specific model. **No authentication required.** This is arguably the most useful endpoint for integration planning — yet it's not mentioned in the Quick Start or Introduction.

## Request

```
GET https://api.concentrate.ai/v1/models/{model}/providers/{provider}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model slug (e.g. `gpt-5.1`, `claude-sonnet-4-5`) |
| `provider` | string | Provider slug (e.g. `openai`, `anthropic`, `vertex`, `xai`) |

## Response Schema

```json
{
  "provider_slug": "<string>",
  "pricing": {
    "tokens": {
      "input": { "price": { "USD": <float> }, "units": 1000000 },
      "output": { "price": { "USD": <float> }, "units": 1000000 },
      "cache": {
        "read": { "price": { "USD": <float> }, "units": 1000000 },
        "write": {
          "ephemeral_5m_input_tokens": { "price": { "USD": <float> }, "units": 1000000 },
          "ephemeral_1h_input_tokens": { "price": { "USD": <float> }, "units": 1000000 }
        }
      }
    },
    "tool_calls": {
      "web_search": { "price": { "USD": <float> }, "units": 1000 }
    }
  },
  "context_window": <int>,
  "max_output_tokens": <int>,
  "supports": {
    "reasoning": <bool>,
    "streaming": <bool>,
    "temperature": <bool>,
    "tools": {
      "function_calling": <bool>,
      "web_search": <bool>
    }
  }
}
```

## Empirical Results (Our 4 Models)

### Pricing Comparison

| Model | Input $/M | Output $/M | Cache Read $/M | Web Search $/1K |
|-------|-----------|------------|----------------|-----------------|
| gpt-5.1/openai | $1.25 | $10.00 | $0.125 | $10.00 |
| claude-sonnet-4-5/anthropic | $3.00 | $15.00 | $0.30 | $10.00 |
| gemini-2.5-pro/vertex | $1.25 | $10.00 | — | **$35.00** |
| grok-4-1-fast-reasoning/xai | $0.20 | $0.50 | $0.05 | $5.00 |

### Context Windows

| Model | Context Window | Max Output |
|-------|---------------|------------|
| grok-4-1-fast-reasoning/xai | **2,000,000** | 131,072 |
| gemini-2.5-pro/vertex | **1,000,000** | 65,536 |
| gpt-5.1/openai | 400,000 | 128,000 |
| claude-sonnet-4-5/anthropic | 200,000 | 64,000 |

### Capabilities

All 4 models declare: `reasoning: true`, `streaming: true`, `temperature: true`, `web_search: true`.

**Anomaly**: All 4 declare `function_calling: false` — yet we successfully used function calling in compare.py Section 3. See Finding C16.

### Cache Pricing (Provider-Specific)

- **OpenAI**: Read only ($0.125/M) — 90% discount vs input
- **Anthropic**: Read ($0.30/M) + Write with 5-minute TTL ($3.75/M) and 1-hour TTL ($6.00/M)
- **Vertex**: No cache pricing listed
- **xAI**: Read only ($0.05/M) — 75% discount vs input

## Key Findings

1. **Web search pricing varies 7x**: xAI $5/1K vs Vertex $35/1K (Finding C17)
2. **Context windows vary 10x**: xAI 2M vs Anthropic 200K (Finding C18)
3. **function_calling: false for all models** despite working empirically (Finding C16)
4. **Cache pricing is not uniform** across providers (Finding C19)
5. **This endpoint would have prevented Finding A3** (vertex prefix confusion)

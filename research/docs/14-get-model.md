# Get Model — `GET /v1/models/{model}`

> Source: https://docs.concentrate.ai/api-reference/endpoint/get-model
> Captured: 2026-02-16

## Overview

Retrieve detailed information about a specific AI model, including all available providers, pricing, context windows, and supported features. **No authentication required.**

## Request

```
GET https://api.concentrate.ai/v1/models/{model}
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model identifier. Supports canonical names (e.g. `gpt-4o`, `claude-opus-4-6`), aliases, and provider-prefixed formats (e.g. `openai/gpt-4o`). Use `"auto"` for automatic model selection. |

## Response (200)

```json
{
  "slug": "<string>",
  "aliases": ["<string>"],
  "name": "<string>",
  "description": "<string>",
  "author": {
    "slug": "openai",
    "display_name": "<string>"
  },
  "providers": {}
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `slug` | string | Canonical model identifier (e.g. `gpt-5.1`) |
| `aliases` | string[] | Alternative names that resolve to this model |
| `name` | string | Human-readable model name |
| `description` | string | Model description |
| `author` | object | Author info (`slug`, `display_name`) |
| `providers` | object | Per-provider capabilities, pricing, and limits |

## Key Observations

- The `author.slug` field uses `google` but the provider slug (and routing prefix) is `vertex`. This is the root cause of Finding A3.
- The `providers` object keys are provider slugs (e.g., `openai`, `vertex`), not author slugs.
- Use `GET /v1/models/{model}/providers/{provider}` for detailed per-provider info.

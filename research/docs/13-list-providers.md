# List Providers — `GET /v1/models/providers`

> Source: https://docs.concentrate.ai/api-reference/endpoint/list-providers
> Captured: 2026-02-16

## Overview

Retrieve the complete list of AI providers available through Concentrate AI. Returns all providers with their slugs, display names, and aliases. **No authentication required.**

## Request

```
GET https://api.concentrate.ai/v1/models/providers
```

## Response (200)

Array of provider objects:

```json
[
  {
    "slug": "openai",
    "display_name": "OpenAI",
    "aliases": ["open-ai", "oai"]
  }
]
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `slug` | enum\<string\> | Canonical provider identifier |
| `display_name` | string | Human-readable provider name |
| `aliases` | enum\<string\>[] | Alternative identifiers that resolve to this provider |

### Provider Slugs (Canonical)

| Slug | Display Name | Aliases |
|------|-------------|---------|
| `openai` | OpenAI | open-ai, oai |
| `anthropic` | Anthropic | anthropic-ai |
| `azure` | Azure | microsoft, microsoft-azure, ms-azure |
| `bedrock` | AWS Bedrock | aws, aws-bedrock, amazon, amazon-bedrock |
| `xai` | xAI | x-ai, grok |
| `cohere` | Cohere | *(none)* |
| `mistral` | Mistral | mistralai |
| `vertex` | Google Vertex AI | google-vertex, vertex-ai |
| `cloudflare` | Cloudflare | cf, cloudflare-ai |
| `huggingface` | Hugging Face | hf, hugging-face |

## Key Finding

**`vertex` is the canonical slug, not `google`.** The catalog's `author.slug` field returns `google` but the API routing prefix must use `vertex/`. This endpoint would have prevented Finding A3 entirely.

## Our Testing Coverage

We tested 4/10 providers: openai, anthropic, vertex, xai.
Untested: azure, bedrock, cohere, mistral, cloudflare, huggingface.

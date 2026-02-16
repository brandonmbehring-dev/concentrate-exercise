# Create Message — `POST /v1/messages/`

> Source: https://docs.concentrate.ai/api-reference/endpoint/create-message
> Captured: 2026-02-16

## Overview

Beta endpoint implementing the Anthropic Messages API format. Primary use case is Claude Code integration, but available for any client that uses the Messages format.

## Request

```
POST https://api.concentrate.ai/v1/messages/
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## Response

Has proper `stop_reason` enum values:
- `end_turn` — model finished naturally
- `max_tokens` — hit token limit
- `stop_sequence` — hit a stop sequence
- `tool_use` — model wants to use a tool

## Content Types

The Messages API supports richer content types than the Responses API:
- **Text** — Standard text content
- **Image** — Image content (base64 or URL)
- **Thinking** — Chain-of-thought reasoning blocks
- **Tool Use** — Tool invocation requests
- **Tool Result** — Results from tool execution
- **Server Tool Use** — Server-side tool calls
- **Web Search Result** — Web search results

## Key Observations

- The `stop_reason` enum is more informative than the Responses API, where our results always show `null`
- "Thinking" content type suggests reasoning/chain-of-thought support
- Beta status means the API may change without notice
- This is the only endpoint that explicitly supports the Anthropic message format

## Relevance to Our Exercise

Not tested. The proper `stop_reason` values would have been useful for understanding why responses truncate (Finding C1: Gemini ignoring max_output_tokens).

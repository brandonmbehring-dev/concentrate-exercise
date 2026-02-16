# Claude Code Integration — `/integrations/claude-code`

> Source: https://docs.concentrate.ai/integrations/claude-code
> Captured: 2026-02-16

## Overview

Beta integration for using Claude Code (Anthropic's CLI) through Concentrate AI's unified API. Uses the **Messages API** (`POST /v1/messages/`), not the Responses API.

## Configuration

```bash
# Set environment variables
export ANTHROPIC_BASE_URL=https://api.concentrate.ai
```

In Claude Code config (or `~/.claude.json`):
```json
{
  "apiKeyHelper": "echo $CONCENTRATE_API_KEY"
}
```

## Key Points

- Uses Messages API endpoint (`POST /v1/messages/`) — separate from main Responses API
- Mentions `gemini-3-pro-preview` as available — newer than our `gemini-2.5-pro`
- **Limitations**: No multi-modal support, some models may not be compatible
- Beta feature — API may change

## Messages API vs Responses API

| Feature | Messages API | Responses API |
|---------|-------------|---------------|
| Endpoint | `POST /v1/messages/` | `POST /v1/responses/` |
| Format | Anthropic Messages format | OpenAI-compatible format |
| Status | Beta | Stable |
| Primary use | Claude Code integration | General-purpose |
| `stop_reason` | Proper enum (`end_turn`, `max_tokens`, `stop_sequence`, `tool_use`) | Always null in our results |

## Relevance to Our Exercise

We did not test the Messages API. It's listed in Category D (Untested Features) as "DX feature worth watching." The proper `stop_reason` enum is notable — our Responses API results always show `stop_reason: null`.

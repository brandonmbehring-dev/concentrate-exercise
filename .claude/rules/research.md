---
paths:
  - "**/*.py"
  - "README.md"
  - "research/**"
---
# Research Context

All exercise research is in `research/`. Key files:
- `research/INDEX.md` — master reference (read FIRST before any code decisions)
- `research/api-reference.md` — complete Concentrate API docs
- `research/provider-analysis.md` — 4 providers with pricing + decision matrix
- `research/prompt-strategy.md` — 8 research-backed prompts + 3-tier eval approach
- `research/exercise-strategy.md` — D-Lite structure, execution sequence, writeup format

## Critical Facts
- GPT-4.1 is RETIRED — use `openai/gpt-5` or newer
- 4 providers: OpenAI, Anthropic, Google Gemini, DeepSeek
- Writeup is 60% of evaluation — protect writeup time
- Run `discover.py` first to confirm model names

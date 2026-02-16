# Provider Analysis — 4 Providers Selected

## Decision: OpenAI + Anthropic + Google Gemini + xAI

### Models Configuration
```python
MODELS = {
    "openai": "openai/gpt-5.1",
    "anthropic": "anthropic/claude-sonnet-4-5",
    "google": "vertex/gemini-2.5-pro",
    "xai": "xai/grok-4-1-fast-reasoning",
}
```

---

## Provider Profiles

### OpenAI (`openai/gpt-5.1`)
- **Role in comparison**: The incumbent / default choice — Comparator
- **Strengths**: Best structured output (100% JSON schema compliance natively), strong tool calling, massive ecosystem
- **Pricing**: $1.25/M input, $10.00/M output
- **Note**: gpt-4.1 RETIRED Feb 13-19. Using gpt-5.1.

### Anthropic (`anthropic/claude-sonnet-4-5`)
- **Role in comparison**: The reasoning/safety leader — Planner
- **Strengths**: Strong reasoning, best at nuanced prompts, prompt caching support
- **Pricing**: $3.00/M input, $15.00/M output
- **Note**: Only provider (with Bedrock) that supports prompt caching on Concentrate

### Google Gemini (`vertex/gemini-2.5-pro`)
- **Role in comparison**: The capability leader — Synthesizer
- **Strengths**: #1 Chatbot Arena (1439), 1M-2M token context, native multimodal, IMO 2025 gold medal
- **Weaknesses**: Premium output pricing, limited web search on Concentrate
- **Pricing**: $1.25/M input, $10.00/M output
- **Strategic fit**: JD explicitly says "Gemini" — not including it would be an omission

### xAI (`xai/grok-4-1-fast-reasoning`)
- **Role in comparison**: The cost disruptor — Researcher
- **Strengths**: 75x cheaper input than Anthropic, strong reasoning, fast inference
- **Weaknesses**: Newer ecosystem, less established tooling
- **Pricing**: $0.20/M input, $0.50/M output
- **Strategic fit**: Creates the cost-quality spectrum that IS Concentrate's value prop

---

## Decision Matrix

| Criterion | Gemini | xAI | Mistral | Cohere |
|-----------|--------|-----|---------|--------|
| JD alignment | **Explicit** | Good (cost story) | Indirect | None |
| Comparison interest | High (capability) | **High (cost)** | Medium | Low |
| Narrative value | "The Big 3" | "The cost disruptor" | "The OSS coder" | "The RAG specialist" |
| Writeup material | Good | **Excellent** | OK | Thin |

---

## Cost-Quality Spectrum

The 4 providers create a clear spectrum — this IS Concentrate's value proposition:

```
xAI (cheapest)     → OpenAI (mid)     → Google (mid)        → Anthropic (premium)
$0.20/M input        $1.25/M            $1.25/M               $3.00/M
$0.50/M output       $10.00/M           $10.00/M              $15.00/M
```

Smart routing across this spectrum = Concentrate's core product story.
75x input price spread between xAI and Anthropic. 30x output price spread.

---

## Why Not Others?

| Provider | Why Excluded |
|----------|-------------|
| DeepSeek | Replaced by xAI — grok-4-1-fast-reasoning is strictly better (cheaper, faster, stronger reasoning) |
| Mistral | Overlaps with xAI in cost-optimization category, less interesting spread |
| Cohere | Niche (RAG-focused), not in JD, doesn't add to core comparison narrative |

---

## Amendment (2026-02-16): DeepSeek → xAI Switch

**Rationale**: xAI's grok-4-1-fast-reasoning ($0.20/$0.50) is strictly cheaper than
DeepSeek's deepseek-chat ($0.27-0.55/$1.10-2.19) while providing stronger reasoning
and faster inference. The cost-quality spectrum narrative is even stronger with xAI:
75x cheaper input than Anthropic vs DeepSeek's 20-50x. No downside to the switch.

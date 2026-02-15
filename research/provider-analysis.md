# Provider Analysis — 4 Providers Selected

## Decision: OpenAI + Anthropic + Google Gemini + DeepSeek

### Models Configuration
```python
MODELS = {
    "openai": "openai/gpt-5",
    "anthropic": "anthropic/claude-sonnet-4-5-20250929",
    "google": "google/gemini-2.5-pro",
    "deepseek": "deepseek/deepseek-chat",
}
```

---

## Provider Profiles

### OpenAI (`openai/gpt-5`)
- **Role in comparison**: The incumbent / default choice
- **Strengths**: Best structured output (100% JSON schema compliance natively), strong tool calling, massive ecosystem
- **Pricing**: Mid-range (~$2-5/M input, $8-15/M output)
- **Note**: gpt-4.1 RETIRED Feb 13-19. Must use gpt-5 or newer.

### Anthropic (`anthropic/claude-sonnet-4-5-20250929`)
- **Role in comparison**: The reasoning/safety leader
- **Strengths**: Strong reasoning, best at nuanced prompts, prompt caching support
- **Pricing**: Mid-high (~$3/M input, $15/M output)
- **Note**: Only provider (with Bedrock) that supports prompt caching on Concentrate

### Google Gemini (`google/gemini-2.5-pro`)
- **Role in comparison**: The capability leader
- **Strengths**: #1 Chatbot Arena (1439), 1M-2M token context, native multimodal, IMO 2025 gold medal
- **Weaknesses**: Premium pricing (4.1x more than DeepSeek), limited web search on Concentrate
- **Pricing**: Premium (~$2/M input, $12/M output)
- **Strategic fit**: JD explicitly says "Gemini" — not including it would be an omission

### DeepSeek (`deepseek/deepseek-chat`)
- **Role in comparison**: The cost disruptor / OSS representative
- **Strengths**: 20-50x cheaper than GPT o1, open-source (Apache 2.0), strong math/reasoning
- **Weaknesses**: 128K context (smallest), limited multimodal
- **Pricing**: ~$0.27-0.55/M input, $1.10-2.19/M output
- **Strategic fit**: JD says "OSS". Creates the cost-quality spectrum that IS Concentrate's value prop

---

## Decision Matrix

| Criterion | Gemini | DeepSeek | Mistral | Cohere |
|-----------|--------|----------|---------|--------|
| JD alignment | **Explicit** | **"OSS"** | Indirect | None |
| Comparison interest | High (capability) | **High (cost)** | Medium | Low |
| Narrative value | "The Big 3" | "The cost disruptor" | "The OSS coder" | "The RAG specialist" |
| Writeup material | Good | **Excellent** | OK | Thin |

---

## Cost-Quality Spectrum

The 4 providers create a clear spectrum — this IS Concentrate's value proposition:

```
DeepSeek (cheapest) → OpenAI (mid) → Anthropic (mid-high) → Gemini (premium)
$0.27/M input         $2-5/M         $3/M                   $2/M (but $12/M output)
```

Smart routing across this spectrum = Concentrate's core product story.

---

## Why Not Others?

| Provider | Why Excluded |
|----------|-------------|
| xAI/Grok | Eliminated by Brandon (political concerns) |
| Mistral | Overlaps with DeepSeek in "OSS" category, less interesting cost story |
| Cohere | Niche (RAG-focused), not in JD, doesn't add to core comparison narrative |

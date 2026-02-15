# Prompt Strategy — 8 Research-Backed Prompts + Eval

## Research Findings (Why These Prompts)

1. **Statistical reasoning prompts are THE best diagnostic** — OpenAI o1-preview: 30% → 90% on Simpson's Paradox with "think like a careful statistician". Sensitivity to prompting = a finding worth documenting.
2. **Structured output compliance is #1 cross-provider differentiator** — OpenAI 100% JSON natively; Anthropic needs tool-calling workaround; Google has limitations. Measurable, objective.
3. **Logic puzzle VARIANTS beat classics** — 4-door Monty Hall separates true reasoning from memorized training data.
4. **Constrained creative writing reveals stylistic fingerprints** — GPT embellishes, Claude minimizes. Measurable instruction-following.
5. **LLM meta-questions are risky** — Models bias toward own capabilities. Use sparingly (1 max).

---

## The 8 Prompts

### Prompt 1: Simpson's Paradox (Causal Reasoning)
```
A hospital has two treatments for a condition. Treatment A has a higher
success rate in every patient subgroup (mild cases: 90% vs 85%, severe
cases: 40% vs 35%), but Treatment B has a higher overall success rate
(80% vs 75%). Explain how this is mathematically possible, identify the
bias, and recommend which treatment to choose.
```
**Why**: Objectively verifiable, reveals reasoning depth, shows YOUR causal inference expertise.
**Eval**: Check for "confounding" / "Simpson's Paradox" / correct math explanation.

### Prompt 2: A/B Test Interpretation (Statistical Reasoning)
```
An A/B test shows the new checkout flow has 3% higher conversion
(p=0.04, n=5000 per group), but the Bayesian posterior puts 15%
probability on no real effect. The PM wants to ship immediately.
What do you recommend and why?
```
**Why**: No single right answer — quality of statistical reasoning is evaluable.
**Eval**: Check for frequentist vs Bayesian nuance, practical recommendation.

### Prompt 3: JSON Schema Compliance (THE Differentiator)
```
Generate a JSON error response for an API with this exact schema:
{error_code: int, message: string, timestamp: ISO 8601,
request_id: UUID v4, details: {field: string, constraint: string,
received_value: any}[]}. Generate exactly 3 error examples.
```
**Why**: #1 cross-provider differentiator. OpenAI should nail it; others may struggle.
**Eval**: Parse JSON, validate against schema, check field types.

### Prompt 4: 4-Door Monty Hall Variant (Logic — Anti-Memorization)
```
You're on a game show with 4 doors. Behind one is a car, behind the
others are goats. You pick door 1. The host, who knows what's behind
each door, opens door 3 (goat). Should you switch, and if so, to
which door? Calculate the exact probability for each remaining door.
```
**Why**: Variant prevents memorization. Correct: switch to either remaining door (each 1/3 vs 1/4).
**Eval**: Check probabilities are correct (1/4 for door 1, 1/3 for doors 2 and 4).

### Prompt 5: Constrained Flash Fiction (Creative + Instruction Following)
```
Write exactly 100 words of flash fiction. Requirements:
(1) Set in a library, (2) include the word 'algorithm',
(3) the last sentence must recontextualize everything before it,
(4) no dialogue, (5) present tense only. Count your words.
```
**Why**: Reveals stylistic fingerprints. Word count accuracy is measurable.
**Eval**: Count words (target 100 ±5), check all 5 constraints.

### Prompt 6: Cost-Optimized Routing Design (LLM Meta)
```
A startup makes 100K LLM API calls per day: 70% simple classification,
20% summarization, 10% complex reasoning. Design a cost-optimized
routing strategy using multiple providers. Include specific model
recommendations, estimated costs, and quality tradeoffs.
```
**Why**: Directly relevant to Concentrate's product. Tests ecosystem understanding.
**Eval**: Check for multi-tier routing, cost estimates, quality tradeoffs.

### Prompt 7: Fermi Estimation (Reasoning Chain)
```
Estimate the total number of API calls made to LLM providers globally
per day in February 2026. Show your reasoning chain with explicit
assumptions at each step.
```
**Why**: No memorizable answer — pure reasoning. Chain quality evaluable.
**Eval**: Check for explicit assumptions, reasonable final estimate, logical chain.

### Prompt 8: Insurance Pricing Factors (Domain Expertise)
```
Compare the factors that influence term life insurance pricing vs
auto insurance pricing. Which product has more pricing variables and why?
Include at least 5 factors for each.
```
**Why**: Shows YOUR domain. Broadly accessible. Factual claims verifiable.
**Eval**: Check for ≥5 factors each, accuracy of claims, comparison quality.

---

## Top 3 for Writeup Focus

1. **Prompt 3 (JSON Schema)** — measurable cross-provider differences
2. **Prompt 1 (Simpson's Paradox)** — reasoning depth + your expertise
3. **Prompt 5 (Constrained Fiction)** — stylistic fingerprints, fun to write about

---

## Evaluation Strategy (3 Tiers)

### Tier 1: Automatic (every API call — 0 extra time)
```python
def auto_eval(result: dict) -> dict:
    return {
        "success": result["error"] is None,
        "latency_ms": result["latency_ms"],
        "response_length": len(result.get("text", "")),
        "has_content": len(result.get("text", "")) > 10,
    }
```

### Tier 2: Task-Specific (after each section — 5 min extra)
```python
# JSON compliance (Prompt 3)
def check_json_compliance(text: str, schema: dict) -> dict: ...

# Factual accuracy (Prompts 1, 4, 8)
def check_contains(text: str, expected: list[str]) -> dict: ...

# Instruction following (Prompt 5)
def check_word_count(text: str, target: int, tolerance: int = 5) -> dict: ...
```

### Tier 3: LLM-as-Judge (5-10 key comparisons — 10 min extra)
```python
JUDGE_PROMPT = """Evaluate this response. Return JSON with binary pass/fail:
{"accuracy": "pass"|"fail", "reasoning": "pass"|"fail",
 "completeness": "pass"|"fail", "note": "one sentence"}

Question: {question}
Response: {response}"""

# Use cheapest model as judge
judge_result = call_model("anthropic/claude-haiku-3-5", JUDGE_PROMPT)
```

### Per-Prompt Metrics to Capture

| Metric | How | Why |
|--------|-----|-----|
| Correctness | Manual + contains check | Core quality |
| Reasoning quality | Shows work? Identifies assumptions? | Depth |
| Instruction compliance | Constraint checks | Reliability |
| Latency (ms) | `result["latency_ms"]` | Performance |
| Response length | `len(result["text"])` | Verbosity comparison |
| Cost estimate | tokens × pricing | Economics |

### Writeup Result Format
```
Provider Comparison: [Prompt Name]
┌──────────┬──────────┬────────┬───────────┬──────────┐
│ Provider │ Correct? │ Latency│ Cost Est. │ Judge    │
├──────────┼──────────┼────────┼───────────┼──────────┤
│ OpenAI   │ ✓        │ 1.2s   │ $0.003    │ pass     │
│ Anthropic│ ✓        │ 1.8s   │ $0.004    │ pass     │
│ Google   │ ✓        │ 2.1s   │ $0.008    │ pass     │
│ DeepSeek │ ✗        │ 0.9s   │ $0.0004   │ fail     │
└──────────┴──────────┴────────┴───────────┴──────────┘
```

### Eval Tools to Mention in Writeup (Not Implement)
- **Promptfoo**: YAML-based, multi-provider, perfect for Concentrate
- **Braintrust**: End-to-end offline eval + production observability
- **Langfuse**: Open-source observability with cost tracking

# Brainstorm Archive — Full Lists for Reference

> Selected prompts are in `prompt-strategy.md`. This file preserves all options.

---

## All 30 Prompt Ideas

### Category A: Causal/Statistical Reasoning

1. **Simpson's Paradox** ★ SELECTED — "A hospital has two treatments..."
2. **Correlation ≠ Causation** — "Ice cream sales and drowning deaths..."
3. **Confounding** — "A study finds that coffee drinkers live longer..."
4. **A/B Test Interpretation** ★ SELECTED — "An A/B test shows 3% higher conversion (p=0.04)..."
5. **Selection Bias** — "A company surveys departing employees..."

### Category B: Insurance/Finance

6. **Insurance Pricing** ★ SELECTED — "Compare term life vs auto insurance pricing factors..."
7. **Interest Rate Impact** — "Explain how 100bp increase affects bonds, annuities, bank profitability..."
8. **Risk Assessment** — "Design framework for gig economy insurance product..."
9. **Regulatory ML** — "Key challenges of deploying ML in regulated industries..."
10. **Actuarial vs ML** — "Compare GLMs/experience rating with GBMs/neural nets for auto insurance..."

### Category C: LLM/AI Meta

11. **Model Selection** — "When should a team use GPT-5 vs Claude Sonnet vs Llama?"
12. **LLM Cost Optimization** ★ SELECTED — "100K calls/day, 70% classification, 20% summarization, 10% reasoning..."
13. **Provider Reliability** — "Design failover strategy for 99.9% uptime..."
14. **Prompt Engineering** — "Compare zero-shot, few-shot, chain-of-thought..."
15. **LLM Evaluation** — "How to evaluate LLM factual correctness for financial services?"

### Category D: Technical/Production

16. **Circuit Breaker** — "Design circuit breaker for LLM API calls..."
17. **Streaming vs Batch** — "Tradeoffs for chat vs batch document processing..."
18. **Tool Calling Reliability** — "LLM generates invalid JSON in tool calls. Design validation/retry..."
19. **Multi-Agent Coordination** — "Three agents (researcher, analyst, writer) collaborate..."
20. **Observability** — "Metrics and logs for production LLM system with 50+ services..."

### Category E: Logic/Reasoning Puzzles

21. **Bat and Ball** — "$1.10 total, bat costs $1 more than ball..."
22. **Switches** — "Three switches, three bulbs, enter room once..."
23. **Knights & Knaves** — "A says 'We are both knaves.' What can you determine?"
24. **Monty Hall Variant** ★ SELECTED — "4 doors instead of 3..."
25. **Fermi Estimation** ★ SELECTED — "Estimate total LLM API calls globally per day..."

### Category F: Creative/Writing

26. **Haiku** — "Write a haiku about debugging code at 3am." (already in compare.py)
27. **Perspective Shift** — "Last sentence changes meaning of everything before it."
28. **Analogy** — "Explain CAP theorem to a 10-year-old using pizza delivery."
29. **Constrained Writing** — "100-word product description, no buzzwords."
30. **Code Poetry** — "Python function that prints a poem about itself."

### Selected for Exercise (8)
1. Simpson's Paradox (Prompt 1)
2. A/B Test Interpretation (Prompt 2)
3. JSON Schema Compliance (Prompt 3) — new, not in brainstorm
4. 4-Door Monty Hall (Prompt 4)
5. Constrained Flash Fiction (Prompt 5) — adapted from #27+#29
6. Cost-Optimized Routing (Prompt 6) — adapted from #12
7. Fermi Estimation (Prompt 7)
8. Insurance Pricing Factors (Prompt 8) — from #6

---

## All 7 Agent Question Ideas

### Tier 1: Broadly Interesting + Shows Expertise
A. "How should a company decide between building vs buying an LLM gateway?"
B. ★ SELECTED — "Compare strategies for reducing LLM costs in production..."
C. "Key considerations for deploying ML in regulated industries?"

### Tier 2: Domain-Specific but Accessible
D. "Compare approaches for estimating price elasticity from observational data..."
E. ★ SELECTED — "Design framework for validating LLM outputs in financial services..."

### Tier 3: Fun / Conversation Starters
F. "What if every company switched from proprietary to open-source LLMs?"
G. "Design the ideal API for accessing LLMs from 10 providers through one interface."

---

## All 4 Structure Ideas

### A: "The Systematic Explorer" — methodical feature testing
### B: "The Domain Expert" — insurance/finance focus
### C: "The Builder" — production-grade infrastructure
### D: "The Compound" → D-Lite ★ SELECTED — strategic enhancement of existing code

---

## All 3 Writeup Formats

### A: "Production DX Audit" — feature-by-feature findings
### B: "Story Format" — chronological discovery narrative
### C: "Technical Brief" — findings-first professional format
### Selected: Hybrid A+C ★ — findings-first with DX friction section

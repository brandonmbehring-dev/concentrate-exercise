# Exercise Strategy — Structure, Writeup, Agent Questions

## Structure: D-Lite ("Strategic Enhancement")

### What You Do
1. Update models in `client.py` (5 min) — gpt-4.1 → gpt-5, add gemini + xai
2. Add 1 new compare.py section: web search (15 min)
3. Swap 2-3 prompts to research-backed set (10 min)
4. Run everything: discover.py + compare.py + agent.py (30 min)
5. Write the writeup (60 min)

### Budget
- **Total new code**: ~50-80 lines
- **API calls**: ~40-50 (4 providers × 8 prompts + routing + tools + web search + agent)
- **Time**: 2 hours (30 min code + 30 min run + 60 min writeup)

### Why D-Lite Beats Alternatives
- **vs D-Full**: Adding caching + reasoning costs 30+ min better spent on writeup
- **vs Domain Expert**: Too narrow — "cross-provider DX audit" more relevant
- **vs Systematic**: Running existing code without changes shows less initiative

### What Makes It "Uniquely Brandon"
1. **Prompts** — Simpson's Paradox and insurance pricing are YOUR domain
2. **Eval approach** — Cost-quality tradeoff with actuarial/quantitative thinking
3. **Writeup** — Your communication style IS the differentiator (60% of evaluation)

---

## Execution Sequence (Monday)

```
00:00 - 00:05  Run discover.py → confirm available models + pricing
00:05 - 00:10  Update client.py models (gpt-5, add gemini + xai)
00:10 - 00:25  Add web search section + update prompts in compare.py
00:25 - 00:30  Add eval helpers (auto_eval, check_json, check_contains)
00:30 - 00:45  Run compare.py --section all → review results
00:45 - 00:55  Run agent.py with 2 questions → review results
00:55 - 01:00  Take screenshots, save all JSON results
01:00 - 02:00  WRITE THE WRITEUP (this is the real deliverable)
```

---

## Web Search Section (New — Implementation Sketch)

```python
def run_web_search_comparison():
    """Test built-in web search across providers."""
    web_tool = {"type": "web_search", "search_context_size": "medium"}
    prompt = "What are the latest developments in AI regulation in the US? Cite sources."

    for provider, model in MODELS.items():
        result = call_model(model, prompt, tools=[web_tool])
        # Check for web_search_call in output, extract sources
        # Note: Gemini/Mistral can't combine web search + function tools
```

---

## Agent Questions (2 Questions)

### Question B: LLM Cost Reduction
```
Compare strategies for reducing LLM costs in production without sacrificing quality.
Include routing optimization, prompt engineering, caching, and model selection.
```
- Directly about Concentrate's value prop
- Naturally decomposes into 4 sub-tasks
- Plan/execute/synthesize workflow shines here

### Question E: LLM Output Validation in Financial Services
```
Design a framework for validating LLM outputs in financial services, where errors
could cause regulatory penalties. Include quality metrics, human-in-the-loop design,
and failure modes.
```
- Shows YOUR domain without being insurance-specific
- Cross-domain appeal (finance + ML + production engineering)
- Tests whether models can think about risk

---

## Writeup Format (Hybrid A+C)

```markdown
## Summary
One paragraph: what I built, how many providers/prompts, top finding, overall DX assessment.

## What I Built
- Architecture diagram (text-based): client.py → compare.py/agent.py/discover.py
- Why shared client pattern (DRY, consistent error handling)
- 4 providers × 8 prompts + routing + tools + streaming + web search + agent

## Key Findings (The Interesting Part)
### Finding 1: The Structured Output Gap
OpenAI 100% JSON compliance vs [others].

### Finding 2: The Cost-Quality Spectrum
xAI at 20x cheaper with [quality comparison].

### Finding 3: [Most Surprising Discovery]
Whatever actually surprises you during testing.

### Finding 4: Causal Reasoning Across Providers
Simpson's Paradox results.

## Friction & Recommendations
Numbered list. Each:
- **What I experienced**: [concrete behavior]
- **What I expected**: [reasonable expectation]
- **Suggested improvement**: [actionable recommendation]

## Cost Analysis
Real numbers. Table: provider × prompt type → cost per request.
"At 100K calls/day, routing saves $X/month"

## What I'd Build Next
- Prompt caching at scale
- Reasoning params (effort levels)
- Messages API for Claude Code integration
- Eval pipeline with Promptfoo
- Circuit breaker with provider fallback
```

### Writeup Principles
- **Length**: 800-1200 words. Dense, not padded.
- **Lead with findings, not process** — "I discovered X" not "First I did Y"
- **Include real numbers** — latency in ms, cost in $, accuracy in %
- **Have opinions** — "I'd recommend X for production because Y"
- **Friction = gift** — Frame bugs/friction as product improvement suggestions

---

## Submission Plan

| Decision | Answer |
|----------|--------|
| Production repo | Fresh repo on `github.com/brandonmbehring-dev/`, clean commits, no AI attribution |
| Screenshots | Rich formatted tables (tabulate) + terminal screenshots |
| Submission | Public GitHub repo, send link to Zach |
| Deadline | Feb 18, 2026 (Tuesday) |

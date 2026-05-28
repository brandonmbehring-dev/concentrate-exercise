# Concentrate AI — Interview Prep Checklist

> PRIVATE — research repo only. Do NOT include in production repo.

---

## Pre-Implementation Checklist (Monday Morning)

- [ ] Create fresh production repo on `github.com/brandonmbehring-dev/`
- [ ] Copy code files (client.py, compare.py, agent.py, discover.py, eval.py, guardrails.py, smoke_test.py)
- [ ] Run `smoke_test.py` to verify setup (API key, providers, streaming)
- [ ] Run `discover.py` to confirm model names in catalog
- [ ] Verify API key: `curl -H "Authorization: Bearer $CONCENTRATE_API_KEY" https://api.concentrate.ai/v1/models/`
- [ ] Check credit balance in dashboard
- [ ] Confirm all 4 providers available in catalog
- [ ] Install dependencies: `pip install tabulate requests python-dotenv`

---

## JD → Exercise Mapping

| JD Responsibility | How Exercise Demonstrates |
|---|---|
| "Build LLM-powered services using Concentrate" | Built 8-file comparison suite on Concentrate API |
| "Design reliable interactions with LLMs (OpenAI, Anthropic, Gemini, OSS)" | Tested 4 providers: OpenAI, Anthropic, Gemini, xAI |
| "Write tools to test system behavior at scale" | Systematic 8-prompt comparison + auto-routing + tool calling + eval suite |
| "Reproduce bugs, isolate root causes, document findings" | Discovered GPT-4.1 retirement, documented friction points |
| "Drive improvements to APIs, defaults, and DX" | Friction section with actionable recommendations |
| "Clear async communication" | Structured writeup with findings, numbers, opinions |

---

## Bridge Narrative

**Core Pitch**: "I'm a quantitative engineer who builds production ML systems in regulated industries. I tested Concentrate's API the way I'd evaluate any production dependency — systematically, with real metrics, and an eye toward cost-quality tradeoffs that matter at scale."

**Why me specifically**:
- Actuarial/quantitative background → I think about cost-quality tradeoffs naturally
- Insurance/regulated industry experience → I understand the stakes of production ML
- Multi-provider testing → I tested the way a real user would, not just "does it work"

---

## Anticipated Questions from Zach

| Question | Prepared Answer |
|----------|----------------|
| "Why these prompts?" | "I chose prompts that produce measurable cross-provider differences: structured output compliance, reasoning depth, instruction-following. Statistical reasoning prompts are my domain and show real differentiation." |
| "What surprised you?" | "[Fill with actual finding from testing]" |
| "How would you use this in production?" | "The cost-quality spectrum (xAI 15x cheaper input, 30x cheaper output) maps directly to routing optimization. I'd route simple tasks to xAI, complex reasoning to Claude/GPT-5.1, and use Concentrate's auto-routing to validate." |
| "What would you build on day 1?" | "An eval pipeline — Promptfoo + Concentrate's routing = automated quality/cost monitoring across providers. Then a circuit breaker for provider failover." |
| "Why 4 providers?" | "Two is the minimum. Four gives you the cost-quality spectrum that IS Concentrate's value prop. xAI at $0.20/M vs Anthropic at $15/M output — that's the routing story." |
| "What friction did you find?" | "[Fill with actual friction from testing]" |

---

## Success Factors

### Green Flags (What Zach Wants to See)
- [ ] Code runs cleanly — no errors, no missing dependencies
- [ ] Real numbers — latency in ms, cost in $, accuracy in %
- [ ] Opinions — "I'd recommend X because Y"
- [ ] DX friction identified — specific, actionable, constructive
- [ ] Production thinking — "at 100K calls/day, this matters because..."
- [ ] Domain depth — prompts that show expertise, not just "hello world"
- [ ] Multi-provider awareness — not just "I tested OpenAI"
- [ ] Clean writeup — structured, concise, no fluff

### Red Flags (Avoid)
- [ ] Code doesn't run
- [ ] Writeup is just a list of what I did (process, not findings)
- [ ] No real numbers — only "it worked" / "it was fast"
- [ ] Over-engineered — 500 lines of code, 200-word writeup
- [ ] Generic prompts — "write me a poem" doesn't show anything
- [ ] No friction found — looks like you didn't really explore
- [ ] Buzzword-laden — "leveraging cutting-edge AI synergies"

---

## Time Discipline

| Phase | Budget | Hard Stop |
|-------|--------|-----------|
| Code changes | 30 min | Stop adding features at 30 min |
| Running scripts | 30 min | Fix errors only, don't add |
| Writeup | 60 min | This is 60% of the evaluation |
| **Total** | **2 hours** | **Ship it** |

**If behind schedule**: Cut code features, preserve writeup time. The writeup IS the deliverable.

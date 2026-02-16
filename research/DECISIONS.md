# Technical Decisions — Concentrate AI Exercise

> ADR-style decision log. Shareable — can go in production repo.

---

## ADR-001: Provider Selection

**Context**: Exercise requires "at least two LLM providers." JD mentions OpenAI, Anthropic, Gemini, OSS.

**Options**:
- (A) 2 providers — minimum viable
- (B) 3 providers + Gemini — covers "Big 3"
- (C) 4 providers + Gemini + xAI — full spectrum
- (D) 5+ providers — diminishing returns

**Decision**: **(C) 4 providers — OpenAI, Anthropic, Google Gemini, xAI**

**Reasoning**: Gemini explicitly in JD. xAI creates cost-quality spectrum (75x cheaper input) that demonstrates Concentrate's routing value prop. 4 providers is enough to show breadth without diluting analysis.

**Tradeoffs**: More providers = more data but less depth per provider. 4 is the sweet spot.

**Amendment (2026-02-16)**: Originally selected DeepSeek as 4th provider. Switched to xAI
(grok-4-1-fast-reasoning) because it is strictly cheaper ($0.20/$0.50 vs $0.27-0.55/$1.10-2.19)
with stronger reasoning capabilities. The cost-quality spectrum narrative is stronger: 75x input
spread vs DeepSeek's 20-50x.

---

## ADR-002: Prompt Strategy

**Context**: Need prompts that produce interesting cross-provider findings for the writeup.

**Options**:
- (A) Generic prompts (haiku, trivia) — easy but uninteresting
- (B) Pure domain prompts (actuarial) — deep but niche
- (C) Research-backed diagnostic set — optimized for comparison
- (D) Mix of all categories

**Decision**: **(C) 8 research-backed prompts across 6 categories**

**Reasoning**: Research shows specific prompt types (structured output, reasoning variants, constrained writing) produce the most measurable cross-provider differences. Simpson's Paradox and insurance pricing add unique domain signal.

**Key prompts**: JSON schema compliance (#1 differentiator), Simpson's Paradox (causal reasoning), 4-door Monty Hall (anti-memorization), constrained flash fiction (stylistic fingerprints).

---

## ADR-003: Evaluation Approach

**Context**: Need to evaluate responses beyond "did it work."

**Options**:
- (A) Inline assertions only — simple, deterministic
- (B) LLM-as-judge only — semantic but expensive
- (C) Cross-provider agreement — clever but agreement ≠ correctness
- (D) Package C: deterministic + LLM-judge + meta-evals

**Decision**: **(D) Package C — 3-layer evaluation**

**Reasoning**: Layer 1 (deterministic, $0) catches ground truth errors. Layer 2 (LLM-as-judge, ~$0.45) scores all 32 responses via haiku-4-5, deep-evals all providers via gpt-5.1, creative-evals all providers via sonnet-4-5. Layer 3 (meta-evals, ~$0.40) adds self-evaluation, pairwise ranking, and cross-provider agreement. Shows production thinking without over-engineering.

**Tradeoffs**: More complex than (A), but the writeup material from (D) justifies the investment.

---

## ADR-004: Exercise Structure

**Context**: Multiple possible structures for the deliverable.

**Options**:
- (A) Systematic Explorer — methodical feature testing
- (B) Domain Expert — insurance/finance focus
- (C) The Builder — production-grade infrastructure
- (D-Full) Compound — enhance everything
- (D-Lite) Strategic Enhancement — targeted enhancements + strong writeup

**Decision**: **(D-Lite) Strategic Enhancement**

**Reasoning**: Best ROI within 2-hour budget. Minimal code changes (50-80 lines), maximum writeup quality. Adding web search section is the highest-impact new feature. Mentions caching/reasoning in "what I'd build next" without implementation overhead.

**Tradeoffs**: Less code than D-Full, but writeup is 60% of evaluation. Time spent writing > time spent coding.

---

## ADR-005: Agent Questions

**Context**: Agent runs Plan → Execute → Synthesize. Need 2 questions that produce interesting multi-step results.

**Options**:
- (B) LLM cost reduction strategies — Concentrate's value prop
- (E) LLM validation in financial services — domain expertise
- (G) Ideal LLM API design — literally Concentrate's challenge

**Decision**: **B + E**

**Reasoning**: B is directly about Concentrate's product (meta-relevant). E shows domain expertise without being too niche. Together they cover business relevance + technical depth.

**Alternative**: Could swap E for G if you want more "meta" angle about API design.

---

## ADR-006: Writeup Format

**Context**: The writeup is the #1 deliverable.

**Options**:
- (A) Production DX Audit — feature-by-feature
- (B) Story Format — chronological discovery
- (C) Technical Brief — findings-first

**Decision**: **LaTeX Tufte handout — findings-first technical brief with DX friction section**

**Reasoning**: Leads with interesting findings (not process), includes real numbers, has opinions, frames friction as product improvement suggestions. Dense, every sentence carries information.

---

## ADR-007: OpenAI Model

**Context**: GPT-4.1 retiring Feb 13-19, 2026. Current code uses `openai/gpt-4.1`.

**Decision**: Use `openai/gpt-5.1`. Confirmed via discover.py catalog fetch.

**Reasoning**: Docs quickstart shows gpt-5.x as current. Discovery of the retirement IS a writeup finding.

---

## ADR-008: Model Names (Finalized)

**Context**: Need exact model identifiers that match Concentrate catalog.

**Decision**:
- `openai/gpt-5.1` — Comparator ($1.25/$10)
- `anthropic/claude-sonnet-4-5` — Planner ($3/$15)
- `google/gemini-2.5-pro` — Synthesizer ($1.25/$10)
- `xai/grok-4-1-fast-reasoning` — Researcher ($0.20/$0.50)

**Reasoning**: Confirmed via /v1/models/ catalog. Agent roles assigned by cost-capability fit.

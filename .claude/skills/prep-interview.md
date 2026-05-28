# /prep-interview - Technical Interview Preparation

Surface relevant technical content from research-kb knowledge base to prepare for interviews.

## Usage
```
/prep-interview <company> [topic]
```

## Instructions

When this command is invoked:

0. **Check KB readiness** (fast pre-flight):
   - Run `python ~/Claude/research-kb/scripts/eval_interview_readiness.py --json`
   - If overall_score < 0.5: warn that KB coverage is limited for some methods
   - If specific methods show MISS: note them as gaps in the prep output

1. **Load company context**:
   - Read `data/targets.yml` for company profile and requirements
   - Identify technical focus areas (causal inference, time series, ML, etc.)

2. **Query research-kb for relevant content** using MCP tools:

   a. **Search for method-specific content**:
      - Use `research_kb_search` with company's required methods
      - Example: For experimentation roles → search "A/B testing", "causal inference", "treatment effects"
      - Example: For forecasting roles → search "time series", "ARIMA", "GARCH"

   b. **Get assumption audits for key methods**:
      - Use `research_kb_audit_assumptions` for methods the company cares about
      - Example: "double machine learning", "instrumental variables", "diff-in-diff"

   c. **Explore concept neighborhoods**:
      - Use `research_kb_graph_neighborhood` to understand related concepts
      - Helps prepare for "tell me about X and how it relates to Y" questions

3. **Cross-reference with STAR stories**:
   - **Primary source**: `~/Claude/brandon_professional_profile/stories/*/core.yml`
   - **Banned content check**: `~/Claude/brandon_professional_profile/facts/banned_content.yml`
   - **Company matrices**: `~/Claude/brandon_professional_profile/quick_refs/*_matrix.yml`
   - Map technical concepts to your experience:
     - Price Elasticity → causal inference, pricing optimization, DoubleML
     - Underwriting Automation → feature engineering, interpretability, stakeholder trust
     - temporalcv → time series validation, infrastructure building
     - Stakeholder Translation → executive communication, business impact
     - Cloud Certifications → learning velocity, self-directed growth
   - **CRITICAL**: MYGA Cold-Start is EXCLUDED (needs rework) — do not use

4. **Generate interview prep summary**:
   ```
   Technical Interview Prep: <Company>
   ====================================

   ## Company Focus Areas
   - [List from targets.yml: experimentation, ML, forecasting, etc.]

   ## Key Methods to Review
   - [Method 1]: [Brief description + assumption audit summary]
   - [Method 2]: [Brief description + assumption audit summary]

   ## Your Relevant Experience
   - STAR Story: [Story name] → demonstrates [method/concept]
   - STAR Story: [Story name] → demonstrates [method/concept]

   ## Concept Connections to Prepare
   - [Concept A] → related to → [Concept B]
   - Understanding path: [A] → [intermediate] → [B]

   ## Interview Prep Cards (from research-kb)
   - [Top 5 relevant cards from interview_prep domain]
   ```

5. **Offer deep-dive options**:
   - "Want me to explain [method] assumptions in detail?"
   - "Want practice questions on [topic]?"
   - "Want to see how [concept] appears in the literature?"

## Example Output

```
/prep-interview two_sigma experimentation

Technical Interview Prep: Two Sigma
====================================

## Company Focus Areas
- Quantitative research, statistical methods
- Causal inference for trading signals
- High-frequency data analysis

## Key Methods to Review

### Double Machine Learning (DML)
- Used for: High-dimensional treatment effect estimation
- Assumptions: Unconfoundedness, Overlap, Neyman orthogonality
- Your experience: Price elasticity models used similar causal methods

### Instrumental Variables (IV)
- Used for: Identifying causal effects with endogeneity
- Assumptions: Relevance, Exclusion restriction, Independence
- Your experience: Could frame underwriting automation as natural experiment

## Your Relevant Experience
- STAR: Price Elasticity Models → demonstrates causal inference for pricing
- STAR: MYGA Cold-Start → demonstrates transfer learning, prior knowledge

## Concept Connections to Prepare
- DML → requires → cross-fitting → implements → sample splitting
- IV → identifies → LATE → generalizes to → ATE under monotonicity

## Interview Prep Cards
1. "What is the fundamental problem of causal inference?"
2. "Explain the difference between ATE and ATT"
3. "When would you use IV vs. DML?"
4. "What is the overlap assumption?"
5. "How do you validate causal assumptions?"

---
💡 Ask me to deep-dive on any topic above!
```

## Technical Implementation Notes

- Uses research-kb MCP tools: `research_kb_search`, `research_kb_audit_assumptions`, `research_kb_graph_neighborhood`
- Queries both `causal_inference` and `time_series` domains based on company profile
- Interview prep cards from `interview_prep` domain (9,398 cards available)
- **STAR stories source**: `~/Claude/brandon_professional_profile/` (canonical repo)
  - Stories: `stories/*/core.yml` (5 verified stories)
  - Defense Q&A: `stories/*/defense.md`
  - Company framing: `stories/*/{amazon,meta,two_sigma}.md`
  - Banned content: `facts/banned_content.yml` — ALWAYS check before output
- **Old source deprecated**: `data/portfolio.yml` — use brandon_professional_profile instead

## Banned Content Reminder

**NEVER include in prep output:**
- "Transfer learning presentation" — fictional
- "20% to 95% adoption" — fictional
- "5+ years experience" — actual: 4 years
- "3 GCP certifications" — actual: 2
- "Milliman Rx" → "third-party prescription risk scoring vendor"
- "Instrumental variables" / "Propensity score matching" as methods used
  - OK to say: "tried and rejected, chose DoubleML"

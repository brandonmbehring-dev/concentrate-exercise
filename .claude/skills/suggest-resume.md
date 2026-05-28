# /suggest-resume - Resume Variant Suggestion

Suggests the optimal resume variant and cover letter angle for a job posting.

## Usage
```
/suggest-resume <job_id>
```

## Workflow

When this command is invoked:

### 1. Load Job Context

1. **Get job from tracker**:
   ```bash
   grep "<job_id>" data/unified_jobs.csv
   ```

2. **Load JD from cache** (if available):
   ```
   data/jd_cache/<job_id>.md
   ```

3. If no JD cached:
   - Try `WebFetch` on job URL
   - Offer to `make jd_extract URL=<url>` for JS-heavy sites
   - Fall back to manual analysis if extraction fails

### 2. Extract Requirements from JD

Parse the JD to extract:

**Technical Skills** (match against `master/skills_rating.yml`):
- Languages: Python, SQL, R, Julia, etc.
- Frameworks: PyTorch, TensorFlow, Spark, etc.
- Methods: A/B testing, causal inference, time series, NLP, etc.
- Infrastructure: AWS, GCP, Docker, Kubernetes, etc.

**Domain Keywords**:
- Experimentation, pricing, risk, fraud, marketplace, ads, etc.
- Financial services, healthcare, e-commerce, etc.

**Level Signals**:
- Years required (e.g., "5+ years")
- Level mentions (L4, L5, Senior, Staff, etc.)
- Scope (team lead, individual contributor, etc.)

### 3. Score Against Role Masters

For each role master in `templates/role_masters/*.yml`:

1. Extract keywords from `metadata.description` and `metadata.target_companies`
2. Count keyword overlap with JD requirements
3. Calculate match percentage: `(matched_keywords / total_jd_keywords) * 100`

**Available role masters**:
- `ds_experimentation` — A/B testing, causal inference, pricing
- `ds_financial_services` — Finance, risk, insurance
- `ds_risk_modeling` — Healthcare, fraud, credit risk
- `ds_product_analytics` — Product metrics, user behavior
- `quant_analyst` — Quantitative finance, trading
- `mle_general` — ML engineering, production ML
- `ml_research` — Applied research, publications
- `ai_engineering` — LLMs, GenAI, AI systems
- `adtech_ds` — Advertising, bidding, attribution

### 4. LLM Tiebreaker (If Needed)

If top 2 variants are within 10% match score:
- Consider company culture and team focus
- Evaluate which narrative arc fits better
- Pick winner with reasoning

### 5. Generate Cover Letter Angle

**NOT a keyword dump** (ATS handled by resume).

Instead, craft a **narrative hook**:
- Practitioner insight (what you learned doing this work)
- Specific experience alignment (your project → their problem)
- Why you want THIS role (growth, tools, mission)

**Suggest template** from `templates/cover_letters/` if one exists.

### 6. Output and Update Prompt

Present the recommendation, then prompt:

```
Would you like me to:
1. Update unified_jobs.csv with resume_version=<suggested>?
2. Generate the resume? (make resume_<company>)
3. Generate both resume and cover letter?
```

## Output Format

```
Resume Suggestion for: [Company] - [Title]
========================================

JD Analysis:
  Technical: Python, SQL, causal inference, A/B testing
  Domain: Marketplace, pricing, experimentation
  Level: L5 / Senior (5+ years required)

Resume Recommendations:

1. ds_experimentation (87% match)
   Matches: causal inference, A/B testing, Python, pricing
   Target companies include: [company or similar]
   ATS keywords present: [list]

2. ds_product_analytics (71% match)
   Matches: product metrics, Python, SQL
   Missing: pricing emphasis

-> Recommend: ds_experimentation

Cover Letter Angle:
  "Your marketplace experimentation team caught my attention
   because pricing is exactly what I've done at Prudential—
   building models that set rates for $14B+ in products.
   The difference: you have the data velocity I've dreamed about."

  Hook type: Practitioner seeking better tools
  Template: templates/cover_letters/<company>.yml (exists/create)

Next Steps:
  [ ] Update tracker with resume_version? (y/n)
  [ ] Generate resume? (make resume_<company>)
  [ ] Generate cover letter? (make cover_<company>)
```

## Skills Validation

When matching skills:
1. Load `master/skills_rating.yml`
2. For each JD requirement, check if skill exists and rating
3. **Only include skills rated 4+** in recommendation
4. Flag any skills rated 3 that JD heavily emphasizes:
   ```
   Note: JD emphasizes "Spark" (5x mentions) but rated 3.
   Exception: Include if you commit to studying before interview?
   ```

## Company Variant Check

After suggesting role master, check if company variant exists:
```
templates/company_variants/<company>.yml
```

If exists:
- Report which role master it inherits from
- Note any customizations

If doesn't exist:
- Suggest creating one
- Provide template based on recommended role master

## Integration Notes

- **JD Cache**: `data/jd_cache/<job_id>.md` — use if available
- **Skills**: `master/skills_rating.yml` — canonical skill ratings
- **Role Masters**: `templates/role_masters/*.yml` — resume templates
- **Cover Letters**: `templates/cover_letters/*.yml` — cover letter configs
- **Tracker**: `data/unified_jobs.csv` — update `resume_version` field

## Example Session

```
User: /suggest-resume 83769e07a4fe
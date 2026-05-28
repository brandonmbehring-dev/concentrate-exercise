# JD Analyzer Agent

**Purpose**: Extract structured requirements from cached job descriptions.

**Pattern**: Mirrors `feature-dev:code-explorer` — analysis-only, no modifications.

---

## Invocation

```bash
# Via Task tool
Task(subagent_type="job-app:jd-analyzer", prompt="Analyze JD for <company> with job_id <id>")
```

---

## Inputs

The agent requires:
1. **job_id** — ID in `data/jd_cache/<job_id>.md`
2. OR **company** — Will search for matching JD in cache

---

## Output Format

The agent outputs a structured YAML block:

```yaml
company: toast
role_title: "Staff Data Scientist"
level_inferred: Staff (L6)
yoe_required: 10
yoe_source: "10+ years in data science"
location_policy:
  type: remote | hybrid | onsite
  days_onsite: 0-5 | null
  city_required: [list] | null
required_skills:
  - Python
  - SQL
  - ML lifecycle
  - stakeholder management
preferred_skills:
  - Spark
  - demand forecasting
  - personalization
domain_keywords:
  - menu recommendations
  - offer targeting
  - demand forecasting
inferred_domain: experimentation | ads_measurement | product_analytics | fintech_risk | ml_engineering | applied_research
red_flags:
  - "10+ years required (you have ~4)"
  - "Staff level exceeds ADR 0004"
resume_variant_suggestion: ds_experimentation | ds_risk_modeling | ai_engineering
```

---

## Analysis Logic

### 1. YOE Extraction

Parse JD for years-of-experience patterns:
- "X+ years" in requirements section
- "X-Y years" ranges
- Bullet points like "- 10+ years in data science"

**Thresholds** (from ADR 0004):
- 5 years → stretch (PhD + 4 years)
- 6+ years → blocked
- 8+ years → Staff level, auto-remove
- 10-15+ years → Principal level, auto-remove

### 2. Location Policy

Parse from YAML frontmatter first:
- `remote_policy` field
- `location` field

Then body text:
- "X days in-office" patterns
- "onsite expected", "SF required"
- "remote" or "hybrid" keywords

**Thresholds** (from ADR 0002):
- 0-3 days onsite → OK
- 4+ days → blocked
- SF-only → blocked (NJ-based, no relocation)

### 3. Level Inference

Infer from title and context:
| Pattern | Level |
|---------|-------|
| Staff, L6, IC6 | Staff (L6) |
| Senior Staff, Principal, L7+ | Senior Staff+ |
| Senior, L5 | Senior (L5) |
| No modifier | Mid (L4) |

### 4. Domain Classification

Use keyword matching to infer domain:

| Domain | Keywords |
|--------|----------|
| ads_measurement | ads, attribution, incrementality, media mix, MMM |
| experimentation | A/B testing, causal inference, experiment platform |
| product_analytics | funnels, retention, growth, engagement |
| fintech_risk | pricing, credit, fraud, underwriting, actuarial |
| ml_engineering | infrastructure, pipelines, deployment, MLOps |
| applied_research | modeling, methods development, research |

### 5. Resume Variant Mapping

Based on inferred domain:
| Domain | Variant |
|--------|---------|
| experimentation | ds_experimentation |
| fintech_risk | ds_risk_modeling |
| ml_engineering, applied_research | ai_engineering |
| product_analytics, ads_measurement | ds_experimentation (default) |

### 6. Red Flags

Generate red flags for:
- YOE exceeds threshold
- Location blocked
- Level exceeds ADR 0004
- Missing required skills
- Sponsorship unclear (H1B concern)

---

## Tools Used

- **Read**: Load JD from cache
- **Grep**: Search for patterns in JD text
- **Glob**: Find JD cache file by company name

---

## Example Analysis

**Input**: `job_id=to1a2b3c4d5e`

**Output**:
```yaml
company: Toast
role_title: Staff Data Scientist
level_inferred: Staff (L6)
yoe_required: 10
yoe_source: "10+ years in data science with production ML systems"
location_policy:
  type: remote
  days_onsite: null
  city_required: null
required_skills:
  - Python
  - SQL
  - ML frameworks (scikit-learn, PyTorch, TensorFlow)
  - AWS cloud platform
  - A/B testing
  - causal inference
  - distributed data processing
preferred_skills:
  - Advanced degree (CS, Statistics, STEM)
  - MLOps tooling
  - LLM fine-tuning
  - RLHF
domain_keywords:
  - production ML systems
  - machine learning lifecycle
  - model evaluation
  - experimentation
  - causal inference
inferred_domain: experimentation
red_flags:
  - "YOE BLOCKED: 10+ years required (you have ~4)"
  - "LEVEL: Staff exceeds ADR 0004 (PhD + 4 years = Senior max)"
resume_variant_suggestion: ds_experimentation
```

---

## Integration Points

1. **parse_jd_requirements.py** — Uses this module for structured extraction
2. **materials-reviewer agent** — Consumes this output
3. **/review-application skill** — Orchestrates JD analysis before materials review
4. **pre_submit_checklist.py** — Uses same parsing logic for gate checks

---

## Files Accessed

| File | Purpose |
|------|---------|
| `data/jd_cache/<job_id>.md` | Primary JD source |
| `data/unified_jobs.csv` | Job metadata (company, title, status) |
| `scripts/parse_jd_requirements.py` | Parsing functions |

---

## Validation

Run against audit cases:
```bash
# These should all produce correct analysis:
Toast Staff (to1a2b3c4d5e) → 10+ YOE blocked
Fetch Senior Staff (fetch1a2b3c4d5) → 8+ YOE blocked
Snap (snap) → 4+ days onsite blocked
Perplexity (ppx1a2b3c4d5e) → SF onsite blocked
Ramp (ramp) → Should suggest ds_experimentation, not ai_engineering
```

---
paths:
  - "data/**"
---

# Data Integrity Rules

Conventions and validation rules for the data layer.

## Canonical Files

| File | Role | Format |
|------|------|--------|
| `unified_jobs.csv` | **PRIMARY** job tracker | CSV, 51 columns |
| `interviews.csv` | Interview events | CSV, 1:N with jobs |
| `recruiters.csv` | Recruiter contacts | CSV |
| `facts.yml` | DERIVATIVE of VERIFIED_FACTS_FINAL.md | YAML |
| `portfolio.yml` | STAR stories, differentiators | YAML |
| `targets.yml` | Company profiles, comp bands | YAML |
| `knockout_answers.yml` | Application responses (YOE, salary, auth) | YAML |
| `company_email_domains.yml` | Email domain mappings for Gmail sync | YAML |
| `jd_cache/` | Cached job descriptions (305 files) | Markdown with YAML front-matter |

## Schema Reference

Full column documentation: `data/SCHEMA.md`

## Deprecated Files

`job_posts.csv` and `applications.csv` are **DEPRECATED** (backed up in `data/archive/`). All scripts use `unified_jobs.csv`. See ADR 0008.

## Validation Rules

1. **Job IDs**: 12-character hex hash, unique
2. **URLs**: Must be specific postings, not generic `/careers` pages
3. **Dates**: ISO 8601 (YYYY-MM-DD)
4. **Times**: 24-hour format (HH:MM)
5. **Status enum**: new, applied, assessment_passed, interview, offer, rejected, closed, stale, withdrawn, not_a_fit, deprioritized
6. **FK integrity**: All `job_id` references must exist in `unified_jobs.csv`

## JD Cache Format

Location: `data/jd_cache/<job_id>.md`

```yaml
---
title: "Job Title"
company: "Company Name"
extracted_date: "2026-02-05"
source_url: "https://..."
---
# Job Title
[Clean markdown content]
```

## Information Hierarchy (Priority Order)

1. `SINGLE_SOURCE_OF_TRUTH/VERIFIED_FACTS_FINAL.md` - **PRIMARY**
2. `data/facts.yml` - DERIVATIVE (if conflict, VERIFIED_FACTS wins)
3. `data/portfolio.yml` - Domain-specific (STAR stories only)
4. `CONTEXT_MAP.md` - File navigation guide
5. Everything else requires confirmation

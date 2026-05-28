---
paths:
  - "interview_prep_series/**"
---

# Interview Prep Rules

Hub for all interview preparation materials.

## Data Sources

| Source | Location | Purpose |
|--------|----------|---------|
| Interview tracking | `data/interviews.csv` | Scheduled interviews, outcomes |
| Company research | `data/targets.yml` | Compensation bands, contacts |
| Navigation | `interview_prep_series/INDEX.md` | Prep materials map |

## Workflow

1. **Interview scheduled** -> Log in `data/interviews.csv` via `make log_interview`
2. **Check INDEX.md** for existing prep materials
3. **If missing** -> Create company-specific prep checklist
4. **Study** -> Mark `prep_completed=true` in interviews.csv
5. **Verify** -> `make prep-status`

## Temporal Metadata (Freshness Tracking)

All interview prep documents use YAML front-matter:

```yaml
---
last_updated: 2026-01-30
next_review: 2026-04-30
interview_status: awaiting | scheduled | completed | rejected
freshness_claims:
  company_research: "current as of YYYY-MM-DD"
  compensation_data: "stale after 90 days"
  star_stories: "last rehearsed YYYY-MM-DD"
success_probability: "HIGH (70-80%)" | "MEDIUM (50-70%)" | "LOW (<50%)"
success_reason: "Brief justification"
---
```

## Cross-References

- Active prep files: `ACTIVE/`
- Company guides: `amazon_ds_interview_prep_2026/`, `meta_full_loop_prep/`, etc.
- Front-matter template: `interview_prep_series/TEMPLATES/prep_frontmatter.md`

# /audit-portfolio Skill

**Purpose**: Periodic review of all pending applications in the portfolio.

**Trigger**: `/audit-portfolio [--output <path>]`

---

## Usage

```bash
# Basic usage - outputs to ACTIVE/PORTFOLIO_AUDIT.md
/audit-portfolio

# Custom output location
/audit-portfolio --output ACTIVE/AUDIT_2026-02-01.md

# Include passed applications
/audit-portfolio --verbose
```

---

## Flow

1. **Load all jobs from tracker**
   - Read `data/unified_jobs.csv`
   - Filter to active statuses (new, applied, interviewing)

2. **Run materials reviewer on each**
   - Execute `review_materials.py` for each company
   - Collect all issues with severity

3. **Generate audit report**
   - Summary table with counts
   - Issues grouped by severity
   - Prioritized fix list
   - Comparison with previous audit (if exists)

---

## Output Format

```markdown
# Portfolio Audit Report

**Generated**: 2026-02-01
**Previous Audit**: 2026-01-25 (7 days ago)

## Summary

| Status | Current | Previous | Change |
|--------|---------|----------|--------|
| 🔴 BLOCKED | 4 | 6 | -2 ⬇️ |
| 🟡 WARNINGS | 11 | 15 | -4 ⬇️ |
| 🟢 PASS | 30 | 24 | +6 ⬆️ |

## 🔴 Blocked Applications (4)

| Company | Job ID | Issue | Fix |
|---------|--------|-------|-----|
| Toast | to1a2b3c4d5e | 10+ YOE | Remove or downlevel |
| Snap | sn1a2b3c4d5e | 4+ days onsite | Remove |
| ... | ... | ... | ... |

## 🟡 Warnings (11)

### Cover Letter Duplicates (6)
- Adobe, Airbnb, DoorDash, Netflix, Pinterest, Suno

### Missing Cover Letters (4)
- Amazon, Capital One, Oscar Health, Two Sigma

### Domain Mismatches (1)
- Spotify: ads measurement language in non-ads role

## Prioritized Fix List

1. **Remove blocked applications** (4 jobs)
2. **Fix content mismatches** (1 job: Spotify)
3. **Deduplicate cover letters** (6 companies)
4. **Generate missing cover letters** (4 companies)

## Regression Detection

✅ No new blocking issues since last audit
⚠️ 2 new warnings detected:
   - Suno: cover_duplicate (new)
   - Oscar Health: missing cover letter (new)
```

---

## Implementation

```python
def audit_portfolio(output_path: str = "ACTIVE/PORTFOLIO_AUDIT.md"):
    # Load all jobs
    jobs = load_active_jobs()

    # Review each
    reviews = []
    for company, job_id in jobs:
        review = review_materials(company, job_id)
        reviews.append(review)

    # Generate report
    report = generate_audit_report(reviews)

    # Compare with previous if exists
    if previous_audit_exists():
        report += compare_with_previous(reviews)

    # Write report
    Path(output_path).write_text(report)

    return report
```

---

## CLI Fallback

If running outside Claude Code:

```bash
# Run audit
python scripts/audit_portfolio.py

# With options
python scripts/audit_portfolio.py --output ACTIVE/AUDIT_2026-02-01.md
```

---

## Integration Points

| Component | Purpose |
|-----------|---------|
| `review_materials.py` | Individual application review |
| `unified_jobs.csv` | Source of all jobs |
| `PORTFOLIO_AUDIT.md` | Output location |
| `/review-application` | Detailed single-company review |

---

## Recommended Schedule

- **Weekly**: Run as part of `make weekly`
- **Before batch applications**: Validate all materials
- **After pipeline changes**: Catch regressions

---

## Example Session

```
User: /audit-portfolio

Claude: Running portfolio audit on 45 active applications...

┌─────────────────────────────────────────────────────────────┐
│  PORTFOLIO AUDIT SUMMARY                                    │
├─────────────────────────────────────────────────────────────┤
│  🔴 Blocked: 4                                              │
│  🟡 Warnings: 11                                            │
│  🟢 Pass: 30                                                │
├─────────────────────────────────────────────────────────────┤
│  PRIORITY ACTIONS:                                          │
│  1. Remove 4 blocked applications                           │
│  2. Fix Spotify content mismatch                            │
│  3. Deduplicate 6 cover letters                             │
│  4. Generate 4 missing cover letters                        │
└─────────────────────────────────────────────────────────────┘

Full report written to: ACTIVE/PORTFOLIO_AUDIT.md
```

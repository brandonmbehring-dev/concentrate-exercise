# /review-application Skill

**Purpose**: On-demand full review of application materials against JD before submission.

**Trigger**: `/review-application <company> [--job-id <id>]`

---

## Usage

```bash
# Basic usage - auto-finds job_id from tracker
/review-application toast

# With explicit job_id
/review-application toast --job-id to1a2b3c4d5e

# Multiple companies
/review-application snap perplexity ramp
```

---

## Flow

1. **Validate inputs**
   - Company name provided
   - Job ID from args or auto-lookup in `unified_jobs.csv`

2. **Check JD cache**
   - Look for `data/jd_cache/<job_id>.md`
   - If missing → Prompt: "Fetch JD via Playwright?"
   - If yes → Run `/extract-jd-playwright` workflow

3. **Run JD Analyzer**
   - Parse JD via `parse_jd_requirements.py`
   - Extract: YOE, location, domain, red flags
   - Output structured requirements

4. **Run Materials Reviewer**
   - Execute `review_materials.py --company <company> --job-id <id>`
   - Collect all issues with severity

5. **Generate Report**
   - Summary with status: BLOCKED | WARNINGS | PASS
   - Issue list with fixes
   - Recommendation

---

## Output Format

```
┌──────────────────────────────────────────────────────────────┐
│  APPLICATION REVIEW: SNAP                                    │
├──────────────────────────────────────────────────────────────┤
│  Status: 🔴 BLOCKED                                          │
│  Job ID: snap                                                │
│  Domain: ads_measurement → ds_experimentation variant        │
├──────────────────────────────────────────────────────────────┤
│  ISSUES (4 total):                                           │
│                                                              │
│  🔴 BLOCKING:                                                │
│     • [location] 4+ days onsite → ADR 0002 violation         │
│     • [content] Ads measurement language in non-ads role     │
│                                                              │
│  🟡 WARNINGS:                                                │
│     • [duplicate] Same paragraphs as: brex_marketing, reddit │
│                                                              │
│  🟢 INFO:                                                    │
│     • [stretch_yoe] 5 years required (you have ~4)           │
├──────────────────────────────────────────────────────────────┤
│  RECOMMENDATION: DO NOT SUBMIT                               │
│  → Remove from tracker (location blocks)                     │
│  → Or: Find remote role at Snap                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation

```python
# Core workflow
def review_application(company: str, job_id: Optional[str] = None):
    # 1. Find job_id if not provided
    if not job_id:
        job_id = find_job_id_for_company(company)

    # 2. Check/fetch JD
    jd_path = Path(f"data/jd_cache/{job_id}.md")
    if not jd_path.exists():
        # Prompt user or auto-fetch
        fetch_jd_via_playwright(job_id)

    # 3. Run analysis
    result = review_materials(company, job_id)

    # 4. Format and display
    display_review(result)
```

---

## Integration Points

| Component | Purpose |
|-----------|---------|
| `parse_jd_requirements.py` | JD analysis |
| `review_materials.py` | Materials comparison |
| `check_cover_uniqueness.py` | Duplicate detection |
| `validate_jd_alignment.py` | Alignment scoring |
| `/extract-jd-playwright` | JD fetching if missing |

---

## Pre-Commit Hook

This skill is also available via pre-commit hook:

```bash
# In verification_suite/pre-commit.sh
python scripts/validate_staged_applications.py
```

The hook:
1. Detects staged resume/cover letter configs
2. Finds associated job_ids
3. Runs `review_materials.py` on each
4. Fails if BLOCKED issues found
5. Warns (but allows) if WARNINGS only

---

## CLI Fallback

If running outside Claude Code:

```bash
# Direct script execution
python scripts/review_materials.py --company snap --job-id snap

# Check all pending applications
python scripts/review_materials.py --all
```

---

## Examples

### Example 1: Clean pass
```
/review-application ramp --job-id rp1a2b3c4d5e

🟢 RAMP - PASS
   Domain: fintech_risk → ds_risk_modeling variant
   No blocking issues detected
   Recommendation: OK to submit
```

### Example 2: Blocked
```
/review-application toast --job-id to1a2b3c4d5e

🔴 TOAST - BLOCKED
   Issues: 1 block
   • [yoe_mismatch] JD requires 10+ years, you have ~4

   Recommendation: DO NOT SUBMIT
   → Find Senior-level role at Toast instead
   → Or: Remove from tracker (level mismatch)
```

### Example 3: Warnings
```
/review-application netflix

🟡 NETFLIX - WARNINGS
   Issues: 2 warnings
   • [cover_duplicate] Same paragraphs as: adobe, pinterest
   • [domain_mismatch] Cover emphasizes experimentation but JD is product_analytics

   Recommendation: Review and fix before submitting
```

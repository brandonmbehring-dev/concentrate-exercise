# /check-freshness - Job Posting Freshness Verification

Interactive workflow for verifying job posting freshness using external sources.

## Purpose

Verify the actual posted date of jobs where:
- `posted_date` is missing or unknown
- `posted_date_confidence` is "low" or "unknown"
- User suspects a posting has been refreshed/reposted

## Workflow

### Step 1: Identify Jobs Needing Verification

```bash
# Run freshness audit to see current state
make freshness_audit

# Or filter to unknown dates
python scripts/check_freshness.py --tier UNKNOWN

# Or filter to new jobs only
python scripts/check_freshness.py --status new
```

### Step 2: Cross-Reference Sources (Priority Order)

**Source 1: levels.fyi (Preferred)**
1. Navigate to: https://www.levels.fyi/jobs?title=<job_title>&company=<company>
2. Look for "Date Posted" column
3. Convert "X days ago" to actual date

**Source 2: LinkedIn Jobs**
1. Navigate to job posting URL or search for the job
2. Look for "Posted X days/weeks ago" near job title
3. NOTE: LinkedIn updates this periodically

**Source 3: Glassdoor**
1. Search Glassdoor Jobs for the position
2. Cross-reference posting date

### Step 3: Update Tracker

Use Claude Code to update the unified_jobs.csv:

```python
# Example update command
import csv
from datetime import date

# Read CSV
# Find job by ID
# Update posted_date, posted_date_source, posted_date_confidence
# Write back
```

Or manually edit and run verification:
```bash
make verify_jobs
```

## Interactive Session Protocol

When user invokes `/check-freshness`:

1. **List candidates for verification:**
   - Jobs with `status='new'` and `posted_date_confidence != 'high'`
   - Jobs with `posted_date=NULL` or empty

2. **For each candidate:**
   - Try WebSearch for levels.fyi posting date
   - If not found, try WebSearch for LinkedIn job posting
   - Report findings with recommended update

3. **Batch update:**
   - Confirm updates with user
   - Apply changes to unified_jobs.csv
   - Re-run `make freshness_audit` to verify

## Rate Limiting Considerations

- **levels.fyi:** No authentication needed, gentle rate limiting
- **LinkedIn:** Rate limited, check 5-10 jobs per session max
- **Glassdoor:** Can be aggressive with blocking

**Best Practice:** Focus on highest-priority jobs first:
1. `status='new'` and unapplied
2. Target companies (from targets.yml tier 1-2)
3. Jobs where you have referrals

## Example Session

```
User: /check-freshness

Claude: Running freshness audit...

Found 8 jobs needing date verification:
1. Gusto - Staff Data Scientist (⚫ UNKNOWN, status: new)
2. Instacart - Economist/MLE II (⚫ UNKNOWN, status: new)
3. Snap - Sr Data Scientist L5 (🟢 0d, confidence: low)
...

Would you like me to verify these? I'll check levels.fyi first.

User: Yes, check the top 3

Claude: Checking levels.fyi for Gusto Staff Data Scientist...
[WebSearch: "levels.fyi Gusto Staff Data Scientist posted date"]

Found: Posted 12 days ago (2026-01-18)
Source: levels.fyi
Confidence: medium

Update unified_jobs.csv:
- posted_date: 2026-01-18
- posted_date_source: levelsfyi
- posted_date_confidence: medium

Proceed with this update? [Y/n]
```

## Freshness Tiers Reference

| Tier | Days | Icon | Action |
|------|------|------|--------|
| 🟢 FRESH | 0-14 | ✅ | Priority apply |
| 🟡 AGING | 15-29 | ⚠️ | Apply soon |
| 🟠 OLD | 30-44 | 🔶 | Verify before applying |
| 🔴 STALE | 45+ | ❌ | Deprioritize |
| ⚫ UNKNOWN | - | ❓ | Verify date |

## Related Commands

- `make freshness_audit` - Full freshness report
- `make verify_jobs` - Check job URL liveness
- `make weekly` - Sunday maintenance (includes freshness)
- `/pipeline` - Pipeline overview with freshness indicators

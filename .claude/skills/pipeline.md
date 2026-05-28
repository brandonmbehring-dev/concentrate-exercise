# /pipeline - Job Pipeline Summary

Show current job application pipeline status.

## Usage
```
/pipeline
```

## Instructions

When this command is invoked:

1. **Load data sources**:
   - Read `data/unified_jobs.csv`
   - Read `data/unified_jobs.csv` (application columns)
   - Read `data/targets.yml` for tier information

2. **Calculate metrics**:
   ```
   Pipeline Summary
   ================
   Total tracked:     XX jobs
   New (ready):       XX
   Applied:           XX
   Interviewing:      XX
   Rejected:          XX
   Archived:          XX

   By Tier:
   --------
   Tier 1 (Dream):    XX tracked, XX applied
   Tier 2 (Strong):   XX tracked, XX applied
   Tier 3 (Backup):   XX tracked, XX applied

   Urgency:
   --------
   Stale (>30 days):  XX jobs need review
   Fresh (<7 days):   XX new opportunities
   ```

3. **Show action items**:
   ```
   Recommended Actions:
   --------------------
   1. [HIGH] Apply to Google DS L4 (posted 5 days ago, Tier 1)
   2. [MED]  Archive Startup Inc role (45 days stale)
   3. [LOW]  Update status for Meta application
   ```

4. **If stale jobs exist**: Show list with days since posted
5. **If applications pending**: Show interview stages

## Example Output

```
/pipeline

Pipeline Summary (2025-12-25)
============================
Total tracked:     12 jobs
New (ready):       4
Applied:           5
Interviewing:      2
Rejected:          1
Archived:          0

By Tier:
--------
Tier 1 (Dream):    3 tracked, 2 applied (Two Sigma, Google)
Tier 2 (Strong):   6 tracked, 2 applied
Tier 3 (Backup):   3 tracked, 1 applied

Urgency:
--------
[!] 2 jobs posted >30 days ago - consider archiving
[*] 1 new opportunity added this week

Recommended Actions:
--------------------
1. Apply to Netflix DS (Tier 2, posted 3 days ago)
2. Archive Startup Inc (45 days, no response)
```

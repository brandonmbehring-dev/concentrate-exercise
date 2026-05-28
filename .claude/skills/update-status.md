# /update-status - Refresh Status Files

Regenerate all status and job board files from data sources.

## Usage
```
/update-status
```

## Instructions

When this command is invoked:

1. **Run Make targets**:
   ```bash
   cd /home/brandon_behring/Claude/job_applications
   make status && make job_board
   ```

2. **Show what was updated**:
   ```
   Status Update Complete
   ======================
   [✓] ACTIVE/JOB_STATUS.md regenerated
   [✓] ACTIVE/job_board.md regenerated

   Summary:
   - Total jobs: XX
   - Applied: XX
   - Interviewing: XX
   - Last updated: YYYY-MM-DD HH:MM
   ```

3. **If verification warnings**: Show them
4. **Remind about weekly maintenance**: If today is Sunday

## Example Output

```
/update-status

Running status update...
> make status
> make job_board

Status Update Complete (2025-12-25)
===================================
[✓] ACTIVE/JOB_STATUS.md regenerated
[✓] ACTIVE/job_board.md regenerated

Summary:
--------
Total jobs tracked: 12
New positions:      4
Applied:            5
Interviewing:       2

Maintenance Reminders:
----------------------
[!] Sunday detected - remember to run: make weekly
[!] 2 jobs are stale (>30 days) - review and archive
```

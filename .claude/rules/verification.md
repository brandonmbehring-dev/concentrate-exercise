---
paths:
  - "verification_suite/**"
---

# Verification Suite Rules

Automated verification for banned content, credential accuracy, date consistency, and information hierarchy.

## Quick Reference

```bash
make verify                                         # Full audit (via Makefile)
python3 verification_suite/00_run_full_audit.py     # Direct
python3 verification_suite/03_check_banned_content.py  # Individual check
```

**Output**: `verification_suite/reports/audit_report.md`
**Exit codes**: 0 = pass, 1 = fail

## Check Modules

| Script | Purpose | Severity |
|--------|---------|----------|
| `01_check_date_conflicts.py` | Date consistency | LOW |
| `02_check_credentials.py` | Credential claims vs canonical | HIGH |
| `03_check_banned_content.py` | Fictional stories, overclaims | CRITICAL |
| `04_check_job_data.py` | Job CSV validation | MEDIUM |
| `04_check_metrics.py` | Word/page counts | LOW |
| `05_check_hierarchy.py` | ACTIVE/ARCHIVE boundaries | HIGH |

## Extending Checks

### Add New Banned Pattern
Edit `utils/patterns.py`:
```python
BANNED_PATTERNS.append({
    "id": "new_pattern",
    "pattern": r"your regex here",
    "severity": "high",
    "suggestion": "Use this instead..."
})
```

### Add New Check Module
1. Create `NN_check_name.py`
2. Import from `utils.patterns` and `utils.reporters`
3. Return `CheckResult` with issues
4. Add to `00_run_full_audit.py`

## Pre-commit Hook

Installed at `.git/hooks/pre-commit` (symlink to `pre-commit.sh`).

Blocks commits containing: model adoption fiction, transfer-learning story, credential/experience overclaims.

## Known False Positives

- Documentation ABOUT banned content (BANNED_CONTENT.md, ERRATA.md)
- Job requirements mentioning experience levels
- Anki cards explaining what NOT to say

**Fix location**: `utils/patterns.py` - update `should_exclude_file()` or pattern regex.

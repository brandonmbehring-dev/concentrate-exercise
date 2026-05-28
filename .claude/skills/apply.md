# /apply - Pre-Submission Checklist

Run comprehensive checks before submitting an application.

## Usage
```
/apply <company>
```

## Instructions

When this command is invoked:

1. **Load company context**:
   - Read `data/targets.yml` for company profile
   - Read `data/unified_jobs.csv` for matching job listings
   - Check `ACTIVE_DOCUMENTS/resume_system/templates/company_variants/<company>.yml`

2. **Run pre-submission checklist**:
   ```bash
   python3 scripts/pre_submit_checklist.py <company>
   ```

3. **Validate resume output**:
   - Check `ACTIVE_DOCUMENTS/resume_system/output/resume_<company>.tex` exists
   - Verify no banned content patterns from `data/facts.yml`
   - Confirm all claim IDs resolve

4. **Validate cover letter** (if exists):
   - Check `ACTIVE_DOCUMENTS/resume_system/output/cover_letter_<company>.md`
   - Verify personalization matches company
   - **HARD GATE**: Run cover letter conflict validation:
     ```bash
     python3 scripts/validate_cover_letters.py <company>
     ```
   - If validation fails (exit code 1), STOP and report errors
   - If warnings only (exit code 2), show warnings but allow proceed

5. **Show checklist**:
   ```
   Pre-Submission Checklist: <Company>
   ================================
   [ ] Resume generated and validated
   [ ] Cover letter matches company values
   [ ] Cover letter conflict validation passed (HARD GATE)
   [ ] No banned content detected
   [ ] Job posting URL still active
   [ ] Applied within 30 days of posting
   [ ] Profile match confidence: HIGH/MEDIUM/LOW
   ```

6. **If issues found**: List them with severity
7. **If all clear**: Prompt to update `data/unified_jobs.csv` with submission date and status

## Example Output

```
/apply two_sigma

Pre-Submission Checklist: Two Sigma
===================================
[✓] Resume: resume_two_sigma.tex validated
[✓] Cover letter: cover_letter_two_sigma.md exists
[✓] No banned content detected
[✓] Job posting URL active (verified 2025-12-25)
[!] Job posted 28 days ago - apply soon

Ready to submit? Run:
  python3 scripts/submit_application.py two_sigma
```

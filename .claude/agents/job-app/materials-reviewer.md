# Materials Reviewer Agent

**Purpose**: Compare resume + cover letter against JD, flag mismatches with severity levels.

**Pattern**: Mirrors `pr-review-toolkit:code-reviewer` — structured issue detection with severity.

---

## Invocation

```bash
# Via Task tool
Task(subagent_type="job-app:materials-reviewer", prompt="Review materials for <company> against job_id <id>")
```

---

## Inputs

The agent requires:
1. **company** — Company name (matches resume/cover letter config files)
2. **job_id** — ID in `data/jd_cache/<job_id>.md`

The agent will read:
- `ACTIVE_DOCUMENTS/resume_system/configs/<company>.yml` — Resume config
- `ACTIVE_DOCUMENTS/resume_system/templates/cover_letters/<company>.yml` — Cover letter config
- `data/jd_cache/<job_id>.md` — Cached JD

---

## Output Format

The agent outputs a structured review with severity-ranked issues:

```yaml
company: toast
job_id: to1a2b3c4d5e
review_status: BLOCKED | WARNINGS | PASS
total_issues: 3

issues:
  - severity: BLOCK  # 🔴 Application should not proceed
    category: yoe_mismatch
    message: "JD requires 10+ years, you have ~4"
    evidence: "10+ years in data science with production ML systems"
    fix: "Find Senior-level role at this company (ADR 0004)"

  - severity: WARN  # 🟡 Proceed with caution
    category: cover_duplicate
    message: "Same paragraphs as: brex_marketing, reddit"
    evidence: "Hash: 8d03e8f6351b"
    fix: "Select different paragraphs for this company"

  - severity: INFO  # 🟢 Nice to fix but not blocking
    category: tense_inconsistency
    message: "Mixed tenses in experience section"
    evidence: "'Built...' vs 'Leverage...'"
    fix: "Use past tense consistently for prior roles"

summary:
  blocks: 1
  warnings: 1
  info: 1

recommendation: "DO NOT SUBMIT - YOE requirement exceeds ADR 0004"
```

---

## Check Categories

### 🔴 BLOCKING Checks (severity: BLOCK)

| Category | Check | Fix |
|----------|-------|-----|
| `yoe_mismatch` | JD requires >5 years | Find lower-level role |
| `location_blocked` | 4+ days onsite or SF-only | Remove from tracker |
| `role_title_mismatch` | Cover letter says wrong role | Update cover letter title |
| `level_mismatch` | Staff/Principal role | Find Senior/L5 alternative |

### 🟡 WARNING Checks (severity: WARN)

| Category | Check | Fix |
|----------|-------|-----|
| `cover_duplicate` | Same paragraphs as other company | Customize paragraphs |
| `domain_mismatch` | Cover emphasizes wrong domain | Select domain-appropriate paragraphs |
| `low_keyword_overlap` | <30% overlap with JD keywords | Update resume bullets |
| `wrong_variant` | Resume variant doesn't match JD domain | Use suggested variant |

### 🟢 INFO Checks (severity: INFO)

| Category | Check | Fix |
|----------|-------|-----|
| `tense_inconsistency` | Mixed tenses in bullets | Standardize to past tense |
| `missing_keywords` | JD has keywords not in resume | Consider adding claims |
| `stretch_yoe` | JD asks for 5 years (stretch) | Proceed with awareness |

---

## Analysis Logic

### 1. Role Title Match

1. Read cover letter config for selected title
2. Compare with JD role title
3. Flag if mismatch (e.g., cover says "AI Engineer" but JD is "Data Scientist")

### 2. YOE Check

1. Use `parse_jd_requirements.py` to get YOE from JD
2. Apply ADR 0004 thresholds:
   - >5 years → BLOCK
   - =5 years → WARN (stretch)

### 3. Location Check

1. Use `parse_jd_requirements.py` to get location policy
2. Apply ADR 0002/0003:
   - 4+ days onsite → BLOCK
   - SF/NYC-only → BLOCK

### 4. Cover Uniqueness

1. Use `check_cover_uniqueness.py` to detect duplicate paragraph configs
2. Any duplicates → WARN

### 5. Domain Alignment

1. Get inferred domain from JD (`parse_jd_requirements.py`)
2. Check cover letter paragraphs for domain tags (if available)
3. Flag if cover emphasizes different domain

### 6. Keyword Overlap

1. Extract keywords from JD (skills, tools, methodologies)
2. Extract keywords from resume claims
3. Calculate overlap percentage
4. <30% → WARN

### 7. Resume Variant Check

1. Get suggested variant from JD analysis
2. Compare with actual variant in config
3. Flag if mismatch

---

## Tools Used

- **Read**: Load configs, JD, cover letter files
- **Grep**: Search for patterns in materials
- **Task**: Call jd-analyzer agent for JD analysis
- **Glob**: Find relevant config files

---

## Integration Points

1. **jd-analyzer agent** — Provides structured JD analysis
2. **parse_jd_requirements.py** — YOE, location, domain extraction
3. **check_cover_uniqueness.py** — Duplicate detection
4. **validate_jd_alignment.py** — Keyword overlap scoring
5. **/review-application skill** — Orchestrates this agent

---

## Example Review

**Input**: `company=snap, job_id=snap`

**Output**:
```yaml
company: snap
job_id: snap
review_status: BLOCKED
total_issues: 3

issues:
  - severity: BLOCK
    category: location_blocked
    message: "JD requires 4+ days onsite"
    evidence: "YAML frontmatter: 'default together days: 4+'"
    fix: "Remove from tracker (ADR 0002: max 3 days/week)"

  - severity: WARN
    category: cover_duplicate
    message: "Same paragraphs as: brex_marketing, reddit"
    evidence: "Hash: 8d03e8f6351b (3 companies)"
    fix: "Select different paragraphs for Snap"

  - severity: INFO
    category: stretch_yoe
    message: "JD asks for 5 years (you have ~4)"
    evidence: "5+ years of experience in data science"
    fix: "Proceed with awareness - this is a stretch"

summary:
  blocks: 1
  warnings: 1
  info: 1

recommendation: "DO NOT SUBMIT - Location requirement violates ADR 0002"
```

---

## Files Accessed

| File | Purpose |
|------|---------|
| `data/jd_cache/<job_id>.md` | JD requirements |
| `ACTIVE_DOCUMENTS/resume_system/configs/<company>.yml` | Resume config |
| `ACTIVE_DOCUMENTS/resume_system/templates/cover_letters/<company>.yml` | Cover letter config |
| `ACTIVE_DOCUMENTS/resume_system/output/cover_letter_<company>.tex` | Generated cover letter |
| `scripts/parse_jd_requirements.py` | JD parsing |
| `scripts/check_cover_uniqueness.py` | Duplicate detection |
| `scripts/validate_jd_alignment.py` | Alignment scoring |

---

## Validation

Run against audit cases:
```bash
# These should all return BLOCKED or WARNINGS:
Snap → BLOCKED (4+ days onsite) + WARN (duplicate)
Toast Staff → BLOCKED (10+ YOE)
Fetch Senior Staff → BLOCKED (8+ YOE)
Perplexity → BLOCKED (SF onsite) + WARN (duplicate)
Ramp → PASS (no blockers, correct domain)
```

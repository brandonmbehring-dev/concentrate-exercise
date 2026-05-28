---
description: Guided workflow for onboarding a new role category with role master, cover letter mapping, and research-kb integration
---

# /scaffold-role — New Role Category Onboarding

## Usage

```
/scaffold-role <role_name> [--jd <job_id_or_url>]
```

**Examples:**
```
/scaffold-role data_platform_engineer
/scaffold-role applied_scientist_nlp --jd abc123def456
```

## When to Use

When you encounter a job posting that doesn't fit any existing role master:
- New role category (e.g., "Data Platform Engineer" when only DS masters exist)
- Significant variation from existing masters (e.g., "Applied Scientist - NLP" vs generic ML)
- 3+ jobs in tracker with similar titles but no matching role master

## Workflow

### Phase 1: Analysis (Read-Only)

1. **Read existing role masters** to understand patterns:
   - `ACTIVE_DOCUMENTS/resume_system/templates/role_masters/INDEX.md`
   - Closest existing master for inheritance

2. **If JD provided**, extract:
   - Required skills → match against `master/claims.yml`
   - Preferred skills → identify gaps
   - Key themes → map to cover letter paragraphs
   - Level signals → verify against ADR 0004

3. **Search tracker** for similar roles:
   ```
   grep -i "<role_keywords>" data/unified_jobs.csv
   ```

### Phase 2: Skeleton Generation

4. **Create role master** at `templates/role_masters/<role_name>.yml`:
   ```yaml
   metadata:
     role_master: <role_name>
     version: "1.0.0"
     created: "<today>"
     target_companies: []
     description: |
       <Role focus and positioning>

   inherits_from: <closest_existing_master>

   # Override sections as needed
   skills:
     - category: <primary>
       label: "<Label>"
       claim_id: <claim_id>

   # Research metadata
   # key_interview_topics: [...]
   # competitive_positioning:
   #   strengths: [...]
   #   gaps: [...]
   #   framing: "..."
   # freshness:
   #   last_updated: "<today>"
   #   next_review: "<today + 30d>"
   #   confidence: "medium"
   ```

5. **Map claims to JD** — show which claims from `claims.yml` match:
   | JD Requirement | Matching Claim | Strength |
   |----------------|---------------|----------|
   | ... | ... | STRONG/PARTIAL/GAP |

6. **Suggest cover letter paragraphs** from `cover_letter_paragraphs.yml`:
   - Opening paragraph suggestion
   - Body paragraph mapping (which existing paragraphs fit)
   - Identify gaps needing new paragraphs

### Phase 3: Research Integration

7. **Query research-kb** for relevant content:
   ```
   research_kb_search("<role_keywords>", domain="causal_inference")
   research_kb_search("<role_keywords>", domain="interview_prep")
   ```

8. **Generate competitive positioning**:
   - Strengths (from claims + portfolio)
   - Gaps (from JD requirements not matched)
   - Framing language (domain bridge narrative)

### Phase 4: Validation

9. **Check against constraints**:
   - [ ] Level appropriate (ADR 0004)?
   - [ ] Skills rated 4+ in `skills_rating.yml`?
   - [ ] No banned content in generated text?
   - [ ] Publications/presentations enabled?

10. **Update INDEX.md** with new entry

## Output

Produces:
1. New role master YAML file
2. JD-to-claim mapping table
3. Suggested cover letter paragraph set
4. Research-kb queries for interview prep
5. Updated INDEX.md

## Dependencies

- `master/claims.yml` — claim bank
- `master/cover_letter_paragraphs.yml` — paragraph bank
- `data/portfolio.yml` — STAR stories
- research-kb MCP server — interview prep content
- `master/skills_rating.yml` — skill proficiency ratings

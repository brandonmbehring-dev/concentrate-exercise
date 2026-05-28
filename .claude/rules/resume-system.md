---
paths:
  - "ACTIVE_DOCUMENTS/resume_system/**"
---

# Resume System Rules

Claim-based resume and cover letter derivation system.

## Quick Reference

```bash
make resume_<company>   # Generate .tex AND compile PDF
make cover_<company>    # Generate cover letter AND compile PDF
make validate           # Validate all configs
make all                # Generate everything (all .tex + PDFs)
```

**Note**: All targets automatically compile PDFs (2026-01-05 update).

**Available targets**: google, two_sigma, block, affirm, oscar_health, netflix, meta, uber, instacart, brex, plaid, sofi, gusto, flatiron_health, travelers

## Architecture

```
resume_system/
├── master/
│   ├── claims.yml                 # Single source (137 validated claims)
│   └── cover_letter_paragraphs.yml
├── templates/
│   ├── role_masters/              # Role-based configs (10 roles)
│   ├── company_variants/          # Company-specific (14+ companies)
│   ├── cover_letters/             # Cover letter configs
│   ├── resume_base.tex.j2         # LaTeX Jinja2 template
│   └── cover_letter_base.md.j2
├── scripts/
│   ├── generate_resume.py
│   └── generate_cover_letter.py
└── output/                        # Generated files
```

## Claim System

**All resume text lives in `master/claims.yml`**. Role masters and company variants only reference claim IDs.

### Claim Schema
```yaml
- id: exp_pru_lead_pricing
  resume: |      # Terse bullet for resume
    Built prescriptive pricing models...
  cover_letter: | # Narrative prose (optional)
    I originated and developed...
  source_refs:
    - facts.yml#verified.title
    - portfolio.yml#star_stories.pricing
  validated: "2025-12-23"
  tags: [pricing, leadership]
```

### Claim Categories (137 total)
| Category | Count | Prefix |
|----------|-------|--------|
| Summaries | 9 | `summary_` |
| Prudential Lead | 17 | `exp_pru_lead_` |
| Prudential Senior | 13 | `exp_pru_senior_` |
| Prudential DS | 15 | `exp_pru_ds_` |
| NYU | 9 | `exp_nyu_` |
| NJIT | 7 | `exp_njit_` |
| Skills | 17 | `skills_` |
| Credentials | 18 | `cred_` |
| Education | 3 | `edu_` |
| Publications | 3 | `pub_` |
| Research Impact | 5 | `impact_` |
| Key Projects | 5 | `project_` |
| Business Impact | 5 | `biz_impact_` |

## Inheritance

Company variants inherit from role masters:

```yaml
# templates/company_variants/oscar_health.yml
inherits_from: ds_risk_modeling
overrides:
  summary: summary_healthcare
additions:
  experience:
    - exp_pru_lead_healthcare
```

## Validation

The generator validates against banned content from `data/facts.yml`:
- "transfer-learning presentation" (fictional)
- "20-to-95 percent adoption" (fictional)
- Experience overclaims (actual: 4 years at Prudential)
- Credential overclaims (actual: 22 professional)

**Credential Rule (MANDATORY)**: NEVER use separate `aws:` or `gcp:` keys. ALWAYS use `cloud: cred_cloud_two_sigma` (condensed 4-cert format).

**PhD Credibility Rule (MANDATORY)**: ALWAYS enable `publications: true` and `presentations: true` by default. PhD is the key differentiator.

## Standard Patterns (v2.2.0) -- MANDATORY

| Claim ID | Section | When to Use |
|----------|---------|-------------|
| `exp_pru_lead_002_chief_actuary_scale` | Lead DS | DS/Analytics/Applied Scientist roles |
| `exp_pru_lead_009` | Lead DS | MLE/AI Engineer roles |
| `exp_pru_senior_survival_google` | Senior DS | **ALWAYS** |
| `pub_001`, `pub_002`, `pub_003` | Publications | **ALWAYS** |
| `presentation_pru_elasticity`, `presentation_siam_2021` | Presentations | **ALWAYS** |
| `exp_nyu_postdoc_julia_hpc_distributed` | NYU | Applied Scientist only |

## Messaging Standards (v2.3.0) -- MANDATORY

1. **Domain Bridge Narrative**: "[Domain A] and [Domain B] share the same core challenge..."
2. **Leadership-Driven Framing**: "When leadership needed to understand [X], I built..."
3. **Noun-Phrase Summaries**: "[Role] [verb]-ing [achievement]..."
4. **Hybrid AI Tool Mentions**: Skills = "Claude Code"; Narratives = "AI-augmented workflows"
5. **Growth Metrics Without Attribution**: Show contribution, not sole attribution
6. **Direct Framing (v2.6.0)**: BANNED: "hardest part wasn't" pattern. Use direct framing.

### AI-Tool Role Gating (v2.4.1)

| Role Type | AI Tool Visibility |
|-----------|-------------------|
| AI/LLM Engineering | **PROMINENT** |
| ML Platform/Infrastructure | **MODERATE** |
| DS/Analytics | **MINIMAL** |
| Quant/Fintech | **AVOID** |

## Credential Standards (v2.4.0) -- MANDATORY

### Role-Based Credential Decision Framework (v9.1.0)

| Role Type | SOA | Finance (CFA/FRM) | Cloud Credential |
|-----------|-----|-------------------|------------------|
| DS, Experimentation (fintech/marketplace) | **KEEP** | **KEEP** | `cred_cloud_two_sigma` |
| DS, Experimentation (pure tech) | **KEEP** | **HIDE** | `cred_cloud_two_sigma` |
| Applied Scientist (Causal) | **KEEP** | **HIDE** | `cred_cloud_two_sigma` |
| Fintech/Quant | **KEEP** | **KEEP** | `cred_cloud_two_sigma` |
| ML Engineer | **HIDE** | **HIDE** | `cred_cloud_tech_depth` |
| AI/Infrastructure | **HIDE** | **HIDE** | `cred_cloud_tech_depth` |
| Product Analytics | **HIDE** | **HIDE** | `cred_cloud_tech_depth` |

**Finance credential rule**: CFA/FRM only adds signal at companies where financial modeling is core to the role (fintech, insurance, marketplace pricing). At pure tech companies, it risks the "finance lifer" perception.

## Resume Optimization Protocol

### Bullet Point Narrative Arc
| Role Level | Narrative | Focus |
|------------|-----------|-------|
| PhD/Postdoc | **Foundation** | Intellectual horsepower |
| Data Scientist | **Builder** | Learned to ship |
| Senior DS | **Engineer** | Production practices |
| Lead DS | **Architect** | Owns the vertical |

**Rules**: Bullets reinforce the arc. Remove redundancy. Research Impact always disabled. Target 13-15 bullets total.

### No Credential Name-Dropping Rule
NEVER list credentials in summaries or cover letters. Credentials belong in CERTIFICATIONS section.

## Pre-Submission Checklist
```bash
python3 scripts/pre_submit_checklist.py <company>
```

## Anti-Static-Folder Rule (v3.3.0) -- MANDATORY

**NEVER create static snapshot folders of generated output** (e.g., `top20_tex/`, `priority_pdfs/`).
All audits run against `output/` with dynamic company selection from the tracker.

Use `make audit-priority` for dynamic priority audits. The script queries the tracker,
regenerates the top N companies, and runs quality checks -- no snapshot folders needed.

## Integration Points
- Canonical facts: `data/facts.yml`
- Portfolio stories: `data/portfolio.yml`
- Verification suite: `verification_suite/`
- Pre-submit script: `scripts/pre_submit_checklist.py`

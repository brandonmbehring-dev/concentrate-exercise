---
description: Auto-generate company research profile for interview prep and application targeting
---

# /research-company — Company Research Generation

## Usage

```
/research-company <company_name> [--depth light|moderate|thorough]
```

**Examples:**
```
/research-company garner_health
/research-company two_sigma --depth thorough
```

**Default depth**: moderate

## When to Use

- Adding a new target company to the pipeline
- Preparing for an interview (complements `/prep-interview`)
- Refreshing stale company research (>60 days old)
- Called automatically by `/scaffold-role` when a new company appears

## Workflow

### Phase 1: Data Collection

1. **Check existing data** first:
   - `data/targets.yml` — existing company profile
   - `ACTIVE/LATEST_RESEARCH/` — previous research files
   - `data/unified_jobs.csv` — current job listings for this company

2. **Web research** (depth-dependent):

   | Depth | Sources | Time |
   |-------|---------|------|
   | light | Levels.fyi cache, tracker data | 2 min |
   | moderate | + Web search (interview process, recent news) | 5 min |
   | thorough | + Glassdoor, Interview Query data, H1B database | 15 min |

3. **Levels.fyi data** (if cached):
   ```
   ls data/levelsfyi_cache/<company>*.json
   ```
   Extract: TC ranges, YOE expectations, recent data points

4. **Interview Query data** (if available):
   ```
   ls interview_query_data/data/<company>*.json
   ```
   Extract: Common questions, interview format, difficulty

### Phase 2: Research Synthesis

5. **Generate company profile**:
   ```yaml
   company: "<Name>"
   sector: "<Industry>"
   stage: "<Public/Private/Series X>"
   ds_team_size: "<Estimate>"
   interview_process:
     stages: ["phone_screen", "technical", "onsite"]
     typical_duration: "<X weeks>"
     known_topics: ["list"]
   compensation:
     l4_equivalent:
       base: "$X-$Y"
       total: "$X-$Y"
     source: "levels.fyi / glassdoor / reported"
     as_of: "<date>"
   culture_signals:
     remote_policy: "<policy>"
     tech_stack: ["list"]
     ds_focus: "<experimentation / ml / analytics>"
   h1b_sponsorship: true/false/"unknown"
   recent_news:
     - "<headline> (<date>)"
   recommended_role_masters:
     - "<role_master_1>"
     - "<role_master_2>"
   ```

6. **Map to role masters**:
   - Which role master(s) best fit this company's open positions?
   - Check role master INDEX.md for positioning

7. **Identify interview prep gaps**:
   - What topics does this company ask about?
   - Do we have research-kb content for those topics?
   - Flag any gaps needing prep work

### Phase 3: Output

8. **Save research** to `ACTIVE/LATEST_RESEARCH/<company>_research.yml`

9. **Update targets.yml** if company not already present:
   - Add comp bands
   - Add contact/referral info if known
   - Add sponsorship status

10. **Present summary** to user:
    - Key findings
    - Recommended role master
    - Interview prep priorities
    - Any red flags (level mismatch, location, sponsorship)

## Depth Levels

### Light (2 min)
- Levels.fyi cache only
- Tracker data summary
- Basic company info from existing targets.yml

### Moderate (5 min, default)
- All of light, plus:
- Web search: "[company] data scientist interview process 2026"
- Web search: "[company] hiring layoffs recent news"
- Interview format summary

### Thorough (15 min)
- All of moderate, plus:
- Interview Query scraping (if login available)
- H1B sponsor database check
- Glassdoor reviews summary
- Team structure research
- Research-kb cross-reference

## Integration Points

- **`/scaffold-role`**: Calls this skill when encountering unknown company
- **`/prep-interview`**: Research output feeds interview prep
- **`add_job.py`**: Can suggest running this after adding new company
- **`data/targets.yml`**: Updated with new research findings
- **`ACTIVE/LATEST_RESEARCH/`**: Research files stored here

## Constraints

- Verify remote/hybrid BEFORE recommending (ADR 0009)
- Check leveling against ADR 0004 (L4 target, Staff auto-remove)
- Check comp floor against ADR 0001 ($210K total / $180K salary)
- SF-only roles are BLOCKED (NJ-based, no relocation — ADR 0003)

# /extract-jd-playwright — Playwright JD Extraction Workflow

Extract job descriptions from JS-heavy ATS sites using Playwright MCP tools.

## When to Use

Use this skill when:
- `add_job.py` reports "needs Playwright"
- URL is from Workday, Greenhouse, Lever, CareerPuck, Oracle HCM, LinkedIn, etc.
- WebFetch returns empty or minimal content

## Prerequisites

Playwright MCP tools must be available:
- `browser_navigate`
- `browser_snapshot`

## Workflow

### Step 1: Navigate to Job URL

```
Use browser_navigate to open the job posting URL.
Wait for page to fully load (JS content to render).
```

### Step 2: Take Accessibility Snapshot

```
Use browser_snapshot to capture the accessibility tree.
This returns YAML with the page structure and text content.
```

### Step 3: Parse Snapshot into JD

Use the jd_extractor module to parse the snapshot:

```python
from jd_extractor import create_jd_from_playwright_snapshot, save_jd_cached

# snapshot_yaml is the output from browser_snapshot
content = create_jd_from_playwright_snapshot(
    snapshot_yaml,
    url="https://...",
    company="Company Name",
    title="Job Title",
)

# Save to cache
save_jd_cached(job_id, content)
```

### Step 4: Add Job to Tracker

```bash
python scripts/add_job.py \
  --company "Company" \
  --title "Job Title" \
  --url "https://..." \
  --location "Remote" \
  --no-jd  # JD already cached from step 3
```

## Example Session

```
User: Add this Lyft job: https://app.careerpuck.com/job-board/lyft/job/8392976002

Claude: This is a CareerPuck URL (JS-heavy). Let me use Playwright to extract the JD.

[Uses browser_navigate to open URL]
[Uses browser_snapshot to get accessibility tree]
[Parses snapshot with create_jd_from_playwright_snapshot()]
[Saves to data/jd_cache/abc123.md]

Claude: Extracted JD (2,450 chars). Preview:
- Location: San Francisco, CA (Hybrid)
- Requirements: 5 found
  - Python proficiency
  - ML/AI experience
  ...

[Uses add_job.py --no-jd to add to tracker]

Job added: abc123
```

## Supported ATS Domains

The following domains automatically trigger Playwright extraction:

| Domain Pattern | ATS Name |
|----------------|----------|
| `*.myworkdayjobs.com` | Workday |
| `*.greenhouse.io` | Greenhouse |
| `*.lever.co` | Lever |
| `app.careerpuck.com` | CareerPuck |
| `*.ocs.oraclecloud.com` | Oracle Cloud HCM |
| `linkedin.com/jobs` | LinkedIn |
| `*.workable.com` | Workable |
| `*.ashbyhq.com` | Ashby |
| `*.smartrecruiters.com` | SmartRecruiters |
| `*.icims.com` | iCIMS |
| `*.taleo.net` | Taleo |
| `*.jobvite.com` | Jobvite |

## Troubleshooting

### Empty Snapshot

If browser_snapshot returns minimal content:
1. Wait longer for page to load (some ATS are slow)
2. Check if page requires login (job might be private)
3. Try scrolling down to load lazy content

### Parsing Issues

If create_jd_from_playwright_snapshot extracts too little:
1. Check the raw YAML structure
2. Use manual paste fallback: `add_job.py --force-paste`
3. Manually extract key sections and create JDContent

### Page Blocked

Some sites block automated browsers:
1. User-agent detection → Cannot easily work around
2. CAPTCHA → Manual extraction required
3. Login wall → Use manual paste

## Related

- `scripts/jd_extractor.py` — Core extraction module
- `scripts/add_job.py` — Job tracking CLI
- `data/jd_cache/` — Cached JD files

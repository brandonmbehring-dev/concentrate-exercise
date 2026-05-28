---
paths:
  - "coding_interview_guide_2026/**"
---

# Coding Interview Guide Rules

Combined Python + SQL interview guide: 61 problems organized by tier and interleaved by language.

## Quick Reference

```bash
cd coding_interview_guide_2026/latex_version
make digital      # Build digital PDF
make print        # Build print variant (with line numbers)
make pilot        # Quick test build (single pass)
make all          # Build both variants
make clean        # Remove generated files
```

## Structure

- **Part I**: Tier 1 Must-Know (30 problems) - Python + SQL
- **Part II**: Tier 2 Should-Know (20 problems) - Python + SQL
- **Part III**: Tier 3 Nice-to-Have (11 problems) - Python + SQL
- **Appendices**: Quick refs, time estimates, SQL-Pandas crossref, progress tracker

## Tier Breakdown

| Tier | Python | SQL | Total | Focus |
|------|--------|-----|-------|-------|
| Tier 1 | 15 | 15 | 30 | Must-know (80%+ DS rounds) |
| Tier 2 | 10 | 10 | 20 | Should-know (30-50% rounds) |
| Tier 3 | 5 | 6 | 11 | Nice-to-have (rare) |

## Time Budget

**Total**: 14 hours practice / 21 hours interview pace.

## Build Requirements

```bash
sudo apt install texlive-full latexmk
pip install Pygments
```

- Minted code blocks: white background + `default` Pygments style
- Shell escape enabled for syntax highlighting
- Tufte-style layout with margin notes

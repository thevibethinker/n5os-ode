---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_ovCUjlzBxm8TzCGZ
---

# FOHE NYC Q1 2026 Newsletter Build

**Status:** Planning complete → Launching
**Orchestrator:** Vibe Operator
**Build Type:** Parallel content + design synthesis

## Drops
- D1: Survey Synthesis (Researcher) → survey_insights.yaml
- D2: Slack Highlights (Writer) → highlights.md
- D3: Email Template (Builder) → newsletter_template.html
- D4: Content Assembly (Writer) → newsletter_content.md
- D5: Final Integration (Builder) → FOHE_NYC_Q1_2026_Newsletter.html

## Dependencies
- D1, D2, D3, D4 run in parallel
- D5 waits for D3 + D4

## Artifacts Location
`/home/workspace/N5/builds/fohe-newsletter-q1-2026/artifacts/`

## Launch Command
```bash
python3 Skills/pulse/scripts/pulse.py start fohe-newsletter-q1-2026
```

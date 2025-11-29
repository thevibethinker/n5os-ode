# Warm Intro Drafts — 2025-11-28

**Generated:** 2025-11-28 23:40:00 ET  
**Scope:** Last 30 days of [M] meetings in Personal/Meetings/Inbox  
**Status:** DRAFTS ONLY - Manual send required

## Summary

- Meetings scanned: 0
- Intro signals detected: 0
- Email pairs generated: 0
- New this run: 0 (deduplicated)

## Findings

**No [M] meetings found in Personal/Meetings/Inbox folder.**

The workflow is configured to process meetings exclusively from the Inbox folder:
- Location: `/home/workspace/Personal/Meetings/Inbox`
- Status: Empty (0 meetings)
- Date range: Last 30 days (since 2025-10-30)

## Analysis

While [M] meetings exist in other locations under `/home/workspace/Personal/Meetings/`, the workflow explicitly excludes them per architectural design:

> "Meetings with [M] tags in `file Personal/Meetings/Inbox` folder ONLY (Ignore meetings in all other locations)"

**Rationale:** The Inbox folder serves as a staging area for meetings requiring warm intro processing. Meetings in other locations have either:
1. Already been processed for intros
2. Been archived as not requiring introductions
3. Are internal meetings (no intros needed)

## Next Steps

To activate this workflow:
1. Move meetings requiring intro processing to `Personal/Meetings/Inbox/`
2. Ensure they contain B07_WARM_INTRO_BIDIRECTIONAL.md blocks
3. Re-run this scheduled task

## Statistics

- Most common intro type: N/A
- Average intros per meeting: N/A
- Meetings with no intros: N/A

---

**REMINDER: All emails are DRAFTS. Review and send manually.**


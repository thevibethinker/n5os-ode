---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
---

# Pattern: Warm Intro Zero-Signal Digest

## Use Case

Scheduled warm-intro generator runs when there are no `B07_WARM_INTRO_BIDIRECTIONAL.md` blocks in scope, but existing intro drafts may already be present.

## Steps

1. **Scan scope:**
   - Count `[M]` meetings in `Personal/Meetings/Inbox` for the last 30 days.
   - Check for `B07_WARM_INTRO_BIDIRECTIONAL.md` files; if none, record `0` warm-intro blocks.
2. **Confirm preconditions:**
   - Verify `Prompts/warm-intro-generator.prompt.md` exists.
3. **Inspect existing drafts:**
   - Search Inbox for `INTRO_*_opt_in.md` and corresponding `INTRO_*_connector.md` files.
   - Group by `{meeting, PersonA, PersonB}` to identify unique intros and note duplicate file locations (e.g., M-level vs P-level).
4. **Generate digest only:**
   - Create `N5/digests/warm-intro-drafts-{YYYY-MM-DD}.md` with:
     - YAML frontmatter.
     - Summary stats for **this run** (meetings scanned, warm-intro blocks found, intro signals, new pairs = 0).
     - "New Drafts Generated" section explicitly stating none were generated.
     - "Previously Generated (Skipped)" section listing existing intro drafts with file paths.
     - Stats section including zeroed metrics and a clear reminder that all emails are drafts.
5. **No manifest writes:**
   - Skip `manifest.json` updates when there are no warm-intro blocks and no new intros detected.

## When to Apply

- Any scheduled warm-intro digest run where structural prerequisites for semantic intro detection (B07 warm-intro blocks) are missing.
- Useful for:
  - Verifying the pipeline is wired without forcing email generation.
  - Surfacing existing intro drafts without mutating meeting manifests.

## Notes

- Keep language in the digest strictly factual ("this run" vs historical totals).
- Treat existing intro drafts as "Previously Generated (Skipped)" even when they fall partially outside the current `[M]` scope, but label meeting IDs and paths precisely.
- Avoid fabricating intro types when no intros were detected; use `N/A` explicitly instead.


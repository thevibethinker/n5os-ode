---
created: 2025-12-01
last_edited: 2025-12-01
version: 1.0
---

# Pattern: Warm Intro Backwards Run with No Eligible Meetings

## Context
Scheduled task to generate warm introduction email drafts from completed meetings with intro signals, using `[M]`-tagged meetings in `Personal/Meetings/Inbox` that contain `B07_WARM_INTRO_BIDIRECTIONAL.md`.

## Pattern
1. **Scan mechanically for eligible meetings**
   - Use `find` (or equivalent) scoped to `/home/workspace/Personal/Meetings/Inbox`.
   - Filter for directories whose names contain `[M]` and that contain `B07_WARM_INTRO_BIDIRECTIONAL.md`.
2. **Short-circuit on empty result set**
   - If no eligible meeting folders are found, *do not* attempt:
     - Stakeholder extraction
     - Intro opportunity detection
     - Email draft generation
     - Manifest updates
3. **Still generate a run-level digest**
   - Create a dated digest at `N5/digests/warm-intro-drafts-{YYYY-MM-DD}.md` with:
     - YAML frontmatter
     - Explicit zero metrics (meetings scanned, intros detected, emails generated)
     - Clear statement that no eligible meetings were found in scope.
4. **Preserve invariants**
   - Respect scope constraints (Inbox only, `[M]` only, B07 present).
   - Do not touch meetings outside scope or older than the time window.

## When to Reuse
- Any scheduled run of the backwards-looking warm intro workflow where the scan yields zero eligible `[M]` meetings with B07 in the allowed folder.

## Signals It Applied Correctly
- `find` (or equivalent scan) returned an empty set for scoped criteria.
- Digest file exists for the run date with all counts at zero.
- No new INTRO_* files or manifest changes were made in `Personal/Meetings/Inbox`.


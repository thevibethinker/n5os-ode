---
created: 2025-12-12
last_edited: 2025-12-12
version: 1.0
---

# Pattern: Warm intro agent — empty scope handling

## Context
When the warm introduction scheduled task runs and finds no eligible `[M]` meetings in `Personal/Meetings/Inbox` (last 30 days with `B07_WARM_INTRO_BIDIRECTIONAL.md` present), it should still produce a meaningful, truthful digest instead of failing silently or emitting placeholder content.

## Steps
1. Run the `find`-based scan exactly as specified in the task instructions, scoped to the last 30 days and requiring `B07_WARM_INTRO_BIDIRECTIONAL.md`.
2. If the scan returns **no meeting folders**:
   - Set `meetings_scanned = 0`, `intro_signals = 0`, `email_pairs = 0`, `new_this_run = 0`.
3. Create or overwrite the digest file at `N5/digests/warm-intro-drafts-{YYYY-MM-DD}.md` with:
   - YAML frontmatter (created/last_edited/version).
   - A clear statement that no eligible meetings were found in scope.
   - Summary counts all set to 0.
   - "Previously Generated" section explicitly noting there is nothing within the last-30-days scope.
   - Statistics section using explicit "N/A" / `0.0` values instead of placeholders.
4. Update `SESSION_STATE.md` Progress with a concise, factual line (including the digest path).
5. Skip manifest.json updates entirely (no meetings were processed).

## Why this works
- Respects the scoped definition of work (last 30 days, Inbox, `[M]`, `B07` present).
- Preserves observability: each run leaves a trace, even when there is nothing to do.
- Avoids stub/placeholder content while still satisfying the digest requirement.
- Keeps downstream automations simple—other systems can rely on the presence of a daily digest file without special-casing "no data" days.

## When to reuse
Use this pattern for other scheduled agents that:
- Operate on a time-bounded slice of data (e.g., last N days), **and**
- Are required to emit a digest/report on every run, even when the scope is empty.

Key principle: **"Empty scope" is still a valid, meaningful outcome and deserves a real artifact.**


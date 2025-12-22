---
created: 2025-12-07
last_edited: 2025-12-07
version: 1.0
---

# Reasoning Pattern: Scheduled Agent Empty-Scope Handling

## When to Use
- A scheduled task runs over a time-bounded scope (e.g., last 30 days of meetings).
- Mechanics complete successfully (scan executed), but **no new items** meet the semantic criteria (e.g., no B07_WARM_INTRO_BIDIRECTIONAL blocks).

## Core Moves
1. **Differentiate three counts clearly**
   - *Scope size:* total items scanned (e.g., all `[M]` meetings in Inbox last 30 days).
   - *Signals in scope:* items that actually have relevant signals (e.g., meetings with B07 or existing INTRO files).
   - *New work this run:* items that resulted in fresh artifacts (often `0` on an empty run).

2. **Treat "no new work" as a valid outcome, not an error**
   - Don't fabricate intros, drafts, or placeholder content.
   - Don't backfill outside the declared scope to "keep busy".

3. **Still generate a digest artifact**
   - Record what was scanned, what was found, and why no new artifacts were created.
   - Include explicit statements like: "New this run: 0 (no new B07 blocks to process)".

4. **Surface previously generated items separately**
   - List existing artifacts in-scope (e.g., existing INTRO_* files) under a "Previously Generated" section.
   - Make it clear they were **not** regenerated this run.

5. **Avoid unnecessary state mutation**
   - Skip manifest updates when no meetings actually went through the semantic pipeline.
   - Limit changes to a single digest/report file plus SESSION_STATE.

## Why It Works
- Preserves honesty about work done (no P15 "false completion").
- Keeps the system observable even when there is nothing new to generate.
- Protects against noisy or misleading artifacts created just to show activity.

## Example
- Warm-intro agent run on 2025-12-07:
  - 17 `[M]` meetings scanned in `Personal/Meetings/Inbox`.
  - 0 meetings with B07_WARM_INTRO_BIDIRECTIONAL blocks.
  - 2 existing intro pairs noted as "Previously Generated (Skipped This Run)".
  - New drafts generated: 0.
  - Single digest created at `N5/digests/warm-intro-drafts-2025-12-07.md` summarizing the above.



---
created: 2025-12-10
last_edited: 2025-12-10
version: 1.0
---

# Pattern: Warm Intro Zero-Case Sweep (v1)

## Context
Scheduled task: generate warm introduction email drafts from completed meetings with intro signals, scanning only meetings in `Personal/Meetings/Inbox` with `[M]` tags and `B07_WARM_INTRO_BIDIRECTIONAL.md` blocks, limited to the last 30 days.

In this run there were **no eligible meetings** (no `[M]` folders under `Personal/Meetings/Inbox`), so the system needed a safe, non-noisy "zero-case" behavior.

## Steps
1. **Load scheduler context and session state**
   - Ensure `SESSION_STATE.md` exists and classify as `build`.
   - Load `n5_load_context.py scheduler` for scheduled-task protocol.

2. **Validate prerequisites (fail-fast only on hard requirements)**
   - Check `Personal/Meetings/Inbox` exists.
   - Check `Prompts/warm-intro-generator.prompt.md` exists (hard requirement).
   - Soft-check optional references (voice file, architecture doc) and treat missing as warnings, not blockers.

3. **Scope-limited meeting discovery**
   - Use the exact canonical command from the instruction:
     - `find ... -name '*[M]' -type d -mtime -30` → filter to last 30 days.
     - Further filter to only meetings that contain `B07_WARM_INTRO_BIDIRECTIONAL.md`.
   - If command returns **no paths**, treat as "zero eligible meetings" rather than an error.

4. **Short-circuit heavy semantic work when there is no data**
   - Skip B07/B08/B02/B26 reads entirely when there are no candidate meetings.
   - Skip intro detection, draft generation, and manifest updates.

5. **Still generate a structured digest**
   - Create `N5/digests/warm-intro-drafts-{date}.md` with:
     - YAML frontmatter (created/last_edited/version).
     - Scope: last 30 days of `[M]` meetings.
     - Summary counts all at 0.
     - Explicit "no new warm intro opportunities" message.
     - Statistics section with N/A values where appropriate (no placeholders or TODOs).

6. **Update SESSION_STATE**
   - Record progress and outcome (`Overall 100%`, 0 eligible meetings, digest path).
   - Register the digest file as a permanent artifact before/while creating it.

## When to Use
- Any scheduled sweep-style task where **zero data in scope** is a valid and expected state.
- Pipelines that must distinguish between "no results" and "pipeline failure".

## Key Properties
- **Non-noisy**: Does not fabricate intros or placeholder content.
- **Auditable**: Digest file exists even in zero-case runs, with explicit counts and timestamp.
- **Safe**: No destructive operations when there is no data.
- **Aligned with spec**: Honors the 30-day window and `[M]` + B07 gating logic.

## Future Reuse
For other digest-style scheduled tasks:
- Reuse the pattern of **hard vs. soft prerequisites**, **scope-limited discovery**, and **zero-case digest generation**.
- Ensure each task defines what "zero in scope" looks like and how it should be reported (rather than treated as an error).


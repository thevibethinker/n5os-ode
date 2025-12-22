---
created: 2025-12-14
last_edited: 2025-12-14
version: 1.0
---

# Pattern: Warm Intro Zero-Scope Digest Run

## Context
Scheduled warm-intro agent run where no eligible meetings are found in the target window (no `[M]` folders in `Personal/Meetings/Inbox` with `B07_WARM_INTRO_BIDIRECTIONAL.md` in the last 30 days).

## Steps
1. **Verify environment prerequisites**
   - Confirm `Personal/Meetings/Inbox` exists.
   - Confirm `Prompts/warm-intro-generator.prompt.md` exists (fail fast if missing).
2. **Run scoped search**
   - Use the canonical `find` pattern from the instruction (`-name "*[M]" -mtime -30` plus `B07` existence check).
3. **Branch on result count**
   - If ≥1 meetings: proceed to semantic intro detection + draft generation.
   - If 0 meetings: skip generation steps entirely.
4. **Still generate a digest**
   - Create `N5/digests/warm-intro-drafts-{YYYY-MM-DD}.md` with:
     - Accurate zero counts (meetings scanned, intros, pairs, new this run).
     - Explicit note that no eligible meetings were found in scope.
5. **Update SESSION_STATE**
   - Log an explicit progress line noting zero-scope run and digest path.

## Why It Works
- Honors instructions and success criteria without fabricating work.
- Produces a concrete artifact every run, which is important for downstream monitoring.
- Makes zero-scope runs debuggable and visible instead of silent no-ops.

## When to Reuse
Use this pattern for any scheduled digest/report task where:
- The scope can legitimately be empty (no new data), and
- The system still benefits from a dated artifact and progress log instead of doing nothing.

---
created: 2025-12-05
last_edited: 2025-12-05
version: 1.0
---

# Pattern: Warm Intro – B07 Gating and Zero-Intro Runs

## Context
Scheduled warm-intro task ran against `Personal/Meetings/Inbox` for last 30 days of `[M]` meetings. Several meetings existed, but none had `B07_WARM_INTRO_BIDIRECTIONAL.md` (or supporting B02/B08 blocks) generated yet.

## Reasoning Pattern
1. **Structural Gate First:** Treat presence of B07 (and related intelligence blocks) as a strict eligibility gate for warm-intro generation.
2. **Scan vs. Generate:**
   - Scan all `[M]` meetings in scope to understand coverage.
   - Only *process* meetings for intros when B07 exists and is non-empty.
3. **Zero-Intro Handling:**
   - If no eligible meetings found, generate a digest anyway with:
     - Meetings scanned count
     - Zero intros detected
     - Explicit note that B07 is missing and MG-2 still needs to run
   - Do **not** fabricate intros from transcripts alone.
4. **Manifest Discipline:**
   - Keep `warm_intros_generated.count = 0` and `status = "none_detected"` when B07 is absent.
   - Refresh `warm_intros_generated.timestamp` to the current run time so downstream systems know the check occurred.
5. **Non-Destructive Defaults:**
   - Never flip status to `drafts_ready` unless actual intro drafts are written to disk.
   - Avoid touching other manifest fields (only the warm-intro sub-object).

## When to Reuse
Use this pattern for any scheduled workflow that depends on upstream intelligence blocks:
- Warm intros (B07/B08/B02)
- Blurbs (B14)
- Follow-up emails (commitment blocks)

If upstream blocks are missing or incomplete, prefer a **zero-output, fully-documented run** over guessing from raw transcripts.

## Signals That This Pattern Applies
- Scheduled job triggers but core intelligence block is missing.
- Manifest already contains a `none_detected` or similar status note.
- The only available source is a raw transcript or partial metadata.

## Outcome
This pattern prevents premature or speculative outreach, keeps manifests accurate, and still produces a useful daily digest even when no intros are generated.

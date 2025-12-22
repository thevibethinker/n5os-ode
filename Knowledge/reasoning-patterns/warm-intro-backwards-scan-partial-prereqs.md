---
created: 2025-12-09
last_edited: 2025-12-09
version: 1.0
---

# Pattern: Warm-intro backwards scan under partial prerequisites

## When to use
- Scheduled or batch warm-intro generation from meeting intelligence when:
  - B07_TONE_AND_CONTEXT.md and B01_DETAILED_RECAP.md exist for [M] meetings in `Personal/Meetings/Inbox/`,
  - B02_COMMITMENTS.md, B08_STAKEHOLDER_INTELLIGENCE.md, and B07_WARM_INTRO_BIDIRECTIONAL.md are **missing or not yet wired**, and
  - Some intro drafts (opt-in / connector) may already exist from earlier runs.

## Core moves
1. **Scope mechanically, decide semantically**
   - Use shell / scripts only to:
     - Find `[M]` meeting folders with `B07_TONE_AND_CONTEXT.md` in `Personal/Meetings/Inbox/` (last 30 days).
     - Read `manifest.json` + `B26_MEETING_METADATA.md` to classify meetings as `internal` vs `external`.
   - Reserve the LLM for:
     - Reading B01/B07/B26 to understand relationships and commitments.
     - Identifying true warm-intro opportunities (Person A ↔ Person B) from narrative context.

2. **Respect meeting_type gate**
   - Skip all meetings where `meeting_type` (manifest) or `Type` (B26) is clearly `internal`.
   - Default missing/unknown `meeting_type` to "external" but be conservative: require an explicit intro signal in B01/B07 before acting.

3. **Use B01 as commitments fallback**
   - When B02_COMMITMENTS.md is absent, treat B01_DETAILED_RECAP.md as the source of truth for:
     - Who promised to introduce whom.
     - Whether status is still pending vs already closed.
   - Read B01 **end sections** ("Next steps" / "Agreed next steps") carefully; that’s where intro intent usually lives.

4. **Detect intro signals semantically**
   - Look for patterns in B01/B07 like:
     - "I’d be happy to introduce you to…"
     - "I can put your resume in front of…"
     - "I’d love that intro to…"
   - Confirm all of:
     - Clear Person A, clear Person B.
     - Directionality (A → B) and connector (usually V or the other participant).
     - Status is still *pending/possible* (no language like "already introduced" / "we spoke last week").

5. **Deduplicate using existing INTRO_* files**
   - For each detected (Person A, Person B) pair:
     - Compute the canonical intro file stem from existing files instead of inventing a new naming scheme.
       - Example: infer `Alan-Hin` / `Shivam-CorridorX` from `INTRO_Alan-Hin_Shivam-CorridorX_opt_in.md`.
     - Treat `INTRO_{A}_{B}_opt_in.md` as the authoritative dedup key.
     - If opt-in exists and connector exists → mark as **previously generated**.
     - If opt-in exists and connector missing → eligible for **connector-only** generation.
     - If neither exists → eligible for **full pair** generation (opt-in + connector) when other prerequisites are met.

6. **Separate "new this run" from historical intros**
   - Digest logic:
     - `Intro signals detected (total in scope)` = all valid A→B pairs found in B01/B07 for the date window.
     - `New this run` = pairs where no `INTRO_{A}_{B}_opt_in.md` existed before this run.
     - Put:
       - Newly generated pairs under **"New Drafts Generated"**.
       - Existing pairs only under **"Previously Generated (Skipped)"** with context and file links.

7. **Treat missing upstream blocks as "not ready" not "no intros"**
   - If B26 or manifest.json are missing for a fresh [M] meeting:
     - Count the meeting as *scanned* but not *eligible* for intro generation this run.
     - Record the limitation in the digest summary (e.g., "3 recent [M] meetings missing MG-2 blocks; warm-intro evaluation deferred.").

## Why it works
- Honors the architecture (B07/B02/B08/B26, meeting_type gating) even when some blocks lag behind.
- Avoids regenerating or overwriting existing INTRO_* drafts.
- Produces an honest digest that distinguishes **system state** (what exists now) from **new work done this run**.

## Reuse notes
- Good template whenever a scheduled task must:
  - Re-scan past work,
  - Respect incomplete upstream pipelines,
  - Deduplicate against existing artifacts,
  - And still produce a clear, honest summary of what changed vs what was just confirmed.


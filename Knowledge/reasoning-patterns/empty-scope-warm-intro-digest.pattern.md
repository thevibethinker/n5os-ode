---
created: 2025-12-09
last_edited: 2025-12-09
version: 1.0
---

# Pattern: Empty-Scope Warm-Intro Digest

## Use Case
Scheduled warm-intro generation run where **no eligible meetings** are found (no recent `[M]` meetings with `B07_WARM_INTRO_BIDIRECTIONAL.md` in scope).

## Steps
1. **Run context loaders** (`scheduler`, `writer`) and ensure `SESSION_STATE.md` is initialized.
2. **Execute mechanical scan** for candidate meetings (B07 in last 30 days under `Personal/Meetings/Inbox`).
3. If the candidate list is empty:
   - Do **not** attempt any semantic extraction or email generation.
   - Still create a digest file under `N5/digests/` for the current date.
4. **Digest content rules when empty:**
   - Explicitly report zeros for all key metrics (meetings scanned, intro signals, pairs generated, new this run).
   - Use clear language like "None this run — no warm intro signals detected in the last 30 days."
   - Mark sections like "Previously Generated (Skipped)" as "Not applicable this run" instead of leaving placeholders.
5. **State tracking:**
   - Update `SESSION_STATE.md` Progress to reflect an empty-scope run.
   - Register the digest path in `SESSION_STATE.md` Artifacts as a permanent artifact.

## Guarantees
- System remains **observable** even when no intros are generated.
- No placeholder/stub email content is created.
- Downstream automation relying on daily digest files continues to work.

## When to Reuse
- Any scheduled digest-like workflow where the input set can legitimately be empty (e.g., no meetings, no tasks, no events in scope) but where the **digest artifact itself is still expected** for monitoring and predictability.


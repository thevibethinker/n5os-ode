---
created: 2025-12-08
last_edited: 2025-12-08
version: 1.0
---

# Zero-Scope Scheduled Digest Run

Pattern for scheduled tasks where no entities match the selection criteria, but the system still needs to complete gracefully and leave a clear audit trail.

## Steps

1. Run the full selection scan as specified (e.g., meetings with `[M]` tags and `B07_WARM_INTRO_BIDIRECTIONAL.md` in the last 30 days).
2. If the selection is empty:
   - Still generate the digest/report for the run with explicit zero counts and a short explanation.
   - Verify critical dependencies (e.g., prompt files) and log any missing-but-required components as warnings, not fabricated values.
   - Skip email/content generation and manifest updates (no-op) instead of inventing or reusing stale content.
3. Record the run in `SESSION_STATE.md` progress with the key metrics and the path to the digest.

## When to Use

- Any scheduled workflow where scope is defined by filters (dates, tags, statuses) and the filtered set can legitimately be empty.
- Especially for digest/report generators where "nothing to process" is itself meaningful information.

## Notes for Future Reuse

- Avoid placeholder sections; replace template blocks with explicit statements like "None this run" when appropriate.
- Treat "0 items" as a valid, successful outcome as long as the scan actually ran and dependencies were checked.
- Keep success criteria satisfied: "all items scanned" can still be true when the result count is zero.


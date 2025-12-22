---
created: 2025-12-06
last_edited: 2025-12-06
version: 1.0
---

# Pattern: Zero-Candidate Scheduled Task Run (Still Produce Digest)

## Situation

A backwards-looking warm intro generator scheduled task runs against `Personal/Meetings/Inbox` and finds **no eligible meetings** matching all of the following:

- Folder lives under `Personal/Meetings/Inbox`
- Folder name has the `[M]` suffix
- Folder `mtime` within the last 30 days
- Contains `B07_WARM_INTRO_BIDIRECTIONAL.md`

## Approach

1. **Validate assumptions explicitly**
   - First run the exact eligibility `find` query from the task spec.
   - Then independently scan for any `B07_WARM_INTRO_BIDIRECTIONAL.md` files under `Personal/Meetings/Inbox` (no suffix/mtime filters) to confirm that the zero result is real and not a query bug.

2. **Honor the spec even with zero candidates**
   - Treat "0 meetings" as a legitimate outcome, not as an error.
   - Still create the daily digest at `N5/digests/warm-intro-drafts-{YYYY-MM-DD}.md` with:
     - Meetings scanned = 0
     - Intro signals detected = 0
     - Email pairs generated = 0 × 2 = 0
     - New this run = 0

3. **Document why zero happened**
   - In the digest summary, explain the criteria that led to zero meetings (e.g., no `[M]` + B07 folders in last 30 days).
   - Make it clear that the system ran successfully and the empty result is due to input conditions, not failure.

4. **Maintain state & traceability**
   - Update `SESSION_STATE.md` progress with a one-line summary pointing to the digest path.
   - Do **not** touch manifests or create intro files when there are no candidates.

## When to Reuse

Use this pattern for any scheduled workflow where "no eligible inputs" is common or acceptable. The key is to always:

- Verify that "zero" is real (second check), and
- Still leave behind a clear, dated artifact explaining what happened.


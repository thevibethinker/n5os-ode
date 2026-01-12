---
created: 2026-01-12
last_edited: 2026-01-12
version: 1
provenance: con_i0HQjVHjUOEEMkYW
---
# WORKER ASSIGNMENT: Interview Reviewer - Session Expired Bug

**Assigned to:** Zo (Builder Mode)
**Objective:** Diagnose and fix the "Session Expired" bug where transcripts are lost immediately after form submission.

## Context from Parent

V is testing the Interview Reviewer site. When submitting a transcript with a valid promo code:
1. Form submits successfully
2. Promo code is redeemed (verified - uses decremented)
3. Redirects to `/analyze/{sessionId}` 
4. Analysis page briefly shows, then shows "error occurred"
5. Immediately redirects to "Session Expired" page

## Root Cause Hypothesis

Transcripts are stored in-memory via `storeTranscript()` in a Map. The session data is being lost, likely because:
1. Server auto-restarts when code changes (service manager restarts on file change)
2. Memory store is wiped on restart
3. By the time analysis runs, transcript is gone

## Key Files

- **Main source:** `file 'Sites/interview-reviewer/src/index.tsx'`
- **Transcript storage:** Look for `transcriptStore` or `storeTranscript` function
- **Session DB:** `file 'Sites/interview-reviewer/src/lib/db.ts'`

## Diagnosis Steps

1. Check how `transcriptStore` is implemented (in-memory Map?)
2. Check if server is auto-restarting during the flow
3. Check logs: `tail -f /dev/shm/interview-reviewer.log`
4. Trace the flow from form submission → promo validation → redirect → analyze

## Likely Fix

Move transcript storage from in-memory Map to SQLite database (same as sessions). This ensures transcripts survive server restarts.

Alternative: Disable auto-restart during active sessions, but this is fragile.

## Acceptance Criteria

- [x] User can submit form with promo code
- [x] Analysis runs successfully without "Session Expired"
- [x] Transcript data persists through any server restarts
- [x] Privacy: Transcripts still auto-delete after 30 minutes

## Commands to Test

```bash
# Watch logs
tail -f /dev/shm/interview-reviewer.log

# Check if server restarts
ps aux | grep bun | grep interview

# Test promo code
curl -s "http://localhost:3000/admin/promo/list" -H "X-Admin-Key: my-umbrella-banana-reset-bull-2026"
```

---

**INSTRUCTION FOR WORKER:**

1. Read the transcript storage code in index.tsx
2. Confirm root cause by checking if transcriptStore is in-memory
3. Migrate transcript storage to SQLite in db.ts
4. Add a cleanup job that deletes transcripts older than 30 min
5. Test the full flow with promo code LAUNCH-4VPQ
6. Report back with fix confirmation



# Course Correction: Email Intake → Candidate Intake Processor
**Date:** 2025-10-22 08:20 ET  
**Source Thread:** con_6eNkFTCmluuGFa4a (Email Intake Worker implementation)  
**Status:** ⏳ AWAITING ORCHESTRATOR VALIDATION

---

## Summary

While building the Email Intake Worker spec, we identified a fundamental architecture issue: the worker as originally scoped conflates two distinct responsibilities.

## Recommended Change

### Current (Incorrect)
**Worker:** "Email Intake Worker"  
**Responsibilities:** 
- Poll Gmail API for applications
- Process attachments
- Move files to candidate directories

### Proposed (Correct)
**Worker 1:** "Gmail API Intake" (NEW - to be built separately)  
**Responsibilities:**
- Poll Gmail API for applications
- Download attachments + metadata
- Write to `inbox_drop/` staging area

**Worker 2:** "Candidate Intake Processor" (rename current worker)  
**Responsibilities:**
- Scan `inbox_drop/` for new applications
- Apply quick-check validation
- Move valid candidates to `jobs/<job>/candidates/<id>/`
- Create candidate dossier (`interactions.md`)
- Leave invalid applications in `inbox_drop/` for review

---

## Architecture Flow

```
Gmail API → Gmail API Intake Worker → inbox_drop/ (staging)
                                           ↓
                              Candidate Intake Processor
                                           ↓
                              jobs/<job>/candidates/<id>/
```

---

## Key Decisions

1. **inbox_drop/ location:** `/home/workspace/ZoATS/inbox_drop/` (root level)
2. **inbox_drop/ purpose:** Staging area AFTER email processing, BEFORE candidate directory
3. **File handling:** MOVE only (no copy) - passed quick-check → candidate dir, failed → stays in inbox_drop
4. **Candidate ID:** Slugified name + role code + submission date (e.g., `john-doe-fe001-2025-10-22`)
5. **Multi-file bundles:** Support detection logic (resilient pattern matching)
6. **Job parameter:** Required; default to single job if only one exists; create job structure if missing
7. **Candidate dossier:** `jobs/<job>/candidates/<id>/interactions.md` - chronological record of emails, calls, notes

---

## Roadmap Addition

**Feature:** Candidate Dossier Evolution  
**Description:** `interactions.md` file that grows over time with:
- Email correspondence tracking
- Video call notes and recordings
- Interview feedback
- Status changes and decision points
- Becomes the living "candidate dossier"

**Priority:** Phase 2 (after core pipeline works)

---

## Impact on Current Work

### Files to Create/Update
- [ ] `ZoATS/workers/candidate_intake.md` (rename from email_intake.md)
- [ ] `ZoATS/workers/gmail_intake.md` (new spec - deferred)
- [ ] `ZoATS/WORKERS_PLAN.md` (update with architecture change)
- [ ] `ZoATS/docs/ROADMAP.md` (add candidate dossier feature)

### Implementation Order
1. **Tonight:** Candidate Intake Processor (file-drop based)
2. **Future:** Gmail API Intake Worker (feeds inbox_drop)

---

## Validation Required

**Orchestrator please confirm:**
- Architecture separation is sound
- Naming conventions are clear
- Worker responsibilities are properly scoped
- No breaking changes to existing workers (Parser, Rubric, etc.)

**Once validated, thread con_6eNkFTCmluuGFa4a will proceed with Candidate Intake Processor implementation.**

---

## Notes

This correction improves:
- Separation of concerns (API vs file processing)
- Testability (can test file processor without Gmail)
- Flexibility (can add other intake sources later - web form, Dropbox, etc.)
- Maintainability (clearer boundaries between workers)

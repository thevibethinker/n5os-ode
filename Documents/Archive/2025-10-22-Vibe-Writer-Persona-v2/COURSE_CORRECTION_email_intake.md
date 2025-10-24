# Course Correction: Email Intake Worker → Candidate Intake Processor
**Date:** 2025-10-22  
**From:** con_6eNkFTCmluuGFa4a (Email Intake Worker build thread)  
**Status:** Pending Orchestrator Validation

---

## Issue Identified

The worker originally named "Email Intake Worker" (`email_intake.md`) has a scope mismatch with the actual implementation needed for Night 1.

## Analysis

**Original Plan:**
- Email Intake Worker would process emails directly via Gmail API
- Pull resumes/applications from inbox
- Parse and route to candidate directories

**Reality Check:**
- Gmail API integration is a separate, non-trivial component
- Night 1 needs a working pipeline end-to-end
- File-drop folder is the pragmatic starting point

## Recommended Course Correction

### Rename and Refocus
**OLD:** Email Intake Worker  
**NEW:** Candidate Intake Processor

### Revised Scope
1. **Scan** `inbox_drop/` for new candidate submissions (file-drop fallback)
2. **Bundle detection** - identify multi-file applications (resume + cover letter + metadata)
3. **Validation** - basic checks (has resume, readable format)
4. **Routing** - move to `jobs/<job>/candidates/<id>/` with proper structure
5. **Interaction tracking** - initialize `interactions.md` dossier file

### Architecture Split
```
┌─────────────────────────────────────────────────┐
│ Gmail Integration (FUTURE - separate worker)    │
│ - Email monitoring                              │
│ - Attachment extraction                         │
│ - Writes to inbox_drop/                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Candidate Intake Processor (TONIGHT)            │
│ - Scans inbox_drop/                             │
│ - Validates & bundles files                     │
│ - Creates candidate structure                   │
│ - Initializes interactions.md                   │
│ - Moves to jobs/<job>/candidates/<id>/          │
└─────────────────────────────────────────────────┘
```

## Impacts

### File Changes
- Rename: `email_intake.md` → `candidate_intake.md`
- Create: `workers/intake/` directory with implementation
- Update: `WORKERS_PLAN.md` to reflect scope change
- Add to roadmap: Gmail API Integration worker (future)

### Dependencies
- No impact to downstream workers (parser, scorer, etc.)
- Pipeline orchestrator expects candidates in `jobs/<job>/candidates/` - unchanged
- Actually SIMPLIFIES Night 1 by removing Gmail dependency

### Benefits
1. **Pragmatic** - File drop works tonight, no API complexity
2. **Modular** - Clean separation: email→files vs. files→candidates
3. **Testable** - Easy to simulate with manual file drops
4. **Future-proof** - Gmail worker plugs in later without changes

## Roadmap Addition

**New Worker: Gmail Integration**
- **Purpose:** Monitor Gmail inbox, extract attachments, write to inbox_drop/
- **Priority:** Phase 2 (after working pipeline demonstrated)
- **Complexity:** Medium (OAuth, parsing, rate limits)
- **Dependencies:** None (writes to inbox_drop that Candidate Intake already consumes)

## Decision Required

**Option A: Proceed with Course Correction** ✅ RECOMMENDED
- Rename to Candidate Intake Processor
- Build file-drop scanner tonight
- Add Gmail Integration to Phase 2 roadmap

**Option B: Keep Original Plan**
- Build Gmail API integration tonight
- Risk: May not complete end-to-end pipeline
- Adds complexity to Night 1 critical path

## Next Steps (if approved)

1. Update `email_intake.md` → `candidate_intake.md` with corrected spec
2. Create `workers/intake/main.py` implementation
3. Update `WORKERS_PLAN.md` 
4. Add Gmail Integration to `docs/ROADMAP.md`
5. Proceed with implementation and testing

---

**Awaiting Orchestrator Validation**

Please review and approve in the orchestrator thread (con_ETA8J2uDU6Xyj9bK) before implementation proceeds.

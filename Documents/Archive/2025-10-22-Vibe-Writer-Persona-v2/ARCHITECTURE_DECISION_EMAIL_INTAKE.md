# Architectural Decision: Email Intake Split

**Date:** 2025-10-22 08:16 ET  
**Decision By:** Vibe Builder (con_6eNkFTCmluuGFa4a)  
**Status:** Pending Orchestrator Validation  
**Impact:** Medium - Changes worker boundaries and responsibilities

---

## Context

During the build session for the "Email Intake Worker" (con_6eNkFTCmluuGFa4a), a critical architectural clarification emerged:

**Original Plan:** Single "Email Intake" worker that:
- Connects to Gmail API
- Extracts attachments from emails
- Processes candidates
- Moves them to job directories

**Discovered Issue:** This conflates two distinct concerns:
1. **Email processing** (Gmail API integration, attachment extraction)
2. **Candidate intake processing** (validation, bundling, routing to job directories)

---

## Decision

**Split into two separate components:**

### 1. Gmail Integration Worker (NEW - Future Build)
**Purpose:** Email processing and attachment extraction  
**Responsibilities:**
- Connect to Gmail API
- Monitor inbox for applications
- Extract attachments (resume, cover letter, etc.)
- Write files + metadata to `inbox_drop/`
- Track processed emails to avoid duplicates

**Outputs:** `ZoATS/inbox_drop/{candidate-slug}/` with:
- Raw attachments (resume.pdf, cover_letter.pdf, etc.)
- metadata.json (name, email, source, applied_date)

**Status:** Not yet built - needs separate build session

---

### 2. Candidate Intake Processor (CURRENT BUILD)
**Purpose:** Process staged candidates and route to jobs  
**Responsibilities:**
- Scan `inbox_drop/` for new candidates
- Bundle multi-file submissions
- Run quick validation checks (has resume, metadata valid)
- Move qualified candidates to `jobs/<job>/candidates/<id>/`
- Leave non-qualifying candidates in `inbox_drop/` for manual review
- Create initial `interactions.md` dossier file

**Inputs:** `ZoATS/inbox_drop/`  
**Outputs:** `ZoATS/jobs/<job>/candidates/<id>/`  
**Status:** Active build (con_6eNkFTCmluuGFa4a)

---

## Rationale

**Separation of Concerns:**
- Gmail Worker = I/O boundary (external system integration)
- Intake Processor = Business logic (candidate validation and routing)

**Benefits:**
1. **Testability:** Can test intake processor with file-drop without Gmail dependency
2. **Flexibility:** Supports multiple intake sources (Gmail, web form, manual upload, API)
3. **Modularity:** Gmail integration can be swapped/upgraded independently
4. **Clear boundaries:** Each worker has single, well-defined responsibility
5. **Simpler debugging:** Isolate email issues vs. processing issues

**Night 1 Priority:** File-drop fallback (inbox_drop/) is sufficient for testing and demo. Gmail integration can be added later.

---

## Implementation Plan

### Tonight (con_6eNkFTCmluuGFa4a):
1. ✅ Rename worker: "Email Intake" → "Candidate Intake Processor"
2. ⏳ Update `email_intake.md` → `candidate_intake.md` (or keep filename, update content)
3. ⏳ Build `workers/intake/main.py` focused on file-drop processing
4. ⏳ Document `interactions.md` format for future dossier feature

### Future Session:
1. Create `workers/gmail/main.py` for email processing
2. Design Gmail API integration (authentication, monitoring, deduplication)
3. Define metadata.json schema
4. Implement attachment extraction and staging to inbox_drop/

---

## Alternatives Considered

**1. Keep monolithic Email Intake worker:**
- ❌ Harder to test without Gmail credentials
- ❌ Forces Gmail dependency for all environments
- ❌ Couples unrelated concerns

**2. Build Gmail first, then processor:**
- ❌ Blocks progress on testable components
- ❌ Requires production Gmail setup for development

**3. Selected: Build processor first, Gmail later:**
- ✅ Enables immediate progress with file-drop
- ✅ Clear separation of concerns
- ✅ Supports multiple intake sources from day 1

---

## Validation Required

**Orchestrator must confirm:**
1. Architectural split approved
2. Worker naming/numbering updated in plan
3. Dependencies and sequencing adjusted
4. Pipeline integration points clarified

---

## References

- `file 'ZoATS/WORKERS_PLAN.md'` - Original plan with "Email Intake"
- `file 'ZoATS/workers/email_intake.md'` - Current (empty) spec file
- `file 'ZoATS/workers/pipeline_cli.md'` - Pipeline orchestrator dependencies

---

## Future Roadmap Item

**Candidate Dossier Evolution:**
- Location: `jobs/<job>/candidates/<id>/interactions.md`
- Purpose: Track chronological interactions (emails, calls, notes)
- Growth: Continuously updated throughout candidate lifecycle
- Integration: Email responses, interview notes, video call summaries
- Build Phase: Post-Night 1 (after core pipeline working)

---

**Next Steps:** Awaiting validation from Orchestrator thread before proceeding with Candidate Intake Processor build.

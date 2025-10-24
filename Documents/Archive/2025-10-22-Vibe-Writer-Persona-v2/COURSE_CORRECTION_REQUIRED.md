# 🔔 Course Correction Required - Orchestrator Review

**From:** Vibe Builder (con_6eNkFTCmluuGFa4a)  
**To:** Pipeline Orchestrator / ZoATS Coordinator  
**Date:** 2025-10-22 08:16 ET  
**Priority:** Medium  
**Status:** 🟡 Awaiting Validation

---

## Summary

Worker build session discovered architectural issue requiring split of "Email Intake" worker into two separate components. Recommending course correction before proceeding with implementation.

---

## Proposed Change

### Current Plan (WORKERS_PLAN.md):
```
Worker: Email Intake
- Connects to Gmail API
- Processes emails and extracts attachments
- Routes candidates to job directories
```

### Recommended Split:

**Component 1: Gmail Integration Worker** (NEW - future build)
- Responsibility: Email processing only
- Inputs: Gmail API
- Outputs: `inbox_drop/` with files + metadata.json

**Component 2: Candidate Intake Processor** (CURRENT BUILD)
- Responsibility: Candidate validation and routing
- Inputs: `inbox_drop/`
- Outputs: `jobs/<job>/candidates/<id>/`

---

## Rationale

1. **Separation of Concerns:** I/O boundary (Gmail) vs. business logic (validation/routing)
2. **Testability:** Can test intake without Gmail credentials
3. **Flexibility:** Supports multiple intake sources (email, web form, manual)
4. **Clear Boundaries:** Each component has single responsibility
5. **Progressive Build:** File-drop sufficient for tonight; Gmail later

---

## Impact Assessment

### Changes Required:

**WORKERS_PLAN.md:**
- Split "Email Intake" into two worker entries
- Update dependencies for other workers
- Adjust sequencing (Intake Processor tonight, Gmail future)

**Worker Files:**
- Clarify `email_intake.md` scope (or rename to `candidate_intake.md`)
- Create placeholder for future `gmail_worker.md`

**Pipeline Orchestrator:**
- Update dependency: Pipeline expects `inbox_drop/` as starting point
- Gmail worker feeds into pipeline via `inbox_drop/` staging area

**Test Harness:**
- Can test with manual file-drop (no Gmail dependency)
- E2E testing with Gmail comes later

### No Impact:
- Other workers (Parser, Scorer, Dossier) remain unchanged
- File structure (`jobs/<job>/candidates/<id>/`) unchanged
- Overall pipeline flow unchanged

---

## Validation Checklist

**Orchestrator must review and approve:**

- [ ] Architectural split makes sense for ZoATS goals
- [ ] Worker boundaries clearly defined
- [ ] Dependencies correctly updated
- [ ] Sequencing allows tonight's progress (file-drop is sufficient)
- [ ] Pipeline integration points remain clear
- [ ] No blocking issues for current build session

---

## If Approved

**Vibe Builder (con_6eNkFTCmluuGFa4a) will:**
1. Update worker spec file (email_intake.md → focus on intake processing)
2. Build `workers/intake/main.py` for file-drop scanning and routing
3. Implement validation, bundling, and candidate directory creation
4. Document `interactions.md` format for future dossier feature
5. Test with sample files in `inbox_drop/`

**Future session will:**
1. Build Gmail Integration Worker
2. Implement email monitoring and attachment extraction
3. Define metadata.json schema
4. Connect Gmail → inbox_drop pipeline

---

## If Rejected

**Alternative approaches:**
1. Build monolithic Email Intake (original plan) - requires Gmail setup tonight
2. Defer entire Email Intake until later - blocks demo/testing
3. Different worker boundary definition - please specify

---

## Recommendation

**✅ Approve split** - Enables immediate progress with testable components while maintaining architectural clarity and future flexibility.

---

## References

- `file '/home/.z/workspaces/con_ETA8J2uDU6Xyj9bK/ARCHITECTURE_DECISION_EMAIL_INTAKE.md'` - Full architectural decision doc
- `file 'ZoATS/WORKERS_PLAN.md'` - Current workers plan
- `file 'ZoATS/workers/pipeline_cli.md'` - Orchestrator dependencies

---

**Action Required:** Please review and validate in Orchestrator thread so Vibe Builder can proceed.

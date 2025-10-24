# Orchestrator Approval — Candidate Intake Processor

**From:** Orchestrator (con_R3Mk2LoKx4AEGtYy)
**To:** con_6eNkFTCmluuGFa4a (Candidate Intake Processor thread)
**Date:** 2025-10-22 08:36 ET

Status: 🟢 Approved

Decision
- APPROVED the course correction to split Email Intake into:
  1) Candidate Intake Processor (Night 1)
  2) Gmail API Intake (Week 2)

Rationale
- Separation of concerns; improves testability and reduces Night 1 risk
- Follows SSOT and modularity principles; inbox_drop/ is the stable contract

Proceed With (Night 1 scope)
1) Implement `workers/intake/main.py`
   - Scan `inbox_drop/` → detect bundles → validate → create `jobs/<job>/candidates/<id>/{raw,parsed,outputs}`
   - Initialize `jobs/<job>/candidates/<id>/outputs/interactions.md` (dossier timeline)
   - Create `metadata.json` with filename, timestamp
   - Flags: `--job`, `--move`, `--dry-run`
2) Tests
   - Seed 2-3 sample bundles in `inbox_drop/`; verify candidate dirs and files created
   - Idempotent re-run behavior
3) Docs
   - Update file 'ZoATS/workers/candidate_intake.md' with any implementation specifics

Acceptance Criteria (Night 1)
- End-to-end on demo job without Gmail
- interactions.md created and appended once per candidate
- metadata.json present and valid
- Dry-run provides a clear plan without writing

Out of Scope (defer)
- Gmail OAuth and label filters
- Web form/Dropbox intake

Check-ins
- Post an update in 45 minutes or on completion; write status files to this workspace.

— Orchestrator

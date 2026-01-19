---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_AVUiANpq2GYAc3Qz
type: worker_assignment
worker_id: W1_PROCESS_HARDENING
parent_build: position-system-overhaul
sequence: 1
depends_on: null
---

# Worker 1: Position System Process Hardening

**Objective:** Architect and implement safeguards to prevent the data integrity issues encountered during the position reconciliation and promotion workflows.

---

## Ground Truth Context

We observed:
- `positions.db` inflated from 124 → 168 due to non-idempotent promotion/merge automation.
- Candidate queue (`N5/data/position_candidates.jsonl`) had many statuses set without pointers (`promoted_to`, `matched_position_id`, `merged_into`).
- The system has tools that *exist* (`b32_position_extractor.py promote-reviewed`, etc.) but operational discipline and safety rails were missing.

You MUST use intellectual honesty: do not assume; verify with code + schema inspection.

---

## Deliverables (Architect + Implement)

### D1 — Backup Before Writes
Create `file 'N5/scripts/position_backup.py'`:
- Copies `file 'N5/data/positions.db'` to `file 'N5/backups/positions/'` with timestamp and reason string
- Retain last 10 backups (rotate)
- Usage: `python3 N5/scripts/position_backup.py --before "semantic linking apply"`

### D2 — Position Write Protocol (Dry-run + Apply)
Create `file 'N5/prefs/operations/position-write-protocol.md'`:
- Every script that mutates `positions.db` MUST support `--dry-run` and `--apply`
- Dry-run emits machine-readable JSON list of changes: `{action, table, primary_key, before, after}`
- For bulk ops (>10 rows): generate a HITL review markdown under `N5/review/positions/`

### D3 — Idempotency & Traceability
Implement in write scripts:
- Guard keys:
  - For position inserts: prevent duplicate by canonical `id` and also by stable `insight_hash` (sha256 of normalized insight)
  - For connections: unique key (source_id, target_id, relationship)
- Add missing metadata fields back to candidates when statuses change:
  - `promoted_to`
  - `matched_position_id`
  - `merged_into`
  - `status_changed_at`

### D4 — Fix Promotion Pipeline (Candidates → positions.db)
Audit `file 'N5/scripts/b32_position_extractor.py'` and related tools:
- Identify how approved candidates should be promoted
- Ensure `promote-reviewed` is functional and safe
- Add a “reconciliation / backfill” command that:
  - Finds `approved` candidates that lack `promoted_to`
  - Safely promotes or links them

### D5 — JSON Hygiene
We hit “malformed JSON” when querying `connections` as JSON.
- Add a validator tool `file 'N5/scripts/positions_validate.py'`:
  - Checks every row’s `connections` field parses as JSON array (or empty)
  - Emits a report and optionally repairs trivially broken JSON

### D6 — Checkpointing Standard
Document + provide reusable helper module for checkpointing long operations.

---

## Constraints
- Do NOT delete or mass-edit without a dry-run preview.
- Any schema change is a trap door: propose migration strategy + rollback.

---

## Success Criteria
- Re-running a promotion or linking script is safe (no new duplicates)
- Every mutation path has backup + dry-run + HITL for bulk changes
- Candidate statuses always include target pointers

---

## Update Protocol
- Write updates to `file 'N5/builds/position-system-overhaul/STATUS.md'`
- Keep the parent conversation updated with: Completed / Remaining / Status X/Y.

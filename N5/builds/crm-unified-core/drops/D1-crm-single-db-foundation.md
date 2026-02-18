---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: con_aobUiRmCIj5rHnQf
spawn_mode: manual
---

# Drop D1: CRM Single-DB Foundation

## Objective
Eliminate active runtime dependence on legacy CRM databases and establish enforceable single-database guardrails.

## Deliverables
- Legacy-reference guard script (`N5/scripts/crm_single_db_guard.py`)
- Migration readiness artifact (`N5/builds/crm-unified-core/artifacts/migration-readiness.md`)
- Initial rewrite queue for legacy-reference files

## Acceptance Criteria
- `python3 N5/scripts/crm_single_db_guard.py --check` exits non-zero while legacy references remain.
- `python3 N5/scripts/crm_single_db_guard.py --report` writes a report with DB overlap metrics.
- Build plan and drop artifacts are contract-compliant.

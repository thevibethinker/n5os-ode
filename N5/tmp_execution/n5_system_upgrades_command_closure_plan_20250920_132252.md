# N5 System Upgrades Command — Closure Plan (Resilience + Finalization)

Status: Planned
Owner: Command Authoring / Ops
Last updated: 2025-09-20

---

## Context (from after‑action report)
We implemented a CLI for managing system upgrades (add/edit/list) with strong validation, backups, atomic writes, and duplicate detection. Integration with the command registry is working. A key gap remains: dual‑store synchronization between Markdown and JSONL; plus resilience improvements (backup retention, schema checks, dry‑run, telemetry roll‑ups).

---

## Objectives
- Guarantee lossless, append‑only updates across Markdown and JSONL stores.
- Add dry‑run/verify flows and explicit rollback paths.
- Improve duplicate detection accuracy and transparency.
- Control backup growth; ensure restorability.
- Integrate with the unified `record` interface for discoverability.
- Provide tests, runbook, and acceptance criteria.

---

## Deliverables
1) Dual‑Store Sync Module
- Schema file: `/home/workspace/N5/schemas/system-upgrades.schema.json`
- JSONL store: `/home/workspace/N5/system-upgrades.jsonl` (create if absent)
- Sync library: `N5/scripts/lib/system_upgrades_sync.py` with:
  - write_upgrade(md_path, jsonl_path, item) -> atomic dual write
  - edit_upgrade(id, patch) -> atomic dual edit, preserves history
  - list_upgrades(filters) -> reads from JSONL (source of truth), renders Markdown
  - fs_lock context manager using `.lock` file

2) CLI Enhancements in `N5/scripts/system_upgrades_add.py`
- `--dry-run`: compute changes, write nothing; show diff summary
- `--verify`: re-read post-write, validate schema + parity
- `--rollback <backup>`: restore from selected backup
- Duplicate detection improvements:
  - Normalize titles (casefold, punctuation strip, whitespace collapse)
  - Jaccard over shingles + Levenshtein; surface score + preview
  - Threshold default 0.82; `--dupe-threshold` knob; `--force` to bypass

3) Backup Retention + Recovery
- Backup dir: `/home/workspace/N5/backups/system-upgrades/`
- Policy: keep last 30 backups + 14 days TTL
- Pruner: `N5/scripts/system_upgrades_backup_prune.py` (idempotent)
- Recovery doc: Runbook section in command spec

4) Schema + CI Guardrails
- JSON Schema: `/home/workspace/N5/schemas/system-upgrades.schema.json`
- Local validator: `N5/scripts/system_upgrades_validate_jsonl.py`
- CI hook script (optional): validate JSONL lines + render Markdown

5) Telemetry Roll‑ups
- Daily summary emitter: `N5/scripts/system_upgrades_telemetry_rollup.py`
- Output: `/home/workspace/N5/logs/system-upgrades/summary-YYYY-MM-DD.json`
- Metrics: adds/edits, dupes prevented, backups created, failures

6) Record Dispatcher Integration
- Update mappings: `/home/workspace/N5/knowledge/record_mappings.json`
  - `"upgrade" -> script: system_upgrades_add.py` with args pattern
- Example: `record upgrade --title "X" --category Planned --priority H`

7) Documentation
- Command spec update: `N5/commands/system-upgrades-add.md`:
  - Dry‑run/verify/rollback usage
  - Backup retention + recovery steps
  - Schema description + examples
  - Operational runbook (common failures → remedies)

---

## Step‑By‑Step Work Plan

Phase A — Dual‑Store Foundations
- A1: Define JSON Schema (fields: id, title, description, category [Planned|In Progress|Done], priority [L|M|H], tags[], created_at, updated_at, status)
- A2: Create JSONL file if missing; seed from current Markdown (one‑time distillation)
- A3: Implement sync module with atomic write + `.lock` advisory lock and fsync
- A4: Refactor CLI to call sync module for add/edit/list

Phase B — Safety Controls
- B1: Implement `--dry-run` (show intended JSONL line + Markdown delta)
- B2: Implement `--verify` (post‑write parity + schema revalidation)
- B3: Implement `--rollback` (select backup, restore atomically)

Phase C — Duplicates & Retention
- C1: Add normalization + multi‑metric similarity
- C2: Add `--dupe-threshold` and interactive approval prompt (wizard mode)
- C3: Implement backup pruner; run as part of add/edit after success (best‑effort)

Phase D — Telemetry & Record Integration
- D1: Daily roll‑up script and cron/scheduler entry (optional)
- D2: Update record mappings; smoke test `record upgrade` flow

Phase E — Tests & Docs
- E1: Unit tests: sync functions, duplicate logic, retention
- E2: Integration tests: add→list parity, edit patches, forced dupes, rollback
- E3: Update command spec + runbook; add examples and troubleshooting

---

## Acceptance Criteria
- Dual‑store parity: 100% parity after add/edit/list (JSONL is source of truth)
- Schema compliance: 100% of JSONL lines validate against schema
- Dry‑run/verify: available, accurate, and safe (no side effects)
- Backups: created for all mutating ops; prune policy enforces caps
- Duplicates: configurable threshold; surfaced clearly; forced adds logged
- Record integration: `record upgrade` routes correctly and succeeds
- Telemetry: daily roll‑ups emitted with non‑zero metrics

---

## Rollback Plan
- On failure: auto‑restore last backup; emit error log with context (op, file, exception)
- Manual recovery: use `--rollback <backup>`; re‑run `--verify` after restoration

---

## Execution Hints (to run later)
- Build sequence (idempotent): A → B → C → D → E
- Post‑build validation:
  - `python3 N5/scripts/system_upgrades_validate_jsonl.py /home/workspace/N5/system-upgrades.jsonl`
  - `python3 N5/scripts/system_upgrades_add.py --dry-run --title "Smoke Test" --category Planned --priority M`
  - `python3 N5/scripts/system_upgrades_add.py --verify --title "Smoke Test" --category Planned --priority M`

---

## References
- Spec: `/home/workspace/N5/commands/system-upgrades-add.md`
- Store: `/home/workspace/N5/system-upgrades.jsonl` (to be created)
- Backups: `/home/workspace/N5/backups/system-upgrades/`
- Plan file (this): `/home/workspace/N5/tmp_execution/n5_system_upgrades_command_closure_plan.md`

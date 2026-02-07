---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 5: CRM Migration Script (Phase 2 Implementation)

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W5-CRM-MIGRATION  
**Estimated Time:** 60–90 minutes  
**Dependencies:**
- Worker 4 complete (preflight + skeleton + `.n5protected`).
- `PHASE2_target_architecture.md` (v1.1) and `PHASE3_migration_plan.md` (v1.1) reviewed.

---

## Mission
Implement a deterministic, safe CRM migration script that consolidates all CRM assets under `Personal/Knowledge/CRM/**` and converts `Knowledge/crm/` into a compatibility view with stubs, in line with Phase 3 design.

---

## Context

Currently, CRM information is split between:
- `Personal/Knowledge/Legacy_Inbox/crm/**` (DB + profiles), and
- `Knowledge/crm/individuals/**` (legacy profiles + index).

Phase 2/3 design declares `Personal/Knowledge/CRM/` as the **sole CRM SSOT**. This worker builds a script that:
- Moves/normalizes DBs and indices into `Personal/Knowledge/CRM/db/`.
- Unifies markdown profiles into `Personal/Knowledge/CRM/individuals/` with stable IDs.
- Leaves `Knowledge/crm/individuals/` as a compatibility shell with stubs + index generated from the new SSOT.

---

## Dependencies

- Path config: `N5/prefs/paths/knowledge_paths.yaml` (use the `personal_knowledge.crm` section).
- Protection tooling: `N5/scripts/n5_protect.py` available.
- Preflight script from Worker 4 has created `Personal/Knowledge/CRM/{db,individuals,organizations,events,views}/`.

---

## Deliverables

1. CRM migration script, e.g.: `N5/scripts/knowledge_migrate_crm.py` with:
   - `--dry-run` and `--execute` modes.
   - Integration with `.n5protected` via `n5_protect.py check`.
2. Canonical CRM structure after execution:
   - DB + indices under `Personal/Knowledge/CRM/db/`.
   - Unified profiles under `Personal/Knowledge/CRM/individuals/*.md`.
   - Optional `organizations/`, `events/`, `views/` scaffolding if needed.
3. Compatibility view:
   - `Knowledge/crm/individuals/*.md` as stub files pointing to new paths.
   - `Knowledge/crm/individuals/index.jsonl` regenerated from `Personal/Knowledge/CRM/individuals/`.
4. A short log/report file, e.g. `Records/Personal/knowledge-system/logs/crm_migration_run_<timestamp>.md` summarizing counts and any conflicts.

---

## Requirements

- **Language:** Python 3.12.
- **Safety first:**
  - No destructive operations in `--dry-run` mode.
  - In `--execute` mode, do not delete original files until after successful copy/write and validation.
- **Idempotent:** After a successful run, re-running `--dry-run` should report no remaining moves.
- **.n5protected-aware:**
  - Call `n5_protect.py check <path>` before writing to or deleting from protected roots.
- **Path-config-aware:** All root paths must be resolved via `knowledge_paths.yaml` (no hard-coded `Knowledge/crm/...`).

---

## Implementation Guide

1. **Script Interface**

Suggested CLI:

```bash
python3 N5/scripts/knowledge_migrate_crm.py --dry-run
python3 N5/scripts/knowledge_migrate_crm.py --execute
```

Options:
- `--dry-run`: print planned operations (moves, merges, stub creations) with counts.
- `--execute`: perform operations (after prior dry-run).
- `--limit N` (optional): operate on at most N profiles for testing.

2. **Data Sources**

- Legacy DB + indices:
  - `Personal/Knowledge/Legacy_Inbox/crm/crm.db`
  - Any `*.jsonl` index files in `Legacy_Inbox/crm/`.
- Legacy profiles:
  - `Personal/Knowledge/Legacy_Inbox/crm/individuals/*.md`
  - `Knowledge/crm/individuals/*.md`

3. **Profile Normalization Strategy**

- For each profile, derive a stable `person_id` (e.g. from filename slug or explicit frontmatter).
- Merge duplicates by `person_id`:
  - Prefer newer `last_edited` or `updated_at` frontmatter when available.
  - Merge tags/fields conservatively (union of tags, keep both note sections separated with markers if needed).
- Write canonical profiles to `Personal/Knowledge/CRM/individuals/{person_id}.md`.

4. **Stubs in `Knowledge/crm/individuals/`**

- After canonicalization, replace original `Knowledge/crm/individuals/*.md` with small stub files:

```markdown
---
person_id: <person_id>
canonical_path: Personal/Knowledge/CRM/individuals/<person_id>.md
role: compatibility_stub
---

This CRM profile now lives at `Personal/Knowledge/CRM/individuals/<person_id>.md`.
```

5. **Index Regeneration**

- Generate `Knowledge/crm/individuals/index.jsonl` (or a similar view) by scanning `Personal/Knowledge/CRM/individuals/*.md` and emitting:

```json
{"person_id": "...", "path": "Personal/Knowledge/CRM/individuals/...", "name": "..."}
```

- This index is **not SSOT**; it’s a convenience view.

6. **Logging**

- Log counts and any conflicts to `Records/Personal/knowledge-system/logs/crm_migration_run_<timestamp>.md`:
  - Total legacy profiles.
  - Total canonical profiles written.
  - Number of merges vs direct copies.
  - Any profiles that need manual review.

---

## Testing

1. **Dry-run sanity check**

```bash
cd /home/workspace
python3 N5/scripts/knowledge_migrate_crm.py --dry-run
```

- Confirm printed counts and sample operations look correct.

2. **Limited execution (optional)**

- Run with a limit (if implemented) to migrate a small subset and inspect results.

3. **Full execution**

```bash
cd /home/workspace
python3 N5/scripts/knowledge_migrate_crm.py --execute
```

4. **Post-run validation**

- Verify:
  - `Personal/Knowledge/CRM/db/crm.db` exists.
  - `Personal/Knowledge/CRM/individuals/*.md` contains expected profiles.
  - `Knowledge/crm/individuals/*.md` are stubs.
  - `Knowledge/crm/individuals/index.jsonl` is regenerated and consistent.
- Re-run `--dry-run` and confirm no remaining pending operations.

---

## Report Back

When complete, report to the orchestrator with:

1. Paths to the script and any helper modules created.
2. Summary counts (profiles migrated, merges, stubs created).
3. Confirmation that dry-run is idempotent after execution.
4. Any edge cases or manual follow-ups required.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  


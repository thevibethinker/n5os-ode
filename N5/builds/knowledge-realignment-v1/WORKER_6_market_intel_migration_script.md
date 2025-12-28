---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 6: Intelligence/World/Market Migration Script (Phase 3 Implementation)

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W6-MARKET-INTEL-MIGRATION  
**Estimated Time:** 60–90 minutes  
**Dependencies:**
- Workers 4–5 complete.
- `PHASE2_target_architecture.md` (v1.1) and `PHASE3_migration_plan.md` (v1.1) reviewed.

---

## Mission
Implement a deterministic migration script that consolidates GTM / market intelligence (DB + narratives + registry) into `Personal/Knowledge/Intelligence/World/Market/` and converts any `Knowledge/market_intelligence/` usage into a compatibility view.

---

## Context

Legacy GTM/market intelligence is scattered across:
- `Personal/Knowledge/Legacy_Inbox/market_intelligence/**` (DBs, registries, narratives).
- `Personal/Knowledge/Legacy_Inbox/market/*.md`.
- Potential `Knowledge/market_intelligence/**` expectations in scripts.

Phase 2/3 design defines `Personal/Knowledge/Intelligence/World/Market/` as the canonical home for:
- GTM DB (`db/gtm_intelligence.db`).
- Meeting registry (`meeting_registry.jsonl`).
- Narrative writeups (`narratives/*.md`).

---

## Dependencies

- Path config: use `personal_knowledge.market_intelligence` from `N5/prefs/paths/knowledge_paths.yaml`.
- `N5/scripts/n5_protect.py` available.
- CRM migration (Worker 5) complete so that shared utilities/patterns can be reused.

---

## Deliverables

1. GTM migration script, e.g.: `N5/scripts/knowledge_migrate_market_intel.py` with `--dry-run` and `--execute`.
2. Canonical GTM structure after execution:
   - `Personal/Knowledge/Intelligence/World/Market/db/gtm_intelligence.db`.
   - `Personal/Knowledge/Intelligence/World/Market/meeting_registry.jsonl`.
   - `Personal/Knowledge/Intelligence/World/Market/narratives/*.md`.
3. Compatibility view:
   - Any `Knowledge/market_intelligence/**` locations reduced to stubs pointing into `Intelligence/World/Market/`.
4. Migration report file, e.g. `Records/Personal/knowledge-system/logs/market_intel_migration_run_<timestamp>.md`.

---

## Requirements

- **Language:** Python 3.12.
- **Non-destructive in dry-run:** No filesystem writes or DB changes in `--dry-run` mode.
- **Idempotent:** After a successful `--execute` run, `--dry-run` should show no remaining operations.
- **.n5protected-aware:** Check protected paths before writing/deleting.
- **DB-safe:**
  - Make a backup copy of any DB before moving or modifying.
  - Avoid in-place schema changes unless absolutely necessary (and then document).

---

## Implementation Guide

1. **Script Interface**

```bash
python3 N5/scripts/knowledge_migrate_market_intel.py --dry-run
python3 N5/scripts/knowledge_migrate_market_intel.py --execute
```

2. **DB Relocation**

- Locate `gtm_intelligence.db` (and any siblings) under `Personal/Knowledge/Legacy_Inbox/market_intelligence/`.
- In `--execute` mode:
  - Copy DBs into `Personal/Knowledge/Intelligence/World/Market/db/`.
  - Optionally rename with a more explicit name if design calls for it (document in report).
- Ensure `meeting_registry.jsonl` is moved or copied to `Personal/Knowledge/Intelligence/World/Market/`.

3. **Narratives Normalization**

- Scan for GTM/market narrative-like files in:
  - `Personal/Knowledge/Legacy_Inbox/market/*.md`.
  - Narrative-style files in `Legacy_Inbox/market_intelligence/`.
- For each file:
  - Decide whether it is:
    - Still-current and generalizable → promote to `Intelligence/World/Market/narratives/`.
    - Historical-only → send to `Personal/Knowledge/Archive/MarketIntelligence/`.
  - In ambiguous cases, default to Archive and flag in the migration report.

4. **Compatibility Stubs for `Knowledge/market_intelligence/`**

- If `Knowledge/market_intelligence/**` exists and is used by scripts:
  - Replace content with stub files pointing to the new canonical locations, e.g.:

```markdown
---
role: compatibility_stub
canonical_root: Personal/Knowledge/Intelligence/World/Market
---

This directory has moved. Canonical GTM intelligence now lives under `Personal/Knowledge/Intelligence/World/Market/`.
```

5. **Logging & Reporting**

- Record:
  - DB files moved + backup locations.
  - Number of narratives promoted vs archived.
  - Any files left untouched and why.

---

## Testing

1. **Dry-run:**

```bash
cd /home/workspace
python3 N5/scripts/knowledge_migrate_market_intel.py --dry-run
```

- Inspect planned DB moves and narrative classifications.

2. **Execute:**

```bash
cd /home/workspace
python3 N5/scripts/knowledge_migrate_market_intel.py --execute
```

3. **Validation:**

- Confirm:
  - DB and registry files exist under `Personal/Knowledge/Intelligence/World/Market/`.
  - Narratives exist where expected.
  - Legacy locations no longer contain SSOT content.
- Re-run `--dry-run` and ensure no further operations are required.

---

## Report Back

When complete, report to orchestrator with:

1. Paths to the migration script and any helpers.
2. Counts of DB files, narratives promoted, and narratives archived.
3. Any edge cases or manual follow-ups.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  


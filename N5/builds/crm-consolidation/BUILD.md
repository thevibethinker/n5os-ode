---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_orchestrator
status: planned
provenance: con_1xhFJwHkZOZPZ38m
---

# Build: CRM/Deals Database Consolidation

**Slug:** `crm-consolidation`  
**Objective:** Consolidate three fragmented databases (deals.db, crm_v3.db, Personal/Knowledge/CRM/crm.db) into a single unified n5_core.db, and update all 42+ scripts that reference these databases.  
**Type:** code_build  
**Created:** 2026-01-19  
**Orchestrator Thread:** con_1xhFJwHkZOZPZ38m

---

## Current Status

**Phase:** Planning Complete — Ready for Wave 1  
**Last Update:** 2026-01-19 06:50 ET

All worker briefs created. MECE validation pending.

---

## Wave Progress

| Wave | Workers | Status | Notes |
|------|---------|--------|-------|
| 1 | W1.1, W1.2 | ⚪ Pending | Schema, migration, paths |
| 2 | W2.1, W2.2, W2.3 | ⚪ Pending | Script updates (CRM, Deal, Meeting) |
| 3 | W3.1, W3.2 | ⚪ Pending | Integration & sync scripts |
| 4 | W4.1 | ⚪ Pending | Cleanup & deprecation |

**Legend:** ⚪ Pending | 🟡 In Progress | ✅ Complete | 🔴 Blocked

---

## Worker Status

| Worker | Title | Status | Thread | Notes |
|--------|-------|--------|--------|-------|
| W1.1 | Schema & Migration | ⚪ Pending | — | Creates n5_core.db, migrates data |
| W1.2 | Path Constants | ⚪ Pending | — | Updates lib/paths.py, crm_paths.py |
| W2.1 | CRM Script Updates | ⚪ Pending | Depends: W1.1, W1.2 | crm_cli, crm_lookup, etc. |
| W2.2 | Deal Script Updates | ⚪ Pending | Depends: W1.1, W1.2 | deal_cli, deal_query, etc. |
| W2.3 | Meeting/Stakeholder | ⚪ Pending | Depends: W1.1, W1.2 | meeting_crm_linker, stakeholder_intel |
| W3.1 | Integration Scripts | ⚪ Pending | Depends: W2.1, W2.2 | warm_intro, morning_digest |
| W3.2 | Sync & External | ⚪ Pending | Depends: W2.1, W2.2 | notion_deal_sync, sms_handler |
| W4.1 | Cleanup & Deprecation | ⚪ Pending | Depends: W3.1, W3.2 | Final cleanup |

**Status Key:**
- ⚪ **Pending** — Not started, waiting for dependencies or wave launch
- 🟡 **In Progress** — Worker thread active
- ✅ **Complete** — Worker finished, completion report in `completions/`
- 🔴 **Blocked** — Cannot proceed due to issue

---

## Artifacts

- **Plan:** `file 'N5/builds/crm-consolidation/PLAN.md'`
- **Worker Briefs:** `file 'N5/builds/crm-consolidation/workers/'`
- **Completions:** `file 'N5/builds/crm-consolidation/completions/'` (empty until workers complete)

---

## How to Execute

### For V (launching workers):

1. **Start Wave 1** — Open two new threads, paste briefs:
   - Thread 1: Paste contents of `workers/W1.1-schema-migration.md`
   - Thread 2: Paste contents of `workers/W1.2-path-constants.md`

2. **Workers execute** — Each worker follows their brief, writes to `completions/`

3. **Return here** — Once both W1.1 and W1.2 complete, return to orchestrator

4. **Launch Wave 2** — Same process for W2.1, W2.2, W2.3

5. **Continue** — Repeat for Wave 3, then Wave 4

### Thread Title Format:
`[crm-consolidation] W<wave>.<seq>: <title>`

Example: `[crm-consolidation] W1.1: Schema & Migration`

---

## Notes

- This build supersedes the abandoned `deals-system-repair` build
- Backup all databases before Wave 1 execution
- Keep old DBs as .deprecated.bak for rollback capability

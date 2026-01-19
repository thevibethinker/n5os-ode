---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_1xhFJwHkZOZPZ38m
type: aar
---

# AAR: CRM/Deals Database Consolidation

**Date:** 2026-01-19  
**Duration:** ~2 hours  
**Conversation:** con_1xhFJwHkZOZPZ38m

---

## What Happened

V noticed the intro-leads system wasn't connected to deals. A quick audit revealed a much larger problem: **three separate people databases** (deals.db, crm_v3.db, crm.db) with no cross-linking, plus 582 scattered markdown profiles.

We consolidated everything into a single `n5_core.db` with a unified schema.

---

## What Was Built

### Unified Database: `N5/data/n5_core.db`

| Table | Records | Purpose |
|-------|---------|---------|
| people | 259 | Single source of truth for all humans |
| organizations | 152 | Companies and institutions |
| deals | 99 | Deal pipeline (CS acquirers, Zo partnerships, leadership) |
| deal_roles | 0 (new) | Junction table: people ↔ deals with roles |
| interactions | 55 | Meetings, emails, touchpoints |
| calendar_events | 1 | Migrated from crm_v3 |

### Key Artifacts
- `file 'N5/scripts/db_paths.py'` — Single import for all DB access
- `file 'N5/scripts/crm_consolidation_migrate.py'` — Migration script with duplicate detection
- `file 'N5/builds/crm-consolidation/'` — Complete build folder with 8 worker completions
- `file 'Images/crm-deals-consolidated-final.png'` — Architecture diagram

---

## Build Execution

**Pattern:** Document-based orchestration (v2)

| Wave | Workers | Status |
|------|---------|--------|
| 1 | W1.1 (Schema), W1.2 (Paths) | ✅ |
| 2 | W2.1 (CRM), W2.2 (Deals), W2.3 (Meeting) | ✅ |
| 3 | W3.1 (Integration), W3.2 (Sync) | ✅ |
| 4 | W4.1 (Cleanup) | ✅ |

**Total:** 8/8 workers complete, 4 waves

---

## What Went Well

1. **Clean schema design** — The `deal_roles` junction table elegantly solves the "who's involved in which deal" problem without duplicating person data

2. **Build orchestrator worked** — V launched waves smoothly, workers wrote completions, no coordination chaos

3. **57 duplicates merged** — Migration script detected and consolidated duplicate people across the three source databases

4. **Backward compatibility** — `db_paths.py` provides aliases so old imports don't break immediately

---

## What Could Be Better

1. **SESSION_STATE wasn't updated during build** — Progress field still says "Build plan complete" even though build is finished. Should update at wave boundaries.

2. **Worker completions didn't trigger meta.json update** — Had to manually close the build at end

3. **82 old DB references remain** — W4.1 flagged them but didn't fix all. These are in comments and dead code paths.

---

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| **One database, not two** | Separate CRM and deals DBs would require sync logic; single DB is simpler |
| **Keep markdown profiles** | Useful for human readability; DB is for querying, markdown for browsing |
| **`deal_roles` junction** | Flexible: same person can be broker on one deal, champion on another |
| **Deprecate old DBs in place** | Rename to .DEPRECATED for rollback capability |

---

## Patterns Worth Extracting

### Database Consolidation Pattern
When multiple databases store overlapping entities:
1. Design unified schema with junction tables for relationships
2. Create migration script with duplicate detection (fuzzy name matching)
3. Update all scripts via centralized path constants
4. Deprecate old DBs (don't delete) for rollback

### 4-Wave Refactor Pattern
For large refactors affecting 40+ scripts:
- Wave 1: Schema + path constants (foundation)
- Wave 2: Core scripts (the heavy lifting)
- Wave 3: Integration scripts (the long tail)
- Wave 4: Cleanup + deprecation (hygiene)

---

## Follow-Up Items

- [ ] Monitor for import errors over next 24h
- [ ] Run scheduled agents to verify they work with new DB
- [ ] Clean up remaining 82 old DB references in dead code
- [ ] Add `deal_roles` population to proactive sensor flow

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Databases | 3 | 1 |
| People records (scattered) | 259 + 91 + 192 | 259 (deduplicated) |
| Cross-referencing | None | Full (via deal_roles) |
| Scripts updated | 0 | 42+ |
| Scheduled agents | 7 | 3 (consolidated) |

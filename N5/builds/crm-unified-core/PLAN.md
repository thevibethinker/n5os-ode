---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.1
type: build_plan
status: active
provenance: con_aobUiRmCIj5rHnQf
---

# Plan: CRM Unified Core

**Objective:** Standardize CRM on a single authoritative database (`N5/data/n5_core.db`), enforce high-precision triangulation across email+calendar+person identity, and ship full product-surface integration with automatic enrichment.

**Trigger:** V approved architecture decisions: one permanent DB authority, legacy data transfer, high precision over auto-link volume, and mandatory integration across meeting prep + email copilot + pipeline ops.

**Key Design Principle:** Trust-first migration. No new legacy writes, deterministic migration checks, and auditable state changes at every phase.

---

## Open Questions

- [ ] Should the filename stay `n5_core.db` (platform-level naming) or move to `crm_core.db` behind a compatibility alias after stabilization?
- [ ] Which production deadline should gate hard deletion of legacy DB files (`crm.db`, `crm_v3.db`)?

---

## Checklist

### Phase 1: Freeze Legacy Writes + Migration Readiness
- ☐ Add single-DB guardrail script that fails CI/runtime when active scripts point to `crm_v3.db` or `crm.db`.
- ☐ Build migration diff report (`legacy -> n5_core`) for people/orgs/interactions/events.
- ☐ Enforce read-only mode for legacy DB paths.
- ☐ Test: guardrail detects known offenders and exits non-zero.

### Phase 2: Canonical Schema + Resolver Foundation
- ☐ Finalize canonical field map (`people`, `organizations`, `interactions`, `calendar_events`, `event_attendees`, `relationships`).
- ☐ Implement high-precision resolver pipeline: deterministic exact-match first, scored fuzzy fallback second.
- ☐ Add review queue only for below-threshold candidates.
- ☐ Test: precision >= 95% on validation sample; unresolved links routed to queue.

### Phase 3: Calendar + Gmail Triangulation Wiring
- ☐ Update calendar webhook and Gmail enrichment scripts to write only through canonical service layer.
- ☐ Create `event_attendees` + thread linkage writes with provenance metadata.
- ☐ Add idempotency keys for repeated webhook deliveries.
- ☐ Test: duplicate webhook replay creates no duplicate interactions/attendees.

### Phase 4: Semantic Memory Synchronization
- ☐ Emit structured memory facts on CRM mutations (person-state, relationship-state, recency, intent).
- ☐ Backfill embeddings/index sync for recent high-priority people.
- ☐ Add freshness SLO checks for post-mutation semantic availability.
- ☐ Test: CRM update appears in semantic retrieval inside SLO window.

### Phase 5: Product Surfaces (Mandatory)
- ☐ Ship meeting-prep integration using triangulated person context.
- ☐ Ship email copilot context injection from CRM + semantic memory.
- ☐ Ship pipeline ops views/actions on canonical model.
- ☐ Test: all three surfaces retrieve same person/org state for identical identity input.

### Phase 6: Decommission + Hardening
- ☐ Archive legacy DBs, remove legacy path references from active scripts/docs, and close schema drift.
- ☐ Add smoke + regression suite for create/search/link/enrich flows.
- ☐ Add operational dashboard for queue depth, freshness, and link precision.
- ☐ Test: no active scripts reference legacy DBs; all contract checks pass.

---

## Phase 1: Freeze Legacy Writes + Migration Readiness

### Affected Files
- `N5/scripts/db_paths.py` - UPDATE - centralize legacy enforcement helpers and read-only policy.
- `N5/scripts/crm_paths.py` - UPDATE - mark legacy paths as retired and non-writable.
- `N5/scripts/crm_single_db_guard.py` - CREATE - detect direct legacy DB references.
- `N5/builds/crm-unified-core/artifacts/migration-readiness.md` - CREATE - baseline drift report.

### Changes

**1.1 Single-DB Guardrail:**
- Add deterministic scanner for active scripts/capabilities using legacy DB paths.
- Fail with actionable list of offending files.

**1.2 Migration Readiness Report:**
- Compare entity counts and key overlap metrics (`name`, `email`, `org`) between legacy and canonical DB.
- Record unresolved diffs before any hard migration/deletion action.

**1.3 Legacy Read-Only Policy:**
- Enforce no-write discipline for `crm.db` and `crm_v3.db` pending decommission.

### Unit Tests
- `python3 N5/scripts/crm_single_db_guard.py --check`: exits non-zero when legacy references exist.
- `python3 N5/scripts/crm_single_db_guard.py --report`: produces migration-readiness artifact.

---

## Phase 2: Canonical Schema + Resolver Foundation

### Affected Files
- `N5/scripts/meeting_crm_linker.py` - UPDATE - route matching to canonical resolver.
- `N5/scripts/crm_calendar_webhook_handler.py` - UPDATE - canonical write path.
- `N5/scripts/crm_gmail_enrichment.py` - UPDATE - canonical person lookup and interaction linkage.
- `N5/scripts/crm_triage_queue.py` - CREATE - review queue writes for low-confidence links.

### Changes

**2.1 Resolver Service:**
- Build deterministic + probabilistic person resolution with tunable confidence thresholds.

**2.2 Precision-First Default:**
- Set high confidence auto-link threshold and route uncertain matches to queue.

### Unit Tests
- Resolver precision suite on known entities.
- Threshold routing tests for queue behavior.

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Legacy Reference Guardrail | `workers/W1.1-legacy-reference-guardrail.md` |
| 1 | W1.2 | Migration Readiness Metrics | `workers/W1.2-migration-readiness-metrics.md` |
| 2 | W2.1 | Triangulation Resolver | `workers/W2.1-triangulation-resolver.md` |
| 2 | W2.2 | Calendar+Gmail Canonical Writes | `workers/W2.2-calendar-gmail-canonical-writes.md` |
| 3 | W3.1 | Semantic Memory Sync Layer | `workers/W3.1-semantic-memory-sync-layer.md` |
| 3 | W3.2 | Surface Integration Pack | `workers/W3.2-surface-integration-pack.md` |

---

## Success Criteria

1. `n5_core.db` is the only writable CRM datastore in active runtime paths.
2. Triangulation precision is >=95% with unresolved items routed to review queue.
3. Meeting prep, email copilot, and pipeline ops all consume consistent canonical CRM identity state.
4. Legacy DB references in active scripts and capability docs reduced to zero before close.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Duplicate people caused by weak migration keys | Use deterministic dedupe keys (`email`, normalized full_name+company) and write dry-run diff before execution |
| Webhook replay creates duplicate interactions | Add idempotency keys and unique constraints on source event IDs |
| Semantic memory lag causes stale product context | Add freshness SLO monitor and retry/backfill worker |
| Breaking existing legacy scripts mid-transition | Stage transition with guardrail report + targeted rewrites before deleting DB files |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Keep legacy DB files present but read-only until guardrail report reaches zero offenders.
2. Defer DB filename rename until integration hardening is complete to avoid avoidable breakage.

### Incorporated:
- Both recommendations incorporated as migration sequencing constraints.

### Rejected (with rationale):
- Immediate hard deletion of legacy DB files: rejected for now because active script references are still widespread and would cause avoidable outages.

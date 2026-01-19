---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
type: build_plan
status: draft
provenance: con_odn3gQKnXBzjdLzI
---

# Plan: One-way Deal Sync (External SoT) + Meeting Deal Routing (Zo + Careerspan lenses)

**Objective:** Make external sources (Google Sheet + 2 Notion DBs) the canonical source-of-truth, sync one-way into `file 'N5/data/deals.db'` every 6 hours, and route meetings into Zo/Careerspan deal tracking using an LLM-first classifier (multi-label, overlap supported) with traceability and auto-deal creation.

**Trigger:** V wants a low-lift, high-reliability system to (1) keep local deal state current from external lists and (2) classify + attach meetings to the right deal pipelines (Zo partnerships vs Careerspan), including rare overlaps.

**Key Design Principle:** External SoT is authoritative; Zo never writes back upstream. Local DB is an operational cache + query layer + meeting trace layer.

---

## Open Questions (must resolve before execution)

1. **Google Sheet source-of-truth**
   - ☑ Confirmed stable fileId: `11vD0QaR9x0wqzuNGdhf75rgy3hEbPGkYevJC_kzNyZA`
   - ☑ Confirmed canonical tab name: `Data Partnerships`
   - ☑ Confirmed: sync **all rows** (no filters)

2. **Notion data source IDs + field mapping**
   - ☑ Confirmed: use connected Notion account `vrijen@mycareerspan.com`
   - ☑ Careerspan acquirer targets DB (SoT): https://www.notion.so/careerspan/d72308132faa4ba19b5daa9dd619dc14?v=42d00440f7cd4d4793645506d7da396a&source=copy_link
   - ☑ Leadership DB (SoT): https://www.notion.so/careerspan/18fb06613fae45e6973cffd3a22cc88c?v=2dd668d5e2fb4cedb0a5f5db111f961b&source=copy_link
   - ☑ Confirmed: sync **every row** from both Notion DBs
   - ☑ Confirmed leadership modeling: **(B)** store leadership rows as `deal_type='careerspan_acquirer'` with `category='leadership'`

3. **Routing sweep scope + automation settings**
   - ☑ Meeting router should sweep **all meetings missing router output** (i.e., missing `B36_DEAL_ROUTING.json`) going forward.
   - ☐ Confirm thresholds (defaults remain):
     - Attach meeting → existing deal: `>= 0.70`
     - Auto-create new deal from meeting mention: `>= 0.85`

---

## Nemawashi (Alternatives Considered)

### Option A — Scheduled Sweep (recommended v1)
**How it works:** A scheduled job runs every 6 hours:
1) sync external sources → deals.db
2) sweep recent meetings missing deal-routing output → run LLM router → update deals.db + write meeting artifacts

**Pros:** Lowest lift; no changes to meeting pipeline internals; high reliability; easy rollback.
**Cons:** Not “real-time” (up to 6h latency).

### Option B — Deep Integration into meeting_pipeline generation
**How it works:** Modify the meeting pipeline so the routing block is queued during meeting processing.

**Pros:** Real-time; canonical within pipeline.
**Cons:** Higher surface area / risk; more moving parts.

### Option C — External SoT-only, no local DB
**How it works:** Don’t persist locally; query Notion/Sheet on demand.

**Pros:** Simplest conceptual model.
**Cons:** Breaks meeting traceability + analytics; slower; harder to build sequencing.

**Recommendation:** Option A now; upgrade to B only if latency becomes painful.

---

## Trap Doors / Irreversible Decisions

1. **Deal ID strategy**
   - Trap door: choosing unstable IDs (e.g., Sheet row number) causes churn.
   - Mitigation: use `source_system + source_id` as stable identity; for Sheet, derive `source_id` from normalized company name unless a unique key column is added.

2. **Auto-create without HITL**
   - Trap door: deal spam / polluted pipeline.
   - Mitigation: high confidence threshold + strict trace log + easy "archive" stage.

3. **Overlapping meetings**
   - Trap door: forcing exclusive routing will lose nuance.
   - Mitigation: multi-label lenses (Zo + Careerspan simultaneously), with per-lens confidence.

---

## Checklist

### Phase 1: External SoT → Local Cache Sync (6-hour)
- ☐ Identify Notion data source IDs for Acquirer Targets + Leadership and confirm field mapping.
- ☐ Implement a deterministic **one-way sync runner** (Bun/TS) that:
  - downloads/parses the Zo partnerships sheet tab `Data Partnerships`
  - queries Notion DBs for all rows
  - upserts deals into `file 'N5/data/deals.db'`
  - records provenance per row (source_system, source_id, imported_at)
- ☐ Add a lightweight sync audit trail (either a new table `sync_runs` or append-only JSONL log).
- ☐ Test: run sync locally twice; confirm idempotency (row count stable, updates applied, no duplicates).

### Phase 2: Meeting Deal Routing (LLM-first, overlap supported)
- ☐ Define a new meeting artifact output (non-invasive): `B36_DEAL_ROUTING.md` + `B36_DEAL_ROUTING.json` (structured).
- ☐ Implement `deal_router.ts` (Bun) that:
  - reads meeting transcript/recap markdown
  - calls `/zo/ask` with a *strict JSON output contract*:
    - lenses: {zo: 0..1, careerspan: 0..1}
    - companies mentioned + match to existing deals
    - recommended deal links
    - create_new_deals[] with confidence + rationale
  - writes outputs into the meeting folder
  - upserts links + activities into deals.db
- ☐ Add traceability:
  - log an activity row per link: `activity_type='meeting_linked'` with `metadata_json` containing meeting_id + lens scores
  - if auto-created: `activity_type='auto_created_from_meeting'` with meeting_id
- ☐ Test: point the router at 3 known meetings; verify outputs stable + deals updated.

### Phase 3: Scheduling + Operational Views
- ☐ Create a scheduled agent (every 6 hours) that runs:
  1) external sync
  2) meeting sweep + routing for recent meetings
- ☐ Add queryable views:
  - Zo partnerships: by stage/temperature
  - Careerspan acquirers: by proximity/temperature
  - Auto-created deals: last 30 days, with originating meeting
- ☐ Test: one full scheduled run (dry-run mode first), then live.

---

## Phase 1: External SoT → Local Cache Sync (6-hour)

### Affected Files
- `N5/data/deals.db` - UPDATE (schema additions as needed: stable IDs, optional sync_runs)
- `N5/scripts/deal_sync_external.ts` - CREATE (Bun script orchestrating parse + upsert)
- `N5/scripts/deal_sources.ts` - CREATE (source adapters: Google Sheet tab, Notion DB)
- `N5/scripts/deal_db.ts` - CREATE (DB upsert helpers + idempotency)
- `N5/builds/deal-sync-router/STATUS.md` - UPDATE (execution tracking)

### Changes

**1.1 Stable identity + upsert rules**
- Add/standardize fields in deals.db:
  - `source_system` (e.g., `zo_sheet`, `careerspan_acquirers_notion`, `careerspan_leadership_notion`, `auto_meeting`)
  - `source_id` (stable upstream identifier: Notion page ID; Sheet normalized company key)
  - Unique constraint on `(source_system, source_id)` to prevent dupes.

**1.2 External adapters**
- Google Sheet ingestion:
  - Use Zo tools to download xlsx into a temp path
  - Parse tab `Data Partnerships` deterministically
- Notion ingestion:
  - Use Zo Notion tool to query DB content
  - Map required fields into deals schema

**1.3 No write-back guarantee**
- Explicitly enforce “write disabled” to external APIs (no Notion update, no Sheet update).

### Unit Tests
- Sync idempotency: run twice; verify `(source_system, source_id)` unique; deal count stable.
- Update propagation: change 1 row upstream; rerun sync; verify 1 record updated locally.

---

## Phase 2: Meeting Deal Routing (LLM-first)

### Affected Files
- `N5/scripts/deal_router.ts` - CREATE
- `N5/scripts/deal_meeting_sweep.ts` - CREATE (find meetings needing routing)
- `N5/data/deals.db` - UPDATE (add `deal_meetings` link table OR store links via deal_activities)
- Meeting folders under `Personal/Meetings/**/` - CREATE `B36_DEAL_ROUTING.md` and `B36_DEAL_ROUTING.json`

### Changes

**2.1 Dual-lens classifier (overlap supported)**
- The router prompts the LLM to score both lenses independently:
  - `zo_relevance_score`
  - `careerspan_relevance_score`
- A meeting may link to both pipelines.

**2.2 Deal matching + creation**
- Extract company mentions.
- Match to existing deals via exact company name OR alias list (aliases stored in `metadata_json`).
- If not found and confidence >= threshold, create a new deal:
  - `source_system='auto_meeting'`
  - `source_id='<meeting_id>:<company_key>'`
  - log `auto_created_from_meeting` activity (traceability).

**2.3 Traceability block**
- Write `B36_DEAL_ROUTING.md` summarizing:
  - lens scores
  - matched deals
  - auto-created deals + why
  - recommended next action
- Write `B36_DEAL_ROUTING.json` with the structured payload used to update deals.db.

### Unit Tests
- Router determinism test: run twice on same meeting; JSON keys stable; minimal drift.
- Auto-create test: feed a meeting mentioning a new company; confirm deal created and trace activity present.

---

## Phase 3: Scheduling + Views

### Affected Files
- `N5/scripts/deal_cron_runner.ts` - CREATE (runs sync + meeting sweep)
- Scheduled agent (Zo) - CREATE (RRULE every 6 hours)

### Changes
- Scheduled agent runs `bun N5/scripts/deal_cron_runner.ts`.
- Add CLI/readme snippets (optional) for quick manual runs.

### Unit Tests
- Dry-run mode: runner prints intended changes without mutating DB.
- Live run: DB updated, and at least one meeting gets routing artifacts.

---

## Success Criteria

1. Every 6 hours, deals.db reflects latest state from:
   - Zo Data Partnerships sheet
   - Careerspan acquirer targets Notion DB
   - Leadership Notion DB
   (no duplicates; stable IDs; idempotent)
2. For meetings in the last 14 days, the system generates `B36_DEAL_ROUTING.*` and links meetings to deals with dual-lens scoring.
3. Auto-created deals have full traceability: deal record includes source_system/source_id; DB includes an activity referencing originating meeting.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM drift causes inconsistent routing | Use strict JSON contract + low-temperature + “must output valid JSON” guardrails; store raw model output for audit. |
| Auto-created deal spam | High threshold + auto-create only if explicit company + actionable context; easy archive stage. |
| Notion schema changes | Fetch schema each run; fail fast and log a clear error. |
| Meeting overlap misclassified | Multi-label lens scoring; allow both; don’t force exclusivity. |

---

## Level Upper Review (pending)
- To invoke after Open Questions are resolved and before execution begins.

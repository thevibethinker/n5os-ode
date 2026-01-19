---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
type: build_plan
status: draft
---

# Plan: Notion ↔ Deals Sync via Pipedream

**Objective:** Ingest Notion “Deal Brokers” + “Leadership Targets” into `N5/data/deals.db` using Notion page_id as the canonical key, then push Zo-enriched fields (LinkedIn, Email, IntroPath, Last touch, Next action, Owner) back to Notion via Pipedream.

**Trigger:** Notion OAuth in Zo is unreliable; Pipedream is authorized inside Notion and must be used as the integration layer.

**Key Design Principle:** Simple > easy. Avoid schema changes; store extra fields in `metadata_json` unless/until we prove a column is required.

---

## Open Questions

- [ ] What are the two Pipedream workflow endpoint URLs?
  - Inbound (Notion → Zo) for Deal Brokers
  - Inbound (Notion → Zo) for Leadership Targets
  - Outbound (Zo → Pipedream → Notion) for “update page properties”
- [ ] What shared secret (token/header) should Pipedream send so Zo can authenticate inbound webhooks?

---

## Nemawashi (Alternatives Considered)

1. **Direct Notion API from Zo (preferred in theory)**
   - Pros: fewer moving parts, lower latency
   - Cons: currently blocked by OAuth/tooling instability in Zo; brittle right now

2. **Zo Browser scrape/export of Notion tables**
   - Pros: no API auth
   - Cons: requires interactive login and is fragile; hard to do bidirectional updates; high maintenance

3. **Pipedream as the Notion bridge (recommended)**
   - Pros: already authorized in Notion; supports read/write; reliable triggers; easy mapping
   - Cons: adds one extra hop; requires workflow management in Pipedream

**Recommendation:** (3) Pipedream bridge + Zo-owned local DB as system of record for tracking/enrichment.

---

## Checklist

### Phase 1: Inbound Ingestion (Notion → Zo)
- ☐ Add Pipedream-specific webhook endpoints to existing webhook receiver service
- ☐ Persist inbound payloads to JSONL cache under `N5/cache/deal_sync/`
- ☐ Create ingestion script to upsert records into `deals.db` using `page_id` as `source_id`
- ☐ Test: Send 1 sample webhook for each database and confirm rows upsert into `deals.db`

### Phase 2: Outbound Enrichment Push (Zo → Notion via Pipedream)
- ☐ Define enrichment mapping (DB → Notion props) for: LinkedIn, Email, IntroPath, Last touch, Next action, Owner
- ☐ Create script to generate updates and call Pipedream “update page” workflow
- ☐ Add idempotency + rate limiting safeguards
- ☐ Test: Update 1 record in `deals.db`, run push, confirm Notion page updated

### Phase 3: Operationalization
- ☐ Add a scheduled agent (or extend existing deal sync agent) to run ingestion + enrichment push on cadence
- ☐ Add drift checks + a small audit log
- ☐ Test: End-to-end run produces deterministic results; re-running causes no duplication

---

## Phase 1: Inbound Ingestion (Notion → Zo)

### Affected Files
- `webhook-receiver/server.js` - UPDATE - add two new endpoints for Pipedream Notion ingestion + authenticated writes to cache
- `N5/scripts/deal_sync_external.py` - UPDATE - add two new sources: `deal_brokers` and `leadership_targets` (from cache JSONL)
- `N5/cache/deal_sync/deal_brokers.jsonl` - CREATE (runtime artifact) - append-only cache
- `N5/cache/deal_sync/leadership_targets.jsonl` - CREATE (runtime artifact) - append-only cache
- `N5/builds/notion-deals-sync/STATUS.md` - UPDATE - track execution progress

### Changes

**1.1 Add webhook endpoints (Pipedream → Zo):**
- Add:
  - `POST /webhook/pipedream/notion/deal-brokers`
  - `POST /webhook/pipedream/notion/leadership-targets`
- Require a shared secret (e.g. `x-n5-token`) and reject unauthorized requests.
- Normalize payload shape before writing to JSONL cache.

**1.2 Define normalized payload contract (minimal):**
For each Notion row/page:
- `page_id` (canonical)
- `type` (`deal_broker` | `leadership_target`)
- `person_name` (leadership only)
- `company`
- `linkedin`
- `email`
- `intro_path`
- `owner`
- `last_touch` (ISO date or null)
- `next_action`
- `updated_at` (ISO)
- `raw` (optional: full Notion properties blob)

**1.3 Upsert into `deals.db` (people-first model):**
- Store as new deal types:
  - `careerspan_deal_broker`
  - `careerspan_leadership_target`
- Map to existing columns:
  - `company` ← company
  - `primary_contact` ← person_name (leadership), or broker name (brokers)
  - `owner` ← owner
  - `last_touched` ← last_touch
  - `next_action` ← next_action
  - `source_system` ← `notion_pipedream`
  - `source_id` ← page_id
  - `metadata_json` ← { linkedin, email, intro_path, raw_props?, notion_url? }

### Unit Tests
- POST a sample payload to each endpoint (curl) with correct token ⇒ expect 200 and cache file appended.
- Run ingestion for each cache ⇒ expect:
  - row exists with `source_id = page_id`
  - rerun is idempotent (no duplicates)

---

## Phase 2: Outbound Enrichment Push (Zo → Notion via Pipedream)

### Affected Files
- `N5/scripts/notion_enrich_push.py` - CREATE - reads `deals.db`, calls Pipedream update workflow for changed records
- `N5/scripts/deal_cli.py` - OPTIONAL UPDATE - add `push-enrichment` command alias to run `notion_enrich_push.py`
- `N5/builds/notion-deals-sync/STATUS.md` - UPDATE

### Changes

**2.1 Choose enrichment “source of truth”:**
- Notion is user-facing workspace for manual edits.
- Zo `deals.db` is the tracking/enrichment engine.
- Conflict policy:
  - If Notion changes a field, ingestion overwrites DB.
  - If DB changes enrichment fields, push overwrites Notion.
  - Fields designated “Zo-owned”: LinkedIn, Email, IntroPath, Last touch, Next action, Owner.

**2.2 Push workflow contract:**
- Zo calls Pipedream endpoint with:
  - `page_id`
  - `properties`: { LinkedIn, Email, IntroPath, Last touch, Next action, Owner }
  - `idempotency_key`

**2.3 Safety controls:**
- Batch size cap (e.g. 25 pages/run)
- Dry-run mode prints intended updates
- Backoff on 429/5xx

### Unit Tests
- Update one DB record’s `next_action` + `owner` ⇒ run push ⇒ confirm Notion updated.
- Run push again with no changes ⇒ expect 0 updates.

---

## Phase 3: Operationalization

### Affected Files
- `N5/scripts/deal_sync_external.py` - UPDATE - incorporate new sources into `--source all`
- Scheduled agent (new) - CREATE - cadence-based ingestion + push
- `N5/logs/deal_sync_*.log` - UPDATE (runtime) - include pipedream/notion sync stats

### Changes

**3.1 Schedule cadence:**
- Ingest: every 15 minutes (or hourly) depending on volume
- Push: every 1–6 hours depending on enrichment freshness needs

**3.2 Observability:**
- Log counts: received webhooks, upserts, pushes, failures
- Keep last-seen timestamp per page_id in `metadata_json`

### Unit Tests
- End-to-end: Pipedream trigger ⇒ webhook received ⇒ DB updated ⇒ push updates Notion.

---

## Success Criteria

1. A new row added/edited in Notion appears in `deals.db` within one ingestion cycle, keyed by Notion `page_id`.
2. Updating any of: LinkedIn, Email, IntroPath, Last touch, Next action, Owner in `deals.db` results in corresponding Notion property updates via Pipedream.
3. System is idempotent: reruns do not create duplicate deals, and re-push does not spam updates.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Webhook spoofing / unwanted writes | Require shared secret header + reject unauth requests; optionally IP allowlist if Pipedream supports it |
| Data drift / overwrites | Explicit “Zo-owned fields”; ingestion only overwrites non-Zo-owned fields (future) |
| Rate limits / workflow errors | Batch + backoff + dry-run + per-run cap |
| Schema lock-in | Store enrichment fields in `metadata_json` first; only promote to columns after proven necessary |

---

## Trap Doors (Irreversible Decisions)

- **Schema change in `deals.db`:** avoid unless necessary; once deployed, migrations are painful.
- **Overwriting Notion user-entered data:** must restrict to explicitly “Zo-owned” fields.
- **Public endpoints without auth:** must not ship without token gate.

---

## Level Upper Review (Optional)

Not invoked yet. Trigger if we decide to introduce schema changes, multi-source conflict resolution beyond “Zo-owned fields”, or automated creation of many Notion pages.


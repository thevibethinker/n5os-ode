---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_uwKEY1WCAKJqRzCe
---

# Worker 3 Plan — Notion Bidirectional Sync

## Open Questions (answer before live sync)

1. **Auth path:** Do we want the sync to use Zo’s connected Notion integration (LLM tool) or a **direct Notion API token** (e.g., `NOTION_TOKEN`) usable by Python scripts?
2. **Canonical Notion IDs:** Are the database IDs in `WORKER-3-notion-sync.md` definitive for:
   - Acquirer Targets
   - Deal Brokers
   - Leadership Targets
3. **Notion page linking:** For deals/contacts, which local fields are canonical for mapping → Notion page?
   - Deals table: `external_source='notion'` + `external_id=<page_id>`?
   - deal_contacts table: `source_system='notion'` + `source_id=<page_id>`?

## Nemawashi — Alternatives

### A) Direct Notion API from Python (recommended for autonomy)
- **How:** Python calls Notion REST API using a token in env (`NOTION_TOKEN`).
- **Pros:** Deterministic + schedulable with no LLM/tool dependency; simplest long-term.
- **Cons:** Requires managing/storing token; must handle rate limits + pagination.

### B) Zo-tool-driven Notion I/O + Python for transforms (recommended if we can’t store token)
- **How:** A scheduled Zo agent pulls Notion DBs via Notion tool, writes JSON cache, runs Python to update `deals.db`, then uses Notion tool to apply push actions.
- **Pros:** Leverages existing integration; no token management.
- **Cons:** More moving parts; harder to reproduce locally; tool invocation constraints.

### C) Manual export/import (CSV/JSON) + local sync
- **How:** Periodic export from Notion; Python updates local; pushes are manual.
- **Pros:** Minimal auth complexity.
- **Cons:** Not actually “bidirectional”; brittle and slow.

**Decision:** Implement **A** as primary path (Python + `NOTION_TOKEN`) with **dry-run** mode that works even when auth is missing. If we later confirm stable tool invocation, we can add B as an optional runner.

## Trap Doors (call out explicitly)

1. **DB schema changes in `N5/data/deals.db`** (hard to reverse once other scripts depend on them).
   - Mitigation: Add only minimal new tables (`notion_sync_state`, `notion_outbox`) with clear naming.
2. **Notion property name coupling** (renames in Notion break sync silently).
   - Mitigation: Centralize mapping in `N5/config/notion_field_mapping.json` and validate schemas at runtime.
3. **Rich text overwrites vs append** (data-loss risk).
   - Mitigation: Intelligence Summary updates must be prepend/append-only; never replace historical content.

## Phases (2–3 max)

### Phase 1 — Config + Local Sync State

**Affected Files**
- `N5/config/notion_field_mapping.json` (new)
- `N5/scripts/notion_deal_sync.py` (new)
- `N5/data/deals.db` (schema migration: add minimal sync tables)

**Changes**
- Add mapping config exactly once and treat it as the single source of truth.
- Add SQLite tables:
  - `notion_sync_state` (stores last pull timestamp per Notion DB)
  - `notion_outbox` (queue of pending pushes: stage/next_action/intel append)
- Implement `notion_deal_sync.py` CLI:
  - `pull` (Notion → Local) supports `--dry-run`
  - `enqueue-intel` (Local queue for Intelligence Summary append)
  - `compute-push` (Local → Notion action list / outbox)
  - `push` (executes queued outbox items; requires `NOTION_TOKEN` unless we later add tool-runner)

**Unit Tests**
- Add tests for:
  - property extraction (title/select/date/rich_text)
  - conflict resolution rules
  - outbox generation is stable + idempotent

### Phase 2 — Scheduled Sync Agent Update

**Affected Files**
- Scheduled agent: “Deal Sync & Meeting Routing”

**Changes**
- Extend agent instruction:
  1) `pull` Notion → Local (dry-run default until token set)
  2) run deal meeting routing (existing)
  3) `push` outbox Local → Notion

**Unit Tests / Validation**
- Manual dry-run:
  - `python3 N5/scripts/notion_deal_sync.py pull --dry-run`
  - `python3 N5/scripts/notion_deal_sync.py compute-push --dry-run`

## Success Criteria

- Dry-run executes end-to-end with **no writes** (prints intended DB + Notion actions).
- Live pull updates local deals/contacts from Notion and is idempotent.
- Intelligence Summary appends (or prepends) without losing existing content.
- Bidirectional fields resolve correctly per mapping + timestamps.
- Sync finishes in <30s for typical dataset sizes.

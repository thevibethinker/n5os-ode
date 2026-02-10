---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
type: build_plan
status: draft
provenance: con_TS42RN2pwOnBA4Kq
---

# Plan: Unified Knowledge Graph & Semantic Memory System

**Objective:** Merge the entity/relationship graph, meeting edge system, and ingestion/backfill workflows into a single, resilient knowledge graph that auto-ingests meeting intelligence while enabling semantic queries with minimal manual review.

**Trigger:** The graph backfill crashed due to a rate-limit spike, duplicative data lives in `brain.db` and `edges.db`, and V wants one unified system plus safe autop-commit and ingestion.

**Key Design Principle:** Plans are for AI execution — every change must be actionable, avoid complexity, and respect MECE worker separation so the Builder can proceed without re-asking questions.

---

## Open Questions

- [ ] What should the canonical schema look like once we merge entity/relationship data from `brain.db` and `edges.db`? (Do we prefer `entities + relationships` tables with edge metadata, or keep `edges` table specialized?)
- [ ] How do we handle review/autocommit policies once meeting edges go straight into the unified store (what quality checks remain manual vs automated)?

---

## Checklist

### Phase 1: Restore Resiliency
- ☐ Improve `entity_extractor.py` error handling so rate limits fall back to `/zo/ask` instead of crashing on truncated JSON
- ☐ Add exponential backoff/retry to continuous backfill and move progress tracking off the growing JSON list (e.g., `processed_ids` table)
- ☐ Confirm a scheduled agent (or long-running service) is  running the backfill so the control file’s "active" state matches reality
- ☐ Test: Simulate a rate-limit response and confirm the extractor falls back to `/zo/ask`, the queue survives, and progress resumes

### Phase 2: Unified Schema & Ingestion
- ☐ Define the merged schema (`entities`, `relationships`, `edges`, `meetings`) to capture both topic-level knowledge and meeting provenance
- ☐ Update `GraphStore` to read/write the unified schema and provide canonical helper methods (`ensure_entity`, `link_relationship`, `record_edge`) used by both backfill + meeting ingestion
- ☐ Implement a migration/refactor that copies `edges.db` content into the unified store and keeps it synchronized
- ☐ Test: Insert representative entities/edges from both brain.db extractions and meeting edges, query across sources, ensure no duplicates

### Phase 3: Autonomous Meeting Edge Ingestion
- ☐ Review/auto-commit the 5,442 pending `N5/review/edges/pending` records, flagging or dropping only the ones with missing evidence
- ☐ Wire the meeting edge extraction pipeline (B33) to write directly to the unified store with auto-commit plus a lightweight review flag for traceability
- ☐ Schedule/trigger the new ingestion pipeline (via agent or service) so meeting processing and backfill share the same scheduler
- ☐ Test: Run meeting ingestion on two recent meetings, ensure new edges appear in the unified graph, autop-commit logic works, and queries reflect meeting provenance

---

## Phase 1: Restore Resiliency

### Affected Files
- `N5/cognition/entity_extractor.py` - UPDATE - add explicit rate-limit detection, structured error handling, and fallback logic to `/zo/ask`
- `N5/scripts/graph_backfill_continuous.py` - UPDATE - add exponential backoff, durable checkpointing, and referencing normalized progress table
- `N5/cognition/backfill_progress.json` - REPLACE - migrate to persistent SQLite table (e.g., `processed_ids`, `progress_meta`)
- `N5/config/backfill_control.json` - UPDATE - ensure control state matches actual agent, add `last_attempted` and `error_count`
- `N5/scripts/edge_backfill.py` or new helper - UPDATE - use shared GraphStore helpers for progress tracking during dry runs

### Changes

**1.1 Rate-limit handling:**
- Detect HTTP 429s / `rate_limit` in error text inside `extract_entities_via_openai`.
- When rate-limited, return `None` so `extract_entities()` falls back to `/zo/ask` (which already has structured validation).
- Log the raw response when JSON parsing fails so we can diagnose truncated payloads.

**1.2 Resilient Backfill Loop:**
- Introduce an SQLite table (e.g., `backfill_progress`) that stores processed block IDs, last batch timestamp, error count, and last error message. Replace JSON rewriting with incremental inserts.
- Update `graph_backfill_continuous.py` to batch updates: process 100 blocks, commit `processed_ids` via `INSERT OR IGNORE`, flush after each successful batch.
- Add exponential backoff (start 1s, double with ceiling 30s) when the `entity_extractor` raises or returns empty results due to rate limits.
- Persist `last_run_at` and `last_error` in `backfill_control.json` so the agent UI reflects reality.

**1.3 Scheduled watchdog:**
- Verify a scheduled agent runs the continuous script (if missing, create one with instructions to run `graph_backfill_continuous.py`).
- Ensure control state transitions: `active` while running, `paused` when rate-limited for >1h, `complete` when `processed_ids` covers all blocks.

### Unit Tests
- Run `graph_backfill_continuous.py` against a small subset with mocked 429 responses → confirm fallback to `/zo/ask` and resumption.
- Insert ~50 block IDs into `backfill_progress` table and ensure duplicates are skipped on re-run.
- Ensure `backfill_control.json` fields update after success, rate-limit, and completion.

---

## Phase 2: Unified Schema & Ingestion

### Affected Files
- `N5/cognition/graph_store.py` - UPDATE - expand to handle meeting edge metadata, status, and provenance fields
- `N5/data/` (new database) - CREATE - unified `knowledge_graph.db` containing `entities`, `relationships`, `edges`, `meetings`
- `N5/scripts/migrate_positions_to_brain.py` (or new migration) - UPDATE - copy `edges.db` and `brain.db` content into the unified store
- `N5/scripts/edge_writer.py` (new or updated) - CREATE - standardized API for inserting meeting edges into unified graph
- `N5/scripts/edge_query.py` - UPDATE - target unified store for queries across entity types
- `N5/scripts/edge_reviewer.py` - UPDATE - adapt to new storage and autop-commit logic

### Changes

**2.1 Schema Definition:**
- Define `entities(id TEXT PRIMARY KEY, name TEXT, type TEXT, canonical_name TEXT, metadata JSON, created_at TEXT)`.
- Define `relationships(id TEXT PRIMARY KEY, from_entity TEXT, to_entity TEXT, relation_type TEXT, evidence TEXT, context_meeting_id TEXT, status TEXT DEFAULT 'active', extracted_at TEXT, metadata JSON)`.
- Keep `meetings(id TEXT PRIMARY KEY, title TEXT, date TEXT, source_path TEXT)` to link provenance.
- Add indexes on entity names, relation types, and meeting IDs to support query performance.

**2.2 Unified GraphStore:**
- Add helper methods `ensure_entity(entity_type, slug, name, metadata)`, `link_relationship(source_slug, relation_slug, target_slug, meeting_id, evidence, status='active')` and `query_edges(...)`.
- Make both `graph_backfill` and `edge_reviewer` import the same GraphStore to avoid duplication.
- Provide `upsert_meeting()` helper so meeting ingestion can register meeting metadata once.

**2.3 Migration:**
- Write a script to copy all `brain.db` entities/relationships plus `edges.db` meeting edges into the unified store, tagging edges with `context_meeting_id`.
- After migrating, adjust the backfill script to read/write from the new DB instead of `brain.db` for entities/relationships.
- Keep `edges.db` as a readonly log until we fully switch the resolver (one more build), but ensure data stays in sync with the new store for now.

### Unit Tests
- Insert sample data from both sources into the unified schema and query for a mix of entity/meeting-edge combos.
- Verify canonical slug generation prevents duplicates (`idea:context-graph` vs `Context Graph`).
- Run the migration script and confirm counts match (brain relationships + committed edges = new store relationships).

---

## Phase 3: Autonomous Meeting Edge Ingestion

### Affected Files
- `N5/scripts/edge_extractor.py` - UPDATE - write directly to unified graph and drop or mark reviewed meeting edges
- `N5/scripts/edge_writer.py` - CREATE - CLI/batch helper used by extraction/backfill to insert edges with evidence/status
- `N5/scripts/edge_reviewer.py` - UPDATE - include autop-commit flag, quality thresholds, and fallback logging for blacklisted edges
- `N5/review/edges/pending/` - CLEANUP - process existing JSONL files into the unified store, archiving successes
- `N5/agents/` (new scheduled agent) - CREATE - ensure meeting edge ingestion runs after meeting capture

### Changes

**3.1 Review queue cleanup:**
- Iterate through all pending JSONL  files (5,442 edges), validate evidence and required fields, and insert them into the unified store via `edge_writer`.
- Mark each file processed by moving to `N5/review/edges/archived/<timestamp>_batch.jsonl` so the queue stays empty before autop ingestion.
- Keep a log of edges that failed validation for manual review (samples with missing evidence become flagged edges).

**3.2 Auto ingestion:**
- Update B33 extractor to generate an `edges` list and call `edge_writer.bulk_insert(edges)` rather than writing to JSONL.
- For each ingestion run, capture `meeting_id`, `meeting_title`, `meeting_date`, and store them alongside edges in the unified store.
- Add an `edge_reviewed_at` timestamp to the schema so autop-ingested edges can be surfaced by `edge_reviewer` if later flagged.

**3.3 Scheduling:**
- Create or update a scheduled agent (named `🤖 Unified Knowledge Graph Ingestion`) to run the extraction script post-meeting and ensure autop commits occur.
- Sync this agent with the backfill control state so the system shows a single "Knowledge Graph" status.

### Unit Tests
- Run the ingestion pipeline on 2 recent meetings; query the unified graph for edges referencing those meeting IDs.
- Ensure autop commit logic wide test: edges with complete evidence insert successfully, ones missing evidence are logged and skipped (count difference recorded).
- Verify the scheduled agent runs and updates `backfill_control.json`/new control file accordingly.

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Worker | Status |
|------------|--------|--------|
| `N5/cognition/entity_extractor.py` updates | W1.1 | ☐ |
| `backfill_progress` persistence + control file | W1.1 | ☐ |
| `GraphStore` + unified schema | W1.2 | ☐ |
| Migration of `brain.db` + `edges.db` data | W1.2 | ☐ |
| `edge_writer`, `edge_reviewer`, review queue cleanup | W1.3 | ☐ |
| Scheduled agent + autop ingestion | W1.3 | ☐ |

### Token Budget Summary

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~2,500 | ~5,500 | ~6% | Pending |
| W1.2 | ~3,000 | ~6,000 | ~7% | Pending |
| W1.3 | ~2,500 | ~4,000 | ~5% | Pending |

### MECE Validation Result

- [ ] All scope items assigned to exactly ONE worker (no overlaps)
- [ ] All deliverables covered (no gaps)
- [ ] Workers stay under 40% token budget
- [ ] Waves are sequential (W1 then W2) with no circular deps
- [ ] `python3 N5/scripts/mece_validator.py unified-knowledge-graph` must pass before handoff

---

## Worker Briefs

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | `rate-limit-hardened-backfill` | `workers/W1.1-rate-limit-hardened-backfill.md` |
| 1 | W1.2 | `schema-unification` | `workers/W1.2-schema-unification.md` |
| 2 | W2.1 | `autonomous-edge-ingestion` | `workers/W2.1-autonomous-edge-ingestion.md` |

---

## Success Criteria

1. The unified graph contains all entities/relationships from `brain.db` plus meeting edges from `edges.db`, and scheduled ingestion keeps it current without manual JSONL staging.
2. Backfill no longer crashes on rate limits; agent control state stays accurate, and the progress table survives thousands of processed IDs.
3. Pending 5,442 edges are either committed or flagged, and new meetings auto-emit edges into the same store with clear provenance metadata.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Schema migration breaks existing queries | Prototype migration on copy, keep `edges.db` read-only fallback until confirmed |
| Rate-limit workaround still fails after hitting new models | Monitor logs, add manual toggle `SKIP_OPENAI` to force `/zo/ask` and extend fallback tests |
| Autocommit inserts low-quality edges | Keep review flag + evidence length check; backlog moves to `reviewed` directory |
| Agent states diverge from reality | Control file tracks `last_run`, `status`; scheduled agent updates heartbeat each run |

---

## Level Upper Review

### Counterintuitive Suggestions Received
1. Rather than merging everything immediately, keep two stores but create a virtual union view for queries.
2. Delay auto-commit for another week and let humans clear the 5,442 backlog manually before automation.

### Incorporated
- None yet; the benefits of a single store and autop ingestion outweigh the suggestions in this context.

### Rejected (with rationale)
- Automatic commit delay: rejecting because V asked for autop ingestion assuming we debug everything, so waiting another week would lose momentum.
- Virtual union view: rejected because it perpetuates inconsistency and complexity, which conflicts with "Simple > Easy".

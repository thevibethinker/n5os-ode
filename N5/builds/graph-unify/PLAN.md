---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
type: build_plan
status: draft
provenance: con_TS42RN2pwOnBA4Kq
---

# Plan: Unified Knowledge Graph — Fix, Merge, Resume

**Objective:** Fix the crashed backfill, merge brain.db and edges.db into a single graph, commit 5,494 pending meeting edges, and resume processing the remaining 37K blocks with a resilient scheduled agent.

**Trigger:** Graph backfill crashed Feb 4 (rate-limit cascade burned 2,707 blocks). Two disconnected graph systems exist. V wants one unified system with auto-commit and auto-ingestion.

---

## Open Questions

- [x] Unified store or keep separate? → Unified (V decided)
- [x] Auto-commit pending edges? → Approved by V
- [x] New DB or extend existing? → Extend brain.db (see Nemawashi)
- [x] Spot-check before bulk commit? → Yes, sample 50 edges first

---

## Nemawashi (Alternatives Considered)

### Alt A: Create New `knowledge_graph.db`
- Migrate both DBs into a fresh one with clean schema
- **Pro:** Clean slate
- **Con:** 25K entities + 33K relationships to migrate. GraphStore, entity_extractor, graph_backfill all need rewiring. High risk.
- **Rejected:** Too much churn for marginal benefit.

### Alt B: Extend brain.db ← SELECTED
- brain.db already has `meeting_edges` (0 rows), `edge_types` (0 rows), `backfill_progress` (0 rows) — scaffolded but never populated
- Import edges.db data INTO these tables
- Fix backfill, both systems write to same DB
- **Pro:** Minimal code changes. GraphStore already has `add_meeting_edge()`, `get_meeting_edges()`, `has_meeting_edge()`. No migration risk for the 25K entity graph.
- **Con:** Two entity formats coexist (entity graph uses `entities` table, meeting edges reference entities by slug in their own rows). Acceptable — they serve different query patterns.

### Alt C: Keep Separate, Add Query Layer
- **Rejected:** Complects queries, two truth sources, violates Simple > Easy.

---

## 🚨 Trap Doors

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Reset 2,707 errored blocks | HIGH — just remove from processed set | Back up JSON first |
| Bulk-commit 5,494 edges | MEDIUM — can tag and bulk-delete | Spot-check 50 first |
| Migrate progress to SQLite | HIGH — JSON backup preserved | cp before migration |
| Modify entity_extractor error handling | HIGH — git tracked | No schema change |

---

## Checklist

### Phase 1: Fix & Harden
- ☑ Back up brain.db, backfill_progress.json, edges.db
- ☑ Fix entity_extractor.py: catch malformed JSON, add rate-limit detection + exponential backoff
- ☑ Remove 2,707 errored block IDs from processed list
- ☑ Migrate progress tracking from JSON → brain.db `backfill_progress` table
- ☑ Update graph_backfill.py to use DB-based progress
- ☑ Test: mock malformed response → confirm graceful handling + retry

### Phase 2: Merge Graphs + Commit Edges
- ☐ Populate brain.db `edge_types` from edges.db `edge_types` (6 canonical types)
- ☐ Import edges.db committed edges (515) into brain.db `meeting_edges`
- ☐ Spot-check 50 random pending edges (from backfill/completed/*.jsonl)
- ☐ Bulk-commit 5,494 pending edges into brain.db `meeting_edges`
- ☐ Import secondpass edges (273) into brain.db `meeting_edges`
- ☐ Archive JSONL files to `N5/review/edges/archived/`
- ☐ Test: query brain.db for a known person → returns both entity relationships AND meeting edges

### Phase 3: Resume + Schedule
- ☐ Create scheduled agent for backfill (500 blocks/batch, 2hr interval, with backoff)
- ☐ Wire meeting processing to write directly to brain.db `meeting_edges`
- ☐ Test: run 100-block batch → confirm DB progress, entities extracted, no JSON growth

---

## Phase 1: Fix & Harden

### Affected Files
- `N5/cognition/backfill_progress.json` — BACKUP, then phase out
- `N5/cognition/entity_extractor.py` — UPDATE — error handling
- `N5/scripts/graph_backfill.py` — UPDATE — DB-based progress
- `N5/scripts/graph_backfill_continuous.py` — UPDATE — exponential backoff
- `N5/cognition/brain.db` — UPDATE — populate `backfill_progress` table

### Changes

**1.1 Backup:**
```bash
cp N5/cognition/backfill_progress.json N5/cognition/backfill_progress.json.bak
cp N5/cognition/brain.db N5/cognition/brain.db.bak
cp N5/data/edges.db N5/data/edges.db.bak
```

**1.2 Fix entity_extractor.py:**

In `extract_entities_via_openai()`:
- Wrap `json.loads(content)` in try/except that catches JSONDecodeError AND KeyError
- On failure: log the raw response to `/dev/shm/entity_extractor_errors.log` for debugging
- Return `{"entities": [], "relationships": []}` on parse failure (don't raise)
- Add rate-limit detection: if response status is 429, sleep with exponential backoff (1s → 2s → 4s → ... → 30s cap)

In `extract_entities_via_zo()`:
- Same defensive JSON parsing
- If `/zo/ask` returns non-dict output, log and return empty result

In `extract_entities()` (the dispatcher):
- If OpenAI path returns empty AND not a cache hit, try `/zo/ask` as fallback
- Never let a KeyError or JSONDecodeError propagate — always return `([], [])`

**1.3 Migrate progress tracking:**
- Read all block IDs from `backfill_progress.json` 
- Insert into brain.db `backfill_progress` table (schema already exists):
  - `block_id TEXT PK, processed_at TEXT, entity_count INT, relationship_count INT, error TEXT, needs_retry INT, last_attempt_at TEXT, retry_count INT`
- For the 2,707 errored blocks: insert with `needs_retry = 1` and `error = <original error>`
- For the 45,128 successful blocks: insert with `needs_retry = 0`
- Update `graph_backfill.py` to check/insert into this table instead of JSON

**1.4 Update graph_backfill.py:**
- Replace all reads of `backfill_progress.json` with queries to `backfill_progress` table
- On successful extraction: `INSERT OR REPLACE INTO backfill_progress (block_id, processed_at, entity_count, relationship_count, needs_retry) VALUES (?, datetime('now'), ?, ?, 0)`
- On error: `INSERT OR REPLACE INTO backfill_progress (block_id, last_attempt_at, error, needs_retry, retry_count) VALUES (?, datetime('now'), ?, 1, COALESCE((SELECT retry_count FROM backfill_progress WHERE block_id = ?), 0) + 1)`
- Query for unprocessed: `SELECT id FROM blocks WHERE id NOT IN (SELECT block_id FROM backfill_progress WHERE needs_retry = 0)`
- Query for retryable: `SELECT block_id FROM backfill_progress WHERE needs_retry = 1 AND retry_count < 3`

**1.5 Update graph_backfill_continuous.py:**
- Add exponential backoff: if a batch has >50% error rate, sleep `min(30 * 2^consecutive_failures, 1800)` seconds
- Reset failure counter on any successful batch
- Log batch results to `/dev/shm/graph_backfill.log`

### Tests
- Run entity_extractor with a mock 429 response → returns empty, no exception
- Run entity_extractor with truncated JSON → returns empty, no exception  
- Insert 100 block IDs into backfill_progress, query unprocessed → correct set returned
- Run 50-block batch with DB tracking → progress table updated, no JSON file touched

---

## Phase 2: Merge Graphs + Commit Edges

### Affected Files
- `N5/cognition/brain.db` — UPDATE — populate meeting_edges and edge_types
- `N5/data/edges.db` — READ ONLY (then archive)
- `N5/review/edges/backfill/completed/*.jsonl` — READ then archive
- `N5/review/edges/secondpass/*.jsonl` — READ then archive
- `N5/cognition/graph_store.py` — UPDATE — add unified query method

### Changes

**2.1 Populate edge_types:**
- Copy 6 edge types from edges.db `edge_types` into brain.db `edge_types`:
  - originated_by, supported_by, challenged_by, hoped_for, concerned_about, depends_on

**2.2 Import committed edges:**
- Read all 515 edges from edges.db `edges` table
- Map to brain.db `meeting_edges` schema:
  - source_type, source_id, relation, target_type, target_id → direct copy
  - context_meeting_id → meeting_id
  - evidence → evidence
  - status → status
  - created_at → created_at
- Use `GraphStore.add_meeting_edge()` for each (already handles dedup via `has_meeting_edge()`)

**2.3 Spot-check pending edges:**
- Sample 50 random edges from `backfill/completed/*.jsonl`
- Verify: evidence field contains actual reasoning (not stubs), entity references are reasonable
- Report quality score before proceeding

**2.4 Bulk-commit pending edges:**
- Parse all JSONL files in `backfill/completed/` — skip lines with `_meta` or `_extraction_context`
- Expected format per edge: `{source_type, source_id, relation, target_type, target_id, evidence, meeting_id}`
- Insert via `GraphStore.add_meeting_edge()` with status='active'
- Also import `secondpass/*.jsonl` (273 edges) — same format but `context_meeting_id` instead of `meeting_id`

**2.5 Archive:**
- `mv N5/review/edges/backfill/completed/ N5/review/edges/archived/completed-2026-02-10/`
- `mv N5/review/edges/secondpass/ N5/review/edges/archived/secondpass-2026-02-10/`
- Keep `N5/review/edges/backfill/` directory for future batch metadata

**2.6 Add unified query to GraphStore:**
- New method `query_entity_full(name_or_id)` that returns:
  - Entity info from `entities` table
  - All relationships from `relationships` table  
  - All meeting edges from `meeting_edges` where entity appears as source or target
- This is the single entry point for "tell me everything about X"

### Tests
- Query "David Spiegel" → returns entity graph relationships + meeting edges where he appears
- Count meeting_edges after import → should be ~6,282 (515 committed + 5,494 completed + 273 secondpass)
- No duplicate edges (run dedup check)

---

## Phase 3: Resume + Schedule

### Affected Files
- Scheduled agent — CREATE — backfill driver
- `N5/scripts/graph_backfill.py` — already updated in Phase 1
- Meeting processing pipeline — UPDATE — write to brain.db directly

### Changes

**3.1 Create scheduled agent:**
- Run every 2 hours
- Execute: `python3 N5/scripts/graph_backfill.py --batch 500`
- Check backfill_control.json for state before running
- If completion > 99%: notify V, set state to complete, agent can self-disable

**3.2 Wire meeting edge extraction:**
- Update the meeting processing pipeline's edge extraction step to call `GraphStore.add_meeting_edge()` directly
- Skip the JSONL review queue (V approved auto-commit)
- Keep `evidence` quality bar: if evidence < 10 chars, skip that edge

**3.3 Completion monitoring:**
- The scheduled agent prints a status summary each run:
  - Blocks remaining, % complete, entities this batch, errors this batch
  - If 3 consecutive batches have >50% error rate, pause and notify V

### Tests
- Agent runs once → 500 blocks processed, progress table updated
- Run on 2 recent meetings → edges appear in brain.db meeting_edges directly

---

## Success Criteria

1. **Zero errored blocks stuck** — all 2,707 retried or processed
2. **One database** — brain.db contains entity graph + meeting edges + edge types
3. **~6,282 meeting edges committed** — from all pending sources
4. **Backfill resuming autonomously** — scheduled agent processing 500 blocks/2hr
5. **Unified query works** — `query_entity_full("David Spiegel")` returns both types
6. **Resilient** — rate limits cause backoff, not permanent data loss

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bulk edge import has quality issues | Medium | Spot-check 50 edges before committing all |
| Backfill hits rate limits again | Medium | Exponential backoff + DB-based retry |
| brain.db grows too large | Low | Currently 138MB, projected ~200MB at completion. Fine for SQLite. |
| GraphStore schema changes break existing queries | Medium | Only adding methods, not changing existing ones |

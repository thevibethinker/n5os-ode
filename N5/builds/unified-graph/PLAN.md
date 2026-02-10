---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
type: build_plan
status: draft
provenance: con_TS42RN2pwOnBA4Kq
---

# Plan: Unified Knowledge Graph System

**Objective:** Merge brain.db (entity graph) and edges.db (meeting edges) into a single resilient knowledge graph, fix the backfill crash, commit 5,466 pending edges, and resume processing the remaining 37K blocks — all with auto-ingestion going forward.

**Trigger:** Graph backfill crashed on Feb 4 (rate limit cascade burned 2,707 blocks). Two disconnected graph systems exist. V wants one unified system with auto-commit.

**Key Design Principle:** Simple > Easy. Don't create a new database — extend brain.db (which already has 25K entities and 33K relationships) to absorb edges.db data. Minimal schema changes, maximum reuse.

---

## Open Questions

- [x] Unified store or virtual union? → V chose unified (one DB)
- [x] Auto-commit pending edges? → V approved
- [x] New DB or extend existing? → Extend brain.db (see Nemawashi below)

---

## Nemawashi (Alternatives Considered)

### Alt A: Create New `knowledge_graph.db` (Previous Plan's Approach)
- Migrate both brain.db and edges.db into a fresh DB with a clean schema
- **Pro:** Clean slate, ideal schema design
- **Con:** 25K entities + 33K relationships to migrate. GraphStore.py, entity_extractor.py, graph_backfill.py all need rewiring. High risk of breaking working code.

### Alt B: Extend brain.db with meeting edge tables ← RECOMMENDED
- brain.db already has `meeting_edges` and `edge_types` tables (currently empty — they were scaffolded but never used)
- Import edges.db data INTO brain.db's meeting_edges table
- Fix the backfill, then both systems write to the same DB
- **Pro:** Minimal code changes. GraphStore already has infrastructure. No migration risk.
- **Con:** Schema isn't "ideal" — two entity formats coexist temporarily.

### Alt C: Keep Separate DBs, Add Query Layer
- Build a unified query API that queries both
- **Pro:** No data migration
- **Con:** Complects query logic. Two truth sources. Violates Simple > Easy.

**Decision:** Alt B. brain.db already has the scaffolding. The 0-row `meeting_edges` and `edge_types` tables prove this was always the intended destination.

---

## 🚨 Trap Doors

1. **Resetting 2,707 errored block IDs** — Reversible (we just remove them from processed list)
2. **Auto-committing 5,466 pending edges** — Semi-reversible (we can tag them and bulk-delete if quality is bad). Spot-check first.
3. **Modifying backfill_progress.json** — Irreversible if we lose the file. **Mitigation:** Back up before changes.

---

## Checklist

### Phase 1: Fix & Harden Backfill
- ☐ Back up backfill_progress.json and brain.db
- ☐ Fix entity_extractor.py: catch malformed OpenAI responses, add rate-limit detection + backoff
- ☐ Remove 2,707 errored block IDs from processed list so they get retried
- ☐ Migrate progress tracking from JSON file to brain.db's `backfill_progress` table (already exists, 0 rows)
- ☐ Update graph_backfill.py to use DB-based progress tracking
- ☐ Test: simulate malformed response → confirm graceful fallback

### Phase 2: Unify Graphs + Commit Pending Edges
- ☐ Import edges.db data (515 committed edges + 503 entities) into brain.db `meeting_edges` table
- ☐ Spot-check 50 random pending edges for quality
- ☐ Bulk-commit 5,466 pending edges into brain.db `meeting_edges` table
- ☐ Archive pending JSONL files to `N5/review/edges/archived/`
- ☐ Update GraphStore.py with unified query methods that span both entity types
- ☐ Test: query for a person → returns both entity graph relationships AND meeting edges

### Phase 3: Resume Backfill + Auto-Ingestion
- ☐ Create scheduled agent to run backfill in controlled batches (500 blocks/run, with backoff)
- ☐ Wire meeting edge extraction to write directly to brain.db instead of JSONL review queue
- ☐ Test: run backfill on 100 blocks → confirm progress tracked in DB, entities extracted, no JSON file growth

---

## Phase 1: Fix & Harden Backfill

### Affected Files
- `N5/cognition/backfill_progress.json` — BACKUP then phase out
- `N5/cognition/entity_extractor.py` — UPDATE — error handling + rate limit detection
- `N5/scripts/graph_backfill.py` — UPDATE — use DB progress tracking, retry errored blocks
- `N5/scripts/graph_backfill_continuous.py` — UPDATE — exponential backoff, DB progress
- `N5/cognition/brain.db` — UPDATE — populate `backfill_progress` table

### Changes

**1.1 Backup:**
- `cp N5/cognition/backfill_progress.json N5/cognition/backfill_progress.json.bak`
- `cp N5/cognition/brain.db N5/cognition/brain.db.bak`

**1.2 Fix entity_extractor.py:**

In `extract_entities_via_openai()`:
- Wrap `json.loads(content)` in explicit try/except that logs the raw response on failure
- Detect HTTP 429 / rate limit errors and return `None` (triggers fallback to /zo/ask)
- Add a 2-second sleep after any error before returning (prevents cascade)

In `extract_entities()`:
- If both OpenAI and /zo/ask return empty/error, log the block_id and return empty lists (don't raise)
- Never allow a KeyError to propagate — wrap all dict access in .get()

**1.3 Reset errored blocks:**
- Parse `backfill_progress.json`, identify the 2,707 block IDs that errored with `'\n  "entities"'`
- Remove them from `processed_block_ids` list
- These blocks will be re-processed on next run

**1.4 Migrate progress to SQLite:**
- `backfill_progress` table in brain.db already exists with schema: `(block_id TEXT, processed_at TEXT, entity_count INTEGER, relationship_count INTEGER, error TEXT)`
- INSERT all 45,128 successfully processed block IDs from the JSON file
- INSERT the 2,707 errored blocks with their error messages (so we have audit trail) but mark them for retry by adding a `needs_retry INTEGER DEFAULT 0` column
- After migration, graph_backfill.py checks brain.db instead of JSON file

**1.5 Update graph_backfill.py:**
- Replace `progress["processed_block_ids"]` checks with `SELECT block_id FROM backfill_progress WHERE needs_retry = 0`
- Replace JSON file writes with `INSERT INTO backfill_progress`
- Add exponential backoff: if 5+ consecutive errors, sleep 30s; if 10+, sleep 120s; if 20+, pause and set control to "rate_limited"

### Unit Tests
- Mock a malformed OpenAI response → entity_extractor returns empty list, no exception
- Insert 100 block_ids into backfill_progress → graph_backfill skips them correctly
- Simulate 5 consecutive errors → confirm backoff kicks in

---

## Phase 2: Unify Graphs + Commit Pending Edges

### Affected Files
- `N5/cognition/brain.db` — UPDATE — populate `meeting_edges` and `edge_types` tables
- `N5/data/edges.db` — READ ONLY — source for migration
- `N5/review/edges/pending/*.jsonl` — READ + ARCHIVE
- `N5/cognition/graph_store.py` — UPDATE — add unified query methods
- `N5/scripts/edge_reviewer.py` — UPDATE — target brain.db instead of edges.db

### Changes

**2.1 Import edges.db into brain.db:**

brain.db's `meeting_edges` table schema: `(id, source_type, source_id, relation, target_type, target_id, meeting_id, evidence, status, created_at, metadata)`

edges.db's `edges` table has these PLUS lifecycle fields: `superseded_by, reversed_at, reversal_reason, outcome_status, outcome_edge_id, outcome_note, updated_at, evolution_type, resolution_status`

**Schema adjustment needed:** ALTER brain.db `meeting_edges` to add the lifecycle columns from edges.db. These are valuable and should be preserved:
```sql
ALTER TABLE meeting_edges ADD COLUMN superseded_by INTEGER;
ALTER TABLE meeting_edges ADD COLUMN reversed_at TEXT;
ALTER TABLE meeting_edges ADD COLUMN reversal_reason TEXT;
ALTER TABLE meeting_edges ADD COLUMN outcome_status TEXT;
ALTER TABLE meeting_edges ADD COLUMN outcome_note TEXT;
ALTER TABLE meeting_edges ADD COLUMN updated_at TEXT;
ALTER TABLE meeting_edges ADD COLUMN evolution_type TEXT;
ALTER TABLE meeting_edges ADD COLUMN resolution_status TEXT;
```

Also import `edge_types` (10 rows) into brain.db's empty `edge_types` table.

**2.2 Spot-check pending edges:**
- Read 50 random edges from pending JSONL files
- Validate: evidence field is non-empty and >20 chars, required fields present, meeting_id exists
- Report quality score before bulk commit

**2.3 Bulk commit pending edges:**
- Parse all 275 JSONL files (5,466 edges)
- Insert into brain.db `meeting_edges` with `status='active'`
- Move files to `N5/review/edges/archived/2026-02-10_bulk_commit/`

**2.4 Unified query methods in GraphStore:**
```python
def query_person(self, name: str) -> dict:
    """Returns entity graph relationships AND meeting edges for a person."""
    
def query_idea(self, slug: str) -> dict:
    """Returns meeting edges about an idea with originator, supporters, challengers."""

def query_meeting(self, meeting_id: str) -> dict:
    """Returns all edges from a specific meeting."""
```

### Unit Tests
- After migration: `SELECT COUNT(*) FROM meeting_edges` ≥ 515 + 5,466
- Query "David Spiegel" → returns both entity relationships and meeting edges
- Spot-check reports quality ≥ 80% before proceeding with bulk commit

---

## Phase 3: Resume Backfill + Auto-Ingestion

### Affected Files
- Scheduled agent — CREATE — runs backfill in controlled batches
- `N5/scripts/graph_backfill.py` — already updated in Phase 1
- `N5/scripts/edge_extractor.py` — UPDATE — write to brain.db instead of JSONL
- `N5/config/backfill_control.json` — UPDATE — reflect new state

### Changes

**3.1 Create scheduled agent:**
- Runs every 2 hours
- Calls `graph_backfill.py --batch 200` (smaller batches = less damage if rate limited)
- Checks control state first: skip if "paused" or "rate_limited"
- Updates control file with last_run and status

**3.2 Wire meeting edge auto-ingestion:**
- Update edge_extractor.py to import GraphStore and call `add_meeting_edge()` directly
- Remove JSONL file creation for new extractions (existing pipeline writes directly to brain.db)
- Keep a lightweight log for audit (`N5/logs/edge_ingestion.log`)

**3.3 Resume backfill:**
- Set control state to "active"
- Agent picks up remaining 34,374 + 2,707 retry blocks
- At 200 blocks per run, every 2 hours = ~2,400/day ≈ 16 days to completion

### Unit Tests
- Run backfill on 100 blocks → entities appear in brain.db, progress tracked in `backfill_progress` table
- Process one meeting through edge extraction → edges appear in brain.db `meeting_edges`
- Scheduled agent runs once → control file updated with timestamp

---

## MECE Validation

This build is sequential (Phase 1 → 2 → 3), not parallel. **Single-worker build** — no MECE split needed. Each phase depends on the previous.

Rationale: Phase 2 requires Phase 1's DB progress tracking. Phase 3 requires Phase 2's unified schema. Running these in parallel would create merge conflicts in brain.db and graph_store.py.

---

## Success Criteria

1. **Backfill resumes:** Scheduled agent processes blocks without crashing on rate limits
2. **Errored blocks retried:** 2,707 previously-skipped blocks get re-processed
3. **Single graph:** brain.db contains ALL entities (25K+), relationships (33K+), AND meeting edges (6K+)
4. **edges.db retired:** No new code writes to edges.db
5. **Auto-ingestion:** New meetings write edges directly to brain.db
6. **Progress tracking:** No more 3MB JSON file — progress in SQLite

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| brain.db corruption during schema ALTER | Back up before any changes |
| Pending edge quality is bad | Spot-check 50 first, abort bulk commit if <80% quality |
| Rate limit hits again during resumed backfill | Exponential backoff built into Phase 1; smaller batches (200 vs 500) |
| edges.db has lifecycle data we lose | ALTERing meeting_edges to include all lifecycle columns |
| Backfill takes too long at 200/batch | Can increase batch size after confirming stability |

---

## Level Upper Review

Not invoking for this build — the architecture decisions are straightforward (extend existing DB, fix error handling, commit pending data). No novel design needed.

---

## Handoff Notes

**For Builder:**
- Start Phase 1, complete it, test it, then Phase 2, then Phase 3
- Back up brain.db FIRST (trap door protection)
- The `backfill_progress` table already exists in brain.db with the right schema + a needed `needs_retry` column
- The `meeting_edges` table exists but needs ALTERs for lifecycle columns
- Spot-check quality of pending edges before bulk commit — if <80%, stop and ask V

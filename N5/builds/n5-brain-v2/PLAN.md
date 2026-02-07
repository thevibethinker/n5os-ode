---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.0
provenance: con_7fR5qWFds2TAonyD
status: draft
---

# N5 Brain v2: FlashRank + GraphRAG + Temporal Tracking

## Open Questions

1. **FlashRank model selection** — Which model variant? (default `ms-marco-MiniLM-L-6-v2` or larger?)
2. **Entity extraction approach** — Use LLM (`/zo/ask`) or local NER model?
3. **Graph storage** — Extend existing SQLite or create separate `graph.db`?
4. **Reindex requirement** — Do existing documents need full reindex for graph/temporal?

---

## Success Criteria

- [ ] FlashRank reranker integrated, benchmarked against current cross-encoder
- [ ] Entity/relationship extraction working on new documents
- [ ] Graph queries returning connected concepts
- [ ] Temporal queries ("what did I believe before X date") working
- [ ] All existing search functionality preserved (no regressions)
- [ ] Sync between brain.db, vectors_v2.db, and graph tables maintained

---

## Nemawashi: Alternatives Considered

### Alternative 1: All-in-One Database
Add graph tables + temporal fields to existing `vectors_v2.db`

**Pros:** Single DB, simpler sync
**Cons:** DB growing large, mixed concerns

### Alternative 2: Separate Graph Database (Neo4j)
Use Neo4j for graph, keep vectors_v2.db for embeddings

**Pros:** Purpose-built graph DB, Cypher queries
**Cons:** New dependency, deployment complexity, overkill for our scale

### Alternative 3: SQLite Graph Extension ⭐ RECOMMENDED
Add graph tables to `brain.db` (metadata home), keep vectors in `vectors_v2.db`

**Pros:** No new dependencies, brain.db already has metadata, clean separation
**Cons:** Need to ensure sync

**Decision:** Alternative 3 — extend brain.db with graph tables, add temporal fields to blocks

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Schema changes to brain.db | Medium | Create migration script, backup before |
| FlashRank replacing cross-encoder | Easy | Keep both, A/B test, config flag |
| Entity extraction model choice | Medium | Abstract behind interface |

---

## Architecture Overview

```
                    ┌─────────────────────────────────────────────┐
                    │              N5 Memory Client               │
                    └─────────────────────────────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
    ┌─────────────┐            ┌─────────────────┐          ┌──────────────┐
    │  brain.db   │            │  vectors_v2.db  │          │  FlashRank   │
    │             │            │                 │          │  (reranker)  │
    │ - resources │            │ - resources     │          └──────────────┘
    │ - blocks    │            │ - blocks        │
    │ - entities  │ ◄── NEW    │ - vectors       │
    │ - relations │ ◄── NEW    │                 │
    │ - temporal  │ ◄── NEW    │                 │
    └─────────────┘            └─────────────────┘
```

---

## Phase 1: FlashRank Integration (Low Risk, Quick Win)

**Goal:** Replace/augment cross-encoder reranker with FlashRank

### Affected Files
- `N5/cognition/n5_memory_client.py` — Add FlashRank reranker option
- `N5/cognition/requirements.txt` or install — Add flashrank dependency

### Changes
1. Install FlashRank: `pip install flashrank`
2. Add `FlashRankReranker` class alongside existing cross-encoder
3. Add config flag: `N5_RERANKER=flashrank|cross-encoder`
4. Update `search()` method to use configured reranker
5. Benchmark: run same queries, compare MRR/latency

### Unit Tests
- [ ] FlashRank reranker returns sorted results
- [ ] Config flag switches between rerankers
- [ ] Benchmark shows improvement or parity

### Checklist
- [ ] FlashRank installed
- [ ] FlashRankReranker class implemented
- [ ] Config flag working
- [ ] Benchmark completed
- [ ] Documentation updated

---

## Phase 2: Temporal Tracking (Medium Risk, Schema Change)

**Goal:** Track when content was indexed and enable time-bounded queries

### Affected Files
- `N5/cognition/n5_memory_client.py` — Schema migration, temporal query methods
- `N5/scripts/brain_migrate_v2.py` — NEW: migration script

### Schema Changes
```sql
-- Add to blocks table
ALTER TABLE blocks ADD COLUMN indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE blocks ADD COLUMN valid_from TIMESTAMP;
ALTER TABLE blocks ADD COLUMN valid_until TIMESTAMP;
ALTER TABLE blocks ADD COLUMN supersedes_block_id TEXT;

-- Add to resources table  
ALTER TABLE resources ADD COLUMN first_indexed_at TIMESTAMP;
ALTER TABLE resources ADD COLUMN version INTEGER DEFAULT 1;
```

### Changes
1. Create migration script with backup
2. Run migration on brain.db AND vectors_v2.db
3. Update `index_file()` to populate temporal fields
4. Add `search_temporal()` method: filter by time range
5. Add `get_belief_history()` method: show evolution of content for a topic

### Unit Tests
- [ ] Migration runs without data loss
- [ ] New indexes populate temporal fields
- [ ] `search_temporal(before="2026-01-01")` returns only older content
- [ ] `get_belief_history("topic")` shows versions over time

### Checklist
- [ ] Migration script created
- [ ] Backup taken before migration
- [ ] Schema migrated on both DBs
- [ ] index_file() updated
- [ ] Temporal query methods working
- [ ] Tests passing

---

## Phase 3: GraphRAG Layer (Higher Risk, New Capability)

**Goal:** Extract entities/relationships, enable relationship queries

### Affected Files
- `N5/cognition/n5_memory_client.py` — Graph query methods
- `N5/cognition/entity_extractor.py` — NEW: LLM-based entity extraction
- `N5/cognition/graph_store.py` — NEW: Graph storage and traversal
- `N5/scripts/brain_migrate_v2.py` — Add graph tables

### Schema Additions (brain.db)
```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- PERSON, CONCEPT, ORGANIZATION, BELIEF, etc.
    canonical_name TEXT,  -- normalized form
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_block_id TEXT,
    metadata JSON,
    FOREIGN KEY (source_block_id) REFERENCES blocks(id)
);

CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    from_entity_id TEXT NOT NULL,
    to_entity_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,  -- KNOWS, BELIEVES, WORKS_AT, MENTIONS, RELATED_TO
    confidence REAL DEFAULT 1.0,
    source_block_id TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_entity_id) REFERENCES entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES entities(id),
    FOREIGN KEY (source_block_id) REFERENCES blocks(id)
);

CREATE INDEX idx_entities_name ON entities(canonical_name);
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX idx_relationships_to ON relationships(to_entity_id);
CREATE INDEX idx_relationships_type ON relationships(relation_type);
```

### Entity Extraction Pipeline
```python
# Using /zo/ask for extraction
prompt = """Extract entities and relationships from this text.

Text: {chunk_text}

Return JSON:
{
  "entities": [
    {"name": "...", "type": "PERSON|CONCEPT|ORG|BELIEF|EVENT", "context": "..."}
  ],
  "relationships": [
    {"from": "...", "to": "...", "type": "KNOWS|BELIEVES|WORKS_AT|RELATED_TO", "context": "..."}
  ]
}
"""
```

### Changes
1. Create graph schema migration
2. Implement `EntityExtractor` class using `/zo/ask`
3. Implement `GraphStore` class for CRUD + traversal
4. Update `index_file()` to extract entities after chunking
5. Add `search_graph()`: find entities matching query
6. Add `get_connections()`: traverse relationships from entity
7. Add `hybrid_search()`: combine vector + graph results

### Unit Tests
- [ ] Entity extraction returns valid JSON
- [ ] Entities stored and retrievable
- [ ] Relationships link entities correctly
- [ ] `get_connections("V")` returns related entities
- [ ] `hybrid_search()` combines vector + graph results

### Checklist
- [ ] Graph schema created
- [ ] EntityExtractor working
- [ ] GraphStore CRUD working
- [ ] index_file() extracts entities
- [ ] Graph query methods working
- [ ] Hybrid search working
- [ ] Tests passing

---

## Phase 4: Integration & Testing

**Goal:** Ensure all components work together, no regressions

### Changes
1. Update `brain_sync_check.py` to include graph tables
2. Run full reindex on sample documents with all features
3. Benchmark search quality: vector-only vs hybrid
4. Document new query capabilities

### Checklist
- [ ] Sync check updated for graph tables
- [ ] Sample reindex successful
- [ ] Benchmark shows improvement
- [ ] Documentation complete
- [ ] V approves for production use

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema migration breaks existing data | Medium | High | Backup before migration, test on copy first |
| Entity extraction is slow/expensive | Medium | Medium | Batch processing, cache results, async extraction |
| Graph queries are slow | Low | Medium | Add indexes, limit traversal depth |
| FlashRank worse than cross-encoder | Low | Low | Keep both, A/B test, easy rollback |

---

## Dependencies

- `flashrank` — PyPI package for reranking
- Existing `/zo/ask` API — for entity extraction (no new deps)
- SQLite — already in use

---

## Estimated Effort

| Phase | Effort | Can Parallelize? |
|-------|--------|------------------|
| Phase 1: FlashRank | 1-2 hours | Yes (independent) |
| Phase 2: Temporal | 2-3 hours | Yes (independent) |
| Phase 3: GraphRAG | 4-6 hours | After Phase 2 (needs schema) |
| Phase 4: Integration | 1-2 hours | After all phases |

**Total:** ~10-13 hours, but Phases 1-2 can run in parallel

---

## Execution Recommendation

**Option A: Sequential (Safe)**
Phase 1 → Phase 2 → Phase 3 → Phase 4

**Option B: Parallel Start (Faster)** ⭐ RECOMMENDED
- Stream 1: Phase 1 (FlashRank)
- Stream 2: Phase 2 (Temporal)
- Then: Phase 3 (GraphRAG) — needs Phase 2 schema
- Finally: Phase 4 (Integration)

This is parallelizable via Pulse with 2 initial Drops.

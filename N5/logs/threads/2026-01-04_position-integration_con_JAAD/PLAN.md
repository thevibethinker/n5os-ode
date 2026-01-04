---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_JAADiniaFXpKQUTN
build_slug: position-integration
---

# PLAN: Phase 4.5 — Position Integration into Context Graph

## Open Questions

1. **Bidirectional sync timing** — When position evolves (stability change), should edges auto-update? Or manual review?
2. **Granularity of position-edge links** — Link to specific evidence sentences, or whole position?
3. **Position merges** — When positions merge/supersede, how do their edges transfer?

## Checklist

### Phase 4.5: Schema Extension & Entity Registration
- [x] Add `position` to entities table in edges.db
- [x] Add position-specific edge types to edge_types.py
- [x] Create sync script: positions.db → entities table
- [x] Unit test: position entity CRUD

### Phase 4.6: Edge Extraction Enhancement  
- [x] Update B33 prompt to detect position-supporting edges
- [x] Add `crystallized_from` relation for position←edge links
- [x] Add `supports_position` / `challenges_position` relations
- [x] Unit test: edge extraction with position detection

### Phase 4.7: Cognitive Mirror Position Analysis
- [x] New script: `position_stability.py` — edge support analysis
- [x] Enhance existing scripts to include position context
- [x] Unit test: position stability scoring

## Phase 4.5: Schema Extension & Entity Registration

### Affected Files
- `N5/data/edges.db` — schema migration
- `N5/scripts/edge_types.py` — new relations
- `N5/scripts/sync_positions_to_entities.py` — NEW
- `N5/scripts/cognitive_mirror/_base.py` — helper functions

### Changes

#### 1. Schema Migration SQL
```sql
-- positions already valid in ENTITY_TYPES, just need to populate entities table
-- No schema change needed to edges.db - entities table already supports any entity_type

-- Sync script will INSERT positions as entities:
INSERT OR REPLACE INTO entities (entity_type, entity_id, name, metadata, created_at)
SELECT 
    'position' as entity_type,
    id as entity_id,
    title as name,
    json_object(
        'domain', domain,
        'stability', stability,
        'confidence', confidence,
        'insight_preview', substr(insight, 1, 200)
    ) as metadata,
    created_at
FROM positions;  -- This is a cross-db query, needs Python bridge
```

#### 2. New Edge Types (edge_types.py)
```python
# Add to EDGE_TYPES dict:
"crystallized_from": EdgeType(
    relation="crystallized_from",
    category=EdgeCategory.CHAIN,
    description="Position formed from accumulated evidence",
    inverse="contributed_to"
),
"supports_position": EdgeType(
    relation="supports_position",
    category=EdgeCategory.STANCE,
    description="Edge evidence supports this position",
    inverse="supported_by_edge"
),
"challenges_position": EdgeType(
    relation="challenges_position",
    category=EdgeCategory.STANCE,
    description="Edge evidence challenges this position",
    inverse="challenged_by_edge"
),
```

#### 3. Sync Script (sync_positions_to_entities.py)
```python
#!/usr/bin/env python3
"""Sync positions.db → entities table in edges.db"""

def sync_positions():
    # Read all positions from positions.db
    # Upsert into entities table in edges.db
    # Return count synced
    pass

def main():
    # --dry-run: show what would sync
    # --force: sync even if recently synced
    pass
```

### Unit Tests
```bash
# After sync, verify:
sqlite3 N5/data/edges.db "SELECT COUNT(*) FROM entities WHERE entity_type='position'"
# Should equal:
sqlite3 N5/data/positions.db "SELECT COUNT(*) FROM positions"

# Verify entity lookup works:
python3 -c "from N5.scripts.context_graph import get_entity; print(get_entity('position', 'hiring-signal-collapse'))"
```

## Phase 4.6: Edge Extraction Enhancement

### Affected Files
- `N5/prompts/Blocks/Generate_B33.prompt.md` — prompt update
- `N5/scripts/extract_edges.py` — position matching logic
- `N5/scripts/edge_types.py` — already updated in 4.5

### Changes

#### 1. B33 Prompt Enhancement
Add to extraction instructions:
```markdown
## Position Detection
When extracting edges, check if evidence supports or challenges known positions.
If a statement strongly aligns with or contradicts V's documented positions, add:
- `supports_position` edge: idea/decision → position
- `challenges_position` edge: idea/decision → position

Query available positions: `python3 N5/scripts/positions.py search "<key phrase>"`
```

#### 2. Position Matching in extract_edges.py
```python
def match_to_positions(edge_evidence: str) -> list[dict]:
    """Find positions that edge evidence supports/challenges."""
    from N5.scripts.positions import find_similar
    
    matches = find_similar(edge_evidence, threshold=0.7)
    results = []
    for m in matches:
        # Semantic analysis to determine support vs challenge
        stance = analyze_stance(edge_evidence, m['insight'])
        results.append({
            'position_id': m['id'],
            'relation': 'supports_position' if stance > 0 else 'challenges_position',
            'confidence': abs(stance)
        })
    return results
```

### Unit Tests
```bash
# Extract edges from test meeting, verify position links created
python3 N5/scripts/extract_edges.py --meeting-id mtg_test --dry-run
# Check output includes supports_position/challenges_position edges
```

## Phase 4.7: Cognitive Mirror Position Analysis

### Affected Files
- `N5/scripts/cognitive_mirror/position_stability.py` — NEW
- `N5/scripts/cognitive_mirror/_base.py` — add position helpers

### Changes

#### 1. New Script: position_stability.py
```python
"""
Position Stability Analysis

Questions answered:
- Which positions have strongest edge support?
- Which positions are challenged by recent evidence?
- Which positions lack recent validation?
"""

ANALYSIS_PROMPT = """
Given these positions and their supporting/challenging edges:

{positions_with_edges}

Analyze:
1. WELL-SUPPORTED: Positions with 3+ supporting edges, 0-1 challenges
2. CONTESTED: Positions with both support and challenge edges
3. UNVALIDATED: Positions with <2 supporting edges in last 90 days
4. STABILITY RECOMMENDATIONS: Which should upgrade/downgrade stability?

Focus on actionable insights for V's belief maintenance.
"""
```

### Unit Tests
```bash
# Run analysis, verify output
python3 N5/scripts/cognitive_mirror/position_stability.py --dry-run
# Check report generated in N5/insights/cognitive_mirror/
```

## Alternatives Considered

### Alternative A: Foreign Key Only (REJECTED)
**Approach:** Keep positions in positions.db, reference by ID in edges without entity registration.
**Pros:** Simpler, no sync needed
**Cons:** Can't query "all entities connected to X" uniformly; positions are second-class
**Decision:** Rejected — defeats purpose of unified graph

### Alternative B: Merge positions.db into edges.db (REJECTED)
**Approach:** Migrate all position data into edges.db, eliminate positions.db
**Pros:** Single database, no sync
**Cons:** positions.db has different lifecycle (semantic search via brain.db), tight coupling
**Decision:** Rejected — violates separation of concerns, positions have their own indexing layer

### Alternative C: Entity Registration + Sync (SELECTED) ✓
**Approach:** positions.db remains authoritative, sync to entities table for graph queries
**Pros:** Clean separation, positions keep semantic search, graph gets queryable nodes
**Cons:** Requires sync discipline
**Decision:** Selected — best balance of simplicity and capability

## Trap Doors (Irreversible Decisions)

### 🚨 TRAP DOOR 1: Edge Type Naming
Once `supports_position` / `challenges_position` are used in edges, renaming is expensive.
**Mitigation:** Review naming carefully before Phase 4.6 implementation.

### 🚨 TRAP DOOR 2: Position ID as Entity ID
Using position slug as entity_id couples to positions.db ID generation.
**Mitigation:** Acceptable — position IDs are already stable slugs.

### ⚠️ LOW RISK: Sync Direction
positions.db → edges.db sync is one-way. If we later want edges.db to update positions, architecture change needed.
**Mitigation:** Document as intentional constraint. Positions are authoritative source.

## Success Criteria

- [ ] `SELECT * FROM entities WHERE entity_type='position'` returns all 97 positions
- [ ] `python3 N5/scripts/trace_context.py position:hiring-signal-collapse` returns connected edges
- [ ] B33 extraction creates position-linking edges for relevant meetings
- [ ] `position_stability.py` generates actionable stability report
- [ ] No orphaned position references (all position IDs in edges exist in positions.db)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Sync drift (positions.db changes, entities stale) | Medium | Medium | Add sync to position add/update hooks |
| Over-linking (too many edges to positions) | Medium | Low | Threshold tuning, human review queue |
| Performance (97 positions × semantic search) | Low | Medium | Cache position embeddings, batch matching |

## Estimated Effort

- Phase 4.5: 2-3 hours (schema + sync script)
- Phase 4.6: 3-4 hours (prompt + extraction logic)
- Phase 4.7: 2 hours (cognitive mirror script)

**Total: ~8 hours of Builder time**

---

*Plan created by Architect | 2026-01-04 14:38 ET*
*Ready for V review → Builder handoff*





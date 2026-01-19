---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
type: build_plan
status: active
provenance: con_AVUiANpq2GYAc3Qz
---

# Option C: Foundation Validation Before Connection

## Premise

Before adding connections between positions, we must validate that the **positions themselves** are correct. Connecting garbage to garbage just creates well-organized garbage.

## Current State (Problems Identified)

1. **Promotion Pipeline Broken**: 101 approved candidates never made it to positions.db
2. **B32 Extractions Have No Connections**: 80/124 positions (65%) have zero connections
3. **Potential Duplicates**: Unknown duplicate rate between candidates and existing positions
4. **Domain Accuracy Unknown**: 31 positions flagged as potentially mis-domained
5. **Quality Unknown**: No systematic review of the 80 B32-extracted positions in positions.db

## Option C Phases

### Phase 0: Fix the Promotion Pipeline (BLOCKING)
**Goal**: Understand why 101 approved candidates didn't become positions

**Tasks**:
- [ ] Audit the promotion workflow (what script should have run?)
- [ ] Check if 101 approved candidates are duplicates of existing positions
- [ ] Either: promote them properly OR mark them as already-present
- [ ] Fix the pipeline so future approvals auto-promote

**Output**: Clear candidates.jsonl with accurate statuses

---

### Phase 1: Deduplicate (Refinement 1)
**Goal**: Identify and merge duplicate positions

**Method**:
1. Generate embeddings for all 124 positions (insight field)
2. Compute pairwise similarity matrix
3. Flag pairs with >0.85 similarity for human review
4. Generate merge proposals (keep canonical, archive duplicate)

**Output**: `N5/review/positions/deduplication-review.md`

**Decision Points**:
- Merge threshold (0.85? 0.90?)
- Which position to keep when merging (older? more evidence? manual choice?)

---

### Phase 2: Domain Audit
**Goal**: Ensure every position is in the correct domain

**Method**:
1. Already generated: `domain-review.md` with 31 flagged positions
2. Human reviews each flag: confirm or reassign domain
3. Apply corrections to positions.db

**Output**: Updated positions.db with correct domains

---

### Phase 3: Quality Gate for B32 Extractions
**Goal**: Validate that the 80 B32-extracted positions deserve to be positions

**Method**:
1. Generate review queue of all B32 extractions
2. For each, human decides: 
   - ✅ Confirm (this is a real position I hold)
   - 🔀 Merge (this is a fragment of another position)
   - ❌ Demote (this is noise, move to archive)
3. Apply decisions

**Output**: Cleaned positions.db with only validated positions

---

### Phase 4: Connection Enrichment (Return to Original Plan)
**Goal**: Now that the foundation is solid, add meaningful connections

**Method**:
1. Use embedding similarity as pre-filter (only propose connections for pairs with >0.5 similarity)
2. Use LLM reasoning to propose specific relationship types
3. Apply utility-first pruning (only keep connections that imply intellectual dependency)
4. Human reviews connection proposals
5. Apply approved connections

**Output**: Rich, validated connection graph

---

## Utility-First Pruning Rules (Refinement 3)

Only propose connections where the relationship implies **intellectual dependency**:

| Relationship | Keep? | Reasoning |
|--------------|-------|-----------|
| `implies` | ✅ | If A is true, B must be true |
| `contradicts` | ✅ | A and B cannot both be true |
| `prerequisite` | ✅ | Must understand A before B |
| `extends` | ✅ | B builds on A |
| `supports` | ✅ | Evidence for A strengthens B |
| `related_to` | ❌ | Too weak, adds noise |
| `similar_to` | ❌ | Embedding already captures this |

---

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Positions with connections | 22 (18%) | >60% |
| Duplicate rate | Unknown | <5% |
| Domain accuracy | ~75% (est.) | >95% |
| B32 quality (confirmed) | 0% | 100% reviewed |
| Orphan positions | 102 | <30 |

---

## Sequencing

```
Phase 0 (Fix Pipeline) ──┐
                         ├──► Phase 1 (Dedupe) ──► Phase 2 (Domain) ──► Phase 3 (Quality) ──► Phase 4 (Connect)
Current conversation ────┘
```

Phase 0 and 1 can start immediately in this conversation.
Phase 2-4 can be spread across multiple conversations using build orchestrator.

---

## Estimated Effort

| Phase | AI Work | Human Review | Spread Across |
|-------|---------|--------------|---------------|
| Phase 0 | 30 min | 15 min | This conversation |
| Phase 1 | 20 min | 30 min | This conversation |
| Phase 2 | 10 min | 45 min | 1-2 conversations |
| Phase 3 | 15 min | 2 hours | 2-3 conversations |
| Phase 4 | 1 hour | 1 hour | 1-2 conversations |

---

## Parking Lot (Deferred)

- Temporal tracking of position evolution
- Confidence decay over time
- Auto-connection from new B32 extractions (post-Phase 4 automation)


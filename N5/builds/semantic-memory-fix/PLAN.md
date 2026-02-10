---
created: 2026-02-09
last_edited: 2026-02-09
version: 1.0
provenance: con_NhzJGKzQlSxmOBXT
---

# Semantic Memory System — Performance & Quality Fix

## Objective

Fix 8 bugs discovered in the semantic memory system during a debug audit. The system currently has catastrophic search performance (11-14s per query), 25.9% stale data, disabled quality features, and data integrity issues. This build resolves all fixable issues in a single coordinated effort.

## Open Questions

- [x] Is there a single embedding model in vectors_v2.db? → Yes, all 3072-dim (OpenAI)
- [x] Does the reranker work? → Yes, FlashRank works and dramatically improves quality
- [x] Is hnswlib installable? → Yes, dry-run confirmed
- [ ] Should we migrate brain.db vectors to vectors_v2.db? → Deferred (BUG-5, not in scope)

## Phase 1: Foundation Fixes (Wave 1, Parallel)

Three independent fixes that have no interdependencies:

### D1.1: Install hnswlib + Rebuild ANN Index
**Impact**: 100x search speedup (11-14s → <200ms)
- Install hnswlib pip package
- Rebuild HNSW index for all 190K vectors
- Verify ANN fast path activates

### D1.2: Purge Stale & Orphaned Data
**Impact**: Remove 25.9% dead weight from index
- Backup both databases
- Purge 2,504 stale resources from vectors_v2.db
- Clean orphaned resources/blocks from both DBs
- VACUUM databases

### D1.3: Fix Provider Init Order
**Impact**: ~2s faster startup
- Restructure `_init_provider()` to check vector dimensions before loading local model
- Eliminate unnecessary SentenceTransformer load

## Phase 2: Quality & Coverage (Wave 2, Parallel after W1)

### D2.1: Enable Reranker + Fix Context Loading
**Depends on**: D1.1, D1.2
**Impact**: Dramatically better search quality
- Change `search()` default to `use_reranker=True`
- Update `n5_load_context.py` to use reranker with optimized top_k
- Verify no existing callers broken

### D2.2: Index Documents/ + Fix Chunk Overlap
**Depends on**: D1.2
**Impact**: 43% → >90% Documents/ coverage; better chunk boundaries
- Implement the unused overlap parameter in `_chunk_content_markdown()`
- Index ~217 unindexed .md files in Documents/

## Phase 3: Verification (Wave 3, Sequential after W2)

### D3.1: End-to-End Verification & Benchmark
**Depends on**: D2.1, D2.2
- Run comprehensive test suite across all 8 bugs
- Benchmark search latency, data integrity, coverage, quality
- Produce final health report

## Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| Search latency | 11-14s | <1s |
| Stale resources | 25.9% | <2% |
| Orphaned data | 574+ entries | 0 |
| Reranker active | No | Yes |
| Init time | ~5s | ~3s |
| Documents/ coverage | 43% | >85% |
| Chunk overlap | Broken | Working |

## Deferred (Out of Scope)

**BUG-5: Dual-database confusion** — The hybrid_search() and graph functions use brittle path replacement between vectors_v2.db and brain.db. This needs architectural discussion about whether to consolidate into one DB. Deferred to a separate planning session.

## Architecture Notes

- All vectors in vectors_v2.db are 3072-dim (OpenAI text-embedding-3-large) — no dimension mismatch
- The old brain.db dimension mismatch (384 + 3072) was already handled with a skip-and-warn
- Graph store (entities + relationships in brain.db) is healthy and should not be touched
- ANN index uses hnswlib HNSW algorithm with cosine similarity space

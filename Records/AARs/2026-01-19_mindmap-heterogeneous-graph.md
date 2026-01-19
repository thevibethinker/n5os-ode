---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_sb951PA0ftN0Uu9w
type: aar
status: in_progress
---

# AAR: Mind Map Heterogeneous Graph Migration

**Date:** 2026-01-19  
**Thread:** con_sb951PA0ftN0Uu9w  
**Status:** 🚧 In Progress (70%)

---

## Summary

Ilse provided feedback that the mind map's current thought→thought graph architecture won't scale (N² comparison problem) and lacks queryable concept abstractions. This conversation:

1. **Teacher** explained heterogeneous graphs — using concept nodes as intermediaries reduces edge complexity from O(N²) to O(N×C)
2. **Architect** designed a parallel experiment approach (not migration) to de-risk
3. **Builder** executed a working prototype: 20 concepts, 249 edges, 91% coverage
4. **Migrated to production** — data layer complete, visualization updated
5. **Hit physics blocker** — concepts cluster instead of distributing as hubs
6. **Reverted production** — spawned focused physics worker (W2.1)

---

## What Worked

| Item | Why |
|------|-----|
| Parallel experiment approach | Validated architecture without breaking production |
| Pattern-based concept extraction | Fast, deterministic, 91% coverage without LLM costs |
| Teacher→Architect→Builder flow | Clean handoffs, each persona did their job |
| Prototype-first validation | Caught physics issues before full migration |

---

## What Didn't Work

| Item | Why | Lesson |
|------|-----|--------|
| react-force-graph-2d physics | Library's force config doesn't easily support heterogeneous hub distribution | May need raw D3 or different library |
| Rushing to production | Migrated before physics were solid | Validate visualization fully in prototype first |
| Multiple force adjustments | Each fix made it worse | Stop, research properly, then implement |

---

## Key Learnings

1. **Heterogeneous graphs beat homogeneous for knowledge systems** — Concept nodes as hubs make structure legible and queryable
2. **react-force-graph-2d has limitations** — Good for simple graphs, but heterogeneous layouts need more control
3. **The prototype worked because it used raw D3** — Full control over force simulation
4. **Reversion was correct** — Better to pause and fix properly than ship broken UX

---

## Artifacts Created

| Artifact | Location | Status |
|----------|----------|--------|
| Concept extraction pipeline | `N5/builds/concept-graph-experiment/extract_concepts.py` | ✅ Complete |
| Graph transformation | `N5/builds/concept-graph-experiment/build_graph.py` | ✅ Complete |
| Working prototype visualizer | `N5/builds/concept-graph-experiment/visualizer/` | ✅ Complete |
| Production data endpoint | `Sites/vrijenattawar/server.ts` → `/api/concept-graph` | ✅ Complete |
| Production visualization | `Sites/vrijenattawar/src/pages/MindMap.tsx` | ⚠️ Reverted |
| Worker briefs | `N5/builds/mindmap-concept-migration/workers/` | ✅ 4 briefs |

---

## Open Items

| Item | Owner | Status |
|------|-------|--------|
| W2.1: Physics redo | Worker | 🔲 Pending |
| W1.2: Interface polish | Worker | ⏸️ On hold |
| W1.3: Edge-to-edge layout | Worker | ⏸️ On hold |
| Git commit (all changes) | Orchestrator | ⏸️ After workers complete |

---

## Metrics

- **Concepts extracted:** 20
- **Thought-concept edges:** 249
- **Coverage:** 91% (11 orphans)
- **Cross-domain bridges:** 5 concepts span multiple domains
- **Production status:** Reverted (physics issue)

---

## Next Steps

1. Run W2.1 physics worker — fix force layout so concepts distribute as hubs
2. If W2.1 succeeds, run W1.2 and W1.3 in parallel
3. Validate in staging before re-deploying to production
4. Atomic commit after all workers complete

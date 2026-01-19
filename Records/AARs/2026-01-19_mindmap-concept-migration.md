---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_sb951PA0ftN0Uu9w
type: aar
build_slug: mindmap-concept-migration
status: in_progress
---

# AAR: Mind Map Heterogeneous Graph Migration

**Date:** 2026-01-19
**Conversation:** con_sb951PA0ftN0Uu9w
**Status:** 🚧 In Progress (orchestrator spawned, workers pending)

---

## What Happened

Ilse provided architectural feedback on V's mind map (vrijenattawar.com/mind): the current homogeneous thought→thought graph has N² scaling problems and lacks queryable concept abstractions. V wanted to understand this feedback deeply and implement the recommended architecture.

### Journey

1. **Teacher Phase** — Explained heterogeneous graphs: two node types (thoughts and concepts), concepts as intermediary hubs, sparse matrices vs dense matrices, O(N×C) vs O(N²) scaling
2. **Experiment Phase** — Built standalone prototype at `N5/builds/concept-graph-experiment/` with 20 extracted concepts, 249 edges, 91% thought coverage
3. **Migration Phase** — Integrated into production site: new `/api/concept-graph` endpoint, updated `MindMap.tsx` with dual-type rendering (circles for thoughts, diamonds for concepts)
4. **Orchestration Phase** — Physics and layout issues remain; spawned 3 parallel workers for focused fixes

---

## What Worked

| What | Why It Worked |
|------|---------------|
| Parallel experiment first | De-risked migration; proved architecture before touching production |
| Pattern-based concept extraction | Fast, deterministic, no API costs; produced 20 meaningful concepts |
| Teacher → Architect → Builder flow | Each persona focused; clean handoffs |
| Visual differentiation (circles vs diamonds) | Immediately legible which nodes are concepts |

---

## What Didn't Work

| What | Root Cause | Fix |
|------|------------|-----|
| Physics clustering | react-force-graph-2d's d3-force integration doesn't easily support heterogeneous node forces; concepts cluster instead of distributing | Worker W1.1 to tune |
| Edge-to-edge layout | Dimension calculations not accounting for sidebars properly | Worker W1.3 to fix |
| "undefined" domain appearing | Concepts don't have domains; filter wasn't excluding them | Fixed mid-session |

---

## Key Decisions

1. **Parallel experiment, not direct migration** — V explicitly requested this to avoid breaking production
2. **Keep chat and guided paths** — Existing features preserved, defer enhancement
3. **3 parallel workers** — Physics (W1.1), Interface (W1.2), Frame (W1.3) for focused execution

---

## Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| Concept extraction script | `N5/builds/concept-graph-experiment/extract_concepts.py` | Extracts concepts from positions |
| Graph transformer | `N5/builds/concept-graph-experiment/build_graph.py` | Builds heterogeneous graph JSON |
| Standalone visualizer | `N5/builds/concept-graph-experiment/visualizer/` | Proof of concept |
| Concept graph data | `Sites/vrijenattawar/data/concept-graph.json` | Production data |
| Generation script | `Sites/vrijenattawar/scripts/generate-concept-graph.py` | Regenerates concept graph |
| Worker briefs | `N5/builds/mindmap-concept-migration/workers/W1.*.md` | 3 parallel worker briefs |
| Build orchestration | `N5/builds/mindmap-concept-migration/BUILD.md` | Orchestrator tracking |

---

## Open Items

- [ ] **W1.1** — Physics tuning (concepts as distributed hubs)
- [ ] **W1.2** — Interface polish (concept panel, filters, visual refinement)
- [ ] **W1.3** — Edge-to-edge layout (fill viewport between sidebars)
- [ ] Commit all changes after workers complete
- [ ] Manual concept tagging for 11 orphan thoughts

---

## Learnings for Future

1. **Heterogeneous graph physics are non-trivial** — Libraries like react-force-graph-2d assume homogeneous nodes; custom force functions required for hub-spoke layouts
2. **Ilse's N² warning was correct** — Current 164 thoughts × 164 thoughts = 26,896 potential edges; with 20 concepts it's 164 × 20 = 3,280 — an 8× reduction
3. **"Information Asymmetry" bridges 3 domains** — This concept connects hiring-market, careerspan, and worldview; a cross-cutting theme that wasn't visible in the original structure

---

## Metrics

| Metric | Value |
|--------|-------|
| Concepts extracted | 20 |
| Thought→concept edges | 249 |
| Thought coverage | 91% (11 orphans) |
| Avg concepts per thought | 2.0 |
| Top concept | AI Commoditization (48 thoughts) |
| Cross-domain bridges | 5 concepts span multiple domains |

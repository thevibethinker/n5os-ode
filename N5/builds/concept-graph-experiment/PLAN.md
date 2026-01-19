---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: draft
provenance: con_sb951PA0ftN0Uu9w
---

# Plan: Concept Graph Experiment — Heterogeneous Node Architecture

**Objective:** Build a parallel experiment that transforms V's existing mind map (164 positions, homogeneous thought→thought connections) into a heterogeneous graph with two node types: **Thoughts** and **Concepts**. This validates Ilse's architectural recommendation before modifying the production system.

**Trigger:** Ilse's feedback that the current architecture won't scale (N² comparison problem) and lacks queryable concept abstractions.

**Key Design Principle:** Parallel experiment, not migration. The existing mind map (`vrijenattawar.com/mind`) stays untouched. We build a new data pipeline + visualizer to prove the concept.

---

## Open Questions

- [x] **Where is the data?** → `N5/builds/position-viz/positions_triples.json` (current triples), `N5/builds/position-system-overhaul/positions_export.json` (full positions with insights)
- [ ] **Concept extraction strategy:** LLM-based extraction from insight text, or pattern-based extraction from relationship predicates? (Recommendation: Start with predicate patterns + title keywords, then optionally LLM-enrich)
- [ ] **Concept granularity:** How many concepts is ideal? 20-30 feels navigable; 100+ becomes unwieldy.

---

## Architecture: Before vs After

### Current (Homogeneous)
```
Thought A ──"supports"──→ Thought B
Thought A ──"extends"───→ Thought C
Thought B ──"implies"───→ Thought C
```
- All nodes are the same type
- Relationship labels on edges
- N² scaling problem for connections

### Proposed (Heterogeneous)
```
Thought A ──→ [CONCEPT: Signal Decay] ←── Thought B
                     │
                     ↓
              [CONCEPT: Friction]
                     │
                     ↓
             Thought C, Thought D
```
- Two node types: Thoughts (your 164 positions) and Concepts (extracted abstractions)
- Thoughts connect TO concepts, not directly to each other
- Concepts become navigable entry points
- Scales as O(N × C) where C << N

---

## Checklist

### Phase 1: Concept Extraction Pipeline
- [x] 1.1 Load existing positions data from `positions_export.json`
- [x] 1.2 Extract concepts from relationship predicates (supports, extends, implies → concept patterns)
- [x] 1.3 Extract concepts from position titles (keyword/phrase extraction)
- [x] 1.4 Deduplicate and normalize concepts (fuzzy match similar concepts)
- [x] 1.5 Output: `concepts.json` with ~20-40 distinct concepts
- [x] 1.6 Output: `thought_concept_edges.json` mapping each thought to its concepts

### Phase 2: Graph Data Transformation
- [x] 2.1 Generate heterogeneous graph JSON with two node types
- [x] 2.2 Add metadata: node_type (thought/concept), domain, stability, confidence
- [x] 2.3 Compute concept statistics: how many thoughts per concept, cross-domain bridges
- [x] 2.4 Output: `concept_graph.json` (nodes + edges for visualization)

### Phase 3: Local Visualizer Prototype
- [x] 3.1 Create simple HTML + D3.js/vis.js visualizer
- [x] 3.2 Visual differentiation: Thoughts as circles, Concepts as diamonds/squares
- [x] 3.3 Color coding: Concepts in gold/yellow, Thoughts by domain
- [x] 3.4 Click on concept → highlight all connected thoughts
- [x] 3.5 Click on thought → show its concepts in sidebar
- [x] 3.6 Serve locally for V to validate

---

## Phase 1: Concept Extraction Pipeline

### Affected Files
- `N5/builds/concept-graph-experiment/extract_concepts.py` — CREATE
- `N5/builds/concept-graph-experiment/data/concepts.json` — CREATE
- `N5/builds/concept-graph-experiment/data/thought_concept_edges.json` — CREATE

### Changes

**1.1-1.2 Extraction Strategy (Pattern-Based First)**

Extract concepts from:
1. **Relationship predicates** → Group thoughts by what they support/extend/imply
2. **Title keywords** → Common themes: "signal", "friction", "trust", "self-knowledge", "hiring"
3. **Domain bridging** → Thoughts that appear in multiple domains hint at cross-cutting concepts

**1.3-1.4 Normalization**
- Lowercase, stem similar terms
- Merge "self-knowledge" and "self-awareness"
- Target: 20-40 distinct concepts

**1.5-1.6 Output Schema**

```json
// concepts.json
{
  "concepts": [
    {
      "id": "signal-decay",
      "label": "Signal Decay",
      "description": "The degradation of meaningful information in systems",
      "thought_count": 12
    }
  ]
}

// thought_concept_edges.json
{
  "edges": [
    {
      "thought_id": "hiring-signal-collapse",
      "concept_id": "signal-decay",
      "strength": 0.9
    }
  ]
}
```

### Unit Tests
- `python3 extract_concepts.py --dry-run` → Prints top 10 extracted concepts
- Concept count between 20-50
- Every thought has at least 1 concept

---

## Phase 2: Graph Data Transformation

### Affected Files
- `N5/builds/concept-graph-experiment/build_graph.py` — CREATE
- `N5/builds/concept-graph-experiment/data/concept_graph.json` — CREATE

### Changes

**2.1 Heterogeneous Graph Structure**

```json
{
  "nodes": [
    {"id": "t:hiring-signal-collapse", "type": "thought", "label": "Hiring Signal Collapse", "domain": "hiring-market", "stability": "canonical", "confidence": 8},
    {"id": "c:signal-decay", "type": "concept", "label": "Signal Decay", "thought_count": 12}
  ],
  "edges": [
    {"source": "t:hiring-signal-collapse", "target": "c:signal-decay", "type": "embodies"}
  ]
}
```

**2.2-2.3 Computed Statistics**
- Concept centrality (which concepts connect most thoughts)
- Domain bridges (concepts that span multiple domains)
- Orphan detection (thoughts with no concepts → needs manual tagging)

### Unit Tests
- Graph has two distinct node types
- No direct thought→thought edges (all go through concepts)
- Every thought connects to at least one concept

---

## Phase 3: Local Visualizer Prototype

### Affected Files
- `N5/builds/concept-graph-experiment/visualizer/index.html` — CREATE
- `N5/builds/concept-graph-experiment/visualizer/graph.js` — CREATE
- `N5/builds/concept-graph-experiment/visualizer/styles.css` — CREATE
- `N5/builds/concept-graph-experiment/serve.sh` — CREATE

### Changes

**3.1-3.2 Visual Differentiation**

| Node Type | Shape | Size | Color |
|-----------|-------|------|-------|
| Thought | Circle | Small (by confidence) | Domain color |
| Concept | Diamond | Large (by thought_count) | Gold/amber |

**3.3-3.5 Interaction**
- Hover concept → Highlight connected thoughts
- Click concept → Sidebar lists all connected thoughts
- Click thought → Sidebar shows concepts + insight preview

**3.6 Serving**
```bash
# serve.sh
cd N5/builds/concept-graph-experiment/visualizer
python3 -m http.server 8890
```

### Unit Tests
- Visual: Open in browser, see two distinct node shapes
- Functional: Click a concept, connected thoughts highlight

---

## Success Criteria

1. **Concept extraction works:** 20-40 meaningful concepts extracted from 164 thoughts
2. **Graph transforms correctly:** Every thought connects to ≥1 concept; no direct thought→thought edges
3. **Visualizer demonstrates value:** V can click a concept and see all related thoughts (validates Ilse's "queryable concepts" point)
4. **Insights surfaced:** At least 2-3 "aha" moments where concept view reveals connections V hadn't noticed

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Concept extraction too noisy | Start with predicate patterns (high signal), add LLM only if needed |
| Too many concepts (>50) | Merge aggressively; target human-navigable count |
| Visualizer too complex | Use existing vis.js library (same as position-viz build) |
| Experiment scope creeps | This is a **prototype**, not production. No database changes. |

---

## Alternative Approaches Considered (Nemawashi)

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **A: Pattern-based extraction** | Fast, deterministic, no API costs | May miss nuanced concepts | ✅ Start here |
| **B: LLM extraction** | Can understand semantic meaning | Expensive, slower, needs prompt tuning | ⏸️ Optional Phase 1.5 |
| **C: Manual tagging** | Highest quality | Time-consuming, doesn't scale | ❌ Not for v1 |

---

## Execution Notes

- This is a **single-worker build** (no need for MECE validation)
- Can be executed by Builder in one session
- No production systems affected
- Output is a standalone prototype in `N5/builds/concept-graph-experiment/`

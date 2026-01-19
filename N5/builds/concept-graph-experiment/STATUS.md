---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_sb951PA0ftN0Uu9w
---

# Build Status: concept-graph-experiment

## Current Status: ✅ COMPLETE

**Progress:** 16/16 (100%)

---

## Phase Summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Concept Extraction | ✅ Complete | 20 concepts, 249 edges, 91% coverage |
| Phase 2: Graph Transformation | ✅ Complete | Heterogeneous graph built, no T→T edges |
| Phase 3: Visualizer Prototype | ✅ Complete | D3.js visualizer with interactive features |

---

## Results

### Extraction Results
- **Concepts extracted:** 20 (target was 20-40) ✓
- **Thought-concept edges:** 249
- **Coverage:** 91% (11 orphan thoughts)
- **Average concepts per thought:** 2.0

### Top Concepts (by connectivity)
1. AI Commoditization: 48 thoughts
2. Information Asymmetry: 26 thoughts
3. Problem Stack Elevation: 19 thoughts
4. Anthropomorphic Engagement: 19 thoughts
5. Signal Decay: 16 thoughts

### Cross-Domain Bridges (concepts spanning multiple domains)
- AI Commoditization: ai-automation ↔ hiring-market
- Information Asymmetry: hiring-market ↔ careerspan ↔ worldview
- Anthropomorphic Engagement: ai-automation ↔ worldview
- Signal Decay: hiring-market ↔ ai-automation
- Assessment Validity: hiring-market ↔ epistemology

### Validation
- ✓ No direct thought→thought edges
- ✓ 20 concept nodes (human-navigable)
- ⚠ 11 orphan thoughts need manual concept tagging

---

## Artifacts

| File | Description |
|------|-------------|
| `extract_concepts.py` | Concept extraction pipeline |
| `build_graph.py` | Graph transformation script |
| `data/concepts.json` | 20 extracted concepts |
| `data/thought_concept_edges.json` | 249 thought→concept edges |
| `data/concept_graph.json` | Full heterogeneous graph |
| `visualizer/index.html` | D3.js visualizer |
| `visualizer/graph.js` | Graph rendering logic |
| `visualizer/styles.css` | Visual styling |
| `serve.sh` | Local server script |

---

## Access

**Live Preview:** http://p1.proxy.zo.computer:46696

**Local:** `bash N5/builds/concept-graph-experiment/serve.sh`

---

## Next Steps (if validated)

1. Manual tagging for 11 orphan thoughts
2. Consider LLM enrichment for concept descriptions
3. If this architecture proves valuable → integrate into production mind map

---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
type: build_plan
status: draft
provenance: con_sb951PA0ftN0Uu9w
---

# Plan: Mind Map — Migrate to Heterogeneous Concept Graph Architecture

**Objective:** Migrate the production mind map (vrijenattawar.com/mind) from homogeneous thought→thought connections to heterogeneous Thought + Concept node architecture, with improved visualization physics while preserving the current visual styling.

**Source of Truth:**
- Current production site: `Sites/vrijenattawar/`
- Experiment that validated architecture: `N5/builds/concept-graph-experiment/`
- Live proof of concept: http://p1.proxy.zo.computer:24701

---

## Open Questions

1. ~~**Do we need to preserve chat functionality?**~~ → ✅ Keep as-is (searches thoughts only)
2. ~~**What about guided paths feature?**~~ → ✅ Keep as-is, defer enhancement to later

---

## Trap Doors ⚠️

| Decision | Reversibility | Risk | Mitigation |
|----------|---------------|------|------------|
| Adding `type` field to nodes | ✅ Reversible | Low | Backward compatible |
| Changing graph physics params | ✅ Reversible | Low | Can tune post-deploy |
| Replacing visualization library | ⚠️ Medium | Medium | Keep react-force-graph-2d, just reconfigure |
| Data schema change (concept nodes) | ⚠️ Medium | Medium | API returns both formats during transition |

---

## Checklist

### Phase 1: Data Layer (Backend)
- [ ] 1.1 Create concept extraction endpoint or build-time generation
- [ ] 1.2 Update `/api/positions` to return heterogeneous graph (nodes + concepts)
- [ ] 1.3 Add `type: "thought" | "concept"` field to all nodes
- [ ] 1.4 Ensure backward compatibility (old format still works)

### Phase 2: Visualization Layer (Frontend)
- [ ] 2.1 Update `MindMap.tsx` to handle two node types
- [ ] 2.2 Implement concept node rendering (diamond shape, gold color)
- [ ] 2.3 Port improved physics settings from experiment
- [ ] 2.4 Adjust force simulation for concept-hub layout

### Phase 3: Visual Styling Alignment
- [ ] 3.1 Apply existing DOMAIN_COLORS to thought nodes
- [ ] 3.2 Apply gold/amber styling to concept nodes  
- [ ] 3.3 Preserve existing detail panel styling
- [ ] 3.4 Update legend to show both node types

### Phase 4: Testing & Deploy
- [ ] 4.1 Test on staging (vrijenattawar-staging)
- [ ] 4.2 Verify all existing features still work
- [ ] 4.3 Deploy to production
- [ ] 4.4 Verify live at vrijenattawar.com/mind

---

## Phase Details

### Phase 1: Data Layer

**Affected Files:**
- `Sites/vrijenattawar/server.ts` — Add/update positions API
- `Sites/vrijenattawar/data/positions-snapshot.json` — May need regeneration
- NEW: `Sites/vrijenattawar/data/concept-graph.json` — Heterogeneous graph data

**Changes:**
1. Copy concept extraction logic from `N5/builds/concept-graph-experiment/extract_concepts.py`
2. Either:
   - **Option A:** Build-time generation (run script, commit JSON) — simpler
   - **Option B:** Runtime endpoint — more complex but dynamic
3. Recommend **Option A** for v1

**Output Schema:**
```typescript
interface GraphData {
  nodes: Array<{
    id: string;
    type: "thought" | "concept";
    // Thought-specific
    domain?: string;
    title: string;
    insight?: string;
    stability?: string;
    confidence?: number;
    // Concept-specific  
    thought_count?: number;
    domains?: string[];
    description?: string;
  }>;
  links: Array<{
    source: string;
    target: string;
    relationship?: string;
  }>;
}
```

**Unit Tests:**
- Verify API returns both node types
- Verify all thoughts have `type: "thought"`
- Verify all concepts have `type: "concept"`

### Phase 2: Visualization Layer

**Affected Files:**
- `Sites/vrijenattawar/src/pages/MindMap.tsx` — Main visualization

**Changes:**
1. Update `nodeCanvasObject` to render:
   - Circles for thoughts (current behavior)
   - Diamonds for concepts (new)
2. Port physics from experiment:
   ```javascript
   // From experiment - better clustering
   d3ForceCollide(node => node.type === 'concept' ? 35 : 15)
   d3ForceManyBody().strength(node => node.type === 'concept' ? -300 : -80)
   d3ForceLink().distance(link => 80)
   ```
3. Adjust node sizing:
   - Concepts: larger, based on `thought_count`
   - Thoughts: current sizing logic

**Unit Tests:**
- Verify concepts render as diamonds
- Verify thoughts render as circles
- Verify clicking concept highlights connected thoughts

### Phase 3: Visual Styling

**Affected Files:**
- `Sites/vrijenattawar/src/pages/MindMap.tsx` — Colors, styling
- `Sites/vrijenattawar/src/components/mindmap/MindMapLegend.tsx` — Legend update

**Changes:**
1. Concept color: `#fbbf24` (amber-400) — matches experiment
2. Thought colors: Keep existing `DOMAIN_COLORS` 
3. Edge colors: Muted for thought→concept, more visible for highlighted
4. Legend: Add "Concept" entry with diamond icon

### Phase 4: Testing & Deploy

**Staging Validation:**
1. Run on `vrijenattawar-staging` (port 52126 if exists, else create)
2. Manual testing:
   - [ ] Graph loads with both node types
   - [ ] Clicking concept shows related thoughts
   - [ ] Clicking thought shows its concepts
   - [ ] Domain filter still works
   - [ ] Search still works
   - [ ] Chat still works
   - [ ] Mobile view works

**Deploy:**
```bash
cd Sites/vrijenattawar
bun run build
# Service auto-restarts
```

---

## Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **A: Modify existing MindMap.tsx** | Minimal disruption, preserves features | Adds complexity to already large file | ✅ Selected |
| **B: New page /mind-v2** | Safe parallel development | Duplicate code, confusing UX | ❌ Rejected |
| **C: Replace with pure D3** | Full control | Loses react-force-graph features, more work | ❌ Rejected |

---

## Success Criteria

1. ✅ Graph displays 20 concept nodes + 124 thought nodes
2. ✅ Concepts visually distinct (gold diamonds)
3. ✅ Clicking concept highlights all connected thoughts
4. ✅ Physics feels better (less chaotic, more clustered)
5. ✅ All existing features preserved (search, filter, chat, mobile)
6. ✅ No visual regression on thought node styling

---

## Execution Notes

- **Single worker build** — can execute in one session
- Work in staging first, then promote
- Keep experiment at `/N5/builds/concept-graph-experiment/` as reference
- This is a MEDIUM-risk change (production site, but isolated to /mind route)

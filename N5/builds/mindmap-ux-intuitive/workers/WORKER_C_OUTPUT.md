---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_DDVTnqBitsQiKRWC
---

# WORKER C OUTPUT: Polish & Guided Paths

**Status:** ✅ Complete  
**Build verified:** Production build successful

---

## 1. Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/lib/graphAnimations.ts` | Animation config + highlight style utilities | ~140 |
| `src/lib/graphPaths.ts` | Path computation algorithms | ~280 |
| `src/components/mindmap/MindMapGuidedPaths.tsx` | Guided paths UI component | ~210 |
| `src/components/mindmap/index.ts` | Updated barrel export | 12 |

---

## 2. Path Computation Algorithm

The `computeGuidedPaths()` function uses a multi-step approach:

### Seed Node Selection
1. Score all nodes by "importance" combining:
   - Connection count (capped at 20 to avoid over-weighting mega-hubs)
   - Stability bonus (canonical: 30, stable: 20, hardening: 12, etc.)
   - Confidence multiplier (confidence × 1.5)
2. Sort by importance descending
3. Take top 15 candidates, filtering out neighbors of already-used starts

### Chain Discovery
For each seed node, `findLongestChain()` runs a depth-first search:
- Prefers **strong** and **medium** relationships over weak
- Explores top 3 neighbors per node (prevents combinatorial explosion)
- Returns the longest discovered path

### Path Scoring
Each candidate path is scored on:
- **Length bonus:** Sweet spot is 4-7 nodes (+20 points)
- **Domain diversity:** More domains = higher score (+5 per domain, max 25)
- **High-confidence nodes:** Canonical (+8) or confidence ≥8 (+4) each
- **Edge strength:** Strong edges (+5), medium (+2)

### Deduplication
Paths with >60% node overlap with already-selected paths are filtered out.

### Output
Returns top 3 paths sorted by score, each with:
- Auto-generated name (first node keyword → last node keyword)
- Auto-generated description (node count + domain span)

---

## 3. Animation Specs

### Configuration Constants

```ts
ANIMATION_CONFIG = {
  focusTransition: { duration: 300, easing: 'ease-out' },
  highlightFade: { duration: 200 },
  pathStep: { delay: 150 },  // between highlighting each path node
  hoverTransition: { duration: 150 },
}
```

### Highlight State Logic

| State | Opacity | Scale | Glow | Z-Index |
|-------|---------|-------|------|---------|
| Selected | 1.0 | 1.15 | ✅ | 50 |
| In Active Path | 1.0 | 1.05 | ❌ | 40 |
| Neighbor of Selection | 0.9 | 1.0 | ❌ | 30 |
| Default | 1.0 | 1.0 | ❌ | 10 |
| Dimmed (not in path/neighborhood) | 0.15-0.25 | 1.0 | ❌ | 1 |

### Glow Effect
Subtle double drop-shadow for selected nodes:
```ts
filter: drop-shadow(0 0 8px ${color}50) drop-shadow(0 0 16px ${color}30)
```

### Reduced Motion Support
- All animation functions accept/check `prefersReducedMotion`
- When true, durations → 0, delays → 0
- CSS transitions return `"none"` for instant state changes

---

## 4. Integration Notes

### MindMap.tsx Integration (for Orchestrator/Builder)

The guided paths component is ready to integrate. Required state additions:

```tsx
// In MindMap.tsx parent
const [activePath, setActivePath] = useState<GuidedPath | null>(null);
const [activePathStep, setActivePathStep] = useState(-1);

// Derive visible path nodes (up to current step)
const visiblePathNodeIds = useMemo(() => {
  if (!activePath || activePathStep < 0) return [];
  return activePath.nodeIds.slice(0, activePathStep + 1);
}, [activePath, activePathStep]);
```

Add to right rail (after Cornerstones):

```tsx
<MindMapGuidedPaths
  positions={positions}
  links={links}
  onSelectPath={setActivePath}
  activePath={activePath}
  activePathStep={activePathStep}
  onStepPath={setActivePathStep}
/>
```

### Node Rendering Badge
Use `getPathNodeBadge()` to show step numbers on path nodes:

```tsx
import { getPathNodeBadge } from "@/components/mindmap";

// In node render:
const badge = getPathNodeBadge(node.id, visiblePathNodeIds);
{badge.show && (
  <div className="absolute -top-1 -right-1 size-4 rounded-full bg-indigo-500 text-white text-[10px] flex items-center justify-center font-medium">
    {badge.step}
  </div>
)}
```

### Edge Opacity Integration
Use `getEdgeHighlightOpacity()` from graphAnimations.ts when rendering edges:

```tsx
const edgeOpacity = getEdgeHighlightOpacity(
  sourceId,
  targetId,
  selectedId,
  neighborIds,
  visiblePathNodeIds,
  baseOpacity
);
```

---

## 5. Constraints Met

- ✅ Did NOT modify `MindMap.tsx`
- ✅ No heavy animation libraries (pure CSS transitions)
- ✅ Animations under 300ms
- ✅ Reduced-motion users get instant transitions
- ✅ Glow is subtle, not garish

---

## 6. Visual Preview

The guided paths panel features:
- Indigo accent color (distinct from amber Cornerstones)
- Path cards showing node count badge + auto-generated name
- Active path shows progress bar with clickable steps
- Play/pause auto-advance through path
- Clear button to exit path mode

---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_pkCTQbeytKEN0xFK
---

# WORKER B OUTPUT: Meaning & Through-Lines Components

**Status:** ✅ Complete  
**Build verified:** Yes (compiles successfully)

## Files Created

| File | Purpose |
|------|---------|
| `Sites/vrijenattawar-staging/src/lib/graphHighlight.ts` | Pure utility functions for neighborhood computation and cornerstone selection |
| `Sites/vrijenattawar-staging/src/components/mindmap/MindMapLegend.tsx` | Collapsible legend explaining visual encoding |
| `Sites/vrijenattawar-staging/src/components/mindmap/MindMapCornerstones.tsx` | Pinned cornerstone positions with domain dots |
| `Sites/vrijenattawar-staging/src/components/mindmap/index.ts` | Updated barrel export |

## Component Interfaces

### MindMapLegend

```tsx
interface MindMapLegendProps {
  isExpanded: boolean;
  onToggle: () => void;
}
```

**Features:**
- Compact toggle button with info icon
- Expandable panel with smooth animation
- Three sections: Edge Strength, Domains (2-column grid), Stability gradient
- Hover tooltips on stability bars
- Dark theme with zinc/amber accents

### MindMapCornerstones

```tsx
interface MindMapCornerstonesProps {
  positions: Position[];
  links: Link[];
  onSelectPosition: (id: string) => void;
  selectedId: string | null;
  maxCount?: number;  // defaults to 7
}
```

**Features:**
- Uses `computeCornerstones()` from graphHighlight.ts
- Domain-colored dots next to each title
- Selected state highlight (amber)
- "core" badge for canonical positions
- 2-line title truncation

### graphHighlight.ts Utilities

```ts
// Get all nodes within N hops of a node
export function getNeighborhood(
  nodeId: string, 
  links: Link[], 
  depth: 1 | 2
): { nodeIds: Set<string>; linkIndices: Set<number> };

// Compute cornerstone positions
export function computeCornerstones(
  positions: Position[], 
  links: Link[], 
  maxCount?: number
): Position[];

// Classify edge strength tier
export function getRelationshipStrength(
  relationship: string
): "strong" | "medium" | "weak";

// Check if node has no connections
export function isOrphanNode(nodeId: string, links: Link[]): boolean;
```

## Cornerstone Algorithm

The cornerstone selection algorithm identifies foundational positions:

1. **Filter candidates:** Include positions where:
   - `stability === "canonical"` (core beliefs), OR
   - `confidence >= 8` (high-conviction insights)

2. **Sort by importance:**
   - Primary: `confidence` descending (highest conviction first)
   - Secondary: connection count descending (most connected as tiebreaker)

3. **Limit results:** Return top N positions (default 7)

**Rationale:** Canonical positions are foundational by definition. High-confidence positions (8+) represent strongly-held views. Connection count serves as a proxy for centrality — positions that connect many ideas are more likely to be foundational.

## Integration Notes

### For Orchestrator

**MindMapLegend integration:**
```tsx
const [legendExpanded, setLegendExpanded] = useState(false);

// Place in bottom-left corner or sidebar
<div className="fixed bottom-4 left-4 z-40 w-56">
  <MindMapLegend 
    isExpanded={legendExpanded} 
    onToggle={() => setLegendExpanded(!legendExpanded)} 
  />
</div>
```

**MindMapCornerstones integration:**
```tsx
// Replace inline cornerstone logic in sidebar
<MindMapCornerstones
  positions={graphData.nodes}
  links={graphData.links}
  onSelectPosition={(id) => {
    const node = graphData.nodes.find(n => n.id === id);
    if (node) handleNodeClick(node);
  }}
  selectedId={selectedNode?.id || null}
/>
```

**Neighborhood highlight integration:**
```tsx
import { getNeighborhood } from "@/lib/graphHighlight";

// When a node is selected, compute its neighborhood
const neighborhood = selectedNode 
  ? getNeighborhood(selectedNode.id, graphData.links, 1)
  : null;

// Use in render to dim non-neighbor nodes
const isInNeighborhood = neighborhood?.nodeIds.has(node.id);
```

### Path aliases

Components use `@/lib/graphHighlight` — ensure `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Verification

- [x] Build compiles without errors
- [x] TypeScript types are correct
- [x] All exports properly configured
- [x] Pure functions have no side effects
- [x] Handles edge cases (empty positions, orphan nodes)

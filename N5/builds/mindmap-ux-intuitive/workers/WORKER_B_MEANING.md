---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# WORKER B: Meaning & Through-Lines Components

**Objective:** Create components that make the intellectual structure legible — cornerstones, legend, and highlight logic.

## Context

You are building components for V's Mind Map at `Sites/vrijenattawar-staging`. The graph shows ~164 positions connected by ~195 edges. Currently, all nodes look equally important and edge meanings are invisible. Users need entry points and visual hierarchy.

**Tech stack:** React 18, TypeScript, Tailwind CSS, shadcn/ui.

**Data shape from `/api/positions`:**
```ts
interface Position {
  id: string;
  domain: string;  // e.g., "hiring-market", "worldview", "careerspan"
  title: string;
  insight: string;
  stability: string;  // "canonical" | "stable" | "hardening" | "developing" | "emerging"
  confidence: number; // 1-10
  formed_date: string;
}

interface Link {
  source: string;
  target: string;
  relationship: string; // "strongly_related" | "related" | "tangentially_related" | "weakly_related" | "implies" | "supports" | etc.
}
```

## Your Deliverables

### 1. Create `Sites/vrijenattawar-staging/src/components/mindmap/MindMapLegend.tsx`

A collapsible legend explaining edge colors and node meanings.

```tsx
interface MindMapLegendProps {
  isExpanded: boolean;
  onToggle: () => void;
}
```

**Requirements:**
- Compact by default (just a "Legend" button/icon)
- Expands to show:
  - **Edge strength**: Strong (purple, thick) → Weak (faint, thin)
  - **Domain colors**: hiring-market (orange), worldview (purple), careerspan (cyan), etc.
  - **Stability indicators**: canonical (full opacity) → emerging (lower opacity)
- Dark theme, fits in bottom-left or as sidebar section
- Smooth expand/collapse animation

### 2. Create `Sites/vrijenattawar-staging/src/components/mindmap/MindMapCornerstones.tsx`

A pinned list of "cornerstone positions" — the foundational ideas.

```tsx
interface MindMapCornerstonesProps {
  positions: Position[];
  onSelectPosition: (id: string) => void;
  selectedId: string | null;
}
```

**Requirements:**
- Compute cornerstones: `stability === "canonical" OR confidence >= 8` (max 7 items)
- Sort by confidence desc, then by connection count
- Show as compact list in sidebar (above domain filters)
- Each item: domain dot + truncated title
- Click to select and center that node
- Highlight currently selected

### 3. Create `Sites/vrijenattawar-staging/src/lib/graphHighlight.ts`

Utility functions for highlight mode.

```ts
export function getNeighborhood(
  nodeId: string, 
  links: Link[], 
  depth: 1 | 2
): { nodeIds: Set<string>; linkIndices: Set<number> };

export function computeCornerstones(
  positions: Position[], 
  links: Link[], 
  maxCount?: number
): Position[];
```

**Requirements:**
- `getNeighborhood`: returns all nodes within N hops and the connecting edges
- `computeCornerstones`: implements the cornerstone logic (canonical OR confidence >= 8)
- Pure functions, no side effects
- Well-typed, handles edge cases (orphan nodes, missing data)

### 4. Update barrel export: `Sites/vrijenattawar-staging/src/components/mindmap/index.ts`

Add your new exports.

## Output Format

When complete, write a summary to: `N5/builds/mindmap-ux-intuitive/workers/WORKER_B_OUTPUT.md`

Include:
1. Files created (with full paths)
2. Component interfaces
3. Cornerstone algorithm explanation
4. Integration notes

## Constraints

- Do NOT modify `MindMap.tsx` — orchestrator integrates
- Do NOT install new dependencies
- Keep logic in `graphHighlight.ts` pure and testable

## Success Criteria

- Legend clearly explains visual encoding
- Cornerstones provide 5-7 compelling entry points
- Neighborhood computation is correct (verified manually)

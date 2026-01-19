---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# WORKER C: Polish & Guided Paths (30% Wow)

**Objective:** Create the "guided paths" feature and define animation/transition specs that amplify meaning without overwhelming.

## Context

You are building components for V's Mind Map at `Sites/vrijenattawar-staging`. The graph is functional but needs polish that makes exploring ideas delightful. The goal is 30% "wow factor" that serves comprehension, not just aesthetics.

**Tech stack:** React 18, TypeScript, Tailwind CSS, shadcn/ui.

**Existing edge styling (already in MindMap.tsx):**
```ts
const RELATIONSHIP_STYLES = {
  "strongly_related": { color: "#8b5cf6", width: 2.5, opacity: 0.7 },
  "related": { color: "#6366f1", width: 2, opacity: 0.5 },
  "tangentially_related": { color: "#4f46e5", width: 1.5, opacity: 0.35 },
  "weakly_related": { color: "#3730a3", width: 1, opacity: 0.2 },
  // ... legacy types
};
```

## Your Deliverables

### 1. Create `Sites/vrijenattawar-staging/src/components/mindmap/MindMapGuidedPaths.tsx`

Quick-select buttons for curated idea chains.

```tsx
interface GuidedPath {
  id: string;
  name: string;
  description: string;
  nodeIds: string[];  // ordered path
}

interface MindMapGuidedPathsProps {
  paths: GuidedPath[];
  onSelectPath: (path: GuidedPath) => void;
  activePath: string | null;
}
```

**Requirements:**
- Show 2-3 pre-computed paths as buttons in the right rail
- Path examples:
  - "Hiring Signal Collapse" chain (the connected ideas around this core thesis)
  - "Self-Knowledge → Career" chain
  - "AI Impact" chain
- Selecting a path highlights all nodes in sequence
- Visual: subtle numbered badges on path nodes (1, 2, 3...)
- Clear button to exit path mode

### 2. Create `Sites/vrijenattawar-staging/src/lib/graphPaths.ts`

Compute interesting paths through the graph.

```ts
export interface ComputedPath {
  id: string;
  name: string;
  description: string;
  nodeIds: string[];
  score: number;  // interestingness metric
}

export function computeGuidedPaths(
  positions: Position[],
  links: Link[],
  maxPaths?: number
): ComputedPath[];

export function findLongestChain(
  startNodeId: string,
  links: Link[],
  visited?: Set<string>
): string[];
```

**Requirements:**
- `computeGuidedPaths`: find 3-5 interesting paths based on:
  - High-degree nodes (hubs)
  - Strong relationship chains
  - Canonical/high-confidence anchors
- Each path should have 4-8 nodes (not too short, not overwhelming)
- Return paths sorted by "interestingness" score
- Include human-readable name derived from first node's title

### 3. Create `Sites/vrijenattawar-staging/src/lib/graphAnimations.ts`

Animation configuration and helpers.

```ts
export const ANIMATION_CONFIG = {
  focusTransition: { duration: 300, easing: 'ease-out' },
  highlightFade: { duration: 200 },
  pathStep: { delay: 150 },  // delay between highlighting each path node
};

export function getHighlightStyles(
  nodeId: string,
  selectedId: string | null,
  neighborIds: Set<string>,
  pathIds: string[]
): { opacity: number; scale: number; glow: boolean };
```

**Requirements:**
- Respect `prefers-reduced-motion` (skip animations if set)
- Keep transitions under 300ms for responsiveness
- Define glow effect for selected node (subtle, not garish)
- Dim non-highlighted nodes to 0.2-0.3 opacity

### 4. Update barrel export

## Output Format

When complete, write to: `N5/builds/mindmap-ux-intuitive/workers/WORKER_C_OUTPUT.md`

Include:
1. Files created
2. Path computation algorithm explanation
3. Animation specs
4. Integration notes

## Constraints

- Do NOT modify `MindMap.tsx`
- Do NOT add heavy animation libraries (no framer-motion, etc.)
- Keep "wow" tasteful — amplify meaning, don't distract

## Success Criteria

- Guided paths provide instant "aha" moments
- Animations feel smooth, not sluggish
- Reduced-motion users get instant transitions

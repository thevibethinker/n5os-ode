---
created: 2026-01-16
last_edited: 2026-01-16
version: 1
provenance: con_jmgVLfK7jKZO9X1i
---
# WORKER A: Discoverability Components

**Objective:** Create the Right Rail and Search components that make /mind self-explanatory to first-time visitors.

## Context

You are building components for V's Mind Map at `Sites/vrijenattawar-staging`. The Mind Map visualizes ~164 intellectual positions as a force-directed graph. Currently, when no node is selected, the right side of the screen is completely empty — users don't realize a details panel exists.

**Tech stack:** React 18, TypeScript, Tailwind CSS, shadcn/ui components (already installed).

## Your Deliverables

### 1. Create `Sites/vrijenattawar-staging/src/components/mindmap/MindMapEmptyState.tsx`

A component shown in the right rail when no node is selected.

```tsx
interface MindMapEmptyStateProps {
  totalPositions: number;
  totalDomains: number;
  onSearchOpen: () => void;
}
```

**Requirements:**
- Dark theme (bg-zinc-900/50, text-zinc-300/400/500)
- Title: "Select a position" or "Explore V's thinking"
- 3-4 bullet instructions: "Click any node", "Drag to pan", "Scroll to zoom", "Press ⌘K to search"
- Keyboard shortcuts reference (small, muted)
- Subtle visual affordance (faint border, slight glow) so users notice the panel exists
- Optional: small animated hint arrow pointing left toward the graph

### 2. Create `Sites/vrijenattawar-staging/src/components/mindmap/MindMapSearch.tsx`

A Cmd/Ctrl+K search modal for finding positions.

```tsx
interface MindMapSearchProps {
  isOpen: boolean;
  onClose: () => void;
  positions: Array<{ id: string; title: string; domain: string; }>;
  onSelectPosition: (id: string) => void;
}
```

**Requirements:**
- Modal overlay with backdrop blur
- Search input with magnifying glass icon
- Fuzzy match on title and domain (simple includes() is fine)
- Show up to 10 results with domain badge
- Arrow key navigation + Enter to select
- Esc to close
- Use shadcn Dialog or build minimal modal

### 3. Create `Sites/vrijenattawar-staging/src/components/mindmap/index.ts`

Barrel export file:
```ts
export { default as MindMapEmptyState } from './MindMapEmptyState';
export { default as MindMapSearch } from './MindMapSearch';
```

## Output Format

When complete, write a summary to: `N5/builds/mindmap-ux-intuitive/workers/WORKER_A_OUTPUT.md`

Include:
1. Files created (with full paths)
2. Component interfaces (props)
3. Any design decisions made
4. Integration notes for the orchestrator

## Constraints

- Do NOT modify `MindMap.tsx` — the orchestrator will integrate your components
- Do NOT install new dependencies — use what's already available
- Keep components self-contained and well-typed
- Follow existing code style (see `Sites/vrijenattawar-staging/src/components/AmbientGraph.tsx` for reference)

## Success Criteria

- Components compile without errors (`bun run build` passes)
- Empty state clearly communicates "there's a panel here, click a node"
- Search modal is keyboard-accessible and responsive

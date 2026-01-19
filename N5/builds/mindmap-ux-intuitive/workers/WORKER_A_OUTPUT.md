---
created: 2026-01-16
last_edited: 2026-01-16
version: 1
provenance: con_d45fvGy1KlaZigM3
---

# Worker A: Discoverability Components — Output

**Status:** ✓ Complete  
**Build:** Passes (`bun run build` successful)

## Files Created

| File | Path |
|------|------|
| Empty State | `Sites/vrijenattawar-staging/src/components/mindmap/MindMapEmptyState.tsx` |
| Search Modal | `Sites/vrijenattawar-staging/src/components/mindmap/MindMapSearch.tsx` |
| Barrel Export | `Sites/vrijenattawar-staging/src/components/mindmap/index.ts` |

## Component Interfaces

### MindMapEmptyState

```tsx
interface MindMapEmptyStateProps {
  totalPositions: number;   // Count of positions (e.g., 164)
  totalDomains: number;     // Count of unique domains (e.g., 8)
  onSearchOpen: () => void; // Callback to open search modal
}
```

### MindMapSearch

```tsx
interface MindMapSearchProps {
  isOpen: boolean;
  onClose: () => void;
  positions: Array<{ id: string; title: string; domain: string }>;
  onSelectPosition: (id: string) => void;
}
```

## Design Decisions

1. **Empty State Visual Affordance**
   - Used `shadow-[0_0_40px_-10px_rgba(161,161,170,0.15)]` for subtle glow
   - Added animated pulse arrow (`←`) pointing toward graph
   - Card has faint border (`border-zinc-700/50`) to define presence

2. **Search Modal Implementation**
   - Built minimal modal (no Dialog dependency needed)
   - Positioned at 15vh from top for comfortable reach
   - Backdrop blur (`backdrop-blur-sm`) for depth perception

3. **Keyboard Navigation**
   - Arrow keys + Enter for selection
   - Esc closes modal
   - Mouse hover updates selection (hybrid UX)

4. **Domain Colors**
   - Reused `DOMAIN_COLORS` palette from AmbientGraph for consistency
   - Applied to Badge components in search results

5. **Icons**
   - Used lucide-react icons (already in project): `Search`, `MousePointer2`, `Move`, `ZoomIn`, `Command`, `X`

## Integration Notes for Orchestrator

### Import
```tsx
import { MindMapEmptyState, MindMapSearch } from "@/components/mindmap";
```

### State Needed in MindMap.tsx
```tsx
const [isSearchOpen, setIsSearchOpen] = useState(false);
```

### Keyboard Handler (add to existing useEffect)
```tsx
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Cmd/Ctrl+K to open search
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      setIsSearchOpen(true);
    }
  };
  document.addEventListener("keydown", handleKeyDown);
  return () => document.removeEventListener("keydown", handleKeyDown);
}, []);
```

### Empty State Rendering (when no node selected)
```tsx
{!selectedNode && (
  <MindMapEmptyState
    totalPositions={positions.length}
    totalDomains={new Set(positions.map(p => p.domain)).size}
    onSearchOpen={() => setIsSearchOpen(true)}
  />
)}
```

### Search Modal Rendering
```tsx
<MindMapSearch
  isOpen={isSearchOpen}
  onClose={() => setIsSearchOpen(false)}
  positions={positions}
  onSelectPosition={(id) => {
    // Focus node in graph + select it
    const node = positions.find(p => p.id === id);
    if (node) {
      setSelectedNode(node);
      // Optionally center graph on node
    }
  }}
/>
```

## Verification

- [x] Components compile without TypeScript errors
- [x] `bun run build` passes
- [x] Dark theme consistent with existing UI (zinc palette)
- [x] Keyboard-accessible
- [x] No new dependencies added

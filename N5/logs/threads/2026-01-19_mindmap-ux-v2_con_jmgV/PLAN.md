---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# Mind Map UX v2: Implementation Plan

## Checklist

### Phase 1: Visual Hierarchy & Contrast (Core Rendering)
- [x] 1.1 Node size varies by confidence (larger = more confident)
- [ ] 1.2 Background gradient from center (deferred - minimal impact)
- [x] 1.3 Right panel border/shadow for visibility
- [x] 1.4 Increase edge contrast (opacity bump)
- [x] 1.5 Node labels: full title on hover tooltip

### Phase 2: Discoverability & Affordances
- [x] 2.1 "Click a position to explore" hint when no selection
- [x] 2.2 Hover state on nodes (glow/scale)
- [x] 2.3 Domain color dots in sidebar are clickable legend
- [x] 2.4 Stability legend is functional (filters by stability)

### Phase 3: Navigation & Search
- [x] 3.1 Search bar in header (filters nodes by title)
- [x] 3.2 Search highlights matching nodes (via filter)
- [x] 3.3 Deep link support (/mind?position=xyz)
- [x] 3.4 "Fit to view" after domain filter

### Phase 4: Meaning & Structure
- [x] 4.1 Cornerstone positions section (pinned top 5-7)
- [x] 4.2 Edge legend (what relationship types mean)
- [ ] 4.3 Cluster labels for domain groups (deferred - complex)
- [ ] 4.4 Connection count badge on nodes (deferred - visual clutter)

---

## Phase 1: Visual Hierarchy & Contrast

**Objective:** Make the graph readable and the UI panels discoverable.

**Affected Files:**
- `Sites/vrijenattawar-staging/src/pages/MindMap.tsx`

**Changes:**

### 1.1 Node size by confidence
```typescript
// In nodeCanvasObject callback
const baseSize = 6;
const confidenceScale = (node.confidence || 5) / 5; // 0.2 to 2.0
const radius = baseSize * (0.5 + confidenceScale * 0.5); // 3 to 9px
```

### 1.2 Background gradient
```typescript
// Replace backgroundColor="#030303" with custom canvas background
// Radial gradient: center #0a0a0a → edges #030303
```

### 1.3 Right panel visibility
```css
/* Add left border glow */
border-left: 1px solid rgba(255,255,255,0.1);
box-shadow: -4px 0 20px rgba(0,0,0,0.5);
```

### 1.4 Edge contrast boost
```typescript
// Increase all opacity values by 0.15
// Min opacity: 0.25 (was 0.2)
```

### 1.5 Hover tooltips
```typescript
// Add nodeLabel prop to ForceGraph2D
nodeLabel={(node) => node.title}
```

**Test:** Visual inspection - nodes should vary in size, background should have depth, right panel should be visible on low-contrast screens.

---

## Phase 2: Discoverability & Affordances

**Objective:** Make it obvious how to interact.

**Affected Files:**
- `Sites/vrijenattawar-staging/src/pages/MindMap.tsx`

**Changes:**

### 2.1 Empty state hint
```tsx
{!selectedNode && (
  <div className="fixed right-8 top-1/2 -translate-y-1/2 text-zinc-600 text-sm">
    <p>← Click a position to explore</p>
  </div>
)}
```

### 2.2 Hover state
```typescript
// Track hovered node in state
const [hoveredNode, setHoveredNode] = useState<string | null>(null);

// In nodeCanvasObject: scale up + glow when hovered
if (node.id === hoveredNode) {
  ctx.shadowColor = color;
  ctx.shadowBlur = 15;
  radius *= 1.3;
}
```

### 2.3 Domain legend clickable
Already implemented - verify working.

### 2.4 Stability filter
```typescript
const [selectedStability, setSelectedStability] = useState<string | null>(null);

// Add click handlers to stability items in sidebar
// Filter nodes by stability in filteredData memo
```

**Test:** Hover over nodes - should see glow. Click stability level - should filter.

---

## Phase 3: Navigation & Search

**Objective:** Let users find specific positions quickly.

**Affected Files:**
- `Sites/vrijenattawar-staging/src/pages/MindMap.tsx`
- `Sites/vrijenattawar-staging/src/components/ui/input.tsx` (if needed)

**Changes:**

### 3.1-3.2 Search bar
```tsx
const [searchQuery, setSearchQuery] = useState("");

// In header, add search input
<input 
  placeholder="Search positions..."
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  className="bg-zinc-900 border-zinc-800 ..."
/>

// In filteredData memo, also filter by search
const matchesSearch = !searchQuery || 
  node.title.toLowerCase().includes(searchQuery.toLowerCase());
```

### 3.3 Deep links
```typescript
// On mount, check URL params
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const positionId = params.get('position');
  if (positionId) {
    const node = graphData.nodes.find(n => n.id === positionId);
    if (node) {
      setSelectedNode(node);
      // Center on node
      graphRef.current?.centerAt(node.x, node.y, 1000);
    }
  }
}, [graphData]);
```

### 3.4 Fit after filter
```typescript
// After domain filter changes, fit to view
useEffect(() => {
  if (graphRef.current) {
    setTimeout(() => graphRef.current.zoomToFit(400, 50), 100);
  }
}, [selectedDomain]);
```

**Test:** Type in search - nodes should filter. Navigate to /mind?position=hiring-signal-collapse - should open that position.

---

## Phase 4: Meaning & Structure

**Objective:** Surface the intellectual structure, not just the graph.

**Affected Files:**
- `Sites/vrijenattawar-staging/src/pages/MindMap.tsx`
- `Sites/vrijenattawar-staging/server.ts` (cornerstone API)

**Changes:**

### 4.1 Cornerstone positions
```typescript
// Add to sidebar, above domains
const cornerstones = graphData.nodes
  .filter(n => n.stability === 'canonical' || n.confidence >= 9)
  .slice(0, 7);

// Render as clickable cards
```

### 4.2 Edge legend
```tsx
// Add collapsible section in sidebar
<details className="mt-6">
  <summary className="text-zinc-400 text-sm">Relationship Types</summary>
  <div className="mt-2 space-y-1 text-xs">
    <div className="flex items-center gap-2">
      <div className="w-4 h-0.5 bg-purple-500" />
      <span>strongly related</span>
    </div>
    ...
  </div>
</details>
```

### 4.3 Cluster labels (stretch)
```typescript
// Calculate domain centroids
// Render domain names at centroid positions
// Lower z-index, faded text
```

### 4.4 Connection count
```typescript
// In nodeCanvasObject, show connection count for high-connectivity nodes
const connectionCount = graphData.links.filter(
  l => l.source.id === node.id || l.target.id === node.id
).length;
if (connectionCount > 5) {
  // Draw small badge
}
```

**Test:** Cornerstone section shows top positions. Edge legend explains relationships.

---

## Execution Order

1. Phase 1 first (foundation - makes everything else visible)
2. Phase 2 second (interaction patterns)
3. Phase 3 third (navigation)
4. Phase 4 last (polish)

Build and test after each phase. Don't proceed to next phase until current phase verified working.

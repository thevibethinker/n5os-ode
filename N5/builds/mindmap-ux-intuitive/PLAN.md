---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_jmgVLfK7jKZO9X1i
---

# Mind Map: Intuitive, Meaning-First UX (70% meaning / 30% wow)

## Open Questions (answer if you have a strong opinion; otherwise we’ll ship defaults)

1. **“Cornerstones” definition**: should “Cornerstone Positions” be **top confidence**, **canonical stability**, or a **manual curated list**?
   - Default: *canonical OR confidence ≥ 8* (max 7 items).
2. **Relationship semantics UX**: should we show relationship types as **(a)** a simple “Strength” legend (Strong/Related/Tangential/Weak) or **(b)** the full label list (implies/supports/etc.)?
   - Default: *Strength-first legend + advanced tooltip.*
3. **Audience**: is /mind primarily for **you** (thinking tool) or **others** (portfolio artifact)?
   - Default: *50/50* → optimize for first-time visitor comprehension while preserving power.

## Checklist

### Phase 1 — Make the UI self-explanatory (discoverability + navigation)
- ☐ Add “Details panel” affordance so the right side never feels empty
- ☐ Add search (Cmd/Ctrl+K) and node hover tooltips for full titles
- ☐ Add “How to use” micro-onboarding hint + keyboard shortcuts

### Phase 2 — Make meaning legible (themes, through-lines, entry points)
- ☐ Add “Cornerstone Positions” (pinned entry points)
- ☐ Add legend + filters for relationship strength/type
- ☐ Add “Highlight mode”: click node → highlight 1-hop and 2-hop neighbors + dim others

### Phase 3 — 30% wow (polish that amplifies meaning)
- ☐ Smooth transitions, subtle glow for highlighted subgraph
- ☐ “Guided paths”: quick-select curated chains (e.g., Hiring Signal Collapse chain)

## Nemawashi (Alternatives Considered)

### A) “Right panel always visible” (recommended)
- **What**: reserve a right rail (even when empty) with an explicit “Select a node to see details” state.
- **Pros**: solves your exact issue (no contrast → user thinks nothing exists).
- **Cons**: slightly less canvas width.

### B) “Floating inspector card”
- **What**: show a centered / bottom-right floating card on selection.
- **Pros**: preserves canvas space.
- **Cons**: can feel like a tooltip; less “app-like,” weaker affordance.

### C) “Click-to-open drawer”
- **What**: keep panel hidden but show an always-visible “Details ▸” handle.
- **Pros**: preserves space until needed.
- **Cons**: handle can still be missed; more state complexity.

**Decision:** A (always-visible right rail) + optional collapse handle later if needed.

## Trap Doors (Irreversible / High-Cost Decisions)

1. **Introducing a second graph view (cluster map / themes map)** as a separate mode could balloon scope.
   - Mitigation: keep a single graph view; add lightweight overlays (highlight, legend, paths) first.
2. **New schema / DB changes** for themes or manual curation.
   - Mitigation: phase 1–2 ship without schema changes; use client-side heuristics + optional config file later.

## Phases

### Phase 1 — Discoverability + navigation

**Affected files**
- `file 'Sites/vrijenattawar-staging/src/pages/MindMap.tsx'`
- (Possible) new component: `file 'Sites/vrijenattawar-staging/src/components/mindmap/MindMapHelp.tsx'`
- (Possible) new component: `file 'Sites/vrijenattawar-staging/src/components/mindmap/MindMapSearch.tsx'`

**Changes**
- Add a **persistent right rail**:
  - When no node selected: show an “Empty state” card:
    - Title: “Select a position”
    - 2–3 bullet instructions: drag, scroll/zoom, click a node
    - Key shortcuts: `Cmd/Ctrl+K` search, `Esc` clear selection, `F` fit
- Add search (Cmd/Ctrl+K):
  - fuzzy match on title + domain
  - selecting a result focuses/centers node + opens details
- Hover tooltip: show full title (no truncation) + domain chip
- Make interactive controls clearer:
  - Rename icons via `title` tooltips (“Zoom in”, “Zoom out”, “Fit to view”)

**Unit tests / verification**
- Manual QA (desktop + laptop):
  - Confirm user can discover details panel without prior instruction
  - Confirm search opens, results navigate, and selection highlights
  - Confirm `Esc` clears selection and returns to empty state

---

### Phase 2 — Meaning legibility (themes & through-lines)

**Affected files**
- `file 'Sites/vrijenattawar-staging/src/pages/MindMap.tsx'`
- (Possible) new component: `file 'Sites/vrijenattawar-staging/src/components/mindmap/MindMapLegend.tsx'`

**Changes**
- Add a **legend** (relationship strength + color meaning). Default: collapsed; expands on hover/click.
- Add **Highlight mode**:
  - on node select: highlight 1-hop neighborhood (edges + nodes), dim all others
  - optional toggle: “Include 2-hop”
- Add **Cornerstone Positions** list:
  - computed list pinned at top of sidebar
  - clicking an item centers and selects the node

**Unit tests / verification**
- Visual sanity:
  - selecting a node makes its neighborhood unambiguous within 1 second
  - cornerstones give immediate entry points (no “blank canvas” feeling)

---

### Phase 3 — 30% wow (polish that amplifies meaning)

**Affected files**
- `file 'Sites/vrijenattawar-staging/src/pages/MindMap.tsx'`

**Changes**
- Smooth animation when focusing on a node (center + zoom)
- Subtle glow / halo for selected node and highlighted edges
- Add **Guided Paths** (curated chains):
  - start with 2–3 computed paths based on graph structure (high-degree + strong edges)
  - show as quick buttons in right rail

**Unit tests / verification**
- No motion sickness:
  - animations under 250–350ms where possible
  - respect reduced-motion if available

## Success Criteria (Measurable)

1. **Discoverability**: a first-time viewer can tell there *is* a details panel and how to use it **within 5 seconds** (even on low-contrast screens).
2. **Meaning-first**: selecting a node makes its local context (“what it connects to”) obvious **within 1 second**.
3. **Entry points**: “Cornerstone Positions” provides at least **5** compelling starting nodes.
4. **No new schema**: ship without modifying `file 'N5/data/positions.db'`.
5. **Deploy**: changes promoted to prod via `bash N5/scripts/promote_site.sh vrijenattawar`.

## Release / Promotion

1. Implement in staging (`Sites/vrijenattawar-staging`).
2. Quick smoke test:
   - `/mind` loads
   - `/api/positions` returns nodes+links
   - selection, search, highlight, legend work
3. Promote to prod (authorized by V): `bash N5/scripts/promote_site.sh vrijenattawar`


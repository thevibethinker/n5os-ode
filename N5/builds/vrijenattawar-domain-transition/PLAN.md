---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_nxvKhHpwzg225fn8
---

# Build Plan: vrijenattawar.com Landing Page

**Project:** vrijenattawar-domain-transition
**Build ID:** website-design-v1
**Working Directory:** `/home/workspace/Sites/vrijenattawar-staging/`

---

## Design Decisions (from Socratic Discovery)

### Audience
- CEOs, VCs, thought leaders doing due diligence
- High-level professionals who have seen generic websites

### Positioning
**"The Banksy of productivity and vibe coding"**
- Creative builder with mysterious intrigue
- Website as proof artifact, not business card

### Design Principle
**Discovery over presentation**
- Explorable, layered, interactive experience
- Evidence of systems thinking, not just claims

### Aesthetic Direction
- Dark mode, expansive feel
- NYSKI-inspired for drama and "bigness" - but more explorable
- Not minimal - fascinating and traversable

### CTAs
- Follow on X
- Follow on LinkedIn  
- Subscribe on Substack (TBD)
- Book time via Calendly (15-min slots)

---

## Master Checklist

### Phase 1: Landing Page Foundation
- [ ] 1.1 Create dark hero with dramatic typography
- [ ] 1.2 Create about/bio section with V's positioning
- [ ] 1.3 Create "Current Focus" section (Careerspan)
- [ ] 1.4 Create CTA section (X, LinkedIn, Substack, Calendly)
- [ ] 1.5 Create minimal footer
- [ ] 1.6 Implement responsive design
- [ ] 1.7 Add subtle entrance animations

### Phase 2: Position Mind Map
- [ ] 2.1 Create positions API endpoint
- [ ] 2.2 Build interactive graph visualization component
- [ ] 2.3 Implement position detail panel
- [ ] 2.4 Add domain filtering
- [ ] 2.5 Style for "expansive" feel (zoom, pan, explore)
- [ ] 2.6 Integrate into landing page

### Phase 3: Enhancements (Future)
- [ ] 3.1 Chatbot integration (sandboxed Q&A)
- [ ] 3.2 Easter eggs implementation
- [ ] 3.3 Calendly API integration (vs embed)

---

## Phase 1 Details

### Affected Files
- `src/App.tsx` - Main routing and layout
- `src/pages/Landing.tsx` - New landing page component
- `src/components/Hero.tsx` - Hero section
- `src/components/About.tsx` - About/bio section
- `src/components/CurrentFocus.tsx` - Careerspan section
- `src/components/Connect.tsx` - CTAs section
- `src/components/Footer.tsx` - Footer
- `src/index.css` - Global styles and CSS variables

### Design Specs
**Typography:**
- Display: Bold, distinctive (not Inter/Roboto)
- Body: Clean, readable contrast

**Colors (CSS vars):**
- `--bg-primary`: Deep black/dark
- `--text-primary`: High contrast white/cream
- `--accent`: Dramatic highlight (TBD based on research)

**Motion:**
- Staggered fade-in on page load
- Subtle parallax/depth effects
- Smooth scroll

### Tests
- [ ] Site loads without errors
- [ ] All sections render
- [ ] Responsive at mobile (375px), tablet (768px), desktop (1440px)
- [ ] Links functional (X, LinkedIn, Calendly)

---

## Phase 2 Details

### Data Source
- Database: `/home/workspace/N5/data/positions.db`
- 124 positions across 8 domains
- Has connection data (supports, extends, implies, prerequisite)
- Has stability/confidence ratings

### Affected Files
- `server.ts` - Add `/api/positions` endpoint
- `src/pages/MindMap.tsx` - New page for graph
- `src/components/PositionGraph.tsx` - Interactive visualization
- `src/components/PositionPanel.tsx` - Detail view

### Tech Stack for Graph
Options:
1. **react-force-graph** - 2D/3D force-directed graph
2. **cytoscape.js** - Full graph visualization library
3. **d3-force** - Low-level, maximum control
4. **vis-network** - Obsidian-like feel

Recommendation: Start with react-force-graph-2d for rapid iteration

### Tests
- [ ] API returns positions JSON
- [ ] Graph renders with nodes and edges
- [ ] Clicking node shows detail panel
- [ ] Domain filter works
- [ ] Zoom/pan functional

---

## Execution Order

1. **Now:** Execute Phase 1 (Landing Page)
2. **After Phase 1:** Execute Phase 2 (Mind Map)
3. **Future conversation:** Phase 3 (Chatbot, Easter eggs, Calendly API)

---

## Research (Optional Parallel Worker)

Could spawn a worker to research:
- Personal landing pages of notable founders/VCs for inspiration
- Interactive portfolio sites with explorable elements
- Best practices for mind map / knowledge graph UX

---

## Notes

- Site already scaffolded at staging URL
- Using Zo Sites (Bun + Hono + React + Tailwind CSS 4)
- shadcn/ui components available

---

## Phase 1: Landing Page Foundation

### Checklist
- [x] Hero section with name, tagline, CTAs
- [x] About/Journey section
- [x] Current Focus section (Careerspan card)
- [x] Connect section (LinkedIn, Twitter, Email, Calendly)
- [x] Footer with version stamp
- [ ] Add Substack link (pending V setting up Substack)

---

## Phase 2: Position Mind Map

### Checklist
- [x] API endpoint `/api/positions` serving from positions.db
- [x] API endpoint `/api/positions/:id` for single position
- [x] Force-directed graph component with react-force-graph-2d
- [x] Domain filtering sidebar
- [x] Color coding by domain
- [x] Stability legend
- [x] Zoom controls
- [x] Node click → detail panel (basic implementation)
- [ ] Connection lines between related positions
- [ ] Polish detail panel with full position data



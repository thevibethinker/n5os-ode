---
created: 2025-12-22
last_edited: 2025-12-22
version: 1.0
type: build_plan
status: active
provenance: con_dYFeFGsBgupQRRaa
---

# Plan: ZoWrapped v2 Visualizations

**Objective:** Upgrade ZoWrapped 2025 with high-fidelity, quantifiable visualizations including agentic tracking, neural knowledge mapping, and peak velocity clock plots.

**Trigger:** V's request to "level up" the site with creative visualizations and accurate, quantifiable data.

**Key Design Principle:** Modularity over complexity. Extract precise data via Python (determinism) and render via React/Recharts (semantics).

---

## Open Questions
- [ ] Do we want to keep the current `data.json` structure or move to a more granular multi-file data architecture for faster loading? (Initial approach: Granular JSON files).
- [ ] Should the "Neural Map" be a static SVG or an interactive D3/Recharts component? (Initial approach: Interactive component).

---

## Checklist

### Phase 1: Data Extraction Engine (Mechanical Core)
- ☐ Create `N5/scripts/zo_wrapped_v2_extractor.py` to pull quantifiable metrics.
- ☐ Implement "Agent vs. User" conversation classification logic.
- ☐ Extract B-block density metrics and reasoning pattern stats.
- ☐ Export to `Sites/zo-wrapped-2025/src/data/v2_metrics.json`.
- ☐ Test: Run script and verify JSON contains exact counts (956 scripts, 3107 blocks, etc).

### Phase 2: Frontend Component Upgrade (Visual Layer)
- ☐ Create `ClockPlot` component for Peak Velocity visualization.
- ☐ Create `AgenticSplit` donut chart component.
- ☐ Create `KnowledgeNeuralMap` (Force-directed or Tree map) for N5 directory growth.
- ☐ Create `VoiceParameterRadar` for communication style visualization.
- ☐ Test: Verify components render in dev environment with live data.

### Phase 3: Thematic Integration & Deployment
- ☐ Update `Wrapped.tsx` to include the new "Level Up" sections.
- ☐ Apply "Bento Box" layout with glowing border effects.
- ☐ Final cleanup of unused static assets.
- ☐ Test: Full site build and deploy via `promote_site.sh`.

---

## Phase 1: Data Extraction Engine (Mechanical Core)

### Affected Files
- `N5/scripts/zo_wrapped_v2_extractor.py` - CREATE - New canonical extractor for v2 metrics.
- `Sites/zo-wrapped-2025/src/data/v2_metrics.json` - CREATE - Target data artifact for frontend.

### Changes

**1.1 Unified Metric Extraction:**
Create a Python script that connects to `conversations.db`, `meeting_pipeline.db`, `crm_v3.db`, and `wellness.db` to extract:
- Conversation counts by hour (Clock Plot data).
- Conversation counts by type + mode (User vs. Agent).
- Script/Line counts (Code Pulse).
- B-block counts by type (Meeting Intelligence density).
- Knowledge file counts by directory (Neural Map data).

**1.2 Agent Classification Logic:**
Implement heuristic to flag conversations as `agent` if `mode == 'agent'` or title contains "Scheduled", "MG-2", or "Blurb generation".

### Unit Tests
- `python3 N5/scripts/zo_wrapped_v2_extractor.py --dry-run`: Expected output is a valid JSON schema.
- Verification: `agent_count` + `user_count` == `total_conversations`.

---

## Phase 2: Frontend Component Upgrade (Visual Layer)

### Affected Files
- `Sites/zo-wrapped-2025/src/components/v2/ClockPlot.tsx` - CREATE
- `Sites/zo-wrapped-2025/src/components/v2/AgenticSplit.tsx` - CREATE
- `Sites/zo-wrapped-2025/src/components/v2/KnowledgeMap.tsx` - CREATE
- `Sites/zo-wrapped-2025/src/components/v2/VoiceRadar.tsx` - CREATE

### Changes

**2.1 Visual Implementation:**
Use `recharts` for Clock Plot (RadialBarChart) and Radar (RadarChart). Use `react-force-graph` or simple Tree structure for Knowledge Map.

### Unit Tests
- Component Storybook/Preview check: Visuals match the "Careerspan" aesthetic.

---

## Success Criteria
1. Site displays exact quantifiable counts for all N5 artifacts.
2. New "Clock Plot" clearly shows peak activity hours.
3. "Agent vs. User" split is visually represented.
4. Deployment successful to `zo-wrapped-2025-va.zocomputer.io`.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Database lock during extraction | Use `read-only` connections for SQLite. |
| Performance lag with force-directed graph | Limit node depth to top 3 levels of Knowledge/Personal. |
| Data inconsistency | Cross-reference script output with manual `sqlite3` counts. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. "Show what you DIDN'T do" — Track skipped meetings or declined follow-ups to show filtering power.
2. "The Living Pulse" — Make it an interactive timeline rather than a static wrapped.

### Incorporated:
- Incorporating the "Agent vs. User" split as a measure of "Filtering/Leverage."
- Adding the "Peak Velocity" clock to show the "When others were sleeping" narrative.

### Rejected (with rationale):
- "Live Timeline" — Rejected for Phase 1/2 to maintain the "Wrapped" (snapshot) intent, but documented for v3.


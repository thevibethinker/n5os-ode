---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
type: build_plan
status: in_progress
provenance: con_AVUiANpq2GYAc3Qz
---

# Plan: Position System Knowledge Graph Visualization

**Objective:** Visualize V's "Position System" as an interactive knowledge graph using the `ai-knowledge-graph` tool, enabling visual navigation of worldview interrelationships.

**Trigger:** V requested to grok and test a specific GitHub repository against their personal Position System.

**Key Design Principle:** Simple > Easy. We use a bridge script to transform existing structured data (SQLite) into a format the external tool can ingest, rather than modifying the external tool's core logic.

---

## Open Questions

- [ ] **Data Volume:** How many positions are currently in the DB? (Relevant for chunking/LLM costs if we re-extract, though we'll likely use existing connections first).
- [ ] **Relationship Mapping:** Should we use the *existing* JSON connections in the DB, or let the AI re-extract them from the `insight` text? (Recommendation: Start with existing connections for accuracy, then optionally "discover" new ones).

---

## Checklist

### Phase 1: Environment & Bridge
- ☐ Set up Python virtual environment in `N5/builds/position-viz/venv`.
- ☐ Install dependencies (requests, toml, jinja2, networkx, pyvis).
- ☐ Create `position_bridge.py` to extract positions from `N5/data/positions.db` and format for ingestion.
- ☐ Test: Successfully print a list of 5 positions in "Triple" format (Subject, Predicate, Object).

### Phase 2: Execution & Rendering
- ☐ Generate `positions_input.txt` (summary of all positions) or a custom JSON input.
- ☐ Configure `config.toml` to use Zo's internal LLM endpoints (if needed) or bypass LLM by feeding pre-extracted triples.
- ☐ Run `generate_graph.py` to produce `N5/builds/position-viz/positions_graph.html`.
- ☐ Test: Open the generated HTML and verify nodes represent Position Titles.

---

## Phase 1: Environment & Bridge

### Affected Files
- `N5/builds/position-viz/venv/` - CREATE - Python virtual environment.
- `N5/builds/position-viz/position_bridge.py` - CREATE - Script to query SQLite and generate triples.
- `N5/builds/position-viz/config.toml` - UPDATE - Local config for the tool.

### Changes

**1.1 Dependency Setup:**
Initialize `venv` and install `toml`, `jinja2`, `networkx`, `pyvis`. We need these for the tool to function on Zo.

**1.2 Bridge Logic:**
The `positions.db` stores connections in a JSON field. The bridge will:
1.  Connect to `/home/workspace/N5/data/positions.db`.
2.  Iterate through `positions` table.
3.  For each connection in the `connections` column, create a "Triple":
    - Subject: `source_position_title`
    - Predicate: `relationship_type` (e.g., "supports", "extends")
    - Object: `target_position_id` (resolved to title).

### Unit Tests
- `python3 position_bridge.py --dry-run`: Should output 5 valid triples to console.

---

## Phase 2: Execution & Rendering

### Affected Files
- `N5/builds/position-viz/positions_graph.html` - CREATE - The final interactive output.
- `N5/builds/position-viz/positions_data.json` - CREATE - Intermediate data for the visualizer.

### Changes

**2.1 Tool Invocation:**
We will bypass the LLM "Extraction" phase of Robert's tool since we already have high-fidelity structured connections. We will inject our pre-extracted triples directly into the `visualize_knowledge_graph` function.

**2.2 Customization:**
Adjust the `graph_template.html` (if necessary) to ensure it renders correctly in the Zo browser environment (handling relative paths for JS libraries).

### Unit Tests
- Verify `positions_graph.html` exists and is >10KB.

---

## Success Criteria

1. An interactive HTML file is generated at `file 'N5/builds/position-viz/positions_graph.html'`.
2. The graph contains nodes for at least 10 major positions.
3. Clicking a node shows its relationship types (Supports/Extends/etc).

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Missing IDs | The bridge script must resolve `target_id` to `title` correctly or fallback to the ID as the label. |
| Graph Clutter | If there are 100+ positions, the graph might be unreadable. We will implement a "Max Depth" or "Domain Filter" in the bridge. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. **Temporal Animation:** Instead of a static map, show how the positions "formed" over time using the `formed_date` column.
2. **Tension Highlighting:** Use a specific color (red) for relationships labeled "tension" (found in `_tensions.jsonl`).

### Incorporated:
- Tension highlighting (added to Phase 2 styling).

### Rejected (with rationale):
- Temporal Animation: Rejected for v1 to keep the "Simple > Easy" principle. Can be a v2 enhancement.


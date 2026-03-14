# Worker Assignment: w02_edge_infra

**Project:** r-block-framework  
**Component:** edge_infrastructure  
**Output:** `N5/data/reflection_edges.jsonl`, `N5/scripts/reflection_edges.py`

---

## Objective

Create the **edge storage infrastructure** for tracking connections between reflections, positions, knowledge articles, and other content.

## Context

The RIX (Integration) block will identify connections between V's reflections and his existing knowledge base. These connections need to be stored in a queryable format (JSONL) so patterns can emerge over time.

## Edge Types

Define these 5 edge types:

| Type | Meaning | Example |
|------|---------|---------|
| `EXTENDS` | Builds upon, develops further | "recruiter-game-plan EXTENDS candidate-ownership-thesis" |
| `CONTRADICTS` | Challenges or conflicts with | "new-market-signal CONTRADICTS prior-prediction" |
| `SUPPORTS` | Provides evidence for | "team-discussion SUPPORTS product-direction" |
| `REFINES` | Narrows, clarifies, adds nuance | "edge-case-analysis REFINES distribution-strategy" |
| `ENABLES` | Makes possible, unlocks | "technical-insight ENABLES product-feature" |

## JSONL Schema

Each edge is a single JSON line:

```json
{
  "id": "edge_20260109_001",
  "from": "2026-01-09_recruiter-game-plan",
  "from_type": "reflection",
  "to": "2025-12-15_candidate-ownership",
  "to_type": "position",
  "edge_type": "EXTENDS",
  "evidence": "Direct quote or paraphrase that establishes the connection",
  "confidence": "high|medium|low",
  "created": "2026-01-09T11:45:00Z",
  "created_by": "RIX"
}
```

Valid `from_type` / `to_type` values:
- `reflection` — An R-block output
- `position` — A position in positions.db
- `knowledge` — A knowledge article
- `meeting` — A meeting intelligence block

## Deliverables

### 1. `N5/data/reflection_edges.jsonl`
- Create the file with a comment header explaining the schema
- Include 2-3 example edges (can be synthetic/placeholder)

### 2. `N5/scripts/reflection_edges.py`

A CLI utility with these commands:

```bash
# Add a new edge
python3 N5/scripts/reflection_edges.py add \
  --from "2026-01-09_recruiter-game-plan" \
  --from-type reflection \
  --to "candidate-ownership" \
  --to-type position \
  --edge-type EXTENDS \
  --evidence "Quote here" \
  --confidence high

# Find edges FROM a source
python3 N5/scripts/reflection_edges.py from "2026-01-09_recruiter-game-plan"

# Find edges TO a target
python3 N5/scripts/reflection_edges.py to "candidate-ownership"

# Find all edges of a type
python3 N5/scripts/reflection_edges.py type EXTENDS

# Count edges (for detecting patterns/super-connectors)
python3 N5/scripts/reflection_edges.py stats
```

### Implementation Notes

- Use `argparse` for CLI
- JSONL append-only (don't rewrite whole file)
- Include `--json` flag for machine-readable output
- Validate edge_type against allowed values
- Auto-generate edge ID based on timestamp + counter

## Completion Criteria

- [ ] JSONL file created with schema header and examples
- [ ] Python script created with all 5 commands
- [ ] `--help` works for all commands
- [ ] Script handles empty file gracefully
- [ ] Edge IDs are unique and sortable

---

**When complete:** Run `python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker w02_edge_infra`


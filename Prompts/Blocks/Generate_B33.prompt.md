---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.1
provenance: con_JAADiniaFXpKQUTN
tool: true
description: "Generate B33 Decision Edges - extract context graph relationships from meeting intelligence"
tags: [meetings, intelligence, blocks, context-graph, edges, positions]
mg_stage: MG-2+
status: canonical
---

# Generate B33 Decision Edges

Extract context graph edges from meeting intelligence blocks.

## When to Use

Run after MG-2 completes (B01-B32 blocks exist). Can be run:
- Manually on individual meetings
- As part of the [M] → [P] state transition
- In batch mode for backfill

## Usage

```bash
# Dry run - see what would be extracted
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P] --dry-run

# Generate B33 file (edges go to review queue)
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P]

# Generate and auto-commit to edges.db (trusted meetings)
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P] --auto-commit
```

## Edge Types

The B33 block extracts these relationship types:

| Relation | Category | Description |
|----------|----------|-------------|
| `originated_by` | Provenance | Who first voiced this idea/decision |
| `supported_by` | Stance | Who endorsed after hearing |
| `challenged_by` | Stance | Who pushed back or raised concerns |
| `hoped_for` | Expectation | Expected positive outcome |
| `concerned_about` | Expectation | Feared risk or downside |
| `influenced_by` | Provenance | Who shaped thinking on topic |
| `depends_on` | Chain | Logical dependency between ideas/decisions |
| `supports_position` | Stance | Edge evidence validates V's documented position (Phase 4.5) |
| `challenges_position` | Stance | Edge evidence contradicts V's documented position (Phase 4.5) |
| `crystallized_from` | Chain | Position emerged from this evidence (Phase 4.5) |

## Output

Creates `B33_DECISION_EDGES.jsonl` in the meeting folder:

```jsonl
{"_meta": true, "meeting_id": "mtg_2025-12-26_Demo", "generated_at": "2026-01-04T..."}
{"source_type": "idea", "source_id": "semantic-matching", "relation": "originated_by", "target_type": "person", "target_id": "vrijen", ...}
{"source_type": "decision", "source_id": "pilot-program", "relation": "depends_on", "target_type": "decision", "target_id": "budget-approval", ...}
```

## Quality Guidelines

- **Selectivity**: 3-8 high-quality edges per meeting is ideal
- **Evidence**: Every edge must have a quote or paraphrase
- **Attribution**: Carefully distinguish originator vs supporter
- **V Identity**: Vrijen Attawar is always `vrijen` as person ID
- **Position edges**: Only create when alignment/contradiction is CLEAR (don't force it)

## Pipeline Integration

Updates `manifest.json`:
```json
{
  "blocks_generated": {
    "b33_decision_edges": true
  },
  "b33_edge_count": 8,
  "b33_generated_at": "2026-01-04T18:50:02.838343"
}
```

Logs to `PROCESSING_LOG.jsonl` when run as part of MG pipeline.

## Review Flow

Generated edges flow to the review queue (`N5/review/edges/`) unless `--auto-commit` is used. Use `edge_reviewer.py` to approve/reject before committing to `edges.db`.



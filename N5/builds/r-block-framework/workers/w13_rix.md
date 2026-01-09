# Worker Assignment: w13_rix

**Project:** r-block-framework  
**Component:** RIX_Integration  
**Dependencies:** w01_foundation, w02_edge_infra, w03_r04_pilot  
**Output:** `Prompts/Blocks/Reflection/RIX_Integration.prompt.md`

---

## Objective

Develop **RIX (Integration)** — the special block that ALWAYS runs, connecting reflections to the broader knowledge base and tracking patterns across time.

## RIX's Unique Role

Unlike R01-R09 which are selective lenses, RIX:
- **Always runs** (not conditional)
- **Queries memory** (knowledge, positions, meetings profiles)
- **Writes edges** (JSONL + inline markdown)
- **Tracks patterns** (promotes recurring themes to integration-patterns store)

## Pre-Requisites

1. Read the base template: `cat N5/templates/reflection/r_block_base.md`
2. Read the edge infrastructure: `cat N5/scripts/reflection_edges.py`
3. Understand memory profiles: knowledge, positions, meetings

## RIX Analysis Process

### Step 1: Extract Key Concepts
From the transcript, identify:
- Named entities (people, companies, products)
- Abstract concepts (themes, principles)
- Careerspan-specific terms

### Step 2: Query Memory Profiles
```python
from n5_memory_client import N5MemoryClient

client = N5MemoryClient()

# Query each profile
position_hits = client.search_profile("positions", key_concepts, limit=5)
knowledge_hits = client.search_profile("knowledge", key_concepts, limit=5)
meeting_hits = client.search_profile("meetings", key_concepts, limit=3)
```

### Step 3: Identify Connections
For each hit, assess:
- Is this a real connection or surface similarity?
- What type of edge? (EXTENDS, CONTRADICTS, SUPPORTS, REFINES, ENABLES)
- What's the evidence (specific quote)?

### Step 4: Write Edges
Use the edge infrastructure:
```bash
python3 N5/scripts/reflection_edges.py add \
  --from "<this_reflection>" \
  --to "<target>" \
  --edge-type <TYPE> \
  --evidence "<quote>" \
  --confidence <level>
```

### Step 5: Pattern Detection
- Count edges by target
- If any target has 5+ inbound edges: flag as super-connector
- If any theme appears in 3+ reflections: candidate for integration-patterns

## Edge Types Reference

| Type | Meaning | Use When |
|------|---------|----------|
| EXTENDS | Builds upon | New reflection develops prior idea |
| CONTRADICTS | Challenges | New reflection conflicts with prior |
| SUPPORTS | Provides evidence | New data backs prior position |
| REFINES | Adds nuance | Clarifies or narrows prior idea |
| ENABLES | Unlocks | New insight makes prior actionable |

## Output Schema

```markdown
## RIX: Integration Analysis

**Reflection:** [slug/title]
**Concepts Extracted:** [list]
**Edges Created:** [count]

### Memory Hits

#### Positions
- [Position 1]: [connection type] - [brief rationale]
- [Position 2]: ...

#### Knowledge
- [Article 1]: [connection type] - [brief rationale]
- ...

#### Meetings
- [Meeting 1]: [connection type] - [brief rationale]
- ...

### Edges Created

| From | To | Type | Evidence |
|------|----|------|----------|
| this | target1 | EXTENDS | "quote..." |
| ... | ... | ... | ... |

### Pattern Flags
- **Super-connectors:** [targets with 5+ edges]
- **Promotion candidates:** [themes with 3+ occurrences]

### Integration Narrative
[2-3 paragraphs contextualizing how this reflection connects to V's broader thinking]
```

## Completion Criteria

- [ ] Follows base template structure (adapted for RIX)
- [ ] Memory query code included and functional
- [ ] Edge writing integrated with w02 infrastructure
- [ ] Pattern detection logic documented
- [ ] Integration narrative section provides human value
- [ ] 200+ lines (RIX is more complex)

---

**When complete:** Run `python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker w13_rix`

---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_uXZfAchvpXYIevBj
---
# Worker Assignment: Phase 4.5 Planning — Position Integration

## Mission

Analyze the completed Phase 4 Cognitive Mirror implementation and design Phase 4.5+ to integrate the **positions system** as first-class entities in the context graph.

## Context

### Key Decision (Already Made)
- **Positions become first-class graph nodes** in edges.db
- Not just foreign-key references — full entity status
- Enables queries like "trace from position → all originating meetings/people"

### Conceptual Framework
- **Edges = receipts** — raw moments: who said what, when, how it relates
- **Positions = convictions** — synthesized beliefs, compound insights
- Multiple edges → crystallize into → one position
- Positions can have their own edges (supports, challenges, depends_on)

### Systems to Integrate
1. `N5/data/edges.db` — Context graph (just built)
2. `N5/data/positions.db` — Worldview/positions system (exists)
3. `N5/scripts/cognitive_mirror/` — Analysis layer (Phase 4, in progress)

## Worker Tasks

### Task 1: Audit Phase 4 Completion
Review `N5/scripts/cognitive_mirror/` directory:
- What scripts were created?
- What's the output format?
- How do they query edges.db?
- Document findings in `N5/builds/context-graph/PHASE4_AUDIT.md`

### Task 2: Analyze Position System
Review existing positions system:
- `N5/data/positions.db` schema
- `N5/scripts/positions.py` capabilities
- `N5/capabilities/internal/positions-system.md` documentation
- Identify: What fields need to map to edge entities?

### Task 3: Design Schema Extension
Propose schema changes to edges.db:
```sql
-- Example direction (worker should refine)
-- Add position as entity_type in edges
-- Add relation types: crystallized_from, supports_position, challenges_position
```

Consider:
- How do positions reference their source edges?
- How do edges reference positions they support/challenge?
- Bidirectional linking strategy

### Task 4: Design Migration Path
How do existing positions get linked to edges?
- Manual linking via review queue?
- Automated matching based on keywords/dates?
- Hybrid approach?

### Task 5: Generate PLAN.md for Phase 4.5-4.7

Create `N5/builds/context-graph/PLAN_PHASE4.5.md` with:

**Phase 4.5: Schema Extension**
- Add position entity type to edges.db
- Add position-related relation types
- Migration script for existing data

**Phase 4.6: Bidirectional Linking**
- positions.py updates to write edges when positions created/updated
- Edge extraction (B33) updates to detect position-relevant ideas
- Review queue for position-edge linking

**Phase 4.7: Cognitive Mirror Enhancement**
- Update analysis scripts to include position context
- New query: "Which positions did this meeting reinforce/challenge?"
- New analysis: "Position Stability Report" — which convictions have most/least edge support?

## Deliverables

1. `N5/builds/context-graph/PHASE4_AUDIT.md` — What Phase 4 built
2. `N5/builds/context-graph/PLAN_PHASE4.5.md` — Full plan for 4.5-4.7
3. Updated `N5/builds/context-graph/STATUS.md` — Reflect new phases

## Reference Files

- `file 'N5/builds/context-graph/PLAN.md'` — Current plan
- `file 'N5/builds/context-graph/STATUS.md'` — Current status
- `file 'N5/data/positions.db'` — Positions database
- `file 'N5/scripts/positions.py'` — Positions CLI
- `file 'N5/capabilities/internal/positions-system.md'` — Positions docs
- `file 'N5/scripts/edge_types.py'` — Current edge vocabulary

## Success Criteria

- [ ] Phase 4 audit complete with specific findings
- [ ] Schema extension designed with SQL
- [ ] Migration path documented
- [ ] PLAN_PHASE4.5.md is executable by Builder without clarification
- [ ] Trap doors identified (irreversible decisions)
- [ ] 2-3 alternatives considered for key decisions

## Handoff

After completion:
1. Return to this conversation thread
2. Present plan summary for V's review
3. Route to Builder if approved

---

**Assigned to:** Architect (in new thread)
**Estimated time:** 45-60 minutes


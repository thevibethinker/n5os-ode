---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
type: build_plan
status: in_progress
provenance: con_AVUiANpq2GYAc3Qz
---

# Plan: Position System Validation & Connection Enrichment

**Objective:** Transform V's position system from 80% orphaned islands into a richly connected knowledge graph, while fixing the pipeline so future extractions maintain connections.

## Open Questions
1. Should we merge near-duplicate positions (e.g., multiple "auto-apply is bad" variants)?
2. What's the minimum confidence threshold for auto-suggested connections?
3. Should cross-domain connections be weighted differently than within-domain?

## Scope
- **In Scope:** Domain validation, connection enrichment, pipeline fix, deduplication
- **Out of Scope:** UI/visualization improvements (separate build), embedding regeneration

---

## Checklist

### Phase 1: Domain Audit & Correction
- [ ] 1.1 Export all positions with domain + insight for human review
- [ ] 1.2 Flag positions that appear mis-domained
- [ ] 1.3 Apply domain corrections (HITL batch)

### Phase 2: Careerspan Core Connections (22 orphans → connected)
- [ ] 2.1 Generate connection proposals for all 22 careerspan orphans
- [ ] 2.2 Human review of proposals
- [ ] 2.3 Commit approved connections

### Phase 3: AI-Automation Connections (20 orphans → connected)
- [ ] 3.1 Generate connection proposals for all 20 ai-automation orphans
- [ ] 3.2 Human review of proposals
- [ ] 3.3 Commit approved connections

### Phase 4: Cross-Domain Bridge Identification
- [ ] 4.1 Run semantic similarity across all domains
- [ ] 4.2 Surface top 20 cross-domain connection candidates
- [ ] 4.3 Human review and commit

### Phase 5: Pipeline Fix (B32 → Connections)
- [ ] 5.1 Modify B32 generator to query existing positions
- [ ] 5.2 Add connection proposal step to extraction
- [ ] 5.3 Test on next meeting transcript

### Phase 6: Deduplication Pass
- [ ] 6.1 Identify near-duplicate positions by title/insight similarity
- [ ] 6.2 Propose merges (HITL)
- [ ] 6.3 Execute merges with connection preservation

---

## Phase 1: Domain Audit & Correction

### Affected Files
- `N5/data/positions.db` (read)
- `N5/builds/position-system-overhaul/domain-review.md` (create)

### Changes
**1.1 Export for Review:**
Generate a markdown file grouped by domain with position titles and truncated insights for V to scan and flag mis-categorizations.

**1.2 Flag Mis-domained:**
LLM pass to identify positions that semantically don't fit their assigned domain.

**1.3 Apply Corrections:**
SQL UPDATE statements generated from review, applied in single transaction.

### Unit Tests
- Verify no positions orphaned by domain change
- Verify domain enum remains consistent

---

## Phase 2: Careerspan Core Connections

### Affected Files
- `N5/data/positions.db` (read/write)
- `N5/builds/position-system-overhaul/careerspan-connections.md` (create)

### Changes
**2.1 Generate Proposals:**
For each of 22 careerspan orphans:
- Query all non-careerspan positions
- LLM proposes 1-3 connections with relationship type and reasoning
- Output as reviewable markdown table

**2.2 Human Review:**
V marks ✓ or ✗ on each proposal.

**2.3 Commit:**
Script reads approved proposals, generates INSERT/UPDATE statements.

### Unit Tests
- Verify connection targets exist before commit
- Verify bidirectional consistency (if A→B, optionally B→A)

---

## Phase 3: AI-Automation Connections
(Same pattern as Phase 2)

---

## Phase 4: Cross-Domain Bridges

### Affected Files
- `N5/data/positions.db` (read/write)
- `N5/builds/position-system-overhaul/cross-domain-bridges.md` (create)

### Changes
**4.1 Semantic Similarity:**
Use embeddings (if populated) or LLM to find positions in different domains that share conceptual DNA.

**4.2 Surface Candidates:**
Top 20 pairs with reasoning for why they should be connected.

**4.3 Commit:**
Same HITL pattern.

---

## Phase 5: Pipeline Fix

### Affected Files
- `Prompts/Blocks/Generate_B32.prompt.md` (modify)
- `N5/scripts/position_extractor.py` (create or modify)

### Changes
**5.1 Query Existing:**
After extracting a new position insight, query positions.db for semantic matches.

**5.2 Add Connection Step:**
If matches found, include in extraction output as proposed connections.

**5.3 Test:**
Run on a recent transcript, verify connections are proposed.

---

## Success Criteria
- [ ] Orphan rate reduced from 79.8% to <30%
- [ ] All careerspan positions connected to at least 1 other position
- [ ] B32 extractions now include connection proposals
- [ ] No broken connections (target_id validation)

---

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Over-connecting (everything relates to everything) | Require minimum 2 relationship types per connection; cap at 5 connections per position |
| Connection quality degradation | HITL review for all connections in Phase 2-4 |
| Breaking existing connections | All changes in transactions with rollback |

---

## Level Upper Review
*To be completed after initial phases*



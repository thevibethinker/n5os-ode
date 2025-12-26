---
created: 2025-12-22
last_edited: 2025-12-22
version: 1.0
type: build_plan
status: draft
provenance: con_hrrnHOCuFRK8x2KS
---

# Plan: Thought Provoker Meeting Integration

**Objective:** Integrate "Thought Provoker" capabilities into the core meeting processing pipeline by creating a dedicated B32 block and a centralized aggregation mechanism.

**Trigger:** Vrijen requested to revitalize the "Thought Provoker" concept to identify interesting, engaging, or thought-provoking ideas from meetings.

**Key Design Principle:** Simple over Easy. Use the existing B-block architecture to capture intelligence at the source (MG-2) rather than building a separate, complex scanning layer.

---

## Open Questions

- [ ] Should B32 be generated for ALL meeting types, or just strategic ones (Founder, Investor, Networking)?
- [ ] How do we implement the "Surprise Check" to ensure B32 doesn't fill with shallow AI-platitudes?
- [ ] Should the Harvester be the one to trigger "Cross-Pollination" synthesis?

---

## Checklist

### Phase 1: Block Definition & Registration
- ☐ Register B32 in `file 'N5/prefs/block_type_registry.json'` with "Non-Actionable" constraint
- ☐ Create generation prompt in `file 'Prompts/Blocks/Generate_B32.prompt.md'` with "Cringe Filter"
- ☐ Test: Manually generate B32 for a recent meeting transcript

### Phase 2: Pipeline Integration (MG-2)
- ☐ Update `file 'Prompts/Meeting Intelligence Generator.prompt.md'` to include B32
- ☐ Implement "High Threshold" logic (only create B32 if signal > X)
- ☐ Add B32 to stakeholder combinations in `file 'N5/prefs/block_type_registry.json'`
- ☐ Test: Run MG-2 on a test folder and verify B32 creation

### Phase 3: The Harvester & Aggregation
- ☐ Create `file 'N5/scripts/thought_provoker_harvester.py'`
- ☐ Create aggregation prompt/template for the "Collection"
- ☐ Test: Run harvester and verify output in the central collection file

### Phase 4: Cross-Pollination (The Idea Compounder)
- ☐ Create `file 'N5/scripts/idea_compounder.py'` to find connections between disparate B32s
- ☐ Update harvester to trigger compounding on new entries
- ☐ Test: Verify a "Synthesized Provocation" is generated from two different meetings

---

## Phase 1: Block Definition & Registration

### Affected Files
- `N5/prefs/block_type_registry.json` - UPDATE - Register B32 definition
- `Prompts/Blocks/Generate_B32.prompt.md` - CREATE - Block generation logic

### Changes

**1.1 B32 Registration:**
Add B32 definition to the registry. 
Name: `THOUGHT_PROVOKING_IDEAS`
Purpose: "Identify highly provocative themes, strategic 'weirdness', and original mental models."
Guidance: 
- **FORBIDDEN**: Actionable tasks, tactical follow-ups, or meeting recaps.
- **FOCUS**: Socratic challenges, contradictions, and "What if?" scenarios.
- **THRESHOLD**: If no truly provocative ideas exist, DO NOT create the block.

**1.2 B32 Prompt Creation:**
Draft a specific prompt that instructs the LLM to find 2-4 "spark moments" or "provocations" from the transcript.

### Unit Tests
- `B32_GEN_TEST`: Verify B32 generated from `sample_transcript.txt` contains qualitative "spark" moments, not just tactical recaps.

---

## Phase 2: Pipeline Integration (MG-2)

### Affected Files
- `Prompts/Meeting Intelligence Generator.prompt.md` - UPDATE - Add B32 to the generation list
- `N5/prefs/block_type_registry.json` - UPDATE - Add B32 to `INVESTOR`, `FOUNDER`, and `NETWORKING` combinations

### Changes

**2.1 MG-2 Update:**
Ensure the `MG-2` orchestrator knows to look for and generate B32. Ensure it's added to the `PROCESSING_LOG.jsonl` output list.

**2.2 Combination Update:**
Ensure B32 is flagged as required for high-stakes external meetings.

### Unit Tests
- `MG2_INTEGRATION_TEST`: Run MG-2 on an `_[M]` meeting and verify `B32_THOUGHT_PROVOKING_IDEAS.md` is present in the final block list.

---

## Phase 3: The Harvester & Aggregation

### Affected Files
- `N5/scripts/thought_provoker_harvester.py` - CREATE - Script to aggregate B32s
- `Knowledge/reflections/thought_provoker_collection.md` - CREATE - Central repository
- `N5/scripts/morning_digest.py` - UPDATE (Optional) - Include B32 highlights

### Changes

**3.1 Harvester Script:**
A script that scans `Personal/Meetings/` (Week-of folders) for all `B32_*.md` files. It compares timestamps/meeting IDs against the current "Collection" and appends new high-signal entries.

**3.2 Collection Template:**
A markdown file with YAML frontmatter to store the aggregated list, organized chronologically or by theme.

### Unit Tests
- `HARVEST_TEST`: Run harvester on a folder with 3 meetings (2 with B32, 1 without) and verify the collection contains 2 new entries.

---

## Success Criteria

1. B32 is generated ONLY when high-signal provocations are present.
2. B32 blocks are strictly non-actionable (strategic/conceptual only).
3. A central collection file exists and includes "Synthesized Provocations" (Phase 4).
4. Zero "AI-deep" platitudes (verified via manual review of first 5 blocks).

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Semantic Dilution (AI fluff) | Implement the "Cringe Filter" and high-threshold logic in the prompt. |
| Redundancy with B21 (Key Moments) | Enforce the "Non-Actionable" constraint. |
| Information overload | The Idea Compounder reduces volume by synthesizing related thoughts. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. **Idea Compounder**: Don't just list ideas; collide them. Synthesize provocations from disparate domains.
2. **Non-Actionable Constraint**: Forbid B32 from containing anything that could be a task. Keep it conceptual.
3. **Opt-In/High-Threshold**: An empty B32 is a success signal. Avoid "poisoning the well" with shallow content.

### Incorporated:
- All three suggestions incorporated into Phase 1 (Constraint), Phase 2 (Threshold), and Phase 4 (Compounder).

### Rejected (with rationale):
- None. The suggestions directly addressed the risk of redundancy and dilution.

---



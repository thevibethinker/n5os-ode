---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.0
provenance: con_ZBihMPGXJdRDrHQW
---

# Prompt Audit Report: Meeting Block System v3

## Executive Summary

Audited **39 block prompts** in `Prompts/Blocks/`. The PLAN specified 27 blocks (17 external + 10 internal), but actual inventory reveals **30 external blocks (B00-B35)** and **9 internal blocks (B40-B48)**. This mismatch requires clarification with the PLAN.

Key findings:
- **12 prompts** are high-quality and should be kept as-is
- **8 prompts** need refinement (mostly clarifying trigger conditions)
- **4 prompts** need expansion (too sparse for consistent output)
- **15 prompts** should be compressed or deprioritized (not in PLAN's final block list)
- **1 confirmed merge**: B02 + B05 (already in PLAN)
- **2 additional merge candidates**: B11 + B22 (both risk-focused), B13 becomes "Plan of Action" (not risks)

---

## Inventory Summary

### External Blocks (B00-B35) — 30 prompts found

| Block | Name | Words | Status in PLAN | Recommendation |
|-------|------|-------|----------------|----------------|
| B00 | Zo Take Heed | 1,120 | ✅ Always | **Keep** |
| B01 | Detailed Recap | 453 | ✅ Always | **Keep** |
| B02 | Commitments | 89 | ✅ Merge w/B05 | **Merge** |
| B03 | Decisions | 400 | ✅ Always | **Refine** |
| B04 | Open Questions | 384 | ✅ Conditional | **Keep** |
| B05 | Action Items | 840 | ✅ Merge w/B02 | **Merge** |
| B06 | Business Context | 442 | ✅ Conditional | **Keep** |
| B07 | Warm Introductions | 686 | ✅ ZTH-trigger | **Keep** |
| B08 | Stakeholder Intel | 993 | ✅ Always | **Refine** |
| B09 | Collaboration Terms | 1,177 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B10 | Relationship Trajectory | 1,172 | ✅ Conditional | **Compress** |
| B11 | Risks & Flags | 155 | ❌ Not in PLAN | **Merge w/B22** |
| B12 | Technical Infrastructure | 1,155 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B13 | Risks & Opportunities | 151 | ✅ Plan of Action | **Expand** (rename to POA) |
| B14 | Blurbs Requested | 961 | ✅ ZTH-trigger | **Keep** |
| B15 | Energy & Sentiment | 97 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B16 | Follow-Up Schedule | 76 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B17 | Content & Assets | 79 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B20 | Brand Voice | 91 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B21 | Key Moments | 487 | ✅ Always | **Keep** |
| B22 | Risks & Mitigation | 85 | ❌ Not in PLAN | **Merge w/B11** |
| B23 | Context & Continuity | 81 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B24 | Product Ideas | 87 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B25 | Deliverable Map | 486 | ✅ Conditional | **Keep** |
| B26 | Meeting Metadata | 94 | ✅ Always | **Expand** |
| B27 | Wellness Indicators | 900 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B28 | Strategic Intelligence | — | ✅ Conditional | **MISSING** (no prompt file) |
| B31 | Stakeholder Research | 722 | ❌ Not in PLAN | **Compress/Deprioritize** |
| B32 | Thought Provoking Ideas | 762 | ✅ Conditional | **Keep** |
| B33 | Decision Edges | 681 | ✅ Conditional | **Keep** |
| B35 | Linguistic Primitives | 690 | ❌ Not in PLAN | **Compress/Deprioritize** |

### Internal Blocks (B40-B48) — 9 prompts found

| Block | Name | Words | Status in PLAN | Recommendation |
|-------|------|-------|----------------|----------------|
| B40 | Internal Decisions | 214 | ✅ Always | **Keep** |
| B41 | Team Coordination | 240 | ✅ Always | **Keep** |
| B42 | Internal Actions | 232 | ✅ Always | **Keep** |
| B43 | Resource Allocation | 274 | ✅ Conditional | **Keep** |
| B44 | Process Improvements | 279 | ✅ Conditional | **Keep** |
| B45 | Team Dynamics | 316 | ✅ Always | **Keep** |
| B46 | Knowledge Transfer | 323 | ✅ Conditional | **Keep** |
| B47 | Open Debates | 358 | ✅ Always | **Keep** |
| B48 | Internal Synthesis | 439 | ✅ Always | **Keep** |

---

## Quality Assessment

### Scoring Rubric

- **Specificity** (1-5): Does it ask for precise information?
- **Actionability** (1-5): Will output be directly useful?
- **Redundancy** (1-5): Overlap with other blocks? (5=unique, 1=high overlap)
- **Brevity** (1-5): Concise while complete? (5=optimal, 1=bloated/sparse)

### High-Quality Prompts (Keep As-Is)

| Block | Spec | Action | Redund | Brevity | Notes |
|-------|------|--------|--------|---------|-------|
| B00 | 5 | 5 | 5 | 4 | Excellent. Clear triggers, JSONL output, speaker validation |
| B01 | 5 | 5 | 5 | 5 | Good balance of structure and flexibility |
| B04 | 4 | 5 | 5 | 5 | Clean, focused on unresolved questions |
| B06 | 4 | 4 | 5 | 5 | Company-specific context, well-scoped |
| B07 | 5 | 5 | 5 | 4 | Comprehensive warm intro extraction |
| B14 | 5 | 5 | 5 | 4 | Excellent 4-question validation framework |
| B21 | 4 | 5 | 5 | 5 | Good balance of quotes vs. analysis |
| B32 | 5 | 5 | 5 | 4 | Strong principle-grounded requirement |
| B33 | 5 | 5 | 5 | 4 | Well-defined edge types and evolution tracking |
| B40-B48 | 4 | 4 | 5 | 4 | Internal blocks well-structured, consistent |

### Needs Refinement

| Block | Spec | Action | Redund | Brevity | Issue | Recommendation |
|-------|------|--------|--------|---------|-------|----------------|
| B03 | 3 | 4 | 4 | 4 | Overlaps with B40 (Internal Decisions) | Add explicit external-meeting scope |
| B05 | 4 | 5 | 2 | 3 | 840 words, heavy overlap with B02 | Merge into B02+B05 super-block |
| B08 | 4 | 4 | 4 | 3 | 993 words, complex semantic memory deps | Simplify memory loading; keep core sections |
| B10 | 4 | 4 | 4 | 3 | 1,172 words, heavy memory requirements | Trim memory context; focus on trajectory only |
| B25 | 4 | 5 | 4 | 4 | Slight overlap with B02/B05 commitments | Clarify: B25=content deliverables only |

### Needs Expansion (Too Sparse)

| Block | Spec | Action | Redund | Brevity | Issue | Recommendation |
|-------|------|--------|--------|---------|-------|----------------|
| B02 | 2 | 3 | 2 | 2 | Only 89 words, too sparse | Expand after B05 merge |
| B13 | 2 | 2 | 3 | 2 | Only 151 words, labeled "Risks & Opportunities" but PLAN says "Plan of Action" | Rewrite as Plan of Action block |
| B26 | 2 | 3 | 5 | 2 | Only 94 words, needs structure | Expand with explicit metadata fields |

### Compress/Deprioritize (Not in PLAN's Final List)

| Block | Spec | Action | Redund | Brevity | Why Deprioritize |
|-------|------|--------|--------|---------|------------------|
| B09 | 4 | 4 | 3 | 3 | Overlaps with B06 business context; not in final list |
| B11 | 2 | 3 | 1 | 2 | Heavy overlap with B22; sparse |
| B12 | 4 | 4 | 4 | 3 | Technical infra not in final list |
| B15 | 2 | 3 | 4 | 2 | Energy/sentiment, only 97 words, not critical |
| B16 | 2 | 3 | 3 | 2 | Follow-up schedule overlaps with B02+B05 |
| B17 | 2 | 3 | 4 | 2 | Content assets, sparse |
| B20 | 2 | 3 | 4 | 2 | Brand voice, sparse, not in final list |
| B22 | 2 | 3 | 1 | 2 | Overlaps with B11 |
| B23 | 2 | 3 | 4 | 2 | Context/continuity, sparse |
| B24 | 2 | 3 | 4 | 2 | Product ideas, sparse |
| B27 | 4 | 4 | 5 | 3 | Wellness is niche; not in final list |
| B31 | 4 | 4 | 3 | 4 | Overlaps with B08 stakeholder intel |
| B35 | 4 | 4 | 5 | 4 | Linguistic primitives, specialized use case |

---

## Merge Candidates

### Confirmed Merge: B02 + B05 → Commitments & Actions

**Rationale**: PLAN already specifies this. B02 (89 words) is sparse; B05 (840 words) is comprehensive. Merge into single block.

**Recommended structure** for merged block:
```markdown
# B02: Commitments & Actions

## Explicit Commitments
[Promises made with context]

## Action Items
[Tasks with owners, due dates, dependencies]
```

### Proposed Merge: B11 + B22 → Risk Analysis

**Rationale**: Both are risk-focused with high overlap.
- B11 "Risks & Flags" (155 words) — immediate warnings
- B22 "Risks & Mitigation" (85 words) — mitigation strategies

Neither is in PLAN's final list, but if risk tracking is needed, merge into single block.

### Renaming: B13 → Plan of Action

**Rationale**: PLAN lists B13 as "Plan of Action" but current prompt is titled "Risks & Opportunities" (151 words, sparse). Rewrite entirely.

---

## Missing Block

### B28: Strategic Intelligence — NO PROMPT FILE FOUND

PLAN lists B28 as "Strategic Intelligence" (Conditional, broad landscape implications). No `Generate_B28*.prompt.md` file exists.

**Action**: Create B28 prompt during D0.2.

---

## Observations

### Prompt Quality Patterns

1. **Best prompts** (B00, B01, B07, B14, B32, B33): Have clear trigger conditions, explicit output formats, quality checks, and anti-patterns section.

2. **Sparse prompts** (B02, B11, B13, B15-B17, B20, B22-B24, B26): Under 100 words, lack structure and specificity. Either expand or remove.

3. **Bloated prompts** (B05, B08, B09, B10, B12, B27): Over 900 words with heavy semantic memory loading. Consider simplifying memory requirements.

### Semantic Memory Overhead

Multiple blocks (B08, B09, B10, B12, B27, B31) require complex semantic memory context loading:
```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
# Multiple profile searches per block
```

**Concern**: This creates execution overhead and complexity. Consider:
1. Pre-fetching enrichment context once at pipeline start
2. Passing enrichment as input rather than in-prompt loading
3. Reducing mandatory memory checks to truly essential blocks (B08, B10)

### Internal Block Consistency

B40-B48 (internal blocks) are well-structured with consistent format (~200-450 words each). Good template for prompt standardization.

---

## Recommendations Summary

### Immediate Actions (D0.2)

1. **Merge B02 + B05** into "Commitments & Actions" super-block
2. **Rewrite B13** as "Plan of Action" (currently misnamed)
3. **Create B28** "Strategic Intelligence" (missing prompt)
4. **Expand B26** with explicit metadata structure

### Refinements (D0.2)

5. **Trim B08** memory loading sections (keep core extraction)
6. **Trim B10** memory context (focus on trajectory tracking)
7. **Scope B03** explicitly to external meetings

### Deprecation Candidates

The following blocks are NOT in PLAN's final list and have quality issues. Recommend archiving rather than maintaining:

- B09 (Collaboration Terms) — overlaps B06
- B11 + B22 (both risk-focused, sparse) — merge or archive
- B12 (Technical Infrastructure) — niche use case
- B15, B16, B17, B20, B23, B24 — all sparse (<100 words)
- B27 (Wellness) — specialized, not in final list
- B31 (Stakeholder Research) — overlaps B08
- B35 (Linguistic Primitives) — Voice Library specific

---

## Appendix: Word Count Breakdown

| Range | Count | Blocks |
|-------|-------|--------|
| <100 words | 10 | B02, B11, B15, B16, B17, B20, B22, B23, B24, B26 |
| 100-300 words | 5 | B13, B40, B41, B42, B43 |
| 300-500 words | 7 | B01, B03, B04, B06, B44, B45, B48 |
| 500-800 words | 6 | B07, B21, B25, B31, B33, B35 |
| 800-1000 words | 4 | B05, B08, B14, B27 |
| >1000 words | 5 | B00, B09, B10, B12, B32 |

**Observation**: Optimal prompt length appears to be 300-800 words. Prompts outside this range tend to be either too sparse (low quality) or too verbose (complexity overhead).

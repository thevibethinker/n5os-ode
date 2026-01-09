# Worker Assignment: w01_foundation

**Project:** r-block-framework  
**Component:** base_template  
**Output:** `N5/templates/reflection/r_block_base.md`

---

## Objective

Create the **base R-block template** — the common 7-section substructure that ALL reflection blocks (R00-R09 + RIX) will inherit.

## Context

V's reflection system processes raw thoughts (voice memos, stream-of-consciousness text) into structured intelligence. Each R-block is a **lens** that extracts a specific type of insight. This base template ensures consistency and reliable processing across all block types.

## The 7-Section Structure

Every R-block prompt MUST include these sections:

### 1. Domain Definition
- **What this lens sees:** The specific content type this block extracts
- **What this lens ignores:** Explicit exclusions to prevent overlap with other blocks
- **Boundary cases:** How to handle ambiguous content

### 2. Extraction Framework  
- **Trigger patterns:** Keywords/phrases that indicate relevant content
- **Semantic indicators:** Conceptual markers beyond keywords
- **Counter-indicators:** Signals that this block is NOT appropriate

### 3. Analysis Dimensions
- **Primary dimensions:** 3-5 specific analytical angles for this block type
- **Depth guidance:** How deep to analyze (surface observation vs. root cause)
- **Quality bar:** What distinguishes a good extraction from a weak one

### 4. Memory Integration
```python
# Template for memory queries - block-specific profiles to check
profiles_to_query = ["knowledge", "positions", "meetings"]  # customize per block
query_template = "..."  # semantic search query pattern
```

### 5. Output Schema
```markdown
## R## Block Name

**[Primary Field]:** ...
**[Secondary Field]:** ...

### [Analysis Section]
...

### Connections
- Links to: [prior reflections, positions, knowledge]
```

### 6. Connection Hooks
- **Upstream:** What prior content might this extend/refine?
- **Downstream:** What future reflections might build on this?
- **Cross-block:** Which other R-blocks might have related extractions from the same transcript?

### 7. Worked Example
A complete example showing:
- Sample input transcript snippet
- The extraction process (what was noticed, why)
- Final formatted output

## Deliverable

Create `/home/workspace/N5/templates/reflection/r_block_base.md` containing:
1. The template structure with all 7 sections
2. Clear placeholder markers like `{{BLOCK_ID}}`, `{{BLOCK_NAME}}`, `{{DOMAIN_DEFINITION}}`
3. Instructions for how to use this template when creating new R-blocks
4. A brief "quality checklist" at the end for self-validation

## Completion Criteria

- [ ] Template file created at specified path
- [ ] All 7 sections present with clear structure
- [ ] Placeholder markers are consistent and well-documented
- [ ] Memory integration section includes working Python snippet pattern
- [ ] Template is self-documenting (someone could create a new R-block from it)

---

**When complete:** Run `python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker w01_foundation`


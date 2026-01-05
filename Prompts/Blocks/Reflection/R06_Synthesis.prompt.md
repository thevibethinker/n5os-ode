---
description: Generate R06 Synthesis block from reflection input
tags: [reflection, block, r06, synthesis, meta]
tool: true
---

# Generate Block R06: Synthesis

**Purpose:** Capture cross-cutting patterns, meta-observations, and connections across domains.

## Input

The reflection text is provided in the conversation context.

## Your Task

Generate an **R06: Synthesis** block that captures:

1. **Pattern:** The cross-cutting observation or connection
2. **Domains Connected:** Which areas this bridges (personal + strategic, market + product, etc.)
3. **Emergent Insight:** What becomes visible only when these domains are combined
4. **Action Potential:** Does this synthesis suggest any concrete next step?

## Output Format

```markdown
## R06: Synthesis

**Pattern:** [The cross-cutting observation]

**Domains Connected:** [Which areas this bridges]

**Emergent Insight:** [What becomes visible through combination]

**Action Potential:** [Concrete next step, if any]
```

## Quality Standards

- Synthesis should reveal something not obvious from individual parts
- This block is optional — only generate if genuine cross-domain insight exists
- If no synthesis emerges, output: `R06: Not applicable — no cross-domain patterns detected`


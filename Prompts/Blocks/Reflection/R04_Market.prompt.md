---
description: Generate R04 Market Signal block from reflection input
tags: [reflection, block, r04, market]
tool: true
---

# Generate Block R04: Market Signal

**Purpose:** Capture competitive intelligence, market trends, opportunities, and external signals.

## Input

The reflection text is provided in the conversation context.

## Your Task

Generate an **R04: Market Signal** block that captures:

1. **Signal:** The market observation or competitive insight
2. **Source:** How V encountered this (conversation, observation, research)
3. **Signal Strength:** Strong (validated) / Medium (plausible) / Weak (speculation)
4. **Implication for Careerspan:** What this means for positioning or opportunity

## Output Format

```markdown
## R04: Market Signal

**Signal:** [The observation]

**Source:** [How this was encountered]

**Signal Strength:** [Strong / Medium / Weak]

**Implication for Careerspan:** [Positioning or opportunity impact]
```

## Quality Standards

- Distinguish between observed facts and V's interpretation
- Be specific about competitors, trends, or opportunities named
- If the reflection doesn't contain market signals, output: `R04: Not applicable — reflection lacks market content`


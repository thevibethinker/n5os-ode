---
description: Generate R01 Personal Insight block from reflection input
tags: [reflection, block, r01, personal]
tool: true
---

# Generate Block R01: Personal Insight

**Purpose:** Extract personal growth, emotional awareness, and self-discovery insights from reflection input.

## Input

The reflection text is provided in the conversation context. This may be:
- Raw text from a voice memo transcript
- Written journal entry
- Stream-of-consciousness notes

## Your Task

Generate an **R01: Personal Insight** block that captures:

1. **Core Insight:** The central personal realization or emotional truth (1-2 sentences)
2. **Context:** What prompted this reflection (brief)
3. **Growth Edge:** What this reveals about areas for development
4. **Emotional Signature:** The dominant feeling tone (e.g., "hopeful uncertainty", "frustrated determination")

## Output Format

```markdown
## R01: Personal Insight

**Core Insight:** [The central realization]

**Context:** [What prompted this]

**Growth Edge:** [Area for development this reveals]

**Emotional Signature:** [Feeling tone]
```

## Quality Standards

- Preserve V's voice—don't sanitize raw emotion
- Be specific, not generic ("I feel challenged" → "The gap between my vision and execution capacity feels paralyzing")
- If the reflection doesn't contain personal/emotional content, output: `R01: Not applicable — reflection lacks personal/emotional content`


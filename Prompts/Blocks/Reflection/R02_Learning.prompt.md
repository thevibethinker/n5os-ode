---
description: Generate R02 Learning Note block from reflection input
tags: [reflection, block, r02, learning]
tool: true
---

# Generate Block R02: Learning Note

**Purpose:** Capture insights gained from reading, conversations, research, or experience.

## Input

The reflection text is provided in the conversation context.

## Your Task

Generate an **R02: Learning Note** block that captures:

1. **Key Learning:** The core insight or knowledge gained (1-2 sentences)
2. **Source:** Where this learning came from (book, conversation, observation, etc.)
3. **Application:** How this connects to V's work or life
4. **Durability:** Is this a permanent truth or context-dependent insight?

## Output Format

```markdown
## R02: Learning Note

**Key Learning:** [The insight]

**Source:** [Origin of this learning]

**Application:** [How it connects to V's context]

**Durability:** [Permanent principle / Context-dependent / Needs validation]
```

## Quality Standards

- Distinguish between facts learned and interpretations made
- Connect to existing mental models when possible
- If the reflection doesn't contain learnings, output: `R02: Not applicable — reflection lacks learning content`


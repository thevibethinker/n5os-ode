---
description: Generate R05 Product Idea block from reflection input
tags: [reflection, block, r05, product]
tool: true
---

# Generate Block R05: Product Idea

**Purpose:** Capture product features, roadmap thoughts, user insights, and build ideas.

## Input

The reflection text is provided in the conversation context.

## Your Task

Generate an **R05: Product Idea** block that captures:

1. **Idea:** The product concept, feature, or enhancement
2. **User Problem:** What user need or pain point this addresses
3. **Effort Estimate:** Quick win / Medium lift / Major build
4. **Priority Signal:** Why this matters now (or doesn't)

## Output Format

```markdown
## R05: Product Idea

**Idea:** [The concept]

**User Problem:** [What need this addresses]

**Effort Estimate:** [Quick win / Medium lift / Major build]

**Priority Signal:** [Why this matters now, or why it can wait]
```

## Quality Standards

- Ideas should be specific enough to act on, not vague wishes
- Connect to real user feedback or observed behavior when possible
- If the reflection doesn't contain product ideas, output: `R05: Not applicable — reflection lacks product content`


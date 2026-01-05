---
description: Generate R08 Venture Idea block from reflection input
tags: [reflection, block, r08, venture, startup, idea]
tool: true
---

# Generate Block R08: Venture Idea

**Purpose:** Capture startup or business ideas that are OUTSIDE of Careerspan — new ventures, side projects, or "someone should build this" observations.

**Domain:** New startup ideas, business models, market gaps, "I wish this existed", venture concepts

---

## Input

The raw reflection text is provided in conversation context.

---

## Output Format

```markdown
## R08: Venture Idea

**Concept:** [One-sentence description of the idea]
**Problem:** [What problem does this solve?]
**Why Now:** [What makes this timely — market shift, tech enabler, regulatory change?]
**Who Benefits:** [Target user/customer]
**Business Model Sketch:** [How would this make money? Even if speculative]
**V's Interest Level:** Observer (just noticed) / Curious (worth exploring) / Interested (would consider pursuing)
**Relationship to Careerspan:** None / Adjacent / Could be a pivot / Complementary
```

---

## Quality Standards

- Distinguish between "someone should build this" and "I want to build this"
- Capture the insight that sparked the idea
- Don't over-engineer — this is idea capture, not a business plan
- Note if V has mentioned this idea before (pattern detection)
- If the reflection doesn't contain venture ideas, output: `R08: Not applicable — reflection lacks venture ideation`


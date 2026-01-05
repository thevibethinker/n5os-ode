---
description: Generate R00 Emergent block for content that doesn't fit existing R-blocks
tags: [reflection, block, r00, emergent, extensible, provisional]
tool: true
---

# Generate Block R00: Emergent

**Purpose:** Capture reflection content that doesn't fit cleanly into R01-R09. This is the extensibility mechanism — when V reflects on something that needs its own framework, R00 generates a provisional structure that can be refined into a formal block later.

**Domain:** Anything not covered by existing blocks — new categories of thought, edge cases, novel domains

---

## Input

The raw reflection text is provided in conversation context.

---

## When to Use R00

Generate R00 when the reflection contains meaningful content that:
- Doesn't fit R01-R09 categories
- Represents a potentially new category of V's thinking
- Would be lost or distorted if force-fit into existing blocks

Do NOT use R00 for:
- Content that genuinely fits existing blocks (even if imperfectly)
- Low-signal tangents or asides
- Content that's just "misc" without coherent theme

---

## Output Format

```markdown
## R00: Emergent — [Provisional Category Name]

**Domain Detected:** [What area of thinking is this?]
**Why Emergent:** [Why doesn't this fit existing blocks?]

### Provisional Framework

**Core Element 1:** [What's the main thing to capture?]
**Core Element 2:** [Secondary dimension]
**Core Element 3:** [Tertiary dimension if applicable]

### Extracted Content

[Apply the provisional framework to extract the actual content from the reflection]

### Framework Notes

**Recurrence Potential:** One-off / Might recur / Definitely a pattern
**Suggested Block Name:** [If this becomes a formal block, what would it be called?]
**Suggested Block ID:** R10, R11, etc.
```

---

## Quality Standards

- Don't create R00 blocks casually — this is for genuinely novel content
- The provisional framework should be USEFUL for capturing this type of content, not generic
- Note if this seems like a one-off or a recurring pattern
- If you generate an R00, flag it for V's review as a potential new block type
- If the reflection fits existing blocks, DON'T use R00 — use the appropriate existing block


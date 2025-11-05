---
tool: true
description: Generate B24 intelligence block
tags:
  - meeting
  - intelligence
  - b24
---

# B24 - PRODUCT_IDEA_EXTRACTION Generation Prompt

You are generating a PRODUCT_IDEA_EXTRACTION intelligence block.

## Core Principle

Capture feature requests, product ideas, pain points that suggest product direction.

## Output Structure

### [Idea #]: [Short Title]

**What they said**: [Quote/paraphrase with timestamp]  
**The need**: [Underlying problem/pain point]  
**Frequency signal**: [One-off mention vs repeated emphasis]  
**Market signal**: [Just them or broader pattern?]  
**Feasibility gut-check**: [Quick assessment if mentioned]  
**Priority**: [HIGH/MEDIUM/LOW based on pain intensity]  
**Actionability**: [What we could do about this]

## Extraction Rules

### Include:
- Explicit feature requests ("I wish it could...")
- Pain points ("The hard part is...")
- Workarounds they've built (signals unmet need)
- Comparisons to competitors ("X does this well, but...")
- Process frustrations that software could solve

### Analyze:
- Is this a vitamin (nice-to-have) or painkiller (urgent need)?
- Is this unique to them or broader market signal?
- How intensely do they feel this pain?

## Quality Standards

✅ DO: Ground in quotes, assess pain intensity, note if repeated, evaluate market breadth  
❌ DON'T: Miss implicit pain points, ignore workarounds, fail to prioritize

## Edge Cases

**No product ideas**: Output: "No explicit product ideas or feature requests discussed."  
**Contradictory signals**: Note: "UNCERTAIN - Expressed interest but also said [contrary point]"

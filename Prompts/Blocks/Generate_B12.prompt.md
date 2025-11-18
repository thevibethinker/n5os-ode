---
description: Generate B12 Questions Raised block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b12
  - questions
tool: true
---
# Generate Block B12: Questions Raised

**Input:** Meeting transcript provided in conversation context

**Your task:** Generate a B12 Questions Raised block capturing substantive questions and discussion points from the meeting.

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
---

# B12: Questions Raised

## Strategic Questions
[High-level strategic questions discussed]

## Tactical Questions
[Operational/implementation questions]

## Unresolved Questions
[Questions that remain open for follow-up]
```

## Quality Standards
- Real questions from transcript only (no invented questions per P29)
- Include context for why each question matters
- Distinguish between answered and unanswered questions
- Quote verbatim when possible for strategic questions
- Min 200 words

**Generate the B12 block now using the transcript provided in this conversation.**


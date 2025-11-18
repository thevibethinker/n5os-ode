---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
block_code: B01
block_name: DETAILED_RECAP
category: core
---

# B01: Detailed Recap

## Objective

Generate a comprehensive narrative summary of the entire meeting conversation, capturing the arc of discussion, key topics covered, and natural flow of the conversation.

## Output Format

A well-structured markdown narrative (500-800 words) organized chronologically or thematically. Use clear section headers where appropriate. Write in past tense, third person.

## Quality Criteria

**Good B01 includes:**
- Natural narrative flow that tracks the conversation
- All major topics discussed (nothing significant omitted)
- Speaker attributions for key points
- Context for why topics came up
- Transitions between discussion areas
- Both substance AND dynamics of the conversation

**Avoid:**
- Bullet-point lists (this is narrative, not outline)
- Verbatim transcript quotes (synthesize instead)
- Speculation beyond what was said
- Missing significant discussion threads

## Instructions

1. Read the entire transcript carefully
2. Identify the main discussion phases/topics
3. Write a flowing narrative that captures:
   - What was discussed
   - Who raised what points
   - How the conversation evolved
   - Key insights or realizations that emerged
4. Organize logically (chronological or thematic)
5. Include specific details that matter (names, numbers, dates)
6. Capture tone shifts or notable interaction moments

## Edge Cases

**If meeting was very short (<5 min):**
- Still write narrative, just briefer (200-300 words)
- Focus on what WAS discussed comprehensively

**If meeting was unfocused/rambling:**
- Organize recap thematically rather than chronologically
- Group related threads together

**If highly technical:**
- Include technical specifics but explain them contextually
- Don't oversimplify, but make accessible to V

## Example Structure

```markdown
## B01_DETAILED_RECAP

The meeting began with [Speaker] providing an update on [topic], explaining that [key point]. This led to a discussion about [related area], where [Speaker 2] raised concerns about [specific issue].

The conversation then shifted to [next major topic]... [continue narrative]

Toward the end, the group discussed [final topic], reaching consensus that [outcome]. The meeting concluded with [final points].
```

## Validation

Before finalizing, check:
- [ ] All major topics from transcript are included
- [ ] Narrative flows naturally (not choppy)
- [ ] Speaker attributions present for key points
- [ ] No hallucinated information
- [ ] Length appropriate (500-800 words for typical meeting)
- [ ] Written in past tense, third person


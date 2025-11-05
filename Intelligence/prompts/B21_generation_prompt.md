---
tool: true
description: Generate B21 intelligence block
tags:
  - meeting
  - intelligence
  - b21
---

# B21 - KEY_MOMENTS Generation Prompt

You are generating a KEY_MOMENTS intelligence block from a meeting transcript.

## Core Principle

Capture the 5-10 most MEMORABLE and REVEALING moments—quotes and questions that expose personality, priorities, decision-making style, and relationship dynamics.

## Output Structure

### MEMORABLE QUOTES

### [Number]. **"[Exact quote from transcript]"** ([Speaker, timestamp])
   - **Context**: [What prompted this / what was being discussed]
   - **Why it matters**: [What this reveals about speaker/situation]
   - **Reveals**: [Personality trait, priority, mindset, belief, emotional state]

### SALIENT QUESTIONS

### [Number]. **"[Exact question asked]"** ([Speaker, timestamp])
   - **Why it matters**: [What this question reveals about priorities/concerns]
   - **Who asked**: [Speaker name]
   - **Action hint**: [If this question indicates need for follow-up/deliverable]

## Selection Criteria

### Memorable Quotes - Look For:
1. **Vulnerability moments**: Admitting uncertainty, sharing challenges
2. **Passion signals**: Strong emotion/energy around specific topics
3. **Decision criteria reveal**: "The key factor for us is..."
4. **Credibility signals**: Compliments, validation, enthusiasm
5. **Hesitation/resistance**: Where they pushed back or expressed doubt
6. **Transformation narratives**: Before/after stories about change
7. **Distinctive phrasing**: Unique way of expressing common idea

### Salient Questions - Look For:
1. **Priority signals**: Their LAST question (closing priority)
2. **Curiosity areas**: Deep dive questions vs surface questions
3. **Buying signals**: Questions about implementation, pricing, next steps
4. **Risk concerns**: "What if X happens?" or "How do you handle Y?"
5. **Validation seeking**: Checking if their understanding is correct

## Extraction Rules

### Include:
- 3-5 memorable quotes (quality over quantity)
- 3-5 salient questions
- EXACT wording from transcript
- Timestamps for all items

### Exclude:
- Generic pleasantries ("Thanks for your time")
- Logistical questions ("What time works for you?")
- Quotes that require extensive context to understand
- Redundant expressions of same sentiment

## Quality Standards

✅ **DO:**
- Use EXACT quotes (character-for-character)
- Explain what's revealed about the speaker
- Note action hints from questions
- Prioritize moments that surprised you or had emotional weight
- Include timestamp for traceability

❌ **DON'T:**
- Paraphrase or clean up quotes
- Miss the speaker's closing question (high signal)
- Ignore vulnerability/hesitation moments
- List obvious statements without insight value
- Forget timestamps

## Example Quality Indicators

**HIGH QUALITY:**
### 1. **"Are you serious?"** (Elaine, 26:26)
   - **Context**: Reaction to learning Vrijen built entire N5 system in Zo, not Cursor
   - **Why it matters**: Genuine surprise/excitement about Zo's capabilities
   - **Reveals**: Technically literate enough to appreciate the accomplishment, primed for Zo adoption

**LOW QUALITY:**
### 1. **"That's interesting"** (John, 15:30)
   - **Context**: During product demo
   - **Why it matters**: Shows interest
   - **Reveals**: John is engaged

## Edge Cases

**Few memorable moments**: Quality over quantity—3 great quotes better than 10 mediocre ones

**Highly technical conversation**: Still look for personality/priority reveals in HOW they engage with technical topics

**Multiple speakers**: Balance representation but prioritize external stakeholder moments

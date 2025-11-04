# B07 - WARM_INTRO_BIDIRECTIONAL Generation Prompt

You are generating a WARM_INTRO_BIDIRECTIONAL intelligence block from a meeting transcript.

## Core Principle

Track potential introductions mentioned during conversation—both directions (who they could introduce us to, who we could introduce them to).

## Output Structure

### Introductions THEY Could Make for US

**[Contact Name/Description]**
- **Why valuable**: [What this person could offer Careerspan]
- **Context**: [How it came up in conversation - quote/timestamp]
- **Warm intro quality**: [Strong/Medium/Weak - based on their relationship]
- **Ask timing**: [Immediate/After milestone/Long-term relationship building]
- **How to frame the ask**: [Specific language to use]

### Introductions WE Could Make for THEM

**[Contact Name/Description]**
- **Why valuable to them**: [What they're seeking/what this solves]
- **Context**: [How it came up - their need/interest]
- **Our connection strength**: [Strong/Medium/Weak]
- **Timing**: [Immediate/Wait for signal/Conditional]
- **Value to relationship**: [How making this intro helps us]

## Extraction Rules

### Include:
1. **Explicit requests**: "Could you introduce me to X?"
2. **Implicit signals**: "I'd love to meet someone who does Y"
3. **Name drops**: "Do you know Z?" (if relevant)
4. **Network mapping**: "How do you know [Person]?"
5. **Mutual connections discovered**: Overlapping networks

### Exclude:
- Generic "we should network" without specific targets
- Introductions already made (past tense)
- People mentioned but no intro interest indicated

## Quality Standards

✅ **DO:**
- Assess intro quality (do they actually know them well?)
- Consider timing (too early to ask?)
- Frame the value exchange (why intro benefits everyone)
- Note any sensitive context (competitors, conflicts)

❌ **DON'T:**
- Assume every name mentioned = intro opportunity
- Miss bidirectional possibilities
- Forget to assess relationship strength
- Ignore timing considerations

## Edge Cases

**No warm intros discussed**: Output: "No explicit warm introductions discussed in this meeting."

**Unclear if intro desired**: Note as "POTENTIAL - Monitor for future signal: [Person mentioned, context]"

**Sensitive intros** (competitors, former employers): Flag with "CAUTION - [specific consideration]"

---
description: Generate B05 Action Items block - commitments and to-dos from meeting
tags: [meeting-intelligence, block-generation, b05, action-items]
tool: true
created: 2025-11-03
last_edited: 2026-01-21
version: 2.0
---
# Generate Block B05: Action Items

Extract explicit commitments, to-dos, and follow-up actions from the transcript.

## Output Format

**REQUIRED YAML FRONTMATTER:**
```yaml
---
created: {YYYY-MM-DD}
last_edited: {YYYY-MM-DD}
version: 1.0
provenance: {agent_id or conversation_id}
---
```

**REQUIRED STRUCTURE:**

```markdown
# B05: Action Items

## Immediate Actions (Next 48 Hours)

| Owner | Action | Context | Mentioned At |
|-------|--------|---------|--------------|
| {Name} | {Specific deliverable} | {Why/what triggered this} | {Approximate timestamp} |

## Near-Term Actions (This Week)

| Owner | Action | Context | Deadline |
|-------|--------|---------|----------|
| ... | ... | ... | ... |

## Open Loops / Follow-Ups

- **{Topic}**: {What needs resolution} — Owner: {Name}
- ...

## Commitments Made

- {Name} committed to {specific action} for {recipient/purpose}
- ...
```

## Extraction Rules

1. **ONLY EXPLICIT COMMITMENTS**
   - "I'll send you..." → Action item
   - "We should..." → NOT an action item (too vague)
   - "Let me check on..." → Action item with owner

2. **IDENTIFY OWNERS CLEARLY**
   - Use actual names from transcript
   - If unclear who owns it, note "TBD - needs clarification"

3. **INCLUDE CONTEXT**
   - Why was this action mentioned?
   - What triggered the commitment?
   - Who is the recipient/beneficiary?

4. **TIME SENSITIVITY**
   - Note any explicit deadlines ("by Friday", "next week")
   - Infer urgency from context if not explicit

## Anti-Patterns (NEVER DO THESE)

❌ Copying transcript quotes verbatim
❌ "- Speaker: [quote from transcript]"
❌ Generic actions like "follow up" without specifics
❌ Including discussion points that aren't actionable
❌ Missing owner/accountability

## Example of GOOD vs BAD Output

**BAD:**
```markdown
### Action Items
- Vrijen Attawar: I'll call you and explain why.
- Trinayaan: Let me just give you context.
```

**GOOD:**
```markdown
---
created: 2026-01-21
last_edited: 2026-01-21
version: 1.0
provenance: agent_xyz123
---

# B05: Action Items

## Immediate Actions (Next 48 Hours)

| Owner | Action | Context | Mentioned At |
|-------|--------|---------|--------------|
| Vrijen | Send intro email to Ben at Zo | Trinayaan expressed interest in AI productivity tools | ~15:00 |
| Trinayaan | Share GitHub repo with take-home project feedback | Discussed hiring process pain points | ~22:00 |

## Open Loops / Follow-Ups

- **Careerspan partnership**: Explore whether coaching data could help with technical hiring signal — Owner: Vrijen
- **Interview process feedback system**: Trinayaan mentioned building something, V offered to help test — Owner: Both

## Commitments Made

- Vrijen committed to making an introduction to the Zo team
- Trinayaan committed to sharing his hiring process analysis
```

---

**Generate the B05 block now using the transcript provided.**

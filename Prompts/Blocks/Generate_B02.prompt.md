---
description: Generate B02 Commitments & Actions block from meeting transcript
tags: [meeting-intelligence, block-generation, b02, commitments, action-items, task-decomposition]
tool: true
created: 2025-11-03
last_edited: 2026-02-01
version: 4.0
provenance: con_QfbFKjSTBb0cNEIt
---

# Generate B02: Commitments & Actions

Extract commitments and action items from the meeting transcript. This unified block captures both explicit promises (commitments) and concrete tasks (action items).

## Commitment vs Action Item

**Commitment** = Explicit promise or agreement made during the meeting
- Language signals: "I commit to...", "We will...", "I promise...", "You have my word..."
- Focus: The obligation itself, why it matters, accountability
- May or may not have specific next steps

**Action Item** = Concrete task that needs to be done
- Language signals: "I'll send...", "Let me check...", "Need to...", "Follow up on..."
- Focus: What, who, when, first step
- Always has decomposable structure

Some commitments generate action items. Some action items aren't commitments (just tasks). Capture both.

## Input

You will receive:
1. **Transcript content** - Full meeting transcript
2. **Meeting metadata** (optional) - Context about meeting type, participants

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
# B02: Commitments & Actions

## Commitments

| Commitment | Who | To Whom | Why It Matters | Status |
|------------|-----|---------|----------------|--------|
| [Explicit promise] | [Owner] | [Recipient] | [Stakes/context] | [Pending/Fulfilled] |

## Action Items

### 1. [Action item title]
- **Owner**: [Name or "Unassigned"]
- **Priority**: [external|strategic|urgent|normal]
- **Commitment**: [Yes - links to commitment above | No]
- **First Step**: [Specific 2-minute actionable step]
- **Estimated**: [X min]
- **Domain**: [Careerspan|Zo|Personal|Other]
- **Dependencies**: [Blockers or prerequisites, if any]
- **Due**: [Date if stated, or "Not specified"]

[Repeat for each action item]
```

## Commitment Extraction

### Language Patterns to Look For:
- "I commit to..."
- "We will deliver..."
- "I promise you..."
- "You have my word..."
- "We're committed to..."
- "I guarantee..."
- Explicit agreements: "Deal", "Agreed", "Done"

### Commitment Table Fields:
- **Commitment**: The exact promise (preserve original language)
- **Who**: Person making the commitment
- **To Whom**: Person/party receiving the commitment (counterparty, team, self)
- **Why It Matters**: Stakes, context, what's at risk if broken
- **Status**: Default "Pending" unless explicitly fulfilled

## Action Item Extraction

### Priority Bucket Definitions:
- **external**: Commitment to external party (investors, partners, customers) - always high priority
- **strategic**: Long-term impact, foundational work, decisions that shape direction
- **urgent**: Time-sensitive, deadline-driven, blocking other work
- **normal**: Routine tasks, ongoing work without time pressure

### Domain Inference:
- **Careerspan**: Careerspan business, clients, partnerships, product work
- **Zo**: Zo system development, N5 tasks, personal productivity infrastructure
- **Personal**: Non-work items (health, finances, relationships)
- **Other**: Everything else (unclear context)

### First Step Rule (2-Minute Rule):
The "First Step" should be:
- Actionable in 2 minutes or less
- Clearly defined (no ambiguity)
- The absolute smallest move forward
- Not "think about" or "plan to" - must be DO

Examples:
- ✅ "Open email to Sarah, write 2-sentence check-in"
- ✅ "Create new folder for project files"
- ✅ "Draft agenda bullet points"
- ❌ "Plan the project"
- ❌ "Think about approach"
- ❌ "Research the topic" (too vague)

### Time Estimation Guidelines:
- **5 min**: Quick email, message, small edit
- **15 min**: Draft document, review materials, focused work
- **30 min**: Substantial writing, call prep, research
- **60 min+**: Deep work, complex deliverable

Be realistic - prefer overestimation by 20% than underestimation.

## Owner Attribution

Default to "Vrijen" unless:
- Explicitly assigned to someone else in the transcript
- Clear it's the counterparty's responsibility
- Use "Unassigned" if ownership is ambiguous

## Extraction Rules

1. **ONLY EXPLICIT CONTENT**
   - "I commit to delivering by Friday" → Commitment + Action item
   - "I'll send you the doc" → Action item
   - "We should..." → NOT captured (too vague)
   - "Let me check on..." → Action item with owner

2. **LINK COMMITMENTS TO ACTIONS**
   - If a commitment generates an action item, mark "Commitment: Yes" on that action
   - Reference which commitment it fulfills

3. **NO HALLUCINATIONS**
   - Only extract items explicitly discussed
   - Don't infer commitments from tone
   - Don't create action items from suggestions

4. **REAL DATES ONLY**
   - Use stated dates or "Not specified"
   - No "TBD" - either there's a date or there isn't (per P29)

## Quality Standards

- **No hallucinations**: Only extract items explicitly discussed
- **No vague items**: Every item must be specific and actionable
- **Preserve accountability**: Track who committed to whom
- **Complete fields**: Every action item must have all required fields

## Example Output

```markdown
---
created: 2026-02-01
last_edited: 2026-02-01
version: 1.0
provenance: agent_xyz123
---

# B02: Commitments & Actions

## Commitments

| Commitment | Who | To Whom | Why It Matters | Status |
|------------|-----|---------|----------------|--------|
| Deliver revised partnership terms by Friday | Vrijen | Sarah Chen | Partnership kickoff depends on this | Pending |
| Provide engineering resources for integration | Sarah Chen | Vrijen | Blocks product roadmap | Pending |

## Action Items

### 1. Send revised partnership terms to Sarah
- **Owner**: Vrijen
- **Priority**: external
- **Commitment**: Yes (links to commitment #1)
- **First Step**: Open partnership template, review current terms
- **Estimated**: 30 min
- **Domain**: Careerspan
- **Dependencies**: Need latest pricing from finance team
- **Due**: Friday

### 2. Schedule integration planning call
- **Owner**: Sarah Chen
- **Priority**: strategic
- **Commitment**: No
- **First Step**: (Sarah's action)
- **Estimated**: 5 min
- **Domain**: Careerspan
- **Dependencies**: None
- **Due**: Not specified

### 3. Review investor memo
- **Owner**: Vrijen
- **Priority**: strategic
- **Commitment**: No
- **First Step**: Open memo draft, read first section
- **Estimated**: 15 min
- **Domain**: Careerspan
- **Dependencies**: None
- **Due**: Before Monday board call
```

## No Commitments or Action Items?

If neither found:

```markdown
# B02: Commitments & Actions

## Commitments

No explicit commitments made in this meeting.

## Action Items

No action items identified in this meeting.
```

## Process

1. Read transcript thoroughly
2. First pass: Identify commitments (explicit promises with accountability)
3. Second pass: Identify action items (concrete tasks)
4. Link action items to commitments where applicable
5. Decompose each action item according to format
6. Output in structured markdown format above

---

**Generate the B02 block now using the transcript provided.**

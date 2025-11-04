# B02 - COMMITMENTS_CONTEXTUAL Generation Prompt

You are generating a COMMITMENTS_CONTEXTUAL intelligence block from a meeting transcript.

## Input
- Meeting transcript with timestamps
- Attendee list
- Meeting metadata

## Output Format

Generate a markdown table with exactly 5 columns:

| Owner | Deliverable | Context/Why | Due Date | Dependencies |
|-------|------------|-------------|----------|--------------|
| [Name] | [Action] | [Strategic context] | [Timeline] | [Blockers/Prerequisites] |

## Column Specifications

### Owner
- **For Careerspan team:** Use "We (Vrijen)", "We (Logan)", "We (Team)", etc.
- **For external stakeholders:** Use their specific name
- **For shared responsibility:** List both parties: "We (Vrijen) & Alex"
- **For unclear ownership:** Use "TBD" but flag in Context/Why that ownership needs clarification

### Deliverable
- Concrete, actionable output or action
- Specific enough to verify completion
- Use infinitive form: "Share resources", "Schedule follow-up", "Review proposal"
- If commitment is conditional, note condition: "If budget approved: Sign contract"

### Context/Why
**This is the most important column** - explain strategic value:
- Why this commitment matters for the relationship
- What problem it solves
- How it advances the deal/partnership/conversation
- Connection to stakeholder pain points or priorities
- Risk if not completed

**DON'T:** Simply restate the deliverable
**DO:** Explain strategic importance

Examples:
- ❌ "Send follow-up email" → "Need to maintain contact"
- ✅ "Send follow-up email" → "Closes conversation loop and maintains momentum while Alex evaluates budget internally (2-week decision window)"

### Due Date
- **Preserve exact language from transcript:** "EOD Friday", "next Tuesday", "within 48 hours", "early next week"
- **If no explicit date:** Use relative timeframe based on urgency cues: "Within 1 week", "Before Q4", "ASAP"
- **If truly unclear:** Use "TBD" but note in Context/Why
- **Don't invent precision:** If they said "soon", write "Soon" not "Within 3 days"

### Dependencies
- What must happen before this commitment can be fulfilled?
- What's blocking this action?
- What does this action unlock for other commitments?
- External factors (approvals, resources, third parties)
- If no dependencies: "None"

## Extraction Rules

### Include:
1. **Explicit commitments:** "I'll send you X", "We'll have that ready by Y"
2. **Implied commitments:** "Let me check with my team" = commitment to follow up
3. **Conditional commitments:** "If X happens, I'll do Y"
4. **Mutual commitments:** BOTH "we owe them" AND "they owe us"
5. **Follow-up meetings:** "Let's reconnect next week" = commitment to schedule

### Exclude:
- Vague intentions without commitment: "Maybe we could...", "It would be nice to..."
- Past actions already completed during the call
- General discussion topics that didn't result in action

## Quality Standards

✅ **DO:**
- Capture commitments from ALL parties (bidirectional)
- Preserve transcript language for dates/timelines
- Explain strategic value in Context/Why column
- Identify dependencies that could cause delays
- If no commitments exist, create table but note: "No explicit action items or commitments discussed in this meeting"

❌ **DON'T:**
- Miss commitments we owe them OR they owe us
- Invent artificial precision for timelines
- Write generic context that just repeats deliverable
- Ignore implicit commitments (follow-ups, checks, etc.)
- List more than 10 commitments (focus on meaningful actions, not minutiae)

## Example Quality Indicators

**HIGH QUALITY:**
| Owner | Deliverable | Context/Why | Due Date | Dependencies |
|-------|------------|-------------|----------|--------------|
| We (Vrijen) | Share AI learning resources (YouTube: Nate B. Jones, 3Blue1Brown) + intermediate materials | Elaine explicitly asked "how do you learn about design patterns?" - positions Vrijen as expert resource and supports her learning journey | Within 72 hours | None - resources already identified |
| Elaine | Try Zo platform | Expressed interest after demo ("I'll definitely check it out") - potential advocate/user if it resonates. Critical for gathering feedback from technical audience | Self-directed | Promo code shared (VA-T5) |

**LOW QUALITY:**
| Owner | Deliverable | Context/Why | Due Date | Dependencies |
|-------|------------|-------------|----------|--------------|
| Vrijen | Send stuff | Important to follow up | Soon | N/A |
| Elaine | Test platform | She wants to try it | Later | None |

## Edge Cases

**No commitments:** Create file with header and single row:
| Owner | Deliverable | Context/Why | Due Date | Dependencies |
|-------|------------|-------------|----------|--------------|
| - | No explicit action items or commitments discussed | This was an exploratory/informational conversation without concrete next steps defined | - | - |

**Too many commitments (>10):** Prioritize by:
1. Time-sensitive commitments
2. Deal-critical commitments
3. Relationship-maintaining commitments
4. Nice-to-have commitments (drop these)

**Ambiguous ownership:** Flag in Context/Why: "Ownership unclear - both parties mentioned willingness but no explicit agreement on who leads"

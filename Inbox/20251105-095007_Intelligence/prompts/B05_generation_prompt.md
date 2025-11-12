---
tool: true
description: Generate B05 intelligence block
tags:
  - meeting
  - intelligence
  - b05
---

# B05 - OUTSTANDING_QUESTIONS Generation Prompt

You are generating an OUTSTANDING_QUESTIONS intelligence block from a meeting transcript.

## Core Principle

Capture questions/uncertainties that BLOCK progress or need resolution. Not every question is worth tracking—focus on questions that have IMPACT if left unresolved.

## Output Structure

For each outstanding question, use this format:

---

### [Number]. [The specific question]

**Owner**: [Who needs to answer/resolve this]  
**Needed by**: [When/why this needs resolution]  
**Blocker type**: [Category - see below]  
**Unblocking action**: [Concrete next step to resolve]  
**Impact if delayed**: [What breaks/suffers if this isn't answered]

---

## Blocker Type Categories

- **UNCLEAR_REQUIREMENT**: Ambiguity about what's actually needed
- **WAITING_ON_DATA**: Missing information from external source
- **DEPENDENCY**: Blocked by someone else's action/decision
- **TECHNICAL_UNKNOWN**: Need to investigate feasibility/approach
- **DECISION_PENDING**: Waiting for strategic/tactical decision
- **RESOURCE_CONSTRAINT**: Unclear if we have budget/time/people
- **SCOPE_CREEP**: Definition of "done" is unclear

## Extraction Rules

### Include Questions That:
1. **Block commitments**: "I'll do X once we know Y"
2. **Indicate uncertainty**: "I'm not sure if...", "We need to figure out..."
3. **Require clarification**: "What exactly do you mean by...?"
4. **Reveal missing information**: Gaps noticed during conversation
5. **Create risk**: "If we don't know X, then Y could fail"

### Exclude Questions That:
1. Were answered during the meeting
2. Are rhetorical or conversational
3. Have no actionable consequence
4. Are "nice to know" but not blocking anything

## Quality Standards

✅ **DO:**
- Frame as specific, actionable questions
- Identify WHO owns resolution (even if it's "TBD")
- Explain IMPACT—why this matters
- Provide concrete unblocking action
- Prioritize by criticality (time-sensitive first)

❌ **DON'T:**
- List questions that were resolved in the meeting
- Include vague uncertainties without impact
- Miss implicit blockers (things mentioned as "need to check")
- Forget to specify owner and unblocking action

## Example Quality Indicators

**HIGH QUALITY:**
### 1. What's the pricing model for enterprise tier?

**Owner**: We (Logan/Vrijen)  
**Needed by**: Before proposal delivery (Oct 30)  
**Blocker type**: UNCLEAR_REQUIREMENT  
**Unblocking action**: Review pricing research doc + internal decision on enterprise packaging  
**Impact if delayed**: Cannot provide accurate proposal, risks looking unprepared

**LOW QUALITY:**
### 1. What do they think about our product?

**Owner**: Them  
**Needed by**: Eventually  
**Blocker type**: Unknown  
**Unblocking action**: Ask them  
**Impact if delayed**: We won't know

## Edge Cases

**No outstanding questions**: Create file with: "No blocking questions or uncertainties identified. All discussed items were resolved or clarified during the meeting."

**Too many questions (>8)**: Prioritize by:
1. Time-critical blockers
2. Deal/relationship-critical items
3. Nice-to-know items (drop these)

**Unclear ownership**: Use "TBD" but note in Unblocking action who should clarify ownership

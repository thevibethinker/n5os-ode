# N5 System - Architectural Principles

**Version:** 1.0  
**Date:** 2025-10-13  
**Purpose:** Core design principles for information architecture across N5 system

---

## MECEM Principle: Information Storage Architecture

**MECEM = Mutually Exclusive, Collectively Exhaustive, Minimally Repeating**

*Framework for AI information architecture*

### Core Tenets

1. **Mutually Exclusive**
   - Each piece of information belongs in exactly ONE canonical location
   - No overlap between blocks/documents
   - Clear boundaries between information types

2. **Collectively Exhaustive**
   - All relevant information is captured SOMEWHERE in the system
   - No gaps in intelligence gathering
   - Complete coverage of meeting intelligence

3. **Minimally Repeated**
   - Information stored once, referenced everywhere
   - Use pointers and cross-references instead of duplication
   - When repetition is necessary (e.g., for readability), mark it as derivative

### Implementation Guidelines

#### For Block Design
- Each block has a distinct, non-overlapping purpose
- Strategic context lives in B40 (INTERNAL_DECISIONS)
- Action items reference B40 for context (don't duplicate it)
- Use block references: "See B40.D3 for strategic rationale"

#### For Decision Tracking
- Strategic reasoning: B40
- Tactical execution: B40 (linked to strategic)
- Action items: B41 (pointers to B40 decisions)
- Open debates: B47 (unresolved strategic items only)

#### Cross-References Format
- Between blocks: `[See B40.D3]` (Block 40, Decision 3)
- Between meetings: `[See 2025-08-27_internal-team/B40.D5]`
- Within block: `[Relates to D1 above]`

#### When to Break MISI
Acceptable exceptions:
1. **B26 (MEETING_METADATA)** - Can summarize key points for quick reference
2. **B48 (STRATEGIC_MEMO)** - Synthesizes across blocks for executive summary
3. **Readability** - Brief context reminders when jumping between sections

### Examples

**BAD (Violates MISI):**
```
B40: "Decided to hire 2 engineers because we need to ship Q2 roadmap faster"
B41: "Vrijen: Post job descriptions | Context: Need to ship Q2 roadmap faster | Due: EOW"
```
*Problem: Strategic context duplicated*

**GOOD (Follows MISI):**
```
B40.D3: "Decided to hire 2 engineers because we need to ship Q2 roadmap faster"
B41: "Vrijen: Post job descriptions for 2 engineers [B40.D3] | Due: EOW"
```
*Solution: Context stored once, referenced in action*

---

## Decision Architecture: Two-Axis Framework

### Axis 1: Strategic vs. Tactical
- **Strategic**: Changes direction, defines objectives, sets priorities
- **Tactical**: Executes on strategy, implements specific approaches

### Axis 2: Decision Type
- Product (features, architecture, UX)
- Go-to-Market (positioning, pricing, distribution)
- Operations (processes, tools, workflows)
- Hiring (roles, compensation, team structure)
- Investment/Fundraising (capital allocation, investor relations)
- Partnerships (integrations, collaborations)

### Interrelationships
- Strategic decisions spawn tactical decisions
- Tactical execution validates/invalidates strategic assumptions
- Document: "Strategic decision X requires tactical decisions Y, Z"
- Document: "Tactical decision A supports strategic objectives B, C"

### The "Holistic Push"
Every major strategic initiative should capture:
1. **Strategic Rationale**: Why we're doing this (objectives, assumptions, success criteria)
2. **Tactical Execution Path**: How we'll do it (individual blocks/actions)
3. **Interrelationships**: How tactical blocks achieve strategic objective
4. **Dependencies**: What needs to happen first, what this enables

---

## Tactical Disagreements: Resolution Protocol

When tactical disagreements arise during meetings:

1. **If Resolved During Meeting**
   - Capture the conclusion in B40 (tactical decision)
   - Note the disagreement briefly: "Initially debated X vs Y, chose X because..."
   - Mark as RESOLVED

2. **If Not Resolved During Meeting**
   - If it's a tactical detail that doesn't block progress: Capture in B47 as open question
   - If it's blocking: Escalate to B40 as a decision that needs follow-up
   - If it reveals strategic uncertainty: Mark in B47 as strategic open debate

3. **Strategic Debates**
   - Always go to B47 (OPEN_DEBATES)
   - These are unresolved strategic questions, not tactical details

---

## Block Namespace Design

### External Stakeholder Blocks: B01-B39
- B01-B31: Existing external blocks
- B32-B39: Reserved for future external blocks

### Internal Stakeholder Blocks: B40-B59
- B40-B48: Core internal intelligence blocks
- B49-B59: Reserved for future internal blocks

### System/Meta Blocks: B60+
- Reserved for cross-meeting aggregation, system-level intelligence

---

## Application: Internal Meeting Intelligence

### Information Flow
```
Meeting Transcript
    ↓
B26 (Metadata: Quick reference)
    ↓
B40 (Decisions: Strategic + Tactical with interrelationships)
    ↓           ↓                    ↓
B41 (Actions)  B42-B46 (Intelligence)  B47 (Open Debates)
    ↓
B48 (Strategic Memo: Synthesizes all above)
```

### Avoiding Overlap
- **B40**: What we decided and why (strategic rationale + tactical approach)
- **B41**: Who does what by when (references B40 for why)
- **B42-B46**: Market/competitive/product intelligence extracted from discussion
- **B47**: What we haven't decided yet (strategic uncertainty)
- **B48**: Executive summary synthesizing B40, B41, B47

---

## Review Checklist

When creating/reviewing blocks, ask:

1. ✓ **Mutually Exclusive**: Does this information exist elsewhere?
2. ✓ **Collectively Exhaustive**: Have I captured everything relevant?
3. ✓ **Minimally Repeated**: Am I duplicating context unnecessarily?
4. ✓ **Clear References**: Do I use pointers instead of repetition?
5. ✓ **Correct Location**: Is this in the canonical block for this info type?

---

## Version History

- **v1.0** (2025-10-13): Initial architectural principles document
  - MECEM principle codified
  - Two-axis decision framework
  - Tactical disagreement protocol
  - Block namespace design

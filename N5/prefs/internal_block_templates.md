# Internal Meeting Block Templates

**Version:** 1.0  
**Date:** 2025-10-13  
**Purpose:** Generation guidance for internal meeting blocks B40-B48

---

## B40_INTERNAL_DECISIONS Template

```markdown
# B40 - INTERNAL_DECISIONS

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]  
**Attendees:** [Names]

---

## Strategic Decisions

| ID | Decision | Type | Rationale | Related Tactical |
|----|----------|------|-----------|------------------|
| D1 | [Decision text] | [Product/GTM/Ops/Hiring/Investment/Partnerships] | [Why this decision] | [T1, T2] |
| D2 | ... | ... | ... | ... |

---

## Tactical Decisions

| ID | Decision | Type | Rationale | Supports Strategic |
|----|----------|------|-----------|-------------------|
| T1 | [Decision text] | [Type] | [Why this approach] | [D1] |
| T2 | ... | ... | ... | ... |

---

## Holistic Pushes

### [Initiative Name]

**Strategic Rationale:** [Why are we doing this? What's the big picture goal?]

**Tactical Execution Blocks:**
1. [Specific executable block 1]
2. [Specific executable block 2]
3. [Specific executable block 3]

**Dependencies:** [What needs to be in place first]

**Success Criteria:** [How we know we've succeeded]

**Related Decisions:** [D#, T#]

---

## Resolved Tactical Debates

### [Debate Topic]

**Options Considered:**
- Option A: [Description]
- Option B: [Description]

**Resolution:** [What we decided]

**Rationale:** [Why we chose this]

**Settled Date:** [YYYY-MM-DD]

---

**Generated:** [Timestamp]
```

---

## B41_TEAM_COORDINATION Template

```markdown
# B41 - TEAM_COORDINATION

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Action Items

| Owner | Action | Context | Due Date | Dependencies | Status |
|-------|--------|---------|----------|--------------|--------|
| [Name] | [Specific deliverable] | [B40.D#] or [B40.T#] | [Date] | [What's needed first] | 🔴 Not Started |
| [Name] | [Action] | [Context ref] | [Date] | None | 🟡 In Progress |
| [Name] | [Action] | [Context ref] | [Date] | [Dep] | 🟢 Complete |

---

## Dependencies & Blockers

### Critical Path
1. [Action 1] → [Action 2] → [Action 3]

### Current Blockers
- 🔴 **[Blocker]**: [Description] - Blocking: [Actions] - Owner: [Name]
- 🟡 **[Risk]**: [Description] - May block: [Actions] - Mitigation: [Plan]

---

## Team Capacity Notes

[Any capacity constraints, availability issues, or resource allocation notes discussed]

---

**Generated:** [Timestamp]
```

---

## B42_MARKET_COMPETITIVE_INTEL Template

```markdown
# B42 - MARKET_COMPETITIVE_INTEL

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Market Trends

### [Trend Name]

**What's changing:** [Description]

**Evidence:** [What we're seeing]

**Impact on Careerspan:** [How this affects our strategy]

**Related decisions:** [B40.D#]

---

## Competitive Intelligence

### [Competitor/Category]

**What they're doing:** [Actions observed]

**Our read:** [Analysis of their strategy]

**Implications for us:** [How we should respond]

**Related decisions:** [B40.D#]

---

## Customer/ICP Insights

### [Insight]

**What we learned:** [Description]

**Source:** [Where this came from]

**Positioning implications:** [How this affects our messaging/positioning]

**Related decisions:** [B40.D#]

---

## Positioning Evolution

[How our understanding of positioning is evolving based on this intelligence]

---

**Generated:** [Timestamp]
```

---

## B43_PRODUCT_INTELLIGENCE Template

```markdown
# B43 - PRODUCT_INTELLIGENCE

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Product Strategy

**Current direction:** [Where we're heading]

**Strategic shifts:** [Any changes to product strategy - link to B40.D#]

**Rationale:** [Why this direction]

---

## Roadmap Updates

### Immediate (Next 2 weeks)
- [Feature/work] - Owner: [Name] - Why: [B40.D#]

### Near-term (2-8 weeks)
- [Feature/work] - Owner: [Name] - Why: [B40.D#]

### Future (8+ weeks)
- [Feature/work] - Owner: [Name] - Why: [B40.D#]

---

## Feature Decisions

### [Feature Name]

**Decision:** [Build/Kill/Postpone/Modify]

**Rationale:** [B40.D# or B40.T#]

**Technical approach:** [How we're building it]

**Success metrics:** [How we measure success]

---

## Technical Architecture

[Any architecture decisions or technical approach discussions]

**Related decisions:** [B40.T#]

---

## User Experience

[Any UX insights, design decisions, or user flow discussions]

---

**Generated:** [Timestamp]
```

---

## B44_GTM_SALES_INTEL Template

```markdown
# B44 - GTM_SALES_INTEL

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## GTM Strategy

**Current approach:** [Our go-to-market strategy]

**Strategic shifts:** [Changes discussed - link to B40.D#]

**Rationale:** [Why this approach]

---

## Sales Process

### Pipeline Status
[Current state of sales pipeline if discussed]

### Process Changes
[Any changes to sales process - link to B40.T#]

### Conversion Insights
[What we're learning about conversion]

---

## Pricing & Packaging

### Current Model
[What we're charging and how]

### Changes Discussed
[Any pricing/packaging changes - link to B40.D#]

### Rationale
[Why this pricing strategy]

---

## Distribution & Partnerships

### Channels
[Distribution channels we're using/considering]

### Partnership Strategy
[Partnership approach - link to B40.D#]

### Channel Performance
[What we're learning about different channels]

---

## Messaging & Positioning

### Core Message
[How we're talking about Careerspan]

### Positioning Shifts
[Any changes to positioning - link to B40.D#]

### What's Resonating
[What's working in conversations]

---

**Generated:** [Timestamp]
```

---

## B45_OPERATIONS_PROCESS Template

```markdown
# B45 - OPERATIONS_PROCESS

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Process Changes

### [Process Name]

**Old approach:** [How we used to do it]

**New approach:** [How we'll do it now]

**Rationale:** [B40.T#]

**Owner:** [Who's implementing]

**Timeline:** [When this takes effect]

---

## Tool Decisions

### [Tool Name]

**Decision:** [Adopt/Replace/Evaluate/Deprecate]

**Rationale:** [B40.T#]

**Implementation plan:** [How we roll this out]

**Owner:** [Who's responsible]

---

## Team Structure & Coordination

[Any organizational structure changes or coordination approaches]

**Related decisions:** [B40.D#]

---

## Efficiency Improvements

### [Improvement]

**Problem:** [What we're solving]

**Solution:** [How we're solving it]

**Expected impact:** [What we expect to gain]

**Related decisions:** [B40.T#]

---

**Generated:** [Timestamp]
```

---

## B46_HIRING_TEAM Template

```markdown
# B46 - HIRING_TEAM

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Hiring Decisions

### [Role Title]

**Decision:** [Hire/Don't Hire/Postpone]

**Rationale:** [B40.D#]

**Timeline:** [When to hire]

**Priority:** [High/Medium/Low]

---

## Role Definitions

### [Role Title]

**Responsibilities:**
- [Key responsibility 1]
- [Key responsibility 2]

**Requirements:**
- [Key requirement 1]
- [Key requirement 2]

**Why we need this:** [B40.D#]

---

## Compensation Strategy

[Any compensation, equity, or benefits decisions]

**Related decisions:** [B40.D#]

---

## Pipeline Status

### [Role]
- **Status:** [Sourcing/Interviewing/Offer/Hired]
- **Candidates:** [Number in pipeline]
- **Next steps:** [What's next]

---

**Generated:** [Timestamp]
```

---

## B47_OPEN_DEBATES Template

```markdown
# B47 - OPEN_DEBATES

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]

---

## Strategic Open Questions

### Q1: [Question]

**Type:** Strategic

**Context:** [Why this question matters]

**Perspectives:**
- **[Person]:** [Their view]
- **[Person]:** [Their view]

**What we need to resolve this:** [Info/decision/experiment needed]

**Next steps:** [How we'll address this]

**Related decisions:** [B40.D# if applicable]

---

## Tactical Open Questions

*(Only if blocking execution)*

### Q#: [Question]

**Type:** Tactical

**Context:** [Why this is unresolved]

**Blocking:** [What actions this blocks]

**Options:**
- Option A: [Description]
- Option B: [Description]

**Next steps:** [How we'll resolve]

---

## Trade-offs Under Consideration

### [Trade-off]

**Option A:** [Description] - Pros: [...] - Cons: [...]

**Option B:** [Description] - Pros: [...] - Cons: [...]

**Key factors to consider:** [What will drive the decision]

**Decision deadline:** [When we need to decide]

**Owner:** [Who's driving this decision]

---

**Generated:** [Timestamp]
```

---

## B48_STRATEGIC_MEMO Template

```markdown
# B48 - STRATEGIC_MEMO

**Meeting:** [Meeting title]  
**Date:** [YYYY-MM-DD]  
**Duration:** [Minutes]  
**Attendees:** [Names]

---

## Executive Summary

[2-3 sentences capturing the essence of this meeting - what was decided, what direction we're heading, what matters most]

---

## Key Strategic Decisions

### [Decision Category - Product/GTM/Ops/etc]

[Narrative summary of strategic decisions from B40, with references]

- **[Decision]** [B40.D1]: [Why this matters strategically]
- **[Decision]** [B40.D2]: [Impact and rationale]

---

## Major Initiatives

### [Initiative Name]

**Strategic Goal:** [What we're trying to achieve]

**Tactical Path:** [How we're executing - reference B40 tactical blocks]

**Owner:** [Who's leading]

**Timeline:** [When this happens]

**Success looks like:** [Concrete outcomes]

---

## Intelligence Highlights

### Market & Competitive [if B42 exists]
[Key insights from B42]

### Product [if B43 exists]
[Key insights from B43]

### GTM & Sales [if B44 exists]
[Key insights from B44]

### Operations [if B45 exists]
[Key insights from B45]

### Hiring [if B46 exists]
[Key insights from B46]

---

## Open Strategic Questions

[Summary from B47 - what major questions remain]

- **Q#:** [Question] - Why it matters - Next steps

---

## Critical Next Steps

[From B41 - the most critical actions that will move us forward]

| Owner | Action | Due | Why It's Critical |
|-------|--------|-----|-------------------|
| [Name] | [Action] | [Date] | [B40.D#] |

---

## Strategic Implications

**For Product:** [What this means for product direction]

**For GTM:** [What this means for go-to-market]

**For Company:** [What this means for Careerspan overall]

---

## Context for Future V

*Why this memo matters:* [What you need to know if you're reading this 3 months from now - what was the inflection point, what changed, what context is important]

---

**Generated:** [Timestamp]
```

---

## Generation Rules

### Always Generate
- B26, B40, B41, B47

### Conditional Generation
- **B42**: Market/competitive topics discussed
- **B43**: Product strategy/roadmap discussed  
- **B44**: GTM/sales topics discussed
- **B45**: Operations/process topics discussed
- **B46**: Hiring/team topics discussed
- **B48**: Meeting ≥30min AND significant strategic decisions

### Never Generate for Internal
- B01, B02, B05, B07, B08, B21, B25, B31 (external-only)

---

## Cross-Reference Format

- Decision: `[B40.D#]`
- Tactical: `[B40.T#]`
- Action: `[B41.A#]`
- Question: `[B47.Q#]`
- Past meeting: `[YYYY-MM-DD_meeting-slug/B##.ID]`

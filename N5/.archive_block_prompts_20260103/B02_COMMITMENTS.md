---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
block_code: B02
block_name: COMMITMENTS
category: core
---

# B02: Commitments & Contextual Promises

## Objective

Extract explicit commitments, promises, and agreements made during the meeting. Focus on WHO committed to WHAT by WHEN, with enough context to understand the commitment.

## Output Format

Structured list with context. Each commitment should include:
- **Who** made the commitment
- **What** they committed to deliver/do
- **When** (deadline/timeframe if specified)
- **Context** (why this matters, dependencies)

## Quality Criteria

**Good B02 includes:**
- ONLY explicit commitments (not implied or inferred)
- Clear ownership (who is accountable)
- Specific deliverables/actions
- Deadlines when mentioned
- Enough context to understand importance

**Avoid:**
- General intentions ("we should...") unless made concrete
- Speculative commitments
- Action items without clear ownership (those go in B05)
- Commitments from past meetings (only THIS meeting)

## Instructions

1. Scan transcript for commitment language:
   - "I will..."
   - "I commit to..."
   - "We'll deliver..."
   - "I'll send you..."
   - "I promise..."
   - "I'll have this done by..."

2. For each commitment, extract:
   - WHO: Person/party making commitment
   - WHAT: Specific deliverable/action
   - WHEN: Timeline/deadline
   - CONTEXT: Why it matters

3. Group by person/party if helpful

4. Include dependencies if mentioned ("After X delivers Y, I'll...")

## Edge Cases

**If no explicit commitments:**
```markdown
## B02_COMMITMENTS

No explicit commitments were made in this meeting. The discussion was exploratory/informational.
```

**If commitment has conditional dependencies:**
```markdown
- **V** → Send contract draft by Friday, dependent on legal review completion
```

**If timeline is vague:**
```markdown
- **Rory** → Follow up on vendor pricing (timeline: "soon"/"next week")
```

## Example Output

```markdown
## B02_COMMITMENTS

### Vrijen's Commitments
- **Send partnership proposal deck** by EOD Wednesday Nov 20
  - Context: Needed for Nicole's board meeting on Nov 22
  - Includes pricing tiers and implementation timeline

- **Schedule follow-up with legal team** within next 2 weeks
  - Context: Review IP clauses before final agreement

### Rory's Commitments
- **Provide user research findings** by Monday Nov 18
  - Context: Vrijen needs this to finalize proposal deck
  - Will include 3 customer case studies

### Mutual Agreements
- Both parties agreed to **maintain confidentiality** on pricing discussions until contracts are signed
```

## Validation

Before finalizing, check:
- [ ] Only EXPLICIT commitments included (not implied)
- [ ] Clear ownership for each commitment
- [ ] Deadlines captured when mentioned
- [ ] Context explains WHY it matters
- [ ] No duplicate or redundant entries
- [ ] Names spelled correctly


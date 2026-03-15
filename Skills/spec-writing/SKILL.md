---
name: spec-writing
description: >
  Structured interview to extract behavioral scenarios from rough intent before Architect planning.
  Runs before pulse-interview. Outputs scenario specs that the Architect consumes as input to PLAN.md.
  Use when starting any Pulse build or when the user describes a new feature/system to build.
compatibility: Created for Zo Computer
metadata:
  author: n5os
  version: "1.0"
  created: "2026-02-21"
---

# Spec-Writing Skill

## When to Activate

- Before any Pulse build (runs before pulse-interview)
- When the user says "I want to build X" or describes a new feature/system
- When the Architect persona needs scenario specs as planning input
- On explicit request: "write specs", "extract scenarios", "what does working look like"

## Workflow

```
User describes intent ("I want to build X")
  → Spec-writing skill activates
  → Structured interview (5 rounds max)
  → Outputs: scenario list + ambiguities + decision points
  → User reviews and approves scenarios
  → Architect receives approved scenarios as PLAN.md input
```

## Interview Structure

### Round 1: Intent Clarification
Ask these questions (adapt to context — skip what's already clear):

1. **What is the core thing this should do?** (one sentence)
2. **Who or what triggers it?** (user action, scheduled, webhook, another system)
3. **What's the happy path?** Walk through: trigger → processing → output
4. **What does "done" look like?** How would you verify it's working?

### Round 2: Edge Cases & Boundaries
Based on Round 1 answers:

5. **What inputs could be weird?** (empty, huge, malformed, duplicate)
6. **What external dependencies exist?** (APIs, files, services) — what if they're down?
7. **What data could be missing?** Fields that might not exist, optional vs required
8. **What are the boundaries?** (rate limits, file size, timeout, concurrency)

### Round 3: Failure Modes
9. **What should happen when it breaks?** (retry, skip, alert, degrade gracefully)
10. **What should NEVER happen?** (data loss, duplicate sends, silent failures)
11. **What's the blast radius if it goes wrong?** (affects just this system, or cascades)

### Round 4: Scenario Drafting
Using the answers, draft 3-5 scenarios per major component in Given/When/Then/Verify format.

Present them to the user for review:
- Are these the right scenarios?
- Anything missing?
- Are the Verify clauses executable?

### Round 5: Approval
User approves or modifies scenarios. Output the final scenario set.

## Output Format

Save to conversation workspace as `scenarios-<slug>.md`:

```markdown
---
created: YYYY-MM-DD
build_slug: <slug>
status: approved
provenance: <conversation_id>
---

# Scenario Specs: <Build Name>

## Component: <Name>

S1: <Descriptive name>
  Given: <precondition>
  When: <trigger>
  Then: <expected outcome>
  Verify: <executable check or LLM judgment>

S2: ...

## Component: <Name>

S3: ...
S4: ...

## Identified Ambiguities

- <Thing that needs user's decision before planning>
- <Thing that could go either way>

## Decision Points

| ID | Question | Options | Recommendation |
|----|----------|---------|----------------|
| DP-1 | ... | A, B | A because ... |
```

## Integration with Pulse

- Spec-writing outputs feed into the Architect's planning phase
- Scenarios from the spec get distributed into individual Drop briefs
- The Filter evaluates deposits against these scenarios
- See `Skills/pulse/references/interview-protocol.md` Question 7 for how scenarios integrate with the interview

## Principles Applied

- **P28 (Plans as Code):** Scenarios are the executable DNA of the spec
- **P40 (Specify Behaviorally):** Observable outcomes over implementation checklists
- **P16 (Accuracy Over Sophistication):** Concrete checks over impressive-sounding criteria

## Reference

See `Skills/spec-writing/references/scenario-patterns.md` for common scenario patterns by build type.

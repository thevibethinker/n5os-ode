---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_mG5yzbSSJUnMnZcK
---

# P40: Specify Behaviorally

**Principle:** Define acceptance as observable scenarios (Given/When/Then/Verify), not implementation checklists. Specs must be complete enough that output quality can be assessed without reading the output's implementation.

**Origin:** Dan Shapiro's "Five Levels of AI Coding" framework and StrongDM's dark factory model. The core insight: as AI handles more implementation, the bottleneck shifts from code quality to spec quality. The system that writes better specs produces better output.

---

## Pattern

**Instead of:**
```markdown
## Success Criteria
- [ ] API endpoint exists
- [ ] Error handling implemented
- [ ] Tests pass
```

**Write:**
```markdown
## Scenarios

S1: Successful request
  Given: Service running on port 8080
  When: POST /api/data with valid JSON payload
  Then: Returns 200 with created resource ID
  Verify: curl -s -X POST -H "Content-Type: application/json" -d '{"name":"test"}' localhost:8080/api/data | jq .id

S2: Malformed input
  Given: Service running
  When: POST /api/data with invalid JSON
  Then: Returns 400 with error describing the problem
  Verify: curl -s -X POST -d '{bad' localhost:8080/api/data | jq .error

S3: Missing required field
  Given: Service running
  When: POST /api/data with empty body
  Then: Returns 400 listing required fields
  Verify: curl -s -X POST -H "Content-Type: application/json" -d '{}' localhost:8080/api/data | jq .missing_fields
```

## Why This Matters

**For a non-technical founder managing AI workers:**
- Implementation checklists test *structure* ("does the file exist?") not *behavior* ("does it do the right thing?")
- Scenarios are readable by non-engineers — you can assess quality without reading code
- Scenarios are machine-executable — the Filter can run Verify clauses automatically
- Scenarios survive implementation changes — if someone rewrites the code but the scenarios pass, it still works

**The Shapiro hierarchy:**
- Level 3: You review code the AI writes
- Level 4: You write specs, AI writes + validates against scenarios
- Level 5: AI writes specs from intent, validates against scenarios you don't even see

P40 is the mechanism for moving from Level 3 to Level 4.

## When to Apply

- **Every Pulse Drop brief** — Scenarios section is the primary acceptance mechanism
- **Feature specifications** — Before building, extract scenarios via the spec-writing skill
- **Bug reports** — Frame bugs as "Given X, When Y, expected Z but got W"
- **Integration testing** — Post-build verification follows the same pattern

## Verify Clause Types

| Type | Zone | When to Use |
|------|------|-------------|
| Shell command (`curl`, `duckdb`, `test`) | Zone 3 (deterministic) | API responses, data state, file existence |
| `LLM: <instruction>` | Zone 2 (structured) | Code quality, UX evaluation, pattern adherence |
| None / inferred | Zone 1 (squishy) | Avoid — always try to make verification explicit |

**Always prefer executable verification.** If you can't write a command, that's a signal the scenario is too vague.

## Relationship to Other Principles

| Principle | Connection |
|-----------|-----------|
| P28 (Plans as Code) | P40 makes P28's specs behaviorally testable |
| P15 (Complete Before Claiming) | P40 gives P15 concrete criteria to verify |
| P37 (Pipelines) | Each pipeline stage can have its own scenarios |
| P38 (Isolate) | Isolated workers are evaluated against isolated scenarios |

## Anti-Patterns

- **Scenario without Verify:** "Then: It should work correctly" — useless
- **Verify that checks implementation:** "Verify: grep -c 'class UserService' service.py" — tests structure, not behavior
- **Too many scenarios:** >8 per Drop means the Drop is too large — decompose it
- **Scenarios that restate requirements:** Scenarios test *behavior*, not *existence*

## Scoring

Scenarios are scored individually 0.0-1.0 by the Filter. Satisfaction is the weighted average:
- >= 0.9: PASS
- 0.7-0.89: WARN (advance with concerns)
- < 0.7: FAIL (auto-retry with specific feedback)

This replaces the binary PASS/FAIL of checklist-based validation.

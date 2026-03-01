---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_mG5yzbSSJUnMnZcK
---

# Holdout Scenarios

Holdout scenarios are acceptance criteria that workers CANNOT see. They test whether the implementation genuinely satisfies the intent — not just the visible specification.

## Convention

**Location:** `N5/builds/<slug>/holdout_scenarios/`

**File naming:** `<drop_id>_holdouts.yaml` (e.g., `D1.1_holdouts.yaml`)

**When to write holdouts:**
- During Architect planning phase (after scenarios are approved)
- V can also write holdouts during or after planning
- Holdouts should test the *intent* behind scenarios, not just restate them differently

## Template

```yaml
# holdout_scenarios/D1.1_holdouts.yaml
drop_id: D1.1
created: YYYY-MM-DD
author: architect  # or "V"

scenarios:
  - id: H1
    name: "Descriptive name for the hidden test"
    given: "Precondition the worker wouldn't think to test"
    when: "Trigger that exposes assumptions"
    then: "Expected behavior that reveals genuine understanding"
    verify: "LLM: <specific check instruction>"
    weight: 0.5  # 0.0-1.0, how much this holdout counts toward satisfaction

  - id: H2
    name: "Another hidden test"
    given: "..."
    when: "..."
    then: "..."
    verify: "..."
    weight: 0.5
```

## Good Holdouts

Holdouts should test things the worker *should* handle but might not think to:

- **Implicit requirements:** "Does the API validate Content-Type header?" (never mentioned in brief)
- **Boundary conditions:** "What happens with 0 items? With 10,000?"
- **Integration assumptions:** "Does it actually work with the real data format, not just the example?"
- **Robustness:** "What if the upstream service returns slowly?"
- **Security basics:** "Does it sanitize user input?"

## Bad Holdouts

Don't write holdouts that:

- **Restate a public scenario differently** — that just increases the weight of one concern
- **Test implementation details** — holdouts should test behavior, not "did you use pattern X"
- **Are impossible to satisfy without clairvoyance** — if the brief doesn't give enough context to handle the holdout, that's a spec gap, not a holdout
- **Contradict public scenarios** — holdouts extend, they don't override

## Weight Guidelines

| Holdout Type | Suggested Weight |
|-------------|-----------------|
| Basic robustness (should be obvious) | 0.7 - 1.0 |
| Edge case the brief hints at | 0.5 |
| Subtle requirement from context | 0.3 - 0.5 |
| Nice-to-have beyond spec | 0.1 - 0.3 |

## Who Writes Holdouts

**Decision:** The Architect writes holdouts during planning. V can add more during or after.

**Philosophical note:** There's a tension — the same "system" (Zo) writes both the brief and the holdouts. This is mitigated by:
1. Holdouts are written during *planning* (Architect mode), evaluated during *filtering* (different context)
2. Workers are separate `/zo/ask` invocations with no access to holdout files
3. V can always add holdouts that the Architect wouldn't think of

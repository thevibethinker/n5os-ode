---
created: 2026-02-03
last_edited: 2026-02-03
version: 1.0
type: build_plan
status: draft
---

# Plan: Zo Obsession Site

**Objective:** {{ONE_SENTENCE_OBJECTIVE}}

**Trigger:** {{WHAT_PROMPTED_THIS_BUILD}}

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [ ] {{QUESTION_1}}
- [ ] {{QUESTION_2}}

---

## Checklist

<!-- Concise one-liners. ☐ = pending, ☑ = complete. Zo updates as it executes. -->

### Phase 1: {{PHASE_1_NAME}}
- ☐ {{TASK_1}}
- ☐ {{TASK_2}}
- ☐ Test: {{TEST_DESCRIPTION}}

### Phase 2: {{PHASE_2_NAME}}
- ☐ {{TASK_1}}
- ☐ {{TASK_2}}
- ☐ Test: {{TEST_DESCRIPTION}}

<!-- Add more phases as needed. Keep to 2-4 phases that logically stack. -->

---

## Phase 1: {{PHASE_1_NAME}}

### Affected Files
<!-- List EVERY file this phase touches. Format: path - ACTION - brief description -->
- `path/to/file.py` - CREATE - description
- `path/to/other.py` - UPDATE - description

### Changes

**1.1 {{SUBCHANGE_TITLE}}:**
<!-- Describe what changes. Be specific enough for AI to execute without clarification. -->

**1.2 {{SUBCHANGE_TITLE}}:**
<!-- Continue as needed -->

### Unit Tests
<!-- Tests for THIS phase. Run after phase completion. -->
- {{TEST_1}}: Expected outcome
- {{TEST_2}}: Expected outcome

---

## Phase 2: {{PHASE_2_NAME}}

### Affected Files
- `path/to/file.py` - CREATE/UPDATE/DELETE - description

### Changes

**2.1 {{SUBCHANGE_TITLE}}:**
<!-- Describe changes -->

### Unit Tests
- {{TEST}}: Expected outcome

---

## MECE Validation

<!-- 
MANDATORY for multi-worker builds.
Reference: N5/prefs/operations/mece-worker-framework.md
Run validator: python3 N5/scripts/mece_validator.py zo-obsession-site
-->

### Scope Coverage Matrix

<!-- List ALL scope items from plan. Each must map to exactly ONE worker. -->

| Scope Item | Worker | Status |
|------------|--------|--------|
| `{{FILE_1}}` | W1.1 | ✓ |
| `{{FILE_2}}` | W1.2 | ✓ |
| `{{RESPONSIBILITY}}` | W1.1 | ✓ |

### Token Budget Summary

<!-- Ensure each worker stays within context budget (target <30%, hard limit <40%). -->

| Worker | Brief (tokens) | Files (tokens) | Total % | Status |
|--------|----------------|----------------|---------|--------|
| W1.1 | ~2,000 | ~8,000 | 5% | ✓ |
| W1.2 | ~1,500 | ~6,000 | 3.75% | ✓ |

### MECE Validation Result

- [ ] All scope items assigned to exactly ONE worker (no overlaps)
- [ ] All plan deliverables covered (no gaps)
- [ ] All workers within 40% token budget
- [ ] Wave dependencies are valid (no circular, no same-wave deps)
- [ ] `python3 N5/scripts/mece_validator.py zo-obsession-site` passes

---

## Worker Briefs

<!-- For builds using v2 orchestrator: briefs are in `workers/` folder. -->
<!-- Titles are pre-decided to enable easy thread management. -->

| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | {{W1.1_TITLE}} | `workers/W1.1-{{W1.1_SLUG}}.md` |
| 1 | W1.2 | {{W1.2_TITLE}} | `workers/W1.2-{{W1.2_SLUG}}.md` |
| 2 | W2.1 | {{W2.1_TITLE}} | `workers/W2.1-{{W2.1_SLUG}}.md` |

<!-- Add rows as needed. Wave 2+ workers depend on Wave 1 completion. -->

---

## Success Criteria

<!-- How do we know we're done? Measurable outcomes. -->
1. {{CRITERION_1}}
2. {{CRITERION_2}}
3. {{CRITERION_3}}

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| {{RISK_1}} | {{MITIGATION_1}} |
| {{RISK_2}} | {{MITIGATION_2}} |

---

## Level Upper Review

<!-- Architect invokes Level Upper before finalizing. Document the divergent input here. -->

### Counterintuitive Suggestions Received:
1. {{SUGGESTION_1}}
2. {{SUGGESTION_2}}

### Incorporated:
- {{WHAT_WAS_INCORPORATED}}

### Rejected (with rationale):
- {{WHAT_WAS_REJECTED}}: {{WHY}}

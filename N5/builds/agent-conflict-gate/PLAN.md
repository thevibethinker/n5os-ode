---
created: 2026-02-11
last_edited: 2026-02-11
version: 1
type: build_plan
status: draft
---
# Plan: Agent Conflict Gate System

**Objective:** Prevent scheduled agent duplication, stale builders, and resource conflicts by introducing a pre-creation gate.

**Trigger:** V asked to review the agent conflict analysis and implement safeguards, including conflict detection script + protocol updates.

**Key Design Principle:** Apply the "Simple > Easy" mandate: block conflicts with a lightweight rule plus a focused script, document the protocol, and clean up current duplicates.

---

## Open Questions
- [ ] Should the conflict check operate synchronously (blocking) or log issues and warn while allowing creation?
- [ ] Are there additional APIs or rate-limited services (beyond Fitbit/Gmail/Calendar) that should live in the script's curated list?

---

## Checklist

### Phase 1: Conflict Gate Infrastructure
- ☐ Draft and implement `N5/scripts/agent_conflict_gate.py` with inventory + invariants
- ☐ Document the script output contract for the rule
- ☐ Test script manually with `list_agents` data and edge cases (expired agents, dupe skill digests)

### Phase 2: Safety Protocol Integration & Cleanup
- ☐ Write the safety rule that calls the script before `create_agent`/reactivation, log outputs, and document approval steps
- ☐ Document the gate in docs and flag duplicates/stale agents for cleanup
- ☐ Confirm weekly audit references the gate and that cleanup notes exist

---

## Phase 1: Conflict Gate Infrastructure

### Affected Files
- `N5/scripts/agent_conflict_gate.py` - CREATE - Python gate script that inventories agents, checks duplication/conflict heuristics, and returns structured warnings

### Changes

**1.1 Gate Script:**
- Build script that calls `list_agents`, normalizes fields, and checks:
  1. Title similarity + shared instruction re-use (LLM neighbor) for duplicates
  2. Identical API/Web dependency combos (Fitbit, Gmail, Calendar) within overlapping time windows
  3. Agents pointing to same command/script/skill
  4. Agents with identical delivery method + target file (email, SMS path)
  5. Active agents that have `next_run: null` but `active: true` (stale zombies)
  6. Time slot density warnings (≥3 agents in same hour)
- Output list of conflicts (type, agents involved, reason) and exit non-zero if blocking (configurable)
- Support `--dry-run` to print conflict summary without blocking to test

**1.2 Output Contract:**
- Format the script output (JSON table or similar) so the rule can parse conflict types, involved agents, and recommended actions.
- Include an exit code convention: `0` = clear, `1` = conflicts detected, `2` = fatal error.
- Provide optional `--summary` flag that prints human-friendly text alongside machine-readable data.

**1.3 Tests:**
- Run script against current inventory, verify duplicates found (Skill Evolution, stale agents)
- Simulate new agent creation with conflicting metadata to ensure gate flags it
- Confirm gate exits 0 when no conflicts, non-zero otherwise

### Unit Tests
- `python3 N5/scripts/agent_conflict_gate.py --dry-run` against live data: expect flagged duplicates (Skill Evolution, stale agents)
- `python3 N5/scripts/agent_conflict_gate.py --test-case duplicate-title --time-slot 10` (emulated input) → conflicts reported

---

## Phase 2: Safety Protocol Integration & Cleanup

### Affected Files
- `N5/prefs/operations/scheduled-task-protocol.md` - UPDATE - Insert pre-creation gate steps, mention cleanup of flagged duplicates
- `N5/prefs/system/safety.md` - UPDATE - Extend safety rule list with conflict detection guardrail and logging requirement
- `N5/logs/agent_conflict_gate.log` - CREATE - Append-only log to trace gate results
- `N5/prefs/operations/digest-creation-protocol.md` (if referenced) - UPDATE - Reference gate? (uncertain)

### Changes

**2.1 Protocols:**
- Insert a "Pre-Creation Conflict Gate" section: list steps (run script, review output, document approvals)
- Define the safety rule that executes the script, formats the output for human review, logs events, and requires explicit approval or `--force` overrides when conflicts are present.
- Update weekly audit to include verifying the gate is running and flagged overlaps are resolved
- Add cleanup instructions for duplicates (Skill Evolution) and stale agents (next_run null yet active)

**2.2 Cleanup:**
- Use the gate output to create tickets for:
  - The two Skill Evolution Digest agents (`35523e05`, `ad86b060`) → pick one, disable the other
  - Stale active agents (IDs list) → disable/mark inactive
  - Flag any overlapping Fitbit consumers or heavy-hour clusters
- Document cleanup plan in `N5/notes/agent-conflict-cleanup.md` (new file) referencing the gate report

**2.3 Tests:**
- Run weekly audit script (if exists) to ensure gate is mentioned
- Manually verify new protocol sections read well
- Confirm log entries include timestamp + conflict reasons

### Unit Tests
- `python3 N5/scripts/agent_conflict_gate.py --dry-run --check-log` → log updated
- Proof-check scheduled-task protocol changes via `grep` for gate term

---

## MECE Validation

### Scope Coverage Matrix
| Scope Item | Worker | Status |
|------------|--------|--------|
| Gate script implementation | W1 | ☐ |
| Safety rule creation + logging | W2 | ☐ |
| Protocol documentation | W2 | ☐ |
| Cleanup execution & logging | W2 | ☐ |

### Token Budget Summary
| Worker | Brief (tokens) | Status |
|--------|----------------|--------|
| W1.1 | ~2,000 | pending |
| W2.1 | ~2,000 | pending |

### MECE Validation Result
- [ ] All scope items assigned to exactly ONE worker
- [ ] All plan deliverables covered
- [ ] Workers within token budgets
- [ ] No circular dependencies
- [ ] `python3 N5/scripts/mece_validator.py agent-conflict-gate` passes

---

## Worker Briefs
| Wave | Worker | Title | Brief File |
|------|--------|-------|------------|
| 1 | W1.1 | Gate Script + Rule | `workers/W1.1-gate-script.md` |
| 2 | W2.1 | Protocol Update + Cleanup | `workers/W2.1-protocol-update.md` |

---

## Success Criteria
1. Gate script accurately flags all current and simulated conflicts; exits >0 when conflicts present.
2. Safety rules and protocols reference the gate; weekly audit checks for compliance.
3. Identified duplicates (Skill Evolution Digest) and stale agents are resolved or annotated with next steps.

---

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| False positives block harmless agents | Provide `--force` override + human approval logging |
| Script fails due to API changes | Keep script limited to `list_agents` response; add schema validation + dry-run fallback |
| Protocol update ignored | Mention gate in both `safety.md` and `scheduled-task-protocol.md`, plus weekly audit check |

---

## Level Upper Review
### Counterintuitive Suggestions Received:
1. Consider a lightweight dashboard that shows duplicate warnings rather than blocking entirely.
2. Use a scheduled cleanup agent to prune stale tasks automatically.

### Incorporated:
- Added log-based oversight to keep a historical record of blocked creations (responded with logging requirement in rule/protocol).

### Rejected (with rationale):
- Suggestion to build a dashboard was deferred; simple rule+script meets immediate needs without extra infrastructure.

# Error Tracking Guide

**Purpose:** Comprehensive error logging, categorization, and recovery for distributed builds

---

## Error Code System

### Format: `[TYPE][CATEGORY][NUMBER]`

**Types:**
- **E** = Error (blocks progress)
- **W** = Warning (non-blocking, but note)
- **I** = Info (FYI, no action needed)

**Categories:**
- **0xx** = Assignment/Setup
- **1xx** = Dependencies/Interfaces
- **2xx** = Implementation Quality
- **3xx** = Integration
- **4xx** = Testing
- **5xx** = Principles/Architecture

---

## Error Codes Reference

### E0xx: Assignment & Setup Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E001 | Assignment scope unclear | BLOCKING | Orchestrator clarifies, updates assignment |
| E002 | Missing dependencies in assignment | BLOCKING | Orchestrator adds dependency info |
| E003 | Conflicting constraints | BLOCKING | Orchestrator resolves conflict |
| E004 | Cannot access BUILD_STATE_SESSION.md | BLOCKING | Orchestrator provides correct path |
| E005 | Assignment missing acceptance criteria | BLOCKING | Orchestrator adds criteria |

### E1xx: Dependency & Interface Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E101 | Prerequisite worker not complete | BLOCKING | Wait for prerequisite, update state |
| E102 | Interface mismatch with dependency | BLOCKING | Coordinate with other worker OR orchestrator redesigns interface |
| E103 | Missing required file/module | BLOCKING | Previous worker failed to deliver, escalate to orchestrator |
| E104 | API signature doesn't match spec | BLOCKING | Worker implements correct signature OR orchestrator updates spec |
| E105 | Data structure incompatibility | BLOCKING | Align on shared data structure |

### E2xx: Implementation Quality Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E201 | Scope creep detected | BLOCKING | Worker reverts to assigned scope |
| E202 | Modified files outside whitelist | BLOCKING | Worker undoes unauthorized changes |
| E203 | Code doesn't meet style standards | WARNING → ERROR | Worker reformats OR orchestrator accepts with note |
| E204 | Missing error handling | WARNING | Worker adds error handling |
| E205 | Performance concern | WARNING | Worker optimizes OR documents trade-off |
| E206 | Security vulnerability detected | BLOCKING | Worker fixes immediately |
| E207 | Incomplete implementation | BLOCKING | Worker completes all deliverables |

### E3xx: Integration Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E301 | Integration test failed | BLOCKING | Worker fixes bug |
| E302 | Breaks existing functionality (regression) | BLOCKING | Worker fixes OR orchestrator reverts |
| E303 | Cannot merge (conflicts) | BLOCKING | Worker resolves conflicts |
| E304 | Missing integration documentation | WARNING | Worker adds docs |
| E305 | Unexpected side effects | BLOCKING | Worker isolates side effects |

### E4xx: Testing Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E401 | Unit tests missing | BLOCKING | Worker adds tests |
| E402 | Tests fail | BLOCKING | Worker fixes code or tests |
| E403 | Test coverage below threshold | WARNING | Worker adds tests OR orchestrator accepts |
| E404 | Tests not automated | WARNING | Worker automates OR documents manual process |
| E405 | Edge cases not covered | WARNING | Worker adds edge case tests |

### E5xx: Principle & Architecture Errors

| Code | Description | Severity | Recovery |
|------|-------------|----------|----------|
| E501 | Violates architectural principle | BLOCKING | Worker refactors to align |
| E502 | Introduces technical debt | WARNING → ERROR | Worker fixes OR documents debt + repayment plan |
| E503 | Over-engineered solution | WARNING | Worker simplifies OR justifies complexity |
| E504 | Under-engineered solution | WARNING | Worker adds robustness OR documents limitations |
| E505 | P13 violation (analysis paralysis) | WARNING | Worker ships simpler version |

### W0xx-W5xx: Warnings

Same categories as errors, but non-blocking. Document and assess if they should escalate.

---

## Error Logging

### In BUILD_STATE_SESSION.md

```markdown
## Error Log

| Timestamp | Worker | Code | Severity | Description | Status | Resolution |
|-----------|--------|------|----------|-------------|--------|------------|
| 2025-10-17 14:32:15 | W2 | E104 | BLOCKING | API signature mismatch in `process_data()` | RESOLVED | W2 updated signature to match spec |
| 2025-10-17 15:45:22 | W3 | W403 | WARNING | Test coverage 78% (target 85%) | ACCEPTED | Acceptable for v1, tracked in backlog |
| 2025-10-17 16:10:03 | W1 | E302 | BLOCKING | Broke `import_handler()` in integration test | RESOLVED | W1 fixed regression, tests pass |
```

### In Worker Error Report

When a worker encounters a blocking error, generate: `WN_ERROR_REPORT.md`

**Template:**

```markdown
# Worker [N] Error Report

**Worker:** W[N]  
**Task:** [Task name]  
**Error Code:** [Code]  
**Severity:** [BLOCKING/WARNING]  
**Timestamp:** [ISO timestamp]  
**Status:** OPEN | INVESTIGATING | RESOLVED

---

## Error Description

[Clear description of what went wrong]

---

## Context

**What I was trying to do:**
[Specific action]

**What I expected:**
[Expected behavior]

**What actually happened:**
[Actual behavior]

**Error message/output:**
```
[Paste error message or relevant output]
```

---

## Investigation

**Steps taken:**
1. [Step 1]
2. [Step 2]

**Findings:**
- [Finding 1]
- [Finding 2]

**Root cause:**
[Best guess at root cause]

---

## Proposed Resolution

**Option A:** [Description]
- Pros: [...]
- Cons: [...]

**Option B:** [Description]
- Pros: [...]
- Cons: [...]

**Recommendation:** [Which option and why]

---

## Impact Assessment

**Blocks:**
- [ ] My own progress
- [ ] Other workers: [list which]
- [ ] Integration
- [ ] Build timeline

**Workaround available:** YES | NO
[If yes, describe]

---

## Request

**Need from orchestrator:**
[Specific help needed: clarification, redesign, coordination, etc.]

---

## Resolution (filled after fix)

**Chosen approach:** [Which option]

**Implementation:**
[What was done]

**Validation:**
[How was it verified fixed]

**Lessons learned:**
[What to do differently next time]

**Time to resolve:** [duration]
```

---

## Error Tracking Workflow

### When Worker Encounters Error

1. **Assess severity:**
   - Can I fix it myself? → Fix, log in summary, continue
   - Blocking me? → Generate error report, update state, notify orchestrator

2. **Generate error report:**
   ```bash
   # Create in build folder
   /home/workspace/N5/logs/builds/[build-name]/workers/W[N]_ERROR_LOG.md
   ```

3. **Update BUILD_STATE_SESSION.md:**
   ```markdown
   ### Worker N
   - **Status:** ~~IN_PROGRESS~~ → BLOCKED
   - **Blocker:** E104 - See W[N]_ERROR_LOG.md
   ```

4. **Tell user:**
   "BLOCKED: Error E104. Report at [path]. Need orchestrator input."

### When Orchestrator Handles Error

1. **Read error report** - Understand context, root cause, proposed solutions

2. **Assess scope:**
   - Worker can fix? → Provide guidance, send back
   - Need redesign? → Update assignment, restart worker
   - Need coordination? → Facilitate between workers
   - Fundamental blocker? → Rescope or defer

3. **Document decision** in error report (add resolution section)

4. **Update BUILD_STATE_SESSION.md:**
   ```markdown
   | 2025-10-17 14:32 | W2 | E104 | BLOCKING | API mismatch | RESOLVED | Orchestrator clarified spec, W2 updated |
   ```

5. **Update lessons learned:**
   ```markdown
   ## Lessons Learned
   
   **From W2 error E104:**
   - What: API spec wasn't explicit enough
   - Why: Assumed common understanding
   - Fix: Made spec more explicit in assignment
   - Prevention: Add interface examples to future assignments
   ```

---

## Error Prevention

### In Assignment Phase

**Orchestrator checklist:**
- [ ] Scope is crystal clear (no ambiguity)
- [ ] All dependencies explicitly listed
- [ ] Interface signatures written out (not assumed)
- [ ] Acceptance criteria are testable
- [ ] Constraints are explicit (whitelists/blacklists)
- [ ] Examples provided for complex interfaces

### In Worker Phase

**Worker checklist:**
- [ ] Read assignment fully before starting
- [ ] Clarify any ambiguity upfront
- [ ] Test interfaces early
- [ ] Update state frequently
- [ ] Flag issues immediately (don't let them compound)

### In Integration Phase

**Orchestrator checklist:**
- [ ] Read worker summary before touching code
- [ ] Test in isolation before integration
- [ ] Run regression tests
- [ ] Validate against principles
- [ ] Document any compromises

---

## Common Error Patterns

### Pattern: "Silent Scope Creep"

**Symptoms:**
- Worker delivers more than assigned
- Extra files modified
- New features added

**Root cause:** Worker saw opportunity to improve something related

**Prevention:**
- Explicit anti-scope in assignment
- Worker discipline: "not my job in this context"

**Recovery:** E201, revert extra work, refocus

---

### Pattern: "Interface Mismatch"

**Symptoms:**
- Worker 2 can't consume Worker 1's output
- Integration tests fail
- Data structure incompatibility

**Root cause:** Interface not explicitly defined

**Prevention:**
- Write out exact function signatures in assignment
- Provide interface examples
- Workers confirm understanding before starting

**Recovery:** E104, E105 - coordinate to align

---

### Pattern: "Dependency Hell"

**Symptoms:**
- Worker blocked waiting for another
- Circular dependencies discovered
- Integration order doesn't work

**Root cause:** Dependency graph analysis was wrong

**Prevention:**
- Draw dependency graph during decomposition
- Validate execution order makes sense
- Build foundation → leaf pattern

**Recovery:** E101 - orchestrator reorders or redesigns

---

### Pattern: "Quality Drift"

**Symptoms:**
- Code style inconsistent
- Missing tests
- No error handling
- Principles violated

**Root cause:** Worker didn't check against standards

**Prevention:**
- Link to standards in assignment
- Acceptance criteria include quality gates
- Worker self-reviews before submitting

**Recovery:** E203, E401, E501 - send back for quality fixes

---

## Metrics to Track

In after-action report:

```markdown
## Error Metrics

**Total errors:** [N]
**By severity:**
- BLOCKING: [N]
- WARNING: [N]

**By category:**
- E0xx (Setup): [N]
- E1xx (Dependencies): [N]
- E2xx (Quality): [N]
- E3xx (Integration): [N]
- E4xx (Testing): [N]
- E5xx (Principles): [N]

**Time cost:**
- Average resolution time: [duration]
- Total build delay from errors: [duration]

**Prevention effectiveness:**
- Errors caught before integration: [%]
- Errors caught during integration: [%]

**Most common errors:**
1. [Code]: [count] occurrences
2. [Code]: [count] occurrences
```

**Goal:** Errors ↓ over time as templates improve

---

## When to Escalate to V

Most errors are worker ↔ orchestrator. Escalate to V only if:

1. **Fundamental blocker:** Can't proceed without V's decision
2. **Resource constraint:** Need different model, more time, etc.
3. **Scope question:** Unclear if something is in/out of build scope
4. **Learning opportunity:** V asked to see certain error types

Otherwise, worker and orchestrator should resolve collaboratively.

---

## Emergency Procedures

### Critical Error (E206 - Security)

1. **STOP immediately**
2. **Quarantine:** Don't integrate, don't proceed
3. **Assess impact:** What's exposed? What's the attack surface?
4. **Fix:** Worker fixes immediately, or orchestrator takes over
5. **Verify:** Security review before proceeding
6. **Document:** Full post-mortem in error log

### Build Failure (Cannot Recover)

1. **Acknowledge:** Not all builds succeed
2. **Document:** What went wrong, why, lessons
3. **Decide:**
   - Restart with new approach?
   - Defer to later?
   - Simplify scope?
4. **Update BUILD_STATE_SESSION.md:** Status = FAILED
5. **Generate after-action:** Even failures teach

---

## Error Tracking as Learning

Every error is data:
- Update templates to prevent recurrence
- Add to troubleshooting guide
- Refine decomposition heuristics
- Improve assignment clarity

**Philosophy:** Errors aren't failures, they're feedback for system improvement.

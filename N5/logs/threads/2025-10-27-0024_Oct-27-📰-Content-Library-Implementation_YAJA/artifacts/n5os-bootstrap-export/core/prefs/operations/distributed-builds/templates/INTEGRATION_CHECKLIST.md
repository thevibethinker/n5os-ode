# Integration Checklist

**Purpose:** Step-by-step guide for orchestrator to integrate worker outputs

**Use this for EACH worker integration**

---

## Pre-Integration (Before Touching Code)

- [ ] **Worker status = REVIEW**
  - Check BUILD_STATE_SESSION.md
  - If IN_PROGRESS or BLOCKED → wait

- [ ] **Read worker summary**
  - Location: `N5/logs/builds/[build-name]/workers/W[N]_SUMMARY.md`
  - Understand: What was built, why, design decisions, edge cases

- [ ] **Check deliverables present**
  - All files specified in assignment created/modified?
  - Summary generated?
  - Error log present (if any issues)?

- [ ] **Review error log (if exists)**
  - Location: `N5/logs/builds/[build-name]/workers/W[N]_ERROR_LOG.md`
  - Were all errors resolved?
  - Any warnings to be aware of?

---

## Isolated Testing (Test Worker Output Alone)

- [ ] **Run worker tests**
  ```bash
  cd [worker-output-location]
  [run test command from assignment]
  ```
  - All tests pass? If NO → send back to worker

- [ ] **Manual smoke test**
  - Try key functions/features
  - Does it work as expected?

- [ ] **Check test coverage** (if specified)
  - Meets minimum threshold?
  - If below → decide: accept with note or send back

---

## Code Review (Understand Implementation)

- [ ] **Read all modified files**
  - Line by line review
  - Understand logic flow
  - Note: clever solutions, concerns, questions

- [ ] **Check against assignment**
  - Scope: did worker stay in bounds?
  - Files: only whitelisted files modified?
  - Deliverables: all present?

- [ ] **Evaluate code quality**
  - Readable?
  - Error handling present?
  - Edge cases covered?
  - Comments where needed (but not excessive)?

---

## Interface Validation (Check Contracts)

- [ ] **Function signatures match spec**
  - Compare to interfaces defined in assignment
  - Names, arguments, return types correct?

- [ ] **Data structures match spec**
  - Input/output formats correct?
  - Compatible with dependent workers?

- [ ] **File modifications in bounds**
  - Only modified files on whitelist?
  - No unexpected changes elsewhere?

- [ ] **Dependencies satisfied**
  - Does worker's output provide what other workers need?
  - Can dependent workers consume this interface?

---

## Integration Testing (Test With System)

- [ ] **Merge worker code** (in test environment if available)
  - Integrate into main workspace
  - Or test in isolated branch

- [ ] **Run system-level tests**
  - Do existing tests still pass? (regression check)
  - Do new tests pass?

- [ ] **Manual end-to-end test**
  - Test key flows that touch worker's code
  - Any unexpected behavior?

- [ ] **Check for side effects**
  - Performance changes?
  - New dependencies introduced?
  - Unexpected interactions with other modules?

---

## Principle Validation (Check Against Standards)

- [ ] **Load architectural principles**
  - `file 'Knowledge/architectural/architectural_principles.md'`

- [ ] **Check worker code against relevant principles**
  - Which principles apply to this worker?
  - Does code adhere?
  - Any violations?

- [ ] **Check for anti-patterns**
  - P13 (analysis paralysis)?
  - Over-engineering?
  - Under-engineering?

- [ ] **Document trade-offs**
  - If principles were bent, why?
  - Is rationale sound?
  - Acceptable for this context?

---

## Integration Decision

**Choose ONE:**

### ✅ ACCEPT (Integrate as-is)

**When to use:**
- All checks pass
- No issues found
- Excellent work

**Actions:**
- [ ] Merge code
- [ ] Update BUILD_STATE_SESSION.md → W[N]: INTEGRATED
- [ ] Add integration notes (praise good work)
- [ ] Update quality metrics
- [ ] Proceed to lessons learned

---

### 🔄 REVISE (Orchestrator fixes minor issues)

**When to use:**
- Minor issues found (typos, formatting, simple fixes)
- Worker did 95% right, just needs polish
- Faster to fix than send back

**What counts as "minor":**
- Typo or formatting issue
- Missing simple error message
- Small refactor for clarity
- Adding a simple edge case check

**Actions:**
- [ ] Apply fixes directly
- [ ] Document what was fixed and why
- [ ] Update BUILD_STATE_SESSION.md → W[N]: INTEGRATED (with notes)
- [ ] Add integration notes: "Accepted with minor revisions: [list]"
- [ ] Update quality metrics
- [ ] Note in lessons learned: how to prevent in future assignments

---

### ❌ REJECT (Send back to worker)

**When to use:**
- Major issues found
- Wrong approach taken
- Principle violations
- Missing significant functionality
- Tests fail
- Interface mismatch

**What counts as "major":**
- Logic errors or bugs
- Wrong architecture/approach
- Significant missing functionality
- Principle violations
- Security issues
- Poor error handling
- Interface doesn't match spec

**Actions:**
- [ ] DO NOT integrate code
- [ ] Generate feedback document: `workers/W[N]_FEEDBACK.md`
  ```markdown
  # Feedback for Worker [N]
  
  **Status:** REJECTED
  
  ## Issues Found
  
  1. **[Issue category]:** [Description]
     - **Location:** [file:line]
     - **Problem:** [What's wrong]
     - **Expected:** [What should be]
  
  2. [Continue for each issue]
  
  ## Required Changes
  
  - [ ] [Specific change 1]
  - [ ] [Specific change 2]
  
  ## Acceptance Criteria for Resubmission
  
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]
  
  ## Examples
  
  [If helpful, provide code examples of correct approach]
  ```
- [ ] Update BUILD_STATE_SESSION.md → W[N]: IN_PROGRESS (with feedback link)
- [ ] Add error to error log
- [ ] Notify user: "Worker [N] needs rework. Feedback at [path]."

---

## Post-Integration Actions

- [ ] **Update BUILD_STATE_SESSION.md**
  ```markdown
  ### Worker N
  - **Status:** INTEGRATED
  - **Integrated:** [timestamp]
  - **Decision:** ACCEPTED | REVISED | REJECTED
  - **Issues found:** [N]
  - **Fixes applied:** [list or "none"]
  - **Quality:** ✅ Excellent | ✅ Good | ⚠️ Acceptable | ❌ Needs rework
  ```

- [ ] **Update quality metrics table**
  - Actual LOC
  - Test count
  - Principle violations (if any)
  - Rework cycles

- [ ] **Update integration notes section**
  - What went well
  - What needed adjustment
  - Any concerns for future workers

- [ ] **Update error log** (if issues found)

---

## Lessons Learned (CRITICAL - Do After Each Integration)

- [ ] **Add to "Lessons Learned" section** in BUILD_STATE_SESSION.md

**Template:**
```markdown
### From W[N] Integration ([date])

**What worked:**
- [Specific thing that went well]
- [Pattern to repeat]

**What didn't:**
- [Specific thing that didn't work]
- [Issue that emerged]

**Root cause:**
- [Why did the issue happen?]

**Adjustment for remaining workers:**
- [How will we change W[N+1], W[N+2] assignments?]
- [What will we be more explicit about?]

**Template update needed:**
- [Any changes to WORKER_ASSIGNMENT template?]
```

**Use this to:**
1. Refine remaining worker assignments (make them clearer)
2. Catch patterns (good or bad)
3. Improve system over time

---

## Common Integration Issues

### Issue: "Code works but doesn't match interface"

**Decision:** REJECT or REVISE (depending on severity)

**Actions:**
- If simple mismatch → REVISE (orchestrator aligns interface)
- If architectural → REJECT (worker must fix)

---

### Issue: "Code is over-engineered"

**Decision:** ACCEPT (with note) or REJECT (if P13 violation)

**Actions:**
- Assess: Is complexity justified?
- If yes → ACCEPT, document rationale
- If no (gold-plating, analysis paralysis) → REJECT, ask for simpler version

---

### Issue: "Tests missing but code is good"

**Decision:** REVISE or REJECT (depending on criticality)

**Actions:**
- If non-critical code → REVISE (orchestrator adds simple tests)
- If critical code → REJECT (worker must add comprehensive tests)

---

### Issue: "Small principle violation"

**Decision:** ACCEPT (with note) or REVISE

**Actions:**
- Document trade-off in BUILD_STATE_SESSION.md
- Note in technical debt section
- If easy fix → REVISE
- If acceptable trade-off → ACCEPT with clear rationale

---

### Issue: "Worker added extra features (scope creep)"

**Decision:** REJECT (remove extra work)

**Actions:**
- E201 error: Scope creep detected
- Worker removes extra features
- Orchestrator clarifies scope boundaries more explicitly

---

## Emergency Procedures

### Critical Bug Found During Integration

1. **STOP** - Do not proceed with integration
2. **Assess severity:**
   - Security issue? (E206)
   - Data corruption risk?
   - System crash?
3. **Quarantine** - Isolate worker code
4. **Send back to worker** - REJECT with URGENT tag
5. **Block dependent workers** - Update their status

### Worker Blocking Entire Build

1. **Assess criticality:**
   - Can we route around?
   - Can we simplify scope?
   - Can we defer?

2. **Options:**
   - **Option A:** Orchestrator takes over (if small enough)
   - **Option B:** Redesign assignment, send back to worker
   - **Option C:** De-scope from build, add to backlog

3. **Document decision** in BUILD_STATE_SESSION.md

---

## Integration Timing

**Best practice:** Integrate workers **one at a time, in dependency order**

**Example:**
```
✅ GOOD:
1. Integrate W1 (foundation)
2. Test W1
3. Integrate W2 (depends on W1)
4. Test W2
5. Integrate W3 (parallel to W2)
6. Test W3

❌ BAD:
1. Integrate W1, W2, W3 all at once
2. Test everything
3. [If something breaks, hard to isolate which worker caused it]
```

**Exception:** Workers with zero dependencies can be integrated in any order

---

## Success Criteria for Integration

An integration is successful when:

- [ ] Worker code merged into workspace
- [ ] All tests pass (worker's + system)
- [ ] No regressions
- [ ] No principle violations (or documented trade-offs)
- [ ] Interfaces work as specified
- [ ] Documentation updated
- [ ] Lessons captured
- [ ] Ready for next worker

---

## After All Workers Integrated

See `file 'protocol.md'` Stage 5: Validation for:
- System-level testing
- Full principle review
- Documentation updates
- After-action report generation

---

**Remember:** Integration is where quality compounds or collapses. Take your time. Each integration teaches you how to make the next one better.

# Build State Session: [BUILD_NAME]

**Orchestrator ID:** [conversation-id]  
**Build Location:** `/home/workspace/N5/logs/builds/[build-name]/`  
**Started:** [YYYY-MM-DD HH:MM:SS]  
**Status:** PLANNING | ACTIVE | INTEGRATION | COMPLETE | FAILED  
**Type:** distributed_build

---

## Build Overview

**Objective:**

[One clear sentence: What are we building?]

**Scope:**

- Modules: [N]
- Estimated files: [N]
- Estimated LOC: [N]
- Workers: [N]

**Success Criteria:**

1. [Functional criterion 1]
2. [Functional criterion 2]
3. [Quality criterion]
4. [Documentation criterion]

**Out of Scope:**

- [Thing 1 we're explicitly NOT doing]
- [Thing 2 we're explicitly NOT doing]

---

## Workers

### Worker 1: [TASK_NAME]

- **Status:** ASSIGNED | IN_PROGRESS | REVIEW | INTEGRATED | BLOCKED | FAILED
- **Assignment:** `assignments/WORKER_1_ASSIGNMENT.md`
- **Deliverables:**
  - `[path/file1]`
  - `[path/file2]`
- **Dependencies:** None / W[N], W[N]
- **Started:** [timestamp or empty]
- **Completed:** [timestamp or empty]
- **Summary:** `workers/W1_SUMMARY.md` (when complete)
- **Errors:** [None or link to error log]
- **Notes:** [Any relevant notes]

### Worker 2: [TASK_NAME]

- **Status:** ASSIGNED
- **Assignment:** `assignments/WORKER_2_ASSIGNMENT.md`
- **Deliverables:**
  - `[path/file]`
- **Dependencies:** W1 (must complete first)
- **Started:** 
- **Completed:** 
- **Summary:** 
- **Errors:** 
- **Notes:** 

[Repeat for each worker]

---

## Dependencies Graph

```
Execution Order:

W1 (foundation)
  ├─→ W2 (builds on W1)
  │     └─→ W5 (integrates W2+W3)
  └─→ W3 (parallel to W2)
        └─→ W5
  
W4 (independent, can run anytime)
```

**Execution Phases:**

1. **Phase 1:** W1 (sequential)
2. **Phase 2:** W2, W3, W4 (parallel)
3. **Phase 3:** W5 (after W2, W3)

---

## Integration Checklist

- [ ] W1 integrated and tested
- [ ] W2 integrated and tested
- [ ] W3 integrated and tested
- [ ] W4 integrated and tested
- [ ] W5 integrated and tested
- [ ] Full system test passed
- [ ] Principles validation passed
- [ ] Documentation updated
- [ ] After-action report generated

---

## Error Log

| Timestamp | Worker | Code | Severity | Description | Status | Resolution |
|-----------|--------|------|----------|-------------|--------|------------|
| [YYYY-MM-DD HH:MM:SS] | W[N] | E[code] | BLOCKING/WARNING | [Brief description] | OPEN/RESOLVED | [How it was fixed] |

[Example entry:]
| 2025-10-17 14:32:15 | W2 | E104 | BLOCKING | API signature mismatch in `process_data()` | RESOLVED | W2 updated signature to match spec |

---

## Quality Metrics

| Worker | LOC | Files | Tests | Principle Violations | Rework Cycles | Time (est) |
|--------|-----|-------|-------|---------------------|---------------|------------|
| W1     | 200 | 2     | 5     | 0                   | 0             | 1.5h       |
| W2     | 150 | 1     | 3     | 0                   | 0             | 1h         |
| W3     | 180 | 2     | 4     | 0                   | 1             | 2h         |
| W4     | 220 | 2     | 6     | 0                   | 0             | 1.5h       |
| W5     | 250 | 3     | 7     | 0                   | 0             | 2h         |
| **Total** | **1000** | **10** | **25** | **0** | **1** | **8h** |

---

## Lessons Learned

[Update after EACH worker integration]

### From W1 Integration (Date)

**What worked:**
- [Specific thing that went well]

**What didn't:**
- [Specific thing that didn't work]

**Adjustment for remaining workers:**
- [What we'll do differently for W2, W3, etc.]

### From W2 Integration (Date)

**What worked:**
- [Improvement based on W1 feedback]

**What didn't:**
- [New issue discovered]

**Adjustment:**
- [Refinement for W3, W4, etc.]

[Continue for each worker]

---

## Integration Notes

### W1 Integration

**Date:** [timestamp]  
**Reviewed by:** Orchestrator  
**Decision:** ACCEPTED | REVISED | REJECTED  
**Issues found:** [N]  
**Fixes applied by orchestrator:** [list or "none"]  
**Notes:**

[Detailed notes about what was good, what needed adjustment, any concerns]

### W2 Integration

[Same structure]

---

## Timeline

| Event | Timestamp | Duration |
|-------|-----------|----------|
| Build started (framing) | [timestamp] | |
| Decomposition complete | [timestamp] | [duration] |
| W1 started | [timestamp] | |
| W1 completed | [timestamp] | [duration] |
| W1 integrated | [timestamp] | [integration time] |
| W2 started | [timestamp] | |
| ... | | |
| Build complete | [timestamp] | **Total: [duration]** |

---

## Technical Debt

**Incurred during this build:**

- [ ] [Item 1: description] - **Repayment plan:** [when/how]
- [ ] [Item 2: description] - **Repayment plan:** [when/how]

**Rationale for each:**

[Explain why debt was necessary and acceptable]

---

## Follow-Up Tasks

**Immediate:**
- [ ] [Task that must happen right after build]

**Short-term:**
- [ ] [Task within 1 week]

**Long-term:**
- [ ] [Task within 1 month]

---

## After-Action Report

[Generated when build status = COMPLETE]

### Outcome

✅ SUCCESS | ⚠️ PARTIAL SUCCESS | ❌ FAILED

**Overall assessment:**

[Paragraph summarizing build outcome, quality, lessons]

### What We Built

[Summary with links to key files/modules]

### Key Decisions

1. **Decision:** [What was decided]
   - **Rationale:** [Why]
   - **Trade-offs:** [What we gave up]
   - **Alternatives considered:** [What else we looked at]

2. [Continue for major decisions]

### Build Statistics

- **Total duration:** [hours/days]
- **Workers:** [N]
- **Total LOC:** [N]
- **Files modified:** [N]
- **Tests added:** [N]
- **Error count:** [N] ([breakdown by severity])
- **Rework cycles:** [N]
- **Integration issues:** [N]

### What Worked Well

1. [Specific thing]
2. [Specific thing]

### What Didn't Work

1. [Specific thing]
2. [Specific thing]

### Improvements for Next Build

1. [Actionable improvement based on this build]
2. [Actionable improvement based on this build]

### Template Updates Needed

- [ ] Update WORKER_ASSIGNMENT template: [specific change]
- [ ] Update protocol: [specific change]
- [ ] Add to troubleshooting: [specific issue]

### Principle Adherence

[Review against `file 'Knowledge/architectural/architectural_principles.md'`]

**Principles followed well:**
- [Principle]: [How we exemplified it]

**Principles challenged:**
- [Principle]: [Where we struggled or made trade-offs]

### Recommended for Future V

[Advice for future builds based on this experience]

---

**Last Updated:** [timestamp] by [orchestrator/worker-N]

---

## Quick Status Check

**Current phase:** [PLANNING/ACTIVE/INTEGRATION/COMPLETE]

**Workers ready to start:** [W1, W2, ...] (dependencies met)  
**Workers in progress:** [W3, W4, ...]  
**Workers blocked:** [W5: waiting on W3]  
**Workers complete:** [W1, W2]

**Next action:** [What should happen next]

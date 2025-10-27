# Worker Assignment: [TASK_NAME]

**Build:** [BUILD_NAME]  
**Worker ID:** W[N]  
**Orchestrator Workspace:** `/home/.z/workspaces/[ORCHESTRATOR_CONVERSATION_ID]/`  
**Status:** ASSIGNED

---

## Context

[2-3 sentences explaining what this change is part of and why it matters]

---

## Your Bounded Task

**What you're building:**

[Clear, specific scope - usually 1-3 files, 100-300 LOC]

**What you're NOT building:**

[Explicit anti-scope to prevent drift]

---

## Deliverables

1. [Specific file, function, or module]
2. [Tests or validation]
3. [Documentation]

**Acceptance Criteria:**

- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]
- [ ] Passes principle check: [relevant principle from `file 'Knowledge/architectural/architectural_principles.md'`]

---

## Dependencies

**Before you start, read:**

- `file '[path-to-dependency-1]'`
- `file '[path-to-dependency-2]'`

**Prerequisite workers:**

- [ ] W[N] must be INTEGRATED before you start (check BUILD_STATE_SESSION.md)

**Interfaces you'll implement:**

```[language]
[Exact function signatures, class definitions, or data structures]

# Example:
def process_data(input: Dict[str, Any]) -> ProcessedResult:
    """
    Process raw data according to spec.
    
    Args:
        input: Dict with keys 'source', 'timestamp', 'data'
    
    Returns:
        ProcessedResult with 'status', 'output', 'errors'
    """
    pass
```

**What other workers are doing:**

- **W[N]:** [Brief description] - Provides: [interface/data you'll consume]
- **W[N]:** [Brief description] - Consumes: [interface/data you'll provide]

---

## Constraints

**Files you CAN modify:**

- `[path-1]`
- `[path-2]`

**Files you CANNOT touch:**

- `[path-1]`
- `[path-2]`

**Max scope:** [LOC estimate or file count]

**Coding standards:**

- Follow `file 'Knowledge/architectural/principles/design.md'`
- Style: [specific style requirements if any]
- Testing: [minimum test coverage or approach]

---

## State Tracking

**Your responsibility:**

1. **When you start:**
   - Update BUILD_STATE_SESSION.md → W[N] status: IN_PROGRESS
   - Add timestamp

2. **If blocked:**
   - Generate error report: `/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_ERROR_LOG.md`
   - Update BUILD_STATE_SESSION.md → W[N] status: BLOCKED
   - Use error codes from `file 'N5/prefs/operations/distributed-builds/error-tracking-guide.md'`

3. **When complete:**
   - Update BUILD_STATE_SESSION.md → W[N] status: REVIEW
   - Add timestamp
   - Reference your summary

**State file location:**

`/home/.z/workspaces/[orchestrator-id]/BUILD_STATE_SESSION.md`

Or if already moved: `/home/workspace/N5/logs/builds/[build-name]/BUILD_STATE_SESSION.md`

---

## Quality Gates

**Before marking complete:**

1. **Run tests:**
   ```bash
   [Specific test commands]
   ```

2. **Validate against principles:**
   - Load `file 'Knowledge/architectural/architectural_principles.md'`
   - Check your work against relevant principles
   - Document any trade-offs

3. **Self-review checklist:**
   - [ ] All acceptance criteria met
   - [ ] Tests written and passing
   - [ ] No files modified outside whitelist
   - [ ] No scope creep
   - [ ] Error handling present
   - [ ] Documentation updated
   - [ ] No P13 (analysis paralysis) - shipped focused solution

4. **Generate summary:**
   - Location: `/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_SUMMARY.md`
   - Include:
     - What you built
     - Design decisions made (and why)
     - Edge cases handled
     - Integration notes for orchestrator
     - Any warnings or caveats

---

## Output Locations

**Your code goes here:**

`/home/workspace/[target-path]/[filename]`

[Specify exact paths for each deliverable]

**Your summary goes here:**

`/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_SUMMARY.md`

**If errors occur:**

`/home/workspace/N5/logs/builds/[build-name]/workers/W[N]_ERROR_LOG.md`

---

## Examples

**Example input:**

```[language]
[Provide example of what you'll receive]
```

**Example output:**

```[language]
[Provide example of what you should produce]
```

---

## Questions or Blockers

**If you're stuck:**

1. Check if it's a known error: `file 'N5/prefs/operations/distributed-builds/error-tracking-guide.md'`
2. Generate error report with code
3. Update BUILD_STATE_SESSION.md → BLOCKED
4. Tell user: "BLOCKED: E[code]. Report at [path]. Need orchestrator input."

**DO NOT:**

- Guess at unclear requirements
- Proceed when blocked
- Modify things outside your scope
- Skip testing

---

## Getting Started

1. Read this entire assignment
2. Read all dependency files
3. Check BUILD_STATE_SESSION.md for prerequisites
4. Update state → IN_PROGRESS
5. Begin implementation

**Ready? Update your status and start building.**

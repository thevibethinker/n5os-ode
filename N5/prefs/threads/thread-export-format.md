# Thread Export Format Specification

**Version:** 2.2  
**Date:** 2025-10-12  
**Purpose:** Standard format for thread exports to enable seamless resumption in new conversations

---

## Overview

This document defines the standard structure for exporting conversation threads. The format is optimized for LLM resumption, emphasizing actionability, constraint awareness, and state verification.

**Key Principles:**
- **Action-oriented** - Concrete next steps, not just narrative
- **Constraint-aware** - Explicit about what NOT to change
- **State-verified** - Precise snapshot for detecting drift
- **Context-rich** - Code patterns, decisions, gotchas included
- **Resumption-ready** - Designed for cold starts in new threads

---

## Format Versions

### v2.2 (Modular Format) - Current
**Date:** 2025-10-12  
**Status:** Production

**Structure:** 6 modular markdown files + JSON
- `INDEX.md` - Navigation hub and file directory
- `RESUME.md` - Quick resume entry point (10-minute workflow)
- `DESIGN.md` - Key decisions and rationale
- `IMPLEMENTATION.md` - Technical details and code patterns
- `VALIDATION.md` - Testing status and troubleshooting
- `CONTEXT.md` - Thread lineage and metadata
- `aar-YYYY-MM-DD.json` - JSON source of truth
- `artifacts/` - Copied workspace files

**Benefits:**
- Faster navigation (read only relevant sections)
- Clearer purpose for each file
- Better for resumption (start with INDEX → RESUME)
- Modular updates (edit one file without affecting others)

**Usage:**
```bash
# Generate modular export (default)
python3 N5/scripts/n5_thread_export.py --auto --title "My Thread"

# Explicitly specify modular format
python3 N5/scripts/n5_thread_export.py --auto --format modular
```

### v2.0 (Single File) - Legacy Compatible
**Date:** 2025-10-12  
**Status:** Maintained for backward compatibility

**Structure:** 1 markdown file + JSON
- `aar-YYYY-MM-DD.md` - Single comprehensive markdown
- `aar-YYYY-MM-DD.json` - JSON source of truth
- `artifacts/` - Copied workspace files

**Usage:**
```bash
# Generate single-file export (backward compatible)
python3 N5/scripts/n5_thread_export.py --auto --format single
```

---

## V2.2 Modular File Specifications

### INDEX.md
**Purpose:** Navigation hub - first file to read when resuming

**Contents:**
- File directory table (what each file contains)
- Quick start workflow (reading order)
- File statistics (artifact count, sizes)
- Export metadata

**Audience:** Anyone resuming the thread

### RESUME.md
**Purpose:** Quick 10-minute resume entry point

**Contents:**
- Summary (purpose & outcome)
- Quick start workflow (10-minute plan)
- What was completed (key artifacts)
- Critical constraints (what NOT to change)
- Next steps (prioritized actions)
- Context for resumption

**Audience:** Resuming work immediately

### DESIGN.md
**Purpose:** Decision rationale and design choices

**Contents:**
- Critical constraints
- Key technical decisions
- Alternatives considered
- Trade-offs made
- Lessons learned

**Audience:** Understanding why choices were made

### IMPLEMENTATION.md
**Purpose:** Technical implementation details

**Contents:**
- What was completed (detailed)
- Code patterns and quick reference
- File structure
- Common operations
- Integration points

**Audience:** Implementing or modifying the system

### VALIDATION.md
**Purpose:** Testing and troubleshooting guide

**Contents:**
- Testing status
- Known issues and gotchas
- Troubleshooting guide
- Debug commands
- If stuck, check these

**Audience:** Debugging or testing the system

### CONTEXT.md
**Purpose:** Historical context and metadata

**Contents:**
- Thread lineage (previous/related threads)
- System architecture context
- User preferences
- Files created/modified
- Metadata and telemetry

**Audience:** Background research or understanding history

---

## V2.0 Single File Template (Legacy)


## Complete Template Structure

```markdown
# Thread Export: [Descriptive Title]

**Thread ID:** con_XXXXXXXXXXXXXXXX  
**Export Date:** YYYY-MM-DD  
**Topic:** [Brief topic description]  
**Status:** [Complete | In Progress | Blocked]

---

## Summary

[2-3 sentences: What was accomplished, what's the current state, and what comes next]

---

## Quick Start

**First 10 minutes:**

1. **Verify state** (2 min)
   ```bash
   # Check key files/resources exist
   ls [paths]
   [verification_command]
   ```
   Expected: [what you should see]

2. **Understand context** (3 min)
   - Read "Critical Constraints" below
   - Skim "What Was Completed"
   - Note "Known Issues"

3. **Start work** (5 min)
   - [First concrete action from Next Steps]
   - [Expected outcome]

---

## What Was Completed

### 1. [Deliverable Name]
- **File(s):** `file 'path/to/file'`
- **Purpose:** [What it does]
- **Key Features:**
  - Feature 1
  - Feature 2
  - Feature 3
- **Status:** ✅ Complete | ⏳ In Progress | ❌ Blocked

### 2. [Deliverable Name]
- **File(s):** `file 'path/to/file'`
- **Purpose:** [What it does]
- **Components:**
  - Component A - [description]
  - Component B - [description]
- **Status:** ✅/⏳/❌

### 3. [Additional Deliverables]
...

---

## Critical Constraints

**DO NOT CHANGE:**
- ❌ [System dependency] - breaks [what] if modified
- ❌ [Design pattern] - other code depends on this
- ❌ [File structure] - [what] expects this layout
- ❌ [Data format] - breaking change for [consumers]

**MUST PRESERVE:**
- ✅ [Safety pattern] - required for [reason]
- ✅ [Compatibility rule] - ensures [what]
- ✅ [Convention] - maintained across [where]

**PERFORMANCE/QUALITY BARS:**
- [Metric]: Must be [operator] [threshold]
- [Requirement]: [specific constraint]
- [Quality gate]: [acceptance criteria]

---

## Key Technical Decisions

### Decision: [Topic]
- **Choice made:** [What was decided]
- **Rationale:** [Why this approach was chosen]
- **Alternatives considered:**
  - Option A: [why rejected]
  - Option B: [why rejected]
- **Trade-offs:** [What we gave up, what we gained]
- **Implications:** [Impact on future work]

### Decision: [Topic]
...

---

## Known Issues / Gotchas

### 🐛 Issue: [Brief title]
- **Problem:** [What happens]
- **Cause:** [Root cause if known]
- **Workaround:** [How to avoid or fix]
- **TODO:** [Permanent fix, if planned]

### ⚠️ Gotcha: [Brief title]
- **Issue:** [Non-obvious behavior]
- **Impact:** [What could go wrong]
- **Solution:** [How to handle correctly]

### 🔧 Workaround: [Brief title]
- **Limitation:** [What doesn't work properly]
- **Mitigation:** [Temporary solution]
- **Code:**
  ```bash
  # Example workaround
  [command or snippet]
  ```

---

## Anti-Patterns / Rejected Approaches

### ❌ Approach: [Brief description]
- **Why rejected:** [Fundamental reason it doesn't work]
- **Lesson learned:** [What to do instead]
- **Context:** [When/why this was tried]

### ❌ Don't: [Specific pattern to avoid]
- **Problem:** [Why it's wrong/dangerous]
- **Correct way:** [Right approach]
- **Example:**
  ```python
  # WRONG:
  [bad pattern]
  
  # RIGHT:
  [correct pattern]
  ```

---

## Integration Points & Next Steps

### Scripts/Systems to Update

#### 1. [Script/System Name]
- **File:** `file 'path/to/file'`
- **Action:** [What needs to be done]
- **Pattern:** [Approach or pseudocode]
  ```python
  # Example pattern
  [code showing how to integrate]
  ```
- **Priority:** H | M | L
- **Status:** ⏳ Pending | ✅ Done

#### 2. [Script/System Name]
...

### Integration Architecture

```
[ASCII diagram or description of how components connect]
```

### Data/Control Flow
[Description of how information flows through the system]

---

## Code Patterns / Quick Reference

### [Pattern Category 1]

```python
# [Description of pattern]
def example_function(arg1, arg2):
    """
    [What this does]
    
    Args:
        arg1: [description]
        arg2: [description]
    
    Returns:
        [description]
    """
    [implementation showing pattern]
```

### [Pattern Category 2]

```bash
# [Description of CLI pattern]
command --flag value
```

### Common Operations

| Task | Command | Notes |
|------|---------|-------|
| [Task 1] | `command1` | [When to use] |
| [Task 2] | `command2` | [Important note] |

---

## State Snapshot

**As of export (YYYY-MM-DD HH:MM UTC):**

### File System
```
directory/
├── file1 (size, state)
├── file2 (size, state)
└── subdirectory/
    └── file3 (record count or status)
```

### Key Files Status
- `path/to/file`: [size KB/MB], [state description]
- `another/file`: [N records/items], [status]
- `script.py`: [tested ✅ | untested ⏳ | broken ❌]

### System State
- Database/store: [size], [N records], [status]
- Cache/temp: [state]
- External dependencies: [versions/status]

### Commands/Scripts Status
| Command | Status | Notes |
|---------|--------|-------|
| [name] | ✅ Working | [note] |
| [name] | ⏳ Untested | [note] |
| [name] | ❌ Broken | [issue] |

### Dependencies
- [dependency]: [version] ✅
- [package]: [status/version]
- [external service]: [configured/not configured]

---

## Testing Status

### Completed Tests
✅ [Test category 1] - [specific tests]  
✅ [Test category 2] - [specific tests]

### Pending Tests
⏳ [Test category 3] - [what needs testing]  
⏳ [Test category 4] - [what needs testing]

### Known Failures
❌ [Test category 5] - [issue description]

### Test Commands
```bash
# Run specific test
[test_command]

# Run full suite
[suite_command]

# Smoke test
[quick_validation]
```

---

## Open Questions

### 1. [Question about unresolved decision]
- **Context:** [Why this matters]
- **Options:**
  - A: [approach 1]
  - B: [approach 2]
- **Recommendation:** [If any]
- **Blocking:** [Yes/No - what it blocks]

### 2. [Question about approach]
- **Issue:** [What's unclear]
- **Impact:** [What this affects]
- **Need:** [What information/decision is needed]

---

## If Stuck, Check These

### Problem: [Common issue 1]
**Check:**
1. [Diagnostic step]
2. [Another check]
3. [Validation command]: `command`

**Solution:** [If found]

### Problem: [Common issue 2]
**Check:**
- [Diagnostic approach]
- [Log to examine]: `path/to/log`

**Typical cause:** [Common root cause]

### Problem: [Integration doesn't work]
**Debug steps:**
```bash
# Step 1: Verify X
[command]

# Step 2: Check Y
[command]

# Step 3: Test Z
[command]
```

---

## System Architecture Context

### Where This Fits

```
System/
├── Component A/          ← Upstream dependency
│   └── provides data
│
├── THIS WORK/           ← Current scope
│   ├── file1
│   └── file2
│
└── Component B/          ← Downstream consumer
    └── uses our output
```

### Data Flow
```
Input → [Processing] → [Transformation] → Output → [Consumer]
          ↓
      [Storage/Cache]
```

### Integration Points

| System | Integration Type | Status | Notes |
|--------|-----------------|---------|-------|
| [Name] | [Reads/Writes/Calls] | ✅/⏳/❓ | [Note] |
| [Name] | [Relationship] | [Status] | [Note] |

### Dependencies
- **Upstream:** [What provides data/input to this]
- **Downstream:** [What consumes output from this]
- **Parallel:** [What else might be affected]

---

## Assumptions & Validations

**Assumed to be TRUE (verify if resuming after time gap):**
- [ ] [Assumption 1 about system state]
- [ ] [Assumption 2 about file structure]
- [ ] [Assumption 3 about external dependencies]

**Assumed to be FALSE (confirm if changed):**
- [ ] [Thing we expect not to exist yet]
- [ ] [Constraint we expect still holds]
- [ ] [Feature we expect not implemented]

**Quick validation commands:**
```bash
# Validate assumption 1
[command]

# Validate assumption 2
[command]

# Check if anything changed
[command]
```

---

## User Preferences (V's Style)

### Code Style
- ✅ Use pathlib.Path, not os.path
- ✅ Type hints in function signatures
- ✅ Docstrings for public functions
- ✅ Explicit better than implicit
- ❌ Don't abbreviate variable names excessively

### Error Handling
- ✅ Specific try/except with recovery
- ✅ Log errors with context
- ✅ Clear error messages
- ❌ Don't silently swallow exceptions

### Testing Approach
- ✅ Dry-run mode for destructive ops
- ✅ Sample data before full run
- ✅ Manual smoke tests before automation

### File Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Files: `snake_case.py` or `kebab-case.md`

### Safety Requirements
- ✅ Backup before modifications
- ✅ Validation before writes
- ✅ Rollback capability
- ✅ Confirmation for destructive ops

---

## Files Created/Modified

### Created
- `path/to/file1` - [Brief description of purpose]
- `path/to/file2` - [Brief description]
- `directory/` - [What it contains]

### Modified
- `existing/file` - [What changed and why]
- `another/file` - [What changed and why]

### Deleted
- `old/file` - [Why it was removed]

---

## Thread Lineage & Related Work

### Previous Related Threads
- Thread con_ABC...: [Topic] (YYYY-MM-DD)
  - Outcome: [What was accomplished]
  - Relationship: [How it relates to this work]

### Related System Components
- [Component]: [How it connects to this work]
- [System]: [Potential future integration]

### Cross-Cutting Concerns
- [Concern 1]: [How it affects this work]
- [Concern 2]: [What needs consideration]

---

## Success Criteria

**Definition of Done:**
- [ ] [Specific measurable outcome 1]
- [ ] [Specific measurable outcome 2]
- [ ] [Specific measurable outcome 3]

**Quality Gates:**
- [ ] [Performance requirement met]
- [ ] [All tests passing]
- [ ] [Documentation complete]
- [ ] [Integration verified]

**Acceptance Tests:**
```bash
# Test 1: [Description]
[command] | grep "expected output"

# Test 2: [Description]
[command] && echo "PASS" || echo "FAIL"
```

---

## Context for Resume

**When resuming this thread:**

### Step 1: Verify Environment (5 min)
```bash
# Check state snapshot matches
[validation_commands_from_state_snapshot_section]
```

### Step 2: Review Key Context (5 min)
- Read "Critical Constraints" - know what NOT to change
- Read "Known Issues" - avoid known problems
- Read "What Was Completed" - understand current state

### Step 3: Validate Assumptions (3 min)
```bash
# Run assumption checks
[commands_from_assumptions_section]
```

### Step 4: Start Work (from Next Steps)
- Priority 1: [Action from Integration Points section]
- Use code patterns from "Code Patterns" section
- Follow conventions from "User Preferences" section

### Step 5: Verify Progress
- Run tests from "Testing Status" section
- Check success criteria
- Update status markers (✅/⏳/❌)

---

## Related Documentation

- **System Overview:** `file 'Documents/N5.md'`
- **Preferences:** `file 'N5/prefs/prefs.md'`
- **Related Schema:** `file 'N5/schemas/[relevant].schema.json'`
- **Previous Thread:** `file 'N5/logs/threads/con_XXX/aar.md'`
- **Command Reference:** `file 'N5/commands/[relevant-command].md'`

---

## Export Metadata

**Generated by:** Vrijen The Vibe Strategist (Zo)  
**Generation method:** Interactive  
**Export format version:** 2.0  
**Schema validation:** ✅ Passed (against `N5/schemas/aar.schema.json`)

**Artifact Statistics:**
- Files created: [N]
- Files modified: [N]
- Total size: [N KB/MB]
- Code files: [N]
- Documentation files: [N]

---

**Ready for continuation:** [Yes | No - explain blockers if No]

**To resume:** Load this file, verify state snapshot, review Critical Constraints and Known Issues, then proceed with Next Steps.
```

---

## Section Usage Guidelines

### When to Include Each Section

**Always Include:**
- Summary
- Quick Start
- What Was Completed
- Critical Constraints
- State Snapshot
- Integration Points & Next Steps
- Files Created/Modified
- Context for Resume

**Include When Applicable:**
- Key Technical Decisions (if design choices were made)
- Known Issues (if problems encountered)
- Anti-Patterns (if approaches were tried and rejected)
- Code Patterns (if reusable patterns exist)
- Testing Status (if tests were written)
- Open Questions (if decisions pending)
- System Architecture (for complex integrations)
- Assumptions (if environment-dependent)

**Optional/Nice-to-Have:**
- If Stuck (for complex domains)
- User Preferences (can standardize across exports)
- Thread Lineage (for ongoing work)
- Related Documentation (when deep integration exists)

---

## Formatting Conventions

### Status Indicators
- ✅ Complete/Working/Passed
- ⏳ In Progress/Pending/Untested
- ❌ Blocked/Broken/Failed
- ❓ Unknown/To Be Determined
- 🔮 Future/Planned

### Priority Levels
- **H** - High priority (blocking or critical)
- **M** - Medium priority (important but not blocking)
- **L** - Low priority (nice-to-have)

### File References
Use inline file mentions: `file 'relative/path/to/file'`

### Code Blocks
- Include language identifiers: ```python, ```bash, ```sql
- Add comments explaining non-obvious parts
- Show both wrong and right patterns when illustrating anti-patterns

### Sections
- Use ## for major sections
- Use ### for subsections
- Use #### sparingly for deep nesting

---

## Version History

### v2.0 - 2025-10-12
- Complete restructure based on LLM resumption optimization
- Added Quick Start section
- Added Critical Constraints section
- Added State Snapshot section
- Added Known Issues section
- Added Anti-Patterns section
- Added System Architecture Context
- Added Assumptions & Validations
- Enhanced Context for Resume section
- Removed Quick Verification Checklist (too granular)

### v1.0 - 2025-10-03
- Initial format based on manual AAR examples
- Basic structure: Summary, Events, Artifacts, Next Steps

---

## Related Files

- **Schema:** `file 'N5/schemas/aar.schema.json'`
- **Export Script:** `file 'N5/scripts/n5_thread_export.py'`
- **Command:** `file 'N5/commands/thread-export.md'`
- **System Preferences:** `file 'N5/prefs/prefs.md'`

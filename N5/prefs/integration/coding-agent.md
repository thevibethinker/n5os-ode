# Coding Agent Preference

**Module:** Integration  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Preference

**Always launch a coding agent whenever possible for coding tasks** because it leads to better outcomes.

**Type:** Soft preference that guides decision-making but allows flexibility when direct editing is more appropriate for simple changes.

---

## When to Use Coding Agent

### High-Priority Cases (Always Use)

1. **Planning Complex Code Changes**
   - Multi-file modifications
   - Architectural decisions
   - Refactoring operations

2. **Processing Ambiguous Requirements**
   - Unclear specifications
   - Multiple possible approaches
   - Need for design decisions

3. **Substantial Code Changes**
   - Adding new features
   - Implementing new modules
   - Large-scale refactoring

4. **Code Analysis Tasks**
   - Understanding existing codebase
   - Identifying patterns or issues
   - Dependency analysis

---

### Medium-Priority Cases (Prefer Coding Agent)

1. **Multi-step workflows**
   - Sequential operations across files
   - Complex build processes
   - Testing and validation

2. **Configuration changes with dependencies**
   - Package installations
   - Environment setup
   - Build configuration

3. **Debugging complex issues**
   - Stack trace analysis
   - Cross-file debugging
   - Performance optimization

---

### Low-Priority Cases (Direct Editing OK)

1. **Simple, single-line fixes**
   - Typo corrections
   - Variable renaming (single occurrence)
   - Comment additions

2. **Trivial configuration updates**
   - Version number bumps
   - Single config value changes

3. **Small content changes**
   - Documentation updates
   - Comment clarifications

---

## Rationale

The coding agent provides specialized capabilities:

1. **Comprehensive code analysis**
   - Full codebase understanding
   - Dependency tracking
   - Pattern recognition

2. **Better planning**
   - Multi-step execution plans
   - Risk assessment
   - Rollback strategies

3. **Higher quality results**
   - More thorough testing
   - Better error handling
   - Cleaner implementation

4. **Complex problem solving**
   - Creative solutions
   - Multiple approach evaluation
   - Optimization strategies

---

## How to Invoke

**Via Zo (if `perform_coding_task` tool available):**

```
perform_coding_task(
    instruction="[Clear description of coding task]",
    project_path="/home/workspace/[project-path]"
)
```

**Fallback (Manual coding work):**

If coding agent tool is not available, proceed with standard code editing tools but apply coding agent principles:
1. Read and understand context first
2. Plan changes before executing
3. Test and validate results
4. Document changes clearly

---

## Examples

### Example 1: Refactor Function (Use Coding Agent)

**Task:** Refactor a function across multiple files to improve performance

**Why coding agent:**
- Multi-file changes
- Performance analysis needed
- Risk of breaking dependencies

---

### Example 2: Fix Typo (Direct Edit OK)

**Task:** Fix typo in variable name (single occurrence)

**Why direct edit:**
- Single file, single line
- No dependencies affected
- Trivial change

---

### Example 3: Add New Feature (Use Coding Agent)

**Task:** Add authentication to web application

**Why coding agent:**
- Multiple files involved
- Security considerations
- Testing required
- Configuration changes

---

### Example 4: Update Version Number (Direct Edit OK)

**Task:** Bump version number in package.json

**Why direct edit:**
- Single file, single field
- No logic changes
- Standard operation

---

## Decision Tree

```
Is the change multi-file?
├─ Yes → Use coding agent
└─ No  → Is it complex logic?
          ├─ Yes → Use coding agent
          └─ No  → Is it trivial (typo, comment)?
                   ├─ Yes → Direct edit OK
                   └─ No  → Prefer coding agent
```

---

## Integration with Other Preferences

### File Protection

Coding agent should still respect:
- `file 'N5/prefs/system/file-protection.md'`
- Hard protection files (manual edit only)
- Dry-run requirements for medium protection

---

### Safety Rules

Coding agent should follow:
- `file 'N5/prefs/system/safety.md'`
- Explicit consent for deployments
- Dry-run for destructive operations

---

## Related Files

- **File Protection:** `file 'N5/prefs/system/file-protection.md'`
- **Safety Rules:** `file 'N5/prefs/system/safety.md'`
- **Google Drive Integration:** `file 'N5/prefs/integration/google-drive.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Added detailed when-to-use guidelines
- Added priority levels (high/medium/low)
- Added rationale and examples
- Added decision tree
- Cross-referenced safety and file protection rules

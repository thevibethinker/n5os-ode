# Validation System

**Purpose:** Proactive detection of stubs, placeholders, broken references, and contract issues during build orchestration.

**Version:** 1.0  
**Created:** 2025-10-28

---

## Overview

The validation system provides automated checks to catch common integration issues **during** the build process, not just at the end. It's integrated into the build orchestrator to provide early detection of problems.

### Problem Statement

Build orchestration with multiple workers often results in:
- Stub implementations (`raise NotImplementedError`)
- Placeholder comments (`TODO`, `FIXME`, `XXX`)
- Broken imports (missing modules, typos)
- Missing function contracts (type hints, docstrings)

These issues typically aren't caught until integration phase, wasting time and requiring rework.

### Solution

Enhanced orchestrator with **validation hooks** that scan code after each worker completes, providing immediate feedback on integration issues.

---

## Architecture

```
Orchestrator
├── Worker 1 → validate()
├── Worker 2 → validate()
├── Worker 3 → validate()
└── Final Integration → validate()
```

**Key Decision:** Validation is **part of the orchestrator**, not a separate worker. This keeps it lightweight and avoids API call overhead.

---

## Components

### 1. validation.py

Core validation engine with pluggable checks.

**Checks:**
- **Stubs:** `raise NotImplementedError`, `def foo(): pass`, `def foo(): ...`
- **Placeholders:** `TODO`, `FIXME`, `XXX`, `PLACEHOLDER`, `HACK`
- **Broken Imports:** Unresolvable modules (AST-based)
- **Contracts:** Missing type hints, missing docstrings (public functions)

**Usage:**
```bash
# Scan for stubs and imports only
python3 N5/scripts/validation.py scan /path/to/project

# Check contracts only
python3 N5/scripts/validation.py check-contracts /path/to/project

# Full sweep (all checks)
python3 N5/scripts/validation.py sweep /path/to/project --all

# JSON output
python3 N5/scripts/validation.py sweep /path/to/project --json
```

**Exit Codes:**
- `0`: No critical issues (warnings OK)
- `1`: Critical issues found (errors)

### 2. Enhanced Orchestrator

New `validate` action integrated into orchestrator.py.

**Usage:**
```bash
# Validate project
python3 N5/scripts/orchestrator.py validate /path/to/project

# Fail build on errors
python3 N5/scripts/orchestrator.py validate /path/to/project --fail-on-error

# During orchestration (automatic)
# Orchestrator calls validate_project() after each worker
```

**Output:**
- Console summary (errors, warnings)
- Detailed report: `<orchestrator_workspace>/VALIDATION_REPORT.md`
- JSON result with stats

---

## Validation Rules

### Severity Levels

- **Error:** Blocks integration (stubs, broken imports, syntax errors)
- **Warning:** Should fix but not blocking (placeholders)
- **Info:** Best practice violations (missing docstrings, missing type hints)

### Configurable (Future)

Validation config in `N5/config/validation.json`:
```json
{
  "fail_on": ["stubs", "broken_imports", "syntax"],
  "warn_on": ["placeholders"],
  "ignore": ["missing_docstrings"],
  "ignore_patterns": ["**/test_*.py", "**/__init__.py"]
}
```

---

## Workflow Integration

### During Build Orchestration

1. Orchestrator assigns tasks to workers
2. Workers complete work
3. **Orchestrator validates** worker output
4. If validation fails → flag for review
5. If validation passes → proceed to next worker
6. Final validation before integration

### Manual Usage

```bash
# Quick check during development
cd /home/workspace/my-project
python3 /home/workspace/N5/scripts/validation.py sweep . --all

# Orchestrator command
python3 /home/workspace/N5/scripts/orchestrator.py validate /home/workspace/my-project
```

---

## Example Output

### Console Output
```
2025-10-28T07:29:35Z INFO Scanning /home/workspace/my-project...
2025-10-28T07:29:35Z INFO ✓ Validation complete:
2025-10-28T07:29:35Z INFO   Files scanned: 23
2025-10-28T07:29:35Z INFO   Errors: 2
2025-10-28T07:29:35Z INFO   Warnings: 5
2025-10-28T07:29:35Z ERROR ❌ Critical issues found:
2025-10-28T07:29:35Z ERROR   [stub] auth.py:45 - Stub implementation detected
2025-10-28T07:29:35Z ERROR   [broken_import] utils.py:12 - Cannot resolve import: nonexistent_module
2025-10-28T07:29:35Z WARNING ⚠️  Warnings found:
2025-10-28T07:29:35Z WARNING   [placeholder] handlers.py:89 - Placeholder comment found
2025-10-28T07:29:35Z WARNING   [placeholder] models.py:34 - Placeholder comment found
```

### JSON Output
```json
{
  "status": "fail",
  "files_scanned": 23,
  "errors": 2,
  "warnings": 5,
  "report_file": "/home/.z/workspaces/con_ABC/VALIDATION_REPORT.md",
  "timestamp": "2025-10-28T07:29:35.123Z"
}
```

---

## Testing

Test suite: `N5/scripts/test_validation.py`

Creates temporary project with known issues and validates detection.

```bash
python3 /home/workspace/N5/scripts/test_validation.py
```

**Expected Results:**
- Detects stubs
- Detects placeholders  
- Detects broken imports
- Detects missing contracts

---

## Performance

**Lightweight:**
- AST parsing (no runtime execution)
- Single-threaded (fast enough for typical projects)
- ~0.1s per Python file

**Scalability:**
- 100 files: ~10s
- 1000 files: ~100s

**Optimization opportunities:**
- Parallel file scanning
- Incremental validation (only changed files)
- Caching parse trees

---

## Future Enhancements

### Phase 2
- Configuration file support
- Custom validation rules (regex patterns)
- Ignore patterns (test files, generated code)
- Git integration (only validate changed files)

### Phase 3
- Continuous monitoring (file watcher)
- IDE integration (LSP server)
- Auto-fix suggestions
- Validation dashboard

---

## Principles Alignment

- **P15 (Complete Before Claiming):** Validation enforces this by detecting stubs
- **P16 (No Invented Limits):** No arbitrary limits on checks
- **P18 (Verify State):** Validation is state verification
- **P19 (Error Handling):** Robust error handling in scanner
- **P0 (Rule-of-Two):** Integrated into orchestrator, not separate component

---

## Related Files

- `N5/scripts/validation.py` - Core validation engine
- `N5/scripts/orchestrator.py` - Enhanced orchestrator with validation
- `N5/scripts/test_validation.py` - Test suite
- `n5os-core/Documents/BUILD_ORCHESTRATOR.md` - Orchestrator documentation

---

**Questions? Issues?**
See `BUILD_ORCHESTRATOR.md` for broader context, or check test suite for examples.

---

*v1.0 | 2025-10-28 | Initial implementation*

# Validation System - Quick Reference

**Purpose:** Catch stubs, placeholders, and broken refs during build orchestration

---

## Quick Commands

```bash
# Full validation sweep
python3 /home/workspace/N5/scripts/validation.py sweep /path/to/project --all

# From orchestrator
python3 /home/workspace/N5/scripts/orchestrator.py validate /path/to/project

# Run tests
python3 /home/workspace/N5/scripts/test_validation.py
```

---

## What It Detects

### Errors (Blocking)
- ✗ Stub implementations: `raise NotImplementedError`
- ✗ Empty functions: `def foo(): pass`
- ✗ Broken imports: `import nonexistent_module`
- ✗ Syntax errors

### Warnings (Non-blocking)
- ⚠️ TODO comments
- ⚠️ FIXME comments
- ⚠️ XXX/HACK comments

### Info
- ℹ️ Missing type hints
- ℹ️ Missing docstrings (public functions)

---

## Integration with Orchestrator

Validation runs **automatically** after each worker completes:

1. Worker finishes task
2. Orchestrator calls `validate_project(worker_output_path)`
3. If errors found → report saved to workspace
4. Orchestrator decides: retry worker or flag for manual review

---

## Exit Codes

- `0`: Pass (no errors, warnings OK)
- `1`: Fail (errors found)

---

## Output Files

**Console:** Immediate feedback with summary  
**Report:** `<orchestrator_workspace>/VALIDATION_REPORT.md`  
**JSON:** `--json` flag for programmatic use

---

## Configuration (Future)

Will support `N5/config/validation.json`:

```json
{
  "fail_on": ["stubs", "broken_imports"],
  "warn_on": ["placeholders"],
  "ignore": ["test_*.py"],
  "severity": {
    "missing_docstrings": "info"
  }
}
```

---

## Architecture

**Design Decision:** Validation is **part of orchestrator**, not a separate worker.

**Why?**
- Lightweight (no API calls)
- Fast (AST parsing, no runtime)
- Integrated (runs after each worker)

---

## Performance

- ~0.1s per Python file
- 100 files: ~10s
- 1000 files: ~100s

---

## Files

- `validation.py` - Core engine
- `orchestrator.py` - Integration
- `test_validation.py` - Test suite
- `VALIDATION_SYSTEM.md` - Full docs

---

**See:** file 'n5os-core/Documents/VALIDATION_SYSTEM.md' for complete documentation.

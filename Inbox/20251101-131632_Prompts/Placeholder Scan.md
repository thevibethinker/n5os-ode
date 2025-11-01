---
description: 'Command: placeholder-scan'
tags:
- quality
- principles
- P16
- P21
- conversation-end
tool: true
---
# Placeholder Scan

**Purpose:** Scan conversation workspace for placeholders, stubs, and incomplete code

**Enforces:** P16 (Accuracy Over Sophistication), P21 (Document Assumptions)

**Integration:** Runs automatically at Phase 2.5 of conversation-end workflow

---

## Overview

Detects incomplete work before it leaves conversation context:
- **Placeholders** - TODO, FIXME, undocumented assumptions
- **Fake Data** - test@example.com, 555-1234, dummy values
- **Function Stubs** - Functions without implementation or docstrings
- **Invented Constraints** - "API limit of 5 messages" without citation
- **Hardcoded Paths** - /Users/john/, localhost:3000
- **Empty Exception Handlers** - `except: pass` (P19 violation)

---

## Usage

### Standalone Scan

```bash
# Scan current conversation workspace (auto-detected)
python3 N5/scripts/n5_placeholder_scan.py

# Scan specific workspace
python3 N5/scripts/n5_placeholder_scan.py --workspace /path/to/workspace

# Dry-run mode
python3 N5/scripts/n5_placeholder_scan.py --dry-run
```

### Within Conversation-End

Automatically runs at Phase 2.5 (after cleanup, before git check).

**Behavior:**
- ✅ **Clean:** Continues to next phase
- ⚠️ **Issues found:** Blocks conversation-end, requires resolution

**Resolution options:**
1. **Fix now** - Return to conversation, abort conversation-end
2. **Document as intentional** - Add `# DOCUMENTED:` prefix to line
3. **Acknowledge & continue** - Log issues for later (tracked)

---

## Detection Patterns

### Critical Severity

**Invented Constraints (P16 Violation)**
```python
# ❌ Gmail API has a limit of 3 messages per day
# ✅ Gmail API limits: https://developers.google.com/gmail/api/reference/quota
```

### High Severity

**Function Stubs Without Docstrings**
```python
# ❌
def process_data(user_id):
    pass

# ✅
def process_data(user_id):
    """
    Process user data - NOT IMPLEMENTED YET
    Waiting for: API access, data schema definition
    """
    pass
```

**Fake Data**
```python
# ❌
email = "test@example.com"
phone = "555-1234"

# ✅
email = config.get("notification_email")
phone = user.phone_number
```

**Empty Exception Handlers**
```python
# ❌
try:
    risky_operation()
except:
    pass

# ✅
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return None
```

### Medium Severity

**Comment Placeholders**
```python
# ❌
# TODO: implement this

# ✅
# TODO: implement retry logic after confirming API timeout behavior
# DOCUMENTED: Placeholder until user provides API key
```

**Hardcoded Paths**
```python
# ❌
data_dir = "/Users/john/data"

# ✅
data_dir = Path.home() / "data"
```

---

## Exclusion Mechanism

Prefix lines with special comments to exclude from scan:

```python
# DOCUMENTED: Using placeholder email for demo purposes
demo_email = "test@example.com"

# INTENTIONAL: Empty handler is correct here (fire-and-forget)
except ConnectionError:
    pass

# KNOWN: Function stub - will implement after API docs arrive
def future_feature():
    pass
```

---

## Configuration

Pattern definitions: `file 'N5/config/placeholder_patterns.json'`

**File type rules:**
- Python: All patterns
- Shell: Comments, fake data, hardcoded paths
- JavaScript: All patterns
- Markdown: Fake data, invented constraints
- Config files: Fake data, hardcoded paths

**Pattern categories:**
1. `comment_placeholders` - TODO, FIXME, XXX, HACK
2. `fake_data` - test@example.com, 555-xxxx, dummy-*
3. `function_stubs` - def func(): pass
4. `invented_constraints` - "limit of N messages"
5. `hardcoded_paths` - /Users/*, C:\Users\*
6. `empty_exception_handlers` - except: pass
7. `unclosed_context` - open() without with

---

## Integration with Conversation-End

**Phase sequence:**
```
Phase -1: Lesson Extraction
Phase 0:  AAR Generation
Phase 1:  File Organization
Phase 2:  Workspace Root Cleanup
Phase 2.5: Placeholder Scan  ← NEW
Phase 3:  Personal Intelligence Update
Phase 4:  Git Status Check
Phase 4.5: Timeline Update
```

**Blocking behavior:**
- Scanner returns exit code 1 → conversation-end pauses
- User must choose: fix, document, or acknowledge
- Only "acknowledge" or "fix then re-run" continues workflow

---

## Exit Codes

- **0** - Clean (no issues found)
- **1** - Issues found (requires resolution)
- **2** - Scan error (technical failure)

---

## Output

### Clean Result
```
╔══════════════════════════════════════════════════════════════════════╗
║              PLACEHOLDER SCAN: ✅ NO ISSUES FOUND                    ║
╚══════════════════════════════════════════════════════════════════════╝

All files are clean. No placeholders, stubs, or fake data detected.
```

### Issues Detected
```
======================================================================
⚠️  PLACEHOLDER SCAN: ISSUES DETECTED
======================================================================

Total issues: 5

🔴 CRITICAL SEVERITY (1 issues)
----------------------------------------------------------------------

📄 script.py
   Line   23: Potential invented constraint (P16 violation)
              # API limit of 5 requests per hour

🟠 HIGH SEVERITY (2 issues)
----------------------------------------------------------------------

📄 script.py
   Line   45: Function stub without implementation or docstring
              def process_data(): pass

📄 config.py
   Line   12: Fake or placeholder data detected
              email = "test@example.com"

======================================================================
RESOLUTION REQUIRED
======================================================================
```

---

## Design Principles Applied

✅ **P16 (Accuracy):** Catches invented constraints before they propagate  
✅ **P21 (Document Assumptions):** Enforces explicit documentation of incomplete work  
✅ **P19 (Error Handling):** Detects empty exception handlers  
✅ **P7 (Dry-Run):** Supports dry-run mode for testing  
✅ **P15 (Complete Before Claiming):** Blocks "done" until actually complete  
✅ **P20 (Modular Design):** Standalone script callable from any workflow

---

## Troubleshooting

**False Positive?**
Add exclusion prefix: `# DOCUMENTED:` or `# INTENTIONAL:`

**Scan Times Out?**
Default timeout: 60s. Check for large binary files in workspace.

**Pattern Misses Issue?**
Update `file 'N5/config/placeholder_patterns.json'` and re-run.

**Want to Skip?**
In auto mode (`--auto` flag), issues are logged but don't block.

---

## Related Commands

- `file 'N5/commands/conversation-end.md'` - Full workflow that includes this scan
- `file 'N5/commands/system-design-workflow.md'` - Design principles this enforces
- `file 'Knowledge/architectural/principles/quality.md'` - P15, P16, P21 details

---

**Version:** 1.0.0  
**Created:** 2025-10-15  
**Status:** Active  
**Script:** `file 'N5/scripts/n5_placeholder_scan.py'`  
**Config:** `file 'N5/config/placeholder_patterns.json'`

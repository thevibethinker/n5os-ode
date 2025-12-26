# system-health

**Run diagnostic health check on N5 system**

Quick diagnostic to verify core N5 components are functioning properly.

---

## Usage

```bash
# Full health check
python3 N5/scripts/n5_system_health.py

# Quick check (essential only)
python3 N5/scripts/n5_system_health.py --quick

# Verbose output
python3 N5/scripts/n5_system_health.py --verbose
```

---

## What It Checks

### 1. Core Files
- N5 directory structure intact
- Essential scripts present
- Config files readable
- Permissions correct

### 2. Python Dependencies
- Required modules importable
- Python version compatible (3.8+)
- Script execution permissions

### 3. Data Integrity
- Lists directory accessible
- Knowledge base readable
- No corrupted JSONL files

### 4. Git Status
- Git repository initialized
- No catastrophic uncommitted changes
- .gitignore protecting sensitive data

---

## Exit Codes

- `0` - System healthy
- `1` - Issues found (non-critical)
- `2` - Critical failures

---

## Example Output

```
N5 SYSTEM HEALTH CHECK
======================

✓ Core structure: OK
✓ Python environment: OK (3.12.1)
✓ Scripts: 24/24 present
✓ Commands: 35/35 documented
✓ Data integrity: OK
⚠ Git: 3 uncommitted changes

RESULT: HEALTHY (1 warning)
Recommendation: Commit recent changes
```

---

## When to Use

- After fresh installation
- When troubleshooting issues
- Before major changes
- After pulling updates

---

**Script**: `N5/scripts/n5_system_health.py`  
**Category**: system  
**Priority**: high

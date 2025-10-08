# Phase 6: Final Validation Plan

**Date**: 2025-10-08  
**Purpose**: Comprehensive validation before declaring refactor complete  
**Duration Estimate**: 1-2 hours

---

## Validation Categories

### 1. Critical Systems Validation
- n5_safety.py imports and functions
- Path references all resolve correctly
- Commands.jsonl loads and validates
- Incantum triggers load
- Schemas validate

### 2. Command Registry Validation
- All 36 commands have valid function files
- All function files reference existing scripts (if applicable)
- No broken paths in function files
- Commands.jsonl structure is valid

### 3. File Structure Validation
- Knowledge/ accessible and portable
- Lists/ accessible and portable
- Records/ structure correct
- No loose files in wrong places
- Folder permissions correct

### 4. Smoke Tests (5 Key Workflows)
1. List operations (lists-add, lists-find)
2. Knowledge operations (knowledge-add)
3. Documentation generation (docgen)
4. System audit (core-audit)
5. Health checks (lists-health-check)

### 5. Integration Validation
- Git repository healthy
- Backups accessible
- No broken symlinks
- File count matches expectations

### 6. Health Score Assessment
- Calculate final health score
- Compare to targets
- Document improvements

---

## Validation Tests

### Test 1: Critical Systems ✓
**Purpose**: Ensure core infrastructure works

```python
# Test n5_safety.py
import sys
sys.path.insert(0, '/home/workspace')
from N5.scripts.n5_safety import execute_with_safety
print("✓ n5_safety.py imports successfully")

# Test command registry loads
import json
with open('/home/workspace/N5/config/commands.jsonl') as f:
    commands = [json.loads(line) for line in f]
print(f"✓ Loaded {len(commands)} commands")

# Test incantum triggers load
with open('/home/workspace/N5/config/incantum_triggers.json') as f:
    triggers = json.load(f)
print(f"✓ Loaded {len(triggers)} triggers")
```

### Test 2: Path Resolution ✓
**Purpose**: Verify all critical paths resolve

```bash
# Check Knowledge/ accessible
test -d /home/workspace/Knowledge && echo "✓ Knowledge/ exists"
test -f /home/workspace/Knowledge/architectural_principles.md && echo "✓ architectural_principles.md accessible"

# Check Lists/ accessible
test -d /home/workspace/Lists && echo "✓ Lists/ exists"
test -f /home/workspace/Lists/index.jsonl && echo "✓ Lists index accessible"

# Check Records/ structure
test -d /home/workspace/Records/Company/meetings && echo "✓ Records/Company/meetings exists"
test -d /home/workspace/Records/Personal && echo "✓ Records/Personal exists"

# Check N5/ structure
test -f /home/workspace/N5/config/commands.jsonl && echo "✓ commands.jsonl exists"
test -f /home/workspace/N5/prefs/prefs.md && echo "✓ prefs.md accessible"
```

### Test 3: Command Validation ✓
**Purpose**: Verify all commands have valid references

```python
import json
from pathlib import Path

workspace = Path("/home/workspace")
errors = []

# Load commands
with open(workspace / "N5/config/commands.jsonl") as f:
    commands = [json.loads(line) for line in f]

# Validate each command
for cmd in commands:
    # Check function file exists
    func_file = workspace / "N5" / cmd["function_file"]
    if not func_file.exists():
        errors.append(f"Missing function file: {cmd['function_file']}")
    
    # If has script, check script exists
    if cmd.get("script"):
        script_file = workspace / "N5" / cmd["script"]
        if not script_file.exists():
            errors.append(f"Missing script: {cmd['script']}")

if errors:
    print("✗ Validation errors:")
    for err in errors:
        print(f"  - {err}")
else:
    print(f"✓ All {len(commands)} commands validated successfully")
```

### Test 4: File Count Validation ✓
**Purpose**: Verify file counts match expectations

```bash
echo "=== File Count Validation ==="
echo "N5/: $(find /home/workspace/N5 -type f | wc -l) files (expected: ~414)"
echo "Knowledge/: $(find /home/workspace/Knowledge -type f | wc -l) files (expected: 40)"
echo "Lists/: $(find /home/workspace/Lists -type f | wc -l) files (expected: 33)"
echo "Root folders: $(ls -1d /home/workspace/*/ | wc -l) (expected: 11)"
echo "N5 subdirs: $(ls -1d /home/workspace/N5/*/ | wc -l) (expected: 10)"
```

### Test 5: Smoke Test - Lists Operations ✓
**Purpose**: Test core list functionality

```python
# Test 1: Add item to test list
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import uuid

sys.path.insert(0, '/home/workspace')

# Create test item
test_item = {
    "id": str(uuid.uuid4()),
    "created_at": datetime.now(timezone.utc).isoformat(),
    "title": "Validation Test Item",
    "status": "open",
    "tags": ["test", "validation"],
    "body": "This is a test item for Phase 6 validation"
}

# Write to test list
test_list = Path("/home/workspace/Lists/phase3-test.jsonl")
if test_list.exists():
    with open(test_list, 'a') as f:
        f.write(json.dumps(test_item) + '\n')
    print("✓ Successfully added test item to list")
else:
    print("✗ Test list not found")
```

### Test 6: Git Repository Health ✓
**Purpose**: Verify git repository is healthy

```bash
cd /home/workspace
echo "=== Git Repository Health ==="
echo "Current branch: $(git branch --show-current)"
echo "Total commits: $(git log --oneline | wc -l)"
echo "Phase 4 tags: $(git tag | grep phase4 | wc -l)"
echo "Uncommitted changes: $(git status --short | wc -l)"
echo "Repository size: $(du -sh .git | cut -f1)"
```

---

## Success Criteria

### Must Pass (Blockers)
- [ ] All critical systems import without errors
- [ ] All 36 commands have valid function files
- [ ] All paths resolve correctly (Knowledge/, Lists/, Records/)
- [ ] File counts within 5% of expected
- [ ] Git repository healthy

### Should Pass (Warnings)
- [ ] All command scripts exist (if referenced)
- [ ] No broken symlinks
- [ ] No loose files in wrong locations
- [ ] Folder permissions correct

### Nice to Have
- [ ] Health score ≥ 82/100
- [ ] All smoke tests pass
- [ ] Documentation complete

---

## Execution Checklist

1. [ ] Run Test 1: Critical Systems
2. [ ] Run Test 2: Path Resolution
3. [ ] Run Test 3: Command Validation
4. [ ] Run Test 4: File Count Validation
5. [ ] Run Test 5: Smoke Test - Lists
6. [ ] Run Test 6: Git Health
7. [ ] Calculate health score
8. [ ] Document results
9. [ ] Generate completion report

---

*Validation plan ready for execution*

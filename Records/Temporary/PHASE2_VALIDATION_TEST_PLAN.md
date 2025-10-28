# Phase 2 Validation & Integration Test Plan

**Phase**: 2 (Command System)  
**Date**: 2025-10-28  
**Purpose**: Comprehensive validation of Phase 2 + integration with Phase 0 & 1

---

## Test Objectives

1. **Phase 2 Components Work** - All new Phase 2 functionality operational
2. **Backward Compatible** - Phase 0 & 1 still work perfectly
3. **Forward Integration** - Phase 2 enhances earlier phases
4. **Production Ready** - Safe for real use

---

## Section 1: Phase 2 Component Tests

### 1.1: Commands Registry

**Test**: Create, read, update, delete commands

```bash
cd /home/workspace/N5

# Test 1: Add command
python3 scripts/command_manager.py add \
  --name "Daily Summary" \
  --trigger "daily" \
  --instruction "Generate summary of today's work" \
  --tags "productivity,reporting"

# Test 2: List commands
python3 scripts/command_manager.py list

# Test 3: Get specific command
python3 scripts/command_manager.py get --id <command_id>

# Test 4: Update command
python3 scripts/command_manager.py update \
  --id <command_id> \
  --instruction "Updated instruction"

# Test 5: Disable/enable command
python3 scripts/command_manager.py disable --id <command_id>
python3 scripts/command_manager.py enable --id <command_id>

# Test 6: Delete command
python3 scripts/command_manager.py delete --id <command_id>
```

**Expected**:
- ✅ All operations succeed with exit code 0
- ✅ JSONL file updates correctly
- ✅ No data corruption
- ✅ Proper logging to stdout

---

### 1.2: Schema Validation

**Test**: Validate commands against JSON Schema

```bash
# Test 1: Valid command passes
python3 scripts/validate_command.py --file N5/config/commands.jsonl

# Test 2: Invalid command fails appropriately
# (Create test file with invalid schema)
cat > /tmp/invalid_command.jsonl << 'EOF'
{"id": "test", "name": "Missing Required Fields"}
EOF

python3 scripts/validate_command.py --file /tmp/invalid_command.jsonl
# Should fail with clear error message
```

**Expected**:
- ✅ Valid data passes validation
- ✅ Invalid data rejected with helpful errors
- ✅ Schema documented in N5/schemas/command.schema.json
- ✅ Schema matches actual usage

---

### 1.3: Incantum Triggers (Slash Commands)

**Test**: Slash command system works

```bash
# Test 1: Check triggers file exists
test -f N5/config/incantum_triggers.json && echo "✓ Triggers file exists"

# Test 2: Validate JSON format
python3 -c "import json; json.load(open('N5/config/incantum_triggers.json'))" && echo "✓ Valid JSON"

# Test 3: Verify trigger structure
python3 << 'EOF'
import json
triggers = json.load(open('N5/config/incantum_triggers.json'))
assert isinstance(triggers, dict), "Should be dictionary"
for key, value in triggers.items():
    assert 'command_id' in value, f"Missing command_id in {key}"
    assert 'description' in value, f"Missing description in {key}"
print("✓ Trigger structure valid")
EOF
```

**Expected**:
- ✅ Triggers file well-formed
- ✅ Maps slash commands to command IDs
- ✅ Includes descriptions
- ✅ Format matches spec

---

### 1.4: Example Commands

**Test**: Example commands are useful and work

```bash
# Test 1: Count example commands
EXAMPLE_COUNT=$(python3 scripts/command_manager.py list | grep -c "enabled")
echo "Example commands: $EXAMPLE_COUNT"
test $EXAMPLE_COUNT -ge 3 && echo "✓ At least 3 examples"

# Test 2: Verify examples cover common use cases
python3 scripts/command_manager.py list | grep -i "daily\|health\|summary\|planning"
```

**Expected**:
- ✅ 3-5 example commands
- ✅ Cover different use cases
- ✅ Well-documented
- ✅ Actually useful

---

## Section 2: Integration Tests

### 2.1: Phase 2 + Phase 1 (Infrastructure)

**Test**: Commands integrate with Session State, Bulletins, Registry

```bash
# Test 1: Command creation triggers bulletin
BEFORE=$(wc -l < N5/data/system_bulletins.jsonl)
python3 scripts/command_manager.py add --name "Test Integration" --trigger "test" --instruction "Test"
AFTER=$(wc -l < N5/data/system_bulletins.jsonl)
test $AFTER -gt $BEFORE && echo "✓ Bulletin created"

# Test 2: Session state can reference commands
grep -i "command" /home/.z/workspaces/con_*/SESSION_STATE.md && echo "✓ Commands mentioned in session state"

# Test 3: Conversation registry tracks command usage
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('N5/data/conversations.db')
cursor = conn.execute("SELECT * FROM conversations WHERE focus LIKE '%command%'")
results = cursor.fetchall()
print(f"✓ Found {len(results)} conversations involving commands")
EOF
```

**Expected**:
- ✅ Commands trigger bulletins
- ✅ Session state aware of commands
- ✅ Registry tracks command conversations
- ✅ Clean integration, no conflicts

---

### 2.2: Phase 2 + Phase 0 (Foundation)

**Test**: Commands work with rules and config templates

```bash
# Test 1: Commands respect safety rules
python3 scripts/command_manager.py add \
  --name "Dangerous Test" \
  --trigger "danger" \
  --instruction "Delete everything" \
  --dry-run
# Should trigger safety warnings

# Test 2: Commands use config template system
test -f N5/templates/commands.jsonl && echo "✓ Template exists"
test -f N5/config/commands.jsonl && echo "✓ User config exists"

# Test 3: Git ignores user config, tracks templates
git check-ignore N5/config/commands.jsonl && echo "✓ Config ignored"
git ls-files N5/templates/commands.jsonl && echo "✓ Template tracked"
```

**Expected**:
- ✅ Commands respect safety system
- ✅ Template/config separation working
- ✅ Git configuration correct
- ✅ No conflicts with Phase 0 rules

---

### 2.3: Full System Integration

**Test**: All phases work together harmoniously

```bash
# Test 1: Create command that uses all phases
python3 scripts/command_manager.py add \
  --name "System Status" \
  --trigger "status" \
  --instruction "Check session state, list recent bulletins, show conversation count, verify rules loaded"

# Test 2: Verify all component files exist
for file in \
  N5/config/rules.md \
  N5/config/commands.jsonl \
  N5/data/conversations.db \
  N5/data/system_bulletins.jsonl \
  N5/scripts/session_state_manager.py \
  N5/scripts/command_manager.py \
  N5/schemas/command.schema.json
do
  test -f $file && echo "✓ $file" || echo "✗ MISSING: $file"
done

# Test 3: Run full system health check
python3 << 'EOF'
import json, sqlite3, os
from pathlib import Path

errors = []

# Check Phase 0
if not Path('N5/config/rules.md').exists():
    errors.append("Phase 0: Missing rules.md")

# Check Phase 1
try:
    conn = sqlite3.connect('N5/data/conversations.db')
    conn.execute("SELECT COUNT(*) FROM conversations").fetchone()
except Exception as e:
    errors.append(f"Phase 1: Registry error: {e}")

if not Path('N5/data/system_bulletins.jsonl').exists():
    errors.append("Phase 1: Missing bulletins")

# Check Phase 2
try:
    with open('N5/config/commands.jsonl') as f:
        for line in f:
            json.loads(line)  # Validate each command
except Exception as e:
    errors.append(f"Phase 2: Commands file error: {e}")

if not Path('N5/schemas/command.schema.json').exists():
    errors.append("Phase 2: Missing command schema")

if errors:
    print("✗ FAILURES:")
    for e in errors:
        print(f"  - {e}")
    exit(1)
else:
    print("✓ All phases integrated successfully")
EOF
```

**Expected**:
- ✅ All component files present
- ✅ No conflicts between phases
- ✅ System functions as one cohesive unit
- ✅ Health check passes

---

## Section 3: Regression Tests

### 3.1: Phase 0 Still Works

```bash
# Test: Rules still load correctly
grep -q "MANDATORY" N5/config/rules.md && echo "✓ Phase 0 rules intact"

# Test: Templates still work
python3 N5/scripts/n5_init.py --check
```

**Expected**:
- ✅ Phase 0 unaffected by Phase 2
- ✅ All Phase 0 functionality preserved

---

### 3.2: Phase 1 Still Works

```bash
# Test: Session state manager works
python3 N5/scripts/session_state_manager.py init --convo-id test_regression --type build --dry-run

# Test: Bulletins work
python3 N5/scripts/system_bulletins.py add \
  --severity info \
  --message "Regression test" \
  --component "test" \
  --dry-run

# Test: Registry works
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('N5/data/conversations.db')
count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
print(f"✓ Registry has {count} conversations")
EOF
```

**Expected**:
- ✅ All Phase 1 components work
- ✅ No regressions from Phase 2

---

## Section 4: Production Readiness

### 4.1: Test Suite

```bash
# Run all Phase 2 tests
cd /home/workspace
pytest N5/tests/test_command_*.py -v

# Expected: 70+ tests passing
# Cumulative: 175+ tests (105 from Phase 1 + 70+ from Phase 2)
```

**Expected**:
- ✅ All tests pass
- ✅ 70+ new tests
- ✅ 175+ cumulative
- ✅ No flaky tests

---

### 4.2: Documentation

```bash
# Test 1: README updated
grep -i "phase 2\|command" /home/workspace/README.md

# Test 2: CHANGELOG updated
test -f CHANGELOG.md && grep -i "phase 2\|command\|v0.3" CHANGELOG.md

# Test 3: Component docs exist
test -f N5/docs/COMMANDS.md || test -f Documents/System/COMMANDS.md
```

**Expected**:
- ✅ README mentions Phase 2
- ✅ CHANGELOG has v0.3 entry
- ✅ Command system documented
- ✅ Examples included

---

### 4.3: Git Quality

```bash
# Test 1: Clean history
git log --oneline -20 | head -10

# Test 2: Tagged correctly
git tag | grep -E "v0.3|phase2"

# Test 3: No uncommitted changes
git status --porcelain | wc -l
```

**Expected**:
- ✅ Logical commits
- ✅ Tagged v0.3-phase2
- ✅ Clean working tree
- ✅ Pushed to GitHub

---

## Section 5: User Experience Tests

### 5.1: Command Creation Flow

**Manual Test**: Create a real command

```bash
# As a user, I want to create a command for daily planning
python3 N5/scripts/command_manager.py add \
  --name "Daily Planning" \
  --trigger "plan" \
  --instruction "Review today's calendar, yesterday's progress, create today's priority list" \
  --tags "productivity,planning"
```

**Evaluation**:
- Is the CLI intuitive?
- Are error messages helpful?
- Does it do what I expect?
- Would I use this?

---

### 5.2: Command Discovery

**Manual Test**: Find and understand commands

```bash
# As a user, I want to see what commands are available
python3 N5/scripts/command_manager.py list

# I want to understand a specific command
python3 N5/scripts/command_manager.py get --id daily-planning
```

**Evaluation**:
- Can I find commands easily?
- Are descriptions clear?
- Is the output readable?

---

### 5.3: Command Invocation

**Manual Test**: Actually use a command

```
# In Zo chat, type:
/plan

# Or:
Run the Daily Planning command
```

**Evaluation**:
- Does the command trigger correctly?
- Does it execute as expected?
- Is the output useful?

---

## Completion Criteria

Phase 2 is validated and production-ready when:

- [ ] **All Component Tests Pass** (Section 1)
- [ ] **All Integration Tests Pass** (Section 2)
- [ ] **No Regressions** (Section 3)
- [ ] **Production Ready** (Section 4)
- [ ] **UX Acceptable** (Section 5)
- [ ] **175+ Total Tests Passing**
- [ ] **Documentation Complete**
- [ ] **Git Tagged & Pushed**

---

## Test Report Template

```markdown
# Phase 2 Validation Report

**Date**: YYYY-MM-DD  
**Tester**: <name>  
**Environment**: vademonstrator.zo.computer  
**Status**: PASS/FAIL

## Summary
- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X

## Section Results
1. Component Tests: PASS/FAIL
2. Integration Tests: PASS/FAIL
3. Regression Tests: PASS/FAIL
4. Production Readiness: PASS/FAIL
5. User Experience: PASS/FAIL

## Failures
<List any failures with details>

## Blockers
<List anything preventing production use>

## Recommendations
<Any suggested improvements>

## Conclusion
Phase 2 is/is not production ready.
```

---

**This plan ensures Phase 2 is truly complete, not just "tests passing."**

*Created: 2025-10-28 02:53 ET*  
*For: Demonstrator Validation Worker*

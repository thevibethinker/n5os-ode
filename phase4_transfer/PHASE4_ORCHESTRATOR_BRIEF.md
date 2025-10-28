# N5 OS Core - Phase 4 Orchestrator Brief
**For Demonstrator Account Execution**

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Orchestrator**: Vibe Builder (or equivalent)  
**Est. Time**: 10-13 hours  
**Status**: Ready to Execute  
**Depends On**: Phase 0, 1, 2, 3 Complete ✅

---

## Mission

Build Phase 4 (Knowledge & Preferences) of N5 OS Core on the Demonstrator account. This creates customizable, principled system operation with user control.

**Output**: Users can configure system behavior, architectural principles guide decisions, knowledge is portable and well-managed.

---

## Pre-Flight Checklist

### Required Before Starting

```bash
# 1. Verify Phase 0-3 complete
cd /home/workspace
pytest N5/tests/ -v | grep "passed"
# Should see 245+ tests passing

# 2. Check git status
git status
# Should be clean or only expected files

# 3. Verify core components exist
test -f N5/config/rules.md && echo "✓ Phase 0"
test -f N5/scripts/session_state_manager.py && echo "✓ Phase 1"
test -f N5/config/commands.jsonl && echo "✓ Phase 2"
test -f N5/scripts/build_orchestrator.py && echo "✓ Phase 3"

# 4. Create branch
git checkout -b phase4-knowledge-prefs
```

### Load These Files (MANDATORY)

- **planning_prompt.md** - Design philosophy
- **architectural_principles.md** - P0-P22 reference (will create public subset)

---

## Phase 4 Components

### Phase 4.1: Preferences System (3-4h, 15+ tests)

**Create modular preferences structure:**

```
/N5/prefs/
├── prefs.md                    # Index + loading rules
├── system/
│   ├── safety-rules.md
│   ├── file-operations.md
│   └── command-triggering.md
├── operations/
│   ├── scheduling.md
│   ├── communication.md
│   └── integrations.md
└── workflows/
    ├── conversation-end.md
    ├── knowledge-mgmt.md
    └── reflection.md
```

**Create loader script:**
```bash
/N5/scripts/prefs_loader.py
```

**Functions**:
- `load_preferences(context)` - Load based on context
- `get_preference(key, default)` - Get specific pref
- `list_available_prefs()` - List all modules

**CLI Tool**:
```bash
python3 N5/scripts/prefs_loader.py list
python3 N5/scripts/prefs_loader.py show system/safety-rules
```

**Tests**: `/N5/tests/test_prefs_loader.py` (15+ tests)

---

### Phase 4.2: Architectural Principles (2-3h, 5+ tests)

**Create public principles doc:**

```bash
/N5/docs/architectural_principles.md
```

**Include 10-12 Core Principles**:
- P1: Human-Readable Formats
- P2: Single Source of Truth
- P5: Anti-Overwrite
- P7: Dry-Run First
- P8: Minimal Context
- P11: Failure Modes
- P15: Complete Before Claiming
- P18: Verify State
- P19: Error Handling
- P20: Modular Design

**Format** (per principle):
```markdown
## PX: Principle Name

**What**: Brief description

**Why**: Rationale

**How**: Implementation guidance

**Example**:
\`\`\`python
# Good
...

# Bad
...
\`\`\`
```

**Exclude**: P0 (Rule of Two - removed), V-specific patterns

**Tests**: `/N5/tests/test_principles.py` (5+ tests)
- Validate principle structure
- Check examples are valid
- Verify no V-specific content

---

### Phase 4.3: Knowledge Management (2h, 10+ tests)

**Create knowledge patterns doc:**

```bash
/N5/docs/knowledge_management.md
```

**Document**:
1. SSOT Enforcement (how to maintain single source)
2. Portable Structures (markdown, JSONL, schemas)
3. Knowledge Flow (Records → Processing → Knowledge)
4. Migration Patterns (safe moves, references, rollback)

**Create helper scripts**:
```bash
/N5/scripts/knowledge_validator.py  # Validate SSOT
/N5/scripts/knowledge_migrator.py   # Safe migrations
```

**Tests**: `/N5/tests/test_knowledge_mgmt.py` (10+ tests)

---

### Phase 4.4: User Customization (2h, 15+ tests)

**Create user override system:**

```bash
/N5/config/user_overrides.md         # Template
/N5/scripts/user_config_loader.py    # Loader
/N5/docs/customization_guide.md      # User guide
```

**Load Order** (last wins):
1. `/N5/templates/` (defaults)
2. `/N5/config/` (system config)
3. `/N5/config/user_overrides.md` (user overrides)

**What Users Can Override**:
- Any preference module
- Command triggers
- Workflow templates
- Add safety rules (not remove)
- Add principles (not remove)

**Validation**:
```python
def validate_user_config(config_path):
    """Ensure user config doesn't break system."""
    # Check structure
    # Validate against schema
    # Test load without errors
    pass
```

**CLI Tool**:
```bash
python3 N5/scripts/user_config_loader.py override prefs/system/safety-rules key value
python3 N5/scripts/user_config_loader.py list
python3 N5/scripts/user_config_loader.py validate
```

**Tests**: `/N5/tests/test_user_config.py` (15+ tests)

---

### Phase 4.5: Integration & Testing (1-2h, 5+ tests)

**Integrate with previous phases:**

1. **Phase 0 (Rules)**: Rules reference prefs
2. **Phase 1 (Infrastructure)**: Session state uses prefs
3. **Phase 2 (Commands)**: Commands can use prefs
4. **Phase 3 (Build System)**: Orchestrator uses prefs

**Create integration tests:**
```bash
/N5/tests/test_phase4_integration.py
```

**Test scenarios**:
- Load prefs in different contexts
- Commands use preferences correctly
- Build orchestrator respects principles
- User overrides work system-wide
- No regressions in Phases 0-3

**Full test suite**:
```bash
pytest N5/tests/ -v
# Target: 295+ tests passing (245 existing + 50 Phase 4)
```

---

## Script Template (Use for All Scripts)

```python
#!/usr/bin/env python3
import argparse, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main(dry_run: bool = False) -> int:
    try:
        if not validate_inputs(): return 1
        result = do_work(dry_run=dry_run)
        if not verify_state(result): return 1
        logger.info(f"✓ Complete: {result}")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def do_work(dry_run: bool = False) -> dict:
    if dry_run: logger.info("[DRY RUN]"); return {"status": "dry-run"}
    return {"status": "complete"}

def verify_state(result: dict) -> bool:
    return True  # Verify: files exist, valid, tests pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
```

---

## Testing Requirements

**Phase 4 Tests**: 50+ new
- Preferences: 15+
- Principles: 5+
- Knowledge: 10+
- User config: 15+
- Integration: 5+

**Cumulative**: 295+ (245 existing + 50 Phase 4)

**Test Quality**:
- Unit tests (individual functions)
- Integration tests (cross-component)
- End-to-end (full workflows)
- Edge cases (errors, empty inputs, conflicts)

---

## Git Workflow

```bash
# During development
git add N5/prefs/ N5/docs/ N5/scripts/ N5/tests/
git commit -m "Phase 4.X: <component> - <description>"

# After each component
git push origin phase4-knowledge-prefs

# After Phase 4 complete
git tag v0.5-phase4
git push origin --tags
```

---

## Completion Criteria

Before claiming Phase 4 complete:

- [ ] All 4 components built
- [ ] 50+ Phase 4 tests passing
- [ ] 295+ cumulative tests passing
- [ ] All integration points verified
- [ ] Documentation complete
- [ ] CLI tools working
- [ ] User guide clear
- [ ] Git history clean, tagged
- [ ] Fresh thread test passed (verify in new conversation)
- [ ] No regressions

---

## After Completion

1. **Run full test suite**: `pytest N5/tests/ -v`
2. **Generate completion report** with:
   - Component summaries
   - Test results
   - Time taken
   - Any issues encountered
   - Learnings

3. **Report back to Main** - provide summary of Phase 4 completion

---

**Ready to build Phase 4!**

Remember: 70% Think+Plan, 20% Review, 10% Execute

Start with Phase 4.1 (Preferences System) when ready.

---

*Created: 2025-10-28 03:36 ET*  
*For: vademonstrator.zo.computer*  
*By: V + Vibe Builder (Main)*

# N5 OS Core - Phase 2 Orchestrator Brief
**For Demonstrator Account Execution**

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Orchestrator**: Vibe Builder (or equivalent)  
**Est. Time**: 7-9 hours  
**Status**: Ready to Execute  
**Depends On**: Phase 1 Complete ✅

---

## Mission

Build Phase 2 (Command System) of N5 OS Core on the Demonstrator account. This creates user-defined natural language commands with schema validation.

**Output**: Users can create, store, and invoke custom commands through natural language.

---

## Prerequisites

### Phase 1 Status

**MUST BE COMPLETE**:
- ✅ 105/105 tests passing
- ✅ All 4 components working (Session State, Registry, Bulletins, Safety)
- ✅ Git tagged (v0.2-phase1)
- ✅ GitHub pushed

**Verify before starting**:
```bash
cd /home/workspace
pytest tests/ --tb=short -q
git log --oneline -3
```

### Phase 1 Completion Report

**MUST HAVE**: Completed Phase 1 verification checklist

---

## Phase 2 Components

### 2.1: Commands Registry (2-3h)
**Files**: `incantum.py`, `commands.jsonl`, `command.schema.json`  
**Tests**: 25+  
**What**: CRUD operations + execution framework

### 2.2: Schema Validation (2-3h)
**Files**: `schema_validator.py`, `index.schema.json`, 4+ schemas  
**Tests**: 20+  
**What**: JSON Schema validation for all components

### 2.3: Incantum Triggers (1-2h)
**Files**: `incantum_triggers.json`, extend `incantum.py`  
**Tests**: 15+  
**What**: Slash command UI integration

### 2.4: Integration & Docs (1-2h)
**Files**: README updates, examples, integration tests  
**Tests**: 10+  
**What**: Tie to Phase 1, create examples, document

**Total**: 70+ tests, 7-9 hours

---

## Critical Design Decisions (Trap Doors)

### Trap Door #1: Command Storage Format

**DECIDED**: JSONL for commands  
**Reasoning**: Write-heavy use case, need structure, corruption isolation

**Alternatives considered**:
- Single JSON file (easier to corrupt)
- SQLite (overkill for this use case)
- Markdown (unstructured)

### Trap Door #2: Schema Format

**DECIDED**: JSON Schema (standard)  
**Reasoning**: Industry standard, good tooling, clear validation errors

**Alternatives considered**:
- Custom DSL (reinventing wheel)
- Python dataclasses (code-only validation)
- TypeScript types (wrong language context)

### Trap Door #3: Trigger Storage

**DECIDED**: Single JSON file (not JSONL)  
**Reasoning**: Read-heavy, small dataset, need atomicity

**Trade-off**: Less corruption-resistant, but simpler and faster for this use case

---

## Build Order

### Step 1: Setup Phase 2 Branch

```bash
cd /home/workspace
git checkout -b phase2-command-system
git branch --show-current
```

### Step 2: Build Command Registry (Phase 2.1)

**Create**:
1. `/N5/config/commands.jsonl` (empty file)
2. `/N5/schemas/command.schema.json` (JSON Schema)
3. `/N5/scripts/incantum.py` (Command CRUD + execution)
4. `/tests/test_incantum.py` (25+ tests)

**Test**:
```bash
pytest tests/test_incantum.py -v
```

**Success**: 25+ tests passing

### Step 3: Build Schema Validator (Phase 2.2)

**Create**:
1. `/N5/schemas/index.schema.json` (schema registry)
2. `/N5/schemas/session_state.schema.json`
3. `/N5/schemas/bulletin.schema.json`
4. `/N5/schemas/conversation.schema.json`
5. `/N5/scripts/schema_validator.py` (validation utility)
6. `/tests/test_schema_validator.py` (20+ tests)

**Integrate**: Update Phase 1 scripts to validate against schemas

**Test**:
```bash
pytest tests/test_schema_validator.py -v
```

**Success**: 20+ tests passing

### Step 4: Build Triggers System (Phase 2.3)

**Create**:
1. `/N5/config/incantum_triggers.json` (slash command registry)
2. Extend `/N5/scripts/incantum.py` (trigger management)
3. `/tests/test_incantum_triggers.py` (15+ tests)

**Test**:
```bash
pytest tests/test_incantum_triggers.py -v
```

**Success**: 15+ tests passing

### Step 5: Integration & Documentation (Phase 2.4)

**Tasks**:
1. Create example commands (3-5)
2. Integrate with Phase 1:
   - Add bulletin when command created/modified
   - Session state can reference command context
3. Update README with Phase 2 status
4. Write command authoring guide
5. Integration tests (10+)

**Test**:
```bash
pytest tests/ -v --tb=short
```

**Success**: 70+ tests total (Phase 1: 105 + Phase 2: 70 = 175+)

### Step 6: Git & GitHub Release

```bash
# Commit all changes
git add .
git commit -m "feat: Phase 2 - Command System complete

- Commands registry (incantum.py)
- Schema validation system
- Slash command triggers
- 70+ tests passing
- Integration with Phase 1"

# Tag release
git tag -a v0.3-phase2 -m "Phase 2: Command System

Components:
- Command registry (JSONL storage)
- Schema validation (JSON Schema)
- Incantum triggers (slash commands)
- 70+ tests (175+ total)

Time: X.X hours
Status: Production ready"

# Push
git push origin phase2-command-system
git push origin --tags

# Create PR, review, merge to main
```

---

## Script Template (Use for All Scripts)

```python
#!/usr/bin/env python3
"""
N5 OS Core - [Component Name]

Purpose: [What this does]
Phase: 2 (Command System)
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
SCHEMAS_DIR = ROOT / "schemas"

def main(dry_run: bool = False) -> int:
    """Main entry point."""
    try:
        if not validate_inputs():
            return 1
            
        result = do_work(dry_run=dry_run)
        
        if not verify_state(result):
            return 1
            
        logger.info(f"✓ Complete: {result}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def do_work(dry_run: bool = False) -> Dict:
    """Do the actual work."""
    if dry_run:
        logger.info("[DRY RUN] Would perform operation")
        return {"status": "dry-run"}
    
    # Actual work here
    return {"status": "complete"}

def validate_inputs() -> bool:
    """Validate all inputs before execution."""
    # Check paths exist, inputs valid, etc.
    return True

def verify_state(result: Dict) -> bool:
    """Verify state after execution."""
    # Check: file exists, size > 0, valid format
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="[Component description]")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
```

**Required Elements**:
- Logging with timestamps
- `--dry-run` flag (P7)
- Error handling with try/except (P19)
- State verification (P18)
- Exit codes (0 = success, 1 = failure)
- Docstrings (P21)

---

## Principles to Apply

**From Planning Prompt**:
- Think → Plan → Execute (70-20-10)
- Simple Over Easy (JSONL, JSON Schema, standard formats)
- Flow Over Pools (commands flow through execution)
- Nemawashi (alternatives considered above)

**From Architectural Principles**:
- P1 (Human-Readable): JSONL, JSON, clear logs
- P7 (Dry-Run): All scripts support `--dry-run`
- P15 (Complete Before Claiming): Test everything before saying "done"
- P18 (Verify State): Check writes actually worked
- P19 (Error Handling): Try/except with context
- P21 (Document Assumptions): Explicit in code + docs
- P22 (Language Selection): Python for this (good for data processing, LLM corpus)

---

## Testing Requirements

### Unit Tests (60+)
- Each component has comprehensive tests
- Happy path + error cases
- Validation logic
- CRUD operations

### Integration Tests (10+)
- Commands → Bulletins
- Commands → Session State
- Schema validation → All components
- Triggers → Commands

### Fresh Thread Test
After completion, in a NEW conversation:
1. Clone repo
2. Install deps: `pip install pytest jsonschema`
3. Run tests: `pytest tests/ -v`
4. Should work without any context from this thread

---

## Success Criteria

**Phase 2 Complete When**:
- [ ] 70+ tests passing (175+ total with Phase 1)
- [ ] All components working independently
- [ ] Integration with Phase 1 verified
- [ ] 3-5 example commands created
- [ ] Documentation complete
- [ ] Fresh thread test passed
- [ ] Git tagged (v0.3-phase2)
- [ ] GitHub pushed
- [ ] Completion report generated

---

## Safety Protocols

### Pre-Flight Checks
1. Phase 1 verified complete
2. Git clean working state
3. All paths valid
4. Planning prompt loaded

### During Build
1. Test after each component
2. Use `--dry-run` for destructive ops
3. Commit frequently
4. Document assumptions

### Before Claiming Complete
1. Run full test suite
2. Fresh thread test
3. Production config verified
4. No hardcoded test paths
5. Documentation reviewed

---

## When Stuck

**Protocol** (from Vibe Builder troubleshooting):
1. STOP trying to solve directly
2. Step back from current approach
3. Ask:
   - Am I missing info?
   - Wrong order?
   - Dependencies unconsidered?
   - Barking up wrong tree?
   - Relevant principles to apply?
   - Novel angles?

---

## Reporting

After each component (2.1, 2.2, 2.3, 2.4):
- Tests passing count
- Time spent
- Issues encountered
- Learnings

After Phase 2 complete:
- Generate completion report (like Phase 1)
- Document learnings for Main account
- Highlight any changes to plan

---

**You're ready to build Phase 2!**

Remember: 70% Think+Plan, 20% Review, 10% Execute

Start with Phase 2.1 (Commands Registry) when ready.

---

*Created: 2025-10-28 02:40 ET*  
*For: vademonstrator.zo.computer*  
*By: V + Vibe Builder (Main)*

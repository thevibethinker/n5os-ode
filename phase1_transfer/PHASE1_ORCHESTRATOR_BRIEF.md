# N5 OS Core - Phase 1 Orchestrator Brief
**For Demonstrator Account Execution**

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Orchestrator**: Vibe Builder (or equivalent)  
**Est. Time**: 10-11 hours  
**Status**: Ready to Execute

---

## Mission

Build Phase 1 (Core Infrastructure) of N5 OS Core on the Demonstrator account. This creates the self-tracking, self-maintaining foundation that enables higher-level N5 capabilities.

---

## Critical Context

### What You're Building
4 core infrastructure components:
1. **Session State Manager** - Conversation tracking & initialization
2. **System Bulletins** - Change log for AI transparency
3. **Conversation Registry** - SQLite metadata database
4. **Safety System** - Pre-execution validation (includes file guard with `.n5protected` markers)

### Where You're Building
- **Account**: vademonstrator.zo.computer
- **Repo**: Already cloned from https://github.com/vrijenattawar/zo-n5os-core
- **Branch**: `phase1` (create from main)
- **Working Dir**: `/home/workspace/`

### What Already Exists (Phase 0)
- ✅ Config template system (n5_init.py)
- ✅ Conditional rules (N5/config/rules.md)
- ✅ Basic folder structure (N5/scripts/, N5/data/, N5/templates/)
- ✅ .gitignore configured
- ✅ 34 tests passing
- ✅ Git workflow established

---

## MANDATORY Pre-Flight

**Before writing ANY code**:

1. ✅ Load file 'Knowledge/architectural/planning_prompt.md' (REQUIRED for system work)
2. ✅ Load file 'Knowledge/architectural/architectural_principles.md' (index only)
3. ✅ Read detailed plan: (to be provided in workspace)
4. ✅ Verify Phase 0 is complete:
   ```bash
   cd /home/workspace
   git status  # Should be clean
   ls -la N5/config/rules.md  # Should exist
   python3 N5/scripts/n5_init.py --check  # Should pass
   ```

**If Phase 0 incomplete**: STOP and report to V before proceeding.

---

## Detailed Plan Reference

**Full specifications** in: `PHASE1_DETAILED_PLAN.md` (will be in your conversation workspace)

**Quick Summary**:

### Phase 1.1: Session State Manager (2h)
- Create session_state_manager.py
- Build templates for build/research/discussion/planning types
- Integrate with conversation registry
- CLI: init, update, complete, list
- Success: Creates state file + registers in DB

### Phase 1.2: System Bulletins (1h)
- Create add_bulletin.py
- JSONL storage format
- CLI: add, list, resolve
- Templates for change/issue/resolved types
- Success: Append-only, queryable, AI-readable

### Phase 1.3: Conversation Registry (1.5h)
- Create conversations.db (SQLite)
- Build conversation_registry.py (Python API)
- Schema: id, type, status, focus, tags, timestamps
- Success: CRUD works, queries filter, thread-safe

### Phase 1.4: Safety System (2h)
- **n5_protect.py** - File guard with `.n5protected` markers
- **n5_safety.py** - Pre-execution validation
- **detection_rules.md** - Risk pattern matching
- Integration with rules template
- Success: Blocks risky ops, dry-run works, protection works

---

## Build Order (STRICT SEQUENCE)

```
1. Registry (no deps) → Build DB first
2. Bulletins (no deps) → Can run parallel with Registry  
3. Session State (needs Registry) → Build after Registry complete
4. Safety System (integrates all) → Build last
5. Integration tests → Verify components work together
6. Documentation → README, schemas, examples
7. GitHub release → Tag and push
```

---

## Technical Requirements

### All Scripts MUST Include

```python
#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False) -> int:
    try:
        # Validate inputs
        if not validate(): return 1
        
        # Do work
        if dry_run:
            logger.info("[DRY RUN] Would do X")
            return 0
        
        result = do_work()
        
        # Verify state
        if not verify(result): return 1
        
        logger.info(f"✓ Complete: {result}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
```

**Required**:
- Logging with timestamps
- `--dry-run` flag
- Error handling with try/except
- State verification
- Proper exit codes (0=success, 1=failure)
- Absolute paths only
- Type hints where applicable

---

## Testing Requirements

### Per Component
- Unit tests for all functions
- Integration tests with dependencies
- Dry-run tests
- Error path tests
- State verification tests

### Fresh Thread Test
After each phase, run this check:
> "If a new AI instance read only the docs, could they use this?"

If NO → improve docs before proceeding.

---

## Git Workflow

```bash
# Create Phase 1 branch
git checkout -b phase1

# Commit frequently
git add .
git commit -m "feat(phase1.1): session state manager"

# Push regularly
git push origin phase1

# When Phase 1 complete:
git checkout main
git merge phase1
git tag v0.2-phase1
git push origin main --tags
```

**Commit Convention**:
- `feat(component): description` - New feature
- `fix(component): description` - Bug fix
- `test(component): description` - Test additions
- `docs(component): description` - Documentation

---

## Safety Protocols

### STOP and Ask V If:
- Any component takes >3 hours (exceeds estimate significantly)
- Tests fail repeatedly (>5 attempts to fix)
- Design assumption violated
- Breaking change needed to Phase 0
- External dependency needed

### Checkpoints (Report to Main)
After each phase completion:
1. Component works (tests pass)
2. Git committed and pushed
3. Time spent vs estimate
4. Any learnings or issues
5. Ready for next phase? Y/N

---

## Principles to Apply

**ALWAYS**:
- P7 (Dry-Run): Every script supports --dry-run
- P15 (Complete Before Claiming): Test all criteria before ✅
- P18 (Verify State): Check writes succeeded
- P19 (Error Handling): Specific try/except, log context
- P21 (Document Assumptions): Explicit in code

**NEVER**:
- P16 violation (inventing API limits)
- Skip error handling
- Claim complete at <100%
- Skip state verification
- Use relative paths

---

## Success Criteria (Phase 1 Complete)

- [ ] All 4 components built and tested
- [ ] 35+ tests passing (target vs Phase 0: 34)
- [ ] Fresh thread test passed
- [ ] Git tagged and pushed
- [ ] Documentation complete
- [ ] Time logged: Planning + Execution
- [ ] Learnings documented for Main backport
- [ ] Ready for Phase 2

---

## Files You'll Create

```
N5/
├── data/
│   ├── conversations.db          # Registry database
│   └── system_bulletins.jsonl    # Bulletin storage
├── scripts/
│   ├── session_state_manager.py  # State management
│   ├── add_bulletin.py           # Bulletin operations
│   ├── conversation_registry.py  # DB operations
│   ├── n5_protect.py            # File guard (from Main)
│   ├── n5_safety.py             # Safety validation
│   └── lib/
│       └── conversation_db.py    # DB helper library
├── templates/
│   ├── session_state/
│   │   ├── build.template.md
│   │   ├── research.template.md
│   │   ├── discussion.template.md
│   │   └── planning.template.md
│   └── bulletins/
│       ├── change.template.json
│       ├── issue.template.json
│       └── resolved.template.json
├── schemas/
│   ├── conversation.schema.json
│   ├── bulletin.schema.json
│   └── safety_rules.schema.json
└── config/
    └── detection_rules.md         # Safety detection patterns
```

---

## Communication Protocol

**Format**: Use Main account conversation workspace for updates

**Update Template**:
```markdown
## Phase 1.X Update

**Component**: [name]
**Status**: [in-progress|complete|blocked]
**Time**: [actual vs estimate]
**Tests**: [X/Y passing]

**Completed**:
- Item 1
- Item 2

**Issues**:
- Issue description + resolution

**Next**: [next component]
```

---

## Final Checklist Before Starting

- [ ] Planning prompt loaded
- [ ] Detailed plan read and understood
- [ ] Phase 0 verified complete
- [ ] Git branch created
- [ ] Safety protocols understood
- [ ] Ready to build

---

**When ready, start with Phase 1.1 (Session State Manager).**

**Remember**: Think → Plan → Execute (70-20-10). Spend time planning each component before coding.

---

*Created: 2025-10-28 02:15 ET*  
*For: vademonstrator.zo.computer*  
*By: V + Vibe Builder (Main)*

# N5 OS Core - Phase 3 Orchestrator Brief
**For Demonstrator Account Execution**

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Orchestrator**: Vibe Builder (or equivalent)  
**Est. Time**: 9-12 hours (likely ~6-8h actual based on velocity)  
**Status**: Ready to Execute  
**Depends On**: Phase 0, 1, 2 Complete ✅

---

## Mission

Build Phase 3 (Build System) of N5 OS Core on the Demonstrator account. This creates the orchestration system for coordinating complex multi-phase builds with proper handoffs and phase management.

**Goal**: Users can coordinate sophisticated builds with multiple phases and clear agent handoffs.

---

## What You're Building

### Phase 3.1: Build Orchestrator Core (3-4h)
- Multi-phase build coordination
- Config-driven phase management
- Automated brief generation
- Integration with bulletins + registry

### Phase 3.2: Planning Philosophy (2-3h)
- Simplified planning prompt for public use
- Core design values (Simple Over Easy, Think→Plan→Execute, etc.)
- **NOT** the full Main planning prompt (that's proprietary)
- Safe for open-source distribution

### Phase 3.3: Handoff Protocols (2h)
- Standard patterns for phase transitions
- Context transfer between agents
- Template-driven handoff generation
- Clear next-phase objectives

### Phase 3.4: Integration & Examples (2-3h)
- Full system integration
- 3-5 working example build configs
- Complete documentation
- CLI tools

**Total Tests**: 70+ (25 + 10 + 15 + 20)  
**Cumulative**: 245+ tests (105 Phase 1 + 70 Phase 2 + 70 Phase 3)

---

## Pre-Flight Checklist

### ✅ Verify Phase 0, 1, 2 Complete

```bash
# Check Phase 1 + 2 tests
cd /home/workspace
pytest N5/tests/ -v

# Should see 175+ passing
# Phase 1: 105 tests (session state, bulletins, registry, safety)
# Phase 2: 70 tests (commands, schema, incantum, examples)
```

### ✅ Load Essential Files

**From transfer package**:
1. PHASE3_DETAILED_PLAN.md (this is your spec)
2. planning_prompt.md (MANDATORY - design philosophy)
3. architectural_principles.md (P0-P22 reference)
4. orchestrator.py (existing orchestrator from Main)

### ✅ Create Phase 3 Branch

```bash
cd /home/workspace
git checkout -b phase3-build-system
git status
```

---

## Phase 3.1: Build Orchestrator Core

**Time**: 3-4 hours  
**Tests**: 25+

### What to Build

**File**: `/N5/scripts/build_orchestrator.py`

Core orchestration engine that:
- Loads build config JSON
- Generates phase briefs from template
- Tracks current phase
- Creates handoffs between phases
- Records progress in bulletins
- Updates conversation registry

**Template**: `/N5/templates/orchestrator_brief_template.md`

Standard template for generating phase briefs with:
- Phase objectives
- Context from previous phases
- Success criteria
- File references
- Time estimates

**Schema**: `/N5/schemas/orchestrator.schema.json`

Defines valid build config structure:
- Build metadata (name, description)
- Phase definitions (id, name, objective, dependencies)
- Outputs expected per phase

**Example Config**: `/N5/config/build_configs/example_build.json`

Working 3-phase example:
1. Research & Planning
2. Implementation
3. Testing & Documentation

### CLI Interface

```bash
# Initialize new build
python3 N5/scripts/build_orchestrator.py --config myproject.json --action init

# Check current status
python3 N5/scripts/build_orchestrator.py --config myproject.json --action status

# Advance to next phase
python3 N5/scripts/build_orchestrator.py --config myproject.json --action advance

# Dry-run mode
python3 N5/scripts/build_orchestrator.py --config myproject.json --action init --dry-run
```

### Integration Points

- **Bulletins**: Log phase transitions
- **Registry**: Track orchestrator conversations
- **Session State**: Reference current phase
- **Commands**: Can trigger build actions

### Tests (25+)

```bash
# Unit tests
pytest N5/tests/test_build_orchestrator.py -v

# Test coverage:
# - Load config (valid + invalid)
# - Generate phase briefs
# - Track phase progression
# - Create handoffs
# - Record bulletins
# - Update registry
# - CLI interface
# - Dry-run mode
# - Error handling
```

---

## Phase 3.2: Planning Philosophy

**Time**: 2-3 hours  
**Tests**: 10+

### What to Build

**File**: `/N5/docs/planning_philosophy.md`

**IMPORTANT**: This is a **simplified, public version** for demonstrator users.

**Include**:
- ✅ Core design values (Simple Over Easy, Flow Over Pools, etc.)
- ✅ Think→Plan→Execute framework
- ✅ Trap doors vs trade-offs
- ✅ Nemawashi (explore alternatives)
- ✅ YAGNI (You Aren't Gonna Need It)
- ✅ Basic planning process

**EXCLUDE** (Main-only, proprietary):
- ❌ V-specific workflow patterns
- ❌ Advanced coordination techniques  
- ❌ Company-specific examples
- ❌ Personal productivity methods
- ❌ Proprietary orchestration patterns

**Tone**: Educational, practical, safe for open-source

### Reference

Use file 'planning_prompt.md' as source material, but **simplify and sanitize** for public use.

### Tests (10+)

```bash
pytest N5/tests/test_planning_docs.py -v

# Validate:
# - Core concepts documented
# - Examples work
# - No PII/proprietary content
# - Markdown formatting correct
# - Links valid
```

---

## Phase 3.3: Handoff Protocols

**Time**: 2 hours  
**Tests**: 15+

### What to Build

**File**: `/N5/docs/handoff_protocols.md`

Documents standard patterns for passing work between phases/agents.

**Template**: `/N5/templates/handoff_template.md`

Standard handoff format including:
- What was completed (objectives, artifacts, tests)
- Context for next phase (decisions, constraints, assumptions)
- Next phase objectives (mission, success criteria, time estimate)
- File references (essential reading, nice-to-have)

### Handoff Generation

Build orchestrator auto-generates handoffs when advancing phases using:
- Phase completion status
- Artifacts created
- Tests passed
- Open questions
- Next phase config

### Tests (15+)

```bash
pytest N5/tests/test_handoff_protocols.py -v

# Validate:
# - Template complete
# - Generation works
# - Context transferred
# - References valid
# - Format correct
```

---

## Phase 3.4: Integration & Examples

**Time**: 2-3 hours  
**Tests**: 20+

### Tasks

1. **Full System Integration**
   - Orchestrator uses all Phase 1 components
   - Commands can trigger builds
   - Phase transitions create bulletins
   - Registry tracks all conversations

2. **Example Build Configs** (3-5)
   - Simple single-phase
   - Three-phase pipeline
   - Multi-agent parallel
   - Dependent phases

3. **Complete Documentation**
   - Usage guide
   - Example walkthrough
   - Troubleshooting
   - Best practices

4. **Fresh Thread Test**
   - New conversation
   - Load system
   - Execute example build
   - Verify all phases work

### Tests (20+)

```bash
pytest N5/tests/test_phase3_integration.py -v

# Integration coverage:
# - Orchestrator + registry
# - Orchestrator + bulletins
# - Orchestrator + commands
# - Example builds work
# - Documentation complete
```

---

## Script Template (Use for All Components)

```python
#!/usr/bin/env python3
"""[Component Name] - [Brief description]"""

import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False) -> int:
    try:
        if dry_run:
            logger.info("[DRY RUN] Would execute...")
            return 0
        
        # Validate inputs
        if not validate():
            return 1
        
        # Execute
        result = do_work()
        
        # Verify
        if not verify_state(result):
            return 1
        
        logger.info(f"✓ Complete: {result}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def validate() -> bool:
    """Validate inputs and preconditions."""
    return True

def do_work() -> dict:
    """Execute main logic."""
    return {"status": "complete"}

def verify_state(result: dict) -> bool:
    """Verify post-execution state."""
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
```

---

## Testing Strategy

**Run Tests Continuously**:
```bash
# After each component
pytest N5/tests/test_[component].py -v

# Full suite
pytest N5/tests/ -v

# With coverage
pytest N5/tests/ --cov=N5/scripts --cov-report=term-missing
```

**Target**: 70+ Phase 3 tests, 245+ cumulative

---

## Git Workflow

```bash
# Commit after each component
git add N5/scripts/[new_file].py N5/tests/test_[new_file].py
git commit -m "feat: Add [component] for Phase 3"

# When Phase 3 complete
git add .
git commit -m "feat(phase3): Complete build system - orchestrator, planning, handoffs"

# Tag
git tag -a v0.4-phase3 -m "Phase 3: Build System (9.5h)"
git push origin phase3-build-system
git push origin --tags

# Create PR, review, merge to main
```

---

## Principles to Follow

- **P1**: Human-Readable (markdown briefs, clear docs)
- **P2**: SSOT (config defines build)
- **P5**: Anti-Overwrite (dry-run first)
- **P7**: Dry-Run (all destructive ops)
- **P15**: Complete Before Claiming (all tests pass)
- **P19**: Error Handling (try/except, verify)
- **P20**: Modular (each component independent)
- **P22**: Language Selection (Python for orchestration)

---

## Completion Criteria

### ✅ All Components Built
- [ ] Build orchestrator core
- [ ] Planning philosophy docs
- [ ] Handoff protocols
- [ ] Integration complete

### ✅ Tests Passing
- [ ] 70+ Phase 3 tests
- [ ] 245+ cumulative tests
- [ ] No regressions

### ✅ Documentation Complete
- [ ] Usage guide
- [ ] Examples work
- [ ] Troubleshooting guide

### ✅ Git Quality
- [ ] Clean commit history
- [ ] Tagged v0.4-phase3
- [ ] Pushed to GitHub

### ✅ Production Ready
- [ ] Fresh thread test passed
- [ ] No blockers
- [ ] Safe to use

---

## After Completion

**Generate Report**:
```markdown
# Phase 3 Completion Report

**Components**: [4/4]
**Tests**: [X/70] Phase 3, [Y/245] Total
**Time**: X.X hours
**Status**: Production ready

[Summary of work, learnings, issues]
```

**Report Back to Main**:
- Completion summary
- Time vs estimate
- Issues encountered
- Learnings

---

## When Blocked

1. Re-read detailed plan
2. Check architectural principles
3. Review planning prompt
4. Ask clarifying questions
5. Document assumptions (P21)

---

**You're ready to build Phase 3!**

Remember: 70% Think+Plan, 20% Review, 10% Execute

Start with Phase 3.1 (Build Orchestrator Core) when ready.

---

*Created: 2025-10-28 03:05 ET*  
*For: vademonstrator.zo.computer*  
*By: V + Vibe Builder (Main)*

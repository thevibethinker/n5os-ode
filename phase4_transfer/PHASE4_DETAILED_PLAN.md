# N5 OS Core - Phase 4 Detailed Plan
# Knowledge & Preferences

**Thread**: con_2rD2ojBNmRthdfVR  
**Date**: 2025-10-28  
**Planning Mode**: THINK → PLAN → EXECUTE  
**Status**: 📋 Planning  
**Depends On**: Phase 0, 1, 2, 3 Complete ✅

---

## THINK Phase: What Are We Building?

### Purpose
Phase 4 creates the **knowledge and preferences system** that makes N5 OS customizable and principled. This enables users to configure behavior and establishes architectural guardrails.

### Why Phase 4 Matters
- **Customization**: Users can tailor system behavior
- **Principles**: Architectural patterns guide decisions
- **Portability**: Knowledge structures are system-independent
- **Maintainability**: Clear preferences reduce ad-hoc decisions

### Core Insight
Preferences and principles should be **modular, context-aware, and user-overridable**. Not everything is relevant all the time.

---

## PLAN Phase: Component Breakdown

### Phase 4.1: Preferences System (3-4h)

**Purpose**: Modular preference loading with context-awareness

**Files to Create**:
- `/N5/prefs/prefs.md` - Main index
- `/N5/prefs/system/` - System-level preferences
- `/N5/prefs/operations/` - Operational preferences
- `/N5/prefs/workflows/` - Workflow preferences
- `/N5/scripts/prefs_loader.py` - Dynamic loader

**Structure**:
```
/N5/prefs/
├── prefs.md                    # Index with loading rules
├── system/
│   ├── safety-rules.md        # Safety protocols
│   ├── file-operations.md     # File handling rules
│   └── command-triggering.md  # Command-first protocols
├── operations/
│   ├── scheduling.md          # Task scheduling prefs
│   ├── communication.md       # Email/SMS protocols
│   └── integrations.md        # External app prefs
└── workflows/
    ├── conversation-end.md    # Convo end workflow prefs
    ├── knowledge-mgmt.md      # Knowledge handling
    └── reflection.md          # Reflection protocols
```

**Functionality**:
```python
# prefs_loader.py
from pathlib import Path
import logging

def load_preferences(context: str = "general") -> dict:
    """Load preferences based on context."""
    # Always load: prefs.md + system/
    # Context-aware: Load only relevant modules
    pass

def get_preference(key: str, default=None) -> any:
    """Get specific preference value."""
    pass

def list_available_prefs() -> list:
    """List all preference modules."""
    pass
```

**Success Criteria**:
- ✅ Modular structure (directory-based)
- ✅ Context-aware loading
- ✅ Index with clear loading rules
- ✅ Python loader with tests (15+)
- ✅ Documentation (usage examples)
- ✅ CLI tool (`n5 prefs list`, `n5 prefs show <module>`)

---

### Phase 4.2: Architectural Principles (2-3h)

**Purpose**: Curated subset of principles for public use

**File to Create**:
- `/N5/docs/architectural_principles.md` - Public version

**What to Include**:
1. **Core Principles** (universally applicable):
   - P1: Human-Readable Formats
   - P2: Single Source of Truth (SSOT)
   - P5: Anti-Overwrite (safety)
   - P7: Dry-Run First
   - P8: Minimal Context
   - P11: Failure Modes
   - P15: Complete Before Claiming
   - P18: Verify State
   - P19: Error Handling
   - P20: Modular Design

2. **Simplified Explanations**:
   - Each principle: What, Why, How, Example
   - Remove V-specific context
   - Focus on universal patterns

**What to EXCLUDE** (V-specific):
- P0: Rule of Two (removed)
- Personal workflow preferences
- Company-specific patterns
- Proprietary learnings

**Success Criteria**:
- ✅ 10-12 core principles documented
- ✅ Each has: description, rationale, example
- ✅ Clear, accessible writing
- ✅ Safe for public distribution
- ✅ Integration with scripts (validation checks)

---

### Phase 4.3: Knowledge Management Patterns (2h)

**Purpose**: Patterns for handling knowledge in N5

**File to Create**:
- `/N5/docs/knowledge_management.md`

**Patterns to Document**:

1. **SSOT Enforcement**:
   - How to maintain single source of truth
   - Migration from duplicates
   - Validation scripts

2. **Portable Structures**:
   - Markdown for docs
   - JSONL for data
   - Schema enforcement

3. **Knowledge Flow**:
   - Records → Processing → Knowledge
   - Temporary → Staging → Permanent
   - Archive patterns

4. **Migration**:
   - Safe knowledge moves
   - Maintaining references
   - Rollback strategies

**Success Criteria**:
- ✅ Clear patterns documented
- ✅ Examples for each pattern
- ✅ Integration with existing systems
- ✅ Helper scripts (knowledge validator, migrator)
- ✅ Tests (10+)

---

### Phase 4.4: User Customization Hooks (2h)

**Purpose**: Enable users to override/extend system

**Files to Create**:
- `/N5/config/user_overrides.md` - Template
- `/N5/scripts/user_config_loader.py` - Loader
- `/N5/docs/customization_guide.md` - User guide

**What Users Can Customize**:
1. Preferences (any module)
2. Command triggers
3. Workflow templates
4. Safety rules (add, not remove)
5. Architectural principles (add, not remove)

**Implementation**:
```python
# Load order (last wins):
1. /N5/templates/ (defaults)
2. /N5/config/ (system config)
3. /N5/config/user_overrides.md (user customization)
```

**Success Criteria**:
- ✅ Clear override mechanism
- ✅ User guide with examples
- ✅ Validation (user config doesn't break system)
- ✅ Tests (15+)
- ✅ CLI tool (`n5 config override <module> <key> <value>`)

---

### Phase 4.5: Integration & Testing (1-2h)

**Purpose**: Tie Phase 4 to Phases 0-3

**Integration Points**:

1. **With Phase 0 (Rules)**:
   - Rules reference prefs for behavior
   - Safety rules integrated with prefs

2. **With Phase 1 (Infrastructure)**:
   - Session state uses prefs for context
   - Bulletins track prefs changes

3. **With Phase 2 (Commands)**:
   - Commands can reference prefs
   - Prefs control command behavior

4. **With Phase 3 (Build System)**:
   - Build orchestrator uses prefs for project configs
   - Planning prompt integrated with principles

**Testing**:
```bash
# Preference loading
pytest N5/tests/test_prefs_loader.py -v

# Principle validation
pytest N5/tests/test_principles.py -v

# Knowledge patterns
pytest N5/tests/test_knowledge_mgmt.py -v

# User customization
pytest N5/tests/test_user_config.py -v

# Integration
pytest N5/tests/test_phase4_integration.py -v
```

**Success Criteria**:
- ✅ 50+ Phase 4 tests passing
- ✅ 295+ cumulative tests passing
- ✅ All integration points work
- ✅ No regressions
- ✅ Fresh thread test passed

---

## Time Estimates

| Component | Time | Tests |
|-----------|------|-------|
| 4.1: Preferences System | 3-4h | 15+ |
| 4.2: Architectural Principles | 2-3h | 5+ |
| 4.3: Knowledge Patterns | 2h | 10+ |
| 4.4: User Customization | 2h | 15+ |
| 4.5: Integration & Testing | 1-2h | 5+ |
| **Total** | **10-13h** | **50+** |

**Target**: 10-13 hours (likely ~6-9h actual based on velocity)

---

## Trap Doors (Irreversible Decisions)

1. **Preference Structure**: Directory vs single file
   - **Choice**: Directory (modular, scalable)
   - **Why**: Easier to extend, context-aware loading

2. **Principles Inclusion**: Which ones are public?
   - **Choice**: Core 10-12 only, exclude V-specific
   - **Why**: Safe for open-source, universally valuable

3. **User Override Mechanism**: Full vs partial
   - **Choice**: Layered (defaults → config → user)
   - **Why**: Flexibility + safety

---

## Success Criteria

- [ ] Preferences system functional (modular, context-aware)
- [ ] Architectural principles documented (10-12 core)
- [ ] Knowledge patterns documented (SSOT, portable, flow)
- [ ] User customization working (safe overrides)
- [ ] 50+ Phase 4 tests passing
- [ ] 295+ cumulative tests passing
- [ ] Integration complete (all phases work together)
- [ ] Git tagged v0.5-phase4
- [ ] Fresh thread test passed
- [ ] Production ready

---

## Next Actions

1. **Review this plan** - Get approval, clarify ambiguities
2. **Create orchestrator brief** - Instructions for Demonstrator execution
3. **Transfer to Demonstrator** - Begin Phase 4 implementation
4. **Build & test** - Execute plan
5. **Document learnings** - Update Main with insights

---

*Created: 2025-10-28 03:33 ET*  
*Planning Prompt: Loaded*  
*Status: Ready for Review*

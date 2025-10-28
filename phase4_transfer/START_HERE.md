# START HERE - Phase 4 Execution on Demonstrator

**Account**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Status**: Ready to Execute  
**Depends On**: Phase 0, 1, 2, 3 Complete ✅

---

## ⚠️ You ARE on Demonstrator

You're executing Phase 4 BUILD on **vademonstrator.zo.computer**.

---

## Quick Overview

**Phase 4**: Knowledge & Preferences  
**Components**: 5 (Prefs, Principles, Knowledge, User Config, Integration)  
**Time**: 10-13h (~6-9h likely based on velocity)  
**Tests**: 50+ new (295+ cumulative)

---

## Pre-Flight

### 1. Verify Phase 0-3 Complete

```bash
pytest N5/tests/ -v | tail -1
# Should show 245+ tests passing
```

### 2. Create Branch

```bash
git checkout -b phase4-knowledge-prefs
```

### 3. Load Knowledge Base (MANDATORY)

- **planning_prompt.md** - Design philosophy
- **architectural_principles.md** - Reference for public subset

---

## Execution Order

### Step 1: Read Documentation

1. **START_HERE.md** (this file)
2. **PHASE4_ORCHESTRATOR_BRIEF.md** - Full guide
3. **PHASE4_DETAILED_PLAN.md** - Technical specs

### Step 2: Build Components (In Order)

**4.1: Preferences System** (3-4h, 15+ tests)
- Create `/N5/prefs/` structure
- Build `prefs_loader.py`
- CLI tool

**4.2: Architectural Principles** (2-3h, 5+ tests)
- Create `/N5/docs/architectural_principles.md`
- Public subset (10-12 core principles)
- Exclude V-specific

**4.3: Knowledge Management** (2h, 10+ tests)
- Create `/N5/docs/knowledge_management.md`
- Document patterns (SSOT, portable, flow)
- Helper scripts

**4.4: User Customization** (2h, 15+ tests)
- Create `/N5/config/user_overrides.md`
- Build `user_config_loader.py`
- Validation + CLI

**4.5: Integration** (1-2h, 5+ tests)
- Integrate with Phases 0-3
- Full test suite
- Fresh thread test

---

## Success Criteria

- [ ] 50+ Phase 4 tests passing
- [ ] 295+ cumulative tests passing
- [ ] All integration points work
- [ ] Documentation complete
- [ ] Git tagged v0.5-phase4
- [ ] Production ready

---

## Important Notes

1. **Principles Curation**: Include 10-12 core only, exclude V-specific
2. **Modular Prefs**: Directory structure, context-aware loading
3. **User Safety**: Validate user overrides don't break system
4. **Integration**: All phases must work together

---

**Ready to build Phase 4!**

Start with PHASE4_ORCHESTRATOR_BRIEF.md → then Phase 4.1

---

*Prepared: 2025-10-28 03:38 ET*  
*From: Main (va.zo.computer)*  
*For: Demonstrator (vademonstrator.zo.computer)*

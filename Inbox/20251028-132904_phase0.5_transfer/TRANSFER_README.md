# Phase 0.5 Transfer Package

**Package**: N5 OS Core - Phase 0.5 (Onboarding System)  
**Version**: 0.5.0  
**Created**: 2025-10-28  
**For**: vademonstrator.zo.computer

---

## What's in This Package

Complete onboarding system for N5 OS Core.

**Configures N5-specific systems after user completes manual prerequisites.**

NOT basic info collection - that's done manually first.

---

## How to Use This Package

###  1. Start Here

Read `START_HERE.md` - Quick start guide (15 min read)

### 2. Read Build Instructions

Read `PHASE0.5_ORCHESTRATOR_BRIEF.md` - Complete build instructions

### 3. Install & Test

Follow step-by-step instructions in START_HERE.md:
- Install scripts (15 min)
- Install templates (5 min)
- Install recipe (5 min)
- Test (2-3 hours)
- Fresh account test (2-3 hours)
- Commit (30 min)

**Total time**: 8-10 hours

---

## Package Structure

```
phase0.5_transfer/
├── START_HERE.md                      # Begin here
├── PHASE0.5_ORCHESTRATOR_BRIEF.md     # Build instructions
├── PHASE0.5_DETAILED_PLAN.md          # Implementation plan
├── MANIFEST.md                        # File list
├── TRANSFER_README.md                 # This file
├── planning_prompt.md                 # Design philosophy
├── architectural_principles.md        # System principles
├── N5.md                              # N5 reference
├── scripts/
│   ├── n5_onboard.py                  # Main orchestrator
│   ├── prerequisite_checker.py        # Validate manual setup
│   ├── config_generator.py            # Create user_config/
│   ├── setup_validator.py             # 12 validation tests
│   └── welcome_guide_generator.py     # Generate docs
├── templates/
│   ├── preferences.json.j2            # Config template
│   ├── telemetry_settings.json.j2     # Telemetry template
│   ├── welcome_guide.md.j2            # Welcome template
│   └── user_config_readme.md.j2       # README template
├── tests/
│   ├── test_prerequisites.py          # 4 tests
│   ├── test_config_generation.py      # 4 tests
│   └── test_integration.py            # 4 tests
└── docs/
    ├── ONBOARDING_SPEC.md             # Technical spec
    └── onboard_recipe.md              # Recipe file
```

---

## Quick Install

```bash
# 1. Copy scripts
cp phase0.5_transfer/scripts/*.py n5os-core/N5/scripts/
chmod +x n5os-core/N5/scripts/n5_onboard.py

# 2. Copy templates
mkdir -p n5os-core/N5/templates
cp phase0.5_transfer/templates/*.j2 n5os-core/N5/templates/

# 3. Copy recipe
cp phase0.5_transfer/docs/onboard_recipe.md n5os-core/Recipes/onboard.md

# 4. Test
python3 n5os-core/N5/scripts/n5_onboard.py --dry-run
```

---

## What This Builds

**Onboarding system that**:

1. Verifies manual prerequisites complete
2. Runs interactive 6-question interview
3. Configures N5 workflow systems
4. Sets automation level
5. Creates `user_config/` (gitignored)
6. Validates setup (12 tests)
7. Generates personalized welcome guide

**User journey**:
1. Clone n5os-core
2. Complete manual setup (rules, apps, bio, personas)
3. Run `/onboard` (10-15 minutes)
4. System configured and ready!

---

## Dependencies

**Requires**:
- Phase 0: Rules
- Phase 1: Infrastructure
- Phase 2: Recipes
- Phase 3: Build system
- Phase 4: Preferences
- Phase 5: Workflows

All phases must be complete on Demonstrator.

**No additional Python packages needed** (uses stdlib only).

---

## Testing

**Run tests**:
```bash
cd phase0.5_transfer/tests
python3 -m pytest test_prerequisites.py -v
python3 -m pytest test_config_generation.py -v
python3 -m pytest test_integration.py -v
```

All 12 tests must pass.

**Fresh account test required** - Do NOT test only on Demonstrator.

---

## Success Criteria

Phase 0.5 complete when:

- ✅ All 5 scripts installed
- ✅ All 4 templates installed
- ✅ Recipe registered
- ✅ 12 tests passing
- ✅ Fresh account test passes
- ✅ Committed to n5os-core main
- ✅ PHASE0.5_COMPLETE.md written

---

## Support

**Questions?**
- Check `PHASE0.5_DETAILED_PLAN.md`
- Check `docs/ONBOARDING_SPEC.md`
- Review Phase 1-5 transfer packages for patterns

**Issues?**
- Document in build thread
- Escalate to V

---

## Key Files

**Must Read**:
1. `START_HERE.md` - Begin here
2. `PHASE0.5_ORCHESTRATOR_BRIEF.md` - Build instructions
3. `docs/ONBOARDING_SPEC.md` - Technical spec

**Reference**:
- `MANIFEST.md` - Complete file list
- `planning_prompt.md` - Design philosophy
- `architectural_principles.md` - System principles

---

**Ready to build? Start with START_HERE.md**

*N5 OS Core - Phase 0.5 Transfer Package*  
*Created: 2025-10-28*  
*For: vademonstrator.zo.computer*

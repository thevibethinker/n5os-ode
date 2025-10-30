# N5 OS Core - Phase 0.5 Orchestrator Brief
**For Demonstrator Account Execution**

**Date**: 2025-10-28  
**Account**: vademonstrator.zo.computer  
**Build Location**: `/home/workspace/n5os-core`

---

## Mission

**Build Phase 0.5 (Onboarding System) of N5 OS Core on the Demonstrator account.**

This creates the first-run onboarding experience for new users who clone n5os-core to their own Zo accounts.

---

## What Phase 0.5 Does

**Configures N5 OS Core system AFTER user completes manual prerequisites.**

NOT basic info collection. This is **N5-specific system configuration only.**

### User Journey

**Before Onboarding (User Does Manually)**:
1. Clone n5os-core to their Zo
2. Add rules in Zo settings
3. Connect apps (Gmail, Drive, Notion, Calendar)
4. Add bio in Zo settings
5. Add personas (Vibe Builder Bootstrap, Vibe Debugger Bootstrap)

**During Onboarding (This System)**:
6. Verify prerequisites complete
7. Configure N5 workflows (Lists, Meetings, Digests, Social, CRM)
8. Set automation level (Manual/Semi-Auto/Auto)
9. Setup scheduled tasks
10. Generate `user_config/` (personalized, gitignored)
11. Validate everything works
12. Generate welcome guide

**Result**: Fully configured N5 OS Core, personalized to user

---

## Dependencies

**Phase 0.5 Requires:**
- ✅ Phase 0: Rules system
- ✅ Phase 1: Infrastructure (directories, git)
- ✅ Phase 2: Commands → Recipes migration
- ✅ Phase 3: Build system (session state)
- ✅ Phase 4: Preferences system
- ✅ Phase 5: Workflows

All phases must be complete and tested on Demonstrator.

---

## Package Contents

```
phase0.5_transfer/
├── PHASE0.5_ORCHESTRATOR_BRIEF.md    # This file
├── PHASE0.5_DETAILED_PLAN.md         # Implementation plan
├── START_HERE.md                      # Quick start
├── MANIFEST.md                        # File list
├── TRANSFER_README.md                # How to use
├── scripts/
│   ├── n5_onboard.py                 # Main orchestrator
│   ├── prerequisite_checker.py       # Verify manual setup
│   ├── config_generator.py           # Create user_config/
│   ├── setup_validator.py            # 12 validation tests
│   └── welcome_guide_generator.py    # Personalized docs
├── templates/
│   ├── preferences.json.j2           # Config template
│   ├── telemetry_settings.json.j2    # Telemetry template
│   ├── welcome_guide.md.j2           # Welcome guide template
│   └── user_config_readme.md.j2      # user_config/README.md
├── tests/
│   ├── test_prerequisites.py         # 4 prerequisite tests
│   ├── test_config_generation.py     # 4 config tests
│   └── test_integration.py           # 4 integration tests
└── docs/
    ├── ONBOARDING_SPEC.md            # Full specification
    └── USER_INSTRUCTIONS.md          # For end users
```

---

## Build Instructions

### Step 1: Transfer Package

Copy entire `phase0.5_transfer/` to Demonstrator workspace:
```bash
# On Demonstrator
cd /home/workspace
# Package should arrive via shared method
```

### Step 2: Review Spec

Read `PHASE0.5_DETAILED_PLAN.md` completely before starting.

Key decisions already made:
- Auto-trigger: Manual `/onboard` command
- Re-onboarding: Full reset allowed
- Prerequisites: Must be complete before onboarding
- Validation: Block on failure (strict mode)

### Step 3: Install Scripts

Copy scripts to n5os-core:
```bash
cd /home/workspace/n5os-core
cp /home/workspace/phase0.5_transfer/scripts/* N5/scripts/
chmod +x N5/scripts/n5_onboard.py
```

### Step 4: Install Templates

```bash
cp /home/workspace/phase0.5_transfer/templates/* N5/templates/
```

### Step 5: Create Recipe

```bash
cp /home/workspace/phase0.5_transfer/docs/onboard_recipe.md Recipes/onboard.md
```

### Step 6: Run Tests

```bash
cd /home/workspace/phase0.5_transfer/tests
python3 -m pytest test_prerequisites.py -v
python3 -m pytest test_config_generation.py -v
python3 -m pytest test_integration.py -v
```

All 12 tests must pass.

### Step 7: Manual QA

Run onboarding in dry-run mode:
```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py --dry-run
```

Verify:
- Prerequisites check works
- Interview questions make sense
- Config generation produces valid JSON
- Validation tests run
- Welcome guide generates

### Step 8: Live Test

**CRITICAL**: Test on a FRESH Zo account (not Demonstrator).

Set up test account:
1. Clone n5os-core
2. Complete manual prerequisites
3. Run `/onboard`
4. Verify setup completes successfully

### Step 9: Commit to n5os-core

```bash
cd /home/workspace/n5os-core
git add N5/scripts/n5_*.py
git add N5/templates/*.j2
git add Recipes/onboard.md
git add .gitignore  # Ensure user_config/ listed
git commit -m "feat: Add Phase 0.5 onboarding system

- Main orchestrator with 6-question interview
- Prerequisites validation
- user_config/ generation
- 12-test validation suite
- Welcome guide generation
- Recipe registration

Closes #XX"
git push origin main
```

### Step 10: Documentation

Update n5os-core docs:
```bash
cp /home/workspace/phase0.5_transfer/docs/USER_INSTRUCTIONS.md \
   /home/workspace/n5os-core/Documents/System/ONBOARDING_GUIDE.md
```

---

## Success Criteria

**Phase 0.5 Complete When:**

1. ✅ All 5 scripts installed and tested
2. ✅ All templates validated
3. ✅ Recipe registered and working
4. ✅ 12 validation tests passing
5. ✅ Fresh account test successful
6. ✅ Committed to n5os-core main
7. ✅ Documentation complete
8. ✅ PHASE0.5_COMPLETE.md written

---

## Time Estimate

**Total**: 8-10 hours

- Script installation: 1h
- Testing: 2-3h
- Integration fixes: 2-3h
- Fresh account test: 1-2h
- Documentation: 1h

---

## Key Principles

**From Planning Prompt:**
- Simple Over Easy (minimal concepts, maximum clarity)
- Flow Over Pools (user progresses through stages)
- Maintenance Over Organization (easy to update)

**Architectural Principles:**
- P1: Human-Readable (friendly conversation)
- P7: Dry-Run (preview before applying)
- P15: Complete Before Claiming (validate fully)
- P18: Verify State (test everything)

---

## Notes for Demonstrator AI

1. **Read planning prompt first**: `file 'phase0.5_transfer/planning_prompt.md'`
2. **Follow Think→Plan→Execute**: Already done, you're in EXECUTE phase
3. **Test thoroughly**: This is first-run experience, must be perfect
4. **Fresh account required**: Do not test only on Demonstrator
5. **Validate prerequisites logic**: Critical to check manual setup

---

## Contact

**Questions?** Check:
- `PHASE0.5_DETAILED_PLAN.md` - Complete implementation details
- `docs/ONBOARDING_SPEC.md` - Full specification
- Phase 0-5 transfer packages - Established patterns

**Issues?** Document in build thread and escalate to V.

---

**Ready to build on Demonstrator!**

*Package created: 2025-10-28 05:35 ET*  
*For: vademonstrator.zo.computer*  
*N5 OS Core - Phase 0.5: Onboarding System*

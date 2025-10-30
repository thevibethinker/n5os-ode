# Phase 0.5: Onboarding System - START HERE

**Package**: N5 OS Core - Phase 0.5  
**For**: vademonstrator.zo.computer  
**Date**: 2025-10-28  
**Est. Time**: 8-10 hours

---

## Quick Start

### 1. Read This First

**Mission**: Build onboarding system that configures N5 OS Core for new users.

**NOT**: Basic info collection (that's done manually first)  
**IS**: N5-specific system configuration only

---

### 2. Prerequisites

**Verify Phase 0-5 Complete**:
```bash
cd /home/workspace/n5os-core

# Check phases
ls -la N5/prefs/        # Phase 0 (Rules)
ls -la Lists/           # Phase 1 (Infrastructure)
ls -la Recipes/         # Phase 2 (Commands→Recipes)
ls -la N5/scripts/session_state_manager.py  # Phase 3 (Build)
cat N5/prefs/prefs.md   # Phase 4 (Preferences)
ls -la N5/scripts/n5_conversation_end.py    # Phase 5 (Workflows)
```

All must exist and be tested.

---

### 3. Read Documentation (30 min)

**Required reading order**:

1. **This file** (5 min)
2. `PHASE0.5_ORCHESTRATOR_BRIEF.md` (15 min) - Build instructions
3. `docs/ONBOARDING_SPEC.md` (10 min) - Technical spec

**Optional**:
- `PHASE0.5_DETAILED_PLAN.md` - Full implementation plan
- `MANIFEST.md` - Package contents

---

### 4. Install Scripts (15 min)

```bash
# Copy scripts
cd /home/workspace/phase0.5_transfer
cp scripts/*.py /home/workspace/n5os-core/N5/scripts/

# Make executable
chmod +x /home/workspace/n5os-core/N5/scripts/n5_onboard.py

# Verify
ls -lh /home/workspace/n5os-core/N5/scripts/n5_*.py
```

Should see:
- n5_onboard.py
- prerequisite_checker.py
- config_generator.py
- setup_validator.py
- welcome_guide_generator.py

---

### 5. Install Templates (5 min)

```bash
# Create templates directory if needed
mkdir -p /home/workspace/n5os-core/N5/templates

# Copy templates
cp templates/*.j2 /home/workspace/n5os-core/N5/templates/

# Verify
ls -la /home/workspace/n5os-core/N5/templates/
```

---

### 6. Install Recipe (5 min)

```bash
# Copy recipe
cp docs/onboard_recipe.md /home/workspace/n5os-core/Recipes/onboard.md

# Verify
cat /home/workspace/n5os-core/Recipes/onboard.md
```

---

### 7. Test Scripts (1-2 hours)

```bash
cd /home/workspace/n5os-core

# Test 1: Dry run
python3 N5/scripts/n5_onboard.py --dry-run

# Should show:
# - Prerequisites check
# - Interactive interview (answer questions)
# - Config preview (JSON output)
# - No actual changes made

# Test 2: Validation suite
cd /home/workspace/phase0.5_transfer/tests
python3 -m pytest test_prerequisites.py -v
python3 -m pytest test_config_generation.py -v
python3 -m pytest test_integration.py -v

# All 12 tests should pass
```

---

### 8. Fresh Account Test (2-3 hours)

**CRITICAL**: Must test on fresh Zo account, NOT Demonstrator.

**Setup test account**:
1. Get access to a test Zo account
2. Clone n5os-core
3. Complete manual prerequisites:
   - Add rules in Zo settings
   - Connect apps (Gmail, Drive, Notion)
   - Add bio
   - Add personas (Vibe Builder, Vibe Debugger)
4. Run onboarding:
   ```bash
   python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py
   ```
5. Verify:
   - Interview completes (6 questions)
   - `user_config/` created
   - All files valid
   - Welcome guide generated
   - System works

---

### 9. Commit to n5os-core (30 min)

```bash
cd /home/workspace/n5os-core

# Stage files
git add N5/scripts/n5_*.py
git add N5/templates/*.j2
git add Recipes/onboard.md
git add .gitignore  # Ensure user_config/ listed

# Commit
git commit -m "feat: Add Phase 0.5 onboarding system

- Interactive 6-question configuration interview
- Prerequisites validation (4 tests)
- user_config/ generation (gitignored)
- 12-test validation suite
- Personalized welcome guide

Onboarding configures N5 systems after manual setup.
User completes rules/apps/bio/personas first.
Then runs /onboard to configure workflows and automation.

Phase 0.5 complete."

# Push
git push origin main
```

---

### 10. Write Completion Report (30 min)

Create `PHASE0.5_COMPLETE.md`:

```markdown
# Phase 0.5 Complete

**Date**: [DATE]
**Time**: [HOURS]
**Account**: vademonstrator.zo.computer

## What Was Built

- 5 Python scripts (onboarding system)
- 4 Jinja2 templates
- 12 validation tests
- Recipe registration
- Documentation

## Testing Results

- ✅ Dry-run works
- ✅ 12 validation tests pass
- ✅ Fresh account test successful
- ✅ All files committed

## Fresh Account Test

**Account**: [test_account].zo.computer
**Date**: [DATE]
**Result**: ✅ Success

Interview completed in X minutes.
user_config/ generated successfully.
All validations passed.
Welcome guide created.

## Commit

**SHA**: [commit_sha]
**Message**: "feat: Add Phase 0.5 onboarding system"

## Next Phase

Phase 0.5 complete. N5 OS Core ready for end users.

Users can now:
1. Clone n5os-core
2. Complete manual setup
3. Run /onboard
4. Start using N5

---

*Phase 0.5 Orchestrator: [AI_name]*
*Build time: [X] hours*
```

---

## Quick Reference

**Key Commands**:
```bash
# Dry run
python3 N5/scripts/n5_onboard.py --dry-run

# Real run
python3 N5/scripts/n5_onboard.py

# Reset
python3 N5/scripts/n5_onboard.py --reset

# Tests
pytest tests/ -v
```

**Key Files**:
- Main: `N5/scripts/n5_onboard.py`
- Config: `user_config/preferences.json`
- Recipe: `Recipes/onboard.md`
- Welcome: `Documents/WELCOME.md`

---

## Troubleshooting

**Issue**: Prerequisites fail  
**Fix**: Ensure Phase 0-5 complete on Demonstrator

**Issue**: Templates not found  
**Fix**: Create `N5/templates/` directory first

**Issue**: Import errors  
**Fix**: Verify all 5 scripts in `N5/scripts/`

**Issue**: Tests fail  
**Fix**: Check workspace is `/home/workspace/n5os-core`

---

## Success Criteria

- ✅ All 5 scripts installed and executable
- ✅ All 4 templates installed
- ✅ Recipe registered
- ✅ 12 tests passing
- ✅ Dry-run works
- ✅ Fresh account test passes
- ✅ Committed to main
- ✅ PHASE0.5_COMPLETE.md written

---

**Ready? Go to step 4 and start building!**

*Phase 0.5 Package - v0.5.0*  
*Est. completion: 8-10 hours*

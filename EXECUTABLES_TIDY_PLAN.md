# Executables System Tidy-Up Plan

**Date:** 2025-11-01 10:19 ET
**Mode:** Vibe Debugger
**Conversation:** con_54qlgDX1jwc6jRC3

---

## Current State Diagnosis

**Database:** 142 entries (all prompts, NO scripts)
**Filesystem:** 140 prompts + 393 scripts
**Gap:** 393 scripts not registered ❌
**Docs:** 14 files reference wrong path ❌
**Rules:** No conditional rule ❌

---

## Execution Plan

### Phase 1: Register Scripts (~393)
**Problem:** 0 scripts in DB, should have ~393
**Action:** Scan N5/scripts/*.py, register each
**Trap Doors:** 
- Duplicate IDs → prefix 'script-' if conflict
- Missing docstrings → use filename
- Deprecated → skip _DEPRECATED paths

### Phase 2: Fix Documentation (14 files)
**Problem:** Docs say "Prompts/executables.db" (wrong)
**Action:** Replace with "N5/data/executables.db"
**Verify:** grep returns 0 old refs

### Phase 3: Add Conditional Rule
**Problem:** No rule to check DB first
**Action:** Add to user rules in system
**Text:** "Before system operations check executables DB"

### Phase 4: Clean Test Data
**Problem:** test/test2/update-test-001 in production
**Action:** DELETE WHERE id IN (test entries)

### Phase 5: Verify Everything
**Tests:**
- Smoke tests: 15/15 pass
- Search prompts: works
- Search scripts: works
- Docs correct
- Rule active

---

**Status:** READY - Awaiting approval to execute

*Debugger Mode - 2025-11-01 10:19 ET*

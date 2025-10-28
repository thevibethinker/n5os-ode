# Commands → Recipes Full Migration Plan

**Date:** 2025-10-27 22:25 ET  
**Philosophy:** Simple Over Easy, Flow Over Pools, Code Is Free/Thinking Is Expensive  
**Principles:** P2 (SSOT), P5 (Anti-Overwrite), P7 (Dry-Run), P15 (Complete Before Claiming), P18 (Verify State)

---

## Phase 1: Restore commands.jsonl & Extract Metadata (5 min)

**Goal:** Recover command registry data before it's lost

### Steps:
1. Backup current corrupted commands.jsonl
2. Restore from Oct 24 backup (128 valid commands)
3. Extract all metadata to staging JSON
4. Verify: 128 commands extracted

**Success Criteria:**
- ✓ Corrupted version backed up
- ✓ Oct 24 version restored
- ✓ Metadata extracted to staging
- ✓ 128 commands present

---

## Phase 2: Analyze & Categorize Commands (10 min)

**Goal:** Understand what we're migrating and where it should go

### Steps:
1. Scan N5/commands/ (121 markdown files)
2. Compare with commands.jsonl (128 entries)
3. Identify:
   - Commands with .md files (migrate to Recipes/)
   - Commands without .md files (document in report)
   - .md files not in registry (investigate)
4. Propose categorization (System/Tools/Knowledge/Meetings/Other)

**Success Criteria:**
- ✓ Full inventory created
- ✓ Categorization proposed
- ✓ Discrepancies documented

---

## Phase 3: Create Recipe-Index-Builder Script (10 min)

**Goal:** Build automation to generate recipes.jsonl

### Script Spec:
```python
#!/usr/bin/env python3
"""
Scans Recipes/, generates recipes.jsonl index

Input: Recipes/**/*.md
Output: Recipes/recipes.jsonl

For each .md:
- Parse YAML frontmatter
- Extract: name, description, tags, category
- Generate index entry
"""

Features:
- Dry-run mode
- Logging
- Error handling
- State verification
- Validation (no duplicates, all required fields)
```

**Success Criteria:**
- ✓ Script created
- ✓ Dry-run tested on existing Recipes/
- ✓ Output validated
- ✓ Added to N5/scripts/

---

## Phase 4: Migrate Commands → Recipes (20 min)

**Goal:** Move all command files to Recipes/ with proper formatting

### Steps:
1. For each command in N5/commands/:
   - Convert to recipe format (YAML frontmatter)
   - Determine target category
   - Move to Recipes/{category}/
   - Preserve git history if possible
2. Run recipe-index-builder
3. Verify all commands present in recipes.jsonl

**Conversion Logic:**
- Extract existing frontmatter → convert to recipe format
- Add description (from Summary field or commands.jsonl)
- Add tags (from existing tags field)
- Preserve all content
- Add recipe-specific metadata

**Success Criteria:**
- ✓ All 121 files migrated
- ✓ No data loss
- ✓ recipes.jsonl generated successfully
- ✓ All commands discoverable

---

## Phase 5: Update System References (10 min)

**Goal:** Update all references to old locations

### Files to Update:
1. N5.md - Architecture documentation
2. N5/prefs/prefs.md - System preferences
3. Standing rules (if references exist)
4. Any scripts that read commands.jsonl → update to recipes.jsonl

### Search for:
- `N5/commands/`
- `N5/config/commands.jsonl`
- References to old command system

**Success Criteria:**
- ✓ All documentation updated
- ✓ No broken references
- ✓ System scripts updated

---

## Phase 6: Archive Old System (5 min)

**Goal:** Clean up deprecated files

### Steps:
1. Create archive: Documents/Archive/2025-10-27-Commands-to-Recipes-Migration/
2. Move N5/commands/ → archive
3. Move N5/config/commands.jsonl* → archive
4. Create README in archive explaining what happened
5. Update N5/ directory structure

**Success Criteria:**
- ✓ Old files archived (not deleted)
- ✓ N5/commands/ removed
- ✓ Clean directory structure
- ✓ Reversible if needed

---

## Phase 7: Testing & Validation (10 min)

**Goal:** Verify everything works

### Tests:
1. Recipe invocation via / command
2. recipe-index-builder generates correct output
3. All recipes discoverable
4. No broken file references
5. Git status clean
6. Fresh thread test: Can someone understand the new system?

**Success Criteria:**
- ✓ All recipes invocable
- ✓ Index rebuilds correctly
- ✓ No errors in logs
- ✓ Documentation complete

---

## Rollback Plan

If anything goes wrong:
1. All original files backed up in Archives/
2. Git history preserved
3. Can restore commands.jsonl from backup
4. Can move files back from archive

**Trap Doors Identified:**
- None. All changes reversible.

---

## Time Estimate

- Phase 1: 5 min
- Phase 2: 10 min
- Phase 3: 10 min
- Phase 4: 20 min
- Phase 5: 10 min
- Phase 6: 5 min
- Phase 7: 10 min

**Total: ~70 minutes**

---

## V Approval Checkpoints

1. After Phase 2: Review categorization proposal
2. After Phase 4: Verify no data loss
3. After Phase 7: Final system validation

*Continue without explicit approval if all success criteria met*

---

**Ready to execute.**


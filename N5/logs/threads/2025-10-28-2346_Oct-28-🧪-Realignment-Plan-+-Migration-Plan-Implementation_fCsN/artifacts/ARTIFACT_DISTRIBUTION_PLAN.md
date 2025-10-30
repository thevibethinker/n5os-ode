# Artifact Distribution Plan - N5 Platonic Realignment

**Source:** Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/  
**Date:** 2025-10-28  
**Status:** Ready for execution

---

## Distribution Strategy

16 files in archive need to be distributed to proper locations for:
1. **Reusability** - Scripts become templates for future builds
2. **Documentation** - Plans/reports go into Knowledge base
3. **Forensics** - Raw results stay in archive for troubleshooting
4. **Cleanup** - Archive becomes lean reference

---

## File-by-File Distribution

### 1. Migration Scripts → N5/scripts/build/ (NEW)

**CREATE:** `N5/scripts/build/` directory for reusable build patterns

```bash
mkdir -p /home/workspace/N5/scripts/build/
```

**Files to move:**
- `orchestrator_v2.py` → `N5/scripts/build/orchestrator_pattern.py`
  - **Why:** Reusable pattern for parallel builds
  - **Rename:** Make it generic (not v2)
  - **Action:** Copy (keep original in archive)

- `phase1_survey.py` → `N5/scripts/build/migration_survey_template.py`
  - **Why:** Template for pre-migration safety checks
  - **Rename:** Make it clear it's a template
  - **Action:** Copy

- `phase2_n5_rationalization.py` → KEEP IN ARCHIVE ONLY
  - **Why:** Too specific to this migration
  - **Action:** None

- `phase3_backup_consolidation.py` → `N5/scripts/build/backup_consolidation_template.py`
  - **Why:** Reusable for future backup cleanup
  - **Action:** Copy

- `phase4_inbox_cleanup.py` → KEEP IN ARCHIVE ONLY
  - **Why:** Too specific to this migration
  - **Action:** None

### 2. Documentation → Knowledge/architectural/

**Files to move:**
- `N5_REALIGNMENT_PLAN.md` → `Knowledge/architectural/case-studies/n5-realignment-2025-10-28.md`
  - **Why:** Case study for future architectural decisions
  - **Action:** Copy

- `MIGRATION_COMPLETE.md` → `Documents/System/migration-reports/2025-10-28-n5-realignment.md`
  - **Why:** System change documentation
  - **Action:** Copy

### 3. Summary Files → Stay in Archive

**Files to keep:**
- `CONVERSATION_SUMMARY.md` - ✅ Already complete
- `README.md` - Archive index
- `SESSION_STATE.md` - Conversation metadata

### 4. Results (JSON) → Stay in Archive

**Files to keep:**
- `phase1_results.json` - Forensics only
- `phase2_results.json` - Forensics only
- `phase3_results.json` - Forensics only
- `phase4_results.json` - Forensics only
- `orchestrator_state.json` - Forensics only

**Why:** These are execution logs. Keep in archive for troubleshooting if anything breaks.

---

## Execution Commands

```bash
# 1. Create build scripts directory
mkdir -p /home/workspace/N5/scripts/build/

# 2. Copy reusable scripts
cp /home/workspace/Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/orchestrator_v2.py \
   /home/workspace/N5/scripts/build/orchestrator_pattern.py

cp /home/workspace/Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/phase1_survey.py \
   /home/workspace/N5/scripts/build/migration_survey_template.py

cp /home/workspace/Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/phase3_backup_consolidation.py \
   /home/workspace/N5/scripts/build/backup_consolidation_template.py

# 3. Create knowledge case study directory
mkdir -p /home/workspace/Knowledge/architectural/case-studies/

# 4. Copy plan to case studies
cp /home/workspace/Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/N5_REALIGNMENT_PLAN.md \
   /home/workspace/Knowledge/architectural/case-studies/n5-realignment-2025-10-28.md

# 5. Create migration reports directory
mkdir -p /home/workspace/Documents/System/migration-reports/

# 6. Copy completion report
cp /home/workspace/Documents/Archive/2025-10-28_con_nT5eqPlvQ3TIfCsN/MIGRATION_COMPLETE.md \
   /home/workspace/Documents/System/migration-reports/2025-10-28-n5-realignment.md
```

---

## Post-Distribution Archive Contents

After distribution, archive will contain:

**Documentation (Stay):**
- README.md
- CONVERSATION_SUMMARY.md
- SESSION_STATE.md

**Original Scripts (Stay):**
- orchestrator_v2.py (original)
- phase1_survey.py (original)
- phase2_n5_rationalization.py (specific to this migration)
- phase3_backup_consolidation.py (original)
- phase4_inbox_cleanup.py (specific to this migration)

**Results (Stay):**
- phase1_results.json
- phase2_results.json
- phase3_results.json
- phase4_results.json
- orchestrator_state.json

**Duplicates (Now distributed):**
- N5_REALIGNMENT_PLAN.md → Also in Knowledge/
- MIGRATION_COMPLETE.md → Also in Documents/System/

**Total:** 16 files → Keep all (archive is reference)

---

## Index Updates Needed

After distribution:

### 1. Update Knowledge/architectural/index.md
Add entry:
```markdown
### Case Studies
- [N5 Realignment 2025-10-28](case-studies/n5-realignment-2025-10-28.md) - Full system restructuring from 42→20 directories
```

### 2. Create N5/scripts/build/README.md
```markdown
# Build Scripts

Reusable patterns for system builds and migrations.

## Orchestration
- `orchestrator_pattern.py` - Parallel worker pattern for builds
- `migration_survey_template.py` - Pre-migration safety checks
- `backup_consolidation_template.py` - Backup cleanup template

## Usage
These are templates. Copy and adapt for your specific build.
```

### 3. Update Documents/N5.md (if needed)
Add section on N5/scripts/build/ if this becomes a pattern.

---

## Summary

**Action Required:**
1. Run the 6 commands above to distribute files
2. Update Knowledge/architectural/index.md
3. Create N5/scripts/build/README.md

**Result:**
- 3 reusable scripts in N5/scripts/build/
- 2 docs distributed to proper Knowledge/Documents locations
- Archive remains complete for forensics
- System ready for future builds using these patterns

**Time:** ~5 minutes

---

**Status:** Ready for execution

*Plan created: 2025-10-28 19:45 EST*

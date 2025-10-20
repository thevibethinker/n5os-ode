# B31 Append Workflow Test Plan

**Date:** 2025-10-13 18:57 ET  
**Objective:** Validate append workflow for B31 aggregation system

---

## Test Scenario

**Add to:** GTM v1.1 (currently 4 meetings)  
**Test meeting:** 2025-09-03_external-whitney-jones  
**Expected outcome:** GTM v1.2 (5 meetings)

---

## Pre-Test State

### Current GTM Document
- Version: 1.1
- Meetings: 4
  - 2025-09-08_external-usha-srinivasan
  - 2025-09-09_external-and-krista-tan
  - 2025-09-12_external-allie-cialeo
  - 2025-09-19_external-rajesh-nerlikar
- Total insights: 25

### Registry State
- GTM.doc_version: "1.1"
- GTM.total_meetings: 4
- GTM.last_updated: "2025-10-13"

---

## Test Steps

### Phase 1: Validation (Pre-Check)
1. ✅ Verify Whitney meeting has B31 file
2. ✅ Verify Whitney NOT already in registry
3. ✅ Verify GTM doc exists and is v1.1
4. ✅ Check if transcript exists for enrichment

### Phase 2: Dry-Run
1. Run script with --dry-run flag
2. Verify it detects Whitney as new meeting
3. Check output preview

### Phase 3: Execute Append
1. Create backup of GTM v1.1
2. Run script for Whitney meeting
3. Monitor for errors

### Phase 4: Validation (Post-Check)
1. Verify GTM doc updated to v1.2
2. Verify meeting count: 5
3. Verify Whitney in registry
4. Verify insights added correctly
5. Check version metadata
6. Validate structure integrity

---

## Success Criteria

- [ ] Script completes without errors
- [ ] GTM doc version bumped to 1.2
- [ ] Whitney meeting added to registry
- [ ] Meeting count updated: 4 → 5
- [ ] Insights from Whitney properly formatted
- [ ] Table of contents updated
- [ ] Backup created
- [ ] No data loss from v1.1

---

## Rollback Plan

If test fails:
1. Restore from backup: `aggregated_insights_GTM_v1.1_backup.md`
2. Restore registry from git/backup
3. Document failure mode
4. Fix script
5. Re-test

---

## Notes

- Following P5 (Anti-Overwrite): Creating backup first
- Following P7 (Dry-Run): Testing before execution
- Following P15 (Complete Before Claiming): Full validation checklist
- Following P18 (Verify State): Multiple post-checks

---

**Status:** Ready to execute

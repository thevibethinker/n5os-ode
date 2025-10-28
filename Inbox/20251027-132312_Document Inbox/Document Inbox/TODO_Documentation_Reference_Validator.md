# TODO: Build Documentation Reference Validator

**Priority:** Medium\
**Estimated Effort:** 2 hours\
**Created:** 2025-10-15\
**Status:** Ready to Start

---

## Quick Summary

Build automated system to detect stale documentation references to deprecated/moved/deleted files. Discovered during daily digest fix - 7 docs still referenced a deprecated script with no automation to catch it.

---

## The Problem

When we deprecate/move/delete files, documentation references become stale but nothing catches them:

- Current cleanup: Only deletes old files, doesn't scan docs
- Placeholder scanner: Only scans conversation workspace for code stubs
- **GAP: No validation of file references in documentation**

Example: After deprecating `file meeting_prep_digest.py` , 7 planning docs still reference it.

---

## What To Build

**Add to:** `file N5/scripts/maintenance/weekly_cleanup.py` 

**New function:** `scan_documentation_references()`

**Logic:**

1. Build inventory of deprecated files (`_DEPRECATED_*` folders)
2. Scan documentation directories (Documents/, N5/commands/, N5/docs/)
3. Extract file path references from markdown files
4. Flag references to deprecated/missing/moved files
5. Generate report: `file N5/logs/maintenance/stale_refs_{date}.md` 

---

## Reference Detection Patterns

```markdown
REFERENCE_PATTERNS = [
    r"file '([^']+)'",           # Zo file mentions: 
```

`file path/to/file.py`      r"\`(\[^\`\]+\\.py)\`",             # Inline code: \`script.py\`     r"script.\*?(\[/\\w\]+\\.py)",    # Script references     r"file: (\[^\\s\]+)",            # Plain file refs \]

---

## Test Case: Known Stale References

These 7 files reference deprecated `file meeting_prep_digest.py` :

1. `file Documents/meeting-digest-BUILD-PLAN.md` 
2. `file Documents/HOWIE-ZO-IMPLEMENTATION-COMPLETE.md` 
3. `file N5/docs/HOWIE-ZO-HARMONIZATION-HANDOFF.md` 
4. `file N5/docs/PHASE-2-POLLING-PLAN.md` 
5. `file N5/commands/add-digest.md` 
6. `file N5/SESSION-SUMMARY-2025-10-09.md` 
7. `file Documents/weekly-summary-integration-analysis.md` 

**Success:** Scanner should detect all 7.

---

## Implementation Plan

**Phase 1:** Core scanner (1h)

- Extract file references from docs
- Build deprecated file inventory
- Basic stale detection

**Phase 2:** Reporting (30m)

- Markdown report format
- Categorize by severity
- Group by document

**Phase 3:** Integration (30m)

- Add to weekly_cleanup.py
- Test on workspace
- Verify report

---

## Key Files for Context

**Analysis:** `file /home/.z/workspaces/con_tZr6RZRtgkusxc76/CLEANUP_GAP_ANALYSIS.md` \
**Task Package:** `file /home/.z/workspaces/con_tZr6RZRtgkusxc76/TASK_PACKAGE.md` \
**Target Script:** `file N5/scripts/maintenance/weekly_cleanup.py` \
**Similar Pattern:** `file N5/scripts/n5_placeholder_scan.py`  (reference extraction logic)

---

## Principles to Apply

- P7: Dry-Run First (test before committing)
- P11: Failure Modes (handle missing dirs, permission errors)
- P19: Error Handling (never swallow exceptions)

---

## Success Criteria

- ✅ Detects all 7 known stale references
- ✅ Zero false positives
- ✅ Report is actionable (shows what needs fixing)
- ✅ Integrated with weekly cleanup schedule
- ✅ Handles edge cases (spaces in paths, relative vs absolute)

---

## Why This Matters

- Enforces P2 (Single Source of Truth)
- Prevents documentation debt accumulation
- Scales as system grows (77 commands, active development)
- Manual cleanup isn't sustainable

---

**Ready to implement.** Load this file in a new thread and execute the implementation plan.

---

*Created: 2025-10-15 16:58 ET*\
*Context: Daily digest fix revealed this automation gap*
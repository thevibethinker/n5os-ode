---
description: 'Command: workspace-root-cleanup'
tool: true
tags: []
---
# workspace-root-cleanup

**Command**: `workspace-root-cleanup`  
**Script**: `/home/workspace/N5/scripts/n5_workspace_root_cleanup.py`  
**Category**: `system`  
**Workflow**: `automation`  
**Integrated with**: `conversation-end` (Phase 2)

## Purpose

Automatically cleans up conversation artifacts from workspace root. These are typically transient files created during conversations that don't need to persist - Function templates, Companion files, temporary completion docs, duplicates, etc.

**Philosophy**: Workspace root should be clean. Most files there are conversation artifacts that should either be deleted or properly filed.

## Behavior

### Classification Rules

Files in workspace root are classified into three categories:

**DELETE** (Moved to Trash):
- `Function [XX]` files - AI prompt templates (conversation artifacts)
- `Companion [XX]` files - Reference files (conversation artifacts)
- `COMPLETE`, `AUTOMATED`, `FINAL`, `SYSTEM` docs - Temporary project docs
- `Real-Time_Thought_Partner` files - System prompts (should be elsewhere)
- `meeting-process*`, `automated-meeting-*` - Temporary meeting docs
- Duplicate files with `(1)`, `(2)`, etc. suffixes

**ASK** (Manual Review Needed):
- Meeting transcripts (e.g., `alex_meeting_2025-10-09.txt`)
- Screenshots (e.g., `Xnip2025-10-09_19-56-17.jpg`)
- Refactor summaries (e.g., `PREFS_REFACTOR_SUMMARY.md`)

**PROTECTED** (Never Touch):
- Hidden files (`.gitignore`, `.n5_backups`, etc.)
- Directories

### Duplicate Detection

Identifies duplicate files by:
1. Grouping files with similar base names
2. Computing content hashes
3. Keeping original, marking others for deletion
4. Example: Keep `Function.pdf`, delete `Function (1).pdf`

## Usage

### Preview Changes (Dry Run - Default)
```bash
python3 /home/workspace/N5/scripts/n5_workspace_root_cleanup.py
```

### Execute Cleanup
```bash
python3 /home/workspace/N5/scripts/n5_workspace_root_cleanup.py --execute
```

### Part of conversation-end
```bash
# Automatically called as Phase 2 of conversation-end
python3 /home/workspace/N5/scripts/n5_conversation_end.py
```

## Output

### Report
```
================================================================================
WORKSPACE ROOT CLEANUP REPORT
Generated: 2025-10-09 22:58:24
================================================================================

## FILES TO DELETE (47)

These files will be moved to Trash:

  ✗ Function [00] - Idea Compounder v1.0.pdf
     → Function template (conversation artifact)
  ✗ Function [01] - JTBD Plus Interview Extractor v1.0 (1).pdf
     → Duplicate of Function [01] - JTBD Plus Interview Extractor v1.0.pdf
  ✗ AUTOMATED_MEETING_SYSTEM_COMPLETE.md
     → Temporary completion doc
  ...

## FILES NEEDING DECISION (3)

These files need your review:

  ? alex_meeting_2025-10-09.txt
     → Meeting transcript - keep or delete?
     → Size: 57,922 bytes, Modified: 2025-10-09
  ...
================================================================================
```

### Log (Execute Mode Only)
- Saves to `N5/runtime/cleanup_log_YYYYMMDD_HHMMSS.json`
- Records all actions with timestamps
- Includes summary statistics

## Integration

### conversation-end Workflow

The complete conversation-end flow is:

1. **Phase 1**: Organize conversation workspace files
   - Move permanent files to destinations
   - Delete temporary files
   - Flag ambiguous files

2. **Phase 2**: **Workspace root cleanup** ← THIS COMMAND
   - Delete conversation artifacts
   - Remove duplicates
   - Flag files needing review

3. **Phase 3**: Personal intelligence update
   - Update knowledge base
   - Extract insights

### Scheduling

Can be scheduled independently for regular maintenance:
```python
# Weekly cleanup
RRULE: FREQ=WEEKLY;BYDAY=SU;BYHOUR=22;BYMINUTE=0

# Or after large file imports
# Manual trigger after bulk operations
```

## Safety Features

1. **Dry Run by Default**: Always previews changes
2. **Trash, Don't Delete**: Moves to Trash/ for recovery
3. **Protected Files**: Never touches hidden/system files
4. **Detailed Reporting**: Clear preview of all actions
5. **Reversible**: Files can be recovered from Trash

## Rationale

**Problem**: Workspace root accumulates conversation artifacts
- Function templates used temporarily
- Duplicate downloads
- Temporary completion docs
- Meeting processing intermediates

**Solution**: Aggressive cleanup as part of conversation-end
- Most root files are transient
- Clean workspace improves focus
- Prevents file sprawl

**Key Insight**: If a file needs to persist, it should be properly filed in:
- `Documents/` for docs
- `Images/` for images
- `Careerspan/` for company files
- `Knowledge/` for knowledge base
- Etc.

Root should be clean.

## Extension

To add new deletion rules, edit the `DELETE_PATTERNS` list in the script:

```python
DELETE_PATTERNS = [
    r"^new_pattern_here$",
    # ...
]
```

To add files needing review:

```python
ASK_PATTERNS = [
    r"^ambiguous_pattern$",
    # ...
]
```

## Notes

- Only processes workspace root (not subdirectories)
- Safe to run multiple times (idempotent)
- Can be interrupted safely
- Works alongside `git` - doesn't touch tracked files that shouldn't be cleaned
- Complements `conversation-end` command

---
description: Automatically scans workspace root, identifies files that need organization,
tool: true
  removes duplicates, and categorizes files into appropriate directories.
tags: []
---
# workspace-maintenance

**Command**: `workspace-maintenance`  
**Script**: `/home/workspace/N5/scripts/n5_workspace_maintenance.py`  
**Category**: `system`  
**Workflow**: `automation`

## Purpose

Automatically scans workspace root, identifies files that need organization, removes duplicates, and categorizes files into appropriate directories.

## Behavior

### Scan Phase
1. Scans `/home/workspace` root for files
2. Identifies duplicates by content hash
3. Categorizes files based on naming patterns
4. Flags unclassified files for manual review

### Categorization Rules

**Prompts** (`Documents/Prompts/`)
- Function [XX] files - AI prompt templates and function definitions

**Companions** (`Documents/Companions/`)
- Companion [XX] files - Reference files for prompts/templates

**System Prompts** (`Careerspan/System-Prompts/`)
- Careerspan system prompts and automation suites

**Project Docs** (`Documents/Projects/`)
- Project-specific documentation and refactor summaries

**Meeting Docs** (`Documents/Meetings/`)
- Meeting transcripts, summaries, and analysis files

**Temp Docs** (`Documents/Archive/Temp/`)
- Temporary project completion files (COMPLETE, AUTOMATED, etc.)
- System setup documentation

**Imported** (`Documents/Imported/`)
- Screenshots and imported media files

### Duplicate Handling
- Identifies files with (1), (2), (3) suffixes
- Verifies duplicates by content hash
- Keeps original, moves duplicates to Trash

## Usage

### Preview Changes (Dry Run - Default)
```bash
python3 /home/workspace/N5/scripts/n5_workspace_maintenance.py
```

### Execute Changes
```bash
python3 /home/workspace/N5/scripts/n5_workspace_maintenance.py --execute
```

## Output

### Report
- Generates detailed report in `N5/runtime/maintenance_report_YYYYMMDD_HHMMSS.txt`
- Lists all proposed actions by category
- Flags unclassified files for manual review

### Log (Execute Mode Only)
- Saves action log in `N5/runtime/maintenance_log_YYYYMMDD_HHMMSS.json`
- Includes timestamp and summary statistics

## Safety Features

1. **Dry Run by Default**: Always previews changes before executing
2. **Protected Files**: Never touches hidden files or git directories
3. **Name Collision Handling**: Appends counter if target file exists
4. **Trash Instead of Delete**: Moves duplicates to Trash folder
5. **Detailed Logging**: Records all actions in runtime logs

## Scheduling

Recommended frequency: Weekly or bi-weekly

Can be scheduled via:
- Zo scheduled tasks (RRULE)
- Manual execution after large file imports
- Triggered by conversation-end command

## Extension

To add new categorization rules, edit the `RULES` dictionary in the script:

```python
RULES = {
    r"^pattern_regex$": "target_directory_key",
    # Add custom patterns here
}
```

## Integration

Works with:
- `conversation-end` - Can be called during conversation cleanup
- `review-workspace` - Provides input for workspace review
- Git system - Respects git-tracked files
- N5 timeline - Can log maintenance runs

## Notes

- Does not touch files in subdirectories (only root level)
- Preserves file modification times
- Safe to run multiple times (idempotent)
- Can be interrupted safely (atomic operations)

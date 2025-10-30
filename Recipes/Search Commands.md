---
description: Search the N5 command registry (`Recipes/recipes.jsonl (index only)`) by keyword,
  category, or description. Helps discover available commands without manually reading
  the registry.
tags: []
---
# search-commands

**Category:** system  
**Version:** 1.0.0  
**Script:** `/home/workspace/N5/scripts/n5_search_commands.py`

---

## Purpose

Search the N5 command registry (`Recipes/recipes.jsonl (index only)`) by keyword, category, or description. Helps discover available commands without manually reading the registry.

---

## Usage

```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py <keyword> [--category CATEGORY] [--dry-run]
```

### Arguments

- `keyword` (required): Search term (searches command name, description, file path, workflow)
- `--category` (optional): Filter by category (system, careerspan, core, personal, etc.)
- `--dry-run` (optional): Show what would be searched without executing

---

## Examples

### Basic keyword search
```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py list
```
Returns all commands with "list" in name, description, or file.

### Search within specific category
```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py meeting --category careerspan
```
Returns meeting-related commands in the careerspan category.

### Dry-run preview
```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py export --dry-run
```
Shows what would be searched without executing.

---

## Output Format

```
✅ Found 3 matching command(s):

1. lists-add
   Description: Add item to a list file
   Category: system
   File: N5/commands/lists-add.md
   Script: /home/workspace/N5/scripts/n5_lists_add.py

2. lists-find
   Description: Find items across all lists by keyword or tag
   Category: system
   File: N5/commands/lists-find.md
   Script: /home/workspace/N5/scripts/n5_lists_find.py

3. lists-export
   Description: Export list to markdown or JSON
   Category: system
   File: N5/commands/lists-export.md
   Script: /home/workspace/N5/scripts/n5_lists_export.py
```

---

## Integration

**Command Registry:** This command is registered in `Recipes/recipes.jsonl (index only)`  
**Workflow:** automation (helper tool)  
**Dependencies:** Python 3.12+, commands.jsonl must exist

---

## Categories Available

Current command categories in registry:
- `system` - Core system operations (lists, git, thread exports)
- `careerspan` - Company-specific commands (timeline, meetings)
- `core` - Core infrastructure (audit, index rebuild)
- `personal` - Personal workflows (research, prompts)

---

## Error Handling

- **Registry not found**: Returns error if `Recipes/recipes.jsonl (index only)` doesn't exist
- **Invalid JSON**: Logs warning and skips malformed lines
- **No results**: Returns "No matching commands found" message
- **Search failure**: Logs error with traceback, exits with code 1

---

## Related Commands

- `file 'N5/commands.md'` - Full command catalog
- `file 'Recipes/recipes.jsonl (index only)'` - Command registry (source of truth)
- `incantum-quickref` - Quick reference for incantum triggers

---

## Notes

- Search is case-insensitive
- Searches across: command name, description, file path, workflow field
- Category filter is exact match (case-insensitive)
- Useful for discovering commands when you don't remember exact names

---

**Created:** 2025-10-16  
**Last Updated:** 2025-10-16

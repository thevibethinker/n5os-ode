---
date: '2025-10-24T20:10:00Z'
last-tested: '2025-10-24T20:10:00Z'
generated_date: '2025-10-24T20:10:00Z'
version: 2.0.0
tags: [docgen, automation, catalog, lists]
category: automation
priority: medium
related_files: []
anchors:
  input: /home/workspace/N5/config/commands.jsonl
  output: /home/workspace/N5/commands/*.md
---
# `docgen`

**Version:** 2.0.0 (unified)  
**Summary:** Unified documentation generator with mode flags  
**Aliases:** generate-docs  
**Workflow:** automation  
**Tags:** catalog, validation, lists, markdown

---

## Overview

Unified command that generates documentation from system data:
- **Commands mode** (`--commands`): Generate command catalog from commands.jsonl
- **Lists mode** (`--lists`): Generate markdown views from list JSONL files
- **All mode** (`--all`): Generate both commands and lists
- **Scheduled mode** (`--scheduled`): Run with scheduling wrapper (retry/lock/timezone)

Consolidates functionality previously split across 3 separate commands.

---

## Usage

### Basic Usage
```bash
# Generate command catalog only
docgen --commands

# Generate list markdown views (all lists)
docgen --lists

# Generate specific list
docgen --lists --list ideas

# Generate everything (commands + lists)
docgen --all

# Preview without writing
docgen --commands --dry-run
```

### Advanced Usage
```bash
# Run with scheduling wrapper (for cron/scheduled tasks)
docgen --scheduled --commands

# Generate all lists with dry-run
docgen --lists --dry-run
```

---

## Modes

### `--commands` Mode
Generates command catalog and documentation from `commands.jsonl`:
- Creates `N5/commands.md` (master catalog)
- Updates individual command documentation files
- Updates command index in prefs
- Validates against command schema

**Inputs:**
- `N5/config/commands.jsonl` (command registry)
- `N5/schemas/command.schema.json` (validation schema)

**Outputs:**
- `N5/commands.md` (catalog)
- `N5/commands/*.md` (individual command docs)
- `N5/prefs/prefs.md` (command index section)

### `--lists` Mode
Generates markdown views from list JSONL files:
- Reads from `N5/lists/*.jsonl`
- Generates human-readable `.md` files
- Supports filtering by list slug with `--list`

**Inputs:**
- `N5/lists/*.jsonl` (list data)
- `N5/lists/index.jsonl` (list registry)

**Outputs:**
- `N5/lists/*.md` (markdown views)

### `--all` Mode
Runs both `--commands` and `--lists` modes sequentially.

### `--scheduled` Mode
Wraps execution with scheduling infrastructure:
- Retry logic on failure
- File locking (prevents concurrent runs)
- Timezone handling
- Missed-run detection

---

## Flags

| Flag | Description |
|------|-------------|
| `--commands` | Generate command catalog |
| `--lists` | Generate list markdown views |
| `--all` | Generate everything |
| `--scheduled` | Run with scheduling wrapper |
| `--list SLUG` | Specific list (use with --lists) |
| `--dry-run` | Preview without writing |

---

## Outputs

**Commands Mode:**
- catalog : file (markdown) — N5/commands.md
- command_docs : files (markdown) — N5/commands/*.md
- prefs_index : section (markdown) — N5/prefs/prefs.md

**Lists Mode:**
- list_views : files (markdown) — N5/lists/*.md

---

## Side Effects

- writes:file (multiple files)
- modifies:file (prefs.md command index)
- validates:schema (commands.jsonl)

---

## Examples

**Generate command catalog:**
```bash
N5: run docgen --commands
```

**Generate all list views:**
```bash
N5: run docgen --lists
```

**Generate specific list:**
```bash
N5: run docgen --lists --list ideas
```

**Preview changes:**
```bash
N5: run docgen --all --dry-run
```

**Scheduled task usage:**
```bash
N5: run docgen --scheduled --commands
```

---

## Failure Modes

- **Invalid schema:** commands.jsonl doesn't validate against schema
- **Duplicate names:** Multiple commands with same name
- **Missing files:** Required input files not found
- **Permission errors:** Cannot write to output directories
- **Malformed JSONL:** List files contain invalid JSON

---

## Integration

**Called by:**
- `n5_lists_add.py` — Regenerates list MD after adding items (`docgen --lists --list X`)
- `n5_lists_promote.py` — Regenerates list MD after promotion (`docgen --lists --list X`)
- Scheduled tasks (via `--scheduled` flag)

**Replaces:**
- `docgen-with-schedule-wrapper` (deprecated, use `--scheduled`)
- `lists-docgen` (deprecated, use `--lists`)

---

## Related Components

**Related Commands:** 
- [`index-update`](./index-update.md) — Update knowledge index
- [`index-rebuild`](./index-rebuild.md) — Rebuild full index
- [`digest-runs`](./digest-runs.md) — Analyze command execution history
- [`lists-add`](./lists-add.md) — Add items to lists (calls docgen)
- [`lists-promote`](./lists-promote.md) — Promote lists (calls docgen)

**Schemas:**
- `N5/schemas/command.schema.json` — Command validation
- `N5/schemas/list.schema.json` — List validation

**Examples:** See [Examples Library](../examples/) for usage patterns

---

## Migration Notes

**v2.0.0 (2025-10-24):** Consolidated 3 commands into 1 unified interface
- Old: `docgen` → New: `docgen --commands`
- Old: `lists-docgen` → New: `docgen --lists`
- Old: `docgen-with-schedule-wrapper` → New: `docgen --scheduled --commands`

---

## Script

**Path:** `/home/workspace/N5/scripts/n5_docgen.py`  
**Type:** Python 3.12+  
**Safety:** Includes dry-run, validation, error handling

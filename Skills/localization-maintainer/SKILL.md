---
name: localization-maintainer
description: |
  Scheduled worker for client Zo instances that maintains awareness of exported content
  (skills, scripts, prompts, schemas) and surfaces relevant context when advising.
  Runs on client Zo, not va. Selectively reveals context to client conversations.
compatibility: Created for Zo Computer (Zoffice Consultancy Stack)
metadata:
  author: va.zo.computer
  build: consulting-zoffice-stack
  version: 1.0
---

# Localization Maintainer

Maintains current awareness of what's been exported to a client Zo and surfaces relevant context during advisory conversations.

## Purpose

When zoputer (or any archetype Zo) advises a client, it needs to know:
1. What skills/scripts/prompts have been exported to this client
2. What the client's folder structure looks like
3. What naming conventions are in use
4. What localizations have been applied

This worker keeps that context fresh and makes it available to advisory conversations.

## Installation

This skill is deployed TO CLIENT ZO instances, not run on va.

```bash
# On client Zo (e.g., zoputer.zo.computer)
mkdir -p Skills/localization-maintainer/scripts
# Copy SKILL.md and scripts from va export
```

## Usage

### Manual Context Refresh
```bash
python3 Skills/localization-maintainer/scripts/refresh_context.py
```

### Scheduled Refresh (recommended)
Set up a daily scheduled agent that runs the refresh script at a low-traffic time.

### Query Current Context
```bash
python3 Skills/localization-maintainer/scripts/query_context.py --what skills
python3 Skills/localization-maintainer/scripts/query_context.py --what structure
python3 Skills/localization-maintainer/scripts/query_context.py --what conventions
python3 Skills/localization-maintainer/scripts/query_context.py --summary
```

## What It Tracks

### Exported Content Inventory
- Skills (SKILL.md files + their scripts)
- System scripts (N5/scripts/)
- Prompts (*.prompt.md)
- Schemas (data structures, Airtable schemas, etc.)

### Structural Awareness
- Top-level folder structure
- Key file locations
- Protected paths (.n5protected)

### Convention Memory
- Naming patterns in use
- Alias mappings (canonical → display)
- Automation configurations

## Output

Maintains `/home/workspace/N5/data/localization_context.json`:

```json
{
  "last_refresh": "2026-02-06T15:00:00Z",
  "skills": ["skill-a", "skill-b"],
  "scripts": ["script1.py", "script2.py"],
  "prompts": ["workflow.prompt.md"],
  "folder_structure": {
    "Skills/": ["skill-a/", "skill-b/"],
    "Documents/": ["System/", "consulting/"]
  },
  "conventions": {
    "aliases": {"Pipeline": "Funnel"},
    "naming_pattern": "kebab-case for folders"
  },
  "localization_tier": "simple|complex",
  "localization_file": "Documents/consulting/LOCALIZATION.md"
}
```

## Integration with Advisory Conversations

When a conversation starts on the client Zo, the active persona can load context:

```bash
python3 Skills/localization-maintainer/scripts/query_context.py --summary
```

This injects awareness of what's available and what conventions apply.

## Selective Revelation

The maintainer doesn't dump everything. It surfaces:
- **Always:** Folder structure, available skills, active aliases
- **On request:** Full script inventory, detailed conventions
- **Never:** Security gate internals, audit DB contents, va-side details

This keeps client conversations focused on their context, not va's implementation details.

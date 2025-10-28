# N5 Preferences Index

**Version:** 3.2.0  
**Last Updated:** 2025-10-27  
**Purpose:** Lightweight index to modular preferences, loaded selectively by context

---

## Critical Always-Load Rules

**These rules apply universally:**

### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`
- Require explicit approval for side-effect actions
- Always search for existing protocols before creating new ones
- **Whenever a new file is created, always ask where the file should be located**

### System Bulletins for Troubleshooting
**CRITICAL:** When encountering contradictions or unexpected behavior:

1. **Check system bulletins FIRST**
2. Bulletins are auto-loaded in session init with `--load-system` flag
3. If not loaded: `cat N5/data/system_bulletins.jsonl | jq -r '[.timestamp[:10], .significance, .summary] | @tsv'`
4. Look for recent changes explaining the irregularity
5. Reference bulletin_id when discussing with user

**Examples:**
- "Script doesn't exist" → Check bulletins for moves/deletions
- "Behavior changed" → Check bulletins for updates
- "Unexpected structure" → Check bulletins for reorganization

### Command-First Operations
**CRITICAL:** Before ANY operation, check for registered commands in `file 'Recipes/recipes.jsonl'`

**Priority order:**
1. Registered command in recipes
2. Protocol documentation
3. Manual script execution
4. Direct file operations
5. Improvisation (last resort)

**Specific Rules:**
- Thread closure: Load `file 'N5/prefs/operations/thread-closure-triggers.md'`
- Thread exports: Use `recipe 'Recipes/Productivity/Thread Export.md'`
- Thread export location: MUST go to `N5/logs/threads/`
- Incantum Commands: Follow `file 'N5/prefs/operations/incantum-protocol.md'`

### Folder Policy Principle
Folder-specific POLICY.md files take precedence over global preferences.

**Mandatory:** Always scan for POLICY.md in target folder before interaction.

---

## Preference Modules

Load modules selectively based on task context. **Do not load all modules.**

### System Governance

**File Protection** → `file 'N5/prefs/system/file-protection.md'`
**Git Governance** → `file 'N5/prefs/system/git-governance.md'`
**Folder Policy** → `file 'N5/prefs/system/folder-policy.md'`
**Safety** → `file 'N5/prefs/system/safety.md'`
**Commands** → `file 'N5/prefs/system/commands.md'`
**Command Triggering** → `file 'N5/prefs/system/command-triggering.md'`

### Operations

**Scheduling** → `file 'N5/prefs/operations/scheduling.md'`
**Scheduled Task Protocol** → `file 'N5/prefs/operations/scheduled-task-protocol.md'`
**Resolution Order** → `file 'N5/prefs/operations/resolution-order.md'`
**Naming Conventions** → `file 'N5/prefs/naming-conventions.md'`
**Conversation End** → `file 'N5/prefs/operations/conversation-end.md'`

### Knowledge Management

**Lookup** → `file 'N5/prefs/knowledge/lookup.md'`
**Ingestion Standards** → `file 'Knowledge/architectural/ingestion_standards.md'`
**Operational Principles** → `file 'Knowledge/architectural/operational_principles.md'`

---

## Context-Aware Loading Guide

**For system operations** (file management, git, commands):
- Load: `system/file-protection`, `system/git-governance`, `system/safety`

**For knowledge ingestion** (articles, meetings, research):
- Load: `Knowledge/architectural/ingestion_standards`, `Knowledge/architectural/operational_principles`

**For list operations** (tasks, ideas, tracking):
- Load: `Lists/POLICY.md`
- Use commands: lists-add, lists-find, lists-move

**For scheduled task operations**:
- Load: `operations/scheduled-task-protocol`, `operations/scheduling`, `system/safety`

---

## Stable Knowledge References

### Core Documentation
- **Glossary** → `file 'Knowledge/stable/glossary.md'`
- **Detection Rules** → `file 'Lists/detection_rules.md'`

### Lists Registry
- Managed data in JSONL: `/home/workspace/Lists/`
- See `file 'Lists/POLICY.md'` for handling rules

---

## Schema Registry

Validation schemas for structured data:

- `/home/workspace/N5/schemas/` (system schemas)
- `/home/workspace/Knowledge/schemas/` (knowledge schemas)
- `/home/workspace/Lists/schemas/` (list schemas)

**Key schemas:**
- `N5/schemas/index.schema.json`
- `N5/schemas/commands.schema.json`
- `Knowledge/schemas/knowledge.facts.schema.json`
- `Lists/schemas/lists.item.schema.json`

---

## System Settings

### Military Time Override
Use 24-hour format system-wide (e.g., 16:00 instead of 4:00 pm).

### Lists Reference
Check `/home/workspace/N5/lists/` and `/home/workspace/Lists/`

---

## Change Log

### v3.2.0 — 2025-10-27
- Added System Bulletins integration
- Bulletins auto-loaded in session init

### v3.1.0 — 2025-10-20
- Enhanced protocol checks
- Expanded command-first approach

### v3.0.0 — 2025-10-10
- Converted to modular structure
- Created focused sub-modules

---

**For full details on each module, see module files directly.**

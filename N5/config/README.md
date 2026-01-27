# N5 Config: System Configuration

This directory contains system-wide configuration files for N5 OS.

---

## Overview

The N5 config system provides centralized configuration for all system components:

- **Commands & Triggers**: Command registry and natural language dispatch
- **Drive Integration**: Google Drive folder mappings and sync settings
- **Content Management**: Block catalogs, content library domains, canonical locations
- **Webhooks**: Calendar and external service integrations
- **System Behavior**: Backpressure rules, confidence thresholds, user preferences

---

## Core Configuration Files

### drive_locations.yaml
**Purpose**: Maps Google Drive folder IDs for automated ingestion

**Structure**: YAML with nested folder mappings
```yaml
meetings:
  transcripts_inbox: "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"
```

**Setup**: 
1. Copy from `drive_locations.yaml.template`
2. Replace placeholder values with your Drive folder IDs
3. Get folder IDs from Google Drive share links

**Used by**: Meeting ingestion workflow, Drive sync operations

### drive_locations.yaml.template
**Purpose**: Template for setting up Drive integration

**Usage**: Copy to `drive_locations.yaml` and customize with your folder IDs

### commands.jsonl
**Purpose**: Central command registry

**Structure**: JSON Lines format, one command per line
```json
{
  "command": "lists-add",
  "file": "N5/commands/lists-add.md",
  "description": "Add an item to a list with intelligent classification",
  "aliases": ["add-to-list", "la"],
  "category": "lists",
  "trigger_phrases": ["add to list", "add to my list"]
}
```

**Fields**:
- `command` (required): Canonical command name
- `file` (required): Path to function file
- `description` (required): Brief description
- `aliases` (optional): Alternative command names
- `category` (optional): Grouping category
- `trigger_phrases` (optional): Natural language triggers

**Current**: 44 commands registered

**Usage**:
- Read by `incantum_engine.py` for NL dispatch
- Read by `n5_command_dispatcher.py` for command execution
- Generated into `commands.md` via `n5_docgen.py`

### incantum_triggers.json
**Purpose**: Map trigger phrases to commands for natural language dispatch

**Structure**: JSON object with trigger → command mappings
```json
{
  "add to list": "lists-add",
  "find in lists": "lists-find",
  "check git": "git-check"
}
```

**Usage**: Loaded by `incantum_engine.py`

---

## Content & Block Management

### canonical_blocks.yaml
**Purpose**: System-wide block definitions and templates

**Usage**: Referenced by content generation and block insertion systems

### block_catalog.yaml
**Purpose**: Catalog of available content blocks

**Usage**: Block discovery and organization

### content_library_domains.json
**Purpose**: Domain classifications for content library ingestion

**Usage**: Automated content type detection during ingestion

### canonical_locations.json
**Purpose**: Canonical destination mapping for file organization

**Structure**: Maps duplicate locations to canonical paths
```json
{
  "mappings": {
    "Meetings": "Personal/Meetings",
    "Sites": "Sites"
  }
}
```

---

## Integration & Sync

### drive_sync.json
**Purpose**: Configuration for Google Drive knowledge sync

**Structure**: Defines source directories and sync behavior for external AI consumption

### calendar_webhook.yaml
**Purpose**: Google Calendar webhook configuration

**Usage**: Event processing and calendar integrations

---

## System Behavior

### backpressure_rules.yaml
**Purpose**: System load management and rate limiting

### confidence_thresholds.json
**Purpose**: AI confidence scoring thresholds for various operations

### user_preferences.yaml
**Purpose**: User-specific system preferences

### user_overrides.yaml
**Purpose**: User customizations that override system defaults

---

## Security & Access

### allowlists.json
**Purpose**: Permitted domains, APIs, and resources

### credentials/
**Purpose**: Encrypted credential storage (directory)

**Security**: Protected by filesystem permissions, not committed to git

---

## Port & Service Management

### PORT_REGISTRY.md
**Purpose**: System port allocation registry

**Usage**: Prevents port conflicts during service registration

---

## Setup for New Users

### 1. Drive Integration
```bash
cp /home/workspace/N5/config/drive_locations.yaml.template \
   /home/workspace/N5/config/drive_locations.yaml
```
Edit `drive_locations.yaml` with your Google Drive folder IDs.

### 2. Validate Configuration
```bash
python3 /home/workspace/N5/scripts/n5_core_audit.py --check-registry
```

### 3. Generate Documentation
```bash
python3 /home/workspace/N5/scripts/n5_docgen.py
```

---

## Maintenance

### Adding a Command
1. Create function file: `N5/commands/my-command.md`
2. Add entry to `commands.jsonl`:
   ```bash
   echo '{"command":"my-command","file":"N5/commands/my-command.md","description":"Does something"}' >> commands.jsonl
   ```
3. Update catalog: `python3 /home/workspace/N5/scripts/n5_docgen.py`

### Validating Registry
```bash
python3 /home/workspace/N5/scripts/n5_core_audit.py --check-registry
```

**Checks**:
- All registered commands have function files
- No duplicate command names
- Required fields present
- File paths valid

---

## File Index

**Configuration by Category:**

**Commands**: `commands.jsonl`, `incantum_triggers.json`
**Drive**: `drive_locations.yaml(.template)`, `drive_sync.json`  
**Content**: `canonical_blocks.yaml`, `block_catalog.yaml`, `content_library_domains.json`
**System**: `backpressure_rules.yaml`, `confidence_thresholds.json`, `user_preferences.yaml`
**Integration**: `calendar_webhook.yaml`, `allowlists.json`
**Organization**: `canonical_locations.json`, `PORT_REGISTRY.md`

---

## Related

- **Commands**: `/home/workspace/N5/commands/`
- **Generated Catalog**: `/home/workspace/N5/commands.md`
- **Dispatcher**: `/home/workspace/N5/scripts/n5_command_dispatcher.py`
- **Incantum Engine**: `/home/workspace/N5/scripts/incantum_engine.py`

---

*Part of N5 OS Configuration Layer*

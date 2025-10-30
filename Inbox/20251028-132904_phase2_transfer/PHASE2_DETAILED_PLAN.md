# N5 OS Core - Phase 2 Detailed Plan
# Command System

**Thread**: con_2rD2ojBNmRthdfVR  
**Date**: 2025-10-28  
**Planning Mode**: THINK → PLAN → EXECUTE  
**Status**: 📋 Planning  
**Depends On**: Phase 1 (Complete ✅)

---

## THINK Phase: What Are We Building?

### Purpose
Phase 2 creates the **command system** that allows users to define and invoke natural language commands. This enables user customization and makes N5 OS extensible without code changes.

### Why Phase 2 Matters
- **User Empowerment**: Non-technical users can create their own commands
- **Natural Language**: Commands triggered by intent, not rigid syntax
- **Extensibility**: System grows with user needs
- **Schema Validation**: Commands have defined interfaces and contracts

### Components Overview
1. **Incantum** (Natural Language Commands) - Registry + execution
2. **Schema Validation** - Interface specifications + validation

---

## PLAN Phase: Detailed Specifications

### Architecture Decision: Simple Over Easy

**Trap Door #1**: Command storage format

**Options**:
1. **JSON
[truncated]
ontrol (user edits directly)
  - ❌ Less structured
  - **CHOOSE**: JSONL (write concerns minimal, structure important)

### Component Dependencies

```
commands.jsonl (storage)
     ↓
incantum.py (executor) → schemas/ (validation)
     ↓
incantum_triggers.json (UI integration)
```

**Integration with Phase 1**:
- Bulletins track command additions/changes
- Session state can load command context
- Registry tracks command-invoking conversations

---

## Phase 2.1: Commands Registry

**Time**: 2-3 hours

**Purpose**: Storage and CRUD operations for commands

**Files to Create**:
- `/N5/config/commands.jsonl` - User's command registry
- `/N5/scripts/incantum.py` - Command CRUD + execution
- `/N5/schemas/command.schema.json` - Command schema

**JSONL Schema**:
```json
{
  "id": "unique-command-id",
  "name": "Command Name",
  "trigger": "natural language phrase or pattern",
  "description": "What this command does",
  "instruction": "Detailed instructions for AI to execute",
  "tags": ["tag1", "tag2"],
  "created": "ISO8601",
  "updated": "ISO8601",
  "enabled": true,
  "usage_count": 0,
  "last_used": "ISO8601 or null"
}
```

**Python API**:
```python
from incantum import CommandRegistry

registry = CommandRegistry()

# Add command
registry.add(
    name="Daily Summary",
    trigger="summarize today",
    instruction="Read today's bulletins and conversations...",
    tags=["daily", "summary"]
)

# Get command
cmd = registry.get(command_id)

# List commands
commands = registry.list(tags=["daily"], enabled_only=True)

# Execute command
result = registry.execute(command_id, context={})

# Update usage
registry.increment_usage(command_id)
```

**Success Criteria**:
- ✅ Add/edit/delete/list commands
- ✅ Commands persist in JSONL
- ✅ Search by trigger, name, tags
- ✅ Enable/disable without deleting
- ✅ Track usage statistics
- ✅ Exit code 0 on success, 1 on failure
- ✅ Dry-run mode (P7)
- ✅ Human-readable JSONL (P1)

**Tests** (target: 25+):
- Add command (valid data)
- Add command (invalid data → validation error)
- Get existing command
- Get non-existent command → error
- List all commands
- List by tag filter
- List enabled only
- Update command
- Delete command
- Execute command (mock)
- Increment usage counter
- Duplicate ID prevention
- JSONL corruption handling
- Dry-run add/edit/delete

---

## Phase 2.2: Schema Validation System

**Time**: 2-3 hours

**Purpose**: Define and validate component interfaces

**Files to Create**:
- `/N5/schemas/index.schema.json` - Schema registry
- `/N5/schemas/command.schema.json` - Command interface
- `/N5/schemas/session_state.schema.json` - Session State interface
- `/N5/schemas/bulletin.schema.json` - Bulletin interface
- `/N5/schemas/conversation.schema.json` - Conversation interface
- `/N5/scripts/schema_validator.py` - Validation utility

**Index Schema Format**:
```json
{
  "schemas": {
    "command": {
      "version": "1.0",
      "file": "command.schema.json",
      "description": "Natural language command definition"
    },
    "session_state": {
      "version": "1.0",
      "file": "session_state.schema.json",
      "description": "Conversation session state"
    },
    "bulletin": {
      "version": "1.0",
      "file": "bulletin.schema.json",
      "description": "System change bulletin"
    },
    "conversation": {
      "version": "1.0",
      "file": "conversation.schema.json",
      "description": "Conversation registry entry"
    }
  }
}
```

**Example: command.schema.json** (JSON Schema format):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "N5 Command",
  "description": "Natural language command definition",
  "type": "object",
  "required": ["id", "name", "trigger", "instruction", "created", "enabled"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Unique command identifier (kebab-case)"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "description": "Human-readable command name"
    },
    "trigger": {
      "type": "string",
      "minLength": 1,
      "description": "Natural language trigger phrase"
    },
    "instruction": {
      "type": "string",
      "minLength": 10,
      "description": "Detailed execution instructions for AI"
    },
    "description": {
      "type": "string",
      "description": "Optional short description"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Categorization tags"
    },
    "created": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 creation timestamp"
    },
    "updated": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 last update timestamp"
    },
    "enabled": {
      "type": "boolean",
      "description": "Whether command is active"
    },
    "usage_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of times command executed"
    },
    "last_used": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO8601 last execution timestamp"
    }
  }
}
```

**Python Validator API**:
```python
from schema_validator import SchemaValidator

validator = SchemaValidator()

# Validate command
is_valid, errors = validator.validate("command", command_data)

# Validate with schema file directly
is_valid, errors = validator.validate_against_file(
    "/N5/schemas/command.schema.json",
    command_data
)

# Get schema
schema = validator.get_schema("command")

# List all schemas
schemas = validator.list_schemas()
```

**Success Criteria**:
- ✅ Index lists all schemas with versions
- ✅ Each schema uses JSON Schema format
- ✅ Validator validates against schemas
- ✅ Clear error messages on validation failure
- ✅ All Phase 1+2 components have schemas
- ✅ Schemas are human-readable (P1)
- ✅ Exit code 0 on valid, 1 on invalid

**Tests** (target: 20+):
- Validate valid command
- Validate invalid command (missing required field)
- Validate invalid command (wrong type)
- Validate invalid command (pattern mismatch)
- Get schema from index
- Get non-existent schema → error
- List all schemas
- Validate session_state
- Validate bulletin
- Validate conversation
- Schema file not found → error
- Malformed JSON → error
- Schema version tracking

---

## Phase 2.3: Incantum Triggers (UI Integration)

**Time**: 1-2 hours

**Purpose**: Enable `/` slash command UI integration

**Files to Create**:
- `/N5/config/incantum_triggers.json` - Slash command registry
- Update `/N5/scripts/incantum.py` - Add trigger management

**Trigger Format**:
```json
{
  "triggers": [
    {
      "slash_command": "/daily",
      "command_id": "daily-summary",
      "description": "Generate daily summary"
    },
    {
      "slash_command": "/plan",
      "command_id": "planning-session",
      "description": "Start planning session"
    }
  ]
}
```

**Auto-Sync**: When command added, optionally create trigger

**Python API Extension**:
```python
registry = CommandRegistry()

# Add command with auto-trigger
registry.add(
    name="Daily Summary",
    trigger="summarize today",
    instruction="...",
    create_slash_command=True,
    slash_command="/daily"
)

# List slash commands
triggers = registry.list_triggers()

# Get command by slash
cmd = registry.get_by_slash("/daily")
```

**Success Criteria**:
- ✅ Triggers stored in JSON (not JSONL - smaller, less frequent writes)
- ✅ Link slash commands to command IDs
- ✅ Optional: Auto-generate slash from command name
- ✅ Validate slash format (starts with `/`, alphanumeric)
- ✅ Prevent duplicate slashes
- ✅ Human-readable JSON (P1)

**Tests** (target: 15+):
- Add trigger
- Add duplicate trigger → error
- Get command by slash
- List all triggers
- Delete trigger
- Auto-generate slash from name
- Invalid slash format → error
- Orphaned trigger (command deleted) → warning

---

## Phase 2.4: Integration & Documentation

**Time**: 1-2 hours

**Purpose**: Tie everything together and document

**Tasks**:

1. **Integrate with Phase 1**:
   - Add bulletin when command created/modified
   - Session state can reference active command context
   - Registry tracks command-invoking conversations

2. **Command Examples**:
   - Create 3-5 example commands
   - Daily summary
   - Planning session starter
   - System health check
   - Meeting ingestion trigger
   - Bullet
[truncated]
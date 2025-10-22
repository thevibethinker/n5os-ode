# N5-Core Migration Plan

## Goal
Create "N5 Hiring ATS for Zo Computer" - a minimal, focused distribution for hiring/recruitment workflows

## Core Components to Include

### 1. Essential Scripts
- `session_state_manager.py` - Session state tracking
- `n5_safety.py` - Safety and validation
- `n5_schema_validation.py` - Schema validation
- Core utility modules

### 2. Schemas
- `commands.schema.json` - Command structure
- `lists.item.schema.json` - List items
- `lists.registry.schema.json` - List registry
- `index.schema.json` - Index structure
- Core data schemas

### 3. Commands (Hiring-focused)
- List management commands
- Knowledge indexing commands
- Meeting processing commands
- Timeline tracking

### 4. Configuration
- `commands.jsonl` - Command registry
- `settings.example.json` - Configuration template

### 5. Documentation
- Installation guide
- Quick start guide
- Architecture overview
- Command reference

## Excluded (V's personal/company-specific)
- Meeting history/logs
- Personal stakeholder data
- Company-specific workflows
- Session archives
- Backup files

## Directory Structure
```
n5-core/
├── scripts/          # Python scripts
├── commands/         # Command definitions
├── schemas/          # JSON schemas
├── config/           # Configuration files
└── docs/            # Documentation
```

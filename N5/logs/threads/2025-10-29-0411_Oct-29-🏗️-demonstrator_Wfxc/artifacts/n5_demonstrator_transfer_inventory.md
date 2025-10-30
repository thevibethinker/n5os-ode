# N5 Demonstrator Transfer Inventory

**Conversation:** con_tCXwpSWsX28xWfxc  
**Date:** 2025-10-28  
**Purpose:** Inventory of N5OS core functionality to transfer to demonstrators

---

## Components to Transfer

### 1. Command Authoring System
**Location:** `/home/workspace/N5/scripts/author_command/`

**Main Orchestrator:**
- `author-command` - Main CLI wrapper that orchestrates the workflow

**Pipeline Modules (6 chunks):**
- `chunk1_parser.py` - Conversation parser
- `chunk2_scoper.py` - LLM scoping agent
- `chunk3_generator.py` - Command structure generator
- `chunk4_validator.py` - Validation and enhancement layer
- `chunk5_resolver.py` - Conflict resolution engine
- `chunk6_exporter.py` - Safe export and integration handler

**Supporting Modules:**
- `telemetry_collector.py` - Telemetry collection and monitoring
- `security_reviewer.py` - Security validation
- `performance_optimizer.py` - Performance optimization
- `ux_enhancer.py` - UX improvements
- `commands_doc_updater.py` - Documentation updater
- `test_data_generator.py` - Test data generation
- `test_data_complete.py` - Test data validation

**Data Files:**
- `enhancement_timeline.jsonl` - Enhancement tracking

### 2. Documentation Generator (Docgen)
**Location:** `/home/workspace/N5/scripts/n5_docgen.py`

**Recipe:** `/home/workspace/Recipes/Docgen.md`

**Features:**
- Commands mode (`--commands`) - Generate command catalog from recipes.jsonl
- Lists mode (`--lists`) - Generate markdown views from list JSONL files
- All mode (`--all`) - Generate both commands and lists
- Scheduled mode (`--scheduled`) - Run with scheduling wrapper

**Outputs:**
- Command catalog: `N5/commands.md`
- Individual command docs: `N5/commands/*.md`
- List markdown views: `N5/lists/*.md`
- Prefs index updates

### 3. Timeline System
**Scripts:**
- `/home/workspace/N5/scripts/n5_system_timeline.py` - View timeline entries
- `/home/workspace/N5/scripts/n5_system_timeline_add.py` - Add timeline entries
- `/home/workspace/N5/scripts/n5_careerspan_timeline.py` - Careerspan timeline
- `/home/workspace/N5/scripts/n5_careerspan_timeline_add.py` - Careerspan timeline add
- `/home/workspace/N5/scripts/timeline_automation.py` - Timeline automation
- `/home/workspace/N5/scripts/timeline_automation_module.py` - Timeline automation module

**Data:**
- `/home/workspace/N5/config/system-timeline.jsonl` - System timeline data

**Recipes:**
- `/home/workspace/Recipes/System Timeline.md`
- `/home/workspace/Recipes/System Timeline Add.md`
- `/home/workspace/Recipes/Careerspan Timeline.md`
- `/home/workspace/Recipes/Careerspan Timeline Add.md`

**Features:**
- Filter by category, date range, limit
- Multiple output formats (table, json, markdown)
- Manual and automated entry creation
- Impact/status tracking

### 4. Telemetry & Tracking
**Scripts:**
- `/home/workspace/N5/scripts/phase_telemetry_validator.py` - Phase handoff validation
- `/home/workspace/N5/scripts/system_upgrades_telemetry.py` - System upgrades tracking
- `/home/workspace/N5/scripts/author_command/telemetry_collector.py` - Command authoring telemetry

**Features:**
- Execution time tracking
- Success rate monitoring
- Error tracking and categorization
- Component health monitoring
- Resource usage tracking
- Quality gate enforcement (BLOCK/ALLOW/PASS)

### 5. Essential Commands
**Location:** `/home/workspace/Recipes/`

**Command-related Recipes:**
- `Grep Search Command Creation.md` - Command creation workflow
- `Search Commands.md` - Command search functionality
- `Docgen.md` - Documentation generation

**Need to identify:** Which commands are tagged as "essential" in recipes.jsonl

### 6. Essential Workflows
**Identified Workflows:**
- Command authoring workflow (6-chunk pipeline)
- Documentation generation workflow
- Timeline management workflow
- Telemetry validation workflow

**Supporting Scripts:**
- `/home/workspace/N5/scripts/consolidated_workflow.py`
- `/home/workspace/N5/scripts/consolidated_transcript_workflow_v2.py`
- `/home/workspace/N5/scripts/sync_command_workflow.py`
- `/home/workspace/N5/scripts/read_workflow_metadata.py`

### 7. Core Schemas
**Location:** `/home/workspace/N5/schemas/`

**Required Schemas:**
- `command.schema.json` - Command validation schema
- `list.schema.json` - List validation schema
- `index.schema.json` - Index schema

### 8. Core Infrastructure
**Supporting Systems:**
- `/home/workspace/N5/scripts/n5_safety.py` - Safety layer for operations
- `/home/workspace/N5/scripts/session_state_manager.py` - Session state management
- `/home/workspace/N5/scripts/n5_search_commands.py` - Command search
- `/home/workspace/N5/scripts/audit/audit_commands.py` - Command auditing

---

## Next Steps

1. **Verify recipes.jsonl structure** - Check which commands are tagged "essential"
2. **Check demonstrator structure** - Understand target directory structure
3. **Create transfer manifest** - Document exact file mappings
4. **Identify dependencies** - Map all inter-dependencies between components
5. **Create transfer script** - Automated transfer with validation
6. **Documentation** - Create demonstrator-specific docs

---

## Questions to Resolve

1. What is the target directory structure for demonstrators?
2. Are there existing demonstrators to update or creating new ones?
3. What level of customization/configuration needed for demonstrators?
4. Should we include test data or just production components?
5. Do demonstrators need database schemas or just scripts?

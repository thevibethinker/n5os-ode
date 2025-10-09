# N5 OS: Operating System Layer

**N5 OS** is the cognitive operating system that powers V's digital workspace. It contains the commands, scripts, schemas, and configuration that orchestrate operations across Knowledge, Lists, and user workflows.

---

## Directory Structure

```
N5/
├── commands/       # Function files (orchestration prompts)
├── scripts/        # Executable primitives (Python scripts)
├── schemas/        # OS-level schemas and validation
├── config/         # System configuration
├── prefs/          # System preferences and governance
├── runtime/        # Execution logs and traces
└── backups/        # Rolling backups
```

---

## Core Subsystems

### Commands Layer (`commands/`)
Function files that define **how to execute operations**. These are human-readable orchestration instructions that may invoke scripts, compose multiple operations, or operate purely via LLM.

**See**: `commands/README.md` for command catalog

### Scripts Layer (`scripts/`)
Executable Python primitives that perform atomic operations. Scripts are composable building blocks invoked by function files.

**Critical Scripts**:
- `n5_safety.py` - Tiered file protection (imported by all 73 user-facing scripts)
- `incantum_engine.py` - Natural language command dispatcher
- `listclassifier.py` - Intelligent list assignment by content/URL

**See**: `scripts/README.md` for script inventory

### Schemas Layer (`schemas/`)
JSON Schema definitions for OS-level validation. Note: Data-specific schemas (Knowledge, Lists) are distributed to their respective directories for portability.

**See**: `schemas/README.md` for schema documentation

### Config Layer (`config/`)
System configuration files including the command registry.

**Key Files**:
- `commands.jsonl` - Central command registry (44 commands)

**See**: `config/README.md` for configuration details

### Preferences Layer (`prefs/`)
System-wide preferences and governance rules.

**Key Files**:
- `prefs.md` - Global preferences (HARD protection)

**See**: `prefs/README.md` for preference documentation

---

## Architecture Principles

### 1. Command → Function → Script Flow
```
Natural Language (Incantum)
    ↓
Command (trigger phrase)
    ↓
Function File (orchestration prompt)
    ↓
Script(s) [composable, optional]
    ↓
Execution
```

### 2. Tiered Safety
- **HARD**: Manual edit only (prefs.md, architectural principles)
- **MEDIUM**: Validate before edit (lists, knowledge, configs)
- **AUTO**: Regenerate freely (catalogs, indexes, docs)

### 3. Single Source of Truth
- Commands defined once in `commands/`
- Registered in `config/commands.jsonl`
- Indexed in `commands.md` (auto-generated)

### 4. Composable Scripts
Scripts are atomic operations that can be:
- Invoked individually
- Chained by function files
- Tested independently
- Reused across commands

---

## Key Concepts

### Incantum (Natural Language Dispatch)
Users speak naturally → `incantum_engine.py` maps intent → command executes

**Example**:  
"Add Lynnette to must-contact" → `lists-add` → `n5_lists_add.py`

### Direct Processing (LLM-Based Ingestion)
Zo (AI) analyzes documents directly → extracts facts → updates knowledge reservoirs

**No external API calls, no size limits, full context**

### Safety Layer
`n5_safety.py` enforces protection tiers at every write:
- Validates operation against POLICY
- Creates backups before modifications
- Provides dry-run mode
- Logs all operations to audit trail

---

## Getting Started

1. **Entry Point**: `/home/workspace/Documents/N5.md`
2. **Command Catalog**: `N5/commands.md` (auto-generated)
3. **Preferences**: `N5/prefs/prefs.md`
4. **Quick Reference**: `N5/commands/incantum-quickref.md`

---

## Usage Examples

### Execute a Command
```bash
# Via command name
python3 /home/workspace/N5/scripts/n5_command_dispatcher.py lists-add

# Via natural language (Incantum)
"Add an idea: Build AI-powered career coach"
```

### Invoke a Script Directly
```bash
python3 /home/workspace/N5/scripts/n5_lists_health_check.py --verbose
```

### Generate Documentation
```bash
# Command catalog
python3 /home/workspace/N5/scripts/n5_docgen.py

# System index
python3 /home/workspace/N5/scripts/n5_index_rebuild.py
```

---

## Development

### Adding a New Command
1. Create function file: `N5/commands/my-command.md`
2. Register in: `N5/config/commands.jsonl`
3. (Optional) Create script: `N5/scripts/n5_my_command.py`
4. Test execution
5. Update catalog: `docgen`

### Adding a New Script
1. Create script: `N5/scripts/n5_my_script.py`
2. Import safety: `from n5_safety import SafetyValidator`
3. Validate operations through safety layer
4. Document in script docstring
5. Make executable: `chmod +x`

### Updating Schemas
1. Edit schema: `N5/schemas/my-schema.json`
2. Validate with test data
3. Update dependent scripts
4. Document changes in schema README

---

## Command Registry

44 commands currently registered (see `config/commands.jsonl`):

**Categories**:
- **Lists**: add, find, export, health-check, similarity-scanner
- **Knowledge**: add, direct-ingest, sync-analysis
- **System**: docgen, index-rebuild, core-audit, review-workspace
- **Git**: git-check, git-audit
- **Files**: organize-files, conversation-end
- **Jobs**: jobs-find, jobs-add, jobs-analyze
- **[31 more commands]**

**See**: `commands.md` for full catalog with descriptions

---

## Health & Maintenance

### System Health Check
```bash
python3 /home/workspace/N5/scripts/n5_core_audit.py
```

**Validates**:
- Command registry completeness
- Schema compliance
- Broken dependencies
- Protection tier enforcement

### Cleanup Operations
```bash
# Runtime logs (per retention policy)
python3 /home/workspace/N5/scripts/n5_cleanup_runtime.py

# Backups (rolling window)
python3 /home/workspace/N5/scripts/n5_cleanup_backups.py
```

---

## Troubleshooting

**Issue**: Command not found  
**Solution**: Check `config/commands.jsonl` and run `docgen`

**Issue**: Script import errors  
**Solution**: Verify `n5_safety.py` exists and is importable

**Issue**: Schema validation failures  
**Solution**: Check schema version (Draft 2020-12) and required fields

**Issue**: Permission denied  
**Solution**: Verify protection tier in `prefs.md` and use dry-run mode

---

## Related Documentation

- **System Overview**: `/home/workspace/Documents/N5.md`
- **Vision Document**: `/home/workspace/Documents/Archive/2025-10-08-Refactor/Vision.md`
- **Preferences**: `N5/prefs/prefs.md`
- **List Governance**: `/home/workspace/Lists/POLICY.md`

---

*Part of N5 OS - V's Cognitive Operating System*  
*For questions, see system-upgrades.jsonl or contact Zo*

# N5 Config: System Configuration

This directory contains system-wide configuration files for N5 OS.

---

## Files

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

---

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

## Related

- **Commands**: `/home/workspace/N5/commands/`
- **Generated Catalog**: `/home/workspace/N5/commands.md`
- **Dispatcher**: `/home/workspace/N5/scripts/n5_command_dispatcher.py`
- **Incantum Engine**: `/home/workspace/N5/scripts/incantum_engine.py`

---

*Part of N5 OS Configuration Layer*

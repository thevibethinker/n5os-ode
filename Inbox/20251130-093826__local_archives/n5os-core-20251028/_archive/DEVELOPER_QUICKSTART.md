# Developer Quickstart

**Building custom commands and workflows on N5 OS**

---

## Overview

N5 OS is designed for extension. This guide shows you how to create custom commands, workflows, and integrations.

**Time**: 15 minutes  
**Skill Level**: Basic programming (Python preferred)

---

## Prerequisites

1. N5 OS Core installed (`bash bootstrap.sh`)
2. Basic familiarity with Python or shell scripting
3. Text editor or IDE

---

## Your First Custom Command

### Step 1: Read the Workflow (5 min)

```bash
cat N5/commands/command-author.md
```

This shows the complete 2025 workflow for creating commands.

### Step 2: Create Your Command (5 min)

**Example: Create a "project-init" command**

```bash
# 1. Create command doc
cat > N5/commands/project-init.md << 'EOF'
# project-init

**Initialize a new project with N5 OS integration**

## Purpose

Create project directory, README, and N5 tracking.

## Usage

```bash
python3 N5/scripts/n5_project_init.py --name "My Project" --type web
```

## Parameters

- `--name` (required): Project name
- `--type` (optional): Project type (web, data, research)
- `--dry-run`: Preview without creating

## Output

Creates:
- `/Projects/{name}/` directory
- README.md with template
- Adds to N5 project tracking

---
date: '2025-10-27'
category: productivity
priority: medium
EOF

# 2. Create the script
cat > N5/scripts/n5_project_init.py << 'EOF'
#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main(name: str, proj_type: str = "general", dry_run: bool = False) -> int:
    try:
        base = Path("/home/workspace/Projects")
        proj_dir = base / name
        
        if proj_dir.exists():
            logger.error(f"Project already exists: {proj_dir}")
            return 1
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create: {proj_dir}")
            return 0
        
        proj_dir.mkdir(parents=True)
        (proj_dir / "README.md").write_text(f"# {name}\n\nType: {proj_type}\nCreated: {datetime.now().isoformat()}\n")
        
        logger.info(f"✓ Created project: {proj_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--type", default="general")
    parser.add_argument("--dry-run", action="store_true")
    exit(main(parser.parse_args().name, parser.parse_args().type, parser.parse_args().dry_run))
EOF

chmod +x N5/scripts/n5_project_init.py
```

### Step 3: Test It (2 min)

```bash
# Dry run
python3 N5/scripts/n5_project_init.py --name "Test Project" --dry-run

# Real run
python3 N5/scripts/n5_project_init.py --name "Test Project" --type web

# Verify
ls -la Projects/Test\ Project/
```

### Step 4: Register It (3 min)

Add to `N5/config/commands.jsonl`:

```json
{"id": "project-init", "name": "project-init", "description": "Initialize new project", "category": "productivity", "script": "N5/scripts/n5_project_init.py", "doc": "N5/commands/project-init.md"}
```

Rebuild index:

```bash
python3 N5/scripts/n5_index_rebuild.py
```

---

## Development Tools

### Auto-Generate Documentation

```bash
# Generate docs for all commands
python3 N5/scripts/n5_docgen.py --commands

# Generate for your new command
python3 N5/scripts/n5_docgen.py --commands --target project-init
```

### Search Commands

```bash
# Find commands by keyword
python3 N5/scripts/n5_search_commands.py "project"
```

---

## Best Practices

### 1. **Always Include**
- Logging with timestamps
- `--dry-run` flag
- Error handling with try/except
- Exit codes (0 = success, 1+ = error)
- Verification after writes

### 2. **Command Structure**
```python
def main(**kwargs) -> int:
    try:
        validate_inputs()
        result = do_work(dry_run=kwargs.get('dry_run'))
        verify_state(result)
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
```

### 3. **Documentation**
- Purpose: What does it do?
- Usage: Exact command
- Parameters: All options
- Output: What gets created
- Metadata: date, category, priority

---

## Advanced Topics

### Integrating with Lists

```python
from pathlib import Path
import json

def add_to_list(tag: str, data: dict):
    list_file = Path(f"/home/workspace/Lists/{tag}.jsonl")
    with list_file.open("a") as f:
        json.dump({"tag": tag, **data, "date_added": datetime.now().isoformat()}, f)
        f.write("\n")
```

### Using Knowledge Base

```python
def add_to_knowledge(content: str, category: str):
    kb_file = Path(f"/home/workspace/Knowledge/{category}/{filename}.md")
    kb_file.parent.mkdir(parents=True, exist_ok=True)
    kb_file.write_text(content)
```

### Session State

```python
from N5.scripts.session_state_manager import SessionStateManager

state = SessionStateManager(convo_id="con_abc123")
state.update_context("current_project", "My Project")
```

---

## Common Patterns

### 1. **Batch Processing**
```python
for item in items:
    logger.info(f"Processing: {item}")
    process(item)
    if not verify(item):
        logger.error(f"Failed: {item}")
```

### 2. **Configuration Loading**
```python
import json
config = json.loads(Path("N5/config/my_config.json").read_text())
```

### 3. **Safe File Operations**
```python
from pathlib import Path
import shutil

# Backup before modify
if file.exists():
    shutil.copy(file, f"{file}.backup")
    
# Write atomically
temp_file = file.with_suffix(".tmp")
temp_file.write_text(content)
temp_file.rename(file)
```

---

## Troubleshooting

### "Module not found"
```bash
pip install <module>
```

### "Permission denied"
```bash
chmod +x N5/scripts/my_script.py
```

### "Command not in registry"
```bash
python3 N5/scripts/n5_index_rebuild.py
```

---

## Next Steps

1. Read `N5/commands/system-design-workflow.md` for larger systems
2. Explore existing commands in `N5/commands/` for patterns
3. Check `N5/schemas/` for data validation
4. Review `Knowledge/architectural/architectural_principles.md` for design philosophy

---

## Resources

- **Command Workflow**: `N5/commands/command-author.md`
- **Docgen**: `N5/commands/docgen.md`
- **System Design**: `N5/commands/system-design-workflow.md`
- **Examples**: All `N5/commands/*.md` files

---

**Version**: 1.0  
**Date**: 2025-10-27  
**For**: N5 OS Core Developers

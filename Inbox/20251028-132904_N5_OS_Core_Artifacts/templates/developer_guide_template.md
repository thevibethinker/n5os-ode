# N5 OS Core - Developer Guide

## Architecture Overview

N5 follows a modular, file-based architecture with clear separation between:

- **Runtime state** (`config/`) - Active configurations (gitignored)
- **Source templates** (`templates/`) - Version-controlled defaults
- **User preferences** (`prefs/`) - Customizable behavior modules
- **Scripts** (`scripts/`) - Python automation tools
- **Data** (`Lists/`, `Records/`, `Recipes/`) - Content and history

## Design Principles

From `planning_prompt.md`:

1. **Simple Over Easy** - Transparent systems beat clever abstractions
2. **Flow Over Pools** - Process data in streams, not buckets
3. **Maintenance Over Organization** - Living structure beats rigid taxonomy
4. **Code Is Free, Thinking Is Expensive** - 70% design, 20% review, 10% execute
5. **Nemawashi** - Socialize changes before implementation

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/vrijenattawar/zo-n5os-core.git
cd N5

# Install development dependencies (if any)
pip install -r requirements.txt

# Run system audit
python3 scripts/n5_audit.py
```

### Making Changes

1. **Think** (70% of time):
   - Load `Knowledge/architectural/planning_prompt.md`
   - Identify trap doors (irreversible decisions)
   - Design with maintenance in mind

2. **Plan** (20% of time):
   - Document in conversation workspace
   - Socialize with stakeholders
   - Write tests/validation first

3. **Execute** (10% of time):
   - Implement changes
   - Validate against schemas
   - Update documentation

### Component Interfaces

All components must validate against `schemas/index.schema.json`:

```python
# Example: Validating a command registration
import json

def validate_command(command_data):
    # Load schema
    with open('N5/schemas/commands.schema.json') as f:
        schema = json.load(f)
    
    # Validate (implement jsonschema validation)
    # ...
```

### Creating New Scripts

Follow N5 script conventions:

```python
#!/usr/bin/env python3
"""
Script purpose and description.

Usage:
    python3 script_name.py [args]
"""

import argparse
import json
from pathlib import Path

# Constants
N5_ROOT = Path("/home/workspace/N5")
CONFIG_DIR = N5_ROOT / "config"

def main():
    parser = argparse.ArgumentParser(description="Script description")
    # Add arguments
    args = parser.parse_args()
    
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

### Safety Considerations

Before destructive operations:

```python
# Check protection status
result = subprocess.run(
    ["python3", "N5/scripts/n5_protect.py", "check", target_path],
    capture_output=True
)

if result.returncode == 0:
    # Path is protected, require confirmation
    confirm = input("Path protected. Continue? [y/N]: ")
    if confirm.lower() != 'y':
        return
```

### Testing Changes

```bash
# Run system audit
python3 N5/scripts/n5_audit.py

# Validate specific component
python3 N5/scripts/n5_validate.py --component commands

# Test in isolated environment
# (Use conversation workspace for experiments)
```

## Contributing

### Adding New Features

1. **Proposal**: Open GitHub issue describing feature
2. **Design**: Document in conversation workspace
3. **Implementation**: Follow development workflow above
4. **Testing**: Validate against schemas and run audit
5. **Documentation**: Update relevant docs
6. **PR**: Submit with clear description

### Directory Structure for New Components

```
N5/
├── scripts/
│   └── your_component.py          # Implementation
├── schemas/
│   └── your_component.schema.json # Validation schema
├── templates/
│   └── your_component.template    # Default config
└── docs/
    └── your_component.md          # Documentation
```

### Code Style

- **Python**: PEP 8, type hints encouraged
- **Markdown**: GitHub-flavored, consistent headers
- **JSON**: Validated against schemas
- **Comments**: Only when complexity requires explanation

### Commit Conventions

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat(bulletins): add priority levels to bulletin system

- Added priority field to bulletin schema
- Updated bulletins.py to support priority filtering
- Documented in user guide

Closes #42
```

## Extending N5

### Adding New Preference Modules

1. Create file in `N5/prefs/`:
   ```markdown
   # Module Name
   
   Purpose and description.
   
   ## Preferences
   
   - Preference 1: description
   - Preference 2: description
   ```

2. Reference in `N5/prefs/prefs.md`:
   ```markdown
   - Load `file N5/prefs/your_module.md`
   ```

### Creating New Schemas

Follow JSON Schema conventions:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "description": "Field description"
    }
  }
}
```

### Building New Commands

1. Register in `commands.jsonl`:
   ```json
   {"label": "mycommand", "command": "python3 N5/scripts/my_command.py", "description": "What it does"}
   ```

2. Create script following conventions above

3. Test execution:
   ```bash
   python3 N5/scripts/commands.py list
   python3 N5/scripts/my_command.py
   ```

## Distribution

### Preparing Release

1. **Version bump**: Update version in all relevant files
2. **Changelog**: Document changes
3. **Documentation**: Ensure all docs current
4. **Testing**: Full system audit
5. **Tag**: Git tag with version

### Installation Package

Minimal distribution should include:

```
N5/
├── templates/        # All templates
├── schemas/          # All schemas  
├── scripts/          # All scripts
├── docs/             # All documentation
├── prefs/            # Default preferences
└── scripts/n5_install.py  # Installation script
```

Exclude from distribution:
- `config/` (generated during install)
- User-specific content
- `*.pyc`, `__pycache__/`
- `.git/`

## Resources

- **Architecture Principles**: `Knowledge/architectural/planning_prompt.md`
- **Safety Protocol**: `N5/prefs/operations/scheduled-task-protocol.md`
- **Schema Reference**: `N5/schemas/index.schema.json`

## Support

- GitHub Issues: https://github.com/vrijenattawar/zo-n5os-core/issues
- Email: vademonstrator@zo.computer

---

**Next Steps**: Review existing codebase, identify contribution areas, open issues for discussion.

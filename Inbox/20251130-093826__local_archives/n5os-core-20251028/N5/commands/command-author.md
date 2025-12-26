# command-author

**Author new N5 commands with proper structure and documentation**

---

## Overview

Create well-structured, documented commands that integrate with N5 OS.

**Workflow**: System design → Command authoring → Testing → Documentation

---

## Command Structure (2025 Standards)

### Minimal Command File

```markdown
# command-name

**Brief description (one sentence)**

---

## Overview

What this command does and why it exists.

**Category**: system | list | knowledge | workflow  
**Priority**: high | medium | low

---

## Usage

\`\`\`bash
python3 N5/scripts/n5_command_name.py [--arg value]
\`\`\`

---

## Inputs

- `arg1` (required) — Description
- `arg2` (optional) — Description, default: value

---

## Outputs

- Returns/creates: Description
- Side effects: File writes, state changes

---

## Examples

\`\`\`bash
# Example 1: Basic usage
python3 N5/scripts/n5_command_name.py --arg1 "value"

# Example 2: Advanced
python3 N5/scripts/n5_command_name.py --arg1 "value" --arg2 "other"
\`\`\`

---

## Related

- **Commands**: Related commands
- **Scripts**: `N5/scripts/n5_command_name.py`
- **Prefs**: Related preferences if any

---

**Version**: 1.0  
**Last tested**: YYYY-MM-DD
```

---

## Authoring Workflow

### 1. Design Phase (Use system-design-workflow first)

Before creating command:
- Load `file 'Knowledge/architectural/planning_prompt.md'`
- Define: What problem does this solve?
- Identify: Inputs, outputs, side effects
- Consider: Trap doors (irreversible decisions)

### 2. Create Command File

```bash
# Create in N5/commands/
touch N5/commands/new-command.md

# Follow template above
# Use kebab-case for command names
```

### 3. Create Script (if needed)

```bash
# Create in N5/scripts/
touch N5/scripts/n5_new_command.py
chmod +x N5/scripts/n5_new_command.py
```

**Script template**:
```python
#!/usr/bin/env python3
"""
N5 Command: new-command
Description: Brief description
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main(arg1: str, dry_run: bool = False) -> int:
    """Execute command logic."""
    try:
        if dry_run:
            logger.info("[DRY RUN] Would execute with arg1=%s", arg1)
            return 0
        
        # Command logic here
        logger.info("Executing command with arg1=%s", arg1)
        
        # Verify results
        if not verify_state():
            logger.error("Verification failed")
            return 1
            
        logger.info("✓ Command completed successfully")
        return 0
        
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
        return 1

def verify_state() -> bool:
    """Verify command succeeded."""
    # Check: files exist, sizes > 0, valid format
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N5 Command: new-command")
    parser.add_argument("--arg1", required=True, help="Argument 1")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    exit(main(args.arg1, dry_run=args.dry_run))
```

### 4. Register Command

Add to `N5/config/commands.jsonl`:
```json
{
  "name": "new-command",
  "script": "N5/scripts/n5_new_command.py",
  "category": "system",
  "priority": "medium",
  "description": "Brief description",
  "doc": "N5/commands/new-command.md"
}
```

### 5. Test

```bash
# Test dry-run
python3 N5/scripts/n5_new_command.py --arg1 "test" --dry-run

# Test actual execution
python3 N5/scripts/n5_new_command.py --arg1 "test"

# Verify results
# Check logs, outputs, side effects
```

### 6. Document

Update command file with:
- Actual usage examples
- Edge cases discovered
- Related commands
- Last tested date

---

## Quality Standards (2025)

### Required Elements

1. **Single Responsibility** — One clear purpose
2. **Dry-Run Support** — Always preview before execution
3. **Error Handling** — Try/except with logging
4. **State Verification** — Check results after execution
5. **Logging** — INFO for progress, ERROR for failures
6. **Exit Codes** — 0 = success, 1 = failure
7. **Absolute Paths** — Never rely on CWD
8. **Documentation** — Command file with examples

### Anti-Patterns (Avoid)

- ❌ No dry-run mode
- ❌ Silent failures (no logging)
- ❌ Assumes CWD
- ❌ No verification
- ❌ Undocumented arguments
- ❌ Personal hardcoded paths
- ❌ No examples

---

## Categories

- **system** — Infrastructure, maintenance
- **list** — List management
- **knowledge** — Knowledge base operations
- **workflow** — Multi-step processes
- **integration** — External system connections

---

## Related

- **System Design**: `file 'N5/commands/system-design-workflow.md'`
- **Planning Prompt**: `file 'Knowledge/architectural/planning_prompt.md'`
- **Principles**: `file 'Knowledge/architectural/architectural_principles.md'`
- **Command Schema**: `file 'N5/schemas/command.schema.json'`

---

**Version**: 2.0 (2025 Standards)  
**Last Updated**: 2025-10-27  
**Category**: system  
**Priority**: high

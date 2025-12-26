# N5OS Protection System

## Overview

The protection system prevents accidental deletion or modification of critical directories through explicit markers and confirmation workflows.

## How It Works

### Protection Markers

Create a `.protected` file in any directory that should not be moved or deleted without explicit confirmation:

```bash
# Create protection marker
cat > /path/to/directory/.protected << EOF
reason: Contains critical system configurations
created: 2025-11-03
EOF
```

### Protection Levels

**Protected Directory:**
- Requires explicit confirmation before move/delete
- Shows protection reason to user
- Can still be modified (add/edit files within)
- Cannot be bulk-deleted

**Unprotected Directory:**
- Normal file operations apply
- Still subject to dry-run for bulk ops (>5 files)

## Checking Protection

Before any destructive operation, check for protection:

```python
from pathlib import Path

def is_protected(path):
    """Check if directory is protected"""
    path = Path(path)
    
    # Check current directory
    if (path / '.protected').exists():
        return True
    
    # Check parent directories
    for parent in path.parents:
        if (parent / '.protected').exists():
            return True
    
    return False

def get_protection_reason(path):
    """Get reason for protection"""
    path = Path(path)
    protected_file = path / '.protected'
    
    if protected_file.exists():
        content = protected_file.read_text()
        # Parse YAML or simple key:value format
        for line in content.split('\n'):
            if line.startswith('reason:'):
                return line.split('reason:')[1].strip()
    
    return "No reason specified"
```

## Workflow Integration

### Before Destructive Operations

1. **Check Protection**: Scan target path and parents
2. **If Protected**: Display warning with reason
3. **Ask Confirmation**: "This path is protected. Proceed anyway?"
4. **Only If Confirmed**: Execute operation
5. **Log Action**: Record protected path modification

### Bulk Operations

For operations affecting multiple files:

1. **Scan All Targets**: Check each for protection
2. **Report Protected Items**: List all protected paths
3. **Show Dry-Run**: Preview what would be affected
4. **Require Explicit Confirmation**: No default "yes"

## What to Protect

### Critical Directories
- System configuration directories
- Active project roots (while in-progress)
- Irreplaceable data directories
- Backup locations

### Don't Over-Protect
- Temporary directories (Inbox, tmp)
- Archives (already completed)
- Easily reproducible content

## Protection File Format

Simple YAML format:

```yaml
reason: Brief explanation of why protected
created: YYYY-MM-DD
expires: YYYY-MM-DD  # Optional expiration date
notes: |
  Additional context about this protection.
  Can be multi-line.
```

## Example Protections

### Project Directory (Active Work)
```yaml
reason: Active development, contains uncommitted changes
created: 2025-11-03
expires: 2025-12-01
notes: Remove protection when project is completed and committed
```

### System Configuration
```yaml
reason: Core system configuration, breaking this breaks everything
created: 2025-11-03
notes: Only modify with explicit system design approval
```

### Data Repository
```yaml
reason: Irreplaceable source data for analysis
created: 2025-11-03
notes: All transformations should output to separate directories
```

## Temporary Protection

For temporary protection during risky operations:

```bash
# Add temporary protection
echo "reason: Temporary - running risky migration" > .protected

# Remove after operation
rm .protected
```

## Override Mechanism

For emergency situations, provide override flag:

```bash
# Example script with override
python script.py --delete /protected/path --force-unprotected
```

**Warning:** Use override sparingly. It defeats the safety mechanism.

## Best Practices

1. **Protect Early**: Add protection when creating critical directories
2. **Explain Why**: Always include meaningful reason
3. **Review Regularly**: Check protected directories monthly
4. **Remove When Done**: Clean up protection on completed projects
5. **Don't Over-Use**: Too many protections = protection fatigue

## Related Principles

- **P5: Safety, Determinism, Anti-Overwrite** - Never overwrite without confirmation
- **P7: Idempotence and Dry-Run** - Support dry-run for verification
- **P11: Failure Modes and Recovery** - Halt before destructive actions on uncertainty

---

*Protection system is a guardrail, not a prison. Use wisely.*

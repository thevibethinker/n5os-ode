---
build_slug: store-v2
drop_type: tidying
hygiene_check: cleanup
auto_generated: true
---

---
template_type: hygiene_check
hygiene_phase: tidying
auto_fix: true
auto_fix_scope: safe_removals
priority: 5
---

# Cleanup Hygiene Check

## Scope

Removes development artifacts that shouldn't ship:
- Debug logging (console.log, print statements used for debugging)
- Commented-out code blocks (>3 lines)
- Unused variables
- Dead code paths
- Debugging flags left enabled

## Purpose

These artifacts:
- Pollute logs in production
- Add noise to codebase
- May leak sensitive information
- Indicate incomplete cleanup by Drops

## Commands

```bash
BUILD_DIR="N5/builds/${BUILD_SLUG}"
ARTIFACTS_DIR="${BUILD_DIR}/artifacts"

# Debug print statements (Python)
grep -rn "print(" "$ARTIFACTS_DIR" --include="*.py" | grep -v "# keep\|# production\|logger\."

# Debug console statements (JS/TS)
grep -rn "console\.log\|console\.debug\|console\.warn" "$ARTIFACTS_DIR" --include="*.ts" --include="*.js" | grep -v "// keep\|// production"

# Commented-out code blocks (3+ consecutive comment lines that look like code)
grep -Pzo "(#[^\n]*\n){3,}" "$ARTIFACTS_DIR"/*.py 2>/dev/null | grep -E "def |class |import |return |if |for "

# Unused variables (Python - basic detection)
for file in $(find "$ARTIFACTS_DIR" -name "*.py"); do
  python3 -c "
import ast
import sys
with open('$file') as f:
    tree = ast.parse(f.read())
assigned = set()
used = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Store):
            assigned.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            used.add(node.id)
unused = assigned - used - {'_', '__'}
if unused:
    print(f'$file: unused: {unused}')
" 2>/dev/null
done

# Debug flags
grep -rn "DEBUG\s*=\s*True\|VERBOSE\s*=\s*True" "$ARTIFACTS_DIR" --include="*.py" --include="*.ts"
```

## Output Schema

```json
{
  "findings": [
    {
      "type": "debug_print",
      "file": "scripts/main.py",
      "line": 45,
      "content": "print(f\"DEBUG: {data}\")",
      "safe_to_remove": true
    },
    {
      "type": "commented_code",
      "file": "scripts/api.py",
      "start_line": 20,
      "end_line": 28,
      "lines": 9,
      "preview": "# def old_handler(...):\n#     return ...",
      "safe_to_remove": true
    },
    {
      "type": "unused_variable",
      "file": "scripts/utils.py",
      "line": 15,
      "variable": "temp_data",
      "safe_to_remove": true
    },
    {
      "type": "debug_flag",
      "file": "scripts/config.py",
      "line": 8,
      "content": "DEBUG = True",
      "safe_to_remove": false,
      "reason": "May be intentional configuration"
    }
  ],
  "auto_fixable": [
    {
      "type": "debug_print",
      "file": "scripts/main.py",
      "line": 45,
      "fix": "Remove line"
    },
    {
      "type": "commented_code",
      "file": "scripts/api.py",
      "start_line": 20,
      "end_line": 28,
      "fix": "Remove lines 20-28"
    }
  ],
  "requires_review": [
    {
      "type": "debug_flag",
      "severity": "medium",
      "issue": "DEBUG flag set to True",
      "recommendation": "Verify this should be False for production"
    }
  ],
  "summary": {
    "total_findings": 12,
    "auto_fixed": 8,
    "requires_review": 4,
    "lines_removed": 23
  }
}
```

## Auto-Fix Rules

**auto_fix: true** (for safe removals)

Safe to auto-fix:
- `debug_print` → Remove line (unless marked `# keep` or `# production`)
- `console.log` → Remove line (unless marked `// keep` or `// production`)
- `commented_code` → Remove block (>3 lines of commented code-like content)
- `unused_variable` → Remove assignment (only if never read)

Do NOT auto-fix:
- `debug_flag` → May be intentional configuration
- Print statements in `if __name__ == "__main__":` blocks
- Logging to actual logger objects (`logger.debug()`, etc.)
- Variables starting with `_` (intentionally unused)
- Comments that look like documentation, not code

## Auto-Fix Implementation

```python
def auto_fix_debug_cleanup(file_path, findings):
    """Remove debug artifacts from file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Sort by line number descending to preserve indices
    to_remove = sorted(
        [f for f in findings if f['safe_to_remove']],
        key=lambda x: x.get('end_line', x['line']),
        reverse=True
    )
    
    for finding in to_remove:
        if 'end_line' in finding:
            # Block removal
            del lines[finding['start_line']-1:finding['end_line']]
        else:
            # Single line removal
            del lines[finding['line']-1]
    
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    return len(to_remove)
```

## Escalation Triggers

- DEBUG/VERBOSE flag enabled → Escalate for confirmation
- >20 debug statements → Escalate (may indicate logging strategy issue)
- Unused variable in function signature → Escalate (interface issue)
- Commented code with TODO → Escalate (deferred work)

## Preservation Markers

Lines with these markers are NEVER removed:
- `# keep` / `// keep`
- `# production` / `// production`
- `# intentional` / `// intentional`
- `# noqa`


## Build Context
- **Build Slug**: store-v2
- **Build Dir**: N5/builds/store-v2

## Deposit Location
Write your deposit to: N5/builds/store-v2/deposits/T-cleanup.json

## Required Deposit Schema
```json
{
  "drop_id": "T-cleanup",
  "build_slug": "store-v2",
  "check_type": "cleanup",
  "findings": [...],
  "auto_fixable": [...],
  "requires_review": [...],
  "health_contribution": 0.0-1.0
}
```

---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W3_context_files
status: complete
dependencies: []
---
# Worker Assignment: W3_context_files

**Project:** n5os-ode-release-fix  
**Component:** missing_context_files  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 60 minutes

---

## Objective

Create 7 missing files referenced in `N5/prefs/context_manifest.yaml` that cause `n5_load_context.py` to fail or produce incomplete loads.

---

## Context

The context loading system references files that don't exist in the export. These need to be created as functional stubs that provide real value, not just empty placeholders.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`

---

## Tasks

### Task 1: Create Operations Directory and Files

First, create the directories if they don't exist:
```bash
mkdir -p N5/export/n5os-ode/N5/prefs/operations
mkdir -p N5/export/n5os-ode/N5/prefs/communication
```

#### 1a: Create `N5/prefs/operations/planning_prompt.md`

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Planning Prompt Template

Use this template when planning builds, research, or multi-step work.

## Planning Principles

1. **Scope First** — Define boundaries before diving in
2. **Dependencies Explicit** — Map what blocks what
3. **Exit Criteria Clear** — Know when you're done
4. **Reversibility Considered** — Plan rollback paths

## Planning Template

### Objective
[One sentence: what are we trying to achieve?]

### Scope
- **In scope:** [what's included]
- **Out of scope:** [what's explicitly excluded]

### Approach
1. Step 1
2. Step 2
3. Step 3

### Dependencies
- [ ] Dependency 1
- [ ] Dependency 2

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| - | - | - | - |

### Time Estimate
[X hours/days]
```

#### 1b: Create `N5/prefs/operations/scheduled-task-protocol.md`

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Scheduled Task Protocol

Guidelines for creating and managing scheduled agents/tasks.

## Principles

1. **Idempotent by Default** — Tasks should be safe to run multiple times
2. **Fail Gracefully** — Handle errors without crashing the scheduler
3. **Log Everything** — State changes must be traceable
4. **Minimal Blast Radius** — Scope tasks narrowly

## Task Categories

| Category | Frequency | Examples |
|----------|-----------|----------|
| Maintenance | Daily | Cleanup, backups, health checks |
| Sync | Hourly+ | External API syncs, email checks |
| Reports | Weekly | Summaries, digests, reviews |
| Triggers | Event-based | Webhooks, file watchers |

## Best Practices

### DO
- Use explicit RRULE syntax
- Include timeout limits
- Write to specific output paths
- Check preconditions before acting

### DON'T
- Run destructive operations without confirmation
- Send emails without explicit user request
- Modify files outside designated areas
- Create unbounded loops

## Template

```
RRULE: FREQ=DAILY;BYHOUR=9;BYMINUTE=0
Instruction: [Clear, actionable command with stop condition]
Delivery: email | sms | none
```
```

#### 1c: Create `N5/prefs/communication/style-guide.md`

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Communication Style Guide

Guidelines for AI-generated content tone and formatting.

## Voice Principles

1. **Direct** — Lead with the point, not preamble
2. **Specific** — Concrete details over vague summaries  
3. **Actionable** — Clear next steps when relevant
4. **Human** — Conversational, not robotic

## Formatting Standards

### Headers
- Use sentence case: "Meeting summary" not "Meeting Summary"
- Max 3 levels deep (H1 → H2 → H3)

### Lists
- Bulleted for unordered items
- Numbered for sequences or ranked items
- Max 7±2 items before grouping

### Emphasis
- **Bold** for key terms and actions
- *Italics* for titles and technical terms
- `Code` for file paths, commands, variable names

## Content Types

### Summaries
- Lead with the single most important point
- 3-5 bullet points max for key details
- End with clear next action if applicable

### Emails
- Subject: [Action verb] + [Object] + [Context]
- Body: Context → Ask → Supporting details
- Keep under 200 words when possible

### Reports
- Executive summary first
- Details in collapsible sections
- Data in tables, not prose
```

---

### Task 2: Create n5_safety.py Script

Create `/home/workspace/N5/export/n5os-ode/N5/scripts/n5_safety.py`:

```python
#!/usr/bin/env python3
"""N5OS-Ode Safety Validation Script.

Validates operations against safety rules before execution.
Used by destructive operations to prevent accidental damage.

Usage:
    python3 N5/scripts/n5_safety.py check <operation> <path>
    python3 N5/scripts/n5_safety.py audit
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

__version__ = "1.0.0"
REPO_URL = "https://github.com/vrijenattawar/n5os-ode"

# Protected paths that require extra confirmation
PROTECTED_PATHS = [
    "N5/prefs/",
    "N5/scripts/",
    "Knowledge/",
    "Lists/",
]

# Operations that require safety checks
DANGEROUS_OPS = ["delete", "move", "bulk_edit", "truncate"]


def check_operation(operation: str, path: str) -> dict:
    """Check if an operation on a path is safe."""
    result = {
        "operation": operation,
        "path": path,
        "safe": True,
        "warnings": [],
        "requires_confirmation": False,
    }
    
    path_obj = Path(path)
    
    # Check if path is protected
    for protected in PROTECTED_PATHS:
        if path.startswith(protected) or protected in path:
            result["warnings"].append(f"Path is in protected area: {protected}")
            result["requires_confirmation"] = True
    
    # Check if operation is dangerous
    if operation in DANGEROUS_OPS:
        result["warnings"].append(f"Operation '{operation}' is flagged as dangerous")
        result["requires_confirmation"] = True
    
    # Check for .n5protected marker
    check_path = path_obj
    while check_path != check_path.parent:
        if (check_path / ".n5protected").exists():
            result["safe"] = False
            result["warnings"].append(f"Path protected by .n5protected at {check_path}")
            break
        check_path = check_path.parent
    
    return result


def run_audit() -> dict:
    """Audit the workspace for safety configuration."""
    workspace = Path("/home/workspace")
    audit = {
        "timestamp": datetime.now().isoformat(),
        "protected_markers": [],
        "unsafe_patterns": [],
    }
    
    # Find all .n5protected files
    for marker in workspace.rglob(".n5protected"):
        audit["protected_markers"].append(str(marker.parent))
    
    return audit


def main():
    parser = argparse.ArgumentParser(
        description="N5OS-Ode Safety Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if operation is safe")
    check_parser.add_argument("operation", help="Operation type (delete, move, etc.)")
    check_parser.add_argument("path", help="Path to check")
    
    # audit command
    subparsers.add_parser("audit", help="Audit workspace safety configuration")
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = check_operation(args.operation, args.path)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["safe"] else 1)
    
    elif args.command == "audit":
        result = run_audit()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

---

### Task 3: Create JSON Schema

Create `/home/workspace/N5/export/n5os-ode/N5/schemas/index.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/vrijenattawar/n5os-ode/schemas/index.schema.json",
  "title": "N5OS-Ode Index Schema",
  "description": "Schema for N5OS-Ode index files that track workspace contents",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "description": "Schema version"
    },
    "generated": {
      "type": "string",
      "format": "date-time",
      "description": "When the index was generated"
    },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "Relative path from workspace root"
          },
          "type": {
            "type": "string",
            "enum": ["file", "directory"],
            "description": "Entry type"
          },
          "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Classification tags"
          },
          "last_modified": {
            "type": "string",
            "format": "date-time"
          }
        },
        "required": ["path", "type"]
      }
    }
  },
  "required": ["version", "entries"]
}
```

---

### Task 4: Create Knowledge/architectural/principles.md

First create directory: `mkdir -p Knowledge/architectural`

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# N5OS-Ode Architectural Principles

Core principles guiding the design and evolution of N5OS-Ode.

## 1. Files as Truth

The filesystem is the source of truth. Databases are indexes, not masters.
- Markdown files are human-readable and git-friendly
- Binary formats avoided where possible
- Every important state is recoverable from files alone

## 2. Prompts as Programs

Prompts are first-class citizens, not afterthoughts.
- `.prompt.md` files are executable procedures
- Prompts compose like functions
- Context flows through prompt chains explicitly

## 3. Minimal Dependencies

Fewer dependencies = fewer breakage points.
- Prefer stdlib over external packages
- When external packages required, document explicitly
- No hidden runtime requirements

## 4. Graceful Degradation

Missing components shouldn't crash the system.
- Optional features fail silently with warnings
- Core functionality works with minimal setup
- Clear error messages guide resolution

## 5. Human in the Loop

AI assists but humans decide.
- Destructive operations require confirmation
- Important outputs staged for review
- No autonomous actions on external systems

## 6. State Transparency

Know what state you're in.
- SESSION_STATE.md tracks conversation progress
- Manifest files track processing state
- Git tracks everything else
```

---

### Task 5: Create Lists/POLICY.md

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Lists Policy

Guidelines for managing lists in N5OS-Ode.

## Single Source of Truth (SSOT)

Each list has ONE canonical location. Copies are indexes, not sources.

## List Locations

| List Type | Location | Format |
|-----------|----------|--------|
| Tasks | Akiflow (external) | — |
| Prompts | `/Prompts/` | `.prompt.md` |
| Scripts | `/N5/scripts/` | `.py` |
| Knowledge | `/Knowledge/` | `.md` |

## List Operations

### Adding Items
1. Identify the correct list location
2. Check for duplicates
3. Add with proper formatting
4. Update any dependent indexes

### Removing Items  
1. Check for dependencies
2. Archive if valuable, delete if not
3. Update indexes

### Moving Items
1. Copy to new location first
2. Update references
3. Remove from old location
4. Verify nothing broken

## Naming Conventions

- Lowercase with hyphens: `my-list-item.md`
- Descriptive but concise
- Include date prefix for temporal items: `2026-01-15_meeting-notes.md`
```

---

## Verification

After creating all files:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. All directories exist
test -d N5/prefs/operations && echo "PASS: operations dir"
test -d N5/prefs/communication && echo "PASS: communication dir"
test -d N5/schemas && echo "PASS: schemas dir"
test -d Knowledge/architectural && echo "PASS: Knowledge/architectural dir"

# 2. All files exist
test -f N5/prefs/operations/planning_prompt.md && echo "PASS"
test -f N5/prefs/operations/scheduled-task-protocol.md && echo "PASS"
test -f N5/prefs/communication/style-guide.md && echo "PASS"
test -f N5/scripts/n5_safety.py && echo "PASS"
test -f N5/schemas/index.schema.json && echo "PASS"
test -f Knowledge/architectural/principles.md && echo "PASS"
test -f Lists/POLICY.md && echo "PASS"

# 3. Python compiles
python3 -m py_compile N5/scripts/n5_safety.py && echo "PASS: n5_safety.py compiles"

# 4. JSON is valid
python3 -c "import json; json.load(open('N5/schemas/index.schema.json'))" && echo "PASS: JSON valid"
```

---

## Handoff

When complete:
1. Report: "W3_context_files complete. Created 7 files across 4 directories."
2. List all files created with paths
3. Show verification output
4. Do NOT commit yet - W6 will handle all commits

---

## Files to Create (Summary)

1. `N5/prefs/operations/planning_prompt.md`
2. `N5/prefs/operations/scheduled-task-protocol.md`
3. `N5/prefs/communication/style-guide.md`
4. `N5/scripts/n5_safety.py`
5. `N5/schemas/index.schema.json`
6. `Knowledge/architectural/principles.md`
7. `Lists/POLICY.md`



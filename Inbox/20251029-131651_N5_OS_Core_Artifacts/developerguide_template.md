# N5 Developer Guide

**Version:** 0.1  
**Last Updated:** 2025-10-28

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Philosophy](#design-philosophy)
3. [Core Components](#core-components)
4. [Extension Points](#extension-points)
5. [Contributing](#contributing)
6. [Testing](#testing)

---

## Architecture Overview

### System Design

N5 is built on **flow-based architecture** where information moves through time-bounded stages rather than pooling in static storage.

```
Entry → Triage → Processing → Exit
  ↓        ↓          ↓         ↓
Inbox   Records   Knowledge   Archive/Delete
```

### Design Principles (Priority Order)

1. **Simple Over Easy** - Disentangled systems beat convenient complexity
2. **Flow Over Pools** - Time-bounded stages, not static storage
3. **Maintenance Over Organization** - Self-maintaining systems
4. **Code Is Free, Thinking Is Expensive** - 70% planning, 20% review, 10% execution
5. **Nemawashi** - Explore 2-3 alternatives before deciding

Full principles: `Knowledge/architectural/planning_prompt.md`

### Technology Stack

- **Runtime:** Python 3.12+
- **Database:** SQLite (single-user, portable)
- **Data Formats:** Markdown, JSON, JSONL
- **AI Integration:** Zo Computer platform APIs

---

## Design Philosophy

### Think → Plan → Execute

**THINK Phase (70% of time)**
- What am I building and why?
- What are the alternatives?
- What are the trap doors (irreversible decisions)?
- Is this simple or just easy?

**PLAN Phase**
- Write prose specification
- Define success criteria
- Map information flows
- Document assumptions

**EXECUTE Phase (10% of time)**
- Generate code from plan
- Move fast, don't break things

**REVIEW Phase (20% of time)**
- Test in production conditions
- Verify error paths
- Fresh thread test (can someone else understand this?)

### Trap Doors vs. Trade-offs

**Trap Door** = Irreversible or high-cost-to-reverse decision
- Database technology
- File format choices
- Core API design
→ SLOW DOWN. Explore alternatives. Get input.

**Trade-off** = Reversible choice with pros/cons
- Script language
- Directory structure
- Variable naming
→ Document decision, move forward, iterate.

---

## Core Components

### 1. Session State Manager

**Location:** `N5/scripts/session_state_manager.py`

**Purpose:** Tracks conversation context, objectives, and progress.

**Key Functions:**
```python
init(convo_id, conversation_type, load_system=False)
update(convo_id, field, value)
get(convo_id)
```

**Database Schema:**
```sql
CREATE TABLE conversations (
    convo_id TEXT PRIMARY KEY,
    type TEXT,
    mode TEXT,
    focus TEXT,
    objective TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

**Extension Point:** Add custom fields to schema for domain-specific tracking.

### 2. Command System

**Location:** `N5/commands/` (markdown) → `N5/config/commands.jsonl` (compiled)

**Command Structure:**
```markdown
---
name: command-name
category: list-management
triggers:
  - /trigger1
  - /trigger2
---

# Command Name

## Description
What this command does.

## Parameters
- param1: Description
- param2: Description

## Implementation
Script or workflow to execute.
```

**Compilation:**
```bash
python3 N5/scripts/command_compiler.py
```

**Extension Point:** Add custom commands by creating new markdown files in `N5/commands/`.

### 3. List Management

**Location:** `Lists/*.md`

**Structure:**
```markdown
# List Name

- [ ] Item 1 (added: 2025-10-28T10:00:00Z)
- [x] Item 2 (added: 2025-10-27T09:00:00Z, completed: 2025-10-28T11:00:00Z)
```

**Operations:**
```python
# N5/scripts/n5_lists_add.py
add_item(list_name, item_text)
complete_item(list_name, item_text)
list_items(list_name, filter="active")
```

**Extension Point:** Custom list types, auto-routing rules, SLA tracking.

### 4. Knowledge Base

**Location:** `Knowledge/`

**Index Schema:**
```json
{
  "path": "Knowledge/architectural/P01-human-readable.md",
  "kind": "doc",
  "tags": ["principle", "architecture"],
  "summary": "Code and configs must be human-readable",
  "updated_at": "2025-10-28T10:00:00Z"
}
```

**Search:**
```python
# N5/scripts/knowledge_search.py
search(query, tags=[], kind=[])
```

**Extension Point:** Vector embeddings for semantic search, auto-tagging, link analysis.

### 5. Records Processing

**Location:** `Records/Company/`, `Records/Personal/`, `Records/Temporary/`

**Lifecycle:**
1. Create record with metadata
2. Process through stages (configurable per type)
3. Archive or promote to Knowledge after completion

**Metadata:**
```json
{
  "record_id": "rec_ABC123",
  "type": "stakeholder",
  "created_at": "2025-10-28T10:00:00Z",
  "stage": "processing",
  "sla_expires": "2025-11-04T10:00:00Z"
}
```

**Extension Point:** Custom record types, stage definitions, SLA rules.

---

## Extension Points

### Adding Custom Commands

1. Create markdown file in `N5/commands/`:
```markdown
---
name: my-custom-command
category: custom
triggers:
  - /mycmd
---

# My Custom Command

## Description
Does something useful.

## Implementation
python3 N5/scripts/my_script.py
```

2. Recompile commands:
```bash
python3 N5/scripts/command_compiler.py
```

3. Test:
```bash
/mycmd --dry-run
```

### Adding Custom Scripts

**Template:**
```python
#!/usr/bin/env python3
import argparse, logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False) -> int:
    try:
        if not validate_inputs():
            return 1
        result = do_work(dry_run=dry_run)
        if not verify_state(result):
            return 1
        logger.info(f"✓ Complete: {result}")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def do_work(dry_run: bool = False) -> dict:
    if dry_run:
        logger.info("[DRY RUN]")
        return {"status": "dry-run"}
    # Actual work here
    return {"status": "complete"}

def verify_state(result: dict) -> bool:
    # Verify writes succeeded
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    exit(main(dry_run=parser.parse_args().dry_run))
```

**Required Elements:**
- Logging (ISO 8601 timestamps)
- `--dry-run` flag
- Error handling with context
- State verification after writes
- Exit codes (0=success, 1=error)

### Adding Custom Schemas

1. Create schema in `N5/schemas/`:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://n5.local/schemas/my-type.schema.json",
  "title": "My Custom Type",
  "type": "object",
  "required": ["field1"],
  "properties": {
    "field1": {"type": "string"},
    "field2": {"type": "integer"}
  }
}
```

2. Update index schema reference in `N5/schemas/index.schema.json`

3. Validate:
```python
import jsonschema
schema = json.load(open("N5/schemas/my-type.schema.json"))
jsonschema.validate(instance=data, schema=schema)
```

### Integrating External Services

**Pattern:**
```python
# N5/scripts/integrations/service_name.py
class ServiceIntegration:
    def __init__(self, config):
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
    
    def fetch_data(self, params):
        # API call with error handling
        pass
    
    def sync_to_n5(self, data):
        # Transform and store in appropriate N5 location
        pass
```

**Configuration:** Store credentials in `N5/config/integrations.json` (gitignored)

---

## Contributing

### Setup Development Environment

1. Fork repository
2. Clone locally
3. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Run tests:
```bash
pytest N5/tests/
```

### Contribution Guidelines

1. **Load planning prompt** before significant work:
   ```
   Read Knowledge/architectural/planning_prompt.md
   ```

2. **Follow Think→Plan→Execute**:
   - Write specification first
   - Get feedback on design
   - Implement with tests
   - Review in production conditions

3. **Adhere to principles:**
   - Simple over easy
   - Flow over pools
   - Error handling always
   - State verification after writes

4. **Pull Request Requirements:**
   - Tests pass
   - Documentation updated
   - Principle compliance check
   - Fresh thread test (clear to new reader?)

### Code Review Checklist

- [ ] Follows script template (logging, dry-run, error handling)
- [ ] All writes verified
- [ ] Production config tested
- [ ] Error paths tested
- [ ] Documentation complete
- [ ] No invented API limits
- [ ] Principle-compliant

---

## Testing

### Unit Tests

```python
# N5/tests/test_session_state.py
import pytest
from N5.scripts.session_state_manager import SessionStateManager

def test_init_session():
    manager = SessionStateManager(":memory:")
    result = manager.init("con_TEST", "build")
    assert result["convo_id"] == "con_TEST"
    assert result["type"] == "build"
```

### Integration Tests

```python
# N5/tests/test_list_workflow.py
def test_full_list_workflow(tmp_path):
    # Setup
    list_file = tmp_path / "inbox.md"
    
    # Add item
    add_item("inbox", "Test item")
    
    # Verify
    items = list_items("inbox")
    assert len(items) == 1
    
    # Complete
    complete_item("inbox", "Test item")
    
    # Verify
    items = list_items("inbox", filter="active")
    assert len(items) == 0
```

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest N5/tests/test_session_state.py

# With coverage
pytest --cov=N5 --cov-report=html
```

---

## Appendix: Architectural Principles Index

Located in `Knowledge/architectural/principles/`:

- **P0:** Rule-of-Two (max 2 config files in context)
- **P1:** Human-Readable (no binary configs)
- **P2:** Single Source of Truth
- **P5:** Anti-Overwrite Protection
- **P7:** Dry-Run First
- **P8:** Minimal Context
- **P11:** Explicit Failure Modes
- **P15:** Complete Before Claiming
- **P16:** No Invented API Limits
- **P17:** Test Production Config
- **P18:** Verify State After Writes
- **P19:** Error Handling Always
- **P20:** Modular Over Monolithic
- **P21:** Document Assumptions
- **P22:** Language Selection (Python default, Shell for glue, Node for APIs)

Full principles: `Knowledge/architectural/architectural_principles.md`

---

**Questions?** Open a discussion at [GitHub](https://github.com/[org]/n5-os-core/discussions)

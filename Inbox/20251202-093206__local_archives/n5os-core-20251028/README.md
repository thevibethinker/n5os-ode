# N5 OS Core

**Personal operating system for AI-assisted productivity**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is N5?

N5 is a **foundation for building personal AI systems**. It provides:

- 📚 **Architecture** - 34 battle-tested design principles
- 🛠️ **Scripts** - Core utilities for conversation, workspace, session management  
- 🎯 **Recipes** - Reusable workflow templates
- 🧠 **Intelligence** - Patterns for organizing knowledge and actions
- 🔒 **Safety** - Built-in checks for overwrites, deletions, credential leaks

Think of it as **Linux for your AI workspace** - a minimal, composable foundation you can build on.

---

## Quick Start

### 1. Clone the Repo

```bash
cd /home/workspace
git clone https://github.com/vrijenattawar/n5os-core.git
mv n5os-core/* .
```

### 2. Explore the Foundation

```bash
# Read the philosophy
cat Knowledge/architectural/starter_planning_prompt.md

# Browse principles
ls Knowledge/architectural/principles/

# Check out recipe examples
ls Recipes/
```

### 3. Use Core Scripts

```bash
# Initialize conversation session
python3 N5/scripts/session_state_manager.py init --convo-id test --type build

# Run pre-commit safety check
python3 N5/scripts/n5_git_check.py

# Export conversation thread
python3 N5/scripts/n5_thread_export.py
```

---

## What's Included

### Core Scripts (26 total)

**Session Management:**
- `session_state_manager.py` - Track conversation state
- `conversation_registry.py` - Conversation database
- `spawn_worker.py` - Background task spawning

**Workspace:**
- `n5_workspace_maintenance.py` - Cleanup automation
- `n5_workspace_root_cleanup.py` - Root directory organization

**Safety:**
- `n5_git_check.py` - Pre-commit audit
- `n5_safety.py` - Safety utilities
- `hygiene_preflight.py` - Pre-operation checks

**Knowledge & Lists:**
- `n5_knowledge_add.py` - Ingest to knowledge base
- `n5_lists_add.py` - Add to action lists
- `n5_lists_health_check.py` - List integrity validation

**Conversation:**
- `n5_conversation_end.py` - Formal conversation closure
- `n5_thread_export.py` - AAR generation
- `n5_convo_list.py` - List conversations
- `n5_convo_search.py` - Search conversations

**Index & Search:**
- `n5_index_rebuild.py` - Rebuild search index
- `n5_index_update.py` - Incremental updates
- `n5_search_commands.py` - Command search

**Docs & Validation:**
- `n5_docgen.py` - Generate documentation
- `n5_config_validator.py` - Validate configs
- `n5_placeholder_scan.py` - Detect TODOs/FIXMEs

### Architectural Principles (34 total)

**Design Philosophy:**
- P24: Simulation Over Doing
- P25: Code Is Free, Thinking Is Expensive
- P27: Nemawashi Mode (explore alternatives)
- P32: Simple Over Easy

**Safety & Quality:**
- P5: Anti-Overwrite
- P7: Dry-Run Everything
- P15: Complete Before Claiming
- P16: No Invented Limits
- P19: Error Handling
- P34: Secrets Management

**See:** `Knowledge/architectural/principles/` for all 34

### Recipe Examples (2 included)

- **conversation-end.md** - Formal conversation closure workflow
- **git-check.md** - Pre-commit safety audit

### Planning Framework

- **starter_planning_prompt.md** - Think → Plan → Execute methodology
- **architectural_principles.md** - Complete principle index

---

## Philosophy

### Think → Plan → Execute

Spend **70% of time thinking and planning**, not writing code:

1. **Think (40%)**: What are we building? Why? What are the trap doors?
2. **Plan (30%)**: Write specification in prose
3. **Execute (10%)**: Generate code from plan
4. **Review (20%)**: Test against plan

### Simple Over Easy

**Simple** = few intertwined concepts (objective)  
**Easy** = familiar, convenient (subjective)

Choose simple. Always.

```python
# Easy but complex (6 braided concepts)
df.groupby(['cat', 'date']).agg({'val': ['sum', 'mean']}).reset_index()

# Simple and clear (3 independent concepts)
totals = {}
for record in records:
    key = (record['cat'], record['date'])
    totals[key] = sum(record['val'] for r in records if matches(r, key))
```

### Code Is Free

Writing code costs nothing. Thinking, debugging, and maintaining code is expensive.

**Optimize for understanding, not keystrokes.**

---

## Directory Structure

```
n5os-core/
├── Knowledge/
│   └── architectural/
│       ├── starter_planning_prompt.md
│       ├── architectural_principles.md
│       └── principles/              # 34 principles
├── N5/
│   ├── commands/                    # Command definitions
│   ├── config/                      # Configuration files
│   ├── prefs/                       # Operational preferences
│   ├── scripts/                     # 26 core scripts
│   └── schemas/                     # JSON schemas
├── Lists/                           # Action tracking
├── Recipes/                         # Workflow templates
│   ├── conversation-end.md
│   └── git-check.md
├── Documents/
│   └── N5.md                        # System overview
└── README.md                        # This file
```

---

## Use Cases

### Personal Knowledge Management
- Organize notes into `Knowledge/`
- Track actions in `Lists/`
- Process raw data through `Records/`

### AI-Assisted Development
- Use principles to guide AI code generation
- Apply recipes for common workflows
- Maintain session state across conversations

### Team Collaboration
- Share architectural principles
- Standardize workflows via recipes
- Enforce safety checks with git hooks

---

## Integration

### Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 N5/scripts/n5_git_check.py
exit $?
```

```bash
chmod +x .git/hooks/pre-commit
```

### AI System Prompt

```markdown
At conversation start, load:
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'
- file 'Knowledge/architectural/starter_planning_prompt.md'
```

---

## Extending N5

### Add Your Own Recipes

```markdown
---
description: |
  Your workflow description
tags:
  - your-tag
---

# Your Recipe

## What This Does
...

## Implementation Pattern
...
```

### Add Custom Scripts

Follow patterns in `N5/scripts/`:
- Python 3.12+
- Argparse CLI
- Logging to stdout
- Exit codes (0=success, 1=error)
- Dry-run support

### Add Principles

Document your own architectural decisions:

```markdown
# P35: Your Principle

**Category:** Design/Safety/Process  
**Priority:** Critical/High/Medium

## Principle
One-sentence statement

## Pattern
How to apply it

## Examples
Concrete examples
```

---

## Contributing

This is a personal foundation meant to be forked and customized. However:

- Bug fixes welcome
- Core script improvements welcome
- New universal principles welcome
- Domain-specific additions: fork and customize

---

## License

MIT License - See LICENSE file

---

## Learn More

- 📖 **System Overview:** `Documents/N5.md`
- 🧠 **Planning Framework:** `Knowledge/architectural/starter_planning_prompt.md`
- 🎯 **All Principles:** `Knowledge/architectural/architectural_principles.md`
- 🛠️ **Recipe Examples:** `Recipes/`

---

## Version

**2.0** (2025-10-26)

Core foundation with architectural principles, recipes system, and essential scripts.

---

**Built for:** Zo Computer (https://zo.computer)  
**Maintained by:** V (@vrijenattawar)

## Build Orchestrator

**The secret weapon for complex system builds.**

Instead of one long AI conversation doing everything sequentially, the Build Orchestrator spawns multiple focused AI workers executing tasks in parallel:

```
Orchestrator
├── Worker 1: Database Schema (20 min)
├── Worker 2: API Layer (30 min, after W1)
├── Worker 3: CLI Interface (20 min, parallel with W4)
├── Worker 4: Tests (20 min, parallel with W3)
└── Integration & Validation
```

**Benefits:**
- ⚡ 20-40% faster for multi-component builds
- 🔒 Worker isolation (no conflicts)
- 📊 Full audit trail in SQLite
- 🔄 Resumable orchestration
- 📦 Reusable worker briefs

**Read more:** file 'Documents/BUILD_ORCHESTRATOR.md'

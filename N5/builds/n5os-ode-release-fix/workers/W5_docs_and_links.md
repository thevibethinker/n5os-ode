---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_oaJd6YmS7ETcg4UZ
worker_id: W5_docs_and_links
status: complete
dependencies: []
---
# Worker Assignment: W5_docs_and_links

**Project:** n5os-ode-release-fix  
**Component:** documentation_and_links  
**Orchestrator:** con_oaJd6YmS7ETcg4UZ  
**Estimated time:** 45 minutes

---

## Objective

Fix broken links in prefs.md and create missing documentation files (LICENSE, ARCHITECTURE, CONTRIBUTING, N5/README).

---

## Context

The `N5/prefs/prefs.md` file has broken relative links, and several documentation files expected by the project don't exist.

**Working directory:** `/home/workspace/N5/export/n5os-ode/`

---

## Tasks

### Task 1: Fix Broken Links in prefs.md

Edit `N5/prefs/prefs.md` to fix these broken links:

| Current Link | Problem | Fix |
|--------------|---------|-----|
| `(../README.md)` | Points to wrong level | `(../../README.md)` |
| `(../docs/ARCHITECTURE.md)` | File doesn't exist | `(../docs/ARCHITECTURE.md)` (create the file) |
| `(../docs/CONTRIBUTING.md)` | File doesn't exist | `(../docs/CONTRIBUTING.md)` (create the file) |

Read the file first to find all links and verify the fixes.

### Task 2: Create LICENSE File

Create `/home/workspace/N5/export/n5os-ode/LICENSE`:

```
MIT License

Copyright (c) 2026 Vrijen Attawar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Task 3: Create N5/docs/ARCHITECTURE.md

First check if `N5/docs/` exists, create if not: `mkdir -p N5/docs`

Create `/home/workspace/N5/export/n5os-ode/N5/docs/ARCHITECTURE.md`:

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# N5OS-Ode Architecture

High-level architecture of the N5OS-Ode personal operating system layer.

## Overview

N5OS-Ode is a file-based personal operating system that runs on top of Zo Computer. It provides:

- **Structured Prompts** — Reusable workflows as `.prompt.md` files
- **Context Loading** — Dynamic context injection via manifest files
- **State Management** — Session tracking and conversation continuity
- **Knowledge Organization** — Files-as-truth storage patterns

## Directory Structure

```
/
├── N5/                    # Core system files
│   ├── scripts/           # Python utilities
│   ├── prefs/             # Configuration and context
│   ├── schemas/           # JSON schemas
│   └── docs/              # Documentation
├── Prompts/               # User-facing workflows
│   ├── Blocks/            # Modular prompt components
│   └── reflections/       # Reflection workflows
├── Knowledge/             # Long-term knowledge storage
├── Lists/                 # Tracked lists and collections
└── templates/             # File templates
```

## Key Components

### Context Loader (`n5_load_context.py`)
Loads contextual files based on task type. Reads from `context_manifest.yaml` to determine which files to inject.

### Session State Manager (`session_state_manager.py`)
Tracks conversation progress in SESSION_STATE.md files. Provides continuity across conversation boundaries.

### Journal System (`journal.py`)
Guided reflection workflows with structured output formats.

## Design Principles

See `Knowledge/architectural/principles.md` for core architectural principles.

## Extension Points

1. **New Prompts** — Add `.prompt.md` files to `/Prompts/`
2. **New Context Groups** — Edit `N5/prefs/context_manifest.yaml`
3. **New Scripts** — Add to `N5/scripts/` with CLI interface
```

### Task 4: Create N5/docs/CONTRIBUTING.md

Create `/home/workspace/N5/export/n5os-ode/N5/docs/CONTRIBUTING.md`:

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# Contributing to N5OS-Ode

Thank you for your interest in contributing to N5OS-Ode!

## Getting Started

1. Fork the repository
2. Run the BOOTLOADER prompt in your Zo workspace
3. Make your changes
4. Test locally
5. Submit a pull request

## Types of Contributions

### Prompts
New workflows should be added as `.prompt.md` files in `/Prompts/`. Include:
- Clear description in YAML frontmatter
- Step-by-step instructions
- Example usage

### Scripts
Python scripts go in `N5/scripts/`. Requirements:
- Use argparse for CLI
- Include `--help` documentation
- No external dependencies beyond stdlib (or document in DEPENDENCIES.md)
- Follow existing code style

### Documentation
- Keep docs up to date with changes
- Use clear, concise language
- Include examples where helpful

## Code Style

- Python: Follow PEP 8
- Markdown: Use consistent header levels, one sentence per line for diffs
- YAML: 2-space indentation

## Pull Request Process

1. Update documentation for any changed functionality
2. Test your changes locally
3. Write clear commit messages
4. Reference any related issues

## Questions?

Open an issue for questions or discussion.
```

### Task 5: Create N5/README.md

Create `/home/workspace/N5/export/n5os-ode/N5/README.md`:

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# N5 Directory

Core system files for N5OS-Ode.

## Contents

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Python utilities for system operations |
| `prefs/` | Configuration, context manifests, style guides |
| `schemas/` | JSON schemas for data validation |
| `docs/` | System documentation |

## Scripts Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `session_state_manager.py` | Conversation state tracking | `python3 N5/scripts/session_state_manager.py init --convo-id X` |
| `n5_load_context.py` | Context file loading | `python3 N5/scripts/n5_load_context.py build` |
| `journal.py` | Guided reflection sessions | `python3 N5/scripts/journal.py start` |
| `n5_protect.py` | Path protection checks | `python3 N5/scripts/n5_protect.py check /path` |
| `n5_safety.py` | Safety validation | `python3 N5/scripts/n5_safety.py check delete /path` |
| `init_build.py` | Build workspace creation | `python3 N5/scripts/init_build.py my-build --title "Title"` |

## Configuration

Main configuration files:
- `prefs/context_manifest.yaml` — Defines context loading groups
- `prefs/prefs.md` — Human-readable preferences overview

## For More Information

- [Main README](../README.md) — Project overview
- [Architecture](docs/ARCHITECTURE.md) — System design
- [Contributing](docs/CONTRIBUTING.md) — How to contribute
```

---

## Verification

After creating all files:

```bash
cd /home/workspace/N5/export/n5os-ode

# 1. LICENSE exists
test -f LICENSE && echo "PASS: LICENSE exists"

# 2. N5/docs files exist
test -f N5/docs/ARCHITECTURE.md && echo "PASS: ARCHITECTURE.md"
test -f N5/docs/CONTRIBUTING.md && echo "PASS: CONTRIBUTING.md"

# 3. N5/README.md exists
test -f N5/README.md && echo "PASS: N5/README.md"

# 4. Links in prefs.md resolve (manual check)
# Verify that ../README.md from N5/prefs/ points to root README
ls -la N5/prefs/../README.md 2>/dev/null || echo "Check: README link"
ls -la N5/prefs/../docs/ARCHITECTURE.md 2>/dev/null && echo "PASS: ARCHITECTURE link valid"
ls -la N5/prefs/../docs/CONTRIBUTING.md 2>/dev/null && echo "PASS: CONTRIBUTING link valid"
```

---

## Handoff

When complete:
1. Report: "W5_docs_and_links complete. Fixed links in prefs.md, created 4 documentation files."
2. List all files created
3. Note any link fixes made in prefs.md
4. Show verification output
5. Do NOT commit yet - W6 will handle all commits

---

## Files Summary

**To edit:**
- `N5/prefs/prefs.md` — fix broken links

**To create:**
- `LICENSE`
- `N5/docs/ARCHITECTURE.md`
- `N5/docs/CONTRIBUTING.md`
- `N5/README.md`



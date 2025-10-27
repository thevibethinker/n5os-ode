# N5 OS Bootstrap

Deploy N5 OS (Vrijen's operating system for AI knowledge work) onto your Zo instance.

---

## Quick Install (5 minutes)

```bash
git clone https://github.com/[USERNAME]/n5os-bootstrap.git
cd n5os-bootstrap
bash bootstrap.sh
```

Follow the interactive prompts to select modules.

---

## What is N5 OS?

N5 OS is a modular operating system for AI-enabled knowledge work, built by Vrijen Attawar. It provides:

- **Structured Preferences Architecture** — Modular configuration system for AI agents
- **Command Registry** — 83+ documented commands with natural language triggers
- **List Management System** — JSONL-based structured lists for tracking
- **Meeting Ingestion Workflows** — Automated meeting processing protocols
- **Knowledge Base** — Architectural principles and system documentation
- **Git-Safe Operations** — Built-in safety checks and state management

---

## What You Get

### Core Foundation (Required)
- Preference system (105 modular files)
- JSON schemas for validation
- Command registry (83+ commands)
- Command documentation
- Incantum natural language triggers

### Optional Systems
- **Lists** — Tracking system (ideas, contacts, opportunities, reviews)
- **Meetings** — Processing workflows (11 protocols)
- **Knowledge** — Reference documentation (architectural principles)
- **Scripts** — Python utilities (core/standard/full tiers)

---

## Installation

### Prerequisites
- Python 3
- Git (optional but recommended)
- Unix/Linux environment (Zo instance)

### Run Installer

```bash
bash bootstrap.sh
```

You'll be prompted to select:
1. List Management System (recommended)
2. Meeting Ingestion Workflows (recommended)
3. Knowledge Base Reference (optional)
4. Scripts Package (minimal/standard/full)
5. Communication Templates (optional)

Installation takes ~5 minutes.

---

## After Installation

### First Steps

1. **Review the system**:
   ```bash
   cat N5/prefs/prefs.md | head -50
   ```

2. **Rebuild the index**:
   ```bash
   python3 N5/scripts/n5_index_rebuild.py
   ```

3. **Explore commands**:
   ```bash
   python3 -m json.tool < N5/config/commands.jsonl | less
   ```

### Documentation

- **Quick Start** — `QUICK_START.md` (5-minute guide)
- **Architecture** — `docs/ARCHITECTURE.md` (system overview)
- **Modules** — `docs/MODULES.md` (what each module does)
- **Commands** — `COMMAND_REFERENCE.md` (83+ commands)
- **System Prefs** — `N5/prefs/prefs.md` (detailed preferences)

---

## Package Contents

```
n5os-bootstrap/
├── bootstrap.sh           # Interactive installer
├── core/                  # Core N5 OS components
│   ├── prefs/            # Preference architecture (105 files)
│   ├── schemas/          # JSON validation (19 files)
│   ├── config/           # Command registry (21 files)
│   └── commands/         # Documentation (113 files)
├── systems/              # Optional systems
│   ├── lists/            # List management
│   ├── meetings/         # Meeting workflows
│   └── knowledge/        # Reference docs
├── scripts/              # Python utilities
│   ├── core/             # Essential scripts (4)
│   ├── lib/              # Support libraries
│   └── helpers/          # Helper utilities
└── docs/                 # System documentation
    ├── ARCHITECTURE.md
    └── MODULES.md
```

**Total**: 295 files, 1.6 MB

---

## Commands Available

After installation, you'll have access to 83+ commands:

- `index-rebuild` — Rebuild system index
- `git-check` — Verify git changes are safe
- `meeting-process` — Process meeting transcripts
- `reflection-ingest` — Capture reflections
- `deliverable-generate` — Generate documents
- And 78+ more...

See `COMMAND_REFERENCE.md` for the full list.

---

## Modular Design

N5 OS is designed to be modular. You can:

- Install only what you need
- Add more systems later
- Customize for your workflow
- Extend with your own scripts

---

## Support

- **Documentation**: Start with `QUICK_START.md`
- **Architecture**: Read `docs/ARCHITECTURE.md`
- **Source**: Built from Vrijen Attawar's N5 OS

---

## Version

**Version**: 1.0 (Beta)  
**Last Updated**: 2025-10-26  
**Source**: Vrijen Attawar's N5 OS  
**License**: Private (for Eric's deployment)

---

**Ready to install?** Run `bash bootstrap.sh`

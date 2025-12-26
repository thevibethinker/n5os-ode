# N5 OS Core Bootstrap

Deploy N5 OS (Vrijen's complete operating system for AI knowledge work) onto your Zo instance.

**Philosophy**: Generous core. Start small, prove it works, expand gradually.

---

## Quick Install (5 minutes)

```bash
git clone https://github.com/vrijenattawar/n5os-core.git
cd n5os-core
bash bootstrap.sh
```

**Next**: Follow `QUICK_START.md` for first steps

---

## What's Included

### Core System (32 commands, 23 scripts)

1. **System Infrastructure** — conversation-end, thread-export, session state, git safety, index management
2. **List Management** — JSONL-based task/idea tracking (6 commands)
3. **Knowledge Management** — Stable reference ingestion (4 commands)
4. **Search & Discovery** — Command search, gfetch integration (2 commands)
5. **System Design** — Workflow for building new systems (1 command)
6. **Developer Tools** — Command authoring, docgen (2 commands)

### Philosophy & Architecture
- Zero-Touch Manifesto — Complete guide (`Documents/System/zero_touch_manifesto.md`)
- Architectural Principles — 30+ patterns (`Knowledge/architectural/architectural_principles.md`)

### Preference System
- 25 essential preferences organized by category
- Modular, composable configuration
- Operations protocols + system rules

### Schemas & Validation
- 16 JSON schemas for data integrity
- List structures, knowledge formats, command metadata

### Documentation
All comprehensive guides in `Documents/System/`:
- `QUICK_START.md` — 15-min user guide
- `DEVELOPER_QUICKSTART.md` — 15-min developer tutorial
- `FIRST_RUN_CHECKLIST.md` — Complete setup (45 min)
- `ZO_SETTINGS_REQUIRED.md` — 10 essential Zo rules
- `SCHEDULED_TASKS.md` — 5 automation tasks
- `CONSULTANT_GUIDE.md` — Remote troubleshooting
- `SESSION_STATE_GUIDE.md` — Context across conversations
- `CONVERSATION_DATABASE_GUIDE.md` — Query conversation history

---

## For End Users

**Goal**: Productive AI knowledge work in 15 minutes

1. Install (5 min): `bash bootstrap.sh`
2. Configure Zo rules (5 min): `cat Documents/System/ZO_SETTINGS_REQUIRED.md`
3. Try first command (5 min): `python3 N5/scripts/n5_lists_add.py --help`

**Full guide**: `QUICK_START.md`

---

## For Developers

**Goal**: Build custom commands in 15 minutes

1. Read tutorial: `DEVELOPER_QUICKSTART.md`
2. Study workflow: `N5/commands/command-author.md`
3. Generate docs: `N5/commands/docgen.md`

**System design**: `N5/commands/system-design-workflow.md`

---

## Documentation Index

### Getting Started
- `README.md` (this file) — Overview & entry point
- `QUICK_START.md` — 15-min user guide
- `DEVELOPER_QUICKSTART.md` — 15-min developer tutorial
- `Documents/N5.md` — System architecture overview

### Setup & Configuration
- `Documents/System/FIRST_RUN_CHECKLIST.md` — Complete setup checklist
- `Documents/System/ZO_SETTINGS_REQUIRED.md` — Essential Zo rules
- `Documents/System/SETUP_REQUIREMENTS.md` — Prerequisites
- `Documents/System/SCHEDULED_TASKS.md` — Automation setup

### Architecture & Philosophy
- `Documents/System/zero_touch_manifesto.md` — Zero-Touch philosophy
- `Knowledge/architectural/architectural_principles.md` — 30+ design patterns
- `Documents/System/ONBOARDING_DESIGN.md` — Future interactive setup
- `Documents/System/ROADMAP.md` — Version plan through v1.3

### Operational Guides
- `Documents/System/SESSION_STATE_GUIDE.md` — Maintain context
- `Documents/System/CONVERSATION_DATABASE_GUIDE.md` — Query history
- `Documents/System/CONSULTANT_GUIDE.md` — Remote troubleshooting
- `Documents/System/AUTO_SYNC_DESIGN.md` — Keep core updated
- `Documents/System/TELEMETRY_SERVICE_DESIGN.md` — Usage analytics (opt-in)

### Lists & Knowledge
- `Lists/POLICY.md` — List management rules
- `Lists/README.md` — List system overview
- `N5/prefs/prefs.md` — Complete preference index

---

## What's NOT Included

**These are expansion packs** (future releases):
- Meeting processing workflows
- Deliverable generation
- Social media management
- Job/career tracking (Careerspan)
- Reflection systems
- CRM functionality
- Research intelligence
- All V-specific proprietary workflows

**Core is foundation**. Expansion packs add domain-specific workflows.

---

## Version

**Version**: 1.0-core (Complete Foundation)  
**Last Updated**: 2025-10-27  
**Author**: Vrijen Attawar  
**License**: MIT (free forever)  
**Status**: Production Ready

---

## Links

- **GitHub**: https://github.com/vrijenattawar/n5os-core
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Ask questions via GitHub Discussions

---

**Ready to install?** Run `bash bootstrap.sh` then follow `QUICK_START.md`

**This is the complete N5 OS foundation.** Everything you need to be productive with AI. 🚀

# N5 OS Bootstrap Package — Live Build

**Status**: BUILDING IN REAL TIME  
**Target**: Eric's Zo Instance (Unix/Linux)  
**Date**: 2025-10-26 20:44 ET

---

## Core Layer Definition

The **N5 OS Base Layer** consists of:

### 1. **Preferences Architecture** (`prefs/`)
- Modular configuration system
- Communication, operations, system, integration, knowledge modules
- File protection rules
- Git governance
- Folder policies
- Command triggering (Incantum)

**Source**: `/home/workspace/N5/prefs/` (~20 files, modular)  
**Export**: Full subtree (preserve structure)

### 2. **Configuration Registry** (`config/`)
- `commands.jsonl` — Command definitions (83 commands)
- `incantum_triggers.json` — Natural language triggers
- `tag_taxonomy.json` — Tag system
- Schemas: front matter, relationships, enrichment
- Service configs, drive sync, etc.

**Source**: `/home/workspace/N5/config/` (~35 files)  
**Export**: Core files only (no credentials/)

### 3. **Schemas** (`schemas/`)
- JSON Schema definitions for validation
- Command schema, knowledge schema, list schema

**Source**: `/home/workspace/N5/schemas/`  
**Export**: All `.json` schemas

### 4. **Core Scripts** (`scripts/`)
- Foundation utilities: `n5_index_rebuild.py`, `n5_git_check.py`, etc.
- Command orchestration scripts
- Helper libraries in `scripts/lib/`

**Source**: `/home/workspace/N5/scripts/` (259 .py files!)  
**Export**: Core scripts (TBD via modular selection)

### 5. **Command Documentation** (`commands/`)
- Command definition files (`.md`)
- System design workflows
- Protocols

**Source**: `/home/workspace/N5/commands/`  
**Export**: All `.md` files

### 6. **Lists System** (`Lists/`)
- `POLICY.md` — List handling rules
- Schema definitions
- Empty JSONL structure for Eric's lists

**Source**: `/home/workspace/Lists/`  
**Export**: Policy + schemas (empty data)

### 7. **Meeting Ingestion System**
- Workflow documentation
- Templates
- Protocol files

**Source**: `/home/workspace/N5/` → protocols, templates  
**Export**: TBD

### 8. **Knowledge/Stable** (lightweight reference)
- Glossary, bio, architectural principles
- Company strategy (if needed)

**Source**: `/home/workspace/Knowledge/stable/`  
**Export**: Lightweight reference docs

---

## Modular Export Selection

**Once we have the structure, Eric will choose:**

```
[ ] Core Preferences (required)
[ ] Command Registry (required)
[ ] Command Scripts (choose: minimal, standard, full)
[ ] Schemas (required)
[ ] List System (required)
[ ] Meeting Ingestion (optional)
[ ] Knowledge Base (optional)
[ ] Communication Templates (optional)
```

---

## GitHub Structure (To Be Built)

```
zo-n5os-bootstrap/
├── README.md (setup instructions)
├── bootstrap.sh (main installer script)
├── SELECT_MODULES.json (module selection UI)
├── core/
│   ├── prefs/ (preferences architecture)
│   ├── config/ (registry files)
│   ├── schemas/ (validation schemas)
│   └── commands/ (command docs)
├── systems/
│   ├── lists/ (list system)
│   ├── meetings/ (meeting ingestion)
│   └── knowledge/ (reference docs)
├── scripts/
│   ├── core/ (foundation utilities)
│   ├── lib/ (helper libraries)
│   └── modules/ (modular feature scripts)
└── docs/
    ├── ARCHITECTURE.md
    ├── MODULES.md
    └── TROUBLESHOOTING.md
```

---

## Next Steps

1. ✅ Map core layer
2. ⏳ Build module selection interface
3. ⏳ Create bootstrap.sh installer
4. ⏳ Initialize GitHub repo
5. ⏳ Test with Eric in real-time

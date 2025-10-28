# N5OS Demonstrator - File Structure (Empty Initial State)

**Purpose**: Visual reference for what gets built where during phased implementation

---

## Complete File Tree

```
/home/workspace/
│
├── N5/                                    [Phase 0+]
│   ├── templates/                         [Phase 0] Config templates (from GitHub)
│   │   ├── rules.template.md              [Phase 0] → generates config/rules.md
│   │   ├── prefs.template.md              [Phase 4] → generates config/prefs.md
│   │   └── commands.template.jsonl        [Phase 2] → generates config/commands.jsonl
│   │
│   ├── config/                            [Phase 0] User-generated (in .gitignore)
│   │   ├── rules.md                       [Phase 0] Active rules (user customizable)
│   │   ├── prefs.md                       [Phase 4] Active preferences
│   │   └── commands.jsonl                 [Phase 2] Active command registry
│   │
│   ├── scripts/                           [Phase 0+]
│   │   ├── create_structure.py            [Phase 0] Setup script
│   │   ├── n5_init.py                     [Phase 0] Config generator
│   │   ├── system_cleanup.py              [Phase 0] Cleanup schedule
│   │   ├── generate_self_description.py   [Phase 0] System scanner
│   │   ├── register_cleanup_schedule.py   [Phase 0] Schedule registration helper
│   │   ├── session_state_manager.py       [Phase 1] Session initialization
│   │   ├── n5_safety.py                   [Phase 1] Safety validation
│   │   └── build_orchestrator.py          [Phase 3] Multi-agent coordination
│   │
│   ├── schemas/                           [Phase 2]
│   │   ├── index.schema.json              [Phase 2] Component interfaces
│   │   └── command.schema.json            [Phase 2] Command structure
│   │
│   ├── data/                              [Phase 0+]
│   │   ├── system_description.md          [Phase 0] Generated system summary
│   │   ├── system_bulletins.jsonl         [Phase 1] Change tracking (rolling 10 days)
│   │   └── conversations.db               [Phase 1] SQLite registry
│   │
│   └── prefs/                             [Phase 4]
│       ├── prefs.md                       [Phase 4] Main preferences file
│       ├── operations/                    [Phase 4] Operational preferences
│       │   └── scheduled-task-protocol.md [Phase 4] Task creation rules
│       └── preferences/                   [Phase 4] Category-specific prefs
│
├── Knowledge/                             [Phase 4+]
│   ├── architectural/                     [Phase 4] Design patterns
│   │   ├── planning_prompt.md             [Phase 3] Simplified version
│   │   └── principles/                    [Phase 4] Core principles (curated)
│   │       ├── P0-minimal-context.md
│   │       ├── P1-human-readable.md
│   │       └── [subset of 22 principles]
│   │
│   └── [user knowledge base grows here]   [Phase 5] User-specific knowledge
│
├── Lists/                                 [Phase 5]
│   └── [action items, tasks]              [Phase 5] From conversation end workflow
│
├── Records/                               [Phase 5]
│   └── Temporary/                         [Phase 5] Staging area
│       └── [drafts, in-progress work]
│
├── Documents/                             [Base]
│   ├── N5.md                              [Phase 1] System overview doc
│   └── [user documents]                   [User] User-created content
│
├── .gitignore                             [Phase 0] Excludes /N5/config/, /N5/data/
├── README.md                              [Phase 0] Quick start
├── CHANGELOG.md                           [Phase 0] Version history
└── LICENSE                                [Phase 0] Open source license

```

---

## Phase-by-Phase Build Out

### Phase 0: Foundation
```
/home/workspace/
├── N5/
│   ├── templates/
│   │   └── rules.template.md
│   ├── config/                [GENERATED on first run]
│   │   └── rules.md
│   ├── scripts/
│   │   ├── create_structure.py
│   │   ├── n5_init.py
│   │   ├── system_cleanup.py
│   │   ├── generate_self_description.py
│   │   └── register_cleanup_schedule.py
│   └── data/
│       └── system_description.md
├── .gitignore
├── README.md
└── docs/
    ├── installation.md
    └── configuration.md
```

---

### Phase 1: Infrastructure (adds to Phase 0)
```
N5/
├── scripts/
│   ├── session_state_manager.py       [NEW]
│   └── n5_safety.py                   [NEW]
├── data/
│   ├── system_bulletins.jsonl         [NEW]
│   └── conversations.db               [NEW]
└── config/
    └── detection_rules.md             [NEW] (for safety system)

Documents/
└── N5.md                              [NEW]
```

---

### Phase 2: Commands (adds to Phase 1)
```
N5/
├── templates/
│   └── commands.template.jsonl        [NEW]
├── config/
│   └── commands.jsonl                 [NEW - generated]
└── schemas/
    ├── index.schema.json              [NEW]
    └── command.schema.json            [NEW]
```

---

### Phase 3: Build System (adds to Phase 2)
```
N5/
└── scripts/
    └── build_orchestrator.py          [NEW]

Knowledge/
└── architectural/
    └── planning_prompt.md             [NEW]
```

---

### Phase 4: Preferences & Principles (adds to Phase 3)
```
N5/
├── templates/
│   └── prefs.template.md              [NEW]
├── config/
│   └── prefs.md                       [NEW - generated]
└── prefs/
    ├── prefs.md                       [NEW]
    └── operations/
        └── scheduled-task-protocol.md [NEW]

Knowledge/
└── architectural/
    └── principles/                    [NEW]
        ├── [curated subset]
        └── index.md
```

---

### Phase 5: Workflows (adds to Phase 4)
```
N5/
└── scripts/
    └── conversation_end_workflow.py   [NEW - REBUILT]

Lists/                                 [NOW ACTIVE]
└── [generated by workflow]

Records/                               [NOW ACTIVE]
└── Temporary/
    └── [staging area active]
```

---

## Git Configuration

### .gitignore
```
# User-specific configs (never commit)
N5/config/
N5/data/

# User knowledge and records (never commit)
Knowledge/
Lists/
Records/

# Python
__pycache__/
*.pyc
*.pyo

# OS
.DS_Store
Thumbs.db

# Conversation workspaces (if any)
.z/
```

### What DOES get committed to GitHub
- `/N5/templates/` - Config templates
- `/N5/scripts/` - All scripts
- `/N5/schemas/` - JSON schemas
- `/docs/` - Documentation
- `README.md`, `CHANGELOG.md`, `LICENSE`
- Empty directory structure (via .gitkeep files)

### What NEVER gets committed
- User configs (`/N5/config/`)
- User data (`/N5/data/`)
- User knowledge (`/Knowledge/`)
- User lists (`/Lists/`)
- User records (`/Records/`)

---

## Installation Flow for New User

1. **Clone repo**
   ```bash
   cd /home/workspace
   git clone https://github.com/[org]/n5os-core.git
   cd n5os-core
   ```

2. **Run structure setup**
   ```bash
   python3 N5/scripts/create_structure.py
   ```

3. **Initialize configs**
   ```bash
   python3 N5/scripts/n5_init.py
   ```
   → Generates `/N5/config/` from `/N5/templates/`

4. **Register schedules** (if Phase 0 includes scheduling)
   ```bash
   python3 N5/scripts/register_cleanup_schedule.py
   ```

5. **Verify installation**
   ```bash
   python3 N5/scripts/generate_self_description.py
   cat N5/data/system_description.md
   ```

6. **Customize** (optional)
   - Edit `/N5/config/rules.md`
   - Edit `/N5/config/prefs.md` (when Phase 4 installed)
   - Add custom commands to `/N5/config/commands.jsonl` (when Phase 2 installed)

---

## Update Flow for Existing User

1. **Pull updates**
   ```bash
   cd /home/workspace/n5os-core
   git pull origin main
   ```

2. **Check for new templates**
   ```bash
   python3 N5/scripts/n5_init.py --check
   ```
   → Shows new templates available

3. **Review changes** (optional)
   ```bash
   diff N5/templates/rules.template.md N5/config/rules.md
   ```

4. **Merge manually** (if desired)
   - Copy relevant updates from `/templates/` to `/config/`
   - Or regenerate with `n5_init.py --regenerate [file]`

5. **Run system check**
   ```bash
   python3 N5/scripts/generate_self_description.py
   ```

---

## Directory Purpose Reference

| Directory | Purpose | Committed to Git? | Generated? |
|-----------|---------|-------------------|------------|
| `/N5/templates/` | Config templates (upstream) | ✅ Yes | Manual |
| `/N5/config/` | User configs (local) | ❌ No | Generated from templates |
| `/N5/scripts/` | Executable scripts | ✅ Yes | Manual |
| `/N5/schemas/` | JSON validation schemas | ✅ Yes | Manual |
| `/N5/data/` | Runtime data (bulletins, db) | ❌ No | Generated by scripts |
| `/N5/prefs/` | Preference modules | ✅ Yes | Manual |
| `/Knowledge/` | User knowledge base | ❌ No | User/AI created |
| `/Lists/` | Action items, tasks | ❌ No | Generated by workflows |
| `/Records/` | Staging, temp work | ❌ No | User/AI created |
| `/Documents/` | User documents | Partial | Mixed |
| `/docs/` | System documentation | ✅ Yes | Manual |

---

*Created: 2025-10-27 23:47 ET*

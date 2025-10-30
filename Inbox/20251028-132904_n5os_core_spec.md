# N5OS Core Distribution Specification

**Version**: 0.1-draft  
**Created**: 2025-10-27 23:47 ET  
**Status**: Planning Phase

---

## Executive Summary

**Official Name**: N5 OS (with space, capital N)
**Codename**: Cesc v0.1 (C-E-S-C, after Cesc Fàbregas - Arsenal naming)
**Repo**: `zo-n5os-core`
**License**: MIT
**Credit**: Vrijen Attawar
**Workflow**: Main → Demonstrator → GitHub (test before release)
**Target User**: Non-technical Zo users seeking personal productivity

**Goal**: Create deployable, open-source N5OS core on demonstrator Zo account → distribute via GitHub

**Strategy**: Atomic rebuild (not export/pare-down) with config template system

**Timeline**: Phased execution starting with foundation (rules + schedules), then expanding incrementally

---

## I. Architecture Overview

### Three-Environment Model

```
┌─────────────────────────────────────────────────┐
│  MAIN (va.zo.computer)                          │
│  • Production system                            │
│  • Source of truth for design patterns         │
│  • Testing ground for new features              │
│  • Remains fully intact                         │
└──────────────────┬──────────────────────────────┘
                   │
                   │ (Design patterns, lessons learned)
                   ▼
┌─────────────────────────────────────────────────┐
│  DEMONSTRATOR (TBD.zo.computer)                 │
│  • Fresh rebuild with lessons applied           │
│  • Minimal, self-contained, documented          │
│  • Testing ground for distribution              │
│  • Push to GitHub when stable                   │
└──────────────────┬──────────────────────────────┘
                   │
                   │ (via GitHub)
                   ▼
┌─────────────────────────────────────────────────┐
│  GITHUB REPO (Public Distribution)              │
│  • /install/ - Setup scripts                    │
│  • /packages/ - Monthly releases                │
│  • /docs/ - User documentation                  │
│  • /templates/ - Config templates               │
│  • Users clone, configure, pull updates         │
└─────────────────────────────────────────────────┘
```

---

## II. Config Management Architecture

### Template vs. User Separation

**Problem**: How to distribute updates without overwriting user customizations?

**Solution**: Two-tier config system

```
N5/
├── templates/           # FROM GITHUB (read-only reference)
│   ├── prefs.template.md
│   ├── commands.template.jsonl
│   └── rules.template.md
│
├── config/              # USER GENERATED (never overwritten)
│   ├── prefs.md         # Generated from template on first run
│   ├── commands.jsonl   # User's active config
│   └── rules.md         # User's active rules
│
└── scripts/
    └── n5_init.py       # Detects missing configs, generates from templates
```

**Workflow**:
1. User clones repo → has `/templates/` folder
2. First run of any N5 script → detects missing `/config/` files
3. Auto-generates `/config/` from `/templates/` with prompts for customization
4. Git ignores `/config/` (in .gitignore)
5. Updates via `git pull` → only `/templates/` change → user manually merges if desired

**Benefits**:
- Users never lose their customizations
- Updates don't break existing setups
- Clear separation of "upstream" vs "local"
- Users can diff template vs config to see what changed

---

## III. Core Components by Phase

### Phase 0: Foundation (FIRST PRIORITY)

**Deploy these BEFORE anything else:**

1. **Conditional Rules** (`/N5/config/rules.md`)
   - General rules that make Zo work well
   - Required for AI to operate correctly
   - **Include**: Safety rules, troubleshooting protocol, pre-flight checks
   - **Exclude**: V-specific personal preferences

2. **Scheduled Tasks**
   - System cleanup (logs, temp files)
   - Self-description generator (helps AI understand setup)
   - Session state maintenance

3. **Config Template System**
   - `n5_init.py` script
   - `/templates/` folder structure
   - .gitignore configured correctly

**Output**: Empty Zo with rules → can think properly and maintain itself

---

### Phase 1: Core Infrastructure

**Components**:
1. **Session State Manager** (`session_state_manager.py`)
   - Conversation tracking
   - State initialization
   - System file loading

2. **System Bulletins** (`system_bulletins.jsonl`)
   - Change tracking
   - AI transparency into evolution
   - Troubleshooting context

3. **Conversation Registry** (`conversations.db`)
   - SQLite database for conversation metadata
   - Type tracking (build/research/discussion/planning)
   - Cross-conversation coordination

4. **Safety System** (`n5_safety.py`)
   - Detection rules (`detection_rules.md`)
   - Dry-run enforcement
   - Pre-execution validation

**Output**: Working infrastructure that tracks itself

---

### Phase 2: Command System

**Components**:
1. **Incantum** (Natural Language Commands)
   - `commands.jsonl` registry
   - `incantum_triggers.json` for `/` commands
   - Command execution framework

2. **Schema Validation** (`/N5/schemas/`)
   - `index.schema.json`
   - Component interface specs
   - Validation scripts

**Output**: User can define and invoke commands naturally

---

### Phase 3: Build System

**Components**:
1. **Build Orchestrator**
   - Multi-agent coordination
   - Phase management
   - Handoff protocols

2. **Planning Prompt** (simplified version)
   - Design philosophy (Simple Over Easy, etc.)
   - Think→Plan→Execute framework
   - Not as refined as Main (that's secret sauce)

**Output**: Can coordinate complex builds

---

### Phase 4: Knowledge & Preferences

**Components**:
1. **Preferences System** (`/N5/prefs/`)
   - Modular preference loading
   - Context-aware preference selection
   - User customization hooks

2. **Architectural Principles** (curated subset)
   - Core principles that are generally applicable
   - Not all 22 (some are V-specific learnings)
   - Focus on universally valuable patterns

**Output**: Customizable, principled operation

---

### Phase 5: Workflows (REBUILD ON DEMONSTRATOR)

**Components**:
1. **Conversation End Workflow** (REBUILD - current version flawed)
   - Review → Classify → Propose → Execute
   - Knowledge extraction
   - List/task generation

2. **Knowledge Management**
   - SSOT enforcement
   - Portable knowledge structures
   - Migration patterns

**Output**: Self-maintaining knowledge system

---

### EXCLUDED (Paid Modules - Separate Repos)

These become premium add-ons:
- **Reflection Engine** (deep introspection)
- **Meeting Ingestion** (audio → insights)
- **CRM Integration** (Careerspan-specific)

---

## IV. Section-by-Section Transport Plan

### Unit Definitions

Each "unit" = independently transportable + testable

| Unit ID | Name | Files | Dependencies | Test Criteria |
|---------|------|-------|--------------|---------------|
| U0.1 | Core Rules | `rules.md` template | None | AI loads and applies |
| U0.2 | Cleanup Schedule | `cleanup.py` + cron | None | Runs without error |
| U0.3 | Config Init | `n5_init.py` | U0.1 | Generates configs from templates |
| U1.1 | Session State | `session_state_manager.py` | U0.3 | Creates SESSION_STATE.md |
| U1.2 | System Bulletins | `system_bulletins.jsonl` generator | U1.1 | Tracks changes correctly |
| U1.3 | Conv Registry | `conversations.db` + schema | U1.1 | Registers/queries convos |
| U1.4 | Safety System | `n5_safety.py` + rules | U0.1 | Validates operations |
| U2.1 | Command Registry | `commands.jsonl` parser | U1.1 | Loads and executes commands |
| U2.2 | Incantum | Natural language → command | U2.1 | Parses NL correctly |
| U2.3 | Schema Validator | JSON schema validation | U2.1 | Validates interfaces |
| U3.1 | Build Orchestrator | Multi-agent framework | U1.1, U1.3 | Coordinates phases |
| U3.2 | Planning Prompt | Design philosophy doc | None | Loaded and applied |
| U4.1 | Preferences | Modular pref loading | U0.3 | Loads context-appropriate prefs |
| U4.2 | Principles | Core architectural rules | None | Referenced correctly |
| U5.1 | Conv End Workflow | REBUILD on Demo | U1.1, U1.3, U4.1 | Completes review cycle |
| U5.2 | Knowledge Mgmt | SSOT enforcement | U1.1 | Maintains knowledge base |

**Transport Order**: U0.1 → U0.2 → U0.3 → U1.x → U2.x → U3.x → U4.x → U5.x

---

## V. GitHub Workflow

### Recommended Flow

```
MAIN (Development & Design)
  ↓
  [Extract pattern/component]
  ↓
DEMONSTRATOR (Clean Implementation)
  ↓
  [Test until stable]
  ↓
GITHUB (Distribution)
  ↓
  [Users clone/pull]
  ↓
END USERS (Production Use)
```

**Why this order?**
- Main → Demonstrator: You refine and rebuild cleanly
- Demonstrator → GitHub: You test before public release
- GitHub → Users: Standard distribution

**Alternative (if time-critical)**: Main → GitHub → Demonstrator (but riskier)

---

## VI. Debugging Strategy

### Where to Debug What

| Issue Type | Debug Location | Rationale |
|------------|----------------|-----------|
| Design patterns | MAIN | Source of truth |
| Implementation bugs | DEMONSTRATOR | Clean environment |
| Distribution issues | DEMONSTRATOR | Matches user environment |
| User-reported bugs | DEMONSTRATOR | Reproduce in same setup |
| Integration testing | DEMONSTRATOR | End-to-end flows |

**Communication**: Document fixes on Demonstrator → Extract pattern → Apply to Main (if needed)

---

## VII. Empty Zo Baseline

### What Fresh Zo Account Has

**Out of box**:
- Zo system files (docs, recipes, basic structure)
- No user rules
- No scheduled tasks
- No custom scripts
- Basic workspace folders (Documents, etc.)

**What we assume V has transferred**:
- Conditional rules (in settings)
- (TBD: Any schedules?)

**What N5OS will add**:
- Everything in Phase 0-5 above
- Self-initialization capability
- Documentation for users to understand it

---

## VIII. Design Decisions (LOCKED)

✅ **GitHub Workflow**: Main → Demonstrator → GitHub (test thoroughly before release)

✅ **Rule of Two**: REMOVED (no limit on config files; monitor for issues)

✅ **License & Branding**:
- Official name: **N5 OS** (with space, capital N)
- Codename: **Cesc** (v0.1 - C-E-S-C, after Cesc Fàbregas, Arsenal naming convention)
- Repo name: **zo-n5os-core** (V's choice)
- License: **MIT**
- Credit: **Vrijen Attawar** (personal, not Careerspan)
- Action: ✅ Clashing GitHub repos deleted

✅ **Target User Profile**:
- **Technical level**: Non-technical (cannot assume terminal comfort)
- **Use case**: Personal productivity for Zo users
- **Support**: Community-driven (Discord/GitHub issues)
- **Documentation**: Must be comprehensive, beginner-friendly, step-by-step

---

## IX. Next Steps

### Immediate (This Thread)
1. ✅ Create this spec
2. ✅ V answers open questions → ALL DECISIONS LOCKED
3. ✅ Create Phase 0 detailed build plan
4. ✅ Generate empty file structure for Demonstrator

### Orchestrator Threads (After Planning)
1. **Thread 1**: Phase 0.1 - Directory structure + n5_init.py
2. **Thread 2**: Phase 0.2 - Core rules template extraction
3. **Thread 3**: Phase 0.3 - Scheduled tasks (cleanup + self-description)
4. **Thread 4**: Phase 0.4 - Testing and documentation
5. **Thread 5+**: Phase 1 (infrastructure), then Phase 2, etc.

### GitHub Pre-Work (V's side)
- [ ] Delete clashing repos on GitHub (n5os or similar)
- [ ] Create fresh repo: `n5os-core`
- [ ] Add MIT license file
- [ ] Add README with "N5 OS - Sesc v0.1"

**Status**: ✅ Planning Complete - Ready for Implementation

---

## X. Success Criteria

### Phase 0 Complete When:
- [ ] Fresh Zo loads rules template
- [ ] Cleanup schedule runs automatically
- [ ] Self-description generator provides accurate system summary
- [ ] Config system generates user configs from templates without overwriting

### Full N5OS Core Complete When:
- [ ] New user can clone repo
- [ ] Run init script → working system in < 30 min
- [ ] Can define custom commands
- [ ] Can coordinate multi-step builds
- [ ] System maintains itself (bulletins, cleanup, state tracking)
- [ ] Documentation explains all components
- [ ] Zero dependencies on V's Main account

---

## XI. Risk Mitigation

### Risk: Complexity Creep
**Mitigation**: Phase gates - must complete and test phase N before starting N+1

### Risk: Main-Demonstrator Divergence
**Mitigation**: Document all Demonstrator patterns → extract → apply to Main periodically

### Risk: User Setup Failure
**Mitigation**: Obsessive documentation + setup script that validates each step

### Risk: Breaking Changes in Updates
**Mitigation**: Template system + semantic versioning + migration guides

---

**Status**: ✅ Planning Complete - Ready for Implementation

---

*Generated: 2025-10-27 23:47 ET*

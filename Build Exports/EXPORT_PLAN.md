---
created: 2026-01-14
last_edited: 2026-01-14
version: 2.0
provenance: con_GVEpFCdNSkLXYuwW
---

# N5 OS Kernel Export Plan

## Naming Convention (Arsenal Theme)

| Codename | Named After | Purpose |
|----------|-------------|---------|
| **Fabregas** | Cesc Fàbregas | Original N5OS (ChadGPT era) |
| **Arteta** | Mikel Arteta | V's master N5OS (this workspace) |
| **Ode** | Martin Ødegaard | Public distribution for friends |

## Target Repository
- **Repo:** `vrijenattawar/n5os-ode` ✓ Created
- **Local:** `/home/workspace/N5/export/n5os-ode/`
- **Old repo:** `zo-n5os-core` preserved for posterity

---

## Delivery Architecture

### The Bootloader Pattern

The bootstrap prompt (`BOOTSTRAP.prompt.md`) is a **bootloader** that:
1. **Installs Personas** — Uses `create_persona` tool to inject simplified personas
2. **Installs Rules** — Uses `create_rule` tool to inject required rules
3. **Creates Folder Structure** — Sets up N5/, Prompts/, Knowledge/, etc.
4. **Validates Setup** — Confirms all components installed correctly

### Key Insight
The personas and rules don't just get *documented* — the bootloader actually *installs* them into Zo's settings using the native tools. This means Ode boots up fully configured, not just with instructions.

---

## Export Structure

```
n5os-ode/
├── README.md                    # Setup guide + philosophy
├── BOOTLOADER.prompt.md         # THE MAIN PROMPT - installs everything
├── PERSONALIZE.prompt.md        # User customization (run after boot)
│
├── docs/
│   ├── PHILOSOPHY.md            # Why N5OS exists
│   ├── SEMANTIC_MEMORY.md       # Guide to setting up brain.db
│   ├── PERSONAS.md              # Persona definitions (for reference)
│   └── RULES.md                 # Rule definitions (for reference)
│
├── N5/
│   ├── cognition/               # Semantic memory layer
│   ├── scripts/                 # Core utilities (sanitized)
│   ├── prefs/                   # Preferences + configs
│   └── templates/               # Build templates
│
├── Prompts/
│   ├── Blocks/                  # B-series generators
│   ├── reflections/             # Journal prompts
│   └── [core prompts]
│
├── Knowledge/                   # Empty scaffold
├── Documents/                   # System docs
├── Lists/                       # SSOT list system
└── Personal/                    # Private area
```

---

## Workstreams (Worker Specs)

### Worker 001: PII Tracking Enhancement
**Status:** Spec created, ready to spawn
**File:** `/home/.z/workspaces/con_GVEpFCdNSkLXYuwW/workers/worker_001_pii_tracking.md`
**Deliverable:** Enhanced `n5_protect.py` with PII scanning

### Worker 002: Core Scripts Sanitization
**Status:** Spec needed
**Scope:**
- Sanitize `session_state_manager.py`
- Sanitize `n5_protect.py`
- Sanitize `n5_load_context.py`
- Sanitize `debug_logger.py`
- Sanitize `journal.py`
- Sanitize `content_ingest.py`
- Create generic `context_manifest.yaml`
**Deliverable:** Clean scripts in `/n5os-ode/N5/scripts/`

### Worker 003: Semantic Memory Package
**Status:** Spec needed
**Scope:**
- Sanitize `n5_memory_client.py`
- Create `SEMANTIC_MEMORY.md` setup guide
- Include `schema.sql`
- Create `config.yaml` template
**Deliverable:** Working semantic memory package

### Worker 004: Prompts & Blocks
**Status:** Spec needed
**Scope:**
- Export & sanitize B01-B06, B11 block generators
- Export & sanitize R01, R02, R06 reflection blocks
- Export & sanitize reflection prompts
- Export Journal, Build Capability, Close Conversation prompts
**Deliverable:** Clean prompts in `/n5os-ode/Prompts/`

### Worker 005: Bootloader Creation
**Status:** Spec needed
**Scope:**
- Write BOOTLOADER.prompt.md that:
  - Calls `create_persona` for each Ode persona
  - Calls `create_rule` for each required rule
  - Creates folder structure
  - Validates installation
- Write PERSONALIZE.prompt.md
**Deliverable:** Working bootloader + personalization prompts

### Worker 006: Documentation
**Status:** Spec needed
**Scope:**
- README.md (setup guide)
- PHILOSOPHY.md (why N5OS)
- PERSONAS.md (reference)
- RULES.md (reference)
- Knowledge system guide
- Lists system guide
**Deliverable:** Complete documentation package

---

## Personas for Ode (Simplified)

| Persona | Purpose | Complexity |
|---------|---------|------------|
| **Operator** | Navigation, routing, orchestration | Core |
| **Builder** | Implementation, coding | Core |
| **Researcher** | Information gathering, synthesis | Core |
| **Writer** | Polished communication | Core |
| **Strategist** | Planning, frameworks | Core |
| **Debugger** | QA, verification | Optional |

**Not included in Ode:**
- Teacher, Librarian (can add later)
- Nutritionist, Trainer (personal domain)
- Level Upper (advanced meta-reasoning)

---

## Rules for Ode (Required)

| Rule | Purpose |
|------|---------|
| Session State Init | Initialize SESSION_STATE.md at conversation start |
| YAML Frontmatter | All markdown files include frontmatter |
| Progress Reporting | Honest X/Y progress, no false "Done" claims |
| File Protection | Check `.n5protected` before destructive ops |
| Debug Logging | Log to DEBUG_LOG.jsonl during builds |
| Clarifying Questions | Ask 3+ questions before ambiguous work |

---

## Orchestrator Checklist

- [x] Create repo `n5os-ode`
- [x] Initialize local directory
- [ ] Create worker specs (002-006)
- [ ] V spawns workers in separate threads
- [ ] Workers deliver to `/n5os-ode/`
- [ ] Orchestrator reviews, integrates
- [ ] Final PII audit
- [ ] Push to GitHub
- [ ] Test fresh boot on new Zo (or Claude)

---

## Notes

- **Arteta formalization:** Rename/reorganize V's master N5OS later
- **Ode is standalone:** Should work without any Arteta dependencies
- **Claude compatibility:** Bootloader should work if pasted into Claude Code


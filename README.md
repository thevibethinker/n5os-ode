---
created: 2026-01-15
last_edited: 2026-02-18
version: 2.0
provenance: con_o9nkV9huRbIpeEGn
---

# N5OS Ode

**A cognitive operating system for Zo Computer**

N5OS Ode transforms Zo from a general-purpose AI assistant into a structured thinking partner. It gives your AI memory, specialized modes of operation, and workflows that evolve with you.

---

## What Is This?

Think of N5OS Ode as firmware for your AI. Out of the box, Zo is a powerful but generic assistant. N5OS Ode adds:

- **Specialist Personas** — 9 focused modes (Operator, Builder, Researcher, Writer, Strategist, Debugger, Architect, Teacher, Librarian) that each excel at different work types
- **Behavioral Rules** — 13 persistent instructions that shape AI behavior across all conversations
- **Operational Principles** — 37 codified principles that define quality, safety, and workflow standards
- **Conversation State** — Memory that persists across long sessions
- **Structured Outputs** — Block generators that transform transcripts into actionable intelligence
- **Skills** — Packaged workflows for debugging, build orchestration, frontend design, and more
- **Safety Rails** — Protection mechanisms that prevent data loss

---

## Quick Start

### 1. Install to Workspace Root

> ⚠️ **IMPORTANT:** N5OS Ode files must live at your workspace ROOT, not inside a subfolder.
> The `Prompts/`, `N5/`, `Knowledge/` folders should be directly in `/home/workspace/`, NOT in `/home/workspace/n5os-ode/`.

**One command does everything:**

```bash
git clone https://github.com/YOUR_USERNAME/n5os-ode.git && cd n5os-ode && bash install.sh
```

This clones the repo, moves all contents to your workspace root, and cleans up the `n5os-ode/` folder.

**Verify it worked:** You should see `Prompts/`, `N5/`, `BOOTLOADER.prompt.md` etc. directly in your workspace root.

### 2. Run the Bootloader

Open a new Zo conversation and type:

```
@BOOTLOADER.prompt.md
```

The bootloader will:
- Install 9 specialist personas
- Create 13 core behavioral rules
- Set up the folder structure (N5/, Knowledge/, Records/, Prompts/, Skills/)
- Initialize configuration files and principles
- Set up conversation registry and semantic memory

Takes about 3-5 minutes.

### 3. Personalize

After installation, run:

```
@PERSONALIZE.prompt.md
```

This wizard collects:
- Your name and timezone
- Work context (what you do)
- Communication preferences

Your AI will adapt its behavior to match.

### 4. Start Using

You're ready. Some things to try:

**Journal Entry**
```
@Journal
```
Start a guided reflection session.

**Build Something**
```
I want to create a script that backs up my files daily
```
Routes to Architect for planning, then Builder for implementation.

**Use Personas**
```
Switch to Researcher and find recent papers on AI safety
```
Routes to the research specialist.

**Debug an Issue**
```
This script is failing and I can't figure out why
```
Routes to Debugger with systematic debugging methodology.

---

## Features Overview

### Specialist Personas

| Persona | Best For |
|---------|----------|
| **Operator** | Navigation, routing, state tracking (default home base) |
| **Builder** | Scripts, automations, implementations |
| **Researcher** | Web search, documentation, synthesis |
| **Writer** | Emails, docs, polished content |
| **Strategist** | Decisions, frameworks, planning |
| **Debugger** | Troubleshooting, QA, root cause analysis |
| **Architect** | System design, build planning, major refactors |
| **Teacher** | Explaining concepts, guided learning |
| **Librarian** | State sync, filing, coherence audits |

→ See [docs/PERSONAS.md](docs/PERSONAS.md) for full details and routing logic

### Behavioral Rules

13 core rules that shape AI behavior:

1. **Session State Init** — Tracks conversation context automatically
2. **YAML Frontmatter** — Adds provenance to all markdown files
3. **Progress Reporting (P15)** — Prevents false "done" claims
4. **File Protection** — Guards critical directories with `.n5protected`
5. **Debug Escalation** — Breaks failure loops after 3 attempts
6. **Clarifying Questions** — Reduces mistakes from ambiguity
7. **Persona Routing** — Master routing table for specialist switching
8. **Session State Updates** — Periodic state sync
9. **Honest Workflow Reporting** — Scripts = mechanics, AI = semantics
10. **Agent Conflict Gate** — Prevents agent sprawl
11. **Pulse Orchestration** — Recommends parallelization for >5 items
12. **Anti-Hallucination** — "I don't know" is always preferred over guessing
13. **Debug Logging** — Structured logging during active problem-solving

→ See [docs/RULES.md](docs/RULES.md) for full details

### Principles Library

37 codified operational principles organized by category:

**Core Quality:**
- **P15** — Complete Before Claiming (prevents false "done")
- **P16** — Accuracy over speed
- **P17** — Simplicity over sophistication

**Architectural:**
- **P23** — Identify Trap Doors (flag irreversible decisions)
- **P28** — Plans as Code DNA (quality happens in planning)
- **P32** — Simple Over Easy (Rich Hickey's wisdom)

**Building Fundamentals (P35-P39):**
- **P35** — Version, Don't Overwrite
- **P36** — Make State Visible
- **P37** — Design as Pipelines
- **P38** — Isolate by Default, Parallelize Proactively
- **P39** — Audit Everything

Plus 26 more principles covering safety, modularity, error handling, and workflow patterns.

→ See [docs/PRINCIPLES.md](docs/PRINCIPLES.md) for full details

### Skills

N5OS includes packaged skills for advanced workflows:

| Skill | Description |
| --- | --- |
| **meeting-ingestion** | Pull transcripts from Google Drive, generate intelligence blocks |
| **pulse** | Automated build orchestration — spawn parallel workers, validate deposits |
| **close** | Universal close — auto-routes to thread-close, drop-close, or build-close |
| **thread-close** | Close normal conversation threads with artifact tracking |
| **systematic-debugging** | Root cause analysis methodology: reproduce → isolate → hypothesize → fix |
| **frontend-design** | Production-grade UI design with anti-slop guardrails |

→ See individual `Skills/*/SKILL.md` files for documentation

### Block System

Transform meeting transcripts into structured intelligence:

- **B01** — Detailed recap
- **B02** — Commitments extracted
- **B03** — Decisions made
- **B04** — Open questions
- **B05** — Questions raised
- **B06** — Business context

Plus reflection blocks (R01, R02, R06) for journaling.

→ See [docs/BLOCK_SYSTEM.md](docs/BLOCK_SYSTEM.md) for full details

### Semantic Memory (Optional)

With an OpenAI API key, N5OS Ode builds a semantic memory layer:

- Auto-indexes Knowledge/ content
- Enables similarity search across your notes
- Provides context-aware retrieval for every conversation

→ See [docs/SEMANTIC_MEMORY.md](docs/SEMANTIC_MEMORY.md) for setup

### Safety System

Comprehensive protection preventing catastrophic file operations:

- **.n5protected markers** — Directory-level protection against moves/deletes
- **Folder-specific POLICY.md** — Override global preferences at folder level
- **Protected paths and file types** — Auto-review for databases, secrets, system files
- **Blast radius control** — Logged, reversible operations with audit trails

→ See [docs/SAFETY.md](docs/SAFETY.md) for details

---

## Requirements

- **Zo Computer account** — [zo.computer](https://zo.computer)
- **Fresh workspace** — Works best on new or clean workspaces
- **OpenAI API key** — Optional, for semantic memory features

---

## File Structure

After installation:

```
workspace/
├── N5/                         # System intelligence
│   ├── prefs/                  # Preferences and config
│   │   ├── principles/         # 37 operational principles (YAML)
│   │   ├── system/             # System policies
│   │   └── workflows/          # Persona workflow docs
│   ├── scripts/                # Utility scripts (14+)
│   ├── cognition/              # Semantic memory
│   ├── data/                   # Conversation registry
│   └── builds/                 # Build workspaces (Pulse)
├── Knowledge/                  # Long-term reference
│   ├── architectural/          # Principles docs
│   └── content-library/        # Ingested articles and notes
├── Records/                    # Date-organized records
│   └── journal/                # Journal entries
├── Prompts/                    # Reusable workflows
│   ├── Blocks/                 # Block generators
│   └── reflections/            # Reflection templates
├── Skills/                     # Packaged workflows
│   ├── meeting-ingestion/      # Meeting transcript processing
│   ├── pulse/                  # Build orchestration
│   ├── close/                  # Universal close routing
│   ├── thread-close/           # Thread close
│   ├── systematic-debugging/   # Debugging methodology
│   └── frontend-design/        # UI design skill
├── Lists/                      # Structured lists
├── BOOTLOADER.prompt.md        # Installation script
└── PERSONALIZE.prompt.md       # Configuration wizard
```

→ See [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) for details

---

## Philosophy

N5OS Ode is built on these beliefs:

1. **Structure Enables Creativity** — Frameworks free you to focus on what matters
2. **Specialists Beat Generalists** — Focused context produces better results
3. **Memory Makes Intelligence** — Without continuity, each conversation starts from zero
4. **Safety First** — Better to ask than accidentally destroy
5. **Progressive Enhancement** — Start simple, add complexity as needed

→ See [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) for the full story

---

## Documentation

| Doc | Description |
|-----|-------------|
| [PHILOSOPHY.md](docs/PHILOSOPHY.md) | Why N5OS exists, core concepts |
| [NUANCE_MANIFEST.md](docs/NUANCE_MANIFEST.md) | Prompt engineering patterns for AI quality |
| [PERSONAS.md](docs/PERSONAS.md) | 9 specialist personas and routing |
| [ROUTING.md](docs/ROUTING.md) | Persona choreography, handoffs |
| [RULES.md](docs/RULES.md) | 13 behavioral rules, customization |
| [PRINCIPLES.md](docs/PRINCIPLES.md) | 37 operational principles |
| [FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) | Directory layout, conventions |
| [BLOCK_SYSTEM.md](docs/BLOCK_SYSTEM.md) | Block generators for transcripts |
| [BUILD_PLANNING.md](docs/BUILD_PLANNING.md) | Build planning, templates, execution flow |
| [SEMANTIC_MEMORY.md](docs/SEMANTIC_MEMORY.md) | Optional memory layer setup |
| [CONVERSATION_END.md](docs/CONVERSATION_END.md) | Tiered conversation close |
| [CONTEXT_LOADING.md](docs/CONTEXT_LOADING.md) | Dynamic context injection |
| [DEBUG_SYSTEM.md](docs/DEBUG_SYSTEM.md) | Debug logging, pattern detection |
| [SAFETY.md](docs/SAFETY.md) | Protection mechanisms and usage |
| [SITES.md](docs/SITES.md) | Sites protocol, staging/prod patterns |

---

## Customization

N5OS Ode is a starting point, not a cage:

- **Add personas** — Create specialists for your domains
- **Modify rules** — Adapt to your preferences
- **Add principles** — Codify your own operational standards
- **Create prompts** — Build workflows for recurring tasks
- **Extend blocks** — Generate custom intelligence from transcripts
- **Install skills** — Browse the [skills registry](https://agentskills.io) for more capabilities

Everything can be edited in Zo Settings or the workspace.

---

## Acknowledgments

The semantic memory architecture in N5OS Ode is based on foundational work by **[The Fork Project](https://github.com/theforkproject-dev)**. Their [zo-local-memory](https://github.com/theforkproject-dev/zo-local-memory) project established the core patterns for local semantic memory on Zo Computer.

---

## Version

**N5OS Ode v2.0**
Released: February 2026

---

*Structured thinking for structured doing.*

# N5OS Environment — Claude Code Integration

**Owner:** V (Vrijen Attawar)
**System:** N5OS on Zo Computer
**Integration:** MCP bridge provides `n5_protect_check`, `n5_log_bio`, `n5_close_conversation` tools

---

## System Architecture

N5OS is V's production operating system running on Zo Computer. It's organized as a layered system:

```
N5/
├── prefs/           # 37 architectural principles + 27 operational protocols
├── scripts/         # 669+ Python automation scripts
├── config/          # Centralized configuration (ports, webhooks, integrations)
├── data/            # Runtime state, databases, caches
├── builds/          # Project workspaces (200+ active builds)
├── skills/          # Automated workflow systems (50+ deployed)
├── commands/        # Executable recipes for AI execution
└── logs/            # Thread exports, system logs

Integrations/        # External service connections (Recall.ai, Calendly, Careerspan, etc.)
Sites/               # Production websites (protected)
Personal/            # Personal data and records (protected)
Skills/              # Deployed skill definitions with SKILL.md docs
```

**Key Integrations:**
- Recall.ai (meeting intelligence), Calendly (calendar automation)
- Careerspan (talent matching pipeline), n8n (workflow automation)
- Google Drive (document ingestion), Akiflow (task management)

---

## Core Architectural Principles

The system is built on 37 codified principles. The most critical for Claude Code:

### P02: Single Source of Truth (SSOT)
Each fact lives in exactly one canonical location. All other references link to the source rather than duplicating content. Never sync duplicates manually.

**Behavior:** Before creating new structures, search for existing ones. Prefer extending existing rather than creating duplicates.

### P05: Safety, Determinism, and Anti-Overwrite
Prevent data loss through explicit consent, automatic versioning, and audit logging.

**Behavior:**
- Never overwrite protected files without explicit confirmation
- Auto-version on filename conflict: _v2, _v3, etc.
- Require explicit consent for all side-effects (see Safety Requirements below)

### P08: Minimal Context, Maximal Clarity
Keep prompts self-contained while avoiding excessive file loading. Load only what's needed for precision execution.

**Behavior:**
- Use on-demand context loading (see Context Loading Guide below)
- Don't load full preference modules unless specifically needed
- Balance completeness with efficiency

### P15: Complete Before Claiming Complete
Report accurate progress with quantitative metrics. Only mark tasks complete when all requirements are met and verified.

**Behavior:**
- Track progress explicitly (e.g., "13/23 complete, 56%")
- Test all success criteria before marking complete
- If blocked, state what remains rather than claiming done

### P16: Accuracy Over Sophistication
Trustworthy information beats impressive speculation. Provide accurate, conservative facts rather than sophisticated-sounding embellishments.

**Behavior:**
- When uncertain, state facts conservatively
- Make assumptions explicit and flag them
- If you don't know, say so—NEVER invent technical limitations
- Conservative facts over plausible speculation

### P22: Language Selection
Choose programming languages based on task requirements, not familiarity or trends.

**Decision Framework:**
- **Python:** Default for scripts, data analysis, automation, AI/ML work
- **JavaScript/TypeScript:** Web frontends, Node backends, full-stack apps
- **Bash:** Simple file operations, system tasks, quick automation
- **SQL:** Data queries and transformations
- **Go:** Performance-critical services, CLI tools
- **Specialized:** When ecosystem/performance demands it

Consider: V's maintenance burden (non-technical founder), library ecosystem, performance requirements, deployment context.

### P24: Simulation Over Doing
Always dry-run first. Every state-modifying operation must support `--dry-run` mode.

### P25: Code Is Free, Thinking Is Expensive
Strategic thinking is the constraint, not code generation. Use the Think-Plan-Execute framework (see Operational Philosophy below).

---

## Safety Requirements (Critical Always-Active Rules)

**Explicit Consent Required For:**
1. **Scheduling** — Calendar events, cron jobs, scheduled tasks
2. **External Communications** — Emails, webhooks, API calls to external services
3. **Service Management** — Starting processes, opening ports, modifying running services
4. **Destructive Operations** — Deletions, overwrites, git force-push, database drops

**Dry-Run Requirements:**
- Every state-modifying operation MUST support `--dry-run`
- For high-risk ops, enforce dry-run by default until user confirms with explicit flag
- Show diff of proposed changes before execution

**Protocol Search Requirement:**
- Always search for existing protocols/structures before creating new ones
- Check: N5/commands/, existing folder structures, N5/config/, N5/lists/
- Priority: **Recipe > Protocol > Script > Direct ops > Improvisation**

**File Creation Protocol:**
- Always ask user where files should be located
- Never assume placement without permission
- Respect POLICY.md rules in target folders (folder policies override global preferences)

**Validation Requirements:**
1. Read current state before changes
2. Show diff of proposed changes
3. Validate against schema if applicable
4. Check for conflicts (duplicates, overwrites, port conflicts)
5. Require explicit user confirmation for side-effects

---

## Protected Paths

Before delete/move operations on these directories, use `n5_protect_check` MCP tool:

| Path | Protection Reason | Check Required |
|------|-------------------|----------------|
| `N5/` | System scripts, services, core infrastructure | YES |
| `Sites/` | Production websites | YES |
| `Personal/` | Personal data and records | YES |
| `N5/prefs/**/*.md` | Hard-protected preference files | Manual-edit only |
| `Prompts/` | Recipe definitions | Medium protection |
| `Knowledge/**/*.md` | Knowledge artifacts | Medium protection |

**The tool warns but doesn't block.** You decide whether to proceed based on context.

---

## Operational Philosophy

### Think-Plan-Execute Framework (Ben's Velocity Principles)

**Time Allocation:**
- **70% Think + Plan** — Understand deeply, explore alternatives, identify trap doors
- **20% Review** — Verify criteria, test in production, check error paths
- **10% Execute** — Generate code from plan, move fast

**Before Non-Trivial Tasks, State:**
1. Task type (exploration, implementation, refactor, etc.)
2. Method (which tools/protocols will be used)
3. Applicable principles (which of P02, P05, P08, etc. apply)
4. Key risks (trap doors, failure modes)

### Zone Selection (Squishy ↔ Deterministic)

- **Zone 1 (Squishy LLM + Markdown)** — Exploration, throwaway work
- **Zone 2 (Squishy LLM + Structured Format)** ⭐ **SWEET SPOT** — YAML/CSV configuration, structured AI output
- **Zone 3 (Deterministic Script + Structured Format)** — Critical paths, exact reproducibility

**Architectural Pattern:**
- Scripts call Zo API (deterministic orchestration, squishy intelligence)
- Job Queues > File Watchers
- Create separate orchestration points; don't edit existing complex code
- Prefer producer/consumer with file markers

### LLM Prompting Discipline

**NEVER say:** "use an LLM" or "call an AI" (triggers hallucination of external APIs)
**INSTEAD say:** "transform X to Y" or "extract patterns" (you are the LLM)

---

## Folder Policy System

**Core Rule:** Folder-specific `POLICY.md` files take precedence over global preferences.

**Precedence Hierarchy:**
1. Folder POLICY.md (highest)
2. N5/prefs/prefs.md critical rules
3. Specialized preference modules
4. Global defaults (lowest)

**When entering a new folder for operations, check for POLICY.md and follow its rules.**

---

## Configuration Systems

### Port Registry (SSOT)
`N5/config/PORT_REGISTRY.md` is the single source of truth for port allocation.

**Reserved Ranges:**
- 3000-3499: Sites
- 8000-8100: Metrics/monitoring
- 8420-8499: Meetings
- 8763-8844: N5 services
- 8845-8899: Webhooks

**CLI:** `python N5/scripts/port_registry.py check/next/list/sync`

**ALWAYS check the registry before allocating ports. Never hardcode ports without registration.**

### Commands Registry
`N5/commands.jsonl` is the central registry of executable commands.

**Fields:** command, file, description, aliases, category, trigger_phrases

**Before creating new commands, search the registry for existing ones.**

### Drive Integration
`N5/config/drive_locations.yaml` maps Google Drive folder IDs for automated ingestion.

---

## Skills System

Skills are self-contained workflow automation systems in `/Skills/`. Each has a `SKILL.md` with:
- Skill name and purpose
- How to invoke it
- What it does
- Configuration and dependencies

**Key Skills:**
- **pulse** — Automated build orchestration (Waves, Drops, Streams)
- **git-substrate-sync** — GitHub content synchronization
- **resume-decoded** — Resume intelligence extraction
- **human-escalation** / **mentor-escalation** — Escalation routing
- **careerspan-hiring-intel** — Talent pipeline intelligence

**Before implementing workflow automation, check if a skill already exists.**

---

## Naming Conventions

### Scheduled Tasks
Format: `{emoji} {frequency?} {subject}`

**Emoji Legend:**
- 🔧 Maintenance
- 🧠 Intelligence gathering
- 📰 Digests
- 💾 Data operations
- 📊 Analytics
- 📧 Email operations
- 📅 Meetings
- 🎓 Learning
- 📝 Documentation
- ⏰ Automation

**Examples:**
- `🔧 Daily port conflict check`
- `🧠 Careerspan pipeline heartbeat`
- `📰 Morning resonance digest`

**Rules:**
- No version numbers
- No redundant qualifiers
- Frequency optional if implied

### Files & Directories
- **Scripts:** snake_case.py or kebab-case.ts
- **Directories:** kebab-case/
- **Build slugs:** descriptive-slug-name

---

## On-Demand Context Loading

Use `/load-context <context>` to load domain-specific preferences when needed (follows P08: Minimal Context).

| Context | Use For | Loads |
|---------|---------|-------|
| `system_ops` | System admin, file operations, git work | File protection, git protocols, cleanup rules |
| `content_generation` | Writing emails, documents, social posts | Writing style, content templates, voice library |
| `crm_operations` | Contact management, stakeholder tracking | CRM protocols, contact schemas, relationship management |
| `code_work` | Code modifications, multi-file changes | Refactoring protocols, debug logging, testing |
| `scheduling` | Creating scheduled tasks, calendar ops | Task protocol, naming conventions, calendar integration |
| `research` | Deep research, stakeholder analysis | Research protocols, sourcing rules, synthesis patterns |
| `build` | Implementation, refactoring, engineering | Build conventions, planning protocols, architecture patterns |
| `full` | Load all modules | **Use sparingly per P08** |

**Or load specific files:** `/load-context file 'N5/prefs/path/to/module.md'`

**Default state:** Only core principles and safety rules are loaded. Load additional context as tasks require it.

---

## Key Protocol Reference

When working on specific types of tasks, reference these protocols:

**Planning & Execution:**
- `N5/prefs/operations/planning_prompt.md` — Think-Plan-Execute framework
- `N5/prefs/operations/recipe-execution-guide.md` — How to execute recipes
- `N5/prefs/protocols/task_routing_protocol.md` — Task automation routing

**File & State Operations:**
- `N5/prefs/operations/file-creation-protocol.md` — Where to create files
- `N5/prefs/operations/artifact-placement.md` — Canonical locations
- `N5/prefs/system/file-protection.md` — Protection levels
- `N5/prefs/system/folder-policy.md` — Folder policy system

**Scheduling & Automation:**
- `N5/prefs/operations/scheduled-task-protocol.md` — Task naming, verification
- `N5/prefs/operations/digest-creation-protocol.md` — Creating new digests

**Conversation Management:**
- `N5/prefs/operations/conversation-end-v5.md` — Full Close vs Worker Close
- `N5/prefs/operations/thread-closure-triggers.md` — When to end conversations
- `N5/prefs/operations/conversation-initialization.md` — Setup for new conversations

**Advanced Operations:**
- `N5/prefs/operations/backpressure-protocol.md` — System load management
- `N5/prefs/operations/refactoring-protocol.md` — Safe code modification
- `N5/prefs/operations/debug-logging-auto-behavior.md` — Active debugging

**Don't memorize these — search for them when the task requires specialized guidance.**

---

## Session Lifecycle

- **Session context:** `.claude/session-context.md` tracks progress, decisions, and loaded context modules
- **Session close:** Use `/n5-close` to log the session to N5OS
- **Auto-logging:** The `Stop` hook automatically logs sessions on exit

---

## Build Conventions

When creating major new systems or features:

- **Build workspace:** `N5/builds/<slug>/` with `PLAN.md` and `STATUS.md`
- **Scripts:** New scripts go in `N5/scripts/`
- **Integrations:** External tool integrations go in `Integrations/<service>/`
- **Skills:** Deployed skills go in `Skills/<skill-name>/` with `SKILL.md`

**These are conventions, not requirements. Use your judgment based on task scope.**

---

## What This Integration Provides

1. **Protection warnings** before destructive operations (`n5_protect_check`)
2. **Session continuity** via session-context.md
3. **N5OS logging** so sessions are tracked alongside Zo conversations (`n5_close_conversation`)
4. **Bio event logging** for significant milestones (`n5_log_bio`)

---

## What This Integration Does NOT Do

- Override your planning capabilities or judgment
- Block any operations (tools warn only)
- Require specific workflows (protocols are guidance, not mandates)
- Load all context by default (you control what's loaded per P08)

---

## Critical Reminders

**Always Active:**
1. ✅ Check for existing protocols/workflows before improvising
2. ✅ Priority: Recipe > Protocol > Script > Direct ops > Improvisation
3. ✅ State task type, method, principles, risks before non-trivial work
4. ✅ Use `n5_protect_check` before delete/move on N5/, Sites/, Personal/
5. ✅ Never schedule without explicit consent
6. ✅ Support `--dry-run` for all state-modifying operations
7. ✅ Load context only as needed (P08: Minimal Context)
8. ✅ When uncertain, state facts conservatively (P16: Accuracy Over Sophistication)
9. ✅ Respect folder POLICY.md files (they override global preferences)
10. ✅ Check PORT_REGISTRY.md before allocating ports

**Your planning capabilities remain intact.** This integration keeps you informed about the environment so you can work effectively within V's operational philosophy.

---

**Last Updated:** 2026-02-12
**Session Context:** @.claude/session-context.md
**Full Preferences:** N5/prefs/ (37 principles, 27 protocols — load on-demand)

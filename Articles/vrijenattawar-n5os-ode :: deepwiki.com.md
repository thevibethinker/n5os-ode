---
url: https://deepwiki.com/vrijenattawar/n5os-ode
---

# vrijenattawar/n5os-ode

vrijenattawar/n5os-ode

Menu

N5OS Ode Overview
-----------------

Relevant source files

* [README.md](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md)
* [docs/SITES.md](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/docs/SITES.md)
* [install.sh](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/install.sh)

Purpose and Scope
-----------------

This document provides a technical overview of N5OS Ode, a cognitive operating system designed for Zo Computer. It covers the system's architecture, installation mechanism, directory structure, and core subsystems. For detailed information on specific capabilities:

* For AI behavior configuration (personas, rules, principles), see [AI Behavior System](https://deepwiki.com/vrijenattawar/n5os-ode/2-ai-behavior-system)
* For the structured development workflow, see [Build System](https://deepwiki.com/vrijenattawar/n5os-ode/3-build-system)
* For conversation lifecycle management, see [Conversation Management](https://deepwiki.com/vrijenattawar/n5os-ode/4-conversation-management)
* For protection mechanisms, see [Safety and Protection](https://deepwiki.com/vrijenattawar/n5os-ode/5-safety-and-protection)
* For semantic search and knowledge storage, see [Knowledge and Memory](https://deepwiki.com/vrijenattawar/n5os-ode/6-knowledge-and-memory)

What is N5OS Ode
----------------

N5OS Ode is a structured framework that transforms Zo Computer from a general-purpose AI assistant into a domain-specialized thinking partner with persistent memory, specialized operational modes, and safety-enforced workflows.

The system provides:

* **Specialist Personas**: Six focused AI modes (Operator, Builder, Researcher, Writer, Strategist, Debugger) with domain-specific prompts
* **Behavioral Rules**: Persistent instructions that shape AI behavior across all conversations
* **Conversation State**: `SESSION_STATE.md` as source of truth for conversation context, synced to `conversations.db`
* **Structured Outputs**: Block generators (B01-B28, R01-R06) for transforming transcripts into intelligence
* **Safety System**: Multi-layer protection (`.n5protected` markers, `POLICY.md` overrides, file type analysis)
* **Build System**: Structured AI-driven development with `PLAN.md` and `STATUS.md`
* **Semantic Memory**: Optional RAG layer using `N5MemoryClient` with vector embeddings

**Sources**: [README.md 8-26](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L8-L26)

System Architecture
-------------------

The following diagram shows N5OS Ode's major subsystems and their relationships, using actual file and directory names from the codebase.

### Diagram: N5OS Ode System Architecture

```
Knowledge StorageSafety SystemMemory & ContextBuild SystemSpecialist PersonasCore OrchestrationUser Interface LayerHuman UserBOOTLOADER.prompt.md
PERSONALIZE.prompt.md
PLAN.prompt.mdSkills CLIs
meeting_cli.py
pulse.pyBOOTLOADER.prompt.md
Installs personas & rulesOperator Persona
Central routerSESSION_STATE.md
Conversation contextBuilder
Code/automationResearcher
Search/docsWriter
Content creationStrategist
PlanningDebugger
TroubleshootingArchitect
Build planningN5/scripts/init_build.py
Workspace creationN5/builds/slug/PLAN.md
Execution blueprintN5/builds/slug/STATUS.md
Progress trackingN5/builds/slug/meta.json
Machine stateN5MemoryClient
N5/cognition/src/n5_memory.pybrain.db
SQLite + embeddingsconversations.db
Historical trackingn5_load_context.py
Task-specific injection.n5protected markers
Directory guardsPOLICY.md
Folder overridesN5/scripts/n5_protect.py
Protection CLIN5/
System intelligenceKnowledge/
Long-term referenceRecords/
Date-organizedSkills/
Packaged workflowsSites/
Web applications
```

**Sources**: [README.md 8-26](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L8-L26) [README.md 267-285](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L267-L285)

Installation and Bootstrapping Flow
-----------------------------------

N5OS Ode uses a two-stage installation process: filesystem setup via `install.sh`, followed by AI persona/rule installation via `BOOTLOADER.prompt.md`.

### Diagram: Installation Flow

```
User ConfigurationAI InstallationFilesystem SetupUser clones repoinstall.sh
Lines 1-115merge_dir() function
Lines 21-35Copy N5/ to workspace/N5/Copy Prompts/ to workspace/Prompts/Copy Knowledge/ to workspace/Knowledge/Copy Records/ to workspace/Records/Copy Skills/ to workspace/Skills/Copy templates/ to workspace/templates/Copy BOOTLOADER.prompt.md
PERSONALIZE.prompt.md
PLAN.prompt.md
README.mdRemove n5os-ode/ directory
Line 65User runs @BOOTLOADER.prompt.mdInstall 6 personas:
Operator, Builder, Researcher,
Writer, Strategist, DebuggerInstall 6 behavioral rules:
Session State, Frontmatter,
P15 Progress, File Protection,
Debug Logging, Clarifying QuestionsEnsure N5/, Knowledge/,
Records/, Prompts/ existInitialize config filesUser runs @PERSONALIZE.prompt.mdCollect name & timezoneCollect work contextCollect communication prefsWrite to N5/prefs/prefs.mdSystem ready for use
```

**Sources**: [install.sh 1-115](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/install.sh#L1-L115) [README.md 29-78](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L29-L78)

### Installation Components

| Component | File Path | Purpose |
| --- | --- | --- |
| **Filesystem Installer** | `install.sh` | Merges directories to workspace root, no-clobber copy |
| **AI Bootloader** | `BOOTLOADER.prompt.md` | Installs personas and behavioral rules into Zo Settings |
| **Personalization Wizard** | `PERSONALIZE.prompt.md` | Collects user preferences and writes to `N5/prefs/prefs.md` |
| **Merge Function** | `install.sh:21-35` | Copies directory contents without overwriting existing files |

**Sources**: [install.sh 1-115](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/install.sh#L1-L115) [README.md 29-78](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L29-L78)

Directory Structure
-------------------

N5OS Ode organizes the workspace into five primary namespaces, each with distinct responsibilities.

### Diagram: Directory Namespace Architecture

```
Root LevelCapability LayerData PlaneControl Planeworkspace/N5/
System intelligenceN5/prefs/
User preferences & principlesN5/config/
System configurationN5/scripts/
Utility scriptsN5/cognition/
Semantic memory (optional)N5/builds/
Build workspacesKnowledge/
Long-term referenceKnowledge/content-library/
Ingested articlesRecords/
Date-organized recordsRecords/journal/
Journal entriesRecords/AARs/
After-action reportsPrompts/
Reusable workflowsPrompts/Blocks/
B01-B28 generatorsPrompts/reflections/
Reflection templatesSkills/
Packaged workflowsSkills/meeting-ingestion/
Transcript processingSkills/pulse/
Build orchestrationSites/
Web applicationsBOOTLOADER.prompt.mdPERSONALIZE.prompt.mdPLAN.prompt.mdtemplates/
Document templates
```

**Sources**: [README.md 265-285](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L265-L285)

### Directory Responsibilities

| Namespace | Path | Responsibility |
| --- | --- | --- |
| **Control Plane** | `N5/` | System configuration, scripts, build workspaces, semantic memory |
| **Data Plane** | `Knowledge/`, `Records/` | Long-term reference storage, date-organized historical records |
| **Capability Layer** | `Prompts/`, `Skills/`, `Sites/` | Reusable workflows, packaged skills, web applications |
| **Root Level** | `*.prompt.md`, `templates/` | System bootstrapping, document templates |

**Sources**: [README.md 265-285](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L265-L285)

### Key Subdirectories

| Subdirectory | Purpose | Key Files |
| --- | --- | --- |
| `N5/prefs/` | User preferences, principles library, operational procedures | `prefs.md`, `context_manifest.yaml`, principles (P01-P36) |
| `N5/config/` | System configuration | `config.yaml`, `confidence_thresholds.json`, `drive_locations.yaml` |
| `N5/scripts/` | Utility CLIs | `init_build.py`, `n5_protect.py`, `conversation_sync.py`, `debug_logger.py` |
| `N5/cognition/` | Semantic memory system | `n5_memory.py` (N5MemoryClient), `brain.db`, `brain.hnsw` |
| `N5/builds/` | Build workspaces | `slug/PLAN.md`, `slug/STATUS.md`, `slug/meta.json` |
| `Skills/meeting-ingestion/` | Meeting transcript processing | `meeting_cli.py`, `meeting_registry.db` |
| `Skills/pulse/` | Build orchestration | `pulse.py` |
| `Sites/` | Web applications | `slug/`, `slug-staging/`, `zosite.json` |

**Sources**: [README.md 267-285](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L267-L285)

Core Subsystems
---------------

N5OS Ode consists of six major subsystems that work together to provide structured AI assistance.

### 1. AI Behavior System

Controls how the AI behaves through personas, rules, and dynamic context loading.

| Component | Implementation | Purpose |
| --- | --- | --- |
| **Specialist Personas** | Installed via `BOOTLOADER.prompt.md` | Six focused AI modes: Operator (router), Builder (implementation), Researcher (search/synthesis), Writer (content), Strategist (planning), Debugger (troubleshooting) |
| **Behavioral Rules** | Installed via `BOOTLOADER.prompt.md` | Six rules: Session State init, YAML frontmatter, P15 progress tracking, file protection, debug logging, clarifying questions |
| **Principles Library** | `N5/prefs/principles/P*.md` | 18 codified principles (P01-P36) including P15 (Complete Before Claiming), P28 (Plans as Code DNA), P32 (Simple Over Easy) |
| **Context Loader** | `N5/scripts/n5_load_context.py` | Dynamically injects task-specific files based on `N5/prefs/context_manifest.yaml` |

For details, see [AI Behavior System](https://deepwiki.com/vrijenattawar/n5os-ode/2-ai-behavior-system).

**Sources**: [README.md 104-145](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L104-L145)

### 2. Build System

Structured AI-driven development workflow with planning and execution phases.

| Component | File Path | Purpose |
| --- | --- | --- |
| **Build Initialization** | `N5/scripts/init_build.py` | Creates workspace at `N5/builds/slug/` with `PLAN.md`, `STATUS.md`, `meta.json` |
| **Planning Phase** | Templates in `templates/build/` | Architect persona creates detailed plan, Level Upper reviews, user approves |
| **Execution Phase** | Builder persona reads `PLAN.md` | Autonomous execution, phase-by-phase updates to `STATUS.md` |
| **Orchestration** | `meta.json` wave definitions | Supports sequential (v1) and wave-based parallel (v2) execution |

For details, see [Build System](https://deepwiki.com/vrijenattawar/n5os-ode/3-build-system).

**Sources**: [README.md 87-92](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L87-L92)

### 3. Conversation Management

Tracks conversation state and lifecycle with structured outputs.

| Component | File Path | Purpose |
| --- | --- | --- |
| **Session State** | `SESSION_STATE.md` | Source of truth for current conversation context |
| **Conversation Sync** | `N5/scripts/conversation_sync.py` | ETL process syncing `SESSION_STATE.md` to `conversations.db` every 3-5 exchanges |
| **Conversation Registry** | `conversations.db` | SQLite database with tables: conversations, artifacts, decisions, learnings, issues |
| **Block System** | `Prompts/Blocks/` | B01-B28 intelligence blocks, R01-R06 reflection blocks |
| **Journal System** | `Records/journal/`, `journal.db` | Guided reflection sessions (@Morning Pages, @Evening Reflection) |

For details, see [Conversation Management](https://deepwiki.com/vrijenattawar/n5os-ode/4-conversation-management).

**Sources**: [README.md 22-24](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L22-L24) [README.md 148-159](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L148-L159)

### 4. Safety and Protection

Multi-layer defense-in-depth protection against destructive operations.

| Layer | Implementation | Mechanism |
| --- | --- | --- |
| **Layer 1** | `.n5protected` markers | Directory-level protection against moves/deletes |
| **Layer 2** | `POLICY.md` files | Folder-specific rules override global preferences |
| **Layer 3** | `N5/prefs/safety/safety-rules.md` | Global safety constraints |
| **Layer 4** | File type analysis | Auto-detect `.db`, `.key`, secrets files |
| **Layer 5** | PII tracking | Marked sensitive directories via `n5_protect.py mark-pii` |
| **CLI** | `N5/scripts/n5_protect.py` | Commands: protect, unprotect, check, list, mark-pii |

For details, see [Safety and Protection](https://deepwiki.com/vrijenattawar/n5os-ode/5-safety-and-protection).

**Sources**: [README.md 232-240](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L232-L240) [docs/SITES.md 166-187](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/docs/SITES.md#L166-L187)

### 5. Knowledge and Memory

Semantic search and structured knowledge storage.

| Component | File Path | Purpose |
| --- | --- | --- |
| **Semantic Memory** | `N5/cognition/src/n5_memory.py` | N5MemoryClient class with vector embeddings, hybrid search (semantic + BM25), cross-encoder reranking |
| **Brain Database** | `N5/cognition/brain.db` | SQLite storage for documents, chunks, embeddings |
| **HNSW Index** | `N5/cognition/brain.hnsw` | Fast approximate nearest neighbor search |
| **Knowledge Directory** | `Knowledge/` | Long-term reference storage, indexed by semantic memory |
| **Records** | `Records/` | Date-organized records, AARs, journal entries |

For details, see [Knowledge and Memory](https://deepwiki.com/vrijenattawar/n5os-ode/6-knowledge-and-memory).

**Sources**: [README.md 196-205](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L196-L205)

### 6. Sites Protocol

Immutable infrastructure pattern for web application deployment.

| Concept | Pattern | Implementation |
| --- | --- | --- |
| **Directory Structure** | `Sites/slug/`, `Sites/slug-staging/` | Production vs staging separation |
| **Service Naming** | Label: `slug` or `slug-staging` | Workdir: `Sites/slug/` or `Sites/slug-staging/` |
| **Promotion** | `promote_site.sh slug` | Rsync from staging to production, restart service |
| **Protection** | `.n5protected` markers | `Sites/.n5protected`, per-site markers |
| **Configuration** | `zosite.json` | Site metadata: name, ports, entrypoint |

For details, see [Sites Protocol](https://deepwiki.com/vrijenattawar/n5os-ode/7-sites-protocol).

**Sources**: [docs/SITES.md 1-218](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/docs/SITES.md#L1-L218)

Key File Paths Reference
------------------------

This table maps high-level concepts to actual file paths and code entities in the codebase.

| Concept | File Path | Line Numbers | Key Entities |
| --- | --- | --- | --- |
| **Filesystem Installation** | `install.sh` | 1-115 | `merge_dir()` function (21-35) |
| **AI Installation** | `BOOTLOADER.prompt.md` | - | Installs 6 personas, 6 rules |
| **User Configuration** | `PERSONALIZE.prompt.md` | - | Writes to `N5/prefs/prefs.md` |
| **Session State** | `SESSION_STATE.md` | - | Source of truth for conversation |
| **Conversation Sync** | `N5/scripts/conversation_sync.py` | - | ETL to `conversations.db` |
| **Build Initialization** | `N5/scripts/init_build.py` | - | Creates `N5/builds/slug/` workspace |
| **Build Plan** | `N5/builds/slug/PLAN.md` | - | Checklist, phases, success criteria |
| **Build Status** | `N5/builds/slug/STATUS.md` | - | Quick status, activity log, blockers |
| **Build Metadata** | `N5/builds/slug/meta.json` | - | Machine-readable state, worker stats |
| **Semantic Memory Client** | `N5/cognition/src/n5_memory.py` | - | `N5MemoryClient` class |
| **Brain Database** | `N5/cognition/brain.db` | - | SQLite: documents, chunks, embeddings |
| **HNSW Index** | `N5/cognition/brain.hnsw` | - | Fast vector search index |
| **Conversation Registry** | `conversations.db` | - | Tables: conversations, artifacts, decisions, learnings, issues |
| **Context Loader** | `N5/scripts/n5_load_context.py` | - | Task-specific context injection |
| **Context Manifest** | `N5/prefs/context_manifest.yaml` | - | Category → files mapping |
| **Protection CLI** | `N5/scripts/n5_protect.py` | - | Commands: protect, unprotect, check, list, mark-pii |
| **Protection Markers** | `.n5protected` | - | Directory-level protection |
| **Policy Overrides** | `POLICY.md` | - | Folder-specific safety rules |
| **Debug Logger** | `N5/scripts/debug_logger.py` | - | Logs to `DEBUG_LOG.jsonl`, detects circular patterns |
| **Meeting CLI** | `Skills/meeting-ingestion/scripts/meeting_cli.py` | - | Commands: status, pull, process |
| **Pulse CLI** | `Skills/pulse/scripts/pulse.py` | - | Commands: start, status |
| **Site Promotion** | `promote_site.sh` | - | Rsync staging to production |
| **Site Config** | `Sites/slug/zosite.json` | - | name, ports, entrypoint |

**Sources**: [install.sh 1-115](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/install.sh#L1-L115) [README.md 1-370](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L1-L370) [docs/SITES.md 1-218](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/docs/SITES.md#L1-L218)

System Requirements
-------------------

| Requirement | Details |
| --- | --- |
| **Platform** | Zo Computer account ([zo.computer](https://zo.computer)) |
| **Workspace** | Fresh or clean workspace recommended |
| **Optional** | OpenAI API key for semantic memory features (N5MemoryClient) |
| **Python** | Python 3.x for CLI scripts in `N5/scripts/` and `Skills/` |

**Sources**: [README.md 255-260](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L255-L260)

After reviewing this overview:

1. For installation instructions, see [Installation and Setup](https://deepwiki.com/vrijenattawar/n5os-ode/1.1-installation-and-setup)
2. For directory structure details, see [Directory Structure](https://deepwiki.com/vrijenattawar/n5os-ode/1.2-directory-structure)
3. For core philosophy and principles, see [Core Philosophy and Principles](https://deepwiki.com/vrijenattawar/n5os-ode/1.3-core-philosophy-and-principles)
4. For AI behavior configuration, see [AI Behavior System](https://deepwiki.com/vrijenattawar/n5os-ode/2-ai-behavior-system)
5. For structured development workflows, see [Build System](https://deepwiki.com/vrijenattawar/n5os-ode/3-build-system)

**Sources**: [README.md 1-370](https://github.com/vrijenattawar/n5os-ode/blob/e374d69c/README.md#L1-L370)
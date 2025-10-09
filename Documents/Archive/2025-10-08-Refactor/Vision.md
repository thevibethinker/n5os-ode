# N5 OS: Comprehensive Refactor & Vision Document

**Date**: 2025-10-08  
**Version**: 1.0  
**Author**: Zo (AI Systems Architect Persona)  
**For**: Vrijen Attawar (Founder, Careerspan)

---

## Executive Summary

This document captures the comprehensive refactoring of N5 OS—the personal cognitive operating system built on top of Zo Computer—and defines the platonic ideal architecture we're building towards. 

**Current State**: Functional but bloated (972 files, 68/100 health score)  
**Target State**: Clean, maintainable cognitive OS (384 files, 85/100 health score)  
**Time Investment**: 2 weeks discovery/analysis, 2-3 weeks design/execution  
**Expected Impact**: 60% file reduction, 25% health improvement, robust pointer system

### The Vision

N5 OS is not just workflow automation—it's **cognitive augmentation**. A digital extension of V that:
- Thinks the way V would (the most disciplined version)
- Maintains stable and evolving knowledge about V and Careerspan
- Tracks everything from ideas to investors via intelligent lists
- Processes information through LLM-based direct ingestion
- Dispatches commands via natural language (Incantum)
- Protects critical files with tiered safety mechanisms
- Operates as a portable, self-describing knowledge system

### The Journey

**Phases 1-2 Complete** (Discovery & Analysis):
- Mapped 972 files across 5 system layers
- Identified 187 duplicates from single backup event (19% bloat)
- Discovered command registry abandonment (92% gap)
- Found robust safety layer (n5_safety.py) protecting all operations
- Validated high-quality knowledge (48 SPO triples, 31 system improvements tracked)

**Phases 3-4 Ahead** (Design & Execution):
- Design ideal file structure (Knowledge/Lists at root)
- Implement intelligent pointer/breadcrumb system
- Populate command registry (34 missing commands)
- Delete 588 obsolete files (60% reduction)
- Achieve architectural coherence

---

## Table of Contents

1. [The Refactor Journey](#the-refactor-journey)
2. [The Platonic Ideal: N5 OS Vision](#the-platonic-ideal)
3. [Core Architecture Components](#core-architecture-components)
4. [System Relationships Diagram](#system-relationships-diagram)
5. [Key Subsystems Deep Dive](#key-subsystems-deep-dive)
6. [Data Architecture](#data-architecture)
7. [Execution Flow](#execution-flow)
8. [Roadmap to Ideal State](#roadmap-to-ideal-state)
9. [Success Metrics](#success-metrics)
10. [Appendices](#appendices)

---

## The Refactor Journey

### Why Refactor N5 OS?

**Pain Points Identified**:
1. **File bloat** (972 files, many duplicates)
2. **Misaligned storage** (knowledge buried in OS, not portable)
3. **Inconsistent workflows** (commands not properly registered)
4. **Brittle pointers** (hardcoded paths break on rename)
5. **Discovery broken** (92% of commands not in registry)

**Root Cause**: N5 OS evolved organically during development, accumulating technical debt from a September 20, 2025 backup event that was never cleaned up.

### Phase 1: Discovery (Complete)

**Objective**: Map the entire N5 OS comprehensively

**5 Discovery Passes**:

#### Phase 1A: Structural Topology
- **Discovered**: 1,035 files in N5/, 347 in N5_mirror/, 34 root directories
- **Key Finding**: N5_mirror is obsolete staging area, can be deleted
- **Bloat**: 50 timestamped script duplicates, 200+ backup files
- **Proposal**: Move Knowledge/Lists to root for portability ("self-unpacking Rosetta stone")

#### Phase 1B: Command Layer Inventory
- **Discovered**: 62 function files (37 base + 25 duplicates)
- **Critical Gap**: Only 3 commands in commands.jsonl (jobs-*, vs 37 function files)
- **Key Finding**: Command registry abandonment—34 commands missing
- **Pattern**: All duplicates from Sept 20, 13:22:52 (single backup event)

#### Phase 1C: Script Layer Inventory
- **Discovered**: 174 scripts (79 base + 66 duplicates + 29 author_command/)
- **Critical Infrastructure**: 
  - **Incantum Engine** (incantum_engine.py) - Natural language command dispatcher
  - **n5_safety.py** - Imported by ALL 73 user-facing scripts (SPOF)
  - **listclassifier.py** - Intelligent list assignment by content/URL
- **Architecture**: Scripts are composable primitives, chained by function files

#### Phase 1D: Knowledge & Preferences Layer
- **Discovered**: 54 knowledge files, 46 list files
- **Quality**: High (48 SPO triples with confidence 0.95-1.0, 31 system-upgrades tracked)
- **Governance**: Sophisticated POLICY.md system, tiered file protection (HARD/MEDIUM/AUTO)
- **Key System**: Direct Processing (LLM-based ingestion using Zo directly, no API key)
- **Issue**: All 40+ knowledge files have obsolete N5_mirror anchors in metadata

#### Phase 1E: Infrastructure & Integration Layer
- **Discovered**: 328 runtime logs, 71 backups (368KB—surprisingly lean)
- **Integrations**: GDrive/Gmail well-documented, Howie paused, calendar partial
- **Underutilized**: Workflows (example-only), modules (1 file), jobs system (no data)
- **Cleanup Needed**: 52 tmp_execution files not cleaned up

**Discovery Summary**:
- **Total Files**: ~972
- **Total Duplicates**: ~187 (19%)
- **Root Cause**: Single Sept 20 backup event
- **Health Score**: 68/100 (functional but improvable)

### Phase 2: Analysis (Complete)

**Objective**: Diagnose problems, identify patterns, prioritize remediation

**4 Analysis Passes**:

#### Phase 2A: Overlap & Redundancy Analysis
- **Root Cause Confirmed**: 187 duplicates all from single backup event (not systemic)
- **Safety Assessment**: 123 files safe to delete immediately, 24 need verification
- **N5_mirror**: 347 files, obsolete, merge then delete
- **Impact**: Low (19% duplication, ~20MB storage, moderate maintenance burden)
- **Deduplication Plan**: Delete ~588 files total (60% reduction: 972 → 384 files)

#### Phase 2B: Gap Analysis
- **Command Registry**: 92% gap (3 registered vs 37 functions)
- **Incantum Triggers**: Likely unpopulated (engine exists but can't map NL → commands)
- **Workflows/Modules**: 95% gap (underutilized, should deprecate)
- **Jobs System**: 100% inactive (commands exist, zero data)
- **Article Tracking**: 100% unused (schema exists, file empty)
- **Overall Flowchart vs Reality**: ~44% gap

#### Phase 2C: Dependency & Relationship Mapping
- **Function → Script**: 37 hardcoded paths (HIGH brittleness)
- **Script → Module**: 73 scripts import n5_safety.py (CRITICAL SPOF)
- **Schema Dependencies**: 16 schemas, ~80 scripts (LOW brittleness, robust)
- **Circular Dependencies**: ✅ NONE (clean architecture)
- **Brittleness Score**: 5.3/10 (MEDIUM, needs breadcrumb system)
- **Critical Path**: 9 breakage points in list operation chain

#### Phase 2D: Tech Debt Categorization
- **Total Issues**: 92 categorized
  - Structural: 28 (duplicates, bloat, organization)
  - Code: 23 (registry, SPOFs, brittleness)
  - Documentation: 19 (missing READMEs, broken refs)
  - Architecture: 15 (inconsistencies, no pointer system)
  - Feature: 7 (inactive systems)
- **Priority**: P0: 8, P1: 24, P2: 38, P3: 22
- **Effort**: 18 trivial, 42 easy, 24 moderate, 7 hard, 1 very hard
- **Quick Wins**: 1 day of work = 60% file reduction

**Analysis Summary**:
- Single root cause for most issues (Sept 20 backup)
- Core systems work well (lists, knowledge, safety, direct processing)
- Critical gaps: registry, triggers, pointer system
- Clear path to 85/100 health via systematic refactor

### Phases 3-4: Ahead

**Phase 3 (Design)** - ~1 week:
- Design ideal file structure
- Design pointer/breadcrumb system
- Design command registry population
- Create migration plan with rollback

**Phase 4 (Execution)** - ~1-2 weeks:
- Delete 588 obsolete files
- Populate registry + triggers
- Implement pointer system
- Move Knowledge/Lists to root
- Validate and test

**Expected Outcome**: Clean, maintainable cognitive OS (85/100 health)

---

## The Platonic Ideal: N5 OS Vision

### Core Philosophy

**N5 OS is a cognitive operating system**—a digital extension of V that embodies:

1. **Cognitive Principles Over Workflows**: Not just task automation, but thinking the way V would
2. **Stable + Evolving Knowledge**: Separating historical truth from contemporary understanding
3. **Intelligence at Every Layer**: From list classification to conflict resolution
4. **Portability First**: Knowledge systems are self-describing, OS-agnostic
5. **Safety by Default**: Tiered file protection, dry-run mode, explicit confirmations
6. **Natural Language Interface**: Incantum maps conversational requests to commands
7. **Single Source of Truth**: Each fact lives in one place, referenced everywhere else

### The Ideal Architecture

```
/home/workspace/
│
├── Knowledge/              [PORTABLE - Self-unpacking Rosetta Stone]
│   ├── schemas/            - How to interpret this knowledge
│   ├── stable/             - Historical/biographical (changes rarely)
│   │   ├── bio.md          - Founder profiles, motivations
│   │   ├── company.md      - Careerspan comprehensive info
│   │   └── timeline.md     - Chronological milestones
│   ├── evolving/           - Contemporary info (changes frequently)
│   │   ├── facts.jsonl     - SPO triples (knowledge graph)
│   │   └── article_reads.jsonl - Reading history
│   ├── architectural/      - How N5 operates
│   │   ├── architectural_principles.md - Core principles (Rule-of-Two, SSOT)
│   │   └── ingestion_standards.md - How to process information
│   └── README.md           - Rosetta stone: how to use this knowledge
│
├── Lists/                  [PORTABLE - Self-describing tracker system]
│   ├── schemas/            - List schemas
│   ├── ideas.jsonl         - General ideas
│   ├── must-contact.jsonl  - People to reach out to
│   ├── system-upgrades.jsonl - N5 improvements (31 items tracked)
│   ├── [custom lists]      - Extensible: groceries, investors, etc.
│   ├── POLICY.md           - List governance rules
│   └── README.md           - How to use lists
│
├── N5/                     [OS ONLY - No user data]
│   ├── commands/           - Function files (orchestration prompts)
│   │   ├── lists-add.md    - How to add to list
│   │   ├── docgen.md       - Generate command catalog
│   │   └── [37 commands]   - All command definitions
│   ├── scripts/            - Executable primitives
│   │   ├── n5_safety.py    - CRITICAL: Safety layer (all scripts import)
│   │   ├── incantum_engine.py - Natural language dispatcher
│   │   ├── listclassifier.py - Intelligent list assignment
│   │   └── [79 scripts]    - Composable behaviors
│   ├── schemas/            - Data validation schemas (JSON Schema 2020-12)
│   │   ├── lists.item.schema.json
│   │   ├── knowledge.facts.schema.json
│   │   └── [16 schemas]
│   ├── config/             - System configuration
│   │   └── commands.jsonl  - Command registry (POPULATED with 37 commands)
│   ├── prefs/              - System preferences
│   │   └── prefs.md        - Global preferences (HARD protection)
│   ├── runtime/            - Execution traces (retained per policy)
│   └── backups/            - Rolling backups (retention policy)
│
├── Documents/              [USER-FACING DOCS]
│   ├── N5.md               - System entry point/overview
│   └── N5_OS_Refactor_and_Vision.md - This document
│
└── [User Workspace]        [DOMAIN WORK]
    ├── Careerspan/         - Company-specific work
    ├── Meetings/           - Meeting notes
    └── Articles/           - Saved articles
```

### Design Principles (The Platonic Ideal)

#### 1. Self-Unpacking Rosetta Stone

**Knowledge and Lists are portable**:
- Can be exported with their schemas
- Remain interpretable without N5 OS
- Schemas travel with data
- READMEs explain structure

**Example**: Export `Knowledge/` → another system can read facts.jsonl using knowledge.facts.schema.json without any N5-specific code.

#### 2. Command → Function → Script Architecture

**Three-layer execution**:

```
Command (trigger phrase)
    ↓
Function File (orchestration prompt)
    ↓
Script(s) [optional, composable]
    ↓
Execution
```

**Function files are source of truth**:
- Human-readable orchestration instructions
- Explicit script invocation (not implied)
- Can chain multiple scripts
- Can be pure LLM (no scripts)
- Versioned and documented

**Commands.jsonl is index**:
- Auto-generated or manually maintained
- Enables command discovery
- Used by Incantum for NL mapping
- Contains metadata (args, side effects, permissions)

#### 3. Intelligent Breadcrumb System

**Every file reference is tracked**:
- Function → Script paths
- Script → Module imports
- Knowledge → Knowledge cross-refs
- Schema → Data validation

**On file rename/move/delete**:
- System detects all references
- Proposes cascade updates
- Validates changes
- Logs to audit trail
- Fails fast with clear errors

**Validation strategies**:
- On startup: Validate critical chains
- On command invoke: Validate dependencies
- Periodic: Scan for broken references
- Report: Health dashboard

#### 4. Tiered Safety Architecture

**File Protection Tiers**:

**HARD PROTECTION** (manual edit only):
- N5/prefs.md
- Knowledge/architectural/architectural_principles.md
- Knowledge/architectural/ingestion_standards.md
- Documents/N5.md

**MEDIUM PROTECTION** (validate before edit):
- Lists/*.jsonl (all user data)
- Knowledge/stable/*.md (historical)
- Knowledge/evolving/*.jsonl (facts, articles)
- N5/config/commands.jsonl

**AUTO-GENERATED** (regenerate freely):
- N5/commands.md (catalog)
- N5/index.md (system index)
- Lists/*.md (list documentation)

**Implementation**: n5_safety.py enforces this at every write operation

#### 5. Natural Language Dispatch (Incantum)

**User says**: "Add Lynnette Scott to my must-contact list—we met at Civana, she's HR at CMC looking for AI talent"

**Incantum processes**:
1. Parse natural language intent
2. Lookup in incantum_triggers.json: "add to list" → `lists-add` command
3. Validate command exists in commands.jsonl
4. Load function file: commands/lists-add.md
5. Execute orchestration:
   - Classify person (CRM? must-contact? other?)
   - Extract structured data (name, body, tags)
   - Invoke scripts/n5_lists_add.py with args
   - Script uses listclassifier if needed
   - Validates against schema
   - Writes to must-contact.jsonl
6. Return result to user

**Result**: Entry added to must-contact.jsonl with proper structure, tags, priority.

#### 6. Direct Processing (LLM-Based Ingestion)

**When V says**: "Process this 10-page document about Careerspan's new GTM strategy"

**Direct processing flow**:
1. Invoke direct-knowledge-ingest command
2. Function file loads document, sends to Zo (me) with structured prompts
3. I (Zo) analyze document, extract:
   - Facts → facts.jsonl (SPO triples)
   - Company info → company.md updates
   - Timeline events → timeline.md
   - Glossary terms → glossary.md
   - Source attribution → sources.md
4. Sync analysis checks for contradictions with existing knowledge
5. Conflict resolution (manual or LLM-assisted)
6. Reservoir updates applied
7. V receives summary of changes

**Key**: No external API calls, no size limits, full context maintained (me as execution engine).

#### 7. Lists as Core Cognitive Tool

**Lists are V's extended memory**:
- **ideas.jsonl** - Capture fleeting thoughts
- **must-contact.jsonl** - People to reach out to (recruiting, networking)
- **system-upgrades.jsonl** - N5 improvements (31 tracked, continuous improvement culture)
- **fundraising-opportunity-tracker.jsonl** - Investors, rounds, stages
- **groceries.jsonl** - Personal errands
- **[Custom lists]** - Extensible for any tracking need

**Intelligence at every operation**:
- **Classification**: listclassifier.py auto-assigns lists by URL/keywords
- **Dynamic creation**: If list doesn't exist, creates with barebones schema
- **Validation**: Every write validates against schema
- **Health monitoring**: lists-health-check detects issues
- **Deduplication**: lists-similarity-scanner finds duplicates
- **Schema extensibility**: Lists can add custom fields (additionalProperties: true)

**Example**: Add LinkedIn profile → classifier detects URL pattern → assigns to `crm` or creates `contacts` list → validates data → stores with tags

#### 8. Preferences as Governance

**POLICY.md per subsystem**:
- Global: N5/prefs.md (never auto-schedule, always dry-run first, ask where files go)
- Lists: Lists/POLICY.md (atomic operations, validation, rollbacks)
- Knowledge: [Future] Knowledge/POLICY.md

**Hierarchy**:
- Folder policies override global prefs
- Architectural principles override all
- Order of precedence clearly defined

**Examples**:
- Global: "Never auto-schedule"
- Lists policy: "Allow auto-create lists" (overrides "ask first" for list ops)
- Result: Lists can be created atomically, but scheduled tasks still need permission

---

## Core Architecture Components

### Layer 1: Knowledge Layer (Stable + Evolving)

**Purpose**: Store all information about V, Careerspan, and the world

**Components**:

#### Stable Knowledge
- **bio.md**: Founder profiles (Vrijen, Logan), motivations, philosophy
- **company.md**: Careerspan overview, history, strategy, product, mission (~1500 words)
- **timeline.md**: Chronological milestones
- **glossary.md**: Terms, acronyms, spellings
- **sources.md**: Canonical references

**Characteristics**: Changes rarely, comprehensive, narrative-driven

#### Evolving Knowledge
- **facts.jsonl**: SPO triples (Subject-Predicate-Object)
  - Example: `{"subject": "Careerspan", "predicate": "founded_by", "object": "Vrijen Attawar and Logan Currie", "confidence": 1.0, "source": "Company Overview"}`
  - Current: 48 facts, confidence 0.95-1.0
  - Append-only, source-attributed, machine-readable
- **article_reads.jsonl**: Articles read, summaries, outlets, authors
- **direct_processing.md**: Contemporary observations, notes

**Characteristics**: Changes frequently, structured, fact-based

#### Architectural Knowledge
- **architectural_principles.md**: Core principles (Rule-of-Two, SSOT, Voice tiers, etc.)
- **ingestion_standards.md**: How to process information (ontology weights, voice levels)
- **operational_principles.md**: Operating guidelines

**Characteristics**: Rarely changes, governs all operations

### Layer 2: Lists Layer (Trackers)

**Purpose**: Track everything V needs to stay on top of

**Core Lists**:
- **ideas.jsonl** (4 items): General ideas
- **must-contact.jsonl** (1 item): People to reach out to
- **system-upgrades.jsonl** (31 items): N5 improvements ← Most active, shows continuous improvement culture
- **fundraising-opportunity-tracker.jsonl**: Investors, stages, rounds
- **[Custom lists]**: Extensible for any need

**Schema Structure** (lists.item.schema.json):
```json
{
  "required": ["id", "created_at", "title", "status"],
  "properties": {
    "id": "uuid",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime",
    "title": "string (max 200 chars)",
    "status": "enum [open, pinned, done, archived, planned]",
    "body": "string (optional)",
    "tags": "array of strings",
    "priority": "H/M/L",
    "links": "array of URLs",
    "project": "string",
    "due": "date",
    "notes": "string"
  },
  "additionalProperties": true
}
```

**Key Feature**: `additionalProperties: true` allows custom fields per list (e.g., must-contact might add `"company"`, `"role"`)

**Intelligence**:
- Auto-classification by content/URL (listclassifier.py)
- Dynamic list creation with barebones schema
- Schema validation at every write
- Health monitoring and deduplication

### Layer 3: Command Layer (Orchestration)

**Purpose**: Define how to execute operations

**Components**:

#### Commands Registry (commands.jsonl)
```json
{
  "name": "lists-add",
  "version": "0.2.0",
  "workflow": "single-shot",
  "summary": "Add item to list with intelligent assignment",
  "args": [
    {"name": "title", "type": "string", "required": true},
    {"name": "list", "type": "string", "required": false},
    {"name": "body", "type": "string", "required": false}
  ],
  "flags": ["--dry-run", "--priority"],
  "side_effects": ["writes:lists/*.jsonl"],
  "permissions_required": ["list_write"],
  "entry_point": "function_file"
}
```

**Status in Ideal**: All 37 commands registered

#### Function Files (commands/*.md)
Human-readable orchestration prompts that define multi-step workflows.

**Example**: commands/lists-add.md
```markdown
# `lists-add`

Version: 0.2.0
Summary: Add item to list with intelligent assignment

## Inputs
- title : string (required) — Item title
- list : string (optional) — Target list slug
- body : string (optional) — Item description
- tags : array (optional) — Tags

## Execution Flow
1. If list not specified:
   - Invoke listclassifier.py with title + body
   - Get suggested list + rationale
2. Load list schema from registry (lists/index.jsonl)
3. Validate input against schema
4. Invoke: python N5/scripts/n5_lists_add.py --title="..." --list="..."
5. Script handles:
   - UUID generation
   - Timestamp creation
   - Data validation
   - File write with n5_safety.py
6. Return: Item ID + confirmation

## Examples
N5: Add "Lynnette Scott — HR at CMC" to must-contact
N5: Add "Explore AI agents for recruiting" to ideas
```

**Characteristics**:
- Explicit script invocation (not implied)
- Can chain multiple scripts
- Can be pure LLM (no script, just prompts for Zo)
- Versioned and documented

#### Scripts (scripts/*.py)
Atomic, reusable behaviors.

**Example**: n5_lists_add.py
- Imports n5_safety.py (protection layer)
- Imports listclassifier.py (if needed)
- Loads schema, validates input
- Reads list registry to get target file
- Generates UUID, timestamps
- Validates against schema
- Writes with safety checks
- Returns result

**Composability**: Scripts can be chained by function files for complex operations.

### Layer 4: Execution Layer (Incantum + Safety)

**Purpose**: Translate natural language to commands, protect critical operations

#### Incantum Engine (incantum_engine.py)

**Natural language dispatcher**:
1. Receives user input: "check list system health"
2. Normalizes text
3. Searches incantum_triggers.json:
   ```json
   {
     "trigger": "check list health",
     "aliases": ["list health check", "validate lists"],
     "command": "lists-health-check"
   }
   ```
4. Fuzzy matching via Jaccard similarity
5. Maps to command: `lists-health-check`
6. Tries multiple script naming patterns:
   - N5/scripts/n5_lists_health_check.py
   - N5/scripts/n5_lists-health-check.py
   - scripts/lists_health_check.py
7. Executes script with safety layer
8. Returns result

**Status in Ideal**: Fully populated with 37+ triggers

#### Safety Layer (n5_safety.py)

**Imported by ALL user-facing scripts** (73 scripts).

**Responsibilities**:
1. **Permission checks**: Validate user can perform operation
2. **Dry-run mode**: Check --dry-run flag or N5_DRY_RUN env var
3. **File protection**: Enforce HARD/MEDIUM/AUTO tiers
4. **Execute with safety**: Wrapper function for all commands
5. **Logging**: Audit trail for every operation

**Usage pattern**:
```python
from n5_safety import execute_with_safety, load_command_spec

command_spec = load_command_spec("lists-add")

def execute_lists_add(args):
    # Actual command logic
    pass

# Wrapped execution
result = execute_with_safety(command_spec, args, execute_lists_add)
```

**Critical**: If n5_safety.py breaks, entire system fails (SPOF by design, protected)

### Layer 5: Integration Layer (External Systems)

**Purpose**: Connect to external tools and services

#### Built-In Integrations
- **Google Drive**: 5-step workflow documented in prefs
  1. Verify integration (list_app_tools)
  2. Get file metadata
  3. Download file
  4. Fetch via curl if needed
  5. Read with read_file

- **Gmail**: Auto-process forwarded emails
  - Daily digest scan (6 AM ET)
  - Newsletter/article detection
  - Trigger direct processing

#### AI-to-AI Coordination
- **Howie Integration**: Paused until needed
  - Preferences defined in Knowledge/howie/preferences.md
  - Ready to activate with command

#### Future Integrations
- **Calendar**: Partial (mentioned, not implemented)
- **Coding Agent**: Via perform_coding_task tool

### Layer 6: Infrastructure Layer

**Purpose**: Maintenance, backups, security

#### System Maintenance
- **docgen**: Generate command catalog (auto-updated)
- **index-rebuild**: Rebuild system index
- **core-audit**: Audit critical files
- **lists-health-check**: Validate list integrity

#### Backups
- **Rolling backups**: Retention policy (keep last N, archive old)
- **Git tracking**: Critical files version-controlled
- **Backup triggers**: Before bulk operations, on-demand
- **Recovery**: Git checkout or restore from backups/

#### Security
- **File protection**: n5_safety.py enforces tiers
- **Dry-run by default**: All commands support --dry-run
- **Explicit confirmations**: Required for side effects
- **Audit logging**: Every operation logged

---

## System Relationships Diagram

### N5 OS Architecture Overview

See diagram below for visual representation of component relationships.

![N5 OS Architecture - System Relationships](../Images/n5_architecture_relationships.png)

### Diagram Key Components

**Flow Overview**:
1. **User (V)** → Ingestion Layer (NL, Email, Direct)
2. **Incantum Engine** (hexagon, red) → Natural language dispatcher
3. **Command Registry** (commands.jsonl + triggers) → Lookup tables
4. **Function Files** (orchestration prompts) → lists-add.md, knowledge-ingest.md, etc.
5. **Scripts Layer** (executable code) → Atomic behaviors
6. **n5_safety.py** (hexagon, red) → CRITICAL SPOF, imported by ALL scripts
7. **Validation Schemas** → JSON Schema 2020-12 validation
8. **Data Layer** (cylinders) → Knowledge Store + Lists Store
9. **Runtime Infrastructure** → Logs, backups, audit trail
10. **Breadcrumb System** (dashed hexagon) → To be implemented

**Critical Paths** (red, thick strokes):
- Incantum Engine (command dispatch)
- n5_safety.py (protection layer)
- Function Files → Scripts chain

**Data Flow** (cyan):
- Knowledge Store (stable + evolving)
- Lists Store (ideas, contacts, upgrades)

**New Systems** (purple, dashed):
- Breadcrumb System (dependency tracker, validator, cascade updater)

---

## Key Subsystems Deep Dive

### Subsystem 1: Lists System (Most Complete)

**Purpose**: Core tracker for everything V needs to stay on top of

**Commands** (10):
- lists-add (with classification)
- lists-create (new list)
- lists-find (search)
- lists-export (to various formats)
- lists-docgen (generate docs)
- lists-set (update fields)
- lists-move (between lists)
- lists-pin (mark important)
- lists-promote (to action)
- lists-health-check (validate)

**Data Flow**:
```
User: "Add John Doe to contacts, met at conference"
    ↓
Incantum: "add to" → lists-add command
    ↓
Function File: lists-add.md orchestration
    ↓
listclassifier.py: Analyze "John Doe" + "conference" → suggest "contacts" or "must-contact"
    ↓
n5_lists_add.py: 
  - Load lists/index.jsonl (registry)
  - Check if "contacts" list exists
  - If not: Create with barebones schema
  - Generate UUID, timestamps
  - Validate against lists.item.schema.json
  - Write to lists/contacts.jsonl via n5_safety.py
    ↓
Result: {"id": "uuid", "title": "John Doe", "body": "met at conference", "tags": ["conference"], "status": "open"}
```

**Why It Works**:
- Schema-driven (validation at every step)
- Intelligent classification (reduces manual selection)
- Dynamic creation (lists created as needed)
- Health monitoring (detect issues proactively)
- Extensible (custom fields via additionalProperties)

**Current Usage**: 31 system-upgrades items tracked (V actively uses this for continuous improvement)

### Subsystem 2: Knowledge System (High Quality)

**Purpose**: Store all information about V, Careerspan, and the world

**Commands** (4):
- knowledge-add (add fact)
- knowledge-find (search)
- knowledge-ingest (batch ingestion)
- direct-knowledge-ingest (LLM-based, unlimited size)

**Direct Processing Flow**:
```
User: "Process this document: [10-page Careerspan GTM strategy]"
    ↓
direct-knowledge-ingest command
    ↓
Function File: Sends document + structured prompts to Zo (me)
    ↓
Zo (LLM Processing):
  - Extract facts → SPO triples
  - Identify company info → company.md updates
  - Timeline events → timeline.md
  - New terms → glossary.md
  - Sources → sources.md
    ↓
Sync Analysis:
  - Check for contradictions with existing knowledge
  - Flag conflicts for resolution
  - Manual or LLM-assisted reconciliation
    ↓
Reservoir Updates:
  - Append facts to facts.jsonl
  - Update company.md (SSOT)
  - Log source attribution
    ↓
Result: Knowledge base updated, V receives summary of changes
```

**Data Quality**:
- 48 SPO triples (confidence 0.95-1.0)
- All source-attributed
- Entity-typed (person:, company:, etc.)
- Machine-readable (queryable, inferrable)

**Why It Works**:
- LLM-based (no size limits, full context)
- Zo as execution engine (no API key, conversational)
- SSOT principle (each fact lives once)
- Conflict resolution (contradictions handled)
- Source tracking (traceability)

### Subsystem 3: Command System (Needs Completion)

**Purpose**: Define and discover all N5 operations

**Current State**:
- 37 function files exist
- Only 3 in commands.jsonl (92% gap)
- Incantum triggers likely unpopulated

**Ideal State**:
- All 37 commands registered
- Incantum triggers for each command (+ aliases)
- Function files as SSOT
- commands.jsonl as index

**Registry Population Plan**:
1. Parse all 37 function files
2. Extract metadata (name, version, summary, args)
3. Generate commands.jsonl entries
4. Validate against commands.schema.json
5. Create incantum triggers (NL phrases → command names)
6. Test end-to-end dispatch

**Example Entry**:
```json
{
  "name": "lists-add",
  "version": "0.2.0",
  "workflow": "single-shot",
  "summary": "Add item to list with intelligent assignment",
  "args": [
    {"name": "title", "type": "string", "required": true},
    {"name": "list", "type": "string", "required": false}
  ],
  "function_file": "commands/lists-add.md",
  "script": "scripts/n5_lists_add.py",
  "tags": ["lists", "add", "create"]
}
```

### Subsystem 4: Safety System (Fully Functional)

**Purpose**: Protect critical files, enforce dry-run, audit operations

**Architecture**:
```
ALL User-Facing Scripts (73)
    ↓
    Import n5_safety.py
    ↓
execute_with_safety(command_spec, args, execute_function)
    ↓
Safety Checks:
  1. Validate command_spec (from registry)
  2. Check permissions (can user do this?)
  3. Check dry-run mode (--dry-run flag or env var)
  4. Check file protection tier:
     - HARD: Refuse write, require manual edit
     - MEDIUM: Validate, show preview, confirm
     - AUTO: Allow write
  5. Execute function (if checks pass)
  6. Log to audit trail
    ↓
Result or Error
```

**File Protection Tiers** (from prefs.md):

**HARD** (manual only):
- N5/prefs.md
- Knowledge/architectural/architectural_principles.md
- Documents/N5.md

**MEDIUM** (validate first):
- Lists/*.jsonl
- Knowledge/**/*.md
- N5/config/commands.jsonl

**AUTO** (regenerate):
- N5/commands.md
- Lists/*.md
- N5/index.md

**Why It Works**:
- Centralized (single source of safety logic)
- Imported by all (enforced universally)
- Extensible (easy to add new protections)
- Dry-run by default (safety-first philosophy)
- Clear errors (fails fast with actionable messages)

### Subsystem 5: Pointer/Breadcrumb System (To Be Implemented)

**Purpose**: Track all file references, cascade updates on changes

**Requirements** (from Phase 2C):

**Track**:
1. File metadata (path, type, checksum, last modified)
2. Relationships (references TO, references FROM)
3. Dependency graph (depth, breadth, criticality)

**Cascade Update Rules**:

**On file rename**:
1. Detect all files referencing old path (via dependency graph)
2. Group by reference type:
   - Function → Script paths
   - Scripts: Update import statement
   - Markdown: Update link target
   - Registry: Update path fields
3. For each group, apply update strategy:
   - Function files: Replace path string
   - Scripts: Update import statement
   - Markdown: Update link target
   - Registry: Update path fields
4. Validate all updates succeeded
5. Log to audit trail
6. Run smoke tests on affected commands

**On file delete**:
1. Detect all dependents
2. Warn of breakage (list affected files)
3. Require confirmation
4. Option to delete dependents recursively
5. Option to stub out references

**Validation**:
- On startup: Validate critical chains (Function → Script → Module → Schema)
- On command invoke: Validate dependencies available
- Periodic: Scan for broken references
- Report: Health dashboard

**Implementation Design** (Phase 3):
```
N5/system/
├── dependencies.jsonl     - Complete dependency graph
├── pointer_validator.py   - Validate references
├── cascade_updater.py     - Update on rename/move
└── health_checker.py      - Periodic scans
```

**Brittleness Addressed**:
- Function → Script: HIGH → LOW (tracked, validated, auto-updated)
- Script → Module: MEDIUM → LOW (import validation)
- Cross-references: MEDIUM → LOW (link validation)
- Overall: 5.3/10 → 2/10 (robust)

---

## Data Architecture

### Knowledge Graph (facts.jsonl)

**Structure**: Subject-Predicate-Object (SPO) triples

**Example**:
```json
{
  "subject": "Careerspan",
  "predicate": "founded_by",
  "object": "Vrijen Attawar and Logan Currie",
  "confidence": 1.0,
  "source": "Company Overview",
  "date_added": "2025-09-20",
  "entities": ["person:Vrijen", "person:Logan", "company:Careerspan"]
}
```

**Benefits**:
- Machine-readable (queryable)
- Inferrable (reasoning over triples)
- Source-attributed (traceability)
- Confidence-scored (trust levels)
- Entity-typed (semantic understanding)

**Operations**:
- Add fact: Append to facts.jsonl with validation
- Query facts: Filter by subject/predicate/object
- Infer facts: Reasoning over existing triples
- Resolve conflicts: Compare contradictory facts, choose source/confidence

### List Items Schema

**Base Schema** (lists.item.schema.json):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "N5 List Item",
  "type": "object",
  "required": ["id", "created_at", "title", "status"],
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "title": {"type": "string", "maxLength": 200},
    "status": {"enum": ["open", "pinned", "done", "archived", "planned"]},
    "body": {"type": "string"},
    "tags": {"type": "array", "items": {"type": "string"}},
    "priority": {"enum": ["H", "M", "L"]},
    "links": {"type": "array", "items": {"type": "string", "format": "uri"}},
    "project": {"type": "string"},
    "due": {"type": "string", "format": "date"},
    "notes": {"type": "string"}
  },
  "additionalProperties": true
}
```

**Key**: `additionalProperties: true` allows custom fields

**Custom List Example** (must-contact.jsonl):
```json
{
  "id": "uuid",
  "created_at": "2025-10-04T00:33:09Z",
  "title": "Lynnette Scott — HR at CMC",
  "body": "Met at Civana. Senior HR Manager @ CMC (cement). Interested in AI talent.",
  "status": "open",
  "priority": "H",
  "tags": ["HR", "AI", "Civana", "CMC", "Houston"],
  "company": "CMC",
  "role": "Senior Human Resources Manager",
  "contact_type": "recruiter"
}
```

**Custom fields**: `company`, `role`, `contact_type` (not in base schema, allowed via additionalProperties)

### Registry Pattern (Lists)

**lists/index.jsonl**:
```json
{"slug": "ideas", "title": "Ideas List", "path_jsonl": "Lists/ideas.jsonl", "path_md": "Lists/ideas.md", "created_at": "2025-09-18", "tags": ["general"]}
{"slug": "must-contact", "title": "Must Contact", "path_jsonl": "Lists/must-contact.jsonl", "path_md": "Lists/must-contact.md", "created_at": "2025-09-20", "tags": ["crm", "recruiting"]}
{"slug": "system-upgrades", "title": "System Upgrades", "path_jsonl": "Lists/system-upgrades.jsonl", "path_md": "Lists/system-upgrades.md", "created_at": "2025-09-19", "tags": ["system", "improvement"]}
```

**Benefits**:
- SSOT for list metadata
- Dynamic path resolution (scripts read from registry, not hardcoded)
- Extensible (add new lists without code changes)
- Validated (against lists.registry.schema.json)

---

## Execution Flow

### Example: Adding an Item to a List

**User Input**: "Add Lynnette Scott to my contacts—we met at Civana, she's HR at CMC looking for AI talent"

**Step 1: Incantum Dispatch**
```
Incantum receives: "Add Lynnette Scott to my contacts..."
    ↓
Normalize: "add" + "contacts" + context
    ↓
Search incantum_triggers.json:
  {"trigger": "add to list", "aliases": ["add item", "create entry"], "command": "lists-add"}
    ↓
Fuzzy match: "add" + "contacts" → lists-add (95% confidence)
    ↓
Map to command: lists-add
```

**Step 2: Command Lookup**
```
Load commands.jsonl:
  {"name": "lists-add", "function_file": "commands/lists-add.md", ...}
    ↓
Load function file: N5/commands/lists-add.md
    ↓
Parse orchestration instructions
```

**Step 3: Function Execution**
```
Function file orchestration:
  1. Extract structured data:
     - title: "Lynnette Scott — HR at CMC"
     - body: "Met at Civana. Senior HR Manager..."
     - tags: ["HR", "AI", "Civana", "CMC"]
     - list: "contacts" (from user input)
  
  2. If list not specified or ambiguous:
     - Invoke listclassifier.py
     - Analyze: title + body + tags
     - Pattern match: "HR" + "recruiting" → suggest "must-contact"
     - Return: ("must-contact", "HR + recruiting keywords detected")
  
  3. Load registry:
     - Read Lists/index.jsonl
     - Check if "must-contact" exists → Yes
     - Get path: "Lists/must-contact.jsonl"
  
  4. Invoke script:
     python N5/scripts/n5_lists_add.py \
       --title="Lynnette Scott — HR at CMC" \
       --list="must-contact" \
       --body="Met at Civana..." \
       --tags="HR,AI,Civana,CMC" \
       --priority="H"
```

**Step 4: Script Execution (n5_lists_add.py)**
```python
# Import safety layer
from n5_safety import execute_with_safety, load_command_spec

# Load command spec
command_spec = load_command_spec("lists-add")

def execute_lists_add(args):
    # 1. Load schema
    schema = load_schema("Lists/schemas/lists.item.schema.json")
    
    # 2. Generate item
    item = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "body": args.body,
        "status": "open",
        "tags": args.tags.split(","),
        "priority": args.priority
    }
    
    # 3. Validate against schema
    validator = Draft202012Validator(schema)
    validator.validate(item)
    
    # 4. Read current list
    list_path = Path(f"Lists/{args.list}.jsonl")
    items = read_jsonl(list_path)
    
    # 5. Append new item
    items.append(item)
    
    # 6. Write with safety
    write_jsonl(list_path, items)  # n5_safety enforces protection
    
    # 7. Return result
    return {"id": item["id"], "list": args.list, "status": "added"}

# Execute with safety wrapper
result = execute_with_safety(command_spec, args, execute_lists_add)
```

**Step 5: Safety Checks (n5_safety.py)**
```python
def execute_with_safety(command_spec, args, execute_function):
    # 1. Check permissions
    if command_spec.permissions_required:
        validate_permissions(command_spec.permissions_required)
    
    # 2. Check dry-run mode
    if args.dry_run or os.getenv("N5_DRY_RUN"):
        print("DRY RUN: Would execute", command_spec.name)
        return {"dry_run": True}
    
    # 3. Check file protection
    for side_effect in command_spec.side_effects:
        if "writes:" in side_effect:
            file_path = side_effect.split(":")[1]
            protection = get_file_protection(file_path)
            
            if protection == "HARD":
                raise Error("Cannot auto-write HARD-protected file")
            elif protection == "MEDIUM":
                # Show preview, require confirmation
                confirm = get_user_confirmation(file_path)
                if not confirm:
                    return {"cancelled": True}
    
    # 4. Execute function
    try:
        result = execute_function(args)
        
        # 5. Log to audit trail
        log_audit(command_spec.name, args, result)
        
        return result
    except Exception as e:
        log_error(command_spec.name, e)
        raise
```

**Step 6: Result**
```
Item added successfully:
{
  "id": "e4aaa009-2d17-4d92-a274-ba3ee108845a",
  "created_at": "2025-10-04T00:33:09Z",
  "title": "Lynnette Scott — HR at CMC",
  "body": "Met at Civana. Senior HR Manager @ CMC (cement). Interested in AI talent.",
  "status": "open",
  "priority": "H",
  "tags": ["HR", "AI", "Civana", "CMC"]
}

Stored in: Lists/must-contact.jsonl
```

**User sees**: "Added Lynnette Scott to must-contact list (high priority)"

---

## Roadmap to Ideal State

### Current State (Post-Phase 2)

**Health**: 68/100
**Files**: 972
**Issues**: 92 (P0: 8, P1: 24, P2: 38, P3: 22)
**Duplication**: 19% (187 files from Sept 20 backup)

### Phase 3: Design (1 week)

**Objectives**:
1. Design ideal file structure
2. Design pointer/breadcrumb system
3. Design command registry population
4. Design migration plan with rollback

**Deliverables**:
- Ideal directory structure specification
- Pointer system architecture document
- Command registry population plan
- File-by-file migration plan
- Rollback procedures

### Phase 4: Execution (1-2 weeks)

**Objectives**: Implement Phase 3 designs

**Week 1: Quick Wins + Critical Fixes**

**Day 1-2: Cleanup (P0-P1)**
- [ ] Delete 187 timestamped duplicates (automated)
- [ ] Compare N5/ vs N5_mirror/ critical files
- [ ] Delete N5_mirror/ (347 files)
- [ ] Delete nested N5/N5/ (2 files)
- [ ] Clean tmp_execution/ (52 files)
- [ ] Result: -588 files (60% reduction: 972 → 384)

**Day 3-4: Critical Infrastructure (P0)**
- [ ] Protect n5_safety.py (ensure backups, git tracking)
- [ ] Populate commands.jsonl with 34 missing commands
- [ ] Validate all 37 command entries
- [ ] Populate incantum_triggers.json with NL triggers
- [ ] Test Incantum end-to-end dispatch

**Day 5: Documentation (P1)**
- [ ] Create N5/README.md (system overview)
- [ ] Create N5/scripts/README.md (script guide)
- [ ] Create N5/commands/README.md (command guide)
- [ ] Update Documents/N5.md (entry point)

**Week 2: Architecture + Pointer System (P1)**

**Day 6-7: File Structure Refactor**
- [ ] Create /home/workspace/Knowledge/ structure
- [ ] Create /home/workspace/Lists/ structure
- [ ] Move knowledge files to Knowledge/stable/ and Knowledge/evolving/
- [ ] Move list files to Lists/
- [ ] Update all references (40+ knowledge files, registry paths)
- [ ] Create READMEs (self-unpacking Rosetta stone docs)

**Day 8-9: Pointer System Implementation**
- [ ] Design dependency tracking manifest
- [ ] Implement pointer_validator.py (validate references)
- [ ] Implement cascade_updater.py (update on rename/move)
- [ ] Implement health_checker.py (periodic scans)
- [ ] Test cascade updates on sample renames

**Day 10: Architecture Cleanup (P1)**
- [ ] Deprecate workflows/ system (archive)
- [ ] Deprecate or define modules/ (consolidate into scripts/)
- [ ] Standardize command architecture (document both patterns or choose one)
- [ ] Fix broken cross-references (create stubs or remove)
- [ ] Fix N5_mirror anchors in metadata (40 files)

**Week 3 (Optional): Polish + Testing**

**Day 11-12: Validation + Testing**
- [ ] Run all 37 commands (smoke tests)
- [ ] Validate all Function → Script chains
- [ ] Validate all Schema → Data conformance
- [ ] Test Incantum with various NL inputs
- [ ] Test pointer system cascade updates

**Day 13-14: Polish**
- [ ] Resolve versioned scripts (v2, _fixed, choose production)
- [ ] Decision on jobs system (remove or implement)
- [ ] Decision on article tracking (implement or remove)
- [ ] Decision on Golden/ (complete or archive)
- [ ] Clean up remaining P2/P3 items (opportunistic)

**Day 15: Final Validation**
- [ ] Full system health check
- [ ] Validate against Phase 2 success metrics
- [ ] Document any remaining tech debt
- [ ] Create maintenance runbook

### Target State (Post-Phase 4)

**Health**: 85/100
**Files**: ~384 (60% reduction)
**Issues**: ~20 remaining (P2/P3 only, P0/P1 resolved)
**Duplication**: 0% (all cleaned up)

**Improvements**:
- ✅ Command registry populated (37/37 commands)
- ✅ Incantum functional (NL dispatch works)
- ✅ Pointer system implemented (robust references)
- ✅ Knowledge/Lists at root (portable, self-describing)
- ✅ File bloat eliminated (588 files removed)
- ✅ Documentation complete (READMEs, guides)
- ✅ Architecture consistent (standardized patterns)

---

## Success Metrics

### Quantitative Metrics

**File Count**:
- Current: 972 files
- Target: 384 files
- Reduction: 60%

**Duplication**:
- Current: 19% (187 duplicates)
- Target: 0%

**Command Registry**:
- Current: 3/37 (8%)
- Target: 37/37 (100%)

**Broken References**:
- Current: ~50 (cross-refs) + 40 (N5_mirror anchors) = 90
- Target: 0

**Health Score**:
- Current: 68/100
- Target: 85/100
- Improvement: +17 points (25%)

### Qualitative Metrics

**System Coherence**:
- Current: Two command architectures, unclear SSOT, underutilized systems
- Target: Single SSOT (function files), consistent patterns, deprecated unused systems

**Discoverability**:
- Current: 92% of commands undiscoverable (not in registry)
- Target: All commands discoverable via registry, Incantum, and catalog

**Maintainability**:
- Current: Brittle pointers (manual updates), no validation
- Target: Robust breadcrumb system, automatic cascade updates, health monitoring

**Portability**:
- Current: Knowledge/Lists buried in N5/, not self-describing
- Target: Knowledge/Lists at root with schemas and READMEs, exportable

**User Experience**:
- Current: Confusion about which files are production, commands don't work via NL
- Target: Clean file structure, natural language dispatch works seamlessly

### Validation Checkpoints

**Phase 3 (Design) Complete**:
- [ ] Ideal architecture documented and approved
- [ ] Migration plan detailed with rollback procedures
- [ ] Pointer system design validated
- [ ] Risk assessment complete

**Phase 4 Week 1 Complete**:
- [ ] File count reduced to ~384 (-588 files)
- [ ] Commands.jsonl populated (37/37)
- [ ] Incantum triggers populated
- [ ] Basic documentation created
- [ ] Smoke test: 5 sample commands work end-to-end

**Phase 4 Week 2 Complete**:
- [ ] Knowledge/Lists moved to root
- [ ] Pointer system implemented
- [ ] Architecture cleanup complete (workflows/modules deprecated)
- [ ] All broken references fixed
- [ ] Validation: Sample rename cascades correctly

**Phase 4 Final**:
- [ ] Health score: 85/100+
- [ ] All P0/P1 issues resolved
- [ ] Full system validation passed
- [ ] Maintenance runbook created
- [ ] User acceptance: V confirms system works as intended

---

## Appendices

### Appendix A: Key Files Reference

**Critical Files** (HARD protection):
- `/home/workspace/N5/prefs.md` - System preferences
- `/home/workspace/Knowledge/architectural/architectural_principles.md` - Core principles
- `/home/workspace/Knowledge/architectural/ingestion_standards.md` - Ingestion rules
- `/home/workspace/Documents/N5.md` - System entry point

**Important Files** (MEDIUM protection):
- `/home/workspace/Lists/*.jsonl` - All list data
- `/home/workspace/Knowledge/stable/*.md` - Historical knowledge
- `/home/workspace/Knowledge/evolving/facts.jsonl` - Knowledge graph
- `/home/workspace/N5/config/commands.jsonl` - Command registry

**Infrastructure Files**:
- `/home/workspace/N5/scripts/n5_safety.py` - Safety layer (SPOF)
- `/home/workspace/N5/scripts/incantum_engine.py` - NL dispatcher
- `/home/workspace/N5/scripts/listclassifier.py` - List classification
- `/home/workspace/N5/schemas/*.json` - All validation schemas (16 total)

### Appendix B: Command Catalog (Ideal State)

**Lists Commands** (10):
- lists-add, lists-create, lists-find, lists-export, lists-docgen
- lists-set, lists-move, lists-pin, lists-promote, lists-health-check

**Knowledge Commands** (4):
- knowledge-add, knowledge-find, knowledge-ingest, direct-knowledge-ingest

**System Commands** (5):
- docgen, index-rebuild, index-update, digest-runs, core-audit

**Git Commands** (2):
- git-audit, git-check

**Timeline Commands** (2):
- careerspan-timeline, careerspan-timeline-add

**Jobs Commands** (3):
- jobs-scrape, jobs-add, jobs-review

**Utility Commands** (5):
- hygiene-preflight, file-protector, grep-search-command-creation, incantum-quickref, flow-run

**Total**: 37 commands

### Appendix C: Tech Debt Summary (Post-Phase 2)

**P0 (Critical)** - 8 issues:
- Command registry 92% empty
- Incantum triggers unpopulated
- n5_safety.py SPOF (protect)
- Commands.jsonl vs function files unclear

**P1 (High)** - 24 issues:
- 187 timestamped duplicates
- N5_mirror obsolete (347 files)
- Knowledge at root (architectural)
- Pointer system missing
- Workflows/modules redundant
- Documentation gaps (READMEs)

**P2 (Medium)** - 38 issues:
- Code quality improvements
- Documentation completion
- Minor structural cleanup

**P3 (Low)** - 22 issues:
- Future features (calendar, Howie)
- Minor cleanups
- Nice-to-haves

### Appendix D: Glossary

**N5 OS**: Personal cognitive operating system built on Zo Computer  
**Zo Computer**: AI Computer platform (cloud server + AI agent)  
**Incantum**: Natural language command dispatcher  
**Function File**: Orchestration prompt (multi-step workflow definition)  
**Script**: Atomic, reusable behavior (Python file)  
**SSOT**: Single Source of Truth (each fact lives in one place)  
**SPO Triple**: Subject-Predicate-Object (knowledge graph structure)  
**SPOF**: Single Point of Failure (critical dependency)  
**Breadcrumb System**: Pointer tracking with cascade updates  
**Direct Processing**: LLM-based ingestion (using Zo, no API key)  
**Lists**: Tracker system (ideas, contacts, opportunities, etc.)  
**Knowledge Reservoirs**: Files storing different types of knowledge  
**Rule-of-Two**: Load max 2 config files (architectural principle)  
**Rosetta Stone**: Self-describing data (schemas travel with data)

### Appendix E: Contact & Resources

**Primary Stakeholder**: Vrijen Attawar (V)  
**Company**: Careerspan  
**Platform**: Zo Computer (https://va.zo.computer)  
**Support**: Discord community (https://discord.gg/zocomputer)

**Key Documents**:
- This document: `/home/workspace/Documents/N5_OS_Refactor_and_Vision.md`
- System entry: `/home/workspace/Documents/N5.md`
- Preferences: `/home/workspace/N5/prefs.md`
- Principles: `/home/workspace/Knowledge/architectural/architectural_principles.md`

**Phase 1-2 Analysis** (Conversation Workspace):
- Phase 1A: Structural Topology
- Phase 1B: Command Layer Inventory
- Phase 1C: Script Layer Inventory
- Phase 1D: Knowledge & Preferences
- Phase 1E: Infrastructure & Integration
- Phase 2A: Overlap & Redundancy
- Phase 2B: Gap Analysis
- Phase 2C: Dependency Mapping
- Phase 2D: Tech Debt Categorization

---

## Document History

**Version 1.0** (2025-10-08):
- Initial comprehensive refactor and vision document
- Phases 1-2 complete (Discovery & Analysis)
- Ready for Phase 3 (Design)

**Next Update**: Post-Phase 3 (add design specifications)

---

*This document serves as the north star for N5 OS refactoring. It captures both where we've been (the journey) and where we're going (the platonic ideal). All design and execution decisions should align with this vision.*

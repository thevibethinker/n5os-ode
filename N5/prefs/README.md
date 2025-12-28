# N5 Preferences System v3.0

**Date:** 2025-11-02  
**Status:** Production

---

## Quick Start

### For AI/LLM Loading

**Primary entry point:**
Load: file 'N5/prefs/prefs.md'

This lightweight index contains:
- Critical always-load rules
- Module directory
- Context-aware loading guide

### For Humans

**Navigate by topic:**
- **Principles** → principles/ folder (37 YAML files)
- **Operations** → operations/ folder (27 protocols)
- **System** → system/ folder (governance)
- **Communication** → communication/ folder (voice, style)
- **Strategic** → strategic/ folder (thinking frameworks)

---

## Structure Overview

N5/prefs/
├── prefs.md                      ← Start here
├── README.md                     ← This file
├── principles/                   ← 37 architectural principles (YAML)
│   ├── P00.1_llm_first.yaml
│   ├── P01_human_readable_first.yaml
│   ├── ... (37 total)
│   └── principles_index.yaml
├── operations/                   ← 27 operational protocols
│   ├── planning_prompt.md
│   ├── conversation-end.md
│   ├── scheduled-task-protocol.md
│   └── ... (27 total)
├── strategic/                    ← Strategic frameworks
│   └── thinking_prompt.md
├── system/                       ← System governance
│   ├── navigator_prompt.md
│   ├── file-protection.md
│   ├── folder-policy.md
│   └── safety.md
├── communication/                ← V-voice standards
│   ├── voice.md
│   └── ... (V-voice examples)
└── integration/                  ← Tool integrations

---

## New in v3.0 (Nov 2025)

**Architectural Redesign Complete:**
- 37 principles codified in YAML format
- Schema validation (N5/schemas/principle.schema.json)
- 8 personas integrated with v2.0+ standard
- Pre-flight protocol standardized (5 steps)
- 3 cognitive prompts active

**Key Changes:**
- Principles moved from markdown to YAML
- All principles now schema-validated
- Automatic trigger-based principle loading
- Persona routing standardized
- Risk assessment framework integrated

See: file 'N5/builds/architectural-redesign-v1/MIGRATION_HISTORY.md'

---

## Principles Directory (NEW)

**Location:** N5/prefs/principles/

37 YAML files, each defining a core principle:
- Unique ID (P##)
- Trigger conditions
- Pattern specification
- Examples (good/bad)
- Anti-patterns
- Related principles

**Categories:**
- Core (5): P0.1-P4
- Safety (7): P5-P7, P11, P19, P21, P23
- Quality (7): P15-P16, P18, P20, P28, P30, P33
- Design (5): P8-P10, P13-P14
- Execution (1): P29
- Advanced (2): P36-P37

**Remaining (10):** P22, P24-P27, P31-P32, P34-P35

**Usage:**
- Principles auto-load via trigger conditions
- Personas embed 8 relevant principles
- Schema: N5/schemas/principle.schema.json
- Guide: file 'Knowledge/architectural/PRINCIPLE_USAGE_GUIDE.md'

---

## Operations Directory

**Location:** N5/prefs/operations/

27 operational protocols:
- Planning and execution frameworks
- Conversation management
- File operations
- Scheduling and automation
- Debugging and logging
- Refactoring protocols

**Key Protocols:**
- planning_prompt.md - Think-Plan-Execute framework
- conversation-end.md - Thread closure workflow
- scheduled-task-protocol.md - Agent safety requirements
- debug-logging-auto-behavior.md - Active debugging discipline

---

## System Directory

**Location:** N5/prefs/system/

System governance and structure:
- navigator_prompt.md - N5 organization guide
- file-protection.md - Protection rules
- folder-policy.md - Directory structure
- nuance-manifest.md - Behavior patterns
- safety.md - Safety enforcement

---

## Communication Directory

**Location:** N5/prefs/communication/

V-voice standards and examples:
- voice.md - Voice policy
- Examples of V-voice content
- Communication guidelines

---

## Strategic Directory

**Location:** N5/prefs/strategic/

Strategic thinking frameworks:
- thinking_prompt.md - Analysis patterns
- Strategic decision-making
- Framework building

---

## Integration

Preferences integrate with:
- **Personas** - All 8 personas reference prefs
- **User Rules** - Conditional rules reference principles
- **Scripts** - Validation against principles
- **Schemas** - N5/schemas/ for validation
- **Knowledge** - file 'Knowledge/architectural/' for docs

---

## Loading Strategy

**Always Load:**
- Critical safety principles (P5, P15, P19)
- Context in system prompt

**Load When Needed:**
- Specific principles via trigger conditions
- Cognitive prompts via pre-flight protocol
- Operational protocols as work requires

**Never Load:**
- All principles at once (violates P8: Minimal Context)
- Unused protocols

---

## Related Documentation

- **Architecture Overview:** file 'Knowledge/architectural/ARCHITECTURAL_OVERVIEW.md'
- **Principle Guide:** file 'Knowledge/architectural/PRINCIPLE_USAGE_GUIDE.md'
- **Migration History:** file 'N5/builds/architectural-redesign-v1/MIGRATION_HISTORY.md'
- **Schemas:** file 'N5/schemas/README.md'

---

*Last updated: 2025-11-02 21:15 ET*

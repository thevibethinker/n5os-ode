# N5OS Lite Preferences System

**Version:** 1.0  
**Purpose:** Centralized system for AI behavioral preferences and configurations  
**Status:** Core system component

---

## Overview

The Preferences (Prefs) system provides centralized configuration for AI behavior, operational protocols, and system standards. It's the "operating system" layer that defines how N5OS Lite functions.

## Structure

```
N5/ (or your system directory)
├── prompts/              # Reusable workflows
├── personas/             # Specialized AI modes
├── principles/           # Architectural guidelines
├── rules/                # Behavioral rules
└── system/               # System documentation
    ├── preferences_system.md  (this file)
    ├── filesystem_standard.md
    ├── naming_conventions.md
    └── ...
```

## What Goes in Prefs

### 1. Principles (`principles/`)

**Purpose:** Architectural guidelines that shape decision-making

**Format:** YAML files with structure:
```yaml
id: P##
name: Principle Name
category: [quality|safety|design|strategy]
priority: [critical|high|medium|low]
purpose: |
  What this principle achieves
when_to_apply:
  - Situation 1
  - Situation 2
pattern:
  core_behavior: |
    How to follow this principle
examples:
  - description: Example scenario
    good: "Correct approach"
    bad: "Incorrect approach"
anti_patterns:
  - symptom: "Warning sign"
    fix: "How to correct"
related_principles: [P1, P2, P3]
```

**Usage:**
- Reference by ID: "Apply P15"
- Load contextually based on work type
- Embed in personas for specialized modes

### 2. Personas (`personas/`)

**Purpose:** Specialized AI modes for different cognitive tasks

**Format:** YAML files defining:
- Core identity and role
- When to invoke this mode
- Key capabilities and methods
- Anti-patterns and watch-fors
- Routing protocols (when to switch personas)

**Standard Personas:**
- **Operator** - General execution and routing
- **Builder** - Implementation and scripting
- **Strategist** - Analysis and planning
- **Architect** - System and prompt design
- **Teacher** - Explanations and learning
- **Writer** - Content creation
- **Debugger** - Verification and testing
- **Researcher** - Information gathering

### 3. Prompts (`prompts/`)

**Purpose:** Reusable workflows for common tasks

**Format:** Markdown with YAML frontmatter:
```markdown
---
tool: true
description: Brief description
tags: [category1, category2]
version: 1.0
---

# Prompt Name

## Instructions
[Step-by-step workflow]

## Related
[Links to principles, other prompts]
```

**Categories:**
- Workflow automation (close conversation, export thread)
- Data management (add to list, query list)
- Content generation (docgen, knowledge ingest)
- System operations (review work, planning)

### 4. Rules (`rules/`)

**Purpose:** Persistent behavioral preferences

**Format:** YAML with condition + instruction:
```yaml
condition: "When X happens"
instruction: |
  Do Y in response
```

**Types:**
- Always-applied rules (no condition)
- Conditional rules (triggered by specific situations)
- System rules (persona switching, progress reporting)
- Quality rules (accuracy, authorization, safety)

### 5. System Documentation (`system/`)

**Purpose:** System standards and organization guides

**Includes:**
- File system organization
- Naming conventions  
- Protection protocols
- List maintenance
- Storage strategies

## How Prefs Work

### Loading Strategy

**Always Load:**
- Critical safety principles (P5, P7, P11, P15, P19)
- Active persona definition
- System rules

**Load Contextually:**
- Planning prompt → before system work
- Thinking prompt → before strategic decisions
- Specific principles → triggered by work type
- Related prompts → as workflows require

**Never Load:**
- Everything at once (violates P8: Minimal Context)
- Unused components
- Stale or deprecated prefs

### Persona Integration

Each persona embeds:
- 8-12 relevant principles
- Pre-flight protocol (what to load before work)
- Routing rules (when to switch personas)
- Anti-patterns to avoid

### Rule Integration

Rules enforce:
- Quality standards (P15 enforcement)
- Safety protocols (dry-run, authorization)
- System patterns (persona switchback)
- User preferences (response format, communication style)

## Storage Guidelines

**What Goes Where:**

| Content Type | Location | Format |
|--------------|----------|--------|
| Reusable workflows | `prompts/` | Markdown |
| AI modes | `personas/` | YAML |
| Design principles | `principles/` | YAML |
| Behavioral rules | `rules/` | YAML |
| System docs | `system/` | Markdown |
| Examples | `examples/` | Various |

**Naming Conventions:**

- **Principles:** `P##_slug.yaml` (e.g., `P15_complete_before_claiming.yaml`)
- **Personas:** `name.yaml` (e.g., `operator.yaml`, `builder.yaml`)
- **Prompts:** `action-target.md` (e.g., `close-conversation.md`, `add-to-list.md`)
- **System docs:** `topic.md` (e.g., `filesystem_standard.md`)

## Creating New Prefs

### New Principle

1. Choose next available P## number
2. Use YAML structure (see principles/)
3. Add to principles_index.yaml
4. Link from related principles
5. Reference in relevant personas

### New Persona

1. Define clear domain and purpose
2. Embed 8-12 relevant principles
3. Specify routing rules
4. Add to persona ecosystem
5. Test in fresh thread (P12)

### New Prompt

1. Write clear, step-by-step instructions
2. Add YAML frontmatter with metadata
3. Include examples and quality checks
4. Link to related prompts/principles
5. Test execution (P12)

### New Rule

1. Identify condition (or leave blank for always-applied)
2. Write actionable instruction
3. Test in real scenarios
4. Refine based on results
5. Document rationale

## Maintenance

**Weekly:**
- Review new principles for patterns
- Check rule effectiveness
- Update stale documentation

**Monthly:**
- Audit principle usage
- Validate persona routing
- Clean up deprecated prefs

**Quarterly:**
- Major version updates
- System-wide consistency check
- Architecture review

## Best Practices

1. **Single Source of Truth (P2)**
   - Each fact lives in one place
   - Link rather than duplicate
   - Maintain canonical versions

2. **Minimal Context (P8)**
   - Load only what's needed
   - Progressive disclosure
   - Context-aware loading

3. **Human-Readable First (P1)**
   - Write for humans
   - Generate machine formats from prose
   - Prefer markdown over JSON

4. **Document Assumptions (P21)**
   - Make implicit explicit
   - State confidence levels
   - Track placeholders

5. **Test in Fresh Threads (P12)**
   - Validate self-containment
   - Surface missing dependencies
   - Ensure reproducibility

## Related Documentation

- `filesystem_standard.md` - Directory structure
- `naming_conventions.md` - Naming patterns
- `protection_system.md` - File protection
- `principles/principles_index.yaml` - All principles

---

**The prefs system is the foundation of N5OS Lite. Treat it as sacred infrastructure.**

*Last Updated: 2025-11-03*

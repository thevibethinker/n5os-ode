# N5 Preferences Index

**Version:** 2.0.0  
**Date:** 2025-10-09  
**Purpose:** Lightweight index to modular preferences, loaded selectively by context

---

## Critical Always-Load Rules

These rules apply universally and cannot be overridden:

### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`; sticky safety may enforce it
- Require explicit approval for side-effect actions (email, external API, creating services, deleting files)
- Always search for existing protocols before creating new ones
- **Whenever a new file is created, always ask me where the file should be located**

### Folder Policy Principle (Highest Priority)
Folder-specific POLICY.md files take precedence over these global preferences unless explicitly exempted. 

**Mandatory Check:** Always scan for and consult POLICY.md in the target folder before any interaction.

See `file 'N5/prefs/system/folder-policy.md'` for complete specification.

---

## Preference Modules

Load modules selectively based on task context:

### System Governance
- **File Protection** → `file 'N5/prefs/system/file-protection.md'`
  - Hard/medium/auto-generated file classifications
  - Overwrite protection workflow
  - Recovery protocols
  
- **Git Governance** → `file 'N5/prefs/system/git-governance.md'`
  - Tracked paths
  - Ignore patterns
  - Audit procedures

- **Folder Policy** → `file 'N5/prefs/system/folder-policy.md'`
  - Policy precedence rules
  - Anchors system
  - Creation protocol

- **Safety & Review** → `file 'N5/prefs/system/safety.md'`
  - Approval requirements
  - Dry-run defaults
  - Protocol search requirements

### Operations
- **Scheduling** → `file 'N5/prefs/operations/scheduling.md'`
  - Configuration parameters
  - Retry policies
  - Timezone handling

- **Resolution Order** → `file 'N5/prefs/operations/resolution-order.md'`
  - Preference precedence hierarchy
  - Conflict resolution

- **Naming Conventions** → `file 'N5/prefs/naming-conventions.md'`
  - File and folder naming rules
  - Execution naming patterns

- **Engagement Definitions** → `file 'N5/prefs/engagement_definitions.md'`
  - "Load up" / "prime" protocols
  - Engagement patterns

### Knowledge Management
- **Ingestion Standards** → `file 'Knowledge/architectural/ingestion_standards.md'`
  - What to ingest (inclusion/exclusion criteria)
  - MECE principles
  - Pointers and cross-references

- **Operational Principles** → `file 'Knowledge/architectural/operational_principles.md'`
  - Rule-of-Two (load at most 2 config files)
  - SSOT principles
  - Voice integration policy
  - Anti-overwrite safeguards

- **Knowledge Lookup** → `file 'N5/prefs/knowledge/lookup.md'`
  - Topic-specific knowledge references
  - Where to search first

### Communication & Voice
- **Email Processing** → `file 'N5/prefs/communication/email.md'`
  - Auto-process rules
  - Detection rules reference
  - Digest procedures

- **Voice & Style** → `file 'N5/prefs/communication/voice.md'`
  - Tone weights (warmth, confidence, humility)
  - Formality rules
  - Lexicon preferences
  - Anti-patterns

- **Templates** → `file 'N5/prefs/communication/templates.md'`
  - Follow-up structures
  - CTA patterns
  - Micro-templates

- **Prompt Engineering** → `file 'N5/prefs/communication/meta-prompting.md'`
  - Outcome-first interrogatories
  - Enhancement passes
  - File naming patterns

### Integration Preferences
- **Google Drive** → `file 'N5/prefs/integration/google-drive.md'`
  - Access workflow
  - Integration-first preference

- **Coding Agent** → `file 'N5/prefs/integration/coding-agent.md'`
  - When to launch coding agent
  - Task thresholds

---

## Command Registry

Quick reference to available commands:

→ `file 'N5/config/commands.jsonl'` (authoritative registry)  
→ `file 'N5/commands.md'` (auto-generated documentation)

**Most-used commands:**
- `lists-add` — Add items to lists with intelligent routing
- `knowledge-ingest` — Ingest content into knowledge base
- `index-rebuild` — Rebuild N5 system index
- `docgen` — Generate command documentation
- `git-check` — Audit Git changes for data loss

---

## Stable Knowledge References

These files contain stable, canonical information:

### Personal & Company
- **Bio** → `file 'Knowledge/stable/bio.md'`
  - V (Vrijen Attawar) biographical info
  - Logan Currie info
  - Founding story

- **Company Overview** → `file 'Knowledge/stable/company/overview.md'`
  - Careerspan mission
  - Product details
  - Core philosophy

- **Strategy** → `file 'Knowledge/stable/company/strategy.md'`
  - GTM approach
  - Career Agent wedge
  - Positioning

- **Timeline** → `file 'Knowledge/stable/careerspan-timeline.md'`
  - Company history
  - Key milestones
  - Strategic pivots

- **Glossary** → `file 'Knowledge/stable/glossary.md'`
  - Careerspan terminology
  - Product concepts
  - Strategy frameworks

### Detection & Routing
- **Detection Rules** → `file 'Lists/detection_rules.md'`
  - Email classification patterns
  - Routing destinations

### Lists Registry
Managed data collections in JSONL format:
→ `/home/workspace/Lists/` folder (see `file 'Lists/POLICY.md'` for handling rules)

---

## Context-Aware Loading Guide

**For system operations** (file management, git, commands):
- Load: system/file-protection, system/git-governance, system/safety

**For knowledge ingestion** (articles, meetings, research):
- Load: Knowledge/architectural/ingestion_standards, Knowledge/architectural/operational_principles
- Reference: glossary, bio, company info

**For communication tasks** (emails, follow-ups, writing):
- Load: communication/voice, communication/templates
- Reference: bio (for personal context)

**For strategic work** (planning, GTM, positioning):
- Load: company/strategy, glossary, timeline
- Reference: bio, operational principles

**For list operations** (tasks, ideas, tracking):
- Load: Lists/POLICY.md
- Use commands: lists-add, lists-find, lists-move

---

## Schema Registry

Validation schemas for structured data:

→ `/home/workspace/N5/schemas/` (system schemas)  
→ `/home/workspace/Knowledge/schemas/` (knowledge schemas)  
→ `/home/workspace/Lists/schemas/` (list schemas)

**Key schemas:**
- `N5/schemas/index.schema.json` — N5 index structure
- `N5/schemas/commands.schema.json` — Command registry
- `Knowledge/schemas/knowledge.facts.schema.json` — Knowledge facts
- `Lists/schemas/lists.item.schema.json` — List item structure

---

## Change Log

### v2.0.0 — 2025-10-09
- **Breaking change:** Refactored monolithic prefs.md into modular index + specialized modules
- Created system/, operations/, communication/, integration/, knowledge/ subdirectories
- Synchronized with stable knowledge files (bio, company, timeline, glossary)
- Added context-aware loading guide
- Integrated with existing architectural principles and ingestion standards
- Preserved all original rules across modules

### v1.1 — 2025-09-20
- Added military time override
- Added safeguard note for file editing
- Consolidated from previous versions

---

## Migration Notes

**Old monolithic file preserved at:** `file 'N5/prefs/prefs.md.v1'`

**Backward compatibility:** This index file can be loaded alone for lightweight context. Original full content preserved in modules.

**Validation:** All rules from v1.1 preserved across new modules; no functionality lost.
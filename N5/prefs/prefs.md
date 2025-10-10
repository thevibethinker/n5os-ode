# N5 Preferences Index

**Version:** 3.0.0  
**Last Updated:** 2025-10-10  
**Purpose:** Lightweight index to modular preferences, loaded selectively by context

---

## ⚠️ CRITICAL FILE PROTECTION WARNING

**This file is HARD PROTECTED.** Before any write operation:
1. Read the file first to verify current content
2. If file has content (>0 bytes), STOP and ask for explicit user permission
3. Show user what will be lost if proceeding
4. Require user to type "APPROVED" before proceeding
5. Automatic backup will be created

See `file 'N5/prefs/system/file-protection.md'` for complete protection protocols.

---

## Critical Always-Load Rules

**These rules apply universally and cannot be overridden:**

### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`; sticky safety may enforce it
- Require explicit approval for side-effect actions (email, external API, creating services, deleting files)
- Always search for existing protocols before creating new ones
- **Whenever a new file is created, always ask where the file should be located**

### Folder Policy Principle (Highest Priority)
Folder-specific POLICY.md files take precedence over these global preferences unless explicitly exempted.

**Mandatory Check:** Always scan for and consult POLICY.md in the target folder before any interaction.

See `file 'N5/prefs/system/folder-policy.md'` for complete specification.

---

## Preference Modules

Load modules selectively based on task context. **Do not load all modules by default.**

### System Governance

**File Protection** → `file 'N5/prefs/system/file-protection.md'`
- Hard/medium/auto-generated file classifications
- Overwrite protection workflow
- Recovery protocols

**Git Governance** → `file 'N5/prefs/system/git-governance.md'`
- Tracked paths
- Ignore patterns
- Audit procedures

**Folder Policy** → `file 'N5/prefs/system/folder-policy.md'`
- Policy precedence rules
- Anchors system
- Creation protocol

**Safety & Review** → `file 'N5/prefs/system/safety.md'`
- Approval requirements
- Dry-run defaults
- Protocol search requirements

**Commands** → `file 'N5/prefs/system/commands.md'`
- Quick command reference
- Most-used commands
- Command registry pointers

---

### Operations

**Scheduling** → `file 'N5/prefs/operations/scheduling.md'`
- Configuration parameters
- Retry policies
- Timezone handling

**Resolution Order** → `file 'N5/prefs/operations/resolution-order.md'`
- Preference precedence hierarchy
- Conflict resolution

**Careerspan Info** → `file 'N5/prefs/operations/careerspan.md'`
- Organization identity and aliases
- Email domains (mycareerspan.com, theapply.ai)
- Employee canonicalization

**Naming Conventions** → `file 'N5/prefs/naming-conventions.md'`
- File and folder naming rules
- Execution naming patterns

**Engagement Definitions** → `file 'N5/prefs/engagement_definitions.md'`
- "Load up" / "prime" protocols
- Engagement patterns

**Conversation End** → `file 'N5/prefs/operations/conversation-end.md'`
- End-of-conversation protocols
- Cleanup procedures

---

### Knowledge Management

**Lookup** → `file 'N5/prefs/knowledge/lookup.md'`
- Topic-specific knowledge references
- Where to search first

**Ingestion Standards** → `file 'Knowledge/architectural/ingestion_standards.md'`
- What to ingest (inclusion/exclusion criteria)
- MECE principles
- Pointers and cross-references

**Operational Principles** → `file 'Knowledge/architectural/operational_principles.md'`
- Rule-of-Two (load at most 2 config files)
- SSOT principles
- Voice integration policy
- Anti-overwrite safeguards

---

### Communication & Voice

**⚠️ IMPORTANT:** Only load communication/voice modules when generating **distributed output** or communicating **on V's behalf** (emails, documents, external communications). **DO NOT** load for direct conversation with V.

**Executive Snapshot** → `file 'N5/prefs/communication/executive-snapshot.md'`
- Quick reference: warmth, confidence, humility
- Tone summary and anti-patterns
- High-level style guide

**Voice & Style** → `file 'N5/prefs/communication/voice.md'`
- Relationship depth by medium
- Formality & CTA rigor
- Lexicon preferences
- Follow-up structures

**Templates** → `file 'N5/prefs/communication/templates.md'`
- Follow-up structures (CTA + Next Steps, Summary-Decision-Next Steps, Gentle Nudge)
- Micro-templates
- Reusable patterns

**Meta-Prompting** → `file 'N5/prefs/communication/meta-prompting.md'`
- Outcome-first interrogatories
- Enhancement passes
- File naming patterns

**Nuances** → `file 'N5/prefs/communication/nuances.md'`
- Fine-tuning toggles
- Adaptive behaviors
- User-value features

**General Preferences** → `file 'N5/prefs/communication/general-preferences.md'`
- Operating rules
- Writing metrics
- Feedback loops

**Email** → `file 'N5/prefs/communication/email.md'`
- Auto-process rules
- Detection rules reference
- Digest procedures

**Compatibility** → `file 'N5/prefs/communication/compatibility.md'`
- Cheat-sheet for other AIs
- Quick formatting & tone reference

---

### Integration Preferences

**Google Drive** → `file 'N5/prefs/integration/google-drive.md'`
- Access workflow
- Integration-first preference

**Coding Agent** → `file 'N5/prefs/integration/coding-agent.md'`
- When to launch coding agent
- Task thresholds

---

## Context-Aware Loading Guide

**For system operations** (file management, git, commands):
- Load: `system/file-protection`, `system/git-governance`, `system/safety`

**For knowledge ingestion** (articles, meetings, research):
- Load: `Knowledge/architectural/ingestion_standards`, `Knowledge/architectural/operational_principles`
- Reference: glossary, bio, company info

**For communication tasks** (emails, follow-ups, writing **on V's behalf**):
- Load: `communication/executive-snapshot`, `communication/voice`, `communication/templates`
- Reference: bio (for personal context)
- **Do NOT load for direct conversation with V**

**For strategic work** (planning, GTM, positioning):
- Load: company/strategy, glossary, timeline
- Reference: bio, operational principles

**For list operations** (tasks, ideas, tracking):
- Load: `Lists/POLICY.md`
- Use commands: lists-add, lists-find, lists-move

**For Careerspan-specific context**:
- Load: `operations/careerspan` (organization aliases, email domains)
- Reference: `Knowledge/stable/company/*`

---

## Stable Knowledge References

These files contain stable, canonical information:

### Personal & Company
- **Bio** → `file 'Knowledge/stable/bio.md'`
- **Company Overview** → `file 'Knowledge/stable/company/overview.md'`
- **Strategy** → `file 'Knowledge/stable/company/strategy.md'`
- **Timeline** → `file 'Knowledge/stable/careerspan-timeline.md'`
- **Glossary** → `file 'Knowledge/stable/glossary.md'`

### Detection & Routing
- **Detection Rules** → `file 'Lists/detection_rules.md'`

### Lists Registry
- Managed data collections in JSONL format: `/home/workspace/Lists/`
- See `file 'Lists/POLICY.md'` for handling rules

---

## Schema Registry

Validation schemas for structured data:

- `/home/workspace/N5/schemas/` (system schemas)
- `/home/workspace/Knowledge/schemas/` (knowledge schemas)
- `/home/workspace/Lists/schemas/` (list schemas)

**Key schemas:**
- `N5/schemas/index.schema.json` — N5 index structure
- `N5/schemas/commands.schema.json` — Command registry
- `Knowledge/schemas/knowledge.facts.schema.json` — Knowledge facts
- `Lists/schemas/lists.item.schema.json` — List item structure

---

## System Settings

### Military Time Override
Use 24-hour format system-wide (e.g., 16:00 instead of 4:00 pm).

### Lists Reference
When referring to lists, always check `/home/workspace/N5/lists/` and `/home/workspace/Lists/`

---

## Change Log

### v3.0.0 — 2025-10-10
- **Breaking change:** Converted prefs.md from monolithic document to lightweight index
- Created focused sub-modules for communication preferences
- Moved organization identity to `operations/careerspan.md`
- Added clear loading contexts for communication modules (only for distributed output)
- Deprecated old `index.md` in favor of this streamlined `prefs.md`
- Backed up monolithic version to `prefs.md.v2_monolithic_backup`

### v2.0.0 — 2025-10-09
- Refactored into modular structure with system/, operations/, communication/, integration/, knowledge/ subdirectories
- Created initial module files
- Synchronized with stable knowledge files

### v1.1 — 2025-09-20
- Added military time override
- Added safeguard note for file editing
- Consolidated from previous versions

---

## Migration Notes

**Previous monolithic file preserved at:** `file 'N5/prefs/prefs.md.v2_monolithic_backup'`

**Backward compatibility:** This index file serves as the main entry point. All original content preserved in focused modules.

**Validation:** All rules from previous versions preserved across new modules; no functionality lost.

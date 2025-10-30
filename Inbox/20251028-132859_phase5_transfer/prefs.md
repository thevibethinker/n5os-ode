# N5 Preferences Index

**Version:** 3.2.0  
**Last Updated:** 2025-10-27  
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

### System Bulletins for Troubleshooting
**CRITICAL:** When encountering contradictions, irregularities, unexplained system behavior, missing files, or unexpected configurations:

1. **Check system bulletins FIRST** before asking user or improvising
2. Bulletins are auto-loaded in session init with `--load-system` flag
3. If bulletins weren't loaded, manually load: `cat N5/data/system_bulletins.jsonl | jq -r '[.timestamp[:10], .significance, .change_type, .summary] | @tsv'`
4. Look for recent changes (last 10 days) that explain the irregularity
5. Reference bulletin_id and conversation_id when discussing the change with user

**Scope:** File structure changes, script modifications, workflow updates, command changes, principle additions, architecture decisions, breaking changes

**Rationale:** System bulletins provide AI transparency into recent evolution. Checking bulletins before asking prevents redundant questions and provides context for why something exists or changed.

**Examples:**
- "This script doesn't exist" → Check bulletins for file moves/deletions
- "Workflow behavior changed" → Check bulletins for recent script updates
- "Unexpected directory structure" → Check bulletins for reorganization
- "Command not found" → Check bulletins for command registry changes

### Command-First Operations
**CRITICAL:** Before ANY workflow-related operation, check for registered commands in `file 'Recipes/recipes.jsonl'` OR search `Recipes/**/*.md` for relevant protocols.

**Scope:** System operations, content processing, knowledge management, reflections, automation, scheduled tasks, integrations, file operations, and any workflow with established procedures.

**Priority order:**
1. Registered command in commands.jsonl
2. Protocol documentation in Recipes/
3. Manual script execution
4. Direct file operations
5. Improvisation (last resort after confirming no protocol exists)

**Specific Rules:**
- **Thread closure:** Load `file 'N5/prefs/operations/thread-closure-triggers.md'` to determine correct command
  - User says "end conversation", "wrap up", "close thread" → `conversation-end` (file organization + cleanup)
  - User says "export thread", "create AAR", "continue in new thread" → `thread-export` (documentation + AAR)
- **Thread exports:** When user requests "export this thread" or similar, ALWAYS use `recipe 'Recipes/Productivity/Thread Export.md'`
- **Thread export location:** ALL thread exports MUST go to `N5/logs/threads/` (enforced by thread-export command)
- **Incantum Commands:** When user message starts with "N5" or "incantum", follow `file 'N5/prefs/operations/incantum-protocol.md'` to parse and execute commands using natural language understanding
- **NEVER** create ad-hoc export directories in workspace root (`/home/workspace/ExportedThreads/`, `/home/workspace/Exports/`, etc.)
- **System operations:** Check commands.jsonl before manual implementation (lists, timeline, git, thread operations)
- **Reflections:** Subject "reflection-ingest" or "[Reflect]" → See "Reflection Processing" section below
- **Content workflows:** Always search Recipes/ before creating ad-hoc processes
- **Preference order:** Registered command > Protocol documentation > Manual script execution > Direct file operations > Improvisation

**Rationale:** Maintains SSOT (P2), prevents directory proliferation, ensures consistent naming and structure, leverages established workflows and their benefits (tracking, approval, integration)

### Reflection Processing

**When email subject contains "reflection-ingest", "[Reflect]", or "reflection-pipeline" OR when processing voice reflections:**

1. STOP and load `file 'Recipes/Meetings/Transcript Ingest.md'`
2. Check for email attachments in conversation workspace (`/home/.z/workspaces/*/email_attachment/`)
3. Stage files to `N5/records/reflections/incoming/`:
   - For text files (.txt, .md): Create `.transcript.jsonl` wrapper if needed
   - For audio files: Use transcribe_audio tool first
4. Execute: `python3 /home/workspace/N5/scripts/reflection_ingest.py`
5. Follow established approval workflow
6. **DO NOT improvise alternate analysis approaches**

**Rationale:** Reflections have established pipeline with registry, approval workflow, and synthesis protocols. Bypassing creates inconsistency and loses system benefits (tracking, classification, SSOT).

### Output Review Reminder

**At conversation-end (when user says "end conversation", "close thread", "wrap up"):**

The `n5_conversation_end.py` script will automatically (Phase 2.75):
1. List outputs flagged for review during this conversation
2. Scan workspace for substantial deliverables (>100 words) not yet flagged
3. Show summary and command to flag outputs with improvement notes

**To manually flag outputs for quality review:**
```bash
python3 N5/scripts/review_cli.py add <path> \
  --improve "What to change (e.g., 'Use warmer tone, cut to 150 words')" \
  --optimal "Ideal version (e.g., 'Professional but friendly, 2-3 paras, clear CTA')"
```

**Rationale:** Captures "what to improve" and "optimal state" alongside outputs so future work can directly apply past feedback. Builds training data corpus for style refinement.

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

**Command Triggering** → `file 'N5/prefs/system/command-triggering.md'`
- Two-layer system (formal + natural language)
- Incantum triggers workflow
- When to use commands.jsonl vs incantum_triggers.json
- Troubleshooting command recognition

---

### Operations

**Scheduling** → `file 'N5/prefs/operations/scheduling.md'`
- Configuration parameters
- Retry policies
- Timezone handling

**Scheduled Task Protocol** → `file 'N5/prefs/operations/scheduled-task-protocol.md'`
- Task creation standards
- Naming and instruction conventions
- Testing and safety requirements
- Digest integration patterns

**Resolution Order** → `file 'N5/prefs/operations/resolution-order.md'`
- Preference precedence hierarchy
- Conflict resolution

**Careerspan Info** → `file 'N5/prefs/operations/careerspan.md'`
- Organization identity and aliases
- Email domains (mycareerspan.com, theapply.ai)
- Employee canonicalization

**CRM Usage** → `file 'N5/prefs/operations/crm-usage.md'`
- When to query CRM database
- How to find people and connections
- Network intelligence and interaction tracking

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

**For scheduled task operations** (creating, modifying tasks):
- Load: `operations/scheduled-task-protocol`, `operations/scheduling`, `system/safety`
- Reference: `operations/digest-creation-protocol` (if digest-related)

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

### v3.2.0 — 2025-10-27
- **System Bulletins Integration:** Added "System Bulletins for Troubleshooting" critical rule
- **Behavioral Trigger:** AI must check bulletins FIRST when encountering irregularities
- **Auto-load:** Bulletins automatically loaded in session init with `--load-system` flag
- **Rationale:** Close the loop on bulletins infrastructure—provide explicit instruction to reference bulletins during troubleshooting

### v3.1.0 — 2025-10-20
- **Protocol Enhancement:** Added explicit "Reflection Processing" conditional rule mapping email subjects to reflection pipeline
- **Broadened Command-First:** Expanded scope from just system operations to ALL workflow types with clear priority order
- **Updated reflection-ingest.md:** Added comprehensive AI workflow section with text transcript handling
- **Updated reflection_worker.py:** Native text file support with auto-creation of transcript.jsonl wrappers
- **Rationale:** Prevent protocol bypass incidents, make command-first approach systemic

### v3.0.0 — 2025-10-10
- **Breaking change:** Converted prefs.md from monolithic document to lightweight index
- Created focused sub-modules for communication preferences
- Moved organization identity to `operations/careerspan.md`
- Added clear loading contexts for communication modules (only for distributed output)
- Deprecated old `index.md` in favor of this streamlined `prefs.md`

### v2.0.0 — 2025-10-09
- Refactored into modular structure with system/, operations/, communication/, integration/, knowledge/ subdirectories
- Created initial module files
- Synchronized with stable knowledge files

### v1.1 — 2025-09-20
- Added military time override
- Added safeguard note for file editing
- Consolidated from previous versions

---

**For full details on each module, see the module files directly or consult `file 'N5/prefs/README.md'`.**

**For historical context on preference system evolution, see `file 'N5/prefs/Archive/README.md'`.**

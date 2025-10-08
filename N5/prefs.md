[//]: # (Default Ingestion Method: direct_processing)

---
date: "2025-09-20T22:24:55Z"
last-tested: "2025-09-20T22:24:55Z"
generated_date: "2025-09-20T22:24:55Z"
checksum: dd9c061334a6e850d73b886074ce815b
tags: []
category: unknown
priority: medium
related_files: []
anchors: 
input: null
output: /home/workspace/N5_mirror/prefs.md
---
# N5 OS Preferences (Global)

This governs defaults and rules. Workflow sub-preferences may override; project _prefs.md overrides those.

## Command Index (top)

- `docgen` — Generate command catalog and update prefs Command Index from commands.jsonl (see ./commands/docgen.md)
- `git-check` — Quick audit for overwrites or data loss in staged Git changes (see ./commands/git-check.md)
- `grep-search-command-creation` — Automated command_creation workflow using grep_search, create_command_draft, validate_command (see ./commands/grep-search-command-creation.md)
- `index-rebuild` — Rebuild the N5 system index from source files (see ./commands/index-rebuild.md)
- `lists-add` — Add an item to a list with intelligent assignment (see ./commands/lists-add.md)
- `lists-move` — Move an item from one list to another atomically (see ./commands/lists-move.md)
- `system-upgrades-add` — Interactive command for adding items to the N5 system upgrades list with validation and safety features (see ./commands/system-upgrades-add.md)
- `timeline` — View n5.os development timeline and system history (see ./commands/timeline.md)
- `timeline-add` — Add new entry to n5.os development timeline (see ./commands/timeline-add.md)

## Review & Safety

- Never schedule anything without explicit consent.
- Always support --dry-run; sticky safety may enforce it.
- Require explicit approval for side-effect actions (email, external API, creating services, deleting files).
- Always search for existing protocols or processes for categorizing/storing documents before creating new ones. Prefer placing under existing structure (e.g., lists) to avoid bloat.
- Whenever a new file is created, always ask me where the file should be located. Do not create any file without asking me the location.

## File Saving Policy

**CRITICAL**: This policy addresses workspace bloat by deferring file organization until conversation end.

### Core Philosophy

**During Conversation**:
- Save ALL files to conversation workspace (temp folder with conversation ID)
- Do NOT interrupt flow to ask about file locations
- Focus on productivity and natural conversation

**At Conversation End**:
- Study the conversation workspace file structure
- Propose destinations based on file type and content
- Move files to appropriate permanent locations
- Cleanup conversation workspace

### Conversation Workspace Structure

Each conversation has a dedicated workspace:
```
/home/.z/workspaces/con_[CONVERSATION_ID]/
├── scripts/           - Generated scripts
├── data/              - Data files, CSVs, JSON
├── images/            - Generated/downloaded images
├── documents/         - Text documents, markdown
├── exports/           - Exported data
└── temp/              - Truly temporary files
```

**During Conversation**: All files saved here automatically.

### Default Permanent Locations by File Type

| File Type | Permanent Location | Criteria |
|-----------|-------------------|----------|
| Generated images | `/home/workspace/Images/` | All .png, .jpg, .gif files |
| Meeting notes/transcripts | `/home/workspace/Meetings/` | Files with meeting content |
| Company documents | `/home/workspace/Careerspan/` | Company-related content |
| Saved articles | `/home/workspace/Articles/` | Web articles, saved pages |
| Code/scripts (permanent) | `/home/workspace/Code/` | User-requested code only |
| Exports (lists, data) | `/home/workspace/Exports/` | CSV, JSON, data exports |
| Meeting transcripts (raw) | `/home/workspace/Records/Company/meetings/` | Raw transcripts before processing |
| Emails (raw) | `/home/workspace/Records/Company/emails/` | Email content before processing |
| Documents (raw) | `/home/workspace/Records/Company/documents/` | Documents before processing |
| Analysis/reports | `/home/workspace/Documents/` | Analysis, reports, summaries |
| System documentation | `/home/workspace/Documents/System/` | N5 system docs, guides |
| Temporary files | DELETE | Truly temporary, no value |

### Conversation End Workflow

**Step 1: Inventory**
```bash
# List all files created in conversation workspace
find /home/.z/workspaces/con_[ID]/ -type f -newer [START_TIME]
```

**Step 2: Classify**
For each file, determine:
- File type (extension, content)
- Purpose (what was it created for?)
- Value (permanent vs temporary)
- Context (what conversation topic?)

**Step 3: Propose Destinations**
```markdown
## Files Created This Conversation

### Images (3 files)
- rocket_design.png → Images/rocket_design_20251008.png
- logo_draft.png → Images/logo_draft_20251008.png
- chart.png → DELETE (temporary visualization)

### Documents (2 files)
- meeting_summary.md → Records/Company/meetings/2025-10-08-board-meeting.md
- analysis_report.md → Documents/Company_Analysis_20251008.md

### Scripts (1 file)
- data_processor.py → DELETE (temporary script for one-time task)

**Confirm these moves? (Y/n)**
```

**Step 4: Execute Moves**
```bash
# Move permanent files to destinations
mv [source] [destination]

# Delete temporary files
rm [temp_files]

# Log moves to audit trail
echo "[timestamp] Moved [files] from conversation [ID]" >> N5/runtime/file_moves.log
```

**Step 5: Cleanup**
```bash
# Remove empty conversation workspace
rmdir /home/.z/workspaces/con_[ID]/
```

### Classification Rules

**Images**:
- User-requested generations → Images/
- Temporary visualizations → DELETE
- Charts for reports → Images/ (with descriptive name)

**Documents**:
- Meeting transcripts → Records/Company/meetings/
- Analysis/reports → Documents/
- Notes → Meetings/ or Records/Personal/notes/
- Temporary drafts → DELETE

**Code/Scripts**:
- User-requested → Code/
- One-time automation → DELETE
- Reusable utilities → Code/

**Data Files**:
- User-requested exports → Exports/
- Processing intermediates → DELETE
- Raw data for ingestion → Records/[Category]/inbox/

**Articles/Web Content**:
- Saved for reference → Articles/
- Temporary research → DELETE

### Override Mechanism

User can specify permanent location during conversation:
```
User: "Save this to Careerspan/Strategy/"
Zo: [saves to specified location, bypassing conversation workspace]
```

This should be rare - default is conversation workspace.

### Enforcement Rules

**RULE 1**: During conversation, ALWAYS save to conversation workspace unless user specifies otherwise.

**RULE 2**: At conversation end, ALWAYS propose file destinations before moving.

**RULE 3**: If conversation ends without user confirmation, files stay in conversation workspace (safe default).

**RULE 4**: Conversation workspace is retained for 7 days, then archived/deleted.

**RULE 5**: User can manually trigger file organization mid-conversation: `N5: organize-files`

### Examples

**Example 1: Research Session**
```
During conversation:
- Generated 5 images → /home/.z/workspaces/con_ABC/images/
- Downloaded 3 articles → /home/.z/workspaces/con_ABC/documents/
- Created 1 summary → /home/.z/workspaces/con_ABC/documents/

At conversation end:
"I created 9 files. Here's what I recommend:

Images (5):
- concept_1.png → Images/product_concept_1_20251008.png
- concept_2.png → Images/product_concept_2_20251008.png
- wireframe.png → Images/wireframe_20251008.png
- temp_chart.png → DELETE (temporary)
- analysis_viz.png → DELETE (temporary)

Articles (3):
- ai_trends_2025.md → Articles/ai_trends_2025.md
- competitor_analysis.md → Articles/competitor_analysis.md
- market_research.md → DELETE (extracted to Knowledge/)

Summary (1):
- research_summary.md → Documents/Research_Summary_20251008.md

Total: 6 files moved, 3 deleted.
Proceed? (Y/n)"
```

**Example 2: Meeting Processing**
```
During conversation:
- Transcript uploaded → /home/.z/workspaces/con_XYZ/
- Generated summary → /home/.z/workspaces/con_XYZ/
- Extracted action items → Lists/must-contact.jsonl (direct write)

At conversation end:
"I created 2 files in conversation workspace:

Documents (2):
- board_meeting_transcript.md → Records/Company/meetings/2025-10-08-board-meeting-transcript.md
- board_meeting_summary.md → Meetings/2025-10-08-Board-Meeting-Summary.md

Note: Action items already written to Lists/must-contact.jsonl

Proceed? (Y/n)"
```

### Integration with N5 Commands

**New Commands Needed**:
- `organize-files` - Trigger file organization mid-conversation
- `conversation-end` - Formal conversation close with file organization
- `review-workspace` - Show files in conversation workspace
- `cleanup-temp` - Delete old conversation workspaces

**Existing Commands**:
- All N5 commands continue writing to Knowledge/, Lists/ directly
- Only ad-hoc files (images, documents, exports) go to conversation workspace

### Related Documentation

- `file 'Records/README.md'` - Records intake and processing
- N5/runtime/file_moves.log - Audit trail of file movements
- Conversation workspace retention policy

---

## Folder Policy Principle

**Highest Priority Governance**: Folder-specific POLICY.md files take precedence over these global preferences unless explicitly exempted in the policy file itself (e.g., "Exempts: Safety Overrides"). Policies govern the collective interpretation and handling of folder contents as programs, databases, or dynamic entities.

- **Mandatory Check**: Always scan for and consult POLICY.md in the target folder before any interaction (read, edit, add, delete). If absent, default to this global prefs.md but flag for policy creation.
- **Anchors System**: Each POLICY.md must include an "Anchors" section linking to root N5/prefs.md, related issues, or parent policies for cross-referencing and system coherence.
- **Overrides Mechanism**: Folder policies can override any global rule; document exemptions clearly. Conflicts resolved by escalating to root POLICY.md or user arbitration.
- **Naming Convention**: Use "POLICY.md" for consistency and easy sourcing by title (e.g., search for "POLICY.md" in folder tree).
- **Creation Protocol**: When creating a new folder, always generate POLICY.md first. Include purpose, handling rules, safety flags, dependencies, and anchors.

- **Enforcement**: Automated checks (future N5 command) will validate policy adherence. Manual overrides require timeline logging.

## File Protection & Safety

- **File Classification System**: Files are protected differently based on their role:
  
  **HARD PROTECTION** (Manual-Edit Only)
  - N5.md - Core system index (hand-authored)
  - N5/prefs.md - System preferences and governance (hand-authored)
  
  **MEDIUM PROTECTION** (Requires Pre-Check)
  - N5/commands.jsonl - Command registry (manually curated/validated)
  - N5/lists/*.jsonl - User data lists (manually curated)
  - N5/knowledge/**/*.md - Knowledge content (manually authored)
  
  **AUTO-GENERATED** (Do Not Protect - Regeneratable)
  - N5/commands.md - Generated by docgen
  - N5/commands/*.md - Automatically generated from commands.jsonl
  - N5/index.md - Generated by index-update
  - N5/index.jsonl - Database regenerated by index-update

- **Overwrite Protection Workflow** (Hard Protection):
  1. read_file() to verify current content
  2. If file > 0 bytes, show preview and require explicit confirmation
  3. Check Git status - if modified, require Git diff review
  4. Suggest atomic backup before modification
  5. After modification, verify content was preserved as intended

- **Recovery Protocol**: For any overwrite incident:
  1. Immediately document in timeline system with impact=high and incident tags
  2. Check Git history with 'git log --oneline -10 -- [file]' 
  3. Restore from latest good commit with 'git show [commit]:[file]' > current file
  4. Add incident to N5 timeline system for tracking

## Git Governance

- Track these paths explicitly:
  - N5/prefs.md
  - N5/commands.jsonl
  - N5/lists/*.jsonl
  - N5/knowledge/**/*.md
  - N5/modules/**/*.md
  - N5/flows/**/*.md
  - N5/schemas/**/*.json
  - N5/scripts/**/*.py
  - N5/examples/**/*.md
  - N5/timeline/*.jsonl

- Ignore generated and transient files:
  - N5/commands.md
  - N5/commands/*.md
  - N5/lists/*.md
  - N5/index.md
  - N5/index.jsonl
  - N5/runtime/**
  - N5/exports/**

- Use the command `N5: git-audit` regularly after adding new workflows or files to detect untracked important files.
- This will print exact shell commands to add missing files to Git.
- No automatic changes are made; manual approval is required to add files.

## Scheduling
- Enabled: false
- Max Retries: 2
- Backoff Seconds: 60, 300
- Lock Timeout: 3600
- Missed Run Policy: skip
- Timezone: UTC

## Resolution Order

Project _prefs.md > Workflow sub-pref > Global prefs.md. Knowledge informs, does not override.

## Knowledge Lookup

- Topic: career spans / Careerspan — Always check ./N5/knowledge before answering; prefer facts from there and update if gaps are found.

## Knowledge Ingestion Standards

- **Reference Requirement**: Before initiating any action that could impact the epistemic reservoirs or knowledge base (e.g., ingesting new information, updating facts, or restructuring knowledge), explicitly reference the N5 Knowledge Ingestion Standards (./N5/knowledge/ingestion_standards.md).
- **Alignment Check**: Ensure all actions align semantically and epistemically with the established standards, including inclusion criteria, MECE principles, and adaptive suggestions.
- **Purpose**: Maintain consistency in building out the complete understanding of V and Careerspan, focusing on biographical, historical, and strategic aspects.

## Naming Conventions

- **Location**: ./N5/prefs/naming-conventions.md
- **Purpose**: Human-readable, greppable naming for files and folders.
- **Quick Access**: Reference here for all naming rules in N5 OS.

## Google Drive Access

- **Preference**: Always first try to access Google Drive related content through the integration first, versus through a web browser or consumer access.
- **Steps for Accessing Google Drive Files**:
  1. Verify the Google Drive app integration is connected using `list_app_tools(app_slug="google_drive")`.
  2. Retrieve file metadata using `use_app_google_drive` with `tool_name="google_drive-get-file-by-id"` and the file ID.
  3. Download the file content using `use_app_google_drive` with `tool_name="google_drive-download-file"`, specifying the file ID, filePath (e.g., "/tmp/filename.txt"), and mimeType (e.g., "text/plain" for Google Docs export).
  4. If the tool returns a download URL, use `run_bash_command` with curl to fetch it to the workspace (e.g., "/home/workspace/filename.txt").
  5. Read the downloaded file using `read_file` with the absolute path.

## Coding Agent Preference

- **Preference**: Always launch a coding agent (perform_coding_task tool) whenever possible for coding tasks because it leads to better outcomes.
- **Application**: Use for planning, processing, and executing coding tasks; any task involving substantial code changes; ambiguous or complex coding requirements.
- **Type**: Soft preference that guides decision-making but allows flexibility when direct editing is more appropriate for simple changes.
- **Rationale**: The coding agent provides specialized capabilities for comprehensive code analysis, planning, and implementation that produce higher quality results.
## Email Ingestion (Baseline Behavior)
- **Auto-Process Forwarded Emails**: true (trigger Process Emails command on new Queue/Email/*.json)
- **Auto-Scan Gmail for Digests**: daily (run Scan Gmail for Digests at 6 AM ET)
- **Thread Creation Trigger**: If new Gmail thread contains "newsletter" or "article", process via Process Newsletter command
- **Detection Rules Path**: file N5/lists/detection_rules.md
- **Article Tracker Path**: file N5/knowledge/article_reads.jsonl
- **Digest Path**: file N5/knowledge/digests/{date}.md
- **Log Path**: file N5/knowledge/logs/Email/{date}.log
- **Howie Interaction**: Paused until direct instruction (per stored preferences)

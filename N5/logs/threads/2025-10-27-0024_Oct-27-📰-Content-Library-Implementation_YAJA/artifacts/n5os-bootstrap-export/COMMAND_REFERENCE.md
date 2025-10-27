# N5 OS Command Reference

**Quick reference for the 83+ commands available after installation.**

---

## Running Commands

After installation, commands can be invoked:

```bash
# Method 1: Via script directly
python3 N5/scripts/n5_index_rebuild.py

# Method 2: Via Zo agent (natural language)
"close thread"  →  conversation-end

# Method 3: Via command name (future)
invoke-command --name "index-rebuild"
```

---

## Essential Commands (Start Here)

| Command | Purpose | Script |
|---------|---------|--------|
| **index-rebuild** | Rebuild system index | n5_index_rebuild.py |
| **git-check** | Verify git changes safe | n5_git_check.py |
| **core-audit** | Daily audit of core files | N/A |
| **search-commands** | Find a command by keyword | N/A |

---

## System Commands

### File Management
- `git-check` — Audit staged git changes
- `git-audit` — Find untracked files
- `file-protector` — Manage file protection rules
- `workspace-root-cleanup` — Clean workspace root
- `workspace-maintenance` — General maintenance

### Index & Search
- `index-rebuild` — Rebuild N5 index from scratch
- `index-update` — Incrementally update index
- `search-commands` — Search command registry
- `placeholder-scan` — Find placeholders in files

---

## Meeting Commands

### Processing
- `meeting-process` — Process a meeting transcript
- `meeting-auto-process` — Auto-process discovered meetings
- `meeting-transcript-process` — Detailed transcript processing
- `meeting-detect` — Detect new meetings
- `meeting-transcript-scan` — Scan for transcripts

### Intelligence
- `meeting-intelligence-orchestrator` — Full meeting analysis
- `meeting-prep-digest` — Generate prep digest
- `meeting-approve` — Approve meeting output

### Special Cases
- `internal-meeting-process` — Process internal meetings
- `networking-event-process` — Process networking events

---

## List Commands

### Core Operations
- `lists-add` — Add item to list
- `lists-find` — Search lists
- `lists-export` — Export lists
- `lists-move` — Move item between lists
- `lists-set` — Set list properties

### Utilities
- `lists-create` — Create new list
- `lists-health-check` — Check list integrity
- `lists-pin` — Pin important items
- `lists-promote` — Promote items in lists
- `list-view` — View list contents

---

## Reflection & Ingestion

### Processing
- `reflection-ingest` — Ingest reflection data
- `reflection-pipeline` — Full reflection pipeline
- `reflection-worker` — Worker process
- `reflection-auto-ingest` — Auto-ingest reflections
- `transcript-ingest` — Ingest transcripts

### Advanced
- `reflection-email-orchestrator` — Process via email
- `reflection-synthesizer` — Synthesize reflections
- `reflection-pull-gdrive` — Pull from Google Drive

---

## Knowledge Management

### Core
- `knowledge-add` — Add knowledge item
- `knowledge-find` — Search knowledge
- `knowledge-ingest` — Ingest knowledge source
- `direct-knowledge-ingest` — Direct ingestion

### Analysis
- `aggregate-insights` — Aggregate insights
- `extract-careerspan-insights` — Company-specific insights

---

## Communication & Email

### Generation
- `follow-up-email-generator` — Generate follow-ups
- `warm-intro-generate` — Generate introductions
- `linkedin-post-generate` — LinkedIn posts
- `social-post-generate-multi-angle` — Multi-angle posts

### Management
- `email-post-process` — Post-process emails
- `unsent-followups-digest` — Review unsent follow-ups
- `drop-followup` — Drop a follow-up

---

## Deliverables & Content

### Generation
- `deliverable-generate` — Generate deliverables
- `generate-with-voice` — Generate with voice style
- `generate-deliverables` — Alternative generation

### Review
- `deliverable-review` — Review deliverables
- `lessons-review` — Review lessons learned

---

## Conversation & Thread Management

### Workflow
- `conversation-end` — Formal end with file organization
- `thread-export` — Export thread to AAR
- `thread-export-format` — Thread export specification

### Utilities
- `check-state-session` — Check session state
- `init-state-session` — Initialize session
- `update-state-session` — Update session state

---

## Finding Commands

### Search by Keyword

```bash
# Search for "meeting" commands
grep "meeting" N5/config/commands.jsonl

# Search for "list" commands
grep "list" N5/config/commands.jsonl

# Count total commands
wc -l N5/config/commands.jsonl
```

### List All Commands

```bash
# All command names
python3 -c "import json; [print(line.split('\"')[3]) for line in open('N5/config/commands.jsonl')]"

# With descriptions
python3 N5/scripts/search-commands.py --all
```

---

## Natural Language (Incantum) Shortcuts

These natural language phrases trigger commands:

- "close thread" → conversation-end
- "export this" → thread-export
- "check list health" → lists-health-check
- "find list" → lists-find
- "add to list" → lists-add
- "search commands" → search-commands
- "rebuild index" → index-rebuild
- "check git" → git-check

Add more in N5/config/incantum_triggers.json

---

## Command Structure

Each command has:

```json
{
  "command": "command-name",
  "file": "N5/commands/command-name.md",
  "description": "What it does",
  "category": "system|meetings|lists|communication",
  "workflow": "automation|manual|ui",
  "script": "/path/to/n5_command_name.py"
}
```

View any command documentation:

```bash
cat N5/commands/[command-name].md
```

---

## Common Workflows

### Workflow 1: Process a Meeting
```bash
python3 N5/scripts/n5_meeting_process.py --file meeting.txt
# Extracts decisions, action items, follow-ups
# Generates email if needed
```

### Workflow 2: Add to List and Export
```bash
python3 N5/scripts/lists_add.py --list ideas --content "New idea"
python3 N5/scripts/lists_export.py --list ideas
```

### Workflow 3: End a Conversation
```bash
python3 N5/scripts/n5_conversation_end.py
# Organizes output
# Creates AAR
# Exports thread
```

### Workflow 4: System Maintenance
```bash
python3 N5/scripts/n5_index_rebuild.py
python3 N5/scripts/n5_git_check.py
python3 N5/scripts/n5_core_audit.py
```

---

## Next Steps

1. Read command docs: cat N5/commands/[command-name].md
2. Test a command: Start with index-rebuild --dry-run
3. Use incantum: Try natural language shortcuts in Zo agent
4. Explore: Use grep to discover commands by topic
5. Get help: Review N5/prefs/system/command-triggering.md

---

**Total Commands**: 83+ (as of 2025-10-26)  
**Categories**: 15+  
**Documentation**: All in N5/commands/  
**Registry**: N5/config/commands.jsonl

# Commands Quick Reference

**Version:** 1.0  
**Last Updated:** 2025-10-16

---

## Command Systems

N5 has **two command systems**:

1. **Formal Commands** → `file 'N5/data/executables.db' (index only)` (83 registered)
2. **Natural Language (Incantum)** → `file 'N5/config/incantum_triggers.json'`

**For detailed explanation, see:** `file 'N5/prefs/system/command-triggering.md'`

---

## Most-Used Commands

### Lists
- `lists-add` — Add item to list with intelligent assignment
- `lists-find` — Search and filter items in a list
- `lists-export` — Export list to MD or CSV
- `lists-health-check` — Check list system health

### Knowledge
- `knowledge-add` — Add fact to knowledge base
- `knowledge-find` — Search facts
- `knowledge-ingest` — Ingest biographical/strategic information

### System
- `conversation-end` — End conversation with file organization
- `thread-export` — Generate AAR and export thread
- `docgen` — Generate command catalog from registry
- `index-rebuild` — Rebuild N5 system index

### Git & Safety
- `git-check` — Audit staged changes for overwrites/data loss
- `git-audit` — Find untracked files that should be tracked
- `placeholder-scan` — Scan for placeholders and incomplete code

### Meetings & CRM
- `meeting-process` — Process meeting transcript end-to-end
- `meeting-approve` — Approve meeting outputs and trigger actions
- `crm-find` — Fast CRM queries by name/company/connection

---

## Natural Language (Incantum)

**Examples:**
- "close thread" → `conversation-end`
- "export this thread" → `thread-export`
- "check list health" → `lists-health-check`
- "add timeline entry" → `system-timeline-add`

**How it works:**
1. Incantum matches natural language to formal commands
2. Fuzzy matching with rapidfuzz (55%+ confidence threshold)
3. Prompts for confirmation on ambiguous/destructive commands

**Test a phrase:**
```bash
python3 /home/workspace/N5/scripts/n5_incantum.py "your phrase here"
```

---

## Finding Commands

### Search by keyword
```bash
python3 /home/workspace/N5/scripts/n5_search_commands.py "export"
```

### Browse full catalog
`file 'N5/commands.md'` (DEPRECATED - see recipe-execution-guide.md)

### Check registry directly
`file 'N5/data/executables.db' (index only)` (83 commands)

---

## Command-First Operations

**CRITICAL:** Always check for registered commands BEFORE performing operations manually.

**Priority Order:**
1. Registered command (commands.jsonl)
2. Manual script execution
3. Direct file operations

**Examples:**
- Thread exports → Use `thread-export` command (not ad-hoc directories)
- List operations → Use `lists-*` commands (not direct JSONL edits)
- Timeline → Use `system-timeline-add` (not manual appends)

---

## Quick Links

- **Command Triggering Guide:** `file 'N5/prefs/system/command-triggering.md'`
- **Incantum User Guide:** `file 'N5/commands/incantum-quickref.md'`
- **Prompt Database:** `file 'N5/data/executables.db' (index only)`
- **Command Catalog:** `file 'N5/commands.md'`
- **Incantum Triggers:** `file 'N5/config/incantum_triggers.json'`

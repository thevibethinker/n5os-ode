# Journal System Specification for N5 OS

**Version**: 1.0.0  
**Created**: 2025-10-09  
**Status**: Ready for Implementation  
**Priority**: TOP PRIORITY

---

## Purpose

This document provides complete specifications to build a personal journal system for N5 OS. Use this document to bootstrap the journal system in a new conversation by providing all context, requirements, and implementation details.

---

## System Context

### What is N5 OS?

N5 OS is a personal operating system built on Zo Computer that manages knowledge, commands, workflows, and daily operations for Vrijen Attawar. It consists of:

- **Commands**: Registered operations in `N5/config/commands.jsonl`
- **Scripts**: Python executables in `N5/scripts/`
- **Knowledge**: Information stores in `Knowledge/` and `Personal/`
- **Lists**: Structured data in `Lists/`
- **Preferences**: System rules in `N5/prefs/`

### Integration Points

The journal system will integrate with:

1. **Command Registry** (`N5/config/commands.jsonl`) — Register all journal commands
2. **Lists System** — Tag journal entries with list items
3. **Knowledge Base** — Reference knowledge in journal entries
4. **Git** — Version control all journal entries
5. **Search** — Full-text search across entries

---

## Journal System Overview

### Core Functionality

The journal system provides rapid, structured personal journaling with:

1. **Quick Entry Capture** — Fast text-based journal entry creation
2. **Flexible Tagging** — Tag entries with mood, topics, projects, people
3. **Time-based Organization** — Automatic dating and chronological storage
4. **Rich Search** — Search by date, tags, content, mood
5. **Review Interface** — View entries by date range or filters
6. **Export Capability** — Generate reports and summaries

### Design Principles

1. **Speed First** — Minimize friction to capture thoughts
2. **Structured but Flexible** — Required fields + optional metadata
3. **Privacy by Default** — All entries stored locally, git-tracked
4. **Future-Proof Format** — Plain text markdown for longevity
5. **Extensible** — Easy to add new metadata fields

---

## File Structure

### Directory Layout

```
Personal/
  journal/
    2025/
      01/
        2025-01-15-morning.md
        2025-01-15-evening.md
        2025-01-16-morning.md
      02/
        2025-02-03-midday.md
    .index.json
    README.md
```

### Storage Location

**Primary Path**: `/home/workspace/Personal/journal/`

**Organization**:
- Year folders (`2025/`, `2026/`)
- Month subfolders (`01/`, `02/`, ..., `12/`)
- Date-time stamped entries (`YYYY-MM-DD-{label}.md`)

### Index File

`.index.json` — Auto-generated index for fast searching

```json
{
  "version": "1.0.0",
  "last_updated": "2025-10-09T04:45:00Z",
  "entry_count": 247,
  "entries": [
    {
      "file": "2025/10/2025-10-09-morning.md",
      "date": "2025-10-09",
      "time": "07:30",
      "label": "morning",
      "mood": "energetic",
      "tags": ["careerspan", "planning", "priorities"],
      "word_count": 342
    }
  ]
}
```

---

## Entry Schema

### Markdown Format

Each journal entry is a standalone markdown file:

```markdown
---
date: 2025-10-09
time: 07:30
label: morning
mood: energetic
energy: 8
tags:
  - careerspan
  - planning
  - priorities
people:
  - alice
  - bob
projects:
  - n5-os
  - careerspan-v2
location: home-office
---

# Morning Journal — October 9, 2025

## What's on my mind

[Entry content here — free-form markdown]

## Priorities for today

- Build journal system
- Review meeting notes
- Follow up with Alice

## Reflections

[Optional reflections]

## Action Items

- [ ] Task one
- [ ] Task two

---

*Entry created with `journal-add` command*
```

### Required Fields

1. **date** (YYYY-MM-DD) — Entry date
2. **time** (HH:MM) — Entry time (24-hour format)
3. **label** (string) — Entry label (morning, evening, midday, etc.)

### Optional Fields

1. **mood** (string) — Emotional state (happy, anxious, energetic, tired, focused, etc.)
2. **energy** (integer 1-10) — Energy level
3. **tags** (array) — Topic tags
4. **people** (array) — People mentioned
5. **projects** (array) — Projects referenced
6. **location** (string) — Physical location
7. **weather** (string) — Weather conditions
8. **gratitude** (array) — Things grateful for

---

## Commands to Build

### 1. `journal-add`

**Purpose**: Create a new journal entry

**Usage**:
```bash
journal-add [--label morning|evening|midday|quick] [--mood MOOD] [--energy 1-10] [--tags TAG1,TAG2] [--prompt]
```

**Behavior**:
1. Prompt user for content (or use `--prompt` for guided questions)
2. Auto-generate date/time
3. Collect optional metadata (mood, energy, tags)
4. Create markdown file in correct date folder
5. Update `.index.json`
6. Git commit with message "Journal entry: YYYY-MM-DD label"

**Examples**:
```bash
journal-add --label morning --mood energetic --energy 8
journal-add --label quick --tags "meeting,careerspan"
journal-add --prompt  # Guided entry with questions
```

**Script**: `N5/scripts/n5_journal_add.py`

---

### 2. `journal-view`

**Purpose**: View journal entries

**Usage**:
```bash
journal-view [--date YYYY-MM-DD] [--range YYYY-MM-DD:YYYY-MM-DD] [--last N] [--label LABEL] [--mood MOOD] [--tags TAG1,TAG2]
```

**Behavior**:
1. Query `.index.json` based on filters
2. Load matching entry files
3. Display formatted output (date, mood, excerpt)
4. Offer to open full entries

**Examples**:
```bash
journal-view --date 2025-10-09
journal-view --last 7  # Last 7 entries
journal-view --range 2025-10-01:2025-10-09
journal-view --mood energetic
journal-view --tags careerspan
```

**Script**: `N5/scripts/n5_journal_view.py`

---

### 3. `journal-search`

**Purpose**: Full-text search across journal entries

**Usage**:
```bash
journal-search "search query" [--date-range YYYY-MM-DD:YYYY-MM-DD] [--tags TAG1,TAG2]
```

**Behavior**:
1. Search entry content using `grep` or Python full-text search
2. Search metadata in `.index.json`
3. Return matching entries with context
4. Highlight matching terms

**Examples**:
```bash
journal-search "meeting with Alice"
journal-search "careerspan strategy" --date-range 2025-10-01:2025-10-09
journal-search "priorities" --tags planning
```

**Script**: `N5/scripts/n5_journal_search.py`

---

### 4. `journal-edit`

**Purpose**: Edit an existing journal entry

**Usage**:
```bash
journal-edit [--date YYYY-MM-DD] [--label LABEL] [--last]
```

**Behavior**:
1. Find entry by date/label or use most recent
2. Open in editor or provide inline edit capability
3. Update `.index.json` if metadata changed
4. Git commit with message "Updated journal: YYYY-MM-DD label"

**Examples**:
```bash
journal-edit --date 2025-10-09 --label morning
journal-edit --last  # Edit most recent entry
```

**Script**: `N5/scripts/n5_journal_edit.py`

---

### 5. `journal-stats`

**Purpose**: Generate statistics and insights

**Usage**:
```bash
journal-stats [--range YYYY-MM-DD:YYYY-MM-DD] [--summary]
```

**Behavior**:
1. Analyze `.index.json`
2. Generate statistics:
   - Total entries
   - Entries by month
   - Most common moods
   - Most common tags
   - Average energy levels
   - Longest streak
3. Display charts/graphs (text-based)

**Examples**:
```bash
journal-stats
journal-stats --range 2025-10-01:2025-10-09
journal-stats --summary  # Brief overview
```

**Script**: `N5/scripts/n5_journal_stats.py`

---

### 6. `journal-export`

**Purpose**: Export journal entries to various formats

**Usage**:
```bash
journal-export [--format pdf|html|markdown] [--range YYYY-MM-DD:YYYY-MM-DD] [--output FILE]
```

**Behavior**:
1. Collect entries based on range
2. Compile into single document
3. Convert to requested format
4. Save to output location

**Examples**:
```bash
journal-export --format pdf --range 2025-10-01:2025-10-31 --output october-journal.pdf
journal-export --format markdown --last 30
```

**Script**: `N5/scripts/n5_journal_export.py`

---

## Implementation Steps

### Phase 1: Core Setup (Day 1)

1. **Create directory structure**
   ```bash
   mkdir -p /home/workspace/Personal/journal/2025/{01..12}
   ```

2. **Create README.md** in `Personal/journal/`
   - Explain journal system
   - Document entry format
   - List available commands

3. **Create `.index.json`** starter file

4. **Create schema file** at `N5/schemas/journal-entry.schema.json`

### Phase 2: Build `journal-add` (Day 1-2)

1. **Create command definition** at `N5/commands/journal-add.md`
2. **Create Python script** at `N5/scripts/n5_journal_add.py`
3. **Implement core functionality**:
   - Date/time capture
   - File creation
   - YAML frontmatter generation
   - Content prompting
   - Index update
   - Git commit
4. **Register command** in `N5/config/commands.jsonl`
5. **Test with multiple entry types**

### Phase 3: Build `journal-view` (Day 2)

1. **Create command definition** at `N5/commands/journal-view.md`
2. **Create Python script** at `N5/scripts/n5_journal_view.py`
3. **Implement filtering and display**
4. **Register command**
5. **Test various filters**

### Phase 4: Build `journal-search` (Day 2-3)

1. **Create command definition** at `N5/commands/journal-search.md`
2. **Create Python script** at `N5/scripts/n5_journal_search.py`
3. **Implement full-text search**
4. **Register command**
5. **Test search accuracy**

### Phase 5: Build Additional Commands (Day 3-4)

1. Build `journal-edit`
2. Build `journal-stats`
3. Build `journal-export`

### Phase 6: Integration & Polish (Day 4-5)

1. **Integrate with lists**: Tag journal entries with list items
2. **Add to docgen**: Ensure commands appear in documentation
3. **Create examples**: Add to `N5/examples/`
4. **User testing**: Test full workflows
5. **Documentation**: Update prefs and README

---

## Technical Specifications

### Python Script Template

```python
#!/usr/bin/env python3
"""
N5 OS Journal System - [COMMAND NAME]
Version: 1.0.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Constants
JOURNAL_ROOT = Path("/home/workspace/Personal/journal")
INDEX_FILE = JOURNAL_ROOT / ".index.json"
SCHEMA_FILE = Path("/home/workspace/N5/schemas/journal-entry.schema.json")

def main():
    parser = argparse.ArgumentParser(description="[COMMAND DESCRIPTION]")
    # Add arguments here
    args = parser.parse_args()
    
    # Implementation here
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Index Management

**Update Index Function**:
```python
def update_index(entry_data: Dict) -> None:
    """Update .index.json with new entry data"""
    index = load_index()
    index['entries'].append(entry_data)
    index['entry_count'] = len(index['entries'])
    index['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    save_index(index)
```

**Search Index Function**:
```python
def search_index(filters: Dict) -> List[Dict]:
    """Search index with filters"""
    index = load_index()
    results = index['entries']
    
    if 'date' in filters:
        results = [e for e in results if e['date'] == filters['date']]
    
    if 'mood' in filters:
        results = [e for e in results if e.get('mood') == filters['mood']]
    
    if 'tags' in filters:
        filter_tags = set(filters['tags'])
        results = [e for e in results if filter_tags.intersection(set(e.get('tags', [])))]
    
    return results
```

### Git Integration

**Auto-commit Function**:
```python
import subprocess

def git_commit_entry(entry_file: Path, message: str) -> None:
    """Commit journal entry to git"""
    subprocess.run(['git', 'add', str(entry_file)], cwd='/home/workspace')
    subprocess.run(['git', 'add', str(INDEX_FILE)], cwd='/home/workspace')
    subprocess.run(['git', 'commit', '-m', message], cwd='/home/workspace')
```

---

## Command Registry Entries

Add these to `N5/config/commands.jsonl`:

```json
{"command": "journal-add", "file": "N5/commands/journal-add.md", "description": "Create a new journal entry with optional metadata", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_add.py"}
{"command": "journal-view", "file": "N5/commands/journal-view.md", "description": "View journal entries with filters by date, mood, tags", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_view.py"}
{"command": "journal-search", "file": "N5/commands/journal-search.md", "description": "Full-text search across all journal entries", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_search.py"}
{"command": "journal-edit", "file": "N5/commands/journal-edit.md", "description": "Edit an existing journal entry", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_edit.py"}
{"command": "journal-stats", "file": "N5/commands/journal-stats.md", "description": "Generate statistics and insights from journal entries", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_stats.py"}
{"command": "journal-export", "file": "N5/commands/journal-export.md", "description": "Export journal entries to PDF, HTML, or compiled markdown", "category": "journal", "script": "/home/workspace/N5/scripts/n5_journal_export.py"}
```

---

## Example Workflows

### Morning Routine

```bash
# Quick morning journal entry
journal-add --label morning --prompt

# Prompts:
# - How did you sleep? (1-10)
# - What's your energy level? (1-10)
# - What's your mood? (happy, anxious, focused, etc.)
# - What are your top 3 priorities today?
# - Any concerns or blockers?
```

### Evening Review

```bash
# Evening reflection
journal-add --label evening --prompt

# Prompts:
# - What did you accomplish today?
# - What went well?
# - What could have gone better?
# - What are you grateful for?
# - How are you feeling now? (mood + energy)
```

### Weekly Review

```bash
# View last week's entries
journal-view --last 7

# Generate stats
journal-stats --range 2025-10-02:2025-10-09

# Export to PDF
journal-export --format pdf --range 2025-10-02:2025-10-09 --output weekly-review.pdf
```

---

## Safety & Privacy

### Data Protection

1. **Local Storage Only** — All entries stored in `Personal/journal/`
2. **Git Tracking** — Version control for history and recovery
3. **No External Services** — No cloud sync by default
4. **Encryption Option** — Future: Add GPG encryption for sensitive entries

### Backup Strategy

1. **Git commits** — Every entry auto-committed
2. **Weekly backup** — Scheduled task to backup to external location
3. **Export capability** — Regular exports to PDF for archival

---

## Future Enhancements

### Phase 2 Features (Later)

1. **Voice Entry** — Capture journal entries via voice transcription
2. **Rich Media** — Attach images, audio clips to entries
3. **Analytics Dashboard** — Visual insights (mood trends, productivity patterns)
4. **AI Insights** — Analyze patterns and provide insights
5. **Prompts Library** — Customizable journal prompts
6. **Templates** — Pre-defined entry types (gratitude, decision log, meeting notes)
7. **Encryption** — Encrypt sensitive entries with GPG
8. **Mobile Sync** — Sync with mobile journaling app

---

## Success Criteria

The journal system is successful when:

1. ✅ Can create entry in <60 seconds
2. ✅ Can search and find specific entries in <30 seconds
3. ✅ Can view entries from any date range
4. ✅ All entries are git-tracked automatically
5. ✅ Index stays in sync with actual files
6. ✅ Export generates readable PDFs
7. ✅ Used daily for at least 30 days

---

## Support & Troubleshooting

### Common Issues

**Issue**: Index out of sync  
**Solution**: Run `journal-reindex` to rebuild from files

**Issue**: Can't find old entry  
**Solution**: Use `journal-search` with broad query, then narrow down

**Issue**: Git conflicts  
**Solution**: Manual merge, entries are plain text

---

## Quick Start Guide

To implement this system in a new chat:

1. **Copy this entire document** into the new chat
2. **Say**: "Build the journal system according to this spec. Start with Phase 1 and Phase 2 (journal-add command)."
3. **Provide context**: "This is for N5 OS on Zo Computer. Follow all N5 conventions (commands.jsonl, script structure, git commits)."
4. **Test immediately**: Once `journal-add` works, create a test entry
5. **Iterate**: Build remaining commands one at a time

---

## Related Documentation

- **N5 OS Core**: `/home/workspace/Documents/N5.md`
- **Preferences**: `/home/workspace/N5/prefs/prefs.md`
- **Command Registry**: `/home/workspace/N5/config/commands.jsonl`
- **Lists System**: `/home/workspace/N5/commands/lists-add.md` (reference for patterns)
- **System Status**: Analysis document in conversation workspace

---

## Changelog

- **2025-10-09**: Initial specification created
- **[Future]**: Track updates and iterations here

---

*This specification is ready for implementation. Estimated build time: 4-5 days for full system.*

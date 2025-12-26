# Conversation Database Guide

**Track, search, and analyze all conversations with your AI**

---

## Overview

The conversation database (`conversation_registry.py`) maintains a structured record of every conversation, enabling:
- **Search**: Find past conversations by topic, date, or outcome
- **Analytics**: Understand usage patterns
- **Continuity**: Resume context from prior work
- **Troubleshooting**: Debug issues by reviewing conversation history

**Storage**: `N5/runtime/conversation_registry.jsonl`

---

## Quick Reference

### List Recent Conversations

```bash
# Last 10 conversations
python3 N5/scripts/n5_convo_list.py --limit 10

# Today's conversations
python3 N5/scripts/n5_convo_list.py --since today

# This week
python3 N5/scripts/n5_convo_list.py --since "7 days ago"
```

### Search Conversations

```bash
# By topic
python3 N5/scripts/n5_convo_search.py "bootstrap package"

# By tag
python3 N5/scripts/n5_convo_search.py --tag build

# By date range
python3 N5/scripts/n5_convo_search.py --from "2025-10-20" --to "2025-10-26"
```

### Show Conversation Details

```bash
# Full details for a conversation
python3 N5/scripts/n5_convo_show.py con_ABC123

# Includes: title, summary, tags, artifacts, duration, outcome
```

---

## Database Schema

Each conversation is stored as a JSONL record:

```json
{
  "id": "con_ABC123",
  "title": "N5 OS Bootstrap Package Creation",
  "started_at": "2025-10-26T20:44:00Z",
  "ended_at": "2025-10-26T22:30:00Z",
  "duration_minutes": 106,
  "type": "build",
  "tags": ["n5os", "bootstrap", "github", "deployment"],
  "summary": "Built and deployed N5 OS core v1.0 bootstrap package to GitHub...",
  "artifacts": [
    "/home/.z/workspaces/con_OXimtL6DGe7aYAJA/n5os-core-v2/",
    "https://github.com/vrijenattawar/n5os-core"
  ],
  "outcome": "complete",
  "key_decisions": [
    "MIT license for core",
    "Config separation for privacy",
    "Generous core approach"
  ],
  "files_created": 65,
  "commands_run": 42,
  "tools_used": ["create_or_rewrite_file", "run_bash_command", "read_file"],
  "follow_up_needed": false,
  "related_conversations": ["con_XYZ789"]
}
```

---

## Automatic Tracking

### On Conversation Start

Zo automatically runs (via rule):
```bash
python3 N5/scripts/session_state_manager.py init \
  --convo-id con_ABC123 \
  --load-system
```

This creates:
1. Session state file
2. Conversation registry entry
3. Workspace directory

### During Conversation

- AI updates session state as work progresses
- Tracks files created, commands run, decisions made
- Tags conversation based on activity

### On Conversation End

```bash
# AI or user triggers
python3 N5/scripts/n5_conversation_end.py \
  --convo-id con_ABC123 \
  --summary "Bootstrap package deployed successfully" \
  --outcome complete
```

Updates registry with:
- Final summary
- Total duration
- Artifacts created
- Outcome status (complete/incomplete/blocked)

---

## Querying the Database

### Python API

```python
from conversation_registry import ConversationRegistry

# Initialize
registry = ConversationRegistry()

# Get conversation
convo = registry.get("con_ABC123")
print(convo['title'])
print(convo['summary'])

# Search
results = registry.search(
    query="bootstrap",
    tags=["build"],
    from_date="2025-10-01",
    to_date="2025-10-31"
)

for c in results:
    print(f"{c['id']}: {c['title']}")

# Get stats
stats = registry.stats()
print(f"Total conversations: {stats['total']}")
print(f"This month: {stats['this_month']}")
print(f"Avg duration: {stats['avg_duration_minutes']} min")
```

### Command Line

```bash
# Export to CSV for analysis
python3 N5/scripts/n5_convo_list.py --format csv > conversations.csv

# Get JSON for specific conversation
python3 N5/scripts/n5_convo_show.py con_ABC123 --format json > conversation.json

# Weekly summary
python3 N5/scripts/n5_convo_list.py --since "7 days ago" --stats
```

---

## Troubleshooting Use Cases

### For Users

**"What did we work on last week?"**
```bash
python3 N5/scripts/n5_convo_list.py --since "7 days ago"
```

**"Where's that file we created?"**
```bash
python3 N5/scripts/n5_convo_search.py "filename" --show-artifacts
```

**"Resume that project about X"**
```bash
# Find conversation
python3 N5/scripts/n5_convo_search.py "X"
# Get ID, then
python3 N5/scripts/n5_convo_show.py con_ABC123
# Read session state to resume
```

### For Consultants

**"Show me what the user has been working on"**
```bash
# Last 20 conversations with summaries
python3 N5/scripts/n5_convo_list.py --limit 20 --verbose
```

**"What files were created in conversation X?"**
```bash
python3 N5/scripts/n5_convo_show.py con_ABC123 --show-artifacts
```

**"Find all conversations about Y topic"**
```bash
python3 N5/scripts/n5_convo_search.py "Y" --show-context
```

**"Usage patterns over last month"**
```bash
python3 N5/scripts/n5_convo_list.py --since "30 days ago" --stats
# Shows: total conversations, types, avg duration, most-used tools
```

---

## Privacy & Data Management

### What's Tracked

✅ Metadata (ID, timestamps, duration, type)  
✅ Summary (high-level description)  
✅ Tags (categories)  
✅ Artifacts (files/URLs created)  
✅ Outcome (complete/incomplete/blocked)

❌ **Not tracked**: Full conversation text, sensitive data, user configs

### Export Your Data

```bash
# Full registry export
cat N5/runtime/conversation_registry.jsonl > my_conversations.jsonl

# Human-readable format
python3 N5/scripts/n5_convo_list.py --format md > conversations.md
```

### Clean Up Old Data

```bash
# Archive conversations older than 90 days
python3 N5/scripts/n5_convo_list.py --archive --older-than 90

# Delete incomplete conversations older than 30 days
python3 N5/scripts/n5_convo_list.py --delete --incomplete --older-than 30
```

---

## Integration with Session State

**Session state** = real-time context during conversation  
**Conversation database** = permanent record after conversation

They work together:
1. Session state tracks work-in-progress
2. On conversation end, state → summarized → database entry
3. Database enables search/analytics across all conversations

---

## Best Practices

### For Users
1. **Let AI title** - Don't override auto-generated titles unless wrong
2. **Tag consistently** - Use standard tags (build, research, planning)
3. **Review monthly** - Check `--stats` to understand usage patterns

### For AI
1. **Summarize clearly** - Write summaries a future AI (or consultant) can understand
2. **Track artifacts** - List all files/URLs created
3. **Note outcomes** - Mark complete/incomplete/blocked honestly

### For Consultants
1. **Start with database** - Review recent conversations before asking user
2. **Search before asking** - User might have already worked on similar issue
3. **Check outcomes** - Incomplete conversations = potential issues

---

## Maintenance

### Daily (Automatic via scheduled task)

```bash
# Rebuild index if registry becomes slow
python3 N5/scripts/n5_index_rebuild.py
```

### Monthly (Manual)

```bash
# Archive old conversations
python3 N5/scripts/n5_convo_list.py --archive --older-than 90

# Check database health
python3 N5/scripts/n5_convo_list.py --stats --validate
```

---

## Why This Matters

**Without conversation database**:
- ❌ Can't find prior work
- ❌ Repeat same tasks multiple times
- ❌ No usage analytics
- ❌ Consultant blind to history

**With conversation database**:
- ✅ Instant search across all work
- ✅ Never repeat solved problems
- ✅ Understand usage patterns
- ✅ Consultant has full context

**For remote troubleshooting**: This is ESSENTIAL. Conversation database = your work history in queryable form.

---

**Version**: 1.0-core  
**Script**: `N5/scripts/conversation_registry.py`  
**Required**: Yes (automatic)  
**Date**: 2025-10-26

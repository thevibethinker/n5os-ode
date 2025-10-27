---
description: |
  Diagnose conversation metadata quality and propose cleanup/improvements.
  Uses conversations.db to analyze titles, types, relationships, and suggest batch operations.
tags:
  - system
  - diagnostics
  - maintenance
  - conversations
---
# Conversation Diagnostics

## Purpose
Analyze conversation metadata in conversations.db to identify:
- Incomplete or generic titles
- Misclassified conversation types
- Orphaned worker threads
- Old conversations ready for archive
- Missing relationships (parent/child)

## Quick Start

```bash
# List all related conversations by type in last 7 days
python3 N5/scripts/convo_supervisor.py list-related --type build --window-days 7

# Find conversations with poor titles
python3 N5/scripts/convo_supervisor.py list-related --window-days 30 | grep "None\|Untitled"

# Propose title improvements (dry-run default)
python3 N5/scripts/convo_supervisor.py propose-rename --type build --strategy focus_based

# Propose archive moves for old completed work
python3 N5/scripts/convo_supervisor.py propose-archive --older-than-days 30 --exclude-starred

# Generate summary of related conversations
python3 N5/scripts/convo_supervisor.py summarize --type build --window-days 7 --include-artifacts
```

## Common Diagnostics

### 1. Find Untitled Conversations
```bash
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT id, created_at, type, status FROM conversations WHERE title IS NULL OR title = '' ORDER BY created_at DESC LIMIT 20;"
```

### 2. Find Worker Threads Without Parents
```bash
python3 N5/scripts/convo_supervisor.py list-related --parent MISSING
```

### 3. Find Old Active Conversations
```bash
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT id, title, type, created_at FROM conversations WHERE status = 'active' AND date(created_at) < date('now', '-30 days') ORDER BY created_at;"
```

### 4. Count Conversations by Status
```bash
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT status, type, COUNT(*) as count FROM conversations GROUP BY status, type ORDER BY status, count DESC;"
```

### 5. Find Conversations Without Focus
```bash
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT id, title, type FROM conversations WHERE focus IS NULL OR focus = 'What is this conversation specifically about?' LIMIT 20;"
```

## Batch Operations

### Preview Rename Proposals
```bash
# Focus-based strategy (uses conversation focus field)
python3 N5/scripts/convo_supervisor.py propose-rename \
  --type build \
  --window-days 14 \
  --strategy focus_based \
  --output /tmp/rename_proposals.json

# Pattern-based strategy (extracts from conversation content)
python3 N5/scripts/convo_supervisor.py propose-rename \
  --type discussion \
  --window-days 7 \
  --strategy pattern_based
```

### Preview Archive Proposals
```bash
# Find old completed conversations
python3 N5/scripts/convo_supervisor.py propose-archive \
  --older-than-days 30 \
  --status complete \
  --exclude-starred \
  --output /tmp/archive_proposals.json

# Review the proposals
cat /tmp/archive_proposals.json | jq '.proposals[] | {id, title, age_days, reason}'
```

### Execute Approved Renames
```bash
# After reviewing proposals, execute with --execute flag
python3 N5/scripts/convo_supervisor.py execute-rename \
  --ids con_ABC,con_DEF,con_GHI \
  --execute \
  --output /tmp/rename_results.json
```

## Health Metrics

### Overall Conversation Health
```bash
echo "=== Conversation Health Report ===" && \
echo "" && \
echo "Total conversations:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT COUNT(*) FROM conversations;" && \
echo "" && \
echo "By type:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT type, COUNT(*) FROM conversations GROUP BY type;" && \
echo "" && \
echo "By status:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT status, COUNT(*) FROM conversations GROUP BY status;" && \
echo "" && \
echo "Untitled:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT COUNT(*) FROM conversations WHERE title IS NULL OR title = '';" && \
echo "" && \
echo "Without focus:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT COUNT(*) FROM conversations WHERE focus IS NULL OR focus LIKE '%What is this conversation%';" && \
echo "" && \
echo "Worker threads:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT COUNT(*) FROM conversations WHERE parent_id IS NOT NULL;" && \
echo "" && \
echo "Starred:" && \
sqlite3 /home/workspace/N5/data/conversations.db "SELECT COUNT(*) FROM conversations WHERE starred = 1;"
```

### Artifact Production
```bash
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT c.id, c.title, COUNT(a.id) as artifact_count 
   FROM conversations c 
   LEFT JOIN artifacts a ON c.id = a.conversation_id 
   GROUP BY c.id 
   HAVING artifact_count > 0 
   ORDER BY artifact_count DESC 
   LIMIT 10;"
```

## Maintenance Workflows

### Weekly Cleanup
1. Run diagnostics to find issues
2. Review and approve rename proposals
3. Execute approved renames
4. Archive old completed work
5. Update starred status for important threads

### Monthly Review
1. Generate health metrics report
2. Review conversation type distribution
3. Identify patterns in untitled conversations
4. Update conversation relationships
5. Clean up orphaned worker threads

## Database Direct Access

### Useful Queries
```sql
-- Recent conversations with full metadata
SELECT id, title, type, status, focus, created_at 
FROM conversations 
WHERE date(created_at) > date('now', '-7 days') 
ORDER BY created_at DESC;

-- Worker thread relationships
SELECT 
  p.id as parent_id, 
  p.title as parent_title,
  c.id as child_id,
  c.title as child_title,
  c.created_at
FROM conversations c
JOIN conversations p ON c.parent_id = p.id
ORDER BY c.created_at DESC;

-- Conversations by productivity (artifact count)
SELECT 
  c.type,
  COUNT(DISTINCT c.id) as convo_count,
  COUNT(a.id) as total_artifacts,
  ROUND(CAST(COUNT(a.id) AS FLOAT) / COUNT(DISTINCT c.id), 2) as avg_artifacts_per_convo
FROM conversations c
LEFT JOIN artifacts a ON c.id = a.conversation_id
GROUP BY c.type;
```

## Integration with SESSION_STATE

The supervisor reads conversation metadata from:
1. conversations.db (primary source)
2. SESSION_STATE.md files (supplemental context)

To update SESSION_STATE fields that feed the database:
```bash
python3 N5/scripts/session_state_manager.py update \
  --convo-id con_XXX \
  --field Focus \
  --value "Clear description of conversation purpose"
```

## See Also

- file 'N5/scripts/convo_supervisor.py' - Main supervisor script
- file 'N5/scripts/session_state_manager.py' - Session state management
- file 'N5/scripts/conversation_registry.py' - Database operations
- file 'Recipes/System/Orchestrator Thread.md' - Orchestrator workflow
- file 'Documents/N5.md' - Overall system architecture

## Success Criteria

✅ All active conversations have meaningful titles  
✅ All conversations have accurate type classification  
✅ Worker threads properly linked to parents  
✅ Old completed work archived regularly  
✅ Starred conversations marked appropriately  
✅ Health metrics tracked over time

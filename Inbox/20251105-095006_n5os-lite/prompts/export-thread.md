---
tool: true
description: Export conversation thread with context and artifacts
tags: [workflow, archival, export]
version: 1.0
created: 2025-11-03
---

# Export Thread

Export complete conversation thread including messages, artifacts, and context for archival or sharing.

## Instructions

**You are exporting a conversation thread.**

### 1. Gather Thread Information

**Collect:**
- Thread ID and creation date
- Topic/focus of conversation
- Key participants (if multi-user)
- Total messages and duration

### 2. Identify Artifacts

**Scan for:**
- Files created during conversation
- Scripts generated
- Documentation produced
- Data files or outputs
- Temporary work files

**Categorize:**
- **Keep:** Final outputs, documentation, reusable scripts
- **Discard:** Temp files, intermediate outputs, debug logs

### 3. Create Export Bundle

**Structure:**
```
exports/
└── thread_{id}_{date}/
    ├── THREAD_SUMMARY.md
    ├── conversation.md (or .txt)
    ├── artifacts/
    │   ├── docs/
    │   ├── scripts/
    │   └── data/
    └── metadata.json
```

### 4. Write Thread Summary

**Format:**
```markdown
# Conversation Export

**ID:** {thread_id}
**Date:** {date}
**Topic:** {topic}
**Messages:** {count}

## Summary

{1-2 paragraph overview of what was accomplished}

## Key Decisions

- {decision 1}
- {decision 2}

## Artifacts Produced

- {artifact 1 with path}
- {artifact 2 with path}

## Next Steps

- {follow-up 1}
- {follow-up 2}
```

### 5. Export Conversation

**Options:**
- Plain text format (simple, portable)
- Markdown format (preserves formatting)
- JSON format (structured, machine-readable)

**Include:**
- All messages with timestamps
- Tool calls and results (optional)
- Context loaded (what files were referenced)

### 6. Package and Compress

**Create archive:**
```bash
cd exports/
tar -czf thread_{id}_{date}.tar.gz thread_{id}_{date}/
```

**Verify:**
- Archive created successfully
- Size is reasonable
- Contents accessible

### 7. Report Export

**Format:**
```
✅ Thread Exported

**Location:** exports/thread_{id}_{date}/
**Archive:** exports/thread_{id}_{date}.tar.gz
**Size:** {size}

**Contents:**
- Thread summary
- {N} messages
- {M} artifacts

**Ready for:** Archival, sharing, documentation
```

## Quality Checks

Before finalizing:
- [ ] Summary is accurate and complete
- [ ] All important artifacts included
- [ ] Temporary files excluded
- [ ] Archive compresses successfully
- [ ] Export location documented

## Related

- Prompt: `close-conversation.md`
- Principles: P2 (Single Source of Truth)
- Principles: P1 (Human-Readable First)

---

**Preserve conversations for future reference.**

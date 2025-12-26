# Session State Management Guide

**Maintain context and continuity across conversations**

---

## Overview

Session state lets conversations maintain context, track progress, and resume work across interruptions. Essential for complex tasks.

**Script**: `N5/scripts/session_state_manager.py`

---

## Quick Start

### Initialize Session State

```bash
# Automatic (via Zo rule)
# When a conversation starts, Zo runs:
python3 N5/scripts/session_state_manager.py init \
  --convo-id con_ABC123 \
  --type build  # or research, discussion, planning

# This creates: N5/runtime/sessions/con_ABC123/SESSION_STATE.md
```

### During Conversation

**AI reads state**:
```bash
# State file tracked automatically
cat N5/runtime/sessions/con_ABC123/SESSION_STATE.md
```

**Update focus/objectives**:
```markdown
## Focus
Building N5 OS bootstrap package for Eric

## Objectives
- [x] Core foundation (59 files)
- [x] Documentation complete
- [ ] Test with Eric
- [ ] Gather feedback
```

### End Session

```bash
# Mark complete and archive
python3 N5/scripts/session_state_manager.py complete \
  --convo-id con_ABC123 \
  --outcome "Bootstrap package deployed to GitHub"
```

---

## Session Types

### Build Sessions
**Type**: `--type build`  
**Use**: Creating, refactoring, implementing  
**State Tracks**: Files created, tests passed, deployment status

### Research Sessions
**Type**: `--type research`  
**Use**: Learning, analyzing, investigating  
**State Tracks**: Sources reviewed, insights captured, questions answered

### Discussion Sessions
**Type**: `--type discussion`  
**Use**: Planning, brainstorming, decision-making  
**State Tracks**: Topics covered, decisions made, action items

### Planning Sessions
**Type**: `--type planning`  
**Use**: Roadmapping, strategy, timeline building  
**State Tracks**: Milestones defined, priorities set, timeline agreed

---

## State File Structure

```markdown
# SESSION STATE

**Conversation ID**: con_ABC123  
**Type**: build  
**Started**: 2025-10-26T20:44:00Z  
**Status**: active

---

## Focus

Current primary objective (1 sentence)

## Objectives

- [x] Completed task
- [ ] In-progress task
- [ ] Pending task

## Context

Key information needed throughout conversation:
- User preferences
- Technical constraints
- Prior decisions

## Progress

### Completed
- Task 1 (timestamp)
- Task 2 (timestamp)

### In Progress
- Task 3 (50% complete)

### Blocked
- Task 4 (waiting on: user feedback)

## Artifacts

Files created this session:
- /path/to/file1.md (purpose)
- /path/to/file2.py (purpose)

## Notes

Important observations, learnings, or reminders for future:
- Note 1
- Note 2

---

**Last Updated**: 2025-10-26T22:00:00Z
```

---

## Troubleshooting Commands

### Check Active Sessions

```bash
# List all active sessions
find N5/runtime/sessions -name "SESSION_STATE.md" -type f

# Count active
find N5/runtime/sessions -name "SESSION_STATE.md" -type f | wc -l
```

### Resume Interrupted Session

```bash
# If conversation dropped mid-task
# AI reads state file and continues from last checkpoint
python3 N5/scripts/session_state_manager.py resume \
  --convo-id con_ABC123
```

### Archive Old Sessions

```bash
# Move completed sessions to archive (after 30 days)
python3 N5/scripts/session_state_manager.py archive \
  --days 30
```

### Debug Session Issues

```bash
# Check session metadata
cat N5/runtime/sessions/con_ABC123/.metadata.json

# View full session history
cat N5/runtime/sessions/con_ABC123/SESSION_STATE.md

# Check if session exists
ls N5/runtime/sessions/ | grep con_ABC123
```

---

## Best Practices

### For Users

1. **Let AI manage state** - Don't edit SESSION_STATE.md manually
2. **Use `/convo:resume`** - If conversation drops, tell AI to check session state
3. **Review at end** - Check state file before closing long conversations

### For AI

1. **Update frequently** - Mark objectives complete as you go
2. **Track artifacts** - List all files created
3. **Note blockers** - Document what's waiting on user input
4. **Write for future AI** - State should be readable without full conversation

### For Consultants

1. **Check state first** - `cat SESSION_STATE.md` before asking "what were you doing?"
2. **Resume context** - State file = instant catch-up on complex work
3. **Debug with state** - If user says "AI forgot something", check state tracking

---

## Integration with Zo Rules

**Required Zo Rule** (in `ZO_SETTINGS_REQUIRED.md`):

```
Initialize SESSION_STATE.md for this conversation workspace by running:

python3 /home/workspace/N5/scripts/session_state_manager.py init \
  --convo-id <current_conversation_id> \
  --load-system

Auto-detect conversation type from user's first message.
```

This ensures every conversation has state tracking from the start.

---

## Advanced: Custom State Fields

```bash
# Add custom tracking field
python3 N5/scripts/session_state_manager.py add-field \
  --convo-id con_ABC123 \
  --field "Budget" \
  --value "3 hours remaining"

# Update custom field
python3 N5/scripts/session_state_manager.py update-field \
  --convo-id con_ABC123 \
  --field "Budget" \
  --value "2 hours remaining"
```

---

## Why This Matters

**Without session state**:
- AI forgets context across long conversations
- Can't resume after interruptions
- No record of what was accomplished
- Repeated questions waste time

**With session state**:
- ✅ Continuous context across hours/days
- ✅ Resume instantly after interruptions
- ✅ Clear record of progress
- ✅ Efficient, no repeated work

---

**Version**: 1.0-core  
**Script**: `N5/scripts/session_state_manager.py`  
**Required**: Yes (via Zo rules)  
**Date**: 2025-10-26

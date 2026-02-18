---
name: thread-close
description: |
  Close normal interactive conversation threads. Handles session state finalization,
  progress summary, and artifact listing.
  For Pulse workers use drop-close. For post-build synthesis use build-close.
compatibility: Created for Zo Computer
metadata:
  author: n5os-ode
---

# Thread Close

Finalizes a normal interactive conversation by summarizing what was accomplished, listing artifacts, and marking the session as closed.

## Close Process

### 1. Read Session State

Load `SESSION_STATE.md` from the conversation workspace. Extract:
- Conversation type and classification
- Progress tracking (tasks completed, tasks remaining)
- Artifacts created or modified during the session
- Any open decisions or deferred items

### 2. Generate Summary

Produce a structured summary covering:
- **What was accomplished**: High-level description of completed work
- **Key decisions made**: Any choices or directions confirmed during the conversation
- **Open items**: Tasks started but not finished, or explicitly deferred

### 3. List Artifacts

Enumerate all files created or modified:
- New files added to the workspace
- Existing files edited
- Files moved or reorganized
- Scripts executed and their outputs

### 4. Update Session State

Set the session status to `closed` with:
- Close timestamp
- Final progress snapshot
- Summary text for future reference

### 5. Suggest Commit Message

If work involved file changes that should be committed, generate a conventional commit message based on the artifacts and summary.

## Usage

```bash
python3 Skills/thread-close/scripts/close.py --convo-id <conversation_id>
```

### Flags

| Flag | Description |
|------|-------------|
| `--convo-id` | Conversation ID (used to locate the workspace) |
| `--dry-run` | Print the close summary without modifying session state |

## Script

- `scripts/close.py` — Reads session state, prints structured close summary, optionally updates state.

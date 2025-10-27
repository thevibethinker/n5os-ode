---
description: 'Command: init-state-session'
tags:
- state-session
- tracking
- initialization
- build
---
# init-state-session

Initialize SESSION_STATE.md for current or specified conversation.

## Usage

```bash
# Auto-detect conversation type from user message
/init-state-session

# Explicit type specification
/init-state-session --type build
/init-state-session --type research
/init-state-session --type discussion
/init-state-session --type planning

# With specific mode
/init-state-session --type build --mode refactor
```

## What It Does

1. Creates SESSION_STATE.md in conversation workspace
2. Auto-classifies conversation type based on context
3. Loads appropriate template (build, research, discussion, planning)
4. Outputs system files to load (N5.md, prefs.md)
5. Sets up tracking structure for the conversation

## Auto-Classification

Keywords trigger types:
- **build**: "implement", "code", "script", "create", "develop", "build"
- **research**: "research", "analyze", "learn", "study", "investigate"
- **discussion**: "discuss", "think", "explore", "brainstorm", "consider"
- **planning**: "plan", "strategy", "decide", "organize", "roadmap"

## Output

- Creates: `/home/.z/workspaces/con_XXX/SESSION_STATE.md`
- Logs system files to load
- Returns initialization confirmation

## Related Commands

- file 'N5/commands/update-state-session.md' - Update state fields
- file 'N5/commands/check-state-session.md' - Read current state
- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Full documentation

---
description: |
  Spawn a parallel worker thread with context handoff.
  
  Creates a lightweight worker assignment file that you open in a new conversation.
  Worker runs independently with full parent context.
  
  **With instruction:**
  python3 N5/scripts/spawn_worker.py --parent <PARENT_ID> --instruction "Your task"
  
  **Agnostic (no instruction):**
  python3 N5/scripts/spawn_worker.py --parent <PARENT_ID>
  
  **Dry-run first:**
  python3 N5/scripts/spawn_worker.py --parent <PARENT_ID> --instruction "..." --dry-run
  
  Then open the generated WORKER_ASSIGNMENT_*.md file in Records/Temporary/ in a NEW conversation.
tags:
  - workers
  - parallel
  - distributed
  - forking
tool: true
---
# Spawn Worker Thread

**Quick Start:**

```bash
# Get current conversation ID
echo $ZO_CONVERSATION_ID

# Spawn with instruction
python3 N5/scripts/spawn_worker.py \
    --parent $ZO_CONVERSATION_ID \
    --instruction "Research OAuth2 alternatives and create comparison table"

# Spawn agnostic (specify task in new conversation)
python3 N5/scripts/spawn_worker.py \
    --parent $ZO_CONVERSATION_ID
```

**What it does:**

1. Captures parent context (SESSION_STATE, recent artifacts)
2. Creates worker assignment file in `Records/Temporary/`
3. Updates parent SESSION_STATE with worker reference
4. Creates `worker_updates/` directory in parent workspace

**Next step:**\
Open the generated `file WORKER_ASSIGNMENT_*.md`   file in a **new conversation**

**Full docs:** `file Documents/System/WORKER_SPAWNING_SYSTEM.md` 
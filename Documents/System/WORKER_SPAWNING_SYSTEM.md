# Worker Spawning System

**Purpose:** Lightweight parallel thread forking for mid-conversation task branching  
**Created:** 2025-10-18  
**Status:** Production-ready

---

## What Is This?

A **lightweight alternative to full distributed builds** that lets you spin up parallel worker conversations mid-stream when:
- A tangential idea emerges that you want to pursue without context-switching
- You need parallel workstreams (parent continues, worker does independent work)
- You want to explore alternatives without polluting current conversation

**Key difference from distributed builds:**
- No heavy upfront planning
- No task decomposition required
- No dependency graphs
- Just: "spin up parallel thread, here's the context and optionally an instruction"

---

## Mental Model

Think **Unix process forking**:
- Parent process continues running
- Child process starts with copy of parent's context
- Both run independently
- Child can write updates back to parent's workspace for awareness

---

## Usage

### Inline Instruction Spawn

```bash
python3 N5/scripts/spawn_worker.py \
    --parent con_CURRENT_ID \
    --instruction "Your specific task for the worker"
```

**What you get:**
- Worker assignment file in `Records/Temporary/`
- Parent SESSION_STATE updated with worker reference
- Worker updates directory created in parent's workspace

**Next step:**  
Open the generated `WORKER_ASSIGNMENT_*.md` file in a **new conversation**

### Agnostic Spawn

```bash
python3 N5/scripts/spawn_worker.py \
    --parent con_CURRENT_ID
```

**Use when:**
- You just want a parallel thread with context
- Will specify task in the new conversation
- Exploring without clear directive yet

### Dry-Run (Always Test First)

```bash
python3 N5/scripts/spawn_worker.py \
    --parent con_CURRENT_ID \
    --instruction "..." \
    --dry-run
```

---

## What Gets Passed to Worker

**Worker assignment file contains:**

1. **Parent Metadata**
   - Parent conversation ID
   - Spawn timestamp
   - Link back to parent

2. **Parent Context**
   - What parent is working on (from SESSION_STATE)
   - Parent's objective
   - Parent's status
   - Recent artifacts generated

3. **Instruction** (if provided)
   - Your specific task for worker
   - Or "agnostic" flag if no directive

4. **Worker Setup Instructions**
   - How to initialize SESSION_STATE
   - How to link back to parent
   - Where to write status updates
   - Communication protocol

---

## Communication Between Parent & Worker

### Worker → Parent

Worker writes status updates to:
```
/home/.z/workspaces/con_PARENT/worker_updates/WORKER_<ID>_status.md
```

**Format:**
```markdown
# Worker Status Update

**Worker ID:** WORKER_3KRS_20251018_180035  
**Updated:** 2025-10-18 14:05 ET  
**Status:** In progress

## Current Task
Researching OAuth2 vs JWT authentication methods

## Progress
- ✅ Completed OAuth2 research
- 🔄 In progress: JWT analysis
- ⏳ Not started: Session tokens

## Blockers
None

## Next
Will complete comparison table by end of session
```

**Frequency:** At natural checkpoints:
- Milestone completions
- Before taking a break
- When blocked
- When complete

### Parent → Worker

- Parent can read worker status updates from `worker_updates/` directory
- Parent can update worker's assignment file if needed (rare)
- Parent can write notes in worker's conversation workspace (if needed)

**Both know about each other through SESSION_STATE linkage**

---

## Worker Workflow

1. **V spawns worker in current conversation:**
   ```bash
   python3 N5/scripts/spawn_worker.py --parent con_ABC --instruction "Do X"
   ```

2. **V opens worker assignment file in NEW conversation**
   - File is in `Records/Temporary/WORKER_ASSIGNMENT_*.md`

3. **Worker (new conversation) initializes:**
   ```bash
   python3 N5/scripts/session_state_manager.py init \
       --convo-id con_NEW_WORKER \
       --load-system
   
   python3 N5/scripts/session_state_manager.py link-parent \
       --parent con_ABC
   ```

4. **Worker does work independently**
   - Processes instruction
   - Creates artifacts in its own workspace
   - Writes status updates to parent's workspace at checkpoints

5. **Parent checks worker status (optional)**
   ```bash
   ls /home/.z/workspaces/con_ABC/worker_updates/
   cat /home/.z/workspaces/con_ABC/worker_updates/WORKER_*_status.md
   ```

6. **Integration happens later** (V manages manually)
   - Worker completes work
   - V reviews artifacts
   - V integrates relevant work back into parent context

---

## Architecture Principles Applied

✅ **P7 (Dry-Run):** Script supports `--dry-run` mode  
✅ **P11 (Failure Modes):** Error handling for missing parent, invalid state  
✅ **P15 (Complete Before Claiming):** Full verification before success  
✅ **P18 (Verify State):** Checks file exists and has content  
✅ **P19 (Error Handling):** Comprehensive try/except with logging  
✅ **P21 (Document Assumptions):** Clear docs on communication protocol  
✅ **P22 (Language Selection):** Python (general default, good corpus)

---

## Files

**Scripts:**
- `file 'N5/scripts/spawn_worker.py'` - Main spawning script
- `file 'N5/scripts/session_state_manager.py'` - Updated with `link-parent` command

**Output:**
- `Records/Temporary/WORKER_ASSIGNMENT_*.md` - Generated worker assignments
- `/home/.z/workspaces/con_PARENT/worker_updates/` - Worker status updates

**Docs:**
- `file 'Documents/System/WORKER_SPAWNING_SYSTEM.md'` (this file)

---

## When to Use This vs. Distributed Builds

**Use Worker Spawning When:**
- ❌ No heavy upfront planning needed
- ❌ Single tangent or quick exploration
- ❌ Parallel work with loose coupling
- ✅ Want minimal overhead
- ✅ Want to preserve parent context/flow

**Use Distributed Builds When:**
- ✅ Large-scale refactor (6+ files)
- ✅ Complex dependencies between tasks
- ✅ Need formal coordination/integration plan
- ✅ Want progress tracking dashboard
- ✅ Multiple workers need to integrate cleanly

---

## Examples

### Example 1: Research Alternative

**Parent conversation:** Building auth system

**Mid-conversation thought:** "Wait, should we use JWT or sessions?"

**Action:**
```bash
python3 N5/scripts/spawn_worker.py \
    --parent con_AUTH_BUILD \
    --instruction "Research JWT vs session tokens: security, scalability, implementation complexity. Create comparison table with recommendation."
```

**Result:**
- Parent continues working on current auth implementation
- Worker researches alternatives in parallel
- Worker writes findings back to parent's workspace
- Parent reviews findings later, decides whether to pivot

### Example 2: Agnostic Exploration

**Parent conversation:** Discussing system architecture

**Mid-conversation thought:** "Let me spin off a thread to prototype this idea"

**Action:**
```bash
python3 N5/scripts/spawn_worker.py --parent con_ARCH_DISC
```

**Result:**
- Worker gets full parent context
- Worker conversation starts: "Here's what parent is doing, what should I work on?"
- V specifies task in worker conversation
- Both continue independently

### Example 3: Parallel Implementation

**Parent conversation:** Implementing feature A

**Mid-conversation thought:** "Feature B is unrelated but also needs work"

**Action:**
```bash
python3 N5/scripts/spawn_worker.py \
    --parent con_FEATURE_A \
    --instruction "Implement Feature B: user profile page with avatar upload"
```

**Result:**
- Parent finishes Feature A
- Worker implements Feature B simultaneously
- Both ship independently

---

## Troubleshooting

**Error: "Parent SESSION_STATE.md not found"**
```bash
# Initialize parent first
python3 N5/scripts/session_state_manager.py init \
    --convo-id con_PARENT \
    --load-system
```

**Error: "Cannot determine current conversation ID" (link-parent)**
- Make sure you're running from within a Zo conversation
- The script uses `ZO_CONVERSATION_ID` environment variable

**Worker assignment file is empty**
- Check parent conversation has SESSION_STATE.md
- Try dry-run first to see what would be generated

---

## Future Enhancements

**Potential additions:**
- Auto-merge worker artifacts back to parent workspace
- Worker completion notifications (write to parent status)
- Command wrapper for easier invocation
- Integration with distributed builds system

**Not planned:**
- Real-time sync (defeats purpose of independent threads)
- Automatic task generation (keep lightweight)
- Worker-to-worker communication (parent is hub)

---

## Meta

**Version:** 1.0  
**Last Updated:** 2025-10-18  
**Maintainer:** V (via Vibe Builder)  
**Status:** Production-ready, tested

**Related Docs:**
- `file 'Documents/System/HOW_TO_USE_DISTRIBUTED_BUILDS.md'` - For heavy orchestration
- `file 'N5/prefs/operations/distributed-builds/protocol.md'` - Full distributed builds
- `file 'Documents/System/SESSION_STATE_SYSTEM.md'` - Session state management

---

*Built with Vibe Builder persona following architectural principles*

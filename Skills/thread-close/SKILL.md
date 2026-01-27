---
name: thread-close
description: |
  Close normal interactive conversation threads. Handles tier detection,
  position extraction, AAR generation, and commit suggestions.
  For Pulse workers use drop-close. For post-build synthesis use build-close.
---

# Thread Close

Close interactive conversation threads with semantic synthesis.

## Recommended: Use the Router

The **router** auto-detects your context and calls the correct close skill:

```bash
# Auto-detect and route to correct skill
python3 Skills/thread-close/scripts/router.py --convo-id con_XXXXX

# Preview what would happen
python3 Skills/thread-close/scripts/router.py --convo-id con_XXXXX --dry-run

# Force build-close mode
python3 Skills/thread-close/scripts/router.py --slug my-build
```

The router reads SESSION_STATE and detects:
- **drop_id present** → routes to `drop-close`
- **build_slug present** (no drop_id) → routes to `build-close`  
- **neither** → routes to `thread-close`

## When to Use (Direct)

- Normal conversation threads
- Manual orchestrator threads
- Any thread that is NOT a Pulse Drop

**Wrong tool?**
- If you're a Pulse Drop → use `drop-close`
- If closing a completed build → use `build-close`

## Quick Start (Direct)

```bash
# Auto-detect tier and close
python3 Skills/thread-close/scripts/close.py --convo-id con_XXXXX

# Force specific tier
python3 Skills/thread-close/scripts/close.py --convo-id con_XXXXX --tier 3

# Dry run (preview only)
python3 Skills/thread-close/scripts/close.py --convo-id con_XXXXX --dry-run
```

## Tiers

| Tier | When | What It Does |
|------|------|--------------|
| 1 | Simple discussions (<3 artifacts) | Title, summary, SESSION_STATE audit |
| 2 | Standard work (3-10 artifacts) | + Decisions, next steps |
| 3 | Builds, complex work (10+ artifacts) | + AAR, positions, content library |

## Options

- `--convo-id` (required): Conversation ID
- `--tier N`: Force tier 1, 2, or 3
- `--dry-run`: Preview without making changes
- `--force`: Bypass context guards (use carefully)
- `--skip-positions`: Skip position extraction

---

## Title Generation (REQUIRED)

**You MUST generate a title following the 3-slot emoji system.**

### Title Format

```
MMM DD | {state} {type} {content} [parent_context] Semantic Title
```

**Example:** `Jan 24 | ✅ 👷🏽‍♂️ 🏗️ [Close Skills Build] Thread Close Implementation`

### Step-by-Step Title Generation

1. **Run the context gatherer** to get raw data:
   ```bash
   python3 Skills/thread-close/scripts/close.py --convo-id <CONVO_ID>
   ```

2. **Analyze the JSON output** and determine:
   - What was the thread's completion state?
   - What type of thread was this?
   - What was the primary work type?
   - Does this thread have a parent (build or orchestrator)?

3. **Select emojis for each slot:**

   **Slot 1 — State:**
   | Emoji | When to Use |
   |-------|-------------|
   | ✅ | Thread completed successfully |
   | ⏸️ | Action pending, thread paused |
   | 🚧 | Work in progress, to be resumed |
   | ❌ | Thread ended with unresolved errors |
   | ‼️ | Critical action pending |

   **Slot 2 — Type:**
   | Emoji | When to Use |
   |-------|-------------|
   | 📌 | Normal standalone thread (default) |
   | 🐙 | Orchestrator coordinating workers |
   | 👷🏽‍♂️ | Worker spawned by orchestrator |
   | 🔗 | Part of a series or continuation |

   **Slot 3 — Content:**
   | Emoji | When to Use |
   |-------|-------------|
   | 🏗️ | Building functionality, features, systems |
   | 🔎 | Research, search, investigation |
   | 🛠️ | Debug, fix, troubleshoot |
   | 🕸️ | Site/web app work |
   | 🪵 | Log entries, tracking |
   | ✍️ | Content creation, writing |
   | 🪞 | Reflection, strategizing |
   | 🤳 | Social media work |
   | 📊 | Data work, analytics |
   | 💬 | Communications, email |
   | 🗂️ | Organization, cleanup |
   | 📝 | Planning, roadmapping |

4. **Determine parent context** (for square brackets):
   - If `build_slug` in state → Use build title from `N5/builds/<slug>/meta.json`
   - If `orchestrator_id` or `parent_convo_id` → Look up that conversation's title
   - If thread IS an orchestrator → No brackets needed (it IS the parent)
   - If truly standalone → No brackets

5. **Write a semantic title** (2-6 words describing the work)

6. **Call write function** with your generated title:
   ```python
   from N5.lib.close import core
   core.write_thread_close_output(
       convo_id="con_XXX",
       tier=2,
       title="Jan 24 | ✅ 📌 🏗️ Your Semantic Title",
       summary="Brief summary of what was accomplished...",
       decisions=[...],  # Tier 2+
       next_steps=[...], # Tier 2+
   )
   ```

### Parent Context Resolution

**When to include [brackets]:**

| Scenario | Parent Context |
|----------|----------------|
| Worker/Drop in a build | `[Build Title]` from meta.json |
| Continuation of parent thread | `[Parent Thread's Semantic Title]` |
| Picking up an old build in new thread | `[Build Title]` — look up via build_slug |
| Orchestrator thread | **No brackets** — orchestrators ARE the parent |
| Truly standalone thread | **No brackets** |

**How to resolve parent title:**

```python
from N5.lib.close import guards, emoji

# Get orchestrator context
orch_ctx = guards.detect_orchestrator_context(convo_id)

if orch_ctx['parent_title']:
    parent_context = orch_ctx['parent_title']
elif orch_ctx['build_title']:
    parent_context = orch_ctx['build_title']
else:
    parent_context = None  # No brackets

# Or use the emoji module directly:
parent_context = emoji.resolve_parent_context(state, convo_id)
```

---

## What Thread Close Does

1. **Validates context** — Guards check you're not a Drop or build
2. **Detects tier** — Based on artifacts, conversation type
3. **YOU generate title** — Using 3-slot emoji system above
4. **Extracts decisions** — Key choices with rationale (Tier 2+)
5. **Generates AAR** — After-action report (Tier 3)
6. **Extracts positions** — Belief candidates (Tier 3)
7. **Scans content library** — Reusable artifacts (Tier 3)
8. **PII audit** — Checks for sensitive data

### Task System Integration

When closing a conversation, check if it's an action conversation:

1. **Check for action conversation:**
   ```bash
   python3 Skills/task-system/scripts/context.py action-check --convo-id <id>
   ```

2. **If task found**, get completion context:
   ```bash
   python3 Skills/task-system/scripts/context.py completion-check --convo-id <id> --task-id <id>
   ```

3. **Reason about completion** using the context (see task-system SKILL.md)

4. **Show assessment to V:**
   ```
   TASK: Draft investor memo
   
   Assessment: ✅ COMPLETE
   Evidence: investor-memo-v1.md created, matches task intent
   
   Mark as: [complete] [partial] [blocked]
   ```

5. **Update task** based on V's choice:
   ```bash
   python3 Skills/task-system/scripts/task.py complete <id>
   # or
   python3 Skills/task-system/scripts/task.py update <id> --status in_progress
   ```

6. **If partial, get next step:**
   ```bash
   python3 Skills/task-system/scripts/context.py next-step --task-id <id>
   ```
   Show V the suggested follow-up.

### Key Files

- `file 'Skills/task-system/scripts/context.py'` — Context gathering for AI reasoning (action-check, completion-check, next-step)
- `file 'Skills/task-system/scripts/task.py'` — Task operations (add, list, complete, update, tag-conversation)
- `file 'Skills/task-system/scripts/db.py'` — Database operations
- `file 'Skills/task-system/SKILL.md'` — Complete task system documentation and reasoning discipline
- `file 'N5/lib/close/core.py'` — Thread close core functions with task integration support

---

## Output

```
Running thread-close (Tier 2) for con_XXXXX

✓ Title: Jan 24 | ✅ 📌 🏗️ Build Close Skills
✓ Decisions extracted: 3
✓ PII audit complete

Thread close complete (Tier 2)
```

## Fail-Safes

This skill includes context guards. If you call it incorrectly:

```
⚠️  WRONG SKILL DETECTED

You called: thread-close
Suggested:  drop-close
Reason:     SESSION_STATE has drop_id

Run the suggested skill instead, or use --force to override.
```

## Reference Files

- `file 'N5/config/emoji-legend.json'` — Full emoji definitions and detection hints
- `file 'N5/lib/close/emoji.py'` — Helper functions for title generation
- `file 'N5/lib/close/guards.py'` — Context detection and validation

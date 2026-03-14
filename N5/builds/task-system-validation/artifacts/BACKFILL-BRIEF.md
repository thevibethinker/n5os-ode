---
task: Proper Task Backfill from Meeting Action Blocks
type: manual_worker
orchestrator: con_OaZwIOzCydglh4r4
---

# Task Backfill Worker

## Context

V wiped the task database because D1.2 did a LAZY backfill — it just looked at calendar events and generated fake "Prepare for X meeting" tasks. That's garbage.

**Real tasks come from:**
1. B05_ACTION_ITEMS blocks from processed meetings
2. Actual commitments V has made
3. Real work that needs doing

**There are 293 B05_ACTION_ITEMS.md files** in `/home/workspace/Personal/Meetings/`

## Your Job

Work WITH V interactively to:

1. **Scan recent B05 blocks** (last 2-4 weeks) for V's action items
2. **Present extracted items** for V's review — don't auto-create
3. **Stage tasks** that V approves (use `stage.py add`)
4. **Promote to real tasks** only after V confirms

## Process

### Step 1: Scan Recent Meetings

```bash
# Find B05 blocks from last 4 weeks
find /home/workspace/Personal/Meetings -name "B05_ACTION_ITEMS.md" -mtime -28 2>/dev/null
```

### Step 2: For Each B05 Block

Read the file and extract action items that are:
- Assigned to V (not other attendees)
- Actionable (not vague "think about X")
- Still relevant (not already done)

**Use semantic understanding, NOT regex.**

Present to V like:
```
From: 2025-12-12 Jonathan Beda meeting

Action items for V:
1. "Send follow-up email with pricing" — External, ~15 min
2. "Draft proposal outline" — Strategic, ~45 min

Stage these? (all / 1,2 / none / skip meeting)
```

### Step 3: Stage Approved Items

```bash
python3 Skills/task-system/scripts/stage.py add "Task title" \
  --domain "careerspan" \
  --priority external \
  --estimate 15 \
  --source "meeting:2025-12-12_Jonathan-Beda" \
  --context "Follow up on pricing discussion"
```

### Step 4: After Scanning All Meetings

Show V the full staged list:
```bash
python3 Skills/task-system/scripts/stage.py list
```

Let V do final review and bulk promote:
```bash
python3 Skills/task-system/scripts/stage.py promote <id> --due 2026-01-27
```

## Key Principles

1. **Never auto-create tasks** — always stage first, V promotes
2. **Semantic extraction** — use LLM understanding, not pattern matching
3. **Interactive** — ask V clarifying questions, don't guess
4. **Recent first** — start with last 2 weeks, go back if V wants more
5. **V's tasks only** — skip action items assigned to other people
6. **Still relevant** — skip items that are clearly already done

## Domain Mapping

- Careerspan business → `careerspan`
- Zo/personal productivity → `zo`
- Personal life → `personal`

## Priority Mapping

- Someone waiting on V → `external`
- Important but no external deadline → `strategic`
- Time-sensitive → `urgent`
- Everything else → `normal`

## Start Here

Begin by asking V:
1. How far back should we scan? (2 weeks? 4 weeks? specific date?)
2. Any meetings to skip? (internal team syncs, etc.)
3. Any domains to focus on? (Careerspan only? Include personal?)

Then start the scan.

## Output

At the end, you should have:
- Staged tasks ready for V's final review
- Clear source attribution (which meeting each task came from)
- V's explicit approval before anything becomes a real task

## Deposit

When done, write to `/home/workspace/N5/builds/task-system-validation/deposits/BACKFILL.json`:
```json
{
  "status": "complete",
  "meetings_scanned": 15,
  "action_items_found": 42,
  "tasks_staged": 18,
  "tasks_promoted": 12,
  "notes_for_orchestrator": "Summary of what V approved"
}
```

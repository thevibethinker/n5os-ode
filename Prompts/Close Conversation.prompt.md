---
title: Close Conversation
description: Formal conversation close - auto-detects tier based on conversation type
tool: true
tags:
  - session
  - cleanup
  - conversation
---

# Close Conversation

Runs the formal **conversation-end workflow** with automatic tier detection.

## Quick Reference

| Tier | When | Cost | Time |
|------|------|------|------|
| 1 (Quick) | Default - simple discussions | ~$0.03 | <30s |
| 2 (Standard) | ≥3 artifacts, research | ~$0.06 | <90s |
| 3 (Full) | Builds, orchestrator, debug | ~$0.15 | <180s |

## Flags

- `--tier=1` / `--tier=2` / `--tier=3`: Force specific tier
- `--dry-run`: Preview without changes

## Execution Steps

### Step 1: Detect Tier

Run the router to determine appropriate tier:

```bash
python3 N5/scripts/conversation_end_router.py --convo-id {CONVO_ID}
```

Review the recommendation and signals. Override with `--tier=N` if needed.

### Step 2: Execute Tier

Based on the tier:

**Tier 1 (Quick):**
```bash
python3 N5/scripts/conversation_end_quick.py --convo-id {CONVO_ID}
```

**Tier 2 (Standard):**
```bash
python3 N5/scripts/conversation_end_standard.py --convo-id {CONVO_ID}
```

**Tier 3 (Full Build):**
```bash
python3 N5/scripts/conversation_end_full.py --convo-id {CONVO_ID}
```

### Step 3: LLM Enhancement

After running the script, enhance the output:

**All Tiers:**
- Generate a proper LLM title if the pattern-based one is insufficient
- Write a 2-3 sentence summary of what was discussed/accomplished
- Review file list and confirm organization

**Tier 2+ Only:**
- Extract key decisions with rationale
- Identify any open items

**Tier 3 Only:**
- Review AAR and enhance with conversation context
- Check: Did this create/modify N5 capabilities?
  - If yes: Note what capability was added/changed
  - If no: Note "No capability changes"
- Check for lessons worth logging

### Step 4: Git Check

If git changes detected:
- Note the changes
- Ask: "Would you like to commit these changes?"

## Output

Present the formatted close output per the tier template.

End with:
```
✅ Conversation closed (Tier N)
```

## Full Documentation

`file 'N5/prefs/operations/conversation-end-v3.md'`


---
title: Close Conversation
description: Formal conversation close - auto-detects tier based on conversation type
tool: true
tags:
  - session
  - cleanup
  - conversation
created: 2025-10-15
last_edited: 2026-01-09
version: 2.1
---

# Close Conversation

Runs the formal **conversation-end workflow** with automatic tier detection.

**Semantic work is owned by Librarian.** Scripts handle mechanics, Librarian handles crystallization.

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

### Step 2: Execute Mechanical Close

Based on the tier, run the appropriate script:

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

### Step 3: Invoke Librarian for Semantic Close

**Switch to Librarian:**
```
set_active_persona("1bb66f53-9e2a-4152-9b18-75c2ee2c25a3")
```

**Librarian responsibilities by tier:**

**All Tiers:**
- Audit SESSION_STATE: `python3 N5/scripts/session_state_manager.py audit --convo-id {CONVO_ID}`
- Sync any missing state
- Generate proper title (not pattern-based)
- Write 2-3 sentence summary of what was discussed/accomplished
- Verify artifacts are in correct locations

**Tier 2+ Only:**
- Extract key decisions with rationale
- Identify open items
- Recommend file moves if needed

**Tier 3 Only:**
- Enhance AAR with conversation context
- **Capability Graduation:** If build is complete, run graduation workflow (see below)
- Extract lessons worth logging
- Verify build workspace is complete

### Capability Graduation (Tier 3 builds)

```bash
# Check if build qualifies
python3 N5/scripts/capability_graduation.py check --build-slug <slug>

# If eligible, generate scaffold
python3 N5/scripts/capability_graduation.py graduate --build-slug <slug> --convo-id {CONVO_ID}
```

Then:
1. Read the generated scaffold
2. Complete all `[LLM: ...]` sections with real content from PLAN.md and conversation
3. Remove the "Build Context" section
4. Embed in semantic memory:
   ```bash
   python3 N5/scripts/capability_graduation.py embed --capability-path <path> --update-index
   ```

### Step 4: Final Checks

**Git Check:**
If git changes detected, note them and ask about committing.

**Return to Operator:**
```
set_active_persona("90a7486f-46f9-41c9-a98c-21931fa5c5f6")
```

## Output

Present the formatted close output per the tier template.

End with:
```
✅ Conversation closed (Tier N)
```

## Full Documentation

`file 'N5/prefs/operations/conversation-end-v3.md'`

## Version History

- **v2.0** (2025-12-26): Librarian now owns semantic close work
- **v1.0** (2025-10-15): Initial tiered system



---
description: |
  Formal conversation end-step - resolve all conversation effects.
  Reviews files, proposes organization, executes cleanup, generates AAR, archives build tracker.
tags:
  - session
  - cleanup
  - organization
  - aar
  - conversation
---
# Close Conversation

Runs the formal **conversation-end workflow** - like Magic: The Gathering's end step, where all conversation effects are resolved.

## Flags

- `--require-confirm`: If set, the recipe runs interactively requiring user confirmations.
  Otherwise, it runs in semi-interactive mode where prompts are minimized and only critical confirmations are requested.

## What This Does

**6-Phase Workflow:**

1. **Phase -1:** Lesson Extraction - Captures reusable patterns
2. **Phase 0:** AAR Generation - Creates after-action report with thread export
3. **Phase 0.5:** Artifact Symlinking - Links deliverables to AAR folder
4. **Phase 1-2:** File Organization - Reviews and moves conversation files
5. **Phase 2.5:** Placeholder Detection - Enforces P16 (Accuracy) & P21 (Document Assumptions)
6. **Phase 3:** Personal Intelligence Update - Updates your behavioral patterns
7. **Phase 3.5:** Build Tracker Archival - Archives completed tasks from BUILD_MAP
8. **Phase 4:** Git Status Check - Prompts to commit uncommitted changes
9. **Phase 4.5:** System Timeline Check - Auto-detects timeline-worthy changes
10. **Phase 5:** Thread Title Generation - Creates descriptive thread title
11. **Phase 6:** Archive & Cleanup - Cleans workspace, archives if significant

## When to Use

**Invoke when:**
- Wrapping up a conversation
- Marking work as complete
- Want formal AAR and cleanup
- Ready to archive conversation artifacts

**Commands:**
- `/close-conversation`
- "End conversation"
- "Wrap up"
- "conversation-end"

## What You Get

✅ Complete AAR with thread export  
✅ Files organized to permanent locations  
✅ Build tracker tasks archived  
✅ Git changes committed (if confirmed)  
✅ System timeline updated  
✅ Thread title generated  
✅ Clean workspace ready for next conversation

## Full Documentation

`file N5/prefs/operations/conversation-end.md`

## Execution

**CRITICAL: Before presenting final results to the user, you MUST:**
1. Load `file 'N5/prefs/operations/conversation-end-output-template.md'`
2. **YOU do the actual analysis** - Read conversation files, understand what was built/discussed
3. **Scripts only provide structure** - Use their file lists, but YOU write descriptions/summaries
4. **No placeholder/stub data** - All content must be real, specific to THIS conversation
5. Follow template structure EXACTLY - no improvisation, no reordering
6. Use specified emojis and formatting precisely

**Scripts give you mechanics (file paths, git status), YOU provide semantics (understanding, meaning, context).**

This recipe uses the **conversation-end orchestrator** - a 3-phase pipeline that analyzes, proposes, and executes cleanup operations.

### Quick Run (Recommended)

```bash
# Auto-detect conversation ID and run full pipeline
CONVO_ID=$(basename "$(pwd)")
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py --convo-id "$CONVO_ID" --output /tmp/analysis.json
python3 /home/workspace/N5/scripts/conversation_end_proposal.py --analysis /tmp/analysis.json --format markdown
```

Review the proposal, then execute:

```bash
# Dry-run first (preview changes)
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal /tmp/analysis.json --dry-run

# Execute for real
python3 /home/workspace/N5/scripts/conversation_end_executor.py --proposal /tmp/analysis.json
```

### Manual Phase-by-Phase

**Phase 1: Analyze**
```bash
python3 /home/workspace/N5/scripts/conversation_end_analyzer.py \
  --workspace /home/.z/workspaces/con_XXXXX \
  --convo-id con_XXXXX \
  --output /tmp/conv_analysis.json
```

**Phase 2: Generate Proposal**
```bash
python3 /home/workspace/N5/scripts/conversation_end_proposal.py \
  --analysis /tmp/conv_analysis.json \
  --format markdown \
  --output /tmp/conv_proposal.md
```

**Phase 3: Execute**
```bash
# Dry-run (preview)
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --proposal /tmp/conv_analysis.json \
  --dry-run

# Real execution
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --proposal /tmp/conv_analysis.json
```

### Rollback

If something goes wrong:
```bash
python3 /home/workspace/N5/scripts/conversation_end_executor.py \
  --rollback /tmp/transaction_TIMESTAMP.json
```

---

**Related:**
- `recipe 'Meetings/Export Thread.md'` - AAR only (Phase 0 standalone)
- `recipe 'Meetings/Analyze Meeting.md'` - Meeting-specific processing
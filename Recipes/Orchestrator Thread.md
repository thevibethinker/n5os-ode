---
description: |
  Create and maintain a dedicated orchestrator thread to coordinate multi-conversation upgrades
  (conversation-end consistency, title generation, session-state enrichment, supervisor workflows).
tags:
  - system
  - orchestration
  - planning
---
# Orchestrator Thread (Conversation-End Consistency Initiative)

## Purpose
A single control thread to coordinate changes across multiple conversations:
- Conversation-type detection + metadata tagging
- SESSION_STATE early enrichment (Phase -0.5)
- Title generation improvements per type
- Supervisor workflow for related threads (merge/summarize)
- Diagnostics + runbooks for cleanup and renaming

## How to Use
- Start a new build conversation titled: "Orchestrator: Conversation-End Consistency"
- Pin this recipe to the top of that conversation
- All sub-work is referenced back to this thread

## Initial Tasks
1. Update `n5_conversation_end.py` with convo-type detection using `N5/config/conversation_types.json`
2. Ensure Phase -0.5 updates SESSION_STATE with `conversation_type`, `focus`, `objective`, and `artifacts`
3. Improve title generator to use type-specific templates from config
4. ✅ **IMPLEMENTED:** Supervisor script `N5/scripts/convo_supervisor.py`
   - Groups related conversations by type/focus/time window
   - Generates batch summaries
   - Proposes unified titles
   - Offers batch rename/archive actions (dry-run first)
5. Add diagnostics recipe: `Recipes/System/Conversation Diagnostics.md`

## Supervisor Usage

```bash
# List related conversations by type
python3 N5/scripts/convo_supervisor.py list-related --type build --window-days 7

# List worker conversations under a parent
python3 N5/scripts/convo_supervisor.py list-related --parent con_XXX

# Generate unified summary for specific conversations
python3 N5/scripts/convo_supervisor.py summarize --ids con_XXX,con_YYY,con_ZZZ --include-artifacts

# Propose batch title improvements (dry-run by default)
python3 N5/scripts/convo_supervisor.py propose-rename --type build --window-days 7

# Execute rename proposals
python3 N5/scripts/convo_supervisor.py execute-rename --type build --execute

# Propose archive moves for old completed conversations
python3 N5/scripts/convo_supervisor.py propose-archive --status complete --older-than-days 30

# Save results to file
python3 N5/scripts/convo_supervisor.py list-related --type discussion --output /tmp/related.json
```

## Artifacts
- `file 'N5/config/conversation_types.json'`
- `file 'N5/scripts/n5_conversation_end.py'`
- ✅ `file 'Recipes/System/Conversation Diagnostics.md'` (created 2025-10-27)
- ✅ `file 'N5/scripts/convo_supervisor.py'` (implemented 2025-10-27)
- ✅ `file 'Documents/System/ORCHESTRATOR_QUICK_REFERENCE.md'` (created 2025-10-27)

## Success Criteria
- Titles are consistent across worker/deployment/zoats/system conversations
- SESSION_STATE always enriched before title phase
- Supervisor can generate a unified summary for related threads
- Dry-run paths exist for all destructive operations

## Next Steps
- Implement supervisor + diagnostics
- Backfill titles for last 30 days (dry-run preview + confirm)

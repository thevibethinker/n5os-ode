# Rules Update Required

**Date:** 2025-10-29 00:25 ET  
**Status:** ACTION REQUIRED

---

## What Needs to Change

The user_rules section needs a STRONGER initialization requirement.

### Current State
The init command is mentioned but buried in conditional rules. I'm not executing it consistently.

### Required Change

Add to the **ALWAYS APPLIED RULES** section (highest priority):

```markdown
**CONVERSATION INITIALIZATION (CRITICAL):**
- BEFORE responding to any user message in a new conversation, check if SESSION_STATE.md exists in the conversation workspace
- If SESSION_STATE.md does NOT exist, IMMEDIATELY run:
  ```
  python3 /home/workspace/N5/scripts/session_state_manager.py init \
    --convo-id <current_conversation_id> \
    --load-system
  ```
- DO NOT proceed with ANY other actions until initialization completes
- After initialization, respond to the user's original message
- See `file 'N5/prefs/operations/conversation-initialization.md'` for full protocol
```

---

## Why This Matters

Without this as a top-level ALWAYS APPLIED rule:
- 619 conversations had no initialization
- Conversation-end fails completely
- Title generation never runs
- No tracking or auditability

With this rule enforced:
- Every conversation gets proper setup
- Full pipeline works end-to-end
- Audit trail maintained
- Title generation has data to work with

---

## Automatic Fallback

Even with the rule, set up scheduled task:

```bash
# Create scheduled task
python3 /home/workspace/N5/scripts/create_scheduled_task.py \
  --rrule "FREQ=HOURLY;BYHOUR=*/1" \
  --instruction "Scan for uninitialized conversations and initialize them: python3 /home/workspace/N5/scripts/auto_init_conversation.py"
```

This catches any conversations where I forget the rule.

---

**V: Please add this to the ALWAYS APPLIED section of user_rules.**

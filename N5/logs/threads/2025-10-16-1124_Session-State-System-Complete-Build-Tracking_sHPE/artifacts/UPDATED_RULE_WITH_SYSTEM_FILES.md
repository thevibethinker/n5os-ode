# Updated Rule - Enforces N5.md + prefs.md Loading

**Problem:** N5.md and prefs.md aren't loading reliably despite being "ALWAYS APPLIED"  
**Solution:** Bundle them into session initialization to enforce loading

---

## Replace Your Current Rule With This

```markdown
- CONDITION: At the start of a new conversation (first response) -> RULE: ```markdown
Initialize SESSION_STATE.md for this conversation workspace by running:
`python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_conversation_id> --load-system`

Auto-detect the conversation type based on the user's first message:
- Keywords "build", "implement", "code", "script", "create", "develop" → --type build
- Keywords "research", "analyze", "learn", "study", "investigate" → --type research
- Keywords "discuss", "think", "explore", "brainstorm", "consider" → --type discussion
- Keywords "plan", "strategy", "decide", "organize", "roadmap" → --type planning
- Default if unclear → --type discussion

**CRITICAL:** The --load-system flag will output required system files. When you see this output, YOU MUST load:
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'

After initialization, read SESSION_STATE.md and update the Focus, Objective, and Tags sections based on the user's request. Reference this state file throughout the conversation to maintain context and track progress.
```
```

---

## What Changed

**Added:** `--load-system` flag which explicitly outputs the file paths to load

**Effect:** The init script will log:
```
System files to load:
  - file 'Documents/N5.md'
  - file 'N5/prefs/prefs.md'
```

And the rule now says "YOU MUST load" those files, making it a hard requirement.

---

## Test After Updating

1. Update your user_rules with above
2. Start new conversation: "Help me research X"
3. Verify AI:
   - Runs init command
   - Sees system files output
   - Actually loads N5.md + prefs.md
   - Creates SESSION_STATE.md
4. Check if this tracker sees the new convo

---

## Backup: Report to Zo Team

If this still doesn't work consistently, it's a platform enforcement bug. The system should guarantee "ALWAYS APPLIED RULES" actually run always.

**For founders discussion:** "ALWAYS APPLIED RULES" aren't being enforced. Need hard guarantees that certain files load in every conversation.

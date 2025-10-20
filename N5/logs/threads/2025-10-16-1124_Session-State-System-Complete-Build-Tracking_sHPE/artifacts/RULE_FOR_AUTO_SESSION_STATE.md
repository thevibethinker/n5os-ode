# Hard-Coded Rule for Auto SESSION_STATE.md Initialization

**Purpose:** Auto-initialize SESSION_STATE.md at the start of every conversation

---

## Proposed Rule Addition

Add to your `user_rules` → `CONDITIONAL RULES` section:

```
- CONDITION: On any new conversation start (no SESSION_STATE.md exists yet) -> RULE: ```markdown
Auto-initialize SESSION_STATE.md in the conversation workspace by running:
`python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_convo_id> --type <auto_detected_type>`

Auto-detect type based on first user message:
- Contains "build", "implement", "code", "script" → type=build
- Contains "research", "analyze", "learn" → type=research  
- Contains "discuss", "think", "explore" → type=discussion
- Contains "plan", "strategy", "decide" → type=planning
- Default → type=discussion

After initialization, read the SESSION_STATE.md and use it to guide conversation structure.
```
```

---

## Alternative: Lighter Weight Rule

If the above is too prescriptive, use this simpler version:

```
- CONDITION: At the start of any conversation -> RULE: Consider whether this conversation would benefit from SESSION_STATE.md tracking. If so, initialize it with `python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_convo_id>`.
```

---

## Manual Invocation

Users can also manually invoke:
```bash
python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id con_XXX --type build --mode implementation
```

---

## Benefits of Hard-Coded Rule

1. **Zero-friction adoption** - Happens automatically
2. **Consistent tracking** - Every conversation gets state management
3. **Tracker always works** - All conversations have SESSION_STATE.md to read
4. **Quality improvement** - Forces explicit objectives and success criteria
5. **Knowledge capture** - Insights/decisions logged by default

---

## Testing

After adding the rule, start a new conversation and verify:
1. SESSION_STATE.md gets created automatically
2. Type is detected correctly
3. Tracker picks it up in BUILD_MAP

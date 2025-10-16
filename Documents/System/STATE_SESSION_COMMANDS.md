# State-Session Commands Quick Reference

**Purpose:** Slash commands for SESSION_STATE.md management  
**Created:** 2025-10-16  

---

## Three Commands

### `/init-state-session`
**Initialize SESSION_STATE.md for conversation**

```bash
# Auto-detect type from context
/init-state-session

# Explicit type
/init-state-session --type build
/init-state-session --type research  
/init-state-session --type discussion
/init-state-session --type planning

# With mode
/init-state-session --type build --mode refactor
```

**Auto-classification keywords:**
- **build**: implement, code, script, create, develop, build
- **research**: research, analyze, learn, study, investigate
- **discussion**: discuss, think, explore, brainstorm, consider
- **planning**: plan, strategy, decide, organize, roadmap

---

### `/update-state-session`
**Update fields in SESSION_STATE.md**

```bash
# Common updates
/update-state-session --field status --value active
/update-state-session --field phase --value implementation
/update-state-session --field focus --value "System refactor"
/update-state-session --field objective --value "Complete feature X"
/update-state-session --field progress --value "65%"
```

**Common fields:**
- `status`: active | paused | complete | blocked
- `phase`: design | implementation | testing | deployment | complete
- `focus`: What this conversation is about
- `objective`: What we're trying to accomplish
- `progress`: Percentage (e.g., "42%")
- `mode`: Specific mode within type

---

### `/check-state-session`
**Read current SESSION_STATE.md**

```bash
# Current conversation
/check-state-session

# Specific conversation
/check-state-session --convo-id con_XXX
```

**Shows:**
- Metadata (ID, timestamps, status)
- Type, mode, focus, objective
- Success criteria checklist
- Progress tracking
- Key insights and decisions
- Open questions
- Outputs created
- Build-specific: phase, files, tests, rollback plan

---

## Typical Workflow

```bash
# 1. Start conversation - initialize state
/init-state-session --type build

# 2. During work - update progress
/update-state-session --field phase --value implementation
/update-state-session --field progress --value "35%"

# 3. Check progress anytime
/check-state-session

# 4. Mark complete
/update-state-session --field status --value complete
/update-state-session --field progress --value "100%"
```

---

## Integration

**Commands registered in:** file 'N5/config/commands.jsonl'

**Command files:**
- file 'N5/commands/init-state-session.md'
- file 'N5/commands/update-state-session.md'
- file 'N5/commands/check-state-session.md'

**Backend script:** file 'N5/scripts/session_state_manager.py'

**Full docs:** file 'Documents/System/SESSION_STATE_SYSTEM.md'

---

## Auto-Initialization

Per file 'N5/prefs/prefs.md', SESSION_STATE.md should auto-initialize at conversation start.

**Verify rule is active:**
```markdown
CONDITION: At the start of a new conversation (first response) -> RULE:
Initialize SESSION_STATE.md for this conversation workspace by running:
python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_conversation_id> --load-system
```

---

## Benefits

✅ **Slash command access** - Type `/init-state-session` instead of remembering CLI  
✅ **Discoverable** - Shows up in command palette with `/`  
✅ **Documented** - Each command has usage examples  
✅ **Consistent** - Same interface as other N5 commands  
✅ **Integrated** - Works with build-tracker and orchestrator systems  

---

## Related Systems

- **Build Tracker**: Monitors build conversations via SESSION_STATE.md
- **Orchestrator**: Coordinates multi-conversation builds
- **Message Queue**: Inter-conversation communication
- **Principle Detector**: Quality gates for builds

---

*v1.0 | 2025-10-16 14:59 ET*

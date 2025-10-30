# Debug Logging System

**Purpose:** Track problem→hypothesis→outcome cycles during build/debug sessions to detect circular patterns and improve situational awareness.

**Version:** 1.0 | **Created:** 2025-10-29

---

## Overview

Automatic logging system that captures debugging attempts in JSONL format, detects circular patterns, and alerts when stuck in loops.

**Key Features:**
- Append-only JSONL log per conversation
- Auto-detects circular debugging (3+ similar problems)
- Tracks problem/hypothesis/outcome/actions/notes
- Pattern matching via text similarity + keyword overlap
- Auto-review after 3rd consecutive failure

---

## File Location

**Per-conversation log:**
```
/home/.z/workspaces/con_<conversation_id>/DEBUG_LOG.jsonl
```

**Created automatically** for `build` and `debug` conversation types during session initialization.

---

## Log Entry Format

```json
{
  "timestamp": "2025-10-29T04:03:20Z",
  "entry_id": "abc123de",
  "component": "api_client.py",
  "problem": "Rate limit 429 on API calls",
  "hypothesis": "Need exponential backoff",
  "actions": ["Added backoff decorator", "Set intervals 5s, 15s, 45s"],
  "outcome": "success|failure|partial",
  "notes": "Worked after implementing proper retry logic"
}
```

**Fields:**
- `timestamp`: ISO 8601 UTC
- `entry_id`: Short hash (first 8 chars of sha256)
- `component`: File/module/system being debugged
- `problem`: What's broken
- `hypothesis`: What we think will fix it
- `actions`: List of actions taken
- `outcome`: success | failure | partial
- `notes`: Additional context, learnings

---

## Usage

### Logging Attempts (Operator)

```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <conversation_id> \
  --component "component_name" \
  --problem "Description of problem" \
  --hypothesis "What should fix it" \
  --actions "Action 1" "Action 2" \
  --outcome success|failure|partial \
  --notes "Additional context"
```

### Checking Recent Attempts

```bash
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id <conversation_id> \
  --n 5 \
  --format display
```

### Pattern Detection

```bash
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id <conversation_id> \
  --window 10 \
  --threshold 3
```

### User Issue Reports

When V reports an issue:
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id <conversation_id> \
  --component "user_report" \
  --problem "V's description of issue" \
  --hypothesis "User observation" \
  --actions "User reported issue" \
  --outcome reported \
  --notes "Context from conversation"
```

---

## Pattern Detection Logic

**Similarity threshold:** 70% text similarity OR 60% keyword overlap

**Alert threshold:** 3 similar problems within last 10 entries

**When pattern detected:**
- Prints warning: "⚠️ CIRCULAR DEBUGGING DETECTED"
- Shows component + problem + attempt count
- Suggests: Different approach, Debugger mode, ask V

**Pattern clusters:**
```json
{
  "problem": "Import error on module load",
  "component": "test_module.py",
  "count": 3,
  "entry_ids": ["abc123", "def456", "ghi789"]
}
```

---

## Integration Points

### Session State Manager

`session_state_manager.py init` auto-creates `DEBUG_LOG.jsonl` for build/debug types:

```python
if convo_type in ["build", "debug"]:
    debug_log_path = self.workspace / "DEBUG_LOG.jsonl"
    if not debug_log_path.exists():
        debug_log_path.touch()
        logger.info(f"✓ Initialized DEBUG_LOG.jsonl")
```

### Operator Persona Reflexes

**Auto-review trigger:**
- After 3rd consecutive failure
- When V reports issue
- Before escalating to V

**Auto-check patterns:**
- After logging failure
- Before trying same approach again
- When feeling stuck

**Escalation with context:**
- Include recent attempts summary
- Show pattern clusters
- Provide debug log for V review

---

## Example Workflow

**Scenario:** Fixing import error

1. **First attempt:**
   ```bash
   debug_logger.py append --problem "Import error" \
     --hypothesis "Missing dependency" \
     --actions "Ran pip install" --outcome failure
   ```

2. **Second attempt:**
   ```bash
   debug_logger.py append --problem "Import error persists" \
     --hypothesis "Path issue" \
     --actions "Added to sys.path" --outcome failure
   ```

3. **Pattern check:**
   ```bash
   debug_logger.py patterns
   # ⚠️ CIRCULAR DEBUGGING DETECTED
   # Similar problems: 2, Component: module.py
   ```

4. **Third attempt (different approach):**
   ```bash
   debug_logger.py append --problem "Module import failing" \
     --hypothesis "Try absolute imports" \
     --actions "Changed to absolute" --outcome success
   ```

---

## Recipe Integration

**file 'Recipes/Debug Log.md'** - Full usage guide for debug logging

**file 'Recipes/Report Issue.md'** - Simple interface for V to report problems

---

## Design Principles Applied

- **P2 (SSOT):** Single log file per conversation, append-only
- **P19 (Error Handling):** All operations logged with outcome
- **P28 (Fast Feedback):** <5s append latency, immediate pattern detection
- **P11 (Failure Modes):** Handles missing logs, corrupt entries gracefully
- **P7 (Dry-Run):** Test mode available with `con_TEST` conversation ID

---

## Maintenance

**Log rotation:** Not needed - conversation-scoped, ephemeral with conversation

**Pattern tuning:** Adjust thresholds in `debug_logger.py`:
- `SIMILARITY_THRESHOLD = 0.7` (70% text similarity)
- `KEYWORD_THRESHOLD = 0.6` (60% keyword overlap)
- `DEFAULT_WINDOW = 10` (last 10 entries)
- `DEFAULT_THRESHOLD = 3` (3 similar problems)

**Testing:**
```bash
# Run test sequence
python3 debug_logger.py append --convo-id con_TEST ...
python3 debug_logger.py patterns --convo-id con_TEST
rm /home/.z/workspaces/con_TEST/DEBUG_LOG.jsonl
```

---

## Future Enhancements

**Potential additions:**
- Auto-summarize failed attempts for Debugger mode handoff
- Export patterns to squawk_log.jsonl (system-wide issues)
- Cross-conversation pattern detection (common failure modes)
- Integration with Builder/Debugger mode activation logic
- ML-based similarity (beyond text + keyword matching)

---

**Status:** ✅ Implemented, tested, integrated with session_state_manager

*v1.0 | 2025-10-29 | Operator Mode Enhancement*

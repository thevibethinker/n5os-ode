---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
grade: knowledge
domain: systems
stability: time_bound
form: spec
---

# Debug Logging System

**Version:** 1.0  
**Created:** 2025-10-29  
**Purpose:** Track problem→hypothesis→outcome cycles to detect circular debugging

---

## Overview

The debug logging system provides structured tracking of debugging attempts in build/debug conversations. It enables:

1. **Pattern Detection**: Automatically identifies when you're going in circles
2. **Situational Awareness**: Review recent attempts before trying new approaches
3. **Learning**: Capture what worked and what didn't
4. **Escalation Logic**: Trigger mode changes or V consultation when stuck

---

## Architecture

### Storage
- **Location**: `/home/.z/workspaces/con_<id>/DEBUG_LOG.jsonl`
- **Format**: JSONL (JSON Lines) for append-only, machine-parseable logs
- **Scope**: Per-conversation (isolated, auto-cleanup with conversation)

### Entry Schema

```json
{
  "ts": "2025-10-29T04:03:20Z",
  "entry_id": "abc123de",
  "component": "file/module/system being debugged",
  "problem": "What's wrong",
  "hypothesis": "What we think will fix it",
  "actions": ["What we did", "Step 2"],
  "outcome": "success|failure|partial",
  "notes": "Learnings or additional context",
  "conv_id": "con_XXX"
}
```

### Pattern Detection Algorithm

**Similarity Scoring:**
1. **Text Similarity**: SequenceMatcher ratio on problem descriptions (>0.7 = match)
2. **Keyword Overlap**: Shared meaningful words (≥4 chars) / union (>0.6 = match)
3. **Component Match**: Must be same component

**Threshold:**
- 3+ similar problems (by default)
- Within last 10 entries (configurable window)
- Only counts failures (successes excluded)

**Alert:**
When threshold reached, returns warning suggesting:
- Different approach
- Activate Debugger mode with planning prompt
- Ask V for guidance

---

## Usage

### Script Interface

**Append Entry:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py append \
  --convo-id con_XXX \
  --component "api.py" \
  --problem "Rate limit 429" \
  --hypothesis "Add exponential backoff" \
  --actions "Added retry decorator" "Set intervals 5s, 15s, 45s" \
  --outcome success \
  --notes "Worked after implementing backoff"
```

**View Recent:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py recent \
  --convo-id con_XXX \
  --n 5 \
  --format display|json
```

**Check Patterns:**
```bash
python3 /home/workspace/N5/scripts/debug_logger.py patterns \
  --convo-id con_XXX \
  --window 10 \
  --threshold 3
```

### Python API

```python
from debug_logger import DebugLogger

logger = DebugLogger(convo_id="con_XXX")

# Append
logger.append(
    component="api.py",
    problem="Rate limit errors",
    hypothesis="Need backoff",
    actions=["Added retry logic"],
    outcome="success",
    notes="5s, 15s, 45s intervals worked"
)

# Recent
entries = logger.recent(n=5)

# Patterns
result = logger.detect_patterns(window=10, threshold=3)
if result["circular_detected"]:
    print(result["warning"])
```

---

## Integration Points

### 1. Session State Manager

- Auto-create `DEBUG_LOG.jsonl` for build/debug type conversations
- Initialize in `session_state_manager.py init` when type=build|debug

### 2. Vibe Operator Persona

**Reflexes to add:**

1. **After 3rd consecutive failure** (same component):
   ```
   → Auto-run: debug_logger.py patterns
   → If circular: Display warning + suggest mode shift
   ```

2. **Before trying 4th approach**:
   ```
   → Auto-review: debug_logger.py recent --n 5
   → Analyze: "What have we tried? What patterns emerge?"
   → Consider: Debugger mode, different angle, or V escalation
   ```

3. **On success after ≥3 failures**:
   ```
   → Log success with detailed notes
   → Extract learnings for future reference
   ```

### 3. Debugger Mode Activation

When circular pattern detected:
```markdown
**Activating Debugger Mode**
**Objective:** Break circular debugging pattern
**Scope:** [component from log]
**Success:** Root cause identified, verified fix
**Context:** file '/home/.z/workspaces/con_XXX/DEBUG_LOG.jsonl' shows [N] similar failures
**Planning:** Yes (need fresh perspective, systematic verification)
```

---

## Design Principles Applied

### P2 (SSOT)
- Single log file per conversation
- All debug attempts recorded in one place

### P7 (Dry-Run)
- Read operations have no side effects
- Append-only, never modifies existing entries

### P15 (Complete Before Claiming)
- Outcome field required (success|failure|partial)
- Must log what actually happened, not just attempt

### P19 (Error Handling)
- All operations wrapped in try/except
- Graceful degradation (pattern detection fails → returns empty)
- Logs errors without crashing

### P28 (Fast Feedback)
- <5s latency for all operations
- Immediate visibility of recent attempts
- Real-time pattern detection

### Planning Prompt: Flow Over Pools
- Append-only flow (information moves forward)
- Pattern detection prevents stagnation
- Escalation ensures flow doesn't stop

### Planning Prompt: Simple Over Easy
- JSONL = simple format, easy to parse
- Single concern: track attempts
- No complex state management

---

## Workflow Example

**Scenario:** Debugging API rate limit issue

```bash
# Attempt 1: Increase timeout
python3 debug_logger.py append --convo-id con_ABC \
  --component "api_client.py" \
  --problem "Rate limit 429 on bulk requests" \
  --hypothesis "Timeout too short, server needs more time" \
  --actions "Increased timeout 5s → 30s" \
  --outcome failure \
  --notes "Still getting 429, timeout not the issue"

# Attempt 2: Add delay between requests
python3 debug_logger.py append --convo-id con_ABC \
  --component "api_client.py" \
  --problem "Rate limit 429 continuing" \
  --hypothesis "Requests too fast, need delay" \
  --actions "Added time.sleep(1) between calls" \
  --outcome failure \
  --notes "Still 429, need smarter approach"

# Attempt 3: Exponential backoff
python3 debug_logger.py append --convo-id con_ABC \
  --component "api_client.py" \
  --problem "Rate limit 429 persisting" \
  --hypothesis "Need exponential backoff on retry" \
  --actions "Implemented backoff decorator" "5s, 15s, 45s intervals" \
  --outcome success \
  --notes "This worked! Backoff + retry handled rate limit gracefully"

# Check what we learned
python3 debug_logger.py recent --convo-id con_ABC --n 3 --format display
```

**Pattern Check After Attempt 2:**
```bash
python3 debug_logger.py patterns --convo-id con_ABC --threshold 2

# Output:
# ⚠️ CIRCULAR DEBUGGING DETECTED
# Component: api_client.py
# Problem: Rate limit 429...
# Attempts: 2 similar failures
# → Consider: Different approach, load Debugger mode, or ask V for guidance
```

---

## Future Enhancements

**V1.1 (Potential):**
- [ ] Semantic similarity using embeddings (better than keyword matching)
- [ ] Auto-extract learnings from successful attempts
- [ ] Link to SESSION_STATE.md timeline
- [ ] Export to squawk_log.jsonl for systemic issues
- [ ] Integration with N5 knowledge base (pattern library)

**V1.2 (Potential):**
- [ ] Cross-conversation pattern detection (same problem across sessions)
- [ ] Suggest relevant past solutions from history
- [ ] AI-generated hypothesis based on past successes

---

## Testing

**Test Coverage:**
- ✅ Append entry (success/failure/partial)
- ✅ Read recent entries
- ✅ Pattern detection (similar problems)
- ✅ Format display (human-readable)
- ✅ Edge cases (no log, empty log, single entry)

**Test Results:** All pass (2025-10-29)

---

## Recipe

Load: `file 'Recipes/Debug Log.md'` for quick reference commands

---

**Principles:** P2, P7, P15, P19, P28  
**Design Values:** Simple Over Easy, Flow Over Pools  
**Status:** Production ready v1.0

*Created: 2025-10-29T04:03 ET*

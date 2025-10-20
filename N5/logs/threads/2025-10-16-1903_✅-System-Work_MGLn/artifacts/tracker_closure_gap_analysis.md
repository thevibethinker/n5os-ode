# Build Tracker + Conversation-End Integration Gap Analysis

**Date:** 2025-10-16 15:00 ET  
**Status:** Gap Identified - Integration Missing

---

## Question

Is the conversation-end command set up to remove completed items from the build tracker, allowing the tracker to hold more than 5 items without getting full?

---

## Answer: NO - Integration Does Not Exist

### Current State

**Build Tracker (`build_tracker.py`):**
- ✅ Tracks tasks with states: open, active, complete, paused, abandoned
- ✅ Logs all task events to JSONL session file
- ✅ Displays completed tasks separately in BUILD_MAP.md
- ❌ **Never removes or archives completed tasks**
- ❌ **No cleanup mechanism**

**Conversation-End (`conversation-end.md`):**
- ✅ Phase 1: File inventory and classification
- ✅ Phase 2: Move/delete temporary files
- ✅ Phase 2.5: Placeholder detection
- ✅ Phase 3: Personal intelligence update
- ✅ Phase 4: Git status check
- ✅ Phase 4.5: System timeline check
- ✅ Phase 5: Thread title generation
- ✅ Phase 6: Optional archive
- ❌ **No integration with build tracker**
- ❌ **No task cleanup or archiving**

**Closure Tracker (`closure_tracker.py`):**
- ✅ Records conversation closures with metadata
- ✅ Updates manifest with event ranges
- ✅ Updates SESSION_STATE.md with closure info
- ❌ **No integration with build tracker**
- ❌ **Doesn't know about tasks or BUILD_MAP**

---

## The Gap

### What's Missing

When `conversation-end` is run on a build conversation:

1. **No task archiving:** Completed tasks remain in the session log forever
2. **No BUILD_MAP cleanup:** Completed section grows indefinitely
3. **No cross-conversation cleanup:** BUILD_MAP shows all conversations, but completed conversations never get archived
4. **No tracker reset:** Active task count never decreases, even when work is done

### Current Behavior

```
conversation-end runs → files organized → git committed → thread titled
                     ↓
           BUILD_MAP untouched
                     ↓
         Completed tasks accumulate
                     ↓
    Tracker becomes cluttered over time
```

### Desired Behavior

```
conversation-end runs → build work detected → archive completed tasks
                     ↓
          Move to closure manifest
                     ↓
      Clean active tasks from BUILD_MAP
                     ↓
         Tracker stays focused
```

---

## Impact

**Current problem:**
- Tracker will show all tasks ever tracked in this conversation
- BUILD_MAP's "Completed" section grows without bound
- No way to "graduate" work from active tracking to archive
- Forces manual cleanup or tracker becomes unusable

**V's stated goal:**
> "The tracker won't get full (so can be longer than 5) as long as it drops an item from the list once end-command has been fully run"

This goal is **not currently implemented**.

---

## Solution Design

### Option 1: Archive Completed Tasks on Conversation-End (Recommended)

**Add Phase 3.5 to conversation-end:**

```markdown
### Phase 3.5: Build Tracker Archival

**Purpose:** Archive completed tasks from active build tracking

**Workflow:**
1. Check if BUILD_MAP.md exists in conversation workspace
2. If exists, load completed tasks from session log
3. Append completed tasks to closure manifest or separate archive
4. Remove completed tasks from active BUILD_MAP
5. Keep session log intact for historical record
6. Update BUILD_MAP to show only open/active tasks

**Output:**
- Completed tasks moved to N5/logs/build-sessions/archive/
- BUILD_MAP shows only active work
- Session log preserved for audit trail
```

**Implementation points:**
- Run after git check (Phase 4), before thread title (Phase 5)
- Create archive file: `N5/logs/build-sessions/archive/{convo_id}_completed.jsonl`
- Update BUILD_MAP to filter out completed tasks when rendering
- Log archival event to session log

### Option 2: Filter Completed Tasks from Display

**Simpler approach:**
- Don't remove completed tasks from session log
- Update `_update_build_map()` to skip completed tasks after conversation-end
- Add marker to session log: `{"event": "session_closed", "timestamp": "..."}`
- Filter logic: if session_closed event exists, don't show completed tasks

**Pros:**
- Non-destructive (all data preserved)
- Simpler to implement
- Reversible

**Cons:**
- Session log still grows indefinitely
- Doesn't actually archive work

### Option 3: Hybrid Approach (Best)

**Combine both:**
1. Mark session as closed in session log
2. Generate archive file with completed tasks + metadata
3. Update BUILD_MAP rendering to:
   - Show completed tasks for active sessions
   - Hide completed tasks for closed sessions
4. Preserve full session log for historical queries

**Archive format:**
```jsonl
{"type": "session_archive", "convo_id": "con_XXX", "closed_at": "2025-10-16T19:00:00Z"}
{"type": "task_completed", "task": "Feature Implementation", "completed_at": "2025-10-16T18:30:00Z"}
{"type": "task_completed", "task": "Testing", "completed_at": "2025-10-16T18:45:00Z"}
```

---

## Recommendation

**Implement Option 3 (Hybrid Approach)**

**Rationale:**
- Preserves full history for debugging/audit
- Keeps BUILD_MAP focused on active work
- Non-destructive (can always regenerate from session log)
- Aligns with N5 principles (SSOT, portable, auditable)

**Work required:**
1. Add `session_closed` event to session log on conversation-end
2. Create archive generator in build_tracker.py
3. Update `_update_build_map()` to filter closed sessions
4. Add Phase 3.5 to conversation-end.md
5. Test with existing build conversation

**Effort estimate:** ~2 hours
- 30 min: Add session_closed event logic
- 45 min: Archive generation
- 30 min: BUILD_MAP filtering
- 15 min: Testing and verification

---

## Files to Modify

1. `file N5/scripts/build_tracker.py` 
   - Add `close_session()` method
   - Add `generate_archive()` method
   - Update `_update_build_map()` filtering
   - Add `is_session_closed()` helper

2. `file N5/commands/conversation-end.md` 
   - Add Phase 3.5: Build Tracker Archival
   - Document integration
   - Add to workflow checklist

3. `file N5/scripts/n5_conversation_end.py` 
   - Import build_tracker
   - Call close_session() if BUILD_MAP exists
   - Log archival event

---

## Testing Plan

**Test case 1: Build conversation with completed tasks**
1. Create build conversation with 3 tasks
2. Mark all as complete
3. Run conversation-end
4. Verify: BUILD_MAP shows no tasks, archive file created

**Test case 2: Mixed state tasks**
1. Create conversation with 2 active, 2 completed tasks
2. Run conversation-end
3. Verify: BUILD_MAP shows only 2 active, archive has 2 completed

**Test case 3: Non-build conversation**
1. Create discussion conversation
2. Run conversation-end
3. Verify: No build tracker operations attempted

---

## Next Steps

**Immediate:**
1. Confirm this analysis with V
2. Get approval on Option 3 approach
3. Create implementation task

**Implementation order:**
1. Build tracker session closure
2. Archive generation
3. BUILD_MAP filtering
4. Conversation-end integration
5. Testing

**Follow-up:**
- Monitor BUILD_MAP size over time
- Verify cleanup is effective
- Consider periodic archive consolidation

---

## Related Files

- `file N5/scripts/build_tracker.py` - Task tracking
- `file N5/scripts/closure_tracker.py` - Conversation closure
- `file N5/commands/conversation-end.md` - End workflow
- `file N5/logs/build-sessions/` - Session logs directory
- `file N5/prefs/operations/thread-closure-triggers.md` - Closure triggers

---

## Principles Applied

- **P2 (SSOT):** Archive is derived from session log
- **P7 (Dry-Run):** Can preview archive before generation
- **P15 (Complete Before Claiming):** Must implement fully, not just mark
- **P18 (Verify State):** Check BUILD_MAP after cleanup
- **P20 (Modular):** Each tracker handles own cleanup

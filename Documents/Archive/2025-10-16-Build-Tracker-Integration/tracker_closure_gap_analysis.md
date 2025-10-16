# Build Tracker + Conversation-End Integration Gap Analysis

**Date:** 2025-10-16 15:00 ET  
**Status:** Gap Identified - Integration Missing

---

## Question

Is the conversation-end command set up to remove completed items from the build tracker, allowing the tracker to hold more than 5 items without getting full?

---

## Answer: NO - Integration Does Not Exist

### Current State

**Build Tracker:**
- Tracks tasks with states (open, active, complete, paused, abandoned)
- Logs all events to session JSONL file (`N5/logs/build-sessions/`)
- Displays all tasks in BUILD_MAP.md (including completed)
- **Never removes or archives completed tasks**

**Conversation-End Command:**
- Has 6 phases (AAR, file organization, placeholder scan, intelligence update, git check, timeline)
- Archives conversation artifacts
- Closes thread and organizes files
- **Does not interact with build tracker at all**

**Gap:** Completed tasks accumulate in BUILD_MAP, creating clutter over time.

---

## Problem Statement

When build tracker shows many tasks (>5), it becomes hard to see what's active. Completed tasks should be archived/hidden after conversation-end runs, but currently there's no integration between these systems.

### Current Behavior

```
BUILD_MAP.md (after many conversations):
- Task 1 [complete]
- Task 2 [complete]
- Task 3 [active]
- Task 4 [complete]
- Task 5 [complete]
- Task 6 [open]
- Task 7 [complete]
... (gets cluttered)
```

### Desired Behavior

```
BUILD_MAP.md (after conversation-end):
- Task 3 [active]
- Task 6 [open]

Archive: N5/logs/build-sessions/archive/con_XXX_completed.jsonl
- Task 1, 2, 4, 5, 7 archived with timestamps
```

---

## Solution Options

### Option 1: Delete Completed Tasks

**Approach:**
- Add cleanup method to build_tracker.py
- Remove completed tasks from session log during conversation-end
- Simplest implementation

**Pros:**
- Clean BUILD_MAP immediately
- Simple logic

**Cons:**
- **Violates P2 (SSOT)** - loses audit trail
- **Violates P5 (Anti-Overwrite)** - destructive operation
- Can't recover if mistake
- No historical record

**Verdict:** ❌ Not recommended

### Option 2: Filter Completed Tasks from Display

**Approach:**
- Don't remove completed tasks from session log
- Update `_update_build_map()` to skip completed tasks when displaying
- Keep full history in session log

**Pros:**
- Non-destructive
- Full audit trail preserved
- Can regenerate BUILD_MAP anytime

**Cons:**
- Completed tasks still in session log (grows over time)
- No explicit "archived" record
- Filtering happens every refresh

**Verdict:** ⚠️ Better, but incomplete

### Option 3: Hybrid Approach (Archive + Filter) ✅

**Approach:**
1. **Mark session as closed** when conversation-end runs
2. **Generate archive file** with completed tasks (separate JSONL)
3. **Filter display** to hide completed tasks after closure
4. **Preserve session log** intact for full audit trail

**Implementation:**
- Add `close_session()` to build_tracker.py
  - Logs `session_closed` event with summary
  - Returns count of completed vs active tasks
- Add `generate_archive()` to build_tracker.py
  - Creates `N5/logs/build-sessions/archive/{convo_id}_completed.jsonl`
  - Contains only completed tasks with timestamps
- Update `_load_tasks()` to check for `session_closed` event
  - If found, filter out completed tasks from display
- Add Phase 3.5 to conversation-end.md
  - Calls build_tracker.py close + archive
  - Reports summary
  - Updates BUILD_MAP

**Pros:**
- ✅ Non-destructive (preserves full session log)
- ✅ Explicit archive for completed work
- ✅ Clean BUILD_MAP after closure
- ✅ Can regenerate from session log if needed
- ✅ Complies with P2 (SSOT) and P5 (Anti-Overwrite)
- ✅ Clear "before/after" behavior

**Cons:**
- Slightly more complex
- Two sources of truth (session log + archive)
  - *Mitigation: Archive is derived, not authoritative*

**Verdict:** ✅ **Recommended** - Best balance of cleanliness and safety

---

## Implementation Plan (Option 3)

### Changes to build_tracker.py

```python
def close_session(self, dry_run=False) -> Dict:
    """Mark session as closed and return summary."""
    if self.is_session_closed():
        return {"error": "Session already closed"}
    
    tasks = self._load_tasks()
    summary = {
        "total": len(tasks),
        "complete": len([t for t in tasks if t["state"] == "complete"]),
        "active": len([t for t in tasks if t["state"] == "active"]),
        "open": len([t for t in tasks if t["state"] == "open"])
    }
    
    if not dry_run:
        self._log_event("session_closed", {"summary": summary, "tasks": tasks})
    
    return summary

def generate_archive(self, dry_run=False) -> Optional[Path]:
    """Generate archive of completed tasks."""
    tasks = self._load_tasks()
    completed = [t for t in tasks if t["state"] == "complete"]
    
    if not completed:
        return None
    
    archive_file = self.archive_dir / f"{self.convo_id}_completed.jsonl"
    
    if not dry_run:
        with open(archive_file, "w") as f:
            # Write header
            f.write(json.dumps({
                "type": "session_archive",
                "convo_id": self.convo_id,
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "task_count": len(completed)
            }) + "\n")
            
            # Write completed tasks
            for task in completed:
                f.write(json.dumps({
                    "type": "task_completed",
                    **task
                }) + "\n")
    
    return archive_file

def is_session_closed(self) -> bool:
    """Check if session has been marked closed."""
    if not self.session_file.exists():
        return False
    
    with open(self.session_file) as f:
        for line in f:
            event = json.loads(line.strip())
            if event["event"] == "session_closed":
                return True
    return False

# Update _load_tasks() to filter completed if closed
def _load_tasks(self) -> List[Dict]:
    # ... existing loading logic ...
    
    # Filter completed tasks if session is closed
    if self.is_session_closed():
        tasks = {k: v for k, v in tasks.items() if v["state"] != "complete"}
    
    return list(tasks.values())
```

### Changes to n5_conversation_end.py

Add after Phase 3 (Personal Intelligence Update):

```python
def archive_build_tasks():
    """Phase 3.5: Archive completed build tracker tasks."""
    print("\n" + "="*70)
    print("PHASE 3.5: BUILD TRACKER ARCHIVAL")
    print("="*70)
    
    # Check if BUILD_MAP exists
    build_map = CONVERSATION_WS / "BUILD_MAP.md"
    if not build_map.exists():
        print("⏭️  No BUILD_MAP found, skipping")
        return
    
    try:
        from build_tracker import BuildTracker
        tracker = BuildTracker()
        
        # Check if already closed
        if tracker.is_session_closed():
            print("✓ Build session already closed (delta conversation)")
            return
        
        # Close session
        summary = tracker.close_session()
        
        # Generate archive if completed tasks exist
        archive_file = tracker.generate_archive()
        
        # Report
        print(f"\n✓ Build session closed successfully")
        print(f"  Total tasks: {summary['total']}")
        print(f"  Completed (archived): {summary['complete']}")
        print(f"  Active/Open: {summary['active'] + summary['open']}")
        if archive_file:
            print(f"  Archive: {archive_file.name}")
        
        # Refresh BUILD_MAP
        tracker.refresh()
        print(f"\n✓ BUILD_MAP updated to hide completed tasks")
        
    except Exception as e:
        print(f"⚠️  Build archival failed: {e}")
        print("Continuing with conversation-end...")
```

### Changes to conversation-end.md

Add Phase 3.5 documentation between Phase 3 and 4.

---

## Testing Plan

1. **Create test build session:**
   ```bash
   python3 build_tracker.py activate
   python3 build_tracker.py track "Test Task 1"
   python3 build_tracker.py status "Test Task 1" --state complete
   python3 build_tracker.py track "Test Task 2"
   ```

2. **Verify before closure:**
   - BUILD_MAP shows both tasks
   - Session log has both tasks

3. **Run conversation-end (dry-run):**
   ```bash
   python3 n5_conversation_end.py --dry-run
   ```

4. **Run conversation-end (real):**
   ```bash
   python3 n5_conversation_end.py
   ```

5. **Verify after closure:**
   - BUILD_MAP shows only Task 2 (active)
   - Archive file exists with Task 1
   - Session log intact with both tasks
   - Can regenerate BUILD_MAP from session log

---

## Related Files

- `file 'N5/scripts/build_tracker.py'` - Build tracker implementation
- `file 'N5/scripts/n5_conversation_end.py'` - Conversation end script
- `file 'N5/commands/conversation-end.md'` - End command docs
- `file 'N5/prefs/operations/thread-closure-triggers.md'` - Closure triggers

---

## Principles Applied

- **P2 (SSOT):** Archive is derived from session log
- **P7 (Dry-Run):** Can preview archive before generation
- **P15 (Complete Before Claiming):** Must implement fully, not just mark
- **P18 (Verify State):** Check BUILD_MAP after cleanup
- **P20 (Modular):** Each tracker handles own cleanup

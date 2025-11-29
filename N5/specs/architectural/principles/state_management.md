# Principle 23: State Management Philosophy

**Category**: Design  
**Priority**: High  
**Related**: P18 (State Verification), ZT1 (Context + State Framework)

---

## Statement

Every system component must maintain and expose its current state. State should be queryable, auditable, and recoverable at any point in time.

---

## Rationale

From Zero-Touch Principle 1: Knowledge work requires both Context (right information) and State (current condition of all information). Without state visibility:
- You can't resume interrupted work efficiently
- You can't debug failures
- You can't trust the system
- Cognitive load increases ("Where was I? What's pending?")

State management is infrastructure, not overhead.

---

## Implementation Patterns

### Pattern 1: State Files

Every workflow maintains state in standard format:

```jsonl
{"stage": "intake", "item_count": 3, "last_update": "2025-10-24T18:00:00Z", "items_awaiting": ["voice_2024.m4a", "article_123.md", "email_456.txt"]}
{"stage": "processing", "item_count": 5, "last_update": "2025-10-24T12:00:00Z", "oldest_item_age_hours": 76, "pool_warning": true}
{"stage": "knowledge", "item_count": 247, "last_ingest": "2025-10-22T09:00:00Z"}
```

**Location**: `N5/state/*.state.jsonl` or embedded in workflow dirs

### Pattern 2: State Query Command

```bash
$ n5 state-check

N5 System State - 2025-10-24 18:45 EDT
========================================

Records/Intake: 3 items awaiting triage (2 auto-processed, 1 needs manual)
Records/Processing/Company: 5 items (3 days average age)
  ⚠️  POOL WARNING: 2 items > 7 days old
Records/Processing/Personal: 2 items (1 day average age)
Lists: 12 active, 3 stale (>30d no update)
Knowledge: 247 items, last ingest 2 days ago
Git: 4 uncommitted changes, last push 6 hours ago

System Health: 2 warnings, 0 errors
```

### Pattern 3: Recoverable State

State includes enough information to:
- Resume from interruption
- Rollback failed operations
- Audit what happened
- Replay transformations

```python
# Save state before transformation
state = {
    "operation": "article_ingest",
    "input_file": "/path/to/article.md",
    "stage": "pre_summarize",
    "timestamp": datetime.now().isoformat()
}
save_state("article_ingest.state.jsonl", state)

try:
    result = ai_summarize(article)
    state["stage"] = "summarized"
    state["output"] = result
    save_state("article_ingest.state.jsonl", state)
except Exception as e:
    state["stage"] = "failed"
    state["error"] = str(e)
    save_state("article_ingest.state.jsonl", state)
    raise
```

---

## Key Insights

1. **State is not status**: Status is "completed/failed". State is "3 items in intake, 2 auto, 1 manual, oldest 6hr".

2. **Queryable beats logged**: Logs are linear history. State is current snapshot. Both are valuable.

3. **Expose, don't hide**: No "black box" processes. Every component should answer "What are you doing right now?"

4. **State enables trust**: When you can see system state, you trust it. When you can't, you constantly check manually.

---

## Anti-Patterns

❌ **Silent processing**: Workflows that run without exposing current stage  
❌ **Point-in-time only**: State that's only visible at completion  
❌ **Manual state tracking**: Keeping "Where was I?" in your head  
❌ **State in proprietary formats**: State files that require special tools to read

---

## Testing

```bash
# State should be checkable without running workflows
$ n5 state-check
# Should show current state even if workflows are idle

# State should update during operations
$ n5 article-ingest test.md &
$ sleep 2
$ n5 state-check
# Should show "article_ingest" in progress

# State should persist across restarts
$ n5 state-check > before.txt
$ [restart system]
$ n5 state-check > after.txt
$ diff before.txt after.txt
# Should show minimal diff (timestamps ok, state preserved)
```

---

## Examples

### Example 1: Intake State

```bash
$ cat Records/Intake/.state.jsonl
{"timestamp": "2025-10-24T18:30:00Z", "items": 3, "auto_processed": 2, "needs_review": 1}
```

Query shows:
- How many items waiting
- How many were auto-handled
- What needs human attention

### Example 2: Processing State with Pool Warning

```bash
$ cat Records/Processing/Company/.state.jsonl
{"timestamp": "2025-10-24T18:30:00Z", "items": 5, "avg_age_hours": 76, "pool_warning": true, "flagged": ["meeting_2025-10-17.md", "email_thread_old.md"]}
```

Automatic detection that items are pooling beyond expected residence time (>72hr = 3 days).

### Example 3: Cross-System State

```bash
$ n5 state-check --full

System-Wide State:
- Records flow: 3 → 5 → (output)
- Lists active: 12
- Git sync: OK (last push 6hr ago)
- Knowledge items: 247
- AI processes: 1 running (article summarization)
- Last full health check: 18 hours ago [OVERDUE]
```

---

## Success Criteria

State management is working when:
- [ ] Any team member can run `state-check` and understand current system status
- [ ] Interrupted work can resume without "Where was I?" confusion
- [ ] Failed operations can be debugged from state logs
- [ ] Pool warnings trigger before manual discovery
- [ ] State queries take <5 seconds
- [ ] State is human-readable (can inspect .state.jsonl files directly)

---

## Related Principles

- **P18 (State Verification)**: Verify writes succeeded - tactical implementation of state tracking
- **P11 (Failure Modes)**: State helps identify and recover from failures
- **P26 (Maintenance-First)**: State visibility enables maintenance workflows
- **ZT1 (Context + State)**: Philosophical foundation for this principle

---

*Added: 2025-10-24*  
*Source: Zero-Touch integration (ZT1)*
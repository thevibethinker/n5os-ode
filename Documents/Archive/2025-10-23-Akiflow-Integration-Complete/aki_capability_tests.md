# Aki Email Capability Tests
**Date:** 2025-10-22 23:21 ET

## Email 1: Query Capabilities (Thread: 19a11ab7a08e1fe2)
**Subject:** Test: Query capabilities

**Requests sent:**
1. Show me all uncompleted tasks
2. List tasks for tomorrow
3. Show tasks in the Operations project
4. List tasks tagged with 'warm_intro'
5. Show me all tasks for this week

**Testing:** Date filters, project filters, tag filters, status filters

---

## Email 2: Task Modification Commands (Thread: 19a11abb568b7aa0)
**Subject:** Test: Task completion commands

**Requests sent:**
1. Complete: Review Akiflow integration docs
2. Mark as complete: Draft intro Sarah Chen → Marcus Rodriguez
3. Done: Send intro Sarah Chen → Marcus Rodriguez
4. ✓ Follow-up: Sarah Chen ↔ Marcus Rodriguez
5. Completed the task "Review candidate pipeline for SWE role"
6. Can you delete the task "Test task - Review Akiflow integration docs"?
7. Move "Draft recap for Leadership Team Sync" to next Monday

**Testing:** 
- Completion commands (multiple formats)
- Deletion capability
- Rescheduling capability

---

## Expected Response Time
30-90 seconds per email

## Next Steps
1. Wait for both responses
2. Parse what Aki can/cannot do
3. Build parser for supported queries
4. Build auto-completion system based on confirmed commands

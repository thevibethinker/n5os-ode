# Worker Tracking Fix Plan
**Date:** 2025-10-27 03:00 ET
**Issue:** Workers not being registered in conversations.db

## Root Cause

1. `spawn_worker.py` creates WORKER_ASSIGNMENT files but doesn't register worker in database
2. `session_state_manager.py init` creates SESSION_STATE but doesn't call conversation_registry.create()
3. `link-parent` only updates markdown, not database parent_id

**Evidence:**
- 15+ worker assignment files found
- Only 1 worker in database (con_WORKER_TEST)
- 3 workers have "Parent Conversation" in SESSION_STATE
- But those 3 aren't in conversations.db

## Fix Strategy

### Option A: Fix session_state_manager.py (Recommended)
Integrate conversation_registry into `init` action:
- When --parent provided → set parent_id and mode=worker
- Always call conversation_registry.create() during init
- Update link-parent to also update database

**Pros:** Automatic, works for all future workflows  
**Cons:** Requires testing init action

### Option B: Add backfill script
Create script to scan /home/.z/workspaces and register missing conversations

**Pros:** Immediate fix for existing workers  
**Cons:** One-time, doesn't prevent future issues

### Option C: Both A + B
Fix the system + backfill existing

## Implementation Plan

1. Update session_state_manager.py:
   - Import conversation_registry
   - Add database registration to init()
   - Add --parent flag to init
   - Update link-parent to set database parent_id

2. Create backfill script:
   - Scan all conversation workspaces
   - Read SESSION_STATE.md files
   - Register missing conversations
   - Extract parent_id if specified

3. Test:
   - Init new conversation
   - Init with --parent
   - link-parent on existing
   - Verify database

4. Backfill:
   - Run on all existing conversations
   - Verify worker relationships

## Next Steps

Implement Option C (both fixes)

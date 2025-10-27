# Orchestrator System Audit & Cleanup Plan
**Date:** 2025-10-26 22:45 ET  
**Conversation:** con_MJlKexUB6SsqoLcU

## THINK Phase

### What are we building?
1. Clean up deprecated meeting orchestrator files
2. Rename reflection_ingest_orchestrator.py for clarity
3. Build out convo_supervisor.py with conversations.db integration
4. Fix recipe references

### Trap Doors (Irreversible Decisions)
- **Deleting deprecated files**: Archived scripts exist in _DEPRECATED folders, safe to remove main deprecated file
- **Renaming script**: Need to check all imports and references first
- **Database schema for supervisor**: Need to align with existing conversations.db schema

### Alternatives Considered (Nemawashi)
**For naming:**
1. reflection_ingest_bridge.py (chosen - clear bridge pattern)
2. reflection_gmail_bridge.py (too specific, also handles Drive)
3. reflection_intake.py (less clear about bridge role)

**For supervisor:**
1. Build new standalone tool (rejected - duplicates registry)
2. Extend conversation_registry.py (rejected - separation of concerns)
3. New convo_supervisor.py using registry as lib (chosen - clean)

### Success Criteria
- [ ] Deprecated meeting orchestrator deleted
- [ ] Recipe reference fixed or archived
- [ ] reflection_ingest script renamed, no broken imports
- [ ] convo_supervisor implements:
  - List related threads by type/focus/time window
  - Generate unified summaries
  - Propose batch renames
  - Dry-run for all operations
  - Integration with conversations.db
- [ ] All tests pass
- [ ] Fresh thread validation

## PLAN Phase

### Task 1: Delete Deprecated Meeting Orchestrator
**Files:**
- /home/workspace/N5/scripts/meeting_intelligence_orchestrator.py
- /home/workspace/Recipes/Meetings/Meeting Intelligence Orchestrator.md

**Actions:**
1. Move script to _DEPRECATED folder (already deprecated in header)
2. Archive recipe or add deprecation banner pointing to new registry-based flow

### Task 2: Rename Reflection Ingest Script
**From:** reflection_ingest_orchestrator.py  
**To:** reflection_ingest_bridge.py

**Verify no imports:**
```bash
grep -r "import.*reflection_ingest_orchestrator\|from.*reflection_ingest_orchestrator" /home/workspace/N5/
```

**Update any recipe references**

### Task 3: Build Convo Supervisor
**Integration points:**
- ConversationRegistry class from conversation_registry.py
- conversations.db schema (already has type, focus, parent_id, related_ids)
- SESSION_STATE.md files in each conversation workspace

**Features:**
1. `list-related` - Group conversations by:
   - Type (build/research/discussion/planning)
   - Focus similarity (fuzzy match)
   - Time window (--window-days)
   - Parent/child relationships
2. `summarize` - Generate unified summary for group
3. `propose-rename` - Suggest batch title improvements
4. `propose-archive` - Suggest archive moves
5. All with --dry-run

**Database queries needed:**
- SELECT by type + time range
- SELECT by parent_id (worker threads)
- SELECT by tags/focus similarity
- UPDATE titles (dry-run mode)

### Task 4: Update Documentation
- Archive/deprecate meeting orchestrator recipe
- Update System/Orchestrator Thread recipe with implementation status
- Add convo_supervisor to commands registry

## Flow Design (Flow Over Pools)

```
Conversations → Supervisor Queries → Group by Criteria → Generate Summaries → Propose Actions → User Review → Execute (if approved)
```

Exit conditions:
- Lists must be reviewable within 30s
- Summaries generated immediately
- All proposals dry-run by default
- Execution requires explicit confirmation

## Failure Modes
1. Database locked → Retry with backoff
2. Missing SESSION_STATE → Skip, log warning
3. Malformed focus field → Use title fallback
4. No related threads found → Return empty, don't error

## Implementation Notes
- Python script (P22: default, good DB/JSON libraries)
- Async not needed (local SQLite queries fast)
- Human-readable output (P1)
- Dry-run by default (P7)
- Error handling on all DB ops (P19)
- State verification for writes (P18)

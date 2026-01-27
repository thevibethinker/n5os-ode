---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_fBRc3AEBzpuDaNH0
---

# Zo Task System MVP — Code Review Results

## Summary

**Status:** ✅ Issues found and fixed. Integration ready.

| Metric | Value |
|--------|-------|
| Files reviewed | 7 |
| Bugs found | 4 |
| Bugs fixed | 4 |
| Integration tests | All passing |

## Bugs Found & Fixed

### BUG-1: Wrong Task Status in Action Tagger (Critical)

**File:** `action_tagger.py`
**Impact:** Task search would return zero results because it filtered by `status='active'` but the tasks table uses `'pending'`, `'in_progress'`, `'blocked'`, etc.

**Fix:** Changed status filter from `'active'` to `'pending'` on lines 102 and 254.

```python
# Before
AND status IN ('active', 'in_progress', 'blocked')

# After  
AND status IN ('pending', 'in_progress', 'blocked')
```

### BUG-2: Inconsistent Priority Ordering

**Files:** `schema.sql`, `evening_accountability.py`
**Impact:** Tasks would appear in different orders between morning and evening reports, causing confusion.

**Fix:** Standardized priority order across all modules to V's preferred strategic-first ordering:
1. Strategic (most important)
2. External (commitments to others)
3. Urgent (time-sensitive)
4. Normal (default)

### BUG-3: JSON Serialization Missing in Close Hooks

**File:** `close_hooks.py`
**Impact:** Passing a dict to `update_task(plan_json=plan)` would fail or corrupt data since the function expects a JSON string.

**Fix:** Added `json.dumps()` when passing plan dict:
```python
plan_json=json.dumps(plan)
```

### BUG-4: Illogical View WHERE Clause

**File:** `schema.sql` (v_tasks_today view)
**Impact:** The condition `date(due_at) >= today OR date(due_at) <= tomorrow` is always true for any date, defeating the purpose of the filter.

**Fix:** Simplified to `date(due_at) <= tomorrow` which correctly captures:
- Overdue tasks
- Tasks due today
- Tasks due tomorrow

## Review Checklist Results

### Schema Integrity ✅
- [x] `tasks.db` schema matches `schema.sql` (after fixes)
- [x] All foreign keys present (domains → tasks, projects → tasks)
- [x] Indexes created for status, priority, due_at, source
- [x] Latency tracking fields correct (created_at, due_at, completed_at)
- [x] Priority buckets: strategic, external, urgent, normal

### Task Registry ✅
- [x] CRUD operations work correctly
- [x] Latency calculation works
- [x] Source linking works
- [x] Event logging works

### Action Tagger ✅ (after fix)
- [x] Inference patterns reasonable
- [x] Status filter now correct
- [x] Integration with action_conversations.db works

### Staging ✅
- [x] capture_staged_task works
- [x] generate_review_markdown produces clean output
- [x] promote/dismiss functions work

### Close Hooks ✅ (after fix)
- [x] assess_task_completion works
- [x] update_task_from_conversation works
- [x] plan_json now properly serialized

### Morning Briefing ✅
- [x] get_todays_tasks returns correct tasks
- [x] Priority ordering is strategic-first
- [x] Capacity calculation works
- [x] SMS format is clean

### Evening Accountability ✅ (after fix)
- [x] get_day_results works
- [x] calculate_score works
- [x] Priority ordering matches morning briefing
- [x] SMS format is clean

## Integration Test Results

All tests passing:
```
1. Task Registry...          ✅
2. Action Tagger...          ✅ (status fix verified)
3. Staging...                ✅
4. Morning Briefing...       ✅
5. Evening Accountability... ✅
6. Close Hooks...            ✅
```

## Known Limitations (Not Bugs)

1. **Calendar Integration:** `check_calendar_blocks()` returns placeholder data. OAuth setup required for Google Calendar.

2. **Timezone:** Uses SQLite's `'localtime'` modifier which depends on server timezone. Currently server is UTC, so date comparisons may be off by hours near midnight.

3. **SMS Length:** Messages can exceed SMS limits. May need truncation for heavy task days.

## Recommendations for Wiring Up Agents

1. **Morning Briefing Agent (7am ET):**
   - Run from `/home/workspace` with `sys.path` setup
   - Call `generate_briefing_text()` and send via SMS
   - Store briefing in day_plans table

2. **Evening Accountability Agent (9pm ET):**
   - Run `generate_accountability_text()` first
   - Then `generate_staged_review_text()` if staged items exist
   - Consider splitting into 2 messages if both are long

3. **Environment:**
   - Ensure `sys.path.insert(0, '/home/workspace')` before imports
   - Or run scripts with `cd /home/workspace && python3 -m N5.task_system.module_name`

## Files Modified

| File | Changes |
|------|---------|
| `action_tagger.py` | Fixed status filter from 'active' to 'pending' |
| `schema.sql` | Fixed v_tasks_today priority order and WHERE clause |
| `evening_accountability.py` | Fixed priority order to strategic-first |
| `close_hooks.py` | Added json.dumps for plan_json |
| `__init__.py` | Added sys.path setup |
| `tasks.db` | Recreated v_tasks_today view |

---
task: Zo Task System MVP - Code Review & Debug
type: debug
priority: high
build_slug: zo-task-system
orchestrator: con_OaZwIOzCydglh4r4
---

# Zo Task System MVP — Code Review & Debug

## Objective
Review all code produced by the zo-task-system build for correctness, integration issues, and bugs before wiring up the scheduled agents.

## Files to Review

All in `/home/workspace/N5/task_system/`:

| File | Purpose | Lines |
|------|---------|-------|
| `task_registry.py` | Core task CRUD, domains, projects, latency tracking | ~500 |
| `action_tagger.py` | Conversation classification (infer + confirm) | ~450 |
| `staging.py` | Pre-task staging from meetings | ~420 |
| `close_hooks.py` | Thread-close → task completion detection | ~400 |
| `morning_briefing.py` | 7am agent script | ~580 |
| `evening_accountability.py` | 9pm agent script | ~550 |
| `schema.sql` | Full schema reference | ~180 |

## Review Checklist

### 1. Schema Integrity
- [ ] `tasks.db` schema matches `schema.sql`
- [ ] All foreign keys and indexes present
- [ ] Latency tracking fields (created_at, due_at, completed_at) correct
- [ ] Priority buckets: strategic, external_commitment, urgent, normal
- [ ] Domain → Project → Task hierarchy enforced

### 2. Task Registry (`task_registry.py`)
- [ ] CRUD operations work (create, read, update, delete)
- [ ] Latency calculation correct: `completed_at - due_at`
- [ ] Source linking (conversation_id, meeting_id, email_id) works
- [ ] Priority bucket logic correct
- [ ] Test: Create a task, complete it, verify latency recorded

### 3. Action Tagger (`action_tagger.py`)
- [ ] Inference patterns reasonable (not too aggressive)
- [ ] Confirmation prompt clear and non-intrusive
- [ ] Integration with action_conversations.db correct
- [ ] Test: Simulate a conversation, verify tagging works

### 4. Staging (`staging.py`)
- [ ] Meeting → pre-task extraction logic correct
- [ ] Staged tasks properly formatted for morning review
- [ ] `generate_review_markdown()` produces clean output
- [ ] Test: Add staged tasks, generate review, verify format

### 5. Close Hooks (`close_hooks.py`)
- [ ] Integration point with thread-close skill clear
- [ ] Task completion detection logic correct
- [ ] Handles partial completions gracefully
- [ ] Test: Simulate thread close, verify tasks marked complete

### 6. Morning Briefing (`morning_briefing.py`)
- [ ] Pulls today's tasks correctly
- [ ] Pulls staged items for review
- [ ] Message format clear and actionable
- [ ] Arsenal tone present but not obnoxious
- [ ] Ready to be wrapped in scheduled agent

### 7. Evening Accountability (`evening_accountability.py`)
- [ ] Pulls incomplete tasks correctly
- [ ] Escalation logic present (gentle → firm → block warning)
- [ ] Commitment tracking (external commitments get extra weight)
- [ ] Tomorrow preview included
- [ ] Ready to be wrapped in scheduled agent

## Integration Tests

Run these to verify end-to-end:

```bash
cd /home/workspace/N5/task_system

# 1. Test task registry
python3 -c "
from task_registry import TaskRegistry
tr = TaskRegistry()
# Create domain
domain_id = tr.create_domain('Work', 'Professional tasks')
# Create project  
project_id = tr.create_project(domain_id, 'Careerspan', 'permanent')
# Create task
task_id = tr.create_task(project_id, 'Test task', priority='normal')
print(f'Created: domain={domain_id}, project={project_id}, task={task_id}')
# Complete task
tr.complete_task(task_id)
print('Task completed')
"

# 2. Test staging
python3 -c "
from staging import StagingManager
sm = StagingManager()
sm.add_staged_item('Follow up with Sarah', source_type='meeting', source_id='meeting_123')
print(sm.generate_review_markdown())
"

# 3. Test morning briefing output
python3 morning_briefing.py --dry-run

# 4. Test evening accountability output  
python3 evening_accountability.py --dry-run
```

## Known Concerns to Investigate

1. **Database paths** — Are all scripts using the same DB path? Or are there hardcoded paths that diverge?

2. **Import structure** — Can all modules import each other cleanly? Check for circular imports.

3. **Error handling** — What happens if DB is locked? If task doesn't exist?

4. **Timezone handling** — Are timestamps in ET or UTC? Consistent?

5. **Arsenal theming** — Is it present in the agent messages? Tone-check the output.

## Deliverable

After review, report back with:

```json
{
  "status": "pass" | "issues_found",
  "bugs": ["list of bugs found"],
  "fixes_applied": ["list of fixes made"],
  "integration_ready": true | false,
  "notes_for_orchestrator": "Summary for V"
}
```

Write this to: `/home/workspace/N5/builds/zo-task-system/deposits/CODE_REVIEW.json`

Also create a summary at: `/home/workspace/N5/builds/zo-task-system/artifacts/CODE-REVIEW-RESULTS.md`

## On Completion

Text V: "Code review complete. [X bugs found / All clear]. Ready to wire up agents."

Then report back to orchestrator: `con_OaZwIOzCydglh4r4`

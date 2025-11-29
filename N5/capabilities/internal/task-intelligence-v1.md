---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Task Intelligence & Scheduling v1

```yaml
capability_id: task-intelligence-v1
name: "Task Intelligence – Scheduling & Completion Detection"
category: internal
status: experimental
confidence: medium
last_verified: 2025-11-29
tags:
  - tasks
  - scheduling
  - productivity
  - maintenance
entry_points:
  - type: script
    id: "N5/services/task_intelligence/calendar_scheduler.py"
  - type: script
    id: "N5/services/task_intelligence/completion_detector.py"
owner: "V"
```

## What This Does

The Task Intelligence system provides **calendar‑aware scheduling** and **passive task completion detection**. It is designed to:

- Suggest good times for tasks based on priority and calendar availability.
- Monitor signals from Gmail, Calendar, and files to decide when tasks are complete.
- Maintain a JSONL task registry that other systems (e.g. Akiflow/Aki, productivity dashboards) can consume.

This capability is currently in an experimental state but defines the internal contracts for future automation.

## How to Use It

### Schedule a task (library usage)

The scheduler is structured as a Python module; typical usage inside Zo‑driven workflows:

```python
from N5.services.task_intelligence.calendar_scheduler import schedule_task

scheduled = schedule_task({
    "id": "task_123",
    "title": "Review proposal",
    "duration": "45m",
    "priority": "High",
    "project": "Operations"
})

print(scheduled["when"], scheduled["scheduling_reasoning"])
```

The current implementation:
- Uses simple heuristics (priority → preferred time window, 9–18 ET).
- Is designed to be upgraded to call `use_app_google_calendar` to respect actual busy/available blocks.

### Completion detection loop

From `/home/workspace`:

```bash
python3 N5/services/task_intelligence/completion_detector.py --interval 300
```

The detector:
- Reads pending tasks from `N5/data/task_registry.jsonl`.
- Checks for signals (currently pattern‑based stubs) such as email replies or sent messages that match the task title.
- Marks tasks as completed in the registry and logs a brief reason.

## Associated Files & Assets

### Registry & logs

- `file 'N5/data/task_registry.jsonl'` – Append‑only registry of tasks created by Zo.
- `file 'N5/logs/task_completions.log'` – Log of detection runs and completion events.

### Service code

- `file 'N5/services/task_intelligence/calendar_scheduler.py'` – Calendar‑aware slot suggester; designed to wrap Zo’s Google Calendar tools.
- `file 'N5/services/task_intelligence/completion_detector.py'` – Completion detection loop using Gmail / Calendar / file heuristics.

### Upstream/downstream integrations (planned)

- Gmail and Calendar via Zo’s `use_app_gmail` / `use_app_google_calendar` (currently stubbed).
- Akiflow/Aki integration via email notifications from completion detector.
- Productivity dashboard linkage by feeding completion events and task registry stats.

## Workflow

```mermaid
flowchart TD
  A[Zo creates task
  - follow-up
  - draft
  - review] --> B[task_registry.jsonl
  status=pending]

  B --> C[calendar_scheduler.py
  - suggest when
  - attach reasoning]

  B --> D[completion_detector.py (loop)
  - check Gmail/Calendar/files
  - infer completion]

  D --> E[Update registry
  status=completed
  completion_reason]

  E --> F[Downstream systems
  - Aki
  - productivity dashboards]
```

## Notes / Gotchas

- **Stubs, not full integrations (yet).** Both scheduler and detector are written with clear extension points for Zo app tools but currently log their intent instead of making real API calls.
- **Heuristic matching.** Completion detection uses simple keyword heuristics on task titles; this is intentionally conservative and should be tuned before relying on it for high‑stakes workflows.
- **Registry is append‑style but rewrites on update.** `completion_detector.py` rewrites `task_registry.jsonl` when marking tasks complete; take backups before major changes if you depend on historical rows.


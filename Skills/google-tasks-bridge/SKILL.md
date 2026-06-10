---
name: google-tasks-bridge
description: Sync Google Tasks into a centralized SQLite task intake ledger, promote routed items into the N5 task system, and conditionally queue `@N5` commands for slower execution. Use when working with the Zo Commands Google Tasks list, task intake architecture, or Google Tasks polling/ledgering.
compatibility: Created for Zo Computer
metadata:
  author: <YOUR_HANDLE>.zo.computer
  version: "1.0"
---

# Google Tasks Bridge

This skill turns Google Tasks into an intake rail for N5OS.

## Use It For

- Fast polling of the `Zo Commands` task list into `N5/data/taskintake.db`
- Recording raw Google task history before interpretation
- Routing active tasks into `N5/task_system/tasks.db` staged intake
- Queueing explicit `@run` tasks for slower downstream execution

## Canonical Surfaces

- Raw intake DB: `N5/data/taskintake.db`
- Dataset wrapper: `Databases/task-intakes/`
- Bridge CLI: `Skills/google-tasks-bridge/scripts/google_tasks_bridge.py`
- Execution output bucket: `N5/task_system/outputs/zo-tasks/`

## Commands

```bash
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py init-db
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py status
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py report
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py lists
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py ensure-list --list-title "Zo Commands"
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py create-task --list-title "Zo Commands" --title "Example"
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py sync --list-title "Zo Commands"
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py route --list-title "Zo Commands"
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py dispatch --list-title "Zo Commands" --limit 5
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py run-job --job-id 123
python3 Skills/google-tasks-bridge/scripts/google_tasks_bridge.py backfill-outputs
```

## Notes

- `Zo Commands` is the intake rail.
- Default behavior is ingest + classify + stage only.
- Only tasks ending in `@run` queue execution.
- `@N5` is temporarily accepted as a legacy alias.
- One execution run writes one output folder under `N5/task_system/outputs/zo-tasks/`.
- The raw intake ledger stays separate from the curated N5 task system on purpose.
- Auth prefers Zo secrets directly: `GOOGLE_TASKS_CLIENT_ID`, `GOOGLE_TASKS_CLIENT_SECRET`, and `GOOGLE_TASKS_REFRESH_TOKEN`.
- If those secrets are not present in the local runtime, the bridge falls back to `file '/home/.z/google-oauth/token.json'` when that token store contains Google Tasks scope plus client + refresh material.
- `dispatch` is the queue-draining step: it recovers stale jobs, queues eligible `@run` tasks, and executes queued jobs.
- `route --list-title "Zo Commands"` remains supported for compatibility with the recurring automation.

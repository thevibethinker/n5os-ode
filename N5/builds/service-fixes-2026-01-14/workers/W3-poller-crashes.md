---
created: 2026-01-14
last_edited: 2026-01-14
version: 1.0
provenance: con_u0LhWqxkPWYn44Fg
status: pending
---

# Worker 3: Poller/Monitor Crash Diagnosis

## Objective

Diagnose and fix crashed background pollers.

## Affected Services

1. **fireflies-poller** (svc_koPo2TYE540) — 520 error
   - Entrypoint: `python3 -m fireflies_webhook.poller --interval 120 --batch 5`
   - Workdir: `/home/workspace/N5/services`

2. **action-approvals-monitor** (svc_BNjB_ZJHGOY) — 520 error
   - Entrypoint: `python3 /home/workspace/N5/scripts/monitor_action_approvals.py --interval 120`
   
3. **task-completion-detector** (svc_IF7aNtRiL30) — 520 error
   - Entrypoint: `python3 /home/workspace/N5/services/task_intelligence/completion_detector.py --interval 300`

## Diagnosis Tasks

### 1. Check Logs
```bash
tail -100 /dev/shm/fireflies-poller.log
tail -100 /dev/shm/fireflies-poller_err.log
tail -100 /dev/shm/action-approvals-monitor.log
tail -100 /dev/shm/action-approvals-monitor_err.log
tail -100 /dev/shm/task-completion-detector.log
tail -100 /dev/shm/task-completion-detector_err.log
```

### 2. Determine if Services Are Still Needed

**fireflies-poller:**
- Question: Is webhook sufficient? Poller may be redundant.
- If webhook handles all transcripts, DELETE poller.

**action-approvals-monitor:**
- Question: Is N5 action approval system still in use?
- If not, DELETE.

**task-completion-detector:**
- Question: Is N5 task intelligence system active?
- If not, DELETE.

### 3. If Keeping, Fix and Restart

Likely issues:
- Missing dependencies
- Database connection errors
- API key expiration
- Import path issues (same as Worker 1)

## Decision Matrix

| Service | Keep? | Reason |
|---------|-------|--------|
| fireflies-poller | TBD | Webhook may be sufficient |
| action-approvals-monitor | TBD | Check if approval system used |
| task-completion-detector | TBD | Check if task system used |

## Files

- `/home/workspace/N5/services/fireflies_webhook/poller.py`
- `/home/workspace/N5/scripts/monitor_action_approvals.py`
- `/home/workspace/N5/services/task_intelligence/completion_detector.py`


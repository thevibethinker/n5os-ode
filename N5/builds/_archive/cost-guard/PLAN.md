# Cost/Runaway Guard Implementation Plan

**Goal:** Prevent runaway expense from misconfigured scheduled agents by implementing a detection and arrest mechanism.

**Worker:** WORKER_AYsu_20251213_024606_371605
**Parent:** con_jR0PGPInKSn1AYsu

## Components

1.  **Arrest Mechanism (The Brake)**
    *   **Artifact:** `N5/flags/ARREST_SYSTEM.json`
    *   **Behavior:** Presence of this file indicates the system is in "Arrested" state.
    *   **Content:** JSON containing `reason`, `timestamp`, `triggering_event`.
    *   **Integration:** `n5_schedule_wrapper.py` checks this file before execution. If present, it aborts.

2.  **Cost Sentinel (The Watcher)**
    *   **Artifact:** `N5/scripts/maintenance/cost_sentinel.py`
    *   **Input:** `N5/data/scheduled_tasks.db` (executions table)
    *   **Logic:**
        *   **Global Velocity:** Check total executions in last hour. (Threshold: > 60/hr - configurable)
        *   **Task Velocity:** Check single task executions in last hour. (Threshold: > 12/hr - configurable)
        *   **Failure Storm:** Check for high failure rate in last window. (Threshold: > 80% failure in last 10 runs)
    *   **Action:** If violation detected -> Write `ARREST_SYSTEM.json`.

## Checklist

### Phase 1: Arrest Mechanism
- [ ] Define `ARREST_SYSTEM.json` schema.
- [ ] Modify `N5/scripts/n5_schedule_wrapper.py` to check for flag.
- [ ] Add CLI override `--ignore-arrest` to wrapper.

### Phase 2: Cost Sentinel
- [ ] Create `N5/scripts/maintenance/cost_sentinel.py`.
- [ ] Implement database query for recent executions.
- [ ] Implement "Global Velocity" check.
- [ ] Implement "Task Velocity" check.
- [ ] Implement "Failure Storm" check.
- [ ] Implement arrest trigger (write JSON).

### Phase 3: Testing & Handover
- [ ] Test Sentinel with mock data (dry run).
- [ ] Test Wrapper with manual arrest flag.
- [ ] Update Worker Status.

## Configuration (Defaults)
*   **Global Max Runs/Hour:** 60 (~$X risk/hr)
*   **Single Task Max Runs/Hour:** 12 (once every 5m)
*   **Consecutive Failures:** 10

## Rollback Plan
*   Delete `N5/scripts/maintenance/cost_sentinel.py`.
*   Revert `N5/scripts/n5_schedule_wrapper.py` to previous version.
*   Delete `N5/flags/ARREST_SYSTEM.json`.


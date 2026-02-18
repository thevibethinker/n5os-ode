---
created: 2026-02-16
last_edited: 2026-02-16
version: 1
provenance: con_7IE2POtd4gjTDQxn
---
# Orchestrator Thread Launcher

## Purpose
Use this thread as the orchestration control plane for `relationship-intelligence-os`.

## Run Sequence
1. Contract gate:
```bash
python3 N5/scripts/build_contract_check.py relationship-intelligence-os
```
2. Launch Pulse:
```bash
python3 Skills/pulse/scripts/pulse.py start relationship-intelligence-os
```
3. Monitor status:
```bash
python3 Skills/pulse/scripts/pulse.py status relationship-intelligence-os
```
4. Finalize at completion:
```bash
python3 Skills/pulse/scripts/pulse.py finalize relationship-intelligence-os
```

## Orchestrator Responsibilities
1. Keep this thread focused on Pulse status, blockers, and wave progression.
2. Do not embed long implementation work here; delegate to thread launch docs below.
3. Record checkpoints after each wave.

## Delegate Threads
Open the following launcher docs in separate conversations:
- `launchers/SPAWN_BOOKING_METADATA_CALENDAR.md`
- `launchers/SPAWN_TASKSYSTEM_COUPLING.md`
- `launchers/SPAWN_ORG_PROFILE_BACKFILL.md`

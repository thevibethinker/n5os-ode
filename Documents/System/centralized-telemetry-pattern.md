# Centralized Telemetry Pattern

**Date:** 2025-10-28
**Architecture:** Orchestrator-Worker Coordination

## Pattern

Workers write telemetry DIRECTLY to orchestrator workspace.
Orchestrator monitors its own workspace (not worker workspaces).

## Benefits

1. Simple coordination - orchestrator checks one location
2. No polling multiple workspaces
3. Clear ownership - orchestrator workspace = results
4. Worker autonomy - complete task, report once, done

## File Locations

Orchestrator workspace: /home/.z/workspaces/con_ORCHESTRATOR/
- worker_1_telemetry.json
- worker_2_telemetry.json
- worker_N_telemetry.json

Worker workspace: /home/.z/workspaces/con_WORKER_N/
- SESSION_STATE.md (internal tracking)
- work files

## Worker Flow

1. Load assignment from orchestrator workspace
2. Execute work
3. Write telemetry to orchestrator workspace (path provided)
4. Done

## Orchestrator Flow

1. Create worker briefs with telemetry paths
2. Spawn workers
3. Monitor own workspace for telemetry files
4. Validate telemetry when received
5. Proceed based on validation

## Implementation

- conversation_orchestrator.py uses this pattern
- Telemetry path: orchestrator_workspace/worker_N_telemetry.json
- Format: phase_handoff.schema.json

## Status
Implemented in N5/scripts/conversation_orchestrator.py

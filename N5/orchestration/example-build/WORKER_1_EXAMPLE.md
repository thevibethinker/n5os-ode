# Worker 1: Example Task

**Orchestrator:** [SET AT RUNTIME]
**Task ID:** W1-EXAMPLE
**Dependencies:** None

## Mission
Demonstrate centralized telemetry - workers write to orchestrator workspace.

## Deliverables
1. /home/workspace/example_output.txt
2. Telemetry JSON (path provided at runtime)

## Instructions

1. Create test file:
   echo "Worker 1 output" > /home/workspace/example_output.txt

2. Write telemetry to orchestrator workspace
   Path format: /home/.z/workspaces/con_ORCH/worker_1_telemetry.json
   
   Include: phase_id, worker_id, timestamp, status, outputs, quality, tests

## Key Pattern
Workers report TO orchestrator workspace (not their own).
Orchestrator monitors for worker_N_telemetry.json files.

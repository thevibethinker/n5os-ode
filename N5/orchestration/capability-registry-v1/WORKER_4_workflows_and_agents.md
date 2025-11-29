---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 4 – Workflows, Agents, Orchestrators

## Objective

Capture high-level **workflows**, **scheduled tasks**, and **orchestrator builds** as capabilities so they are easy to discover and reason about.

## Scope

- N5 workflows (`file 'N5/workflows/**'`)
- Prompts that function as orchestrators (e.g., `Orchestrator Thread`, `System Design Workflow`, pre-build checklist)
- Scheduled tasks (agents) defined in `scheduled_tasks.db` / `config/scheduled_tasks.jsonl`
- Orchestration build folders under `N5/orchestration/**` (CRM v3, knowledge realignment, meeting pipeline v2, capability-registry itself)

## Tasks

1. **Workflow Discovery**
   - Enumerate workflows and orchestrator prompts from `N5/workflows` and `Prompts/`.
   - List active scheduled tasks from the N5 scheduled-task spec / DB.

2. **Capability Docs Creation**
   - Create capability files under `N5/capabilities/workflows/` for:
     - Major orchestrators (CRM v3, knowledge realignment, meeting pipeline v2, capability-registry-v1)
     - Critical workflows (e.g., Follow-Up Email Generator v3, Meeting Intelligence Generator pipeline)
     - Any cornerstone scheduled tasks.

3. **Index Wiring**
   - Update the **Workflows & Orchestrators** section of `N5/capabilities/index.md` with links and one-line summaries.

## Deliverables

- `N5/capabilities/workflows/*.md` covering orchestrators, workflows, and key scheduled tasks.
- Updated Workflows & Orchestrators section in `N5/capabilities/index.md`.

## Success Criteria

- You can answer "What big workflows exist and how do they run?" from a quick scan of the registry.
- Each documented workflow identifies its prompts, scripts, and any agents/services it depends on.



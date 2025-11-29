---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Capability Registry v1 – Orchestrator Monitor

Orchestrator for creating and maintaining the **N5 Capability Registry** under `N5/capabilities/`.

**Orchestrator conversation:** _TBD (set after first run)_

## Objective

- Establish a **single, authoritative registry** of capabilities for this N5OS instance
- Cover **internal systems**, **external integrations**, and **multi-step workflows/orchestrators**
- Wire the registry into the **Close Conversation** pipeline for build threads (forward-only)
- Backfill existing capabilities via distributed worker threads

## Workers

- [ ] **Worker 1 – Schema & Scaffolding**
  - Brief: `N5/orchestration/capability-registry-v1/WORKER_1_schema_and_scaffolding.md`
  - Deliverables:
    - Finalized capability schema (fields, categories, status values)
    - Updated `N5/capabilities/CAPABILITY_TEMPLATE.md` if needed
    - Recommendations for directory conventions and naming

- [ ] **Worker 2 – Integrations Inventory**
  - Brief: `N5/orchestration/capability-registry-v1/WORKER_2_integrations_inventory.md`
  - Focus: Fireflies webhook service, Zapier/webhook bridges, Fillout integration, Tally, Akiflow/Aki, ZoBridge
  - Deliverables:
    - One capability file per integration under `N5/capabilities/integrations/`
    - Cross-links to implementation docs (e.g., `N5/services/**`, `N5/Integrations/**`)

- [ ] **Worker 3 – Internal Systems & Pipelines**
  - Brief: `N5/orchestration/capability-registry-v1/WORKER_3_internal_systems.md`
  - Focus: Meeting pipeline, CRM v3, reflection pipeline, ZoBridge, productivity tracker, content library, etc.
  - Deliverables:
    - Capability files under `N5/capabilities/internal/`
    - Pointers to specs (`N5/specs/**`) and scripts (`N5/scripts/**`)

- [ ] **Worker 4 – Workflows, Agents, Orchestrators**
  - Brief: `N5/orchestration/capability-registry-v1/WORKER_4_workflows_and_agents.md`
  - Focus: N5 workflows (`N5/workflows/**`), scheduled tasks, orchestrator builds under `N5/orchestration/**`
  - Deliverables:
    - Capability files under `N5/capabilities/workflows/`
    - Mapping from prompts/recipes to underlying scripts & services

- [ ] **Worker 5 – Conversation-End Integration & QA**
  - Brief: `N5/orchestration/capability-registry-v1/WORKER_5_conversation_end_integration.md`
  - Focus: Wiring registry updates into `Close Conversation.prompt.md` / conversation-end pipeline for **build orchestrator threads**
  - Deliverables:
    - Updated docs/instructions for capability capture at conversation close
    - Checklist + tests to verify registry stays consistent over time

## Monitoring Checklist

- [ ] `N5/capabilities/index.md` lists major capability groups and links
- [ ] At least one capability documented per **major subsystem** (meetings, CRM, ZoBridge, reflection, productivity, external integrations)
- [ ] Each capability file includes: name, category, status, entry points, associated files, workflow
- [ ] Close Conversation protocol updated to **ask about major capabilities** and create/update registry entries when appropriate
- [ ] Backfill workers completed; gaps and TODOs explicitly documented

## Notes

- Registry files are **system docs**, not user notes – they live under `N5/` by design.
- Use `file '...'` references liberally so both V and N5 can jump directly into implementation.
- This orchestrator itself should eventually have its own capability entry under `N5/capabilities/workflows/`.



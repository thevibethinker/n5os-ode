---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 3 – Internal Systems & Pipelines

## Objective

Document major **internal systems** as capabilities so the registry reflects what this N5OS instance can do without external services.

## Priority Systems

- Meeting pipeline v2 (ingestion → intelligence → archive)
- CRM v3 (profiles DB, enrichment pipeline, CLI)
- Reflection pipeline & knowledge bridge
- Productivity tracker / dashboard
- Content library & block system
- ZoBridge bridge service
- Task intelligence / scheduled maintenance systems

## Tasks

1. **System Identification**
   - Use `N5/docs/system_guide_v2.md`, `N5/specs/architectural/ARCHITECTURAL_OVERVIEW.md`, and relevant logs/specs to list major internal systems.

2. **Capability Docs Creation**
   - For each system, create a capability file under `N5/capabilities/internal/`.
   - Capture:
     - Purpose & scope (what the system owns)
     - Entry points (prompts, scripts, scheduled tasks, services)
     - Key data stores (SQLite DBs, JSONL logs)
     - Core workflows (high-level steps or mermaid diagram)

3. **Index Wiring**
   - Update **Internal Systems** section of `N5/capabilities/index.md` with links and one-line summaries.

## Deliverables

- `N5/capabilities/internal/*.md` for each prioritized internal system.
- Updated Internal Systems section in `N5/capabilities/index.md`.

## Success Criteria

- It is possible to answer "What are the core systems inside N5 and how do I use them?" from the registry alone.
- Each documented system clearly points to its owning scripts, specs, and data stores.



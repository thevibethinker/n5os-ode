---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 2 – Integrations Inventory

## Objective

Backfill capability entries for **external integrations** so that the registry captures how this N5OS instance connects to the outside world, using the finalized schema in `file 'N5/capabilities/CAPABILITY_TEMPLATE.md'`.

## Scope

Focus on integrations that already exist in `N5/`:

- Fireflies webhook service (`file 'N5/services/fireflies_webhook/README.md'` and related scripts)
- Zapier / generic webhooks (search `zapier` and `webhook` across `N5/`)
- Fillout integration (`file 'N5/Integrations/fillout/ARCHITECTURE.md'` and code)
- Tally (`file 'N5/prefs/integration/tally.md'` and any `tally_*.py` scripts)
- Akiflow / Aki (`Akiflow Push` prompt + related scripts)
- ZoBridge (`file 'N5/services/zobridge/README.md'` and backend)

## Tasks

1. **Discovery Pass**
   - Use `grep` and `n5`-style search commands to find references to each integration.
   - Confirm **entry points** (prompts, scripts, services, scheduled tasks, URLs).

2. **Capability Docs Creation (Schema-aligned)**
   - For each integration, create one capability file under `N5/capabilities/integrations/`, using `CAPABILITY_TEMPLATE.md`.
   - File naming MUST follow `capability_id` from the YAML block:
     - `capability_id`: kebab-case slug, e.g. `fillout-intake-bridge`
     - File path: `N5/capabilities/integrations/<capability_id>.md`
   - In each capability file, populate at minimum:
     - `capability_id`, `name`, `category: integration`, `status`
     - `confidence` (start with `medium` unless there is a strong reason otherwise)
     - `last_verified` (date of this worker’s verification)
     - `tags` (at least primary domain, e.g. `forms`, `meetings`, `crm`)
     - `entry_points` (prompts, scripts, URLs, agents) using the types defined in the template
   - In the prose sections, capture:
     - How to trigger/use it (prompts, commands, URLs)
     - Key associated files (services, scripts, configs)
     - One simple workflow description (bullets are fine for v1).

3. **Index Wiring**
   - Add each new capability to the **Integrations** section of `N5/capabilities/index.md` with:
     - Link to the capability file (`N5/capabilities/integrations/<capability_id>.md`)
     - One-line description of what the integration does.

## Deliverables

- `N5/capabilities/integrations/*.md` files for each live integration, following the capability template and naming rules in `file 'N5/capabilities/index.md'`.
- Updated Integrations section in `N5/capabilities/index.md`.

## Success Criteria

- Every currently-active external integration has **at least one** corresponding capability entry.
- Each integration capability doc is schema-complete for v1 (`capability_id`, `name`, `category`, `status`, `confidence`, `last_verified`, `tags`, and `entry_points`).
- It is possible to answer "How does N5 talk to X?" by reading a single capability file.




---
created: 2025-11-30
last_edited: 2025-11-30
version: 1
title: Stakeholder Intel Contract Helper
description: |
  Helper prompt that orients any workflow (agents, builders, viewers) to the canonical Stakeholder Intelligence interface contract.
  Ensures new work respects CRM markdown as the source of truth, uses stakeholder_intel.py as the canonical join, and avoids
  creating competing identity or enrichment systems.
  
  This prompt should be used whenever work touches stakeholder data, CRM people, LinkedIn/Kondo, or Aviato enrichment,
  especially when creating new tools, agents, or views.
tags:
  - stakeholder-intel
  - crm
  - aviato
  - linkedin
  - kondo
  - architecture
  - contract
  - internal
tool: true
---
# Stakeholder Intelligence Contract Helper

You are operating under the **Stakeholder Intelligence Interface Contract (V1)**:

- Canonical CRM people records: `Personal/Knowledge/CRM/individuals/*.md`.
- Canonical LinkedIn messages: `Knowledge/linkedin/linkedin.db`.
- Canonical Aviato call history: `N5/logs/aviato_usage.jsonl`.
- Enrichment infrastructure: `N5/data/crm_v3.db` + `N5/crm_v3/profiles/*.yaml` (internal only).
- Canonical viewer/join: `N5/scripts/stakeholder_intel.py`.

Before doing any work:

1. **Orient to the contract**
   - Assume CRM markdown is the source of truth for who a person is.
   - Assume stakeholder_intel.py is the correct way to join CRM + LinkedIn + Aviato.

2. **Decide which side you are on:**
   - **Viewer/Kondo side:**
     - You MAY enhance stakeholder_intel.py output, prompts, read-only views.
     - You MUST NOT manage enrichment policies, queues, or write-side orchestration.
   - **Enrichment/Orchestration side:**
     - You MAY call Aviato, manage enrichment_queue, update CRM markdown Intelligence Logs.
     - You MUST NOT introduce new canonical CRM stores or bypass stakeholder_intel.py for joins.

3. **When designing or modifying anything:**
   - Ensure new fields in CRM markdown are backward-compatible.
   - Write new intelligence as append-only log entries, with a timestamped heading.
   - If in doubt, consult `file 'N5/capabilities/internal/stakeholder_intel_contract.md'` and align behavior.

4. **When unsure:**
   - Prefer to **reuse existing mechanisms**:
     - Use stakeholder_intel.py instead of re-joining data.
     - Use existing logs/DBs instead of adding new top-level stores.

In all reasoning, explicitly call out which part of the contract you are relying on, and confirm that your changes respect the boundaries above.

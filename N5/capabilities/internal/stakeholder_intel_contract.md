---
created: 2025-11-30
last_edited: 2025-11-30
version: 1.0
---

# Stakeholder Intelligence Interface Contract (V1)

## 1. Purpose

Define clear boundaries and expectations between:

- **Enrichment & Orchestration layer** (this convo)
- **Kondo / LinkedIn ingestion & Viewer layer** (other convo, `con_nMxUrzVQQm0D6QTB`)

So that all components can safely build on a **single stakeholder intel model** without duplicating logic or drifting.

---

## 2. Canonical Data Stores

These are **sources of truth** that everyone must respect:

1. **CRM People Records (canonical)**
   - Location: `Personal/Knowledge/CRM/individuals/*.md`
   - One file per person, keyed by a stable **slug** (e.g. `lauren-salitan.md`).
   - Contains:
     - Core identity (name, email, organization, role).
     - Relationship context (how we know them, relationship strength, category).
     - Meeting IDs list (all meetings they appeared in).
     - Intelligence Log (append-only, chronological enrichment events).

2. **LinkedIn / Kondo DB (canonical for LinkedIn messages)**
   - Location: `Knowledge/linkedin/linkedin.db`
   - Tables:
     - `conversations`
     - `messages`
   - Holds **raw LinkedIn/Kondo conversations**; not summarized.

3. **Aviato Usage Log (canonical for Aviato calls)**
   - Location: `N5/logs/aviato_usage.jsonl`
   - Append-only; each line is a JSON object with at least:
     - `timestamp`
     - `email`
     - `person_found` (bool)
     - `aviato_person_id`
     - `aviato_company_id`
     - `error` (if any)

4. **Enrichment Infrastructure (internal, not user-facing)**
   - DB: `N5/data/crm_v3.db` (`profiles`, `enrichment_queue` tables).
   - YAML views: `N5/crm_v3/profiles/*.yaml`.
   - These exist to **run enrichment and link meetings**, but are not primary sources of truth about people.

---

## 3. Ownership Boundaries

### 3.1 Kondo / Viewer Layer (other convo) – **MAY DO**

These are safe responsibilities for the Kondo-focused work:

1. **Maintain LinkedIn ingestion pipeline**
   - Ensure Kondo webhook + `linkedin.db` stay healthy.
   - Extend LinkedIn schema or metadata as needed (e.g., tags, categories), as long as it remains backward-compatible.

2. **Enhance `stakeholder_intel.py` on the read side**
   - Improve formatting and structure of reports.
   - Control how many messages, emails, or Aviato entries are displayed.
   - Add alternative views ("professional snapshot", "relational history", etc.) **without changing underlying stores**.

3. **Refine CRM markdown template (structure only)**
   - May improve wording and grouping within these *existing* sections:
     - Header identity fields
     - Relationship context
     - Intelligence Log entries
   - May add **new, clearly named subsections** under Intelligence Log, such as:
     - `### 2025-11-30 | linkedin_intelligence`
     - `### 2025-11-30 | aviato_intelligence`
     - `### 2025-11-30 | email_thread_intelligence`
   - Must preserve **append-only, chronological** nature of the Intelligence Log.

4. **Add new read-only prompts and views**
   - `Prompts/meetings/stakeholder_intel.prompt.md` may be extended.
   - Additional prompts can call `stakeholder_intel.py` with different presets.

### 3.2 Kondo / Viewer Layer – **MUST NOT DO**

These are explicitly out of scope for that thread:

1. **No new CRM SQL databases**
   - Must not create another `crm.db` or equivalent.
   - Must not change the schema of `crm_v3.db` directly.

2. **No separate identity model**
   - Must not introduce new primary keys for people outside of:
     - CRM slug
     - Email
     - LinkedIn URL / conversation IDs embedded in CRM markdown.

3. **No enrichment orchestration**
   - Must not:
     - Call Aviato directly.
     - Decide `enrichment_policy` or `enrichment_status`.
     - Manage `enrichment_queue` or retry/backoff logic.

4. **No mutation of meeting files**
   - Must not edit files under `Personal/Meetings/**`.
   - May read them to resolve `Meeting IDs`, but cannot write blocks or manifests.

---

### 3.3 Enrichment & Orchestration Layer (this convo) – **MAY DO**

Responsibilities that belong to this thread:

1. **Aviato + LinkedIn enrichment decisions**
   - When to call Aviato vs fall back to LinkedIn-only enrichment.
   - How to interpret "internal", "vendor", and "high-value external" rules.
   - How to populate `enrichment_policy`, `enrichment_status`, and `last_enrichment_source` in `crm_v3.db`.

2. **Meeting ↔ CRM linking**
   - From `Personal/Meetings/.../manifest.json` + blocks (B03/B26) to:
     - Concrete CRM slugs (people).
     - Meeting IDs appended into CRM markdown.
     - Optional per-meeting Intelligence Log entries.

3. **Ad hoc entry points**
   - LinkedIn URL → "create/resolve person + enrich" path.
   - Future Gmail entry points for email-based relational intel.

4. **Write-side updates to CRM markdown**
   - Append new Intelligence Log entries.
   - Add or update metadata headers (emails, LinkedIn URLs, meeting ID lists) as needed.

### 3.4 Enrichment & Orchestration Layer – **MUST NOT DO**

1. **Must not bypass `stakeholder_intel.py` as the canonical join**
   - Any new *viewer* or *prompt* surface should:
     - Either call `stakeholder_intel.py` directly, or
     - Reuse its internal join functions.

2. **Must not define alternative "canonical" CRM locations**
   - `Personal/Knowledge/CRM/individuals/*.md` remains the source of truth.
   - YAML under `N5/crm_v3/profiles` is an internal cache/view only.

---

## 4. `stakeholder_intel.py` Contract

`N5/scripts/stakeholder_intel.py` is the **canonical viewer/join** over CRM, LinkedIn, and Aviato.

### 4.1 Inputs

- `--person-id <slug>`
  - `<slug>` corresponds to a file `Personal/Knowledge/CRM/individuals/<slug>.md`.

- `--meeting-id <meeting_id>`
  - `meeting_id` must be present either:
    - In meeting manifests under `Personal/Meetings/**/manifest.json`, or
    - In CRM markdown under `**Meeting IDs:**`.

### 4.2 Guarantees

For `--person-id`:

- Reads CRM markdown file.
- Extracts, at minimum:
  - Email
  - LinkedIn URL (if present)
  - LinkedIn conversation IDs (if present in the markdown header/metadata).
- Reads LinkedIn DB to fetch conversations/messages for any known conversation IDs.
- Reads Aviato usage log (`aviato_usage.jsonl`) to find relevant calls for that email.
- Outputs a **human-readable stakeholder report** to stdout, suitable for prompts.

For `--meeting-id`:

- Resolves meeting participants via:
  - Meeting manifest + blocks (B03/B26).
  - CRM markdown files matched by slug/email.
- Aggregates person-level intel for each participant.
- Outputs a meeting-focused stakeholder summary.

### 4.3 Non-goals

- Does **not** modify any data stores.
- Does **not** decide when enrichment should occur.
- Does **not** manage queues, retries, or policies.

---

## 5. CRM Markdown Intelligence Log Format

### 5.1 Structure

Within `Personal/Knowledge/CRM/individuals/<slug>.md`, the Intelligence Log section follows:

```markdown
## Intelligence Log

### 2025-11-18 05:26 | multi_source_enrichment
**Checkpoint:** worker_1_validation
**Sources:** aviato, gmail, linkedin (all stubbed)

**Aviato Professional Intelligence:**
- ...

**Gmail Thread Analysis:**
- ...

**LinkedIn Intelligence:**
- ...

Status: Phase 2 priority
Data Sources Active: Aviato (✓) + Gmail (✓)
```

Rules:

1. **Append-only**
   - New events always added at the bottom with a new `### <timestamp> | <label>` heading.

2. **Chronological**
   - Timestamps ordered ascending.

3. **Source-specific subsections**
   - Subheadings like `**Aviato Professional Intelligence:**`, `**LinkedIn Intelligence:**`, `**Email Thread Analysis:**` are encouraged for clarity.

4. **Cross-source coherence**
   - When multiple sources update the same person, later entries may reference or refine earlier ones, but **must not delete or rewrite history**.

---

## 6. Coordination Rules

1. **If you are building a new VIEWER or PROMPT:**
   - Call `stakeholder_intel.py` where possible.
   - Treat CRM markdown + LinkedIn DB + Aviato log as read-only.

2. **If you are building a new ENRICHMENT FLOW:**
   - Implement it in the enrichment/orchestration layer.
   - Write results into CRM markdown using the Intelligence Log format.
   - Optionally log raw API responses separately (e.g., under `N5/logs/**`).

3. **If you need a new field in CRM markdown:**
   - Add to the CRM template in a backwards-compatible way.
   - Ensure `stakeholder_intel.py` can read it, but avoid breaking older entries.

This contract should be treated as **stable for V1**. Future versions (V1.1, V2) can extend it, but should not silently break these guarantees.

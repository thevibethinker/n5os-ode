---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# CRM V3 Enrichment Spec – V1

Scope: Implementation-ready design for stakeholder enrichment across CRM V3, using Aviato as primary data source, with support for LinkedIn-driven ad hoc contacts and meeting/Gmail–discovered stakeholders.

Canonical home: `file 'N5/crm_v3/ENRICHMENT_SPEC_v1.md'`.

## 1. Goals & Non‑Goals

### 1.1 Goals (V1)

1. **Canonical truth in CRM V3**  
   - Every person "brought into the system" has a CRM person record.  
   - Aviato data, manual research, and briefs live on/under that record.

2. **Aggressive but controlled enrichment posture**  
   - Default behavior is: enrich most **external** stakeholders via Aviato
automatically once we have a viable key (usually work email).  
   - Internal people are never auto-enriched.  
   - Vendors are handled more cautiously (see policy matrix below).

3. **Ad hoc enrichment via LinkedIn URL**  
   - V can paste a LinkedIn URL and get:  
     - a CRM person created/updated,  
     - Aviato enrichment scheduled when possible,  
     - and the ability to request a **Stakeholder Brief** on demand.

4. **Meeting intelligence links cleanly into CRM**  
   - Meeting blocks (especially `B03_STAKEHOLDER_INTELLIGENCE` and `B26_MEETING_METADATA`) reference CRM person ids instead of free-floating names only.

### 1.2 Non‑Goals (V1)

- No complex scoring or prioritization beyond the **policy matrix** below.
- No UI changes; this is all file/worker/prompt level.
- No sophisticated LinkedIn scraping; V1 only requires we **store** the URL and wire it into the same enrichment & briefing pipeline. Any auto-parsing of LinkedIn contents can be a V1.1 extension.


## 2. What counts as “in the system”

> A person is **in the system** once **any** of the following occurs:
>
> 1. They appear in a **non-internal meeting** (manifest `meeting_type != "internal"`).
> 2. They appear in a **Gmail thread** that has been ingested and mapped into CRM.
> 3. They are manually added via a **LinkedIn URL** or manual CRM creation.

Implementation requirement:

- For any such person, ensure a canonical CRM V3 person record exists and is addressable by a stable `person_id`.
- All enrichment, briefs, and meeting references must hang off this `person_id`.


## 3. Data Model Extensions (CRM Person)

Extend the CRM V3 person model with the following fields (names can be normalized to existing conventions, but behavior must match):

### 3.1 Identity & external handles

- `primary_email: str | null`  
  Canonical email used for communication / enrichment (prefer work email).

- `linkedin_url: str | null`  
  Single canonical LinkedIn profile URL for this person.

- `aviato_person_id: str | null`  
  Aviato person identifier returned by the API when enrichment succeeds.

- `aviato_company_id: str | null`  
  Aviato company identifier for their current company, if available.

### 3.2 Classification

- `person_type: enum("internal", "candidate", "prospect", "customer", "investor", "vendor", "founder", "other")`

  Used to drive enrichment policy. Rules for setting:

  - `internal`: team members, advisors, close collaborators explicitly flagged internal.
  - `candidate`: job-seekers / people in active Careerspan coaching or hiring pipelines.
  - `prospect` / `customer`: buyers or evaluators for Careerspan products/services.
  - `investor`: actual or potential investors.
  - `vendor`: vendors, agencies, external providers.  
  - `founder`: founders / co-founders / owners / C-levels where the relationship is primarily founder-to-founder. Can be overlaid with another category (see below).
  - `other`: anything that doesn’t neatly fit yet.

Implementation detail: `founder` can either be a separate boolean flag (`is_founder`) or a `person_type` value. The spec assumes an implementation that can distinguish **vendor founder** from generic vendor (e.g., `person_type="vendor"` plus `is_founder=True`).

### 3.3 Enrichment policy & state

- `enrichment_policy: enum("always", "conditional", "never")`

  Default values (V1):

  - `internal`                  → `never`
  - `candidate`                 → `always`
  - `prospect` / `customer`     → `always`
  - `investor`                  → `always`
  - `vendor` + **founder/C‑level/owner** → `always`
  - `vendor` (non-founder)      → `conditional`
  - `other`                     → `conditional`

  `conditional` means: 
  - Not auto-enriched yet, but eligible for manual triggering or future heuristics.  
  - V1: no automatic `conditional` → `always` promotion; this is manual.

- `enrichment_status: enum(
    "never_attempted",
    "pending",
    "in_progress",
    "succeeded",
    "not_found",
    "failed",
    "skipped_internal",
    "skipped_policy"
  )`

- `last_enriched_at: datetime | null`
- `last_enrichment_source: enum("aviato", "manual_research") | null`
- `last_enrichment_error: str | null` (short, human-readable error/diagnostic)

### 3.4 Enrichment status state machine

Initial state:

- New external person with eligible policy → `enrichment_status = "never_attempted"`.

State transitions:

1. **Scheduling**  
   - Worker/logic decides to attempt enrichment → set `pending`.

2. **Worker picks up job**  
   - Set `in_progress` just before calling Aviato.

3. **Successful enrichment**  
   - Aviato returns usable data → update fields, set:  
     - `enrichment_status = "succeeded"`  
     - `last_enriched_at = now()`  
     - `last_enrichment_source = "aviato"`  
     - `last_enrichment_error = null`

4. **Person not found**  
   - Aviato explicitly reports "no match" / not found → set:  
     - `enrichment_status = "not_found"`  
     - `last_enriched_at = now()`  
     - `last_enrichment_error` with a short code/message.

5. **API / other failure**  
   - Network errors, 5xx, unexpected schema, or repeated client-level errors:  
     - `enrichment_status = "failed"`  
     - `last_enriched_at = now()`  
     - `last_enrichment_error` with summary.

6. **Internal or blocked by policy**  
   - `person_type = internal` → `enrichment_status = "skipped_internal"`.  
   - `enrichment_policy = "never"` (non-internal) → `enrichment_status = "skipped_policy"`.

Retry rules (V1 defaults):

- `failed`: allow **up to 2 total attempts** per person. After that, leave status as `failed` until manually reset.  
- `not_found`: do **not** auto-retry; manual reset only (e.g. after better email is added).  
- `skipped_*`: no auto-enrichment until policy/person_type changes.


## 4. Triggers for Creating/Updating People

### 4.1 Meeting ingestion (primary path)

For any non-internal meeting under `file 'Personal/Meetings/**'`:

1. Read `manifest.json` to get participants and `meeting_type`.
2. If `meeting_type == "internal"`, do **not** auto-enrich anyone for this meeting (respect the broader rule: meeting-level internal means "no outbound enrichment").
3. For each **external participant**:
   - Ensure a CRM person exists or create one (minimal fields: name, email if known, org if known).  
   - Compute `person_type` (using current heuristics + manifest hints).  
   - Set default `enrichment_policy` per matrix above **if not already set**.  
   - Initialize/update `linkedin_url` from manifest metadata if present.
   - Ensure meeting metadata records a **stable `person_id`** for this participant.

4. Write mapping back into:
   - `B26_MEETING_METADATA.md`: add a table or section:  
     - `Participant | Role | Email | CRM Person ID | Enrichment Status (snapshot)`
   - Optionally, `B03_STAKEHOLDER_INTELLIGENCE.md`: for each stakeholder, include a short CRM link annotation like:  
     - `CRM: konrad-kucharski (enrichment: succeeded via Aviato)`.

### 4.2 Gmail ingestion

Wherever existing Gmail → CRM mapping runs (outside this spec), extend behavior so that:

- When a new person is inferred from a Gmail thread:  
  - Create/update CRM person with `primary_email`, name, org, `person_type` (e.g., `candidate`, `prospect`, `vendor`, etc.).  
  - Initialize `enrichment_policy` according to the matrix.  
  - Set `enrichment_status = "never_attempted"` if eligible.

### 4.3 LinkedIn ad hoc entry (V1 minimal)

Provide a minimal workflow (script + prompt) that supports:

**Input:**
- Required: `linkedin_url`  
- Optional: name, current title, company, email, notes.

**Behavior:**

1. Look up existing CRM person by `linkedin_url` or `primary_email` (if provided).  
2. If found:
   - Update `linkedin_url` if missing or changed.  
   - Optionally update name/title/company if they were stubbed.
3. If not found:
   - Create a new CRM person with:  
     - `linkedin_url`  
     - name / title / company if provided (or manually entered in this workflow)  
     - `person_type` defaulting to `prospect` or `other` (configurable).  
   - Initialize `enrichment_policy` using the matrix (likely `always` for `prospect` / `investor`, `conditional` for ambiguous cases).
4. Mark `enrichment_status = "never_attempted"` if eligible by policy.
5. Optionally (if an email is provided and valid):  
   - Immediately schedule Aviato enrichment for this person (see worker section).

V1 does **not** require automatic scraping of LinkedIn HTML. The workflow may ask V to confirm or type name/title/company manually after pasting the URL. Auto-scraping can be documented as a V1.1 extension.


## 5. Aviato Enrichment Worker – Behavior

Implementation will likely extend `file 'N5/scripts/enrichment/aviato_enricher.py'` and `file 'N5/scripts/crm_enrichment_worker.py'`. This spec describes required behavior, not specific function names.

### 5.1 Eligibility filter

When the worker runs (batch or continuous):

1. Select CRM persons where:
   - `enrichment_status in ("never_attempted", "pending", "failed")`, and  
   - `enrichment_policy = "always"`, and  
   - `person_type != "internal"`.
2. For `failed`, enforce the retry limit (max 2 attempts total) before re-queueing.
3. Exclude any with `enrichment_policy = "never"` or `person_type = "internal"`.

### 5.2 Key selection (what we send to Aviato)

Precondition for V1:

- We **prefer** email-based enrichment. The Aviato client (`AviatoClient`) is responsible for mapping from the CRM person to the appropriate API call (e.g., with email, name, company).

Behavior:

1. If `primary_email` is present:
   - Attempt enrichment using email as the primary key.
2. If no email is present, but we have name + company and the Aviato client supports that mode:
   - Optionally, attempt enrichment via name + company (configurable; may be off by default in V1 unless the client is already designed for this).
3. If neither a valid email nor a supported alternate key exists:
   - Leave `enrichment_status` as `never_attempted`, or set to `failed` with `last_enrichment_error = "no_viable_key"` (implementation choice, but must be consistent and documented in code).

### 5.3 Call semantics & cost controls (defaults)

- Implement basic rate limiting / batching in the worker to avoid hammering the API. Suggested defaults:
  - Max **concurrent** Aviato calls: 5–10.  
  - Optional soft daily cap: e.g. **200 successful calls/day**; beyond that, log and skip further auto-enrichment until next day.
- On 429 / 5xx responses:
  - Backoff and retry with exponential delay up to a short limit (e.g., 2–3 retries).  
  - If still failing, mark as `failed` with a clear `last_enrichment_error` (e.g. `"aviato_429_rate_limited"`).

### 5.4 Writing results back to CRM

When Aviato returns a successful response:

1. Map fields into CRM via existing or updated `AviatoCRMMapper`:
   - Core identity (name, emails, title, company, location).  
   - Career history (company roles, dates).  
   - Skills / tags.  
   - Any relevant metadata that is stable and non-noisy.
2. Update enrichment fields on the person:
   - `aviato_person_id`, `aviato_company_id` if present.  
   - `enrichment_status = "succeeded"`  
   - `last_enriched_at = now()`  
   - `last_enrichment_source = "aviato"`  
   - `last_enrichment_error = null`
3. Append or update a section in the person’s markdown file under `file 'Personal/Knowledge/CRM/individuals/**'`, following existing patterns such as:

   ```md
   ### 2025-11-29 14:35 | aviato_enrichment

   **Source:** aviato_api  

   **Aviato Professional Intelligence:**
   - Current role & org summary
   - Career arc bullets
   - Notable skills / focus areas
   - Any other stable, high-signal facts
   ```

On not-found or error cases, update the timestamp/status and write a short line into the person file’s log for traceability.


## 6. Stakeholder Briefs

A **Stakeholder Brief** is a human-centered summary used for prep and strategy.

### 6.1 Trigger

- Explicit request from V (via prompt / script) for a given person (by name or `person_id`).
- Optionally auto-suggested before important meetings (out of V1 scope, but design should not block it).

### 6.2 Inputs

The generator should pull from:

- CRM person record (including Aviato fields).  
- Aviato Professional Intelligence section(s) in the person file.  
- Past meetings and notes linked to this `person_id` (recaps, B03 stakeholder intel, etc.).

### 6.3 Standard structure

Stakeholder Briefs should follow a consistent outline, with emphasis on:

1. **Snapshot: Who they are**  
   - Current role, company, where they sit in the ecosystem.

2. **Career journey**  
   - High-level arc: key roles, transitions, themes (e.g., operator → founder, big tech → startup, etc.).

3. **What they care about**  
   - Inferred themes: what problems, domains, or levers they repeatedly optimize for.  
   - Signals from Aviato + meetings + public footprint.

4. **How they can help Careerspan**  
   - Concrete ways they might plug into Careerspan’s world:  
     - As buyer, champion, referrer, investor, thought partner, design partner, etc.  
   - Any specific angles: talent they might refer, intros they can make, or experiments they might be open to.

5. **Approach strategy**  
   - Recommended tone and framing.  
   - Topics to lead with / avoid.  
   - Risks or sensitivities.

### 6.4 Output location

- Append stakeholder briefs into the person’s markdown under a dedicated heading, e.g.:

  ```md
  ## Stakeholder Briefs

  ### 2025-11-29 | Pre-intro brief
  ...
  ```

- The generator should **not overwrite** previous briefs; it appends new dated entries.
- Meeting blocks can link to these briefs by `person_id` and date when relevant.


## 7. Meeting Integration

### 7.1 B26_MEETING_METADATA.md

Extend B26 to include a canonical participant table such as:

```md
### Participants (canonical)

| Name | Role | Email | CRM Person ID | Enrichment Status (snapshot) |
| --- | --- | --- | --- | --- |
| Konrad Kucharski | CRO & Co-Founder, Aviato | konrad@aviato.co | konrad-kucharski | succeeded |
```

- `Enrichment Status (snapshot)` is informational only; the worker owns the true state.

### 7.2 B03_STAKEHOLDER_INTELLIGENCE.md

Where helpful, annotate stakeholders with CRM linkage, e.g.:

```md
#### Konrad Kucharski
- Role: CRO & Co-Founder, Aviato
- CRM: konrad-kucharski (Aviato enrichment: succeeded)
- Key interests: ...
```

Generation prompts should treat CRM as canonical and **pull** from it when generating/updating B03, rather than duplicating free-hand summarized facts.


## 8. Logging & Observability

V1 minimum requirements:

1. **Enrichment attempt log**  
   - For each Aviato call, log: timestamp, `person_id`, key used (e.g. email), result status (`succeeded`, `not_found`, `failed` + code).

2. **Daily summary (optional but recommended)**  
   - Simple aggregate counters: total attempted, succeeded, not_found, failed, skipped_internal/policy.

3. **Failure introspection**  
   - Errors should be written in a way that future prompts / scripts can surface patterns (e.g. many `no_viable_key` errors → upstream email capture issue).


## 9. Implementation Notes / Handoff

- **Primary files impacted (expected):**
  - `file 'N5/crm_v3/README.md'` (add references to enrichment + fields).  
  - `file 'N5/crm_v3/ENRICHMENT_SPEC_v1.md'` (this spec; keep updated as source of truth).  
  - `file 'N5/scripts/enrichment/aviato_enricher.py'` (update to conform to this behavior).  
  - `file 'N5/scripts/crm_enrichment_worker.py'` (policy + queue + state machine logic).  
  - Meeting generator prompts under `file 'Prompts/**'` to add CRM links into B03/B26.

- **Out of scope for V1 but compatible extensions:**
  - Automatic LinkedIn HTML parsing to pre-fill name/title/company fields.  
  - A dashboard-like summary of all enriched stakeholders.  
  - Automatic suggestion of Stakeholder Briefs before key meetings.


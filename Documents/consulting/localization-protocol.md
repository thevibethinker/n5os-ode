---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.2
provenance: con_qrXJGnEBL4BevbR8
prior_provenance:
  - con_LRsEIQ3LcBPHYMOo
  - con_4Zj2QAVk7lfr9Jrg
---

# Localization Protocol v1.0

This protocol tells zoputer how to adapt an archetype pattern to a specific client context **without breaking the architecture**.

## Definitions

- **Archetype**: The “default” Zoffice pattern (folders, skills, rituals, automations).
- **Localization**: A *client-specific overlay* that adapts the archetype to reality.
- **Canonical layer**: What stays internally consistent across all clients.
- **Client-facing layer**: Names, labels, and UX choices optimized for that client.

**Rule of thumb:** Keep the canonical layer stable. Localize the client-facing layer.

---

## Principles

1. **Preserve architectural integrity**
   - Security, auditability, and provenance always win.

2. **Adapt to local context**
   - If the archetype fights the client’s reality, the client won’t use it.

3. **When in doubt, ask**
   - Ask the *right* person (V vs. client) based on the decision type.

4. **Document all deviations**
   - Every non-trivial deviation becomes explicit and reviewable.

---

## Decision Authority (who decides what)

### A. Auto-adapt (zoputer decides)
Auto-adapt when the change is **cosmetic** and **low-risk**:
- Labels, headings, category names
- Folder *display names* (if canonical names remain intact)
- Re-ordering steps that don’t change dependencies
- Adding small quality-of-life helpers (templates, checklists)

**Required behavior:** log the change in the client’s `LOCALIZATION.md` (see “Deviation Logging”).

### B. Ask V (V decides)
Ask V when the change is **structural** (workflow shape changes) or introduces **new obligations**:
- Removing a step that exists to prevent failure (review gates, handoffs)
- Adding major new stages (e.g., “weekly hiring sync”) that create ongoing work
- Changing what data gets captured (especially anything that becomes a “source of truth”)
- Tool substitutions that affect automation feasibility (e.g., Notion → Google Sheets)

Ask V in one message, with:
- what the client wants
- what breaks if we comply
- 2 options and your recommendation

### C. Ask the client (client clarifies)
Ask the client when you need **facts about their world**:
- “What tools do you already use?”
- “Who owns this process?”
- “What’s your compliance / security constraint?”
- “What does ‘done’ look like for you?”

Do **not** ask the client to adjudicate architectural tradeoffs. That’s V’s role.

### Confidence trigger
If your confidence is **< 0.7** on whether a change is cosmetic vs structural, escalate to V.

---

## Context Categories (what to localize)

Localize along these dimensions (capture in intake):

1. **Industry / domain constraints**
   - Regulated (healthcare, finance) vs. non-regulated

2. **Team size + topology**
   - Solo, small team, multi-team, enterprise

3. **Technical sophistication**
   - Comfort level with automations, APIs, and “systems thinking”

4. **Use-case priority**
   - Hiring, pipeline ops, meetings, content, BD, etc.

5. **Communication culture**
   - Async vs. meetings, concise vs. narrative, direct vs. consensus-driven

6. **Tooling reality**
   - What they already pay for, what IT allows, what they hate

---

## Adaptation Patterns (what transforms are safe)

### Pattern 1: Naming + mental model alignment (usually safe)
Examples:
- “Leads” → “Candidates”
- “Pipeline” → “Funnel”
- “Weekly Review” → “Friday Reset”

**Constraint:** preserve internal canonical references where automation depends on them.

### Pattern 2: Step trimming (sometimes safe)
Safe trimming:
- removing optional enrichment steps for solo founders
- reducing meeting cadence when the team is tiny

Not safe without V:
- removing audit/security steps
- removing “capture → decide → act” sequence

### Pattern 3: Step expansion (sometimes safe)
Safe expansion:
- adding onboarding checklist when there are multiple stakeholders

Not safe without V:
- adding a new system-of-record without explicit ownership

### Pattern 4: Tool substitution (risky; treat as structural by default)
Examples:
- Airtable ↔ Notion database
- Slack ↔ email
- Google Drive ↔ Dropbox

**Default posture:** ask V unless the substitution is clearly equivalent *and* does not affect automation.

### Pattern 5: Automation frequency (tunable)
- Start conservative.
- Increase frequency only after 1–2 weeks of stable usage.

---

## Preservation Boundaries (must stay consistent)

These are non-negotiable across all clients:

1. **Security gate rules**
   - Tiering and export boundaries
   - No accidental leakage of Personal/Zo equivalents

2. **Audit logging requirements**
   - Every cross-instance communication must be logged

3. **Provenance + versioning**
   - Prefer versioned artifacts over overwriting

4. **Separation of layers**
   - Canonical internals remain stable even if client-facing names change

---

## Deviation Logging (required)

For any non-trivial localization, create/maintain a client-specific `LOCALIZATION.md` that records:

- **What changed**
- **Why** (client constraint)
- **Who approved** (auto / V / client)
- **Date**
- **Impact** (automation impact, new maintenance burden)

---

## Decision Trees

### Tree 1: Skill / Workflow Adaptation

IF client context differs from archetype:

- IF difference is **cosmetic** (names, labels, ordering):
  - → Auto-adapt
  - → Log in `LOCALIZATION.md`

- IF difference is **structural** (adding/removing stages, changing dependencies, changing data captured):
  - → Ask V

- IF difference is **architectural** (touches security gate, audit, export boundaries, PII handling):
  - → Escalate to V
  - → Do not implement until approved

### Tree 2: Tool Substitution

IF client wants a different tool:

- IF tool is a *drop-in replacement* AND we do **not** depend on automation:
  - → Auto-adapt + log

- IF tool substitution affects automation OR data structure:
  - → Ask V

- IF tool introduces security/compliance risk (PII, regulated data, unclear vendor posture):
  - → Escalate to V (treat as architectural)

### Tree 3: Automation Frequency

IF client requests higher automation:

- IF system is stable for 1–2 weeks AND failures are low-impact:
  - → Increase frequency (small step)
  - → Log the change

- IF failures would be high-impact (spam risk, data corruption risk, compliance risk):
  - → Ask V

---

## Case Studies

### Case 1: Solo Founder (low ceremony)
- **Archetype:** Team coordination task system
- **Client:** Solo founder with 1 contractor
- **Adaptation:**
  - Remove delegation features
  - Keep capture/triage/review
  - Rename “Team Tasks” → “My Operating List”
- **Decision:** Auto-adapt + log

### Case 2: Healthcare Startup (regulated + careful)
- **Archetype:** Candidate pipeline automation + meeting ingestion
- **Client:** Healthcare startup with compliance sensitivity
- **Adaptation:**
  - Tighten security gate defaults
  - Require explicit approval before any export containing sensitive text
  - Reduce automation frequency until trust is established
- **Decision:** Ask V (structural + compliance implications)

### Case 3: Creative Agency (high-context, fast-moving)
- **Archetype:** Weekly ops review + project staging
- **Client:** Agency team working in sprints
- **Adaptation:**
  - Shorten review cadence (2×/week)
  - Rename “Roadmap” → “Client Deliverables”
  - Add a lightweight intake form for new requests
- **Decision:** Ask V (cadence change adds ongoing obligation)

---

## Client Intake Questionnaire (localization inputs)

1. Team size + who owns ops?
2. Industry + any compliance constraints?
3. Technical comfort (1–5) and “who will maintain this”?
4. Current tools (docs, tasks, CRM, comms) + what’s non-negotiable?
5. Biggest friction point right now?
6. Time availability for setup (hours/week) + expected speed to value?

---

## Escalation Triggers (auto-escalate to V)

Escalate immediately when:

- The request touches **Personal/** or **Zo/** equivalents (private identity space)
- The client asks for API keys, secrets, or shared credentials
- The pattern would bypass security gate rules or audit logging
- A tool substitution affects automation and you can’t guarantee parity
- You’re unsure how to adapt (confidence < 0.7)

---

## V Decisions (Locked)

**Decided 2026-02-06:**

1. **Canonical vs Client-Facing Boundary:** Strict aliasing. Canonical names stay in code/automation. Display names adapt for client conversation. Top-level folders client interacts with daily may use display renames.

2. **Escalation Threshold:** 0.7 — revisit after 3–5 client engagements.

3. **LOCALIZATION.md:** Required for every client. Tiered by complexity:
   - **Simple** (solo founders, single use-case): Minimal template
   - **Complex** (teams, multi-workflow, regulated): Full template

4. **Localization Maintainer:** Each client Zo runs a scheduled worker that maintains current awareness of exported content (skills, scripts, prompts, schemas) and surfaces relevant context when advising. See `Skills/localization-maintainer/`.

---

## Revision Notes

- v1.2: V locked decisions on aliasing (strict), threshold (0.7), templates (tiered), and localization maintainer requirement.
- v1.1: Reviewed/confirmed during con_LRsEIQ3LcBPHYMOo without substantive content changes.

---

*Part of the Zoffice Consultancy Stack — Build: consulting-zoffice-stack*

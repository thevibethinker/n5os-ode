---
created: 2026-02-02
last_edited: 2026-02-02
version: 1.0
provenance: con_NLOu2MVInIYnuwuf
---
# Careerspan Pipeline v2 — Build Plan

## Objective

Complete the Careerspan-CorridorX pipeline by:
1. Converting each action flow (`[JD]`, `[RESUME]`, `[UPDATE]`, Intelligence Brief processing) into standalone skills
2. Fixing the decomposer skill to align with actual Intelligence Brief output format
3. Wiring the orchestrator to execute these skills (not just generate prompts)

## Context

**Current State:**
- Pipeline orchestrator exists but only generates prompts — doesn't execute actions
- Three skills exist: `careerspan-candidate-guide`, `careerspan-decomposer`, `meta-resume-generator`
- Webhook receiver scaffolded at `careerspan-webhook` (port 8850)
- Heartbeat agent created but relies on incomplete orchestrator

**Target State:**
- Each email tag triggers a complete skill that handles the full flow
- Skills update Airtable, send emails to Shivam, upload to Drive
- Decomposer aligned with actual Careerspan Intelligence Brief format

## Streams

### Stream 1: Action Flow Skills (3 Drops)

| Drop | Skill | Trigger | Actions |
|------|-------|---------|---------|
| D1.1 | `careerspan-jd-intake` | `[JD]` email | Extract JD → Create Airtable record → Generate Hiring POV → Upload to Drive → Email Shivam |
| D1.2 | `careerspan-resume-intake` | `[RESUME]` email | Extract candidate → Match to job → Create Airtable record → Generate Candidate Guide → Upload to Drive → Email Shivam |
| D1.3 | `careerspan-update-handler` | `[UPDATE]` email | Parse update type → Update Airtable record(s) → Email Shivam if needed |

### Stream 2: Decomposer Alignment (1 Drop)

| Drop | Task |
|------|------|
| D2.1 | Analyze actual Intelligence Brief format from `Knowledge/Careerspan/careerspan-product-overview.txt`, compare to decomposer schema, update decomposer to handle real format |

### Stream 3: Orchestrator Wiring (1 Drop)

| Drop | Task |
|------|------|
| D3.1 | Update `pipeline_orchestrator.py` to invoke the new skills instead of just generating prompts; wire heartbeat to full execution |

## Dependencies

```
Stream 1 (D1.1, D1.2, D1.3) → parallel, no dependencies
Stream 2 (D2.1) → parallel with Stream 1
Stream 3 (D3.1) → depends on Stream 1 + Stream 2 completion
```

## Drop Briefs

### D1.1 — JD Intake Skill

**Skill:** `Skills/careerspan-jd-intake/`

**Inputs:**
- Email data (subject, body, attachments)
- Config from `Integrations/careerspan-pipeline/config.yaml`

**Actions:**
1. Extract JD from email body and/or attachments (PDF/DOCX → text)
2. Use LLM to extract: company name, role title, location, requirements
3. Check JD against 5 Core Questions, identify missing answers
4. Create Job Opening record in Airtable (`tblHgSEOsoegYnJl7`)
5. Run `careerspan-candidate-guide` decompose_jd to generate Hiring POV
6. Upload Hiring POV to Drive using `drive_upload.py` pattern
7. Email Shivam with: POV link, missing Core Questions list
8. Update Airtable record with Drive link, status, ball_in_court

**Output:** Job Opening record ID, Hiring POV Drive link

---

### D1.2 — Resume Intake Skill

**Skill:** `Skills/careerspan-resume-intake/`

**Inputs:**
- Email data with resume attachment
- Config

**Actions:**
1. Extract candidate info from email (name, email)
2. Extract resume from attachment
3. Use LLM to match to existing Job Opening (from email context or Airtable lookup)
4. Create Candidate record in Airtable (`tblWB2mGbioA8pLBL`)
5. Run `careerspan-candidate-guide` to generate Candidate Guide PDF
6. Upload to Drive (employer/candidates/candidate-slug/)
7. Email Shivam with: candidate summary, Guide link, any flags
8. Update Airtable candidate status

**Output:** Candidate record ID, Guide Drive link

---

### D1.3 — Update Handler Skill

**Skill:** `Skills/careerspan-update-handler/`

**Inputs:**
- Email data
- Config

**Actions:**
1. Use LLM to classify update type: employer_response, candidate_status, role_status, general_intel
2. Extract relevant updates from email body
3. Identify target record(s) in Airtable
4. Update Airtable record(s) with new info
5. If Core Questions answered → trigger Hiring POV refresh
6. Email Shivam if response needed
7. Update ball_in_court tracking

**Output:** Updated record ID(s), response sent flag

---

### D2.1 — Decomposer Alignment

**Task:** Align `careerspan-decomposer` with actual Intelligence Brief format

**Reference:** `Knowledge/Careerspan/careerspan-product-overview.txt`

**Key sections to extract from Intelligence Brief:**
- Overall score (e.g., 72/100)
- Bottom line statement
- Category breakdowns (Background, Uniqueness, Responsibilities, Hard Skills, Soft Skills)
- Key strengths and development areas
- Career trajectory context
- "Our Take" assessments per skill
- Story-verified vs resume-only signal strength

**Actions:**
1. Read current decomposer schema (`Skills/careerspan-decomposer/assets/canonical_schema.json`)
2. Compare to actual Intelligence Brief format from product overview
3. Update decompose.py to handle the real format
4. Update validate.py with new schema checks
5. Test with existing Hardik data

**Output:** Updated decomposer skill aligned with real format

---

### D3.1 — Orchestrator Wiring

**Task:** Wire pipeline_orchestrator.py to invoke skills

**Actions:**
1. Replace prompt-generation with skill invocation
2. Add Airtable CRUD functions (using `use_app_airtable`)
3. Add Gmail send function (using `use_app_gmail`)
4. Add Drive upload execution
5. Update heartbeat agent instruction to use new orchestrator
6. Test full flow with sample data

**Output:** Working end-to-end pipeline

---

## Spawn Mode

All Drops: `spawn_mode: auto` (headless via /zo/ask)

## Success Criteria

1. `[JD]` email → Job Opening in Airtable + Hiring POV in Drive + Email to Shivam
2. `[RESUME]` email → Candidate in Airtable + Guide in Drive + Email to Shivam
3. `[UPDATE]` email → Airtable record updated + Response if needed
4. Intelligence Brief → Decomposed YAML matching real format → Meta-Resume PDF
5. Heartbeat runs automatically and processes all flows

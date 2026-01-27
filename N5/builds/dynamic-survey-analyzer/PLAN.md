---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
type: build_plan
status: active
provenance: con_BzmgI4mjor9Wsvfy
---

# Plan: Dynamic Survey Analyzer Skill

**Objective:** Build an automated survey analysis system that triggers on first webhook submission, spawns analysis workers via Pulse, generates insights + dashboard, and creates a 30-day recurring agent for ongoing updates.

**Trigger:** V needs automated analysis of Fillout survey responses (specifically "Next Play - Fundamentals of AI Productivity Pre-Event Survey") with creative/divergent analysis layer.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

<!-- All resolved -->
- [x] Viz library choice → **Plotly** (interactive HTML dashboards, publication quality)
- [x] Trigger mechanism → Webhook detects first submission for new formId
- [x] Multi-account support → Use `FILLOUT_SECRET_CAREERSPAN` and `FILLOUT_SECRET_PERSONAL` env vars

---

## Checklist

### Phase 1: Foundation
- ☐ Create SKILL.md for `Skills/dynamic-survey-analyzer/`
- ☐ Create multi-account Fillout API client (`scripts/fillout_client.py`)
- ☐ Update webhook to detect new forms and trigger analysis
- ☐ Test: Webhook correctly detects first submission for unknown formId

### Phase 2: Analysis Pipeline
- ☐ Create Context/Hypothesis Worker brief
- ☐ Create Analysis Worker brief  
- ☐ Create Level Upper Worker brief
- ☐ Create Synthesis Worker brief
- ☐ Test: Worker briefs pass MECE validation

### Phase 3: Dashboard & Persistence
- ☐ Create dashboard generator script (`scripts/generate_dashboard.py`)
- ☐ Create scheduled agent generator (`scripts/create_analysis_agent.py`)
- ☐ Create analysis file template and storage structure
- ☐ Test: Dashboard generates with sample data

---

## Phase 1: Foundation

### Affected Files
- `Skills/dynamic-survey-analyzer/SKILL.md` - CREATE - Skill definition and usage instructions
- `Skills/dynamic-survey-analyzer/scripts/fillout_client.py` - CREATE - Multi-account API client
- `N5/Integrations/fillout/app.py` - UPDATE - Add new form detection trigger

### Changes

**1.1 SKILL.md:**
Create the skill manifest with:
- Name: `dynamic-survey-analyzer`
- Description: Automated survey analysis with multi-worker orchestration
- Usage instructions for manual trigger and webhook-based auto-trigger
- References to scripts and their CLI interfaces

**1.2 Multi-Account Fillout Client:**
Python script that:
- Auto-detects which account a formId belongs to (tries both API keys)
- Fetches form structure (questions, types, options)
- Fetches all submissions for a form
- Returns normalized data structure

**1.3 Webhook Trigger Enhancement:**
Update `N5/Integrations/fillout/app.py` to:
- Track known formIds in a state file (`known_forms.json`)
- On submission, check if formId is new
- If new: log to new form queue, trigger analysis pipeline
- Pass both form metadata and first submission to pipeline

### Unit Tests
- `python3 fillout_client.py --list-forms` shows forms from both accounts
- `python3 fillout_client.py --form-structure <formId>` returns question schema
- Webhook logs new form detection when first submission arrives

---

## Phase 2: Analysis Pipeline

### Affected Files
- `N5/builds/dynamic-survey-analyzer/workers/D1.1-context-hypothesis.md` - CREATE
- `N5/builds/dynamic-survey-analyzer/workers/D1.2-quantitative-analysis.md` - CREATE
- `N5/builds/dynamic-survey-analyzer/workers/D1.3-level-upper.md` - CREATE  
- `N5/builds/dynamic-survey-analyzer/workers/D2.1-synthesis.md` - CREATE

### Changes

**2.1 Context/Hypothesis Worker (D1.1):**
- Inputs: Form structure (questions, types), form description, first N submissions
- Outputs: Interpretation framework, hypotheses about what patterns to look for
- Persona: Researcher

**2.2 Quantitative Analysis Worker (D1.2):**
- Inputs: All submissions, interpretation framework from D1.1
- Outputs: Frequency distributions, cross-tabs, statistical summaries
- Persona: Builder (data analysis focus)

**2.3 Level Upper Worker (D1.3):**
- Inputs: Raw data + D1.1 framework + D1.2 analyses
- Outputs: 20-30% additional novel perspectives, unexpected slices, divergent insights
- Persona: Level Upper (creative/divergent)

**2.4 Synthesis Worker (D2.1):**
- Inputs: All outputs from Stream 1 (D1.1, D1.2, D1.3)
- Outputs: Integrated analysis file, dashboard data structure
- Persona: Strategist
- Depends on: Stream 1 complete

### Unit Tests
- All briefs exist with correct frontmatter
- MECE validator passes: `python3 N5/scripts/mece_validator.py dynamic-survey-analyzer`

---

## Phase 3: Dashboard & Persistence

### Affected Files
- `Skills/dynamic-survey-analyzer/scripts/generate_dashboard.py` - CREATE
- `Skills/dynamic-survey-analyzer/scripts/create_analysis_agent.py` - CREATE
- `Skills/dynamic-survey-analyzer/assets/dashboard_template.html` - CREATE
- `Datasets/survey-analyses/` - CREATE - Storage location for analysis outputs

### Changes

**3.1 Dashboard Generator:**
Uses Plotly to generate:
- Response count over time chart
- Distribution charts for multiple-choice questions
- Word clouds or theme summaries for open-ended questions
- Key metrics cards (response rate, avg completion time, etc.)
- Single self-contained HTML file output

**3.2 Scheduled Agent Generator:**
Script that:
- Creates a scheduled agent via `create_agent` tool
- Runs every 24 hours for 30 days
- Agent checks JSONL for new submissions since last run
- Regenerates analysis and dashboard if new data exists
- Self-destructs after 30 days

**3.3 Analysis Storage:**
- Each survey gets a folder: `Datasets/survey-analyses/<formId>/`
- Contains: `analysis.md`, `dashboard.html`, `data.json`, `meta.json`

### Unit Tests
- Dashboard generates valid HTML from sample data
- Agent creation script produces valid scheduled agent

---

## MECE Validation

### Scope Coverage Matrix

| Scope Item | Drop | Status |
|------------|------|--------|
| `SKILL.md` | D1.1 | ✓ |
| `fillout_client.py` | D1.2 | ✓ |
| `app.py` webhook update | D1.2 | ✓ |
| Context/hypothesis logic | D1.1 | ✓ |
| Quantitative analysis logic | D1.2 | ✓ |
| Level Upper analysis | D1.3 | ✓ |
| Synthesis integration | D2.1 | ✓ |
| `generate_dashboard.py` | D2.1 | ✓ |
| `create_analysis_agent.py` | D2.1 | ✓ |
| Dashboard template | D2.1 | ✓ |
| Storage structure | D2.1 | ✓ |

### Token Budget Summary

| Drop | Brief (tokens) | Files (tokens) | Total % | Status |
|------|----------------|----------------|---------|--------|
| D1.1 | ~2,000 | ~3,000 | ~2.5% | ✓ |
| D1.2 | ~2,500 | ~8,000 | ~5% | ✓ |
| D1.3 | ~1,500 | ~5,000 | ~3% | ✓ |
| D2.1 | ~3,000 | ~10,000 | ~6.5% | ✓ |

### MECE Validation Result

- [x] All scope items assigned to exactly ONE worker (no overlaps)
- [x] All plan deliverables covered (no gaps)
- [x] All workers within 40% token budget
- [x] Stream dependencies are valid (D2.1 depends on Stream 1)
- [ ] `python3 N5/scripts/mece_validator.py dynamic-survey-analyzer` passes (run after briefs created)

---

## Worker Briefs (Drops)

| Stream | Drop | Title | Brief File | Persona |
|--------|------|-------|------------|---------|
| 1 | D1.1 | Context & Hypothesis | `drops/D1.1-context-hypothesis.md` | Researcher |
| 1 | D1.2 | Quantitative Analysis | `drops/D1.2-quantitative-analysis.md` | Builder |
| 1 | D1.3 | Level Upper Analysis | `drops/D1.3-level-upper.md` | Level Upper |
| 2 | D2.1 | Synthesis & Dashboard | `drops/D2.1-synthesis.md` | Strategist |

---

## Success Criteria

1. First submission to a new Fillout form triggers automatic analysis pipeline
2. Pipeline produces: analysis.md, dashboard.html, data.json for each survey
3. Dashboard includes Plotly interactive charts (distributions, time series, themes)
4. 30-day recurring agent updates analysis daily with new submissions
5. Both Fillout accounts (Personal + Careerspan) are supported
6. Level Upper contributes measurably distinct insights (20-30% of final analysis)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Low submission volume makes analysis thin | Require minimum 3 submissions before generating dashboard |
| Open-ended questions hard to analyze | Use LLM-based theme extraction (already have in survey_dashboard.py) |
| Agent runs for 30 days even if survey closes | Agent checks if new submissions exist; skips if none for 7 days |
| Multiple surveys trigger simultaneously | Queue-based processing, one at a time |

---

## Level Upper Review

*Will be completed after initial plan review with V.*

### Counterintuitive Suggestions Received:
- TBD

### Incorporated:
- TBD

### Rejected (with rationale):
- TBD

---

## Viz Stack Decision

**Choice: Plotly**

**Rationale:**
- Interactive HTML dashboards (hover, zoom, filter)
- Publication-quality aesthetics out of the box
- Single self-contained HTML file (no server needed)
- 18K+ GitHub stars, mature ecosystem
- Already familiar from existing survey_dashboard.py work
- Alternatives considered: Altair (good but less interactive), Dash (overkill for static dashboard), Streamlit (needs server)

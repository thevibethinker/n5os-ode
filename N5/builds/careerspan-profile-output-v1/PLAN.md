---
created: 2026-01-29
last_edited: 2026-01-29
version: 1.0
provenance: con_JTGSUg7MJeBHzmdq
---

# Build Plan: Careerspan Profile Output v1

## Purpose

Create a one-page, trade-offs-based candidate presentation that demonstrates Careerspan's deep qualitative signal. The output should help a CEO/Founder answer: **"Is H. worth 30 minutes of my time?"**

**Key Principle:** Framework-first, candidate-second. Define "good" before seeing how the candidate maps. Full audit trail with reasoning traces.

---

## Context

- **Audience:** CEO/Founder of FlowFuse (sophisticated buyer who knows the role deeply)
- **Decision moment:** Final presentation — "Here's our best candidate, what do you think?"
- **Success metric:** Even if H. isn't a fit, the employer trusts Careerspan's lens
- **Design:** Consistent with mycareerspan.com aesthetic
- **Output:** Gamma web page + short.io link + PDF fallback

---

## Data Sources

| Source | Location |
|--------|----------|
| Candidate Analysis | `/home/.z/workspaces/con_4yp5BoXoZM2YzXXN/hardik-flowfuse-data/` |
| Job Description | `jd.md` (saved to build folder) |
| Design Reference | https://www.mycareerspan.com |

---

## Panel Structure

| Panel | Name | Purpose |
|-------|------|---------|
| **1** | The Thesis | One-paragraph synthesis: Who H. is, what you get, core trade-off. Must stand alone (80% value if reader stops here). |
| **2** | Hard Skills: Bar Cleared | Binary table showing JD requirements met with evidence. De-risks the meeting. |
| **3** | Differentiators | What's remarkable + validated soft skills. Signal the resume can't carry. |
| **4** | Why This Meeting Matters | Synthesizes culture fit, company-candidate alignment, specific questions to explore. |

---

## Stream 1: Setup & Framework (Parallel)

| Drop | Task | Inputs | Outputs |
|------|------|--------|---------|
| **D1.1** | Design Capture | mycareerspan.com | `design-spec.md` |
| **D1.2** | FlowFuse Company Research | Web research | `flowfuse-company-intel.md` |
| **D1.3** | FlowFuse Culture/Values Research | Web research, job posting signals | `flowfuse-culture-intel.md` (with thin-results flag if <3 signals) |
| **D1.4a** | Panel Purposes & Success Criteria | JD, build context | `panel-purposes.md` |
| **D1.4b** | Evaluation Rubrics | `panel-purposes.md` | `evaluation-rubrics.md` |

**Dependencies:** D1.4b waits for D1.4a. All others parallel.

---

## Stream 2: Analysis & Content (Sequential after Stream 1)

| Drop | Task | Inputs | Outputs |
|------|------|--------|---------|
| **D2.0** | Remarkable Scan | Candidate data (pre-rubric) | `remarkable-scan.md` — What's surprising/unusual/rare about H.? |
| **D2.1** | Apply Rubric → Panel 1 | `evaluation-rubrics.md`, candidate data | `panel-1-thesis.md` + `panel-1-reasoning.md` |
| **D2.2** | Apply Rubric → Panel 2 | `evaluation-rubrics.md`, candidate data, JD | `panel-2-hard-skills.md` + `panel-2-reasoning.md` |
| **D2.3** | Apply Rubric → Panel 3 | `evaluation-rubrics.md`, candidate data, `remarkable-scan.md` | `panel-3-differentiators.md` + `panel-3-reasoning.md` |
| **D2.4** | Apply Rubric → Panel 4 | `evaluation-rubrics.md`, candidate data, `flowfuse-*-intel.md` | `panel-4-why-meeting.md` + `panel-4-reasoning.md` |

**D2.4 Integration Protocol:**
1. First apply Panel 4 rubric to candidate data
2. Layer in FlowFuse company/culture intel
3. Synthesize into meeting agenda items
4. Reasoning trace MUST show which insights came from which source

**Dependencies:** D2.0 runs first (pre-rubric). D2.1-D2.4 can run in parallel after D2.0 completes.

---

## Stream 3: Assembly & Output (Sequential after Stream 2)

| Drop | Task | Inputs | Outputs |
|------|------|--------|---------|
| **D3.1** | Quality Gate + Assembly | All panel content, all reasoning traces, `design-spec.md` | `assembled-content.md` + `quality-flags.md` |
| **D3.2** | Generate Gamma Page | `assembled-content.md`, `design-spec.md` | Gamma URL |
| **D3.3** | Generate PDF Fallback | `assembled-content.md` | `H-profile.pdf` |
| **D3.4** | Create Short Link | Gamma URL | short.io link |

**Quality Gate (D3.1):**
- Review all reasoning traces
- Flag any that appear thin/generic/boilerplate
- If flags exist, include in `quality-flags.md` for V review before proceeding
- Add "What This Report Assumes" footer with data sources and known gaps

---

## PII Handling

- Candidate name: **H.** (first initial only)
- Schools, companies: Keep as-is
- Contact info: Strip entirely
- Email, phone, LinkedIn URL: Remove

---

## Fallback Protocols

| Risk | Fallback |
|------|----------|
| FlowFuse research yields <3 useful signals | Flag in `flowfuse-culture-intel.md`, D2.4 adjusts Panel 4 to focus on "questions to explore" |
| Gamma API fails | Use PDF fallback (`H-profile.pdf`) |
| Short.io fails | Use raw Gamma URL |
| Candidate data has gaps | Name explicitly in "What This Report Assumes" footer |

---

## Drop Assignments

| Stream | Drops | Parallelizable |
|--------|-------|----------------|
| S1 (Setup) | D1.1, D1.2, D1.3, D1.4a | Yes (except D1.4b waits for D1.4a) |
| S2 (Analysis) | D2.0, D2.1, D2.2, D2.3, D2.4 | D2.0 first, then D2.1-D2.4 parallel |
| S3 (Assembly) | D3.1, D3.2, D3.3, D3.4 | Sequential |

**Total Drops:** 13

---

## Success Criteria

- [ ] Framework created *before* candidate data applied (audit trail proves this)
- [ ] All 4 panels have reasoning traces with evidence citations
- [ ] Design matches mycareerspan.com aesthetic
- [ ] Panel 1 stands alone (80% value test)
- [ ] Known gaps/assumptions explicitly named
- [ ] Final output: short.io link + PDF backup
- [ ] Quality gate passed (no thin reasoning flags, or flags reviewed by V)

---

## Checklist

### Stream 1: Setup & Framework
- [ ] D1.1: Design capture complete
- [ ] D1.2: FlowFuse company research complete
- [ ] D1.3: FlowFuse culture research complete (with thin-flag if needed)
- [ ] D1.4a: Panel purposes defined
- [ ] D1.4b: Evaluation rubrics defined

### Stream 2: Analysis & Content
- [ ] D2.0: Remarkable scan complete
- [ ] D2.1: Panel 1 (Thesis) complete with reasoning
- [ ] D2.2: Panel 2 (Hard Skills) complete with reasoning
- [ ] D2.3: Panel 3 (Differentiators) complete with reasoning
- [ ] D2.4: Panel 4 (Why Meeting) complete with reasoning

### Stream 3: Assembly & Output
- [ ] D3.1: Quality gate passed, content assembled
- [ ] D3.2: Gamma page generated
- [ ] D3.3: PDF fallback generated
- [ ] D3.4: Short link created

---

## Artifacts

All outputs saved to: `/home/workspace/N5/builds/careerspan-profile-output-v1/`

```
careerspan-profile-output-v1/
├── PLAN.md (this file)
├── jd.md (job description)
├── drops/
│   ├── D1.1-design-spec.md
│   ├── D1.2-flowfuse-company-intel.md
│   ├── D1.3-flowfuse-culture-intel.md
│   ├── D1.4a-panel-purposes.md
│   ├── D1.4b-evaluation-rubrics.md
│   ├── D2.0-remarkable-scan.md
│   ├── D2.1-panel-1-thesis.md
│   ├── D2.1-panel-1-reasoning.md
│   ├── D2.2-panel-2-hard-skills.md
│   ├── D2.2-panel-2-reasoning.md
│   ├── D2.3-panel-3-differentiators.md
│   ├── D2.3-panel-3-reasoning.md
│   ├── D2.4-panel-4-why-meeting.md
│   ├── D2.4-panel-4-reasoning.md
│   ├── D3.1-assembled-content.md
│   ├── D3.1-quality-flags.md
│   └── H-profile.pdf
└── output/
    ├── gamma-url.txt
    └── short-link.txt
```

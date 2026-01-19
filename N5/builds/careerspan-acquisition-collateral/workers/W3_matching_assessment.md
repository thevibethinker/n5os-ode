---
created: 2026-01-17
last_edited: 2026-01-17
version: 1.0
provenance: con_xxBgE2F5k5Q4AAo7
worker_id: W3
---

# Worker Brief: Matching/Assessment Positioning

**Pre-decided thread title:** `[careerspan-acquisition-collateral] W1.3: Matching/Assessment One-Pager`

---

## Your Task
Build the strongest possible argument for Careerspan as a **matching system / assessment alternative / vetting layer** for the hiring pipeline. This is an internal strategic document—not polished collateral.

---

## Context

### The Company
**Careerspan** is an AI-powered career coaching platform. The "product" being sold is effectively the team (V + Ilse) plus the technology.

### The Team
- **V (Vrijen Attawar)** — 10+ years career coaching experience, second-time founder
- **Logan Currie** — Harvard Ed School graduate, student leader of Project on Workforce at Harvard, workforce/education domain expertise
- **Ilse** — CTO, technical velocity, builder who ships

### The Metrics
- 4,000 signups, 1,500 fully activated users
- Average activated user: 2 stories (~40 min deep self-reflection)
- 35% completed 3+ stories (impressive retention signal)
- Partnerships: Peace Corps, Emory, Columbia, humanUPtions

### Technical Capability
- Multi-agent GPT-4 architecture
- AISS Framework (Action-Impact-Scale-Skill) for structured career narratives
- Story-based profiling: captures qualitative data assessments miss
- Semantic matching beyond keywords
- Role decomposition: breaks roles into competencies, maps candidate stories to gaps

### What's Been Proven
- Users actually do 40+ min of deep self-reflection (UX cracked)
- Matching tech works (Ilse's manual matching showed high accuracy)
- Story-based verification can detect inconsistencies (behavioral signals)

### HR Pipeline Position
**We target:** Vetting, Matching, Sourcing
**We do NOT target:** Validating/Verifying (background checks), Onboarding, Negotiation

---

## Your Positioning Angle: Matching / Assessment System

**The thesis:** Careerspan can serve as an alternative assessment layer or ATS enhancement that captures what traditional assessments miss—behavioral signals, soft skills, self-awareness.

**Why this matters to acquirers:**
- Traditional assessments (SHL, Pymetrics, Criteria) measure aptitude, not fit
- ATS keyword matching is broken (everyone games it)
- Quality-of-hire is THE metric everyone wants to predict but nobody can
- Careerspan captures behavioral data through coaching interactions that predicts success

**The Careerspan advantage:**
- Story-based profiling reveals what assessments miss (communication style, self-awareness, growth mindset)
- Behavioral signals: users who complete 3+ stories demonstrate follow-through, reflection capability
- AISS Framework provides structured, comparable output (not just vibes)
- Role decomposition maps stories to competencies (actual matching, not keyword matching)
- Pro-candidate framing means candidates engage authentically (vs. gaming assessments)

**Target acquirers for this angle:**
- Greenhouse/Lever/Ashby — ATS looking for differentiation
- iCIMS/SmartRecruiters — enterprise ATS needing AI layer
- Criteria/SHL/Pymetrics — assessments looking for qualitative capability
- HireVue — video interviewing + AI assessment
- Predictive Index — behavioral assessments

---

## MUST DO
1. Construct the strongest possible argument for this positioning
2. Name specific acquirer types and example companies (with why they'd care)
3. Articulate why story-based assessment is better than traditional approaches
4. Surface objections (why wouldn't this work?) and preemptively address them
5. Keep it internal quality—this is thinking scaffolding, not polished prose

## MUST NOT DO
- Do not cover internal mobility angles (that's W1)
- Do not cover sourcing/pipeline angles (that's W2)
- Do not polish for external audiences
- Do not invent metrics or claims not in this brief

## EXPECTED OUTPUT
A markdown file at `/home/workspace/Documents/Careerspan/internal_positioning_matching_assessment.md` containing:
1. **Thesis** (1-2 sentences)
2. **Why Now** (market context—assessments are broken, quality-of-hire unsolved)
3. **The Careerspan Advantage** (story-based signals, behavioral data)
4. **Target Acquirers** (specific companies + why they'd care)
5. **Objections & Rebuttals** (steelman the "no" and address it)
6. **Key Proof Points** (metrics, technical capability)

After creating the file, write a completion report to `/home/workspace/N5/builds/careerspan-acquisition-collateral/completions/W3.json` with:
```json
{
  "worker_id": "W3",
  "status": "complete",
  "output_file": "/home/workspace/Documents/Careerspan/internal_positioning_matching_assessment.md",
  "summary": "<2-3 sentence summary of the argument>",
  "key_insight": "<the single most compelling point>",
  "timestamp": "<ISO timestamp>"
}
```

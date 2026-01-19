---
created: 2026-01-17
last_edited: 2026-01-17
version: 1.0
provenance: con_xxBgE2F5k5Q4AAo7
worker_id: W2
---

# Worker Brief: Sourcing Tool Positioning

**Pre-decided thread title:** `[careerspan-acquisition-collateral] W1.2: Sourcing Tool One-Pager`

---

## Your Task
Build the strongest possible argument for Careerspan as a **talent sourcing / pipeline building tool** for recruiters, agencies, and platforms. This is an internal strategic document—not polished collateral.

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

### What's Been Proven
- Users actually do 40+ min of deep self-reflection (UX cracked)
- Matching tech works
- Communities invite Careerspan in and let them embed (Peace Corps, universities)
- The EMBEDDING model is proven—communities trust Careerspan to serve their members

---

## Your Positioning Angle: Sourcing Tool

**The thesis:** Careerspan is uniquely suited to build high-quality talent pipelines by embedding in communities and capturing signal at the source.

**Why this matters to acquirers:**
- Sourcing is broken (LinkedIn is pay-to-play, job boards are volume-not-quality)
- The best candidates are passive—they need a reason to engage
- Career coaching IS that reason: candidates get value, platform gets signal
- Community embedding gives access to pre-vetted populations (Peace Corps = service-minded, Emory = educated, etc.)

**The Careerspan advantage:**
- Proven community embedding model (Peace Corps, Emory, Columbia)
- Story-based profiles = richer signal than resume databases
- Candidates actively engage (40 min avg) vs. passive resume upload
- The same adaptability that works for communities works for recruiting agencies, Handshake-type platforms

**Target acquirers for this angle:**
- Handshake — campus recruiting, future talent pipeline
- Gem — sourcing automation, candidate engagement
- Greenhouse/Lever — ATS with sourcing add-ons
- Recruiting agencies (TrueBlue, Hudson Global) — better candidate quality
- Beamery — talent CRM, pipeline building
- Phenom — talent experience, employer branding + sourcing

---

## MUST DO
1. Construct the strongest possible argument for this positioning
2. Name specific acquirer types and example companies (with why they'd care)
3. Articulate the community embedding model and why it's hard to replicate
4. Surface objections (why wouldn't this work?) and preemptively address them
5. Keep it internal quality—this is thinking scaffolding, not polished prose

## MUST NOT DO
- Do not cover internal mobility angles (that's W1)
- Do not cover ATS/assessment angles (that's W3)
- Do not polish for external audiences
- Do not invent metrics or claims not in this brief

## EXPECTED OUTPUT
A markdown file at `/home/workspace/Documents/Careerspan/internal_positioning_sourcing_tool.md` containing:
1. **Thesis** (1-2 sentences)
2. **Why Now** (market context—sourcing is broken)
3. **The Careerspan Advantage** (community embedding, signal capture)
4. **Target Acquirers** (specific companies + why they'd care)
5. **Objections & Rebuttals** (steelman the "no" and address it)
6. **Key Proof Points** (partnerships, metrics, technical capability)

After creating the file, write a completion report to `/home/workspace/N5/builds/careerspan-acquisition-collateral/completions/W2.json` with:
```json
{
  "worker_id": "W2",
  "status": "complete",
  "output_file": "/home/workspace/Documents/Careerspan/internal_positioning_sourcing_tool.md",
  "summary": "<2-3 sentence summary of the argument>",
  "key_insight": "<the single most compelling point>",
  "timestamp": "<ISO timestamp>"
}
```

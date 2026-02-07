---
created: 2026-02-03
last_edited: 2026-02-03
version: 1.0
provenance: con_NJlvnFnzUY6KsX9t
name: candidate-synthesis
description: |
  Multi-step pipeline that synthesizes candidate intelligence into employer-focused narratives.
  Merges JD, Hiring POV, decomposer output, and resume to answer:
  (1) Should you take this meeting?
  (2) What would they bring to your team?
  (3) What should you probe?
  (4) What potential have we unveiled?
  
  Generates Hiring POV from JD if not found, stores in GDrive, links to Airtable.
  Outputs deduplicated, story-clustered content for meta-resume-generator.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  pipeline_version: "1.0"
---

# Candidate Synthesis Skill

## Purpose

This skill is the **intelligence layer** between raw Careerspan data and final candidate:decoded output. It answers: *"Given everything we know about this employer and candidate, what narrative best represents the candidate's fit and potential?"*

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CANDIDATE SYNTHESIS PIPELINE                     │
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐ │
│  │  STEP 1  │ → │  STEP 2  │ → │  STEP 3  │ → │  STEP 4  │ → │ STEP 5 │ │
│  │  Gather  │   │  POV Gen │   │ Story    │   │ Resume   │   │ Narrate│ │
│  │  Inputs  │   │ (if need)│   │ Cluster  │   │   Diff   │   │        │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └────────┘ │
│                                                                          │
│  INPUT: candidate_id (Airtable) OR decomposer_dir + employer_name       │
│  OUTPUT: SynthesizedNarrative JSON for meta-resume-generator            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Steps

### Step 1: Gather Inputs
**Script**: `scripts/step1_gather.py`

Fetches all required data:
- **From Airtable**: Candidate record → Job Opening → Employer → JD text
- **From GDrive**: Existing Hiring POV (if any)
- **From Local**: Decomposer output directory
- **From Airtable**: Resume attachment URL → download

**Output**: `gathered_inputs.json`

### Step 2: Generate/Validate Hiring POV
**Script**: `scripts/step2_hiring_pov.py`

If Hiring POV doesn't exist:
1. Generate from JD text via LLM
2. Save to GDrive: `Careerspan Pipeline Outputs/{Employer}/hiring-povs/{Role}_Hiring-POV.md`
3. Update Airtable Employer record: `Hiring POV (Gdrive)` field

If exists, validate it's current (JD hasn't changed significantly).

**Output**: `hiring_pov.json` (structured POV data)

### Step 3: Story Clustering
**Script**: `scripts/step3_cluster.py`

Groups skills by story dimension (not skill-by-skill):
1. Read all skills from `scores_complete.json`
2. Group by `support[].source` (story ID)
3. For each story cluster, synthesize `our_take` fields into unified narrative
4. Identify cross-cutting themes (e.g., "ownership mindset" appears in 3 stories)
5. Rank clusters by employer's valued story types (from Hiring POV)

**Output**: `story_clusters.json`

### Step 4: Resume Diff
**Script**: `scripts/step4_resume_diff.py`

Compares resume vs Careerspan findings:
1. Parse resume (PDF/text)
2. Extract claims from resume
3. Compare against skills with `evidence_type = "Story+profile"`
4. Identify:
   - **Substantiated**: Resume claimed it, Careerspan verified with story evidence
   - **Revealed**: Careerspan found it, resume didn't mention (hidden strengths)
   - **Unverified**: Resume claimed it, Careerspan couldn't verify (caution flags)
5. Identify **Potential**: Transferable skills not obvious from resume

**Output**: `resume_diff.json`

### Step 5: Narrative Generation
**Script**: `scripts/step5_narrate.py`

Generates the final employer-focused narrative:
1. **BLUF Verdict**: Should they take this meeting? (Score + 1-sentence why)
2. **What They Bring**: Story-clustered strengths, ordered by employer's priorities
3. **What to Probe**: Gaps/risks, prioritized by what employer cares about
4. **Unveiled Potential**: Transferable abilities revealed beyond resume

Uses LLM with Hiring POV context to frame everything in employer's language.

**Output**: `synthesized_narrative.json` (ready for meta-resume-generator)

## Usage

### Full Pipeline (from Airtable candidate)
```bash
python3 Skills/candidate-synthesis/scripts/run_pipeline.py \
  --candidate-id rec7JDWoSy94giKQX \
  --output-dir /path/to/output/
```

### Full Pipeline (from decomposer directory)
```bash
python3 Skills/candidate-synthesis/scripts/run_pipeline.py \
  --decomposer-dir Careerspan/meta-resumes/inbox/hardik-flowfuse/ \
  --employer-name "Docsum" \
  --output-dir /path/to/output/
```

### Individual Steps (for debugging)
```bash
# Step 1: Gather inputs
python3 scripts/step1_gather.py --candidate-id rec... --output gathered.json

# Step 2: Generate Hiring POV
python3 scripts/step2_hiring_pov.py --input gathered.json --output pov.json

# Step 3: Cluster stories
python3 scripts/step3_cluster.py --input gathered.json --pov pov.json --output clusters.json

# Step 4: Diff resume
python3 scripts/step4_resume_diff.py --input gathered.json --clusters clusters.json --output diff.json

# Step 5: Generate narrative
python3 scripts/step5_narrate.py --pov pov.json --clusters clusters.json --diff diff.json --output narrative.json
```

## Output Schema

### SynthesizedNarrative (Step 5 output)

```json
{
  "candidate": {
    "name": "Hardik",
    "role": "AI Engineer Candidate",
    "context": "Full Stack Developer (AI-focused) · FlowFuse"
  },
  
  "verdict": {
    "score": 89,
    "action": "Take This Meeting",
    "summary": "Founding-level AI platform builder with strong ownership signal. Key gaps are probeable.",
    "reasoning": "Matches 8/9 implicit filters. Strong evidence of 0→1 building. Only gap: async work style unverified."
  },
  
  "spikes": {
    "up": [
      {"label": "0→1 Platform Builder", "verified": "✓✓", "importance": 10},
      {"label": "Self-Directed Problem Finder", "verified": "✓✓", "importance": 9}
    ],
    "down": [
      {"label": "Async Experience Unknown", "verified": "✓", "importance": 7},
      {"label": "SOC 2 from Scratch", "verified": "~", "importance": 5}
    ]
  },
  
  "story_clusters": [
    {
      "theme": "Building from Zero",
      "story_ids": ["COKUmaqSITrBKdtxSgJp"],
      "narrative": "Led ML SaaS platform from founding stage to enterprise adoption (Apple, Samsung). Owned architecture, backend, frontend, and MLOps.",
      "skills_demonstrated": ["End-to-end delivery", "Technical architecture", "Stakeholder management"],
      "employer_relevance": "Directly maps to '0→1 experience' requirement and 'ownership mindset' trait signal."
    }
  ],
  
  "risks_to_probe": [
    {
      "risk": "Async-first work style",
      "priority": "high",
      "why_it_matters": "Employer filters for people comfortable with async. Resume shows enterprise background.",
      "probe_question": "How do you operate when no one assigns work and decisions are async?"
    }
  ],
  
  "unveiled_potential": {
    "substantiated_beyond_resume": [
      "Resume says 'built ML platform' — Careerspan verified with detailed story of architecture decisions, user adoption metrics, and stakeholder navigation."
    ],
    "revealed_beyond_resume": [
      "Problem-finding instinct: Both stories start with self-identified problems, not assigned tickets. Resume doesn't highlight this."
    ],
    "transferable_abilities": [
      "Stakeholder translation without PM buffer — directly transferable to FlowFuse's 'no PM' culture."
    ]
  },
  
  "interview_questions": [
    {
      "topic": "Async fit",
      "question": "How do you operate when no one assigns work and decisions are async?",
      "why": "Only unverified trait signal. Enterprise background may mean structured work expectations."
    }
  ],
  
  "signal_strength": {
    "story_verified": 78,
    "resume_only": 22,
    "inferred": 0
  },
  
  "methodology": "2 structured interviews · 45 skills assessed · Hiring POV alignment scoring"
}
```

## Integration Points

### Airtable
- **Base**: Candidate Tracker (`appd12asvg42woz9I`)
- **Tables**: Employers, Job Openings, Candidates
- **Field to update**: `Hiring POV (Gdrive)` on Employers table

### Google Drive
- **Parent folder**: `Careerspan Pipeline Outputs` (`1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM`)
- **Structure**: `{Employer}/hiring-povs/{Role}_Hiring-POV.md`

### Meta Resume Generator
- Output of this skill feeds directly to `Skills/meta-resume-generator/`
- The `synthesized_narrative.json` replaces manual JSON crafting

## GDrive & Airtable Integration

### Hiring POV Storage

When a Hiring POV is generated (Step 2), it is:

1. **Uploaded to GDrive** at:
   ```
   Careerspan Pipeline Outputs/
   └── {Employer-Name}/
       └── hiring-povs/
           └── {Role-Title}_Hiring-POV.md
   ```
   
   - Parent folder ID: `1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM` (Careerspan Pipeline Outputs)
   - Template structure: `1QqRfGTcZnBnw9AbRHGzyKNThW6mJ1XrK` (_TEMPLATE_EMPLOYER)

2. **Linked in Airtable** (Candidate Tracker):
   - Base: `appd12asvg42woz9I`
   - Table: `Job Openings` (`tblHgSEOsoegYnJl7`)
   - Field: `Hiring POV (Gdrive)` — URL to the GDrive file

### Sync Script

Use `scripts/gdrive_airtable_sync.py` to manually sync:

```bash
python3 scripts/gdrive_airtable_sync.py \
  --job-opening-id recXUiOL1iOWm9Y9F \
  --pov-file /path/to/hiring_pov.json \
  --employer-name "Docsum" \
  --role-title "Founding Full Stack Engineer"
```

The script outputs instructions for Zo to execute (since it needs app integration tools).

### Automatic Sync

During pipeline execution, Zo handles the GDrive upload and Airtable linking automatically via app integration tools. The pipeline orchestrator (`run_pipeline.py`) includes these steps.

## Files

```
Skills/candidate-synthesis/
├── SKILL.md                    # This file
├── scripts/
│   ├── run_pipeline.py         # Main orchestrator
│   ├── step1_gather.py         # Input collection
│   ├── step2_hiring_pov.py     # POV generation
│   ├── step3_cluster.py        # Story clustering
│   ├── step4_resume_diff.py    # Resume comparison
│   └── step5_narrate.py        # Final narrative
├── references/
│   └── hiring_pov_schema.json  # Schema for Hiring POV structure
└── assets/
    └── prompts/                # LLM prompts for each step
        ├── generate_pov.md
        ├── cluster_stories.md
        ├── diff_resume.md
        └── narrate.md
```

## Dependencies

- Python 3.12+
- Zo app tools (Airtable, Google Drive)
- `/zo/ask` API for LLM calls
- PyYAML, requests

## Relationship to Other Skills

- **Upstream**: `careerspan-decomposer` (provides structured skill data)
- **Upstream**: `careerspan-jd-intake` (provides JD in Airtable)
- **Downstream**: `meta-resume-generator` (consumes synthesized narrative)

---
created: 2026-02-03
last_edited: 2026-02-03
version: 1.0
provenance: con_NJlvnFnzUY6KsX9t
build_slug: meta-resume-v2
drop_id: D2
drop_title: Pipeline Test - Hardik x Docsum
spawn_mode: auto
---

# Drop 2: Test Candidate Synthesis Pipeline

## Context

We've built a new `candidate-synthesis` skill that creates employer-focused narratives from multiple data sources. Need to test it end-to-end with real data.

**Test Case**: Hardik (candidate) × Docsum (employer) / Founding Full Stack Engineer (role)

## Data Locations

### Airtable (Candidate Tracker base: `appd12asvg42woz9I`)
- **Employer**: Docsum (`recPBAWERVQQog01J`) in table `tblvIfVUHxzuBQ2WB`
- **Job Opening**: Founding Full Stack Engineer (`recXUiOL1iOWm9Y9F`) in table `tblHgSEOsoegYnJl7`
- **Candidate**: Hardik in table `tblWB2mGbioA8pLBL`

### Local Files
- **Decomposer output**: `/home/workspace/Careerspan/meta-resumes/inbox/hardik-flowfuse/`
- **Existing Hiring POV**: `/home/workspace/Careerspan/resumes/inbox/docsum/HIRING_POV.json`
- **Resume**: Check Airtable record or `/home/workspace/Careerspan/resumes/`

### GDrive
- **Pipeline Outputs folder**: `1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM`
- **Hiring POVs template folder**: `1pVRd5WuK1la-IQyKn66U6EdDKRYd1rdQ`

## Task

Run the candidate-synthesis pipeline step by step and report results.

### Step 1: Gather Inputs
```bash
cd /home/workspace/Skills/candidate-synthesis/scripts
python3 step1_gather.py \
  --candidate-slug "hardik" \
  --employer-slug "docsum" \
  --decomposer-dir "/home/workspace/Careerspan/meta-resumes/inbox/hardik-flowfuse" \
  --output /tmp/synthesis/gathered.json
```

If step1 fails due to missing Airtable integration, manually construct gathered.json from:
- Airtable records (use `use_app_airtable` tools)
- Local decomposer files
- Existing HIRING_POV.json

### Step 2: Ensure Hiring POV
```bash
python3 step2_hiring_pov.py \
  --input /tmp/synthesis/gathered.json \
  --output /tmp/synthesis/hiring_pov.json
```

Since we already have `/home/workspace/Careerspan/resumes/inbox/docsum/HIRING_POV.json`, this should use existing.

### Step 3: Cluster Stories
```bash
python3 step3_cluster.py \
  --input /tmp/synthesis/gathered.json \
  --pov /tmp/synthesis/hiring_pov.json \
  --output /tmp/synthesis/clusters.json
```

### Step 4: Resume Diff
```bash
python3 step4_resume_diff.py \
  --input /tmp/synthesis/gathered.json \
  --output /tmp/synthesis/resume_diff.json
```

### Step 5: Generate Narrative
```bash
python3 step5_narrate.py \
  --input /tmp/synthesis/gathered.json \
  --pov /tmp/synthesis/hiring_pov.json \
  --clusters /tmp/synthesis/clusters.json \
  --diff /tmp/synthesis/resume_diff.json \
  --output /tmp/synthesis/narrative.json
```

## Expected Output

A `narrative.json` file with structure:
```json
{
  "candidate": { "name": "Hardik", "role": "...", "context": "..." },
  "verdict": { "score": 89, "action": "Take This Meeting", "summary": "..." },
  "spikes": { "up": [...], "down": [...] },
  "what_they_bring": [...],
  "risks_to_probe": [...],
  "unveiled_potential": { "substantiated": [...], "revealed": [...], "transferable": [...] },
  "interview_questions": [...],
  "signal_strength": { "story_verified": 78, "resume_only": 22, "inferred": 0 }
}
```

## Validation Checklist

- [ ] All 5 steps complete without errors
- [ ] `narrative.json` has all required fields
- [ ] Spikes are deduplicated (no repetitive skill names)
- [ ] Story clusters show themes, not skill lists
- [ ] Resume diff shows clear substantiated vs revealed split
- [ ] Output is ready for meta-resume-generator consumption

## Deposit

Write results to: `N5/builds/meta-resume-v2/deposits/D2-deposit.md`

Include:
- Step-by-step execution log
- Any errors encountered and fixes applied
- Sample output from each step
- Final narrative.json (or path to it)
- Assessment: Is the synthesis working? What needs refinement?

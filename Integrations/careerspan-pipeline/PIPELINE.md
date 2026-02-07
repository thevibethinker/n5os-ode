---
created: 2026-02-02
last_edited: 2026-02-02
version: 1
provenance: con_jbT41XzWsZ2W6Odn
---
# Careerspan Pipeline - Full Flow

## Overview

This pipeline integrates three components:
1. **Pipeline Orchestrator** (`Integrations/careerspan-pipeline/`) — Email monitoring, Airtable tracking, task queue
2. **Candidate Guide Generator** (`Skills/careerspan-candidate-guide/`) — Pre-Careerspan: JD + Resume → Hiring POV + Candidate Guide
3. **Careerspan Decomposer** (`Skills/careerspan-decomposer/`) — Post-Careerspan: Intelligence Brief → Structured YAML → Meta-Resume

## Full Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 1: JD INTAKE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [JD] Email from Shivam                                                     │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │ Pipeline        │──► Extract JD content                                  │
│  │ Orchestrator    │──► Create Airtable: Job Opening + Employer             │
│  │                 │──► Store JD locally                                    │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐     Optional POV Refinement                           │
│  │ careerspan-     │◄─── If JD is unclear or missing key info              │
│  │ candidate-guide │                                                        │
│  │ (decompose_jd)  │──► Generate HIRING_POV v0 (internal)                  │
│  └────────┬────────┘──► Surface 5 Core Questions                           │
│           │                                                                 │
│           ▼                                                                 │
│  [Zo→Shivam] "Here's my read + questions..."                               │
│  [Shivam→Employer] Forwards questions                                       │
│  [Employer→Shivam] Answers (1-2 rounds max)                                │
│  [UPDATE] from Shivam with answers                                          │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Finalize        │──► Update HIRING_POV.md                               │
│  │ Hiring POV      │──► Upload PDF to GDrive: /{employer}/hiring-povs/     │
│  │                 │──► Update Airtable: Intake Status = "Finalized"       │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: CANDIDATE RESPONSE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Shivam broadcasts JD to his network                                        │
│  Candidates respond with interest + resume                                  │
│         │                                                                   │
│         ▼                                                                   │
│  [RESUME] Email from Shivam                                                 │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │ Pipeline        │──► Extract resume attachment                           │
│  │ Orchestrator    │──► Create Airtable: Candidate record                  │
│  │                 │──► Link to Job Opening                                │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ careerspan-     │◄─── JD + Resume                                       │
│  │ candidate-guide │                                                        │
│  │ (generate)      │──► Generate {Name}_Guide.md/pdf                       │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Upload to       │──► GDrive: /{employer}/candidates/{name}/             │
│  │ Google Drive    │──► {Name}_Guide.pdf                                   │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  [Zo→Shivam] "Guide ready: {link}"                                         │
│  Shivam sends Guide + Careerspan invite to candidate                       │
│  Update Airtable: Status = "Invited to Careerspan"                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: CAREERSPAN COMPLETION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Candidate completes Careerspan Stories                                     │
│  Careerspan generates Intelligence Brief                                    │
│         │                                                                   │
│         ▼                                                                   │
│  Intelligence Brief available (PDF/OCR or API JSON)                        │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │ careerspan-     │◄─── Intelligence Brief + JD                           │
│  │ decomposer      │                                                        │
│  │                 │──► Structured YAML files                              │
│  │                 │──► scores_complete.json                               │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  Output to: Careerspan/meta-resumes/inbox/{candidate}-{company}/           │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────┐                                                        │
│  │ meta-resume-    │◄─── Structured YAML                                   │
│  │ generator       │                                                        │
│  │                 │──► {Name}_Meta-Resume.pdf                             │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Upload to       │──► GDrive: /{employer}/candidates/{name}/             │
│  │ Google Drive    │──► {Name}_Meta-Resume.pdf                             │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           ▼                                                                 │
│  [Zo→Shivam] "Meta-Resume ready: {link}"                                   │
│  Shivam submits to employer                                                │
│  Update Airtable: Status = "Submitted to Employer"                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Skill Integration Points

### 1. careerspan-candidate-guide

**When triggered:**
- Phase 1: JD intake → `decompose_jd.py` for Hiring POV
- Phase 2: Resume intake → `generate_guides.py` for Candidate Guide

**Inputs:**
- JD text file (stored by pipeline at intake)
- Resume PDF (extracted from [RESUME] email)
- CTA link (Careerspan invite URL)

**Outputs:**
- `HIRING_POV.md` → Internal use + GDrive
- `{Name}_Guide.pdf` → GDrive + sent to candidate via Shivam

**Pipeline integration:**
```python
# In pipeline_orchestrator.py process_resume()
from pathlib import Path
import subprocess

def generate_candidate_guide(jd_path, resume_path, output_dir, company, role, cta):
    """Call careerspan-candidate-guide skill."""
    cmd = [
        "python3", "Skills/careerspan-candidate-guide/scripts/generate_guides.py",
        "--jd-file", str(jd_path),
        "--resumes", str(resume_path),
        "--output", str(output_dir),
        "--company", company,
        "--role", role,
        "--cta", cta,
        "--format", "both"
    ]
    subprocess.run(cmd, check=True)
```

### 2. careerspan-decomposer

**When triggered:**
- Phase 3: After candidate completes Careerspan
- Triggered by: [UPDATE] email with "Careerspan complete" or direct invocation

**Inputs:**
- Careerspan Intelligence Brief (OCR text or structured JSON from API)
- JD YAML (already stored from Phase 1)

**Outputs:**
- Structured YAML files in `Careerspan/meta-resumes/inbox/{candidate}-{company}/`
- `scores_complete.json` with all skill assessments

**Pipeline integration:**
```python
# In pipeline_orchestrator.py process_careerspan_complete()
def decompose_intelligence_brief(doc_path, jd_path, candidate_slug, company_slug):
    """Call careerspan-decomposer skill."""
    cmd = [
        "python3", "Skills/careerspan-decomposer/scripts/decompose.py",
        "--doc", str(doc_path),
        "--jd", str(jd_path),
        "--candidate", candidate_slug,
        "--company", company_slug
    ]
    subprocess.run(cmd, check=True)
    
    # Output will be at:
    return Path(f"Careerspan/meta-resumes/inbox/{candidate_slug}-{company_slug}/")
```

## Airtable Status Progression

### Job Opening Status
```
New → POV Refinement → Finalized → Broadcasted → Candidates Responding → Active → Closed
       (optional)
```

### Candidate Status
```
Interested → Invited to Careerspan → Careerspan Complete → Submitted to Employer → Interviewing → Offered/Hired/Rejected
```

## File Storage Locations

| Type | Local Path | Google Drive Path |
|------|------------|-------------------|
| JD (raw) | `Integrations/careerspan-pipeline/processed/{job_id}/jd.txt` | - |
| Hiring POV | `Integrations/careerspan-pipeline/processed/{job_id}/HIRING_POV.md` | `/{employer}/hiring-povs/{role}_hiring-pov.pdf` |
| Resume | `Integrations/careerspan-pipeline/processed/{job_id}/candidates/{name}/resume.pdf` | - |
| Candidate Guide | `Integrations/careerspan-pipeline/processed/{job_id}/candidates/{name}/{Name}_Guide.pdf` | `/{employer}/candidates/{name}/{Name}_Guide.pdf` |
| Intelligence Brief | `Careerspan/meta-resumes/inbox/{candidate}-{company}/careerspan_full_ocr.txt` | - |
| Decomposed YAML | `Careerspan/meta-resumes/inbox/{candidate}-{company}/*.yaml` | - |
| Meta-Resume | `Careerspan/meta-resumes/inbox/{candidate}-{company}/{Name}_Meta-Resume.pdf` | `/{employer}/candidates/{name}/{Name}_Meta-Resume.pdf` |

## Email Tags Summary

| Tag | Trigger | Action |
|-----|---------|--------|
| `[JD]` | New job description | Create Job Opening, start intake flow |
| `[RESUME]` | Candidate response | Create Candidate, generate Guide |
| `[UPDATE]` | General update | Parse body, update relevant record |

## Zo Communication Rules

1. **Only email Shivam** — Never employers or candidates directly
2. **Separate thread** — Never reply in employer/candidate threads
3. **One thread per topic** — Subject: `[Zo] {type}: {role} @ {company}`
4. **Identify as Zo** — Shivam knows it's automated
5. **Silent observer** — Watch all traffic, act only when needed

## Related Skills

- `file 'Skills/careerspan-candidate-guide/SKILL.md'` — Guide generation
- `file 'Skills/careerspan-decomposer/SKILL.md'` — Intelligence Brief processing
- `file 'Skills/meta-resume-generator/SKILL.md'` — Meta-Resume PDF generation
- `file 'Skills/branded-pdf/SKILL.md'` — PDF styling for all outputs

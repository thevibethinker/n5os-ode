---
created: 2026-02-02
last_edited: 2026-02-02
version: 2.1
provenance: con_jbT41XzWsZ2W6Odn
---

# Careerspan Pipeline

Automated JD intake, candidate management, and Careerspan orchestration for the CorridorX partnership.

**Full flow diagram:** See `file 'Integrations/careerspan-pipeline/PIPELINE.md'`

## Quick Start

```bash
# Check status
python3 scripts/pipeline_orchestrator.py status

# Test with sample JD
python3 scripts/pipeline_orchestrator.py test --type jd

# Test with sample resume
python3 scripts/pipeline_orchestrator.py test --type resume

# Generate candidate guide (via skill)
python3 scripts/pipeline_orchestrator.py generate-guide \
  --jd /path/to/jd.txt \
  --resume /path/to/resume.pdf \
  --output /path/to/output \
  --company "Company" \
  --role "Role"

# Decompose Careerspan brief (via skill)
python3 scripts/pipeline_orchestrator.py decompose \
  --doc /path/to/brief.txt \
  --jd /path/to/jd.yaml \
  --candidate "firstname" \
  --company "company"
```

## Architecture

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Pipeline Orchestrator** | `scripts/pipeline_orchestrator.py` | Email monitoring, task queue, Airtable sync |
| **Candidate Guide Skill** | `Skills/careerspan-candidate-guide/` | JD + Resume → Hiring POV + Candidate Guide |
| **Decomposer Skill** | `Skills/careerspan-decomposer/` | Intelligence Brief → Structured YAML |
| **Meta-Resume Skill** | `Skills/meta-resume-generator/` | Structured YAML → PDF |

### Flow Phases

1. **[JD] Intake** → Extract JD, create Airtable record, optional POV refinement
2. **[RESUME] Response** → Generate Candidate Guide, invite to Careerspan
3. **Careerspan Complete** → Decompose brief, generate Meta-Resume, submit

## Zo's Role

**Silent observer** that:
- Monitors all Shivam email traffic (tags: `[JD]`, `[RESUME]`, `[UPDATE]`)
- Only emails Shivam directly (never employers/candidates)
- Maintains one thread per topic: `[Zo] {type}: {role} @ {company}`
- Uses `/zo/ask` for parallel processing (Pulse patterns)

## Email Tags

| Tag | Action |
|-----|--------|
| `[JD]` | New job description → intake flow |
| `[RESUME]` | Candidate response → guide generation |
| `[UPDATE]` | General update → parse and route |

## Google Drive

**Shared folder:** [Careerspan Pipeline Outputs](https://drive.google.com/drive/folders/1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM)

Structure:
```
Careerspan Pipeline Outputs/
├── {employer-slug}/
│   ├── hiring-povs/
│   │   └── {role}_hiring-pov.pdf
│   └── candidates/
│       └── {candidate}/
│           ├── {Name}_Guide.pdf
│           └── {Name}_Meta-Resume.pdf
```

## Airtable

**Base:** Careerspan Candidate Tracker (`appd12asvg42woz9I`)

Tables:
- **Job Openings** — Roles with intake status, POV tracking
- **Candidates** — Linked to jobs, status progression
- **Employers** — Company info, Drive folder links

## Configuration

`config.yaml` contains:
- Airtable base/table IDs
- Google Drive folder IDs
- 5 Core Questions for POV refinement
- Email tags and routing rules
- Workflow status definitions

## Setup Checklist

- [x] Config file created
- [x] Google Drive folder created
- [x] Skills integrated (candidate-guide, decomposer, meta-resume)
- [x] Shivam access rule created
- [ ] Airtable schema updated (manual step)
- [ ] Drive folder shared with Shivam
- [ ] Heartbeat agent created (when ready)

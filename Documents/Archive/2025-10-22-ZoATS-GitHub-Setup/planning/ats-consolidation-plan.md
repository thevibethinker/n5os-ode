# ATS Consolidation Plan

## Objective
Consolidate ALL ATS functionality into `/home/workspace/ZoATS/` for GitHub distribution as n5-ats

## Current State Analysis

### Already in ZoATS ✅
```
ZoATS/
├── workers/              # Candidate processing
│   ├── candidate_intake/
│   ├── dossier/
│   ├── scoring/
│   └── parser/
├── jobs/                 # Job + candidate data
├── pipeline/             # Orchestration
├── inbox_drop/          # Email intake
└── docs/                # Ethics, roadmap
```

### Scattered in N5 (NEEDS CONSOLIDATION)
```
N5/commands/
├── jobs-add.md
├── jobs-review.md
├── jobs-scrape.md
├── job-source-extract.md
└── job-source.md

N5/scripts/
└── n5_job_source_extract.py

N5/config/
└── job_sourcing.json
```

### In Careerspan (REFERENCE ONLY)
```
Careerspan/Jobs/         # User's job data (don't move)
```

## Consolidation Actions

### 1. Move Commands → ZoATS/commands/
```bash
mkdir -p ZoATS/commands
cp N5/commands/jobs-*.md ZoATS/commands/
cp N5/commands/job-*.md ZoATS/commands/
```

### 2. Move Scripts → ZoATS/scripts/
```bash
mkdir -p ZoATS/scripts
cp N5/scripts/n5_job_source_extract.py ZoATS/scripts/
```

### 3. Move Config → ZoATS/config/
```bash
mkdir -p ZoATS/config
cp N5/config/job_sourcing.json ZoATS/config/
```

### 4. Update Command Registry
Create `ZoATS/config/commands.jsonl` with ATS-specific commands

### 5. Add Schemas
```bash
mkdir -p ZoATS/schemas
# Create: candidate.schema.json, job.schema.json, scoring.schema.json
```

## Final ZoATS Structure
```
ZoATS/
├── README.md
├── install.sh            # Auto-installs n5-core first
├── VERSION
├── commands/             # ATS commands (5 files)
├── scripts/              # ATS scripts
├── schemas/              # ATS schemas
├── config/               # ATS config
│   ├── commands.jsonl
│   └── job_sourcing.json
├── workers/              # Processing workers
├── pipeline/             # Orchestration
├── jobs/                 # Runtime data
├── inbox_drop/          # Intake
└── docs/                # Documentation
```

## Dependency Model
```
n5-ats (ZoATS)
  ↓ depends on
n5-core (foundation)
```

Install flow:
1. User runs: `curl -sSL .../n5-ats/install.sh | bash`
2. Script checks for n5-core, installs if missing
3. Then installs n5-ats on top

## Post-Consolidation Cleanup
- Update N5/config/commands.jsonl to remove job commands (point to ZoATS)
- Add alias commands that delegate to ZoATS
- Document migration path for existing users

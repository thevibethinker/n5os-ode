---
name: aviato
description: Aviato enrichment skill for person/company lookup and CRM-ready mapping.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
created: 2026-03-02
last_edited: 2026-03-02
version: 1
provenance: con_OWM13NmYTfck3QFq
---
# Aviato

Package Aviato enrichment capabilities as a reusable skill.

## What it does
- Enriches people via Aviato (`person/enrich`)
- Enriches companies via Aviato (`company/enrich`)
- Maps raw Aviato payloads into CRM-friendly fields
- Supports simple stakeholder workflow (person + current company)

## Requirements
- Set secret env var: `AVIATO_N5OS_V2_KEY`
- Optional: `AVIATO_API_BASE_URL` (defaults to `https://data.api.aviato.co`)
- Python dependency: `requests`

## Commands

```bash
python3 Skills/aviato/scripts/aviato.py --help

# Live enrichment (API key required)
python3 Skills/aviato/scripts/aviato.py person --email "name@company.com"
python3 Skills/aviato/scripts/aviato.py person --linkedin-url "https://linkedin.com/in/someone"
python3 Skills/aviato/scripts/aviato.py company --website "example.com"

# Full workflow (person + current company + highlights)
python3 Skills/aviato/scripts/aviato.py stakeholder --email "name@company.com"

# Transform existing Aviato JSON payloads to CRM format
python3 Skills/aviato/scripts/aviato.py map-person --input path/to/person.json
python3 Skills/aviato/scripts/aviato.py map-company --input path/to/company.json
```

## Output behavior
- Prints JSON to stdout by default
- Use `--out <path>` to write output JSON to a file

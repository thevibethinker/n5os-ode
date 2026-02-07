---
name: careerspan-resume-intake
description: |
  Processes [RESUME] tagged emails for the Careerspan pipeline. Extracts candidate info, 
  matches to Job Openings in Airtable, creates Candidate records, generates Candidate Guides,
  uploads to Google Drive, and emails Shivam with summary. Part of the CorridorX × Careerspan
  talent matching automation. LLM-first: semantic extraction via /zo/ask, Python for orchestration.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  pipeline: careerspan
---

# Careerspan Resume Intake

## Purpose

When Shivam forwards a resume with `[RESUME]` tag, this skill:

1. Extracts candidate info (name, email, resume content)
2. Matches to an existing Job Opening in Airtable
3. Creates a Candidate record in Airtable
4. Generates a Candidate Guide PDF
5. Uploads to the shared Google Drive folder
6. Emails Shivam with summary and Drive link

## Usage

```bash
python3 Skills/careerspan-resume-intake/scripts/process_resume.py \
  --email-subject "Fwd: [RESUME] John Doe for Senior Engineer" \
  --email-body "Forwarding resume..." \
  --email-from "shivam@corridorx.io" \
  --attachments "/tmp/resume.pdf" \
  [--job-opening-id "recXXX"]  # Optional, if known
  [--dry-run]                   # Preview without creating records
```

## Job Matching Logic

The script uses LLM to match candidates to job openings:

1. Extracts company/role hints from email subject and body
2. Queries Airtable Job Openings for active roles
3. Uses LLM to score matches based on:
   - Company name alignment
   - Role title similarity
   - Resume skills vs JD requirements
4. Returns confidence level: `high`, `medium`, `low`
5. If `low` confidence or no match, flags for manual review

## Airtable Integration

- **Base:** Careerspan Candidate Tracker (`appd12asvg42woz9I`)
- **Candidates table:** `tblWB2mGbioA8pLBL`
- **Job Openings table:** `tblHgSEOsoegYnJl7`
- **Account:** `vrijen@mycareerspan.com`

## Output Format

```json
{
  "candidate_id": "recXXX",
  "candidate_name": "John Doe",
  "candidate_email": "john@example.com",
  "job_opening_id": "recYYY",
  "job_match_confidence": "high",
  "candidate_guide_path": "/tmp/guides/John_Doe_Guide.pdf",
  "candidate_guide_link": "https://drive.google.com/file/d/...",
  "email_sent": true,
  "flags": []
}
```

## Dependencies

- PyMuPDF (for PDF text extraction)
- requests (for /zo/ask API)
- yaml (for config parsing)

## Files

- `scripts/process_resume.py` — Main processing script
- `SKILL.md` — This documentation

## Related

- `Skills/careerspan-candidate-guide/` — Used to generate candidate guides
- `Integrations/careerspan-pipeline/config.yaml` — Central configuration
- `Integrations/careerspan-pipeline/scripts/drive_upload.py` — Drive upload helper

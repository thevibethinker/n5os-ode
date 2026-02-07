---
name: careerspan-jd-intake
description: |
  Processes [JD] tagged emails from Shivam and executes the full JD intake flow. Extracts JD content,
  creates Job Opening in Airtable, generates Hiring POV, uploads to Drive, and emails Shivam with
  results and any missing Core Questions. Uses /zo/ask for LLM semantic extraction and Zo's app
  integration tools for Airtable, Drive, and Gmail.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
---

# Careerspan JD Intake Skill

## Purpose

This skill handles the initial intake of job descriptions (JDs) sent by Shivam with the `[JD]` tag. It automates the following:

1. **Extract JD content** from email attachment using LLM semantic analysis
2. **Create Job Opening record** in Airtable with initial status
3. **Generate Hiring POV** document summarizing what matters most to the hiring manager
4. **Upload to Drive** in the shared folder structure
5. **Email Shivam** with the POV link and request for any missing Core Questions

## Usage

### Prerequisites

- Ensure config.yaml in `Integrations/careerspan-pipeline/` has valid Airtable and Drive settings
- The script uses Zo's app integration tools (Airtable, Google Drive, Gmail)

### Running the Skill

```bash
python3 Skills/careerspan-jd-intake/scripts/process_jd.py \
  --email-subject "[JD] Senior Engineer @ TechCorp" \
  --email-body "Here's the JD for the Senior Engineer role..." \
  --email-from "shivam@corridorx.io" \
  --attachments "/path/to/jd.pdf" \
  [--dry-run]
```

### Arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `--email-subject` | Yes | The email subject line (should contain [JD] tag) |
| `--email-body` | Yes | The email body text |
| `--email-from` | Yes | The sender's email address |
| `--attachments` | No | Path(s) to attached JD file(s) (PDF, text, or docx) |
| `--dry-run` | No | If set, prints what would happen without executing |

## Output

The script outputs a JSON object with:

```json
{
  "job_opening_id": "rec...",
  "company": "Company Name",
  "role": "Role Title",
  "hiring_pov_link": "https://drive.google.com/...",
  "missing_core_questions": ["salary_range", "anti_pattern"],
  "email_sent": true,
  "email_thread_id": "..."
}
```

## 5 Core Questions

Every JD needs answers to these before it's "finalized":

1. **Salary range** (and whether it's hidden from candidates)
2. **Location constraints** (geo, remote, timezone)
3. **Visa sponsorship** (yes/no/required auth)
4. **90-day success criteria**
5. **Anti-pattern** (who should NOT apply)

If a JD is missing answers, the skill sends Shivam a request for clarification.

## Architecture

**Python handles:**
- Argument parsing and validation
- File I/O (reading attachments)
- Config loading
- JSON output formatting

**LLM handles (via /zo/ask):**
- JD semantic analysis (company, role, requirements extraction)
- Hiring POV generation
- Core questions assessment (what's missing from the JD)

**Zo app tools handle:**
- Airtable record creation via `use_app_airtable`
- Google Drive upload via `use_app_google_drive`
- Email sending via `use_app_gmail`

## Files

- `scripts/process_jd.py` — Main entry point for JD intake processing

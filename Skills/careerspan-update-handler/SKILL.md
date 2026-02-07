---
name: careerspan-update-handler
description: Process [UPDATE] tagged emails from Shivam and update Airtable accordingly. Classifies update type via LLM and takes appropriate action.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
---

# Careerspan Update Handler

Process `[UPDATE]` tagged emails from Shivam and update Airtable records accordingly.

## When to Use

When Shivam sends an `[UPDATE]` email that contains:
- Employer answered Core Questions
- Candidate status changed
- Role paused/closed
- General intel update

## Entry Point

```bash
python3 Skills/careerspan-update-handler/scripts/process_update.py \
  --email-subject "..." \
  --email-body "..." \
  --email-from "..." \
  [--dry-run]
```

## Update Types

| Type | Target | Example | Actions |
|------|--------|---------|---------|
| `employer_response` | Job Opening | "Confirmed salary is $180-220k" | Update Core Question fields, possibly refresh Hiring POV |
| `candidate_status` | Candidate | "Jane Doe had first interview, going to round 2" | Update status field |
| `role_status` | Job Opening | "TechCorp role is paused" | Update intake_status, ball_in_court |
| `general_intel` | Any | "Employer prefers async workers" | Add to notes field |

## Classification

Uses LLM (`/zo/ask`) to classify the update:

```
Given this email, classify the update type and extract the relevant information:

Email: {email_body}

Output JSON:
{
  "update_type": "employer_response|candidate_status|role_status|general_intel",
  "target_record_type": "job_opening|candidate|employer",
  "target_identifier": "company name or candidate name",
  "updates": {
    "field_name": "value"
  },
  "requires_response": boolean,
  "suggested_response": "..."
}
```

## Output

```json
{
  "update_type": "...",
  "records_updated": [
    {"table": "job_openings", "id": "rec...", "fields_updated": ["salary_min", "salary_max"]}
  ],
  "hiring_pov_refreshed": false,
  "email_sent": false
}
```

## Special Case: Core Questions Answered

If `update_type == "employer_response"` and Core Questions are now complete:
1. Update all checkbox fields
2. Optionally regenerate Hiring POV with new info
3. Update status to "Finalized" if all 5 answered
4. Email Shivam confirming completion

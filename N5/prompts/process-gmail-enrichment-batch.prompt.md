---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
title: Process Gmail Enrichment Batch
description: Process pending Gmail enrichment requests using use_app_gmail tool
tags: [crm, gmail, batch, enrichment]
tool: true
---

# Process Gmail Enrichment Batch

## Mission
Process all pending Gmail enrichment requests in `N5/data/gmail_enrichment_requests/` using `use_app_gmail` tool.

## Process

### Step 1: List Pending Requests
```bash
ls -1 /home/workspace/N5/data/gmail_enrichment_requests/profile_*_gmail.json | grep -v '.completed'
```

### Step 2: For Each Request
1. Read request JSON
2. Extract email address
3. Call `use_app_gmail` with:
   - tool_name: `gmail-find-email`
   - configured_props: `{"q": "from:{email} OR to:{email}", "maxResults": 10, "withTextPayload": true}`
   - email: "attawar.v@gmail.com" (or vrijen@mycareerspan.com based on context)

### Step 3: Analyze Results
Use LLM intelligence to:
- Count total messages
- Extract subjects and dates
- Identify communication patterns
- Generate intelligence summary

### Step 4: Append to Profile YAML
Use `edit_file_llm` to append intelligence block to profile's YAML:

```yaml
### YYYY-MM-DD HH:MM | gmail_enrichment
**Source:** Gmail thread analysis

**Gmail Thread Analysis:**

Found X message(s) with {email}:

  1. "Subject" (YYYY-MM-DD)
     → Snippet...
  2. "Subject" (YYYY-MM-DD)
     → Snippet...

**Communication Pattern:** [Analysis]
```

### Step 5: Mark Request Complete
Rename request file: `profile_X_gmail.json` → `profile_X_gmail.json.completed`

## Error Handling
- Gmail not found: Append "No Gmail threads found"
- Gmail API error: Log error, keep request pending
- YAML write error: Log error, keep request pending

## Success Criteria
- All pending requests processed
- Gmail intelligence appended to YAML files
- Request files marked complete
- No stub warnings in output

## Output
Report:
- X/Y requests processed successfully
- List any errors
- Sample of enriched intelligence


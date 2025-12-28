---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
title: CRM Gmail Enrichment
description: Search Gmail for threads with a contact and format intelligence for CRM profile
tags: [crm, gmail, enrichment, tool]
tool: true
---

# CRM Gmail Enrichment

## Purpose
Search V's Gmail for email threads with a specific contact and return formatted intelligence block suitable for appending to CRM profile YAML.

## Inputs
- **Email address**: The contact's email to search for

## Process

### Step 1: Build Search Query
Construct Gmail search query: `from:{email} OR to:{email}`

### Step 2: Search Gmail  
Call `use_app_gmail` with tool `gmail-find-email`:
- Use query from Step 1
- Set `withTextPayload: false` (we only need metadata)
- Set `metadataOnly: false` (we need snippets)
- **IMPORTANT**: Include `email: attawar.v@gmail.com` parameter to specify which Gmail account (V's primary)

### Step 3: Format Results
Load and use `file 'N5/builds/crm-v3-unified/gmail_enrichment_module.py'` to format results:
```python
from gmail_enrichment_module import format_gmail_intelligence
intelligence_block = format_gmail_intelligence(gmail_results, target_email)
```

### Step 4: Return Output
Return the formatted intelligence block as markdown, ready to append to CRM YAML.

## Output Format
```markdown
**Gmail Thread Analysis:**

Found X message(s) with email@example.com:

  1. "Subject Line" (2025-11-15)
     → Snippet preview of the message content...
  2. "Another Subject" (2025-11-10)
     → Another snippet preview...

**Total threads:** X
```

## Error Handling
- If Gmail not connected: Return "⚠️ Gmail not connected"
- If no results found: Return "No Gmail threads found with {email}"
- If API error: Return "⚠️ Error searching Gmail: {error}"

## Example Usage
```
@crm-gmail-enrichment john.doe@company.com
```

## Notes
- Searches both sent and received messages
- Shows top 5 most recent threads
- Includes snippet preview for context
- Uses V's primary Gmail account (attawar.v@gmail.com)


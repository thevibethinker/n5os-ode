---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
title: Gmail Contact Enrichment
description: Search Gmail for threads with a contact and generate intelligence summary
tags: [crm, gmail, enrichment, tool]
tool: true
---

# Gmail Contact Enrichment Prompt

## Input
- **Email address** of the contact to enrich

## Task
1. Use `use_app_gmail` with `gmail-find-email` tool to search for messages
2. Search query: `from:{email} OR to:{email}` to find all correspondence
3. Analyze the results and generate an intelligence block

## Search Parameters
- tool_name: `gmail-find-email`
- q: `from:{email} OR to:{email}`
- maxResults: 10
- withTextPayload: true (for easier analysis)

## Output Format
Return a markdown intelligence block formatted as:

```
**Gmail Thread Analysis:**

Found X message(s) with {email}:

  1. "Subject Line" (YYYY-MM-DD)
     → Brief snippet...
  2. "Subject Line" (YYYY-MM-DD)
     → Brief snippet...

Communication pattern: [brief analysis]
```

## Error Handling
- If no results: "No Gmail threads found with {email}"
- If error: "⚠️ Error searching Gmail: {error}"
- If not connected: "⚠️ Gmail not connected"

## Notes
- This prompt is called by the CRM enrichment worker
- Output is inserted into profile YAML intelligence section
- Search both "from" and "to" to catch all correspondence
- Prioritize most recent messages


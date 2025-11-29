---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
title: CRM Profile Enrichment
description: Enrich a CRM profile with multi-source intelligence (Aviato, Gmail, LinkedIn)
tags: [crm, enrichment, gmail, aviato, intelligence]
tool: true
---

# CRM Profile Enrichment

## Purpose
Gather intelligence from multiple sources and append to CRM profile YAML file.

## Inputs
Required as command-line arguments or from trigger:
- `profile_id`: CRM profile ID
- `email`: Contact's email address
- `checkpoint`: Enrichment checkpoint identifier
- `yaml_path`: Path to profile YAML file

## Process

### 1. Aviato Enrichment
Use file 'Integrations/Aviato/aviato_client.py' to search for person by email.
Extract and format: name, title, company, experience, education, investor info, social links.

### 2. Gmail Thread Analysis  
Search V's Gmail for threads with the contact:

```python
# Use primary Gmail account
use_app_gmail(
    tool_name="gmail-find-email",
    configured_props={
        "q": f"from:{email} OR to:{email}",
        "withTextPayload": False,
        "metadataOnly": False
    },
    email="attawar.v@gmail.com"
)
```

Format results using file 'N5/orchestration/crm-v3-unified/gmail_enrichment_module.py':
```python
from gmail_enrichment_module import format_gmail_intelligence
gmail_block = format_gmail_intelligence(results, email)
```

### 3. LinkedIn Intelligence
**Status:** Not yet implemented (stub for now)

### 4. Combine and Append
Combine all intelligence sources into single block:

```markdown
### YYYY-MM-DD HH:MM | multi_source_enrichment
**Checkpoint:** {checkpoint}
**Sources:** aviato, gmail, linkedin

{aviato_intelligence}

{gmail_intelligence}

{linkedin_intelligence}
```

Append to profile YAML under `## Intelligence Log` section.

## Error Handling
- Aviato not found: Include "⚠️ Profile not found" note
- Gmail no results: Include "No Gmail threads found" note
- Any API errors: Log error, continue with other sources
- Always succeed partially - don't fail entire enrichment if one source fails

## Output
Updated profile YAML file with new intelligence log entry.

## Success Indicators
- At least one source returned data
- Intelligence appended to YAML
- No file corruption
- Proper markdown formatting

## Example Intelligence Block

```markdown
### 2025-11-18 15:30 | multi_source_enrichment
**Checkpoint:** checkpoint_1
**Sources:** aviato, gmail, linkedin

**Aviato Enrichment:**

**Name:** John Doe
**Title:** VP of Engineering
**Company:** Acme Corp
**Location:** San Francisco, CA

**Experience:** 3 positions tracked
  - VP Engineering at Acme Corp
  - Senior Engineer at StartupXYZ
  - Engineer at BigTech Inc

**LinkedIn Intelligence:**

⚠️ LinkedIn API not yet integrated

**Gmail Thread Analysis:**

Found 5 message(s) with john.doe@acme.com:

  1. "Product collaboration discussion" (2025-11-15)
     → Thanks for the great meeting yesterday. Looking forward to...
  2. "Introduction" (2025-11-10)
     → Nice to meet you at the conference...

**Total threads:** 5
```


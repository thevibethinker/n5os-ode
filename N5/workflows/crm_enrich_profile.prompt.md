---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
title: CRM Profile Enrichment
description: Enrich a CRM profile with intelligence from external sources (Aviato, Gmail, LinkedIn)
tags: [crm, enrichment, automation, workflow]
tool: true
---

# CRM Profile Enrichment Workflow

## Inputs Required

- `profile_id`: Database profile ID
- `checkpoint`: "checkpoint_1" or "checkpoint_2"
- `email`: Profile email address
- `yaml_path`: Path to profile YAML file

## Workflow

### Step 1: Gather Intelligence

Based on checkpoint:

**Checkpoint 1** (3 days before meeting):
1. Call Aviato API (stub for now - return mock data with TODO marker)
2. Use `use_app_gmail` to search threads with this email
3. Call LinkedIn API (stub for now - return mock data with TODO marker)

**Checkpoint 2** (morning of meeting):
1. Check for new emails since checkpoint 1
2. Generate meeting brief synthesizing all sources
3. Email brief to V using `send_email_to_user`

### Step 2: Append Intelligence to YAML

Use `edit_file_llm` to append intelligence to the profile YAML file.

**Instructions for edit_file_llm:**
- Locate or create "## Intelligence Log" section
- Append new timestamped entry
- Never modify existing content (append-only)
- Use format:

```yaml
### YYYY-MM-DD HH:MM | source_type
**Checkpoint:** checkpoint_X
**Metadata:** {...}

[Intelligence content here]
```

### Step 3: Return Results

Return structured result:
```json
{
  "success": true,
  "sources_checked": ["aviato", "gmail", "linkedin"],
  "intelligence_added": true,
  "yaml_updated": true,
  "errors": []
}
```

## Error Handling

- If API call fails, log error but continue with other sources
- If YAML append fails, raise exception (critical failure)
- Return partial success if some sources fail

## Example Execution

```python
# Worker would call this prompt with:
result = execute_prompt(
    "N5/workflows/crm_enrich_profile.prompt.md",
    context={
        "profile_id": 37,
        "checkpoint": "checkpoint_1",
        "email": "example@company.com",
        "yaml_path": "/home/workspace/N5/crm_v3/profiles/Example_User_example.yaml"
    }
)
```

## Notes

- Aviato and LinkedIn are stubbed with TODO markers
- Gmail integration uses actual `use_app_gmail` tool
- YAML editing uses `edit_file_llm` (no regex!)
- This prompt is invoked by `crm_enrichment_worker.py`


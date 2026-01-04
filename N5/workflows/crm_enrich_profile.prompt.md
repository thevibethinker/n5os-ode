---
created: 2025-11-18
last_edited: 2026-01-03
version: 2.0
title: CRM Profile Enrichment
description: Enrich a CRM profile with intelligence from external sources (Aviato, Nyne, Gmail, LinkedIn)
tags: [crm, enrichment, automation, workflow]
tool: true
---

# CRM Profile Enrichment Workflow

## Inputs Required

- `profile_id`: Database profile ID
- `checkpoint`: "checkpoint_1" or "checkpoint_2"
- `email`: Profile email address
- `yaml_path`: Path to profile YAML file
- `linkedin_url`: LinkedIn profile URL (optional, improves Nyne results)

## Enrichment Sources

| Source | Data Type | When Called |
|--------|-----------|-------------|
| **Aviato** | Professional (title, company, experience, education) | Always first |
| **Nyne** | Social (Twitter, Instagram, newsfeed, interests, phones) | Selectively based on Aviato results |
| **Gmail** | Email history, thread context | If connected |
| **LinkedIn (Kondo)** | Messages, connection context | If metadata exists |

## Selective Enrichment Strategy (Aviato → Nyne)

Nyne provides unique data Aviato lacks:
- Social media profiles (Twitter, Instagram, TikTok, YouTube)
- Newsfeed/recent social activity
- Interests and topics of discussion
- Additional phone numbers and emails

**Selection Logic:**
1. **Aviato returns NO data** → Full Nyne enrichment (person + newsfeed)
2. **Aviato returns SPARSE data** (missing title/experience) → Full Nyne enrichment
3. **Aviato returns RICH data** → Nyne for newsfeed only (if LinkedIn URL available)

This strategy:
- Maximizes data coverage
- Minimizes API costs (Nyne: 6 credits per enrichment, 3 for lite)
- Uses Nyne's unique social data to complement Aviato's professional data

## Workflow

### Step 1: Gather Intelligence

Based on checkpoint:

**Checkpoint 1** (3 days before meeting):
1. Call Aviato API via `enrich_via_aviato(email, linkedin_url)`
2. Call Nyne API selectively via `enrich_with_fallback(email, linkedin_url, aviato_result)`
3. Use `use_app_gmail` to search threads with this email
4. Check LinkedIn/Kondo for conversation history

**Checkpoint 2** (morning of meeting):
1. Check for new emails since checkpoint 1
2. Refresh Nyne newsfeed if stakeholder has active social presence
3. Generate meeting brief synthesizing all sources
4. Email brief to V using `send_email_to_user`

### Step 2: Append Intelligence to Profile Markdown

Use `edit_file_llm` to append intelligence to the CRM profile markdown file.

**Instructions for edit_file_llm:**
- Locate or create "## Intelligence Log" section
- Append new timestamped entry per source
- Never modify existing content (append-only)
- Use format:

```markdown
### YYYY-MM-DD HH:MM | source_type
**Checkpoint:** checkpoint_X
**Metadata:** {...}

[Intelligence content here]
```

**Expected Sections in Profile:**
1. **Aviato Professional Intelligence** - Career, education, skills
2. **Nyne Social Intelligence** - Social profiles, contact info, interests
3. **Nyne Social Activity** - Recent posts/newsfeed (if available)
4. **Gmail Intelligence** - Email thread summaries
5. **LinkedIn Intelligence** - Message history, connection context

### Step 3: Return Results

Return structured result:
```json
{
  "success": true,
  "sources_checked": ["aviato", "nyne", "gmail", "linkedin"],
  "sources_found": ["aviato", "nyne"],
  "intelligence_added": true,
  "nyne_mode": "full|newsfeed_only|skipped",
  "yaml_updated": true,
  "errors": []
}
```

## Error Handling

- If API call fails, log error but continue with other sources
- If YAML append fails, raise exception (critical failure)
- Return partial success if some sources fail
- Rate limits: Both Aviato and Nyne have rate limiting - use backoff

## Example Execution

```python
# Worker would call this workflow with:
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato
from N5.scripts.enrichment.nyne_enricher import enrich_with_fallback

# Step 1: Aviato first
aviato_result = await enrich_via_aviato(email, linkedin_url=linkedin_url)

# Step 2: Nyne with selective logic
nyne_result = await enrich_with_fallback(
    email=email,
    linkedin_url=linkedin_url,
    aviato_result=aviato_result
)

# Step 3: Merge intelligence into profile
# ... append aviato_result['markdown'] and nyne_result['markdown'] to profile
```

## Notes

- Aviato enrichment is the primary source (professional data)
- Nyne enrichment supplements with social data Aviato lacks
- Gmail integration uses actual `use_app_gmail` tool
- YAML/Markdown editing uses `edit_file_llm` (no regex!)
- This prompt is invoked by `crm_enrichment_worker.py`

## Credit Usage (Nyne)

- Full enrichment: 6 credits
- Lite enrichment: 3 credits  
- Newsfeed only: 6 credits (when data found)
- Free trial: 100 credits total



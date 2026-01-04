---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: con_lLosGL4MKCXUQS4V
title: Nyne
description: Nyne.ai enrichment tool - person and company intelligence with social media data
tags: [enrichment, nyne, crm, social, meeting-prep, tool]
tool: true
---

# Nyne Enrichment Tool

Nyne.ai provides person and company intelligence with unique social media capabilities that complement Aviato.

## What Nyne Does (That Aviato Doesn't)

| Capability | Description | Credits |
|------------|-------------|---------|
| **Person Newsfeed** | Recent LinkedIn/Twitter/Instagram posts + engagement | 6 |
| **Person Interests** | Sports teams, politics, hobbies from Twitter follows | 6 |
| **Person Articles** | Interviews, podcasts, publications about someone | 6 |
| **Company CheckSeller** | "Does X company sell Y?" with evidence | 6 |
| **Company Feature Checker** | Tech stack detection (React, Stripe, etc.) | 6 |
| **Company Funding** | Full funding history + investors | 6 |

## Usage

### Person Enrichment

```python
# Run in N5/scripts/enrichment/nyne_enricher.py
from N5.scripts.enrichment.nyne_enricher import enrich_person_via_nyne

result = await enrich_person_via_nyne(
    email="someone@company.com",
    linkedin_url="https://linkedin.com/in/someone",  # optional
    include_newsfeed=True,  # +6 credits if data found
    lite_mode=False  # lite = 3 credits, basic fields only
)

# Returns: {success, data, error, markdown}
```

### Social Activity Only (Meeting Prep)

```python
from N5.scripts.enrichment.nyne_enricher import get_social_newsfeed_via_nyne

result = await get_social_newsfeed_via_nyne(
    linkedin_url="https://linkedin.com/in/someone"
)
# Returns recent posts with engagement metrics
```

### Company Enrichment

```python
from N5.scripts.enrichment.nyne_enricher import enrich_company_via_nyne

result = await enrich_company_via_nyne(
    domain="acme.com",
    # OR company_name="Acme Inc",
    # OR linkedin_url="https://linkedin.com/company/acme"
)
```

### Smart Fallback (With Aviato)

```python
from N5.scripts.enrichment.nyne_enricher import enrich_with_fallback
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato

# First, try Aviato
aviato_result = await enrich_via_aviato(email="someone@company.com")

# Then, use Nyne selectively based on Aviato results
nyne_result = await enrich_with_fallback(
    email="someone@company.com",
    linkedin_url="https://linkedin.com/in/someone",
    aviato_result=aviato_result
)
# - No Aviato data → Full Nyne enrichment
# - Sparse Aviato → Nyne supplemental
# - Rich Aviato → Nyne for newsfeed only
```

## Direct API Access

For specialized queries not covered by the enricher:

```python
from Integrations.Nyne.nyne_client import NyneClient

client = NyneClient()

# Check if company sells something
result = client.check_company_sells("acme.com", "CRM software")
# Returns: {sells: bool, confidence: str, evidence: str}

# Check tech stack
result = client.check_company_feature("acme.com", "Stripe")
# Returns: {uses: bool, details: ...}

# Get funding history
result = client.get_company_funding("acme.com")
# Returns: {rounds: [...], total_raised: ..., investors: [...]}

# Get person interests (Twitter only)
result = client.get_person_interests("https://twitter.com/someone")
# Returns: {sports: [...], politics: [...], hobbies: [...]}
```

## Integration Points

### CRM Enrichment Workflow

Nyne is integrated into `crm_enrich_profile.prompt.md` as a supplemental source:

1. **Checkpoint 1** (3 days before meeting):
   - Aviato for professional data
   - Nyne for social activity + interests (meeting prep gold)

2. **Checkpoint 2** (morning of meeting):
   - Nyne newsfeed refresh for latest posts

### Meeting Prep

For upcoming meetings, use Nyne to get conversation starters:
- Recent LinkedIn posts (what they're thinking about)
- Twitter interests (sports teams, hobbies)
- Recent articles/podcasts featuring them

## Credit Usage

| Endpoint | Credits | Charged When |
|----------|---------|--------------|
| Person Enrichment | 6 | Data found |
| Person Lite | 3 | Data found |
| Person Newsfeed | 6 | Data found |
| Person Interests | 6 | Data found |
| Person Articles | 6 | Data found |
| Company Enrichment | 6 | Data found |

**Credits are NOT charged** when no data is found.

## Files

- **Client:** `Integrations/Nyne/nyne_client.py`
- **Enricher:** `N5/scripts/enrichment/nyne_enricher.py`
- **Usage Log:** `N5/logs/nyne_usage.jsonl`

## Environment Variables

Set in [Settings > Developers](/settings#developers):
- `NYNE_API_KEY`
- `NYNE_API_SECRET`


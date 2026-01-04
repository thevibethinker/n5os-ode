---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: con_lLosGL4MKCXUQS4V
---

# Nyne.ai Integration

Person and company intelligence API with unique social media capabilities.

## Credit Costs (À La Carte)

Nyne charges per-endpoint, not bundles. Call only what you need:

| Endpoint | Credits | Use Case |
|----------|---------|----------|
| Company Enrichment | 1 | Basic company info |
| Person Enrichment | 10 | Full person profile |
| **CheckSeller** | 2 | "Does X sell Y?" |
| **Feature Checker** | 3 | Tech stack detection (opt-in) |
| **Company Needs** | 3 | Pain points from SEC filings |
| **Funding** | 8 | Funding rounds & investors |
| **Investor Lookup** | 20 | Deep investor profiles |

**Cost-conscious defaults:**
- Tech stack detection is **opt-in only** (`--tech-check`)
- Investor deep-dive is **opt-in only** (`--investor-details`)
- No credits charged if lookup fails or returns no data

## Setup

1. API credentials are set in [Settings > Developers](/settings#developers):
   - `NYNE_API_KEY`
   - `NYNE_API_SECRET`

2. Free trial: 100 credits/month

## Files

| File | Purpose |
|------|---------|
| `nyne_client.py` | Low-level API client |
| `N5/scripts/enrichment/nyne_enricher.py` | High-level enricher (mirrors Aviato pattern) |
| `N5/logs/nyne_usage.jsonl` | Usage tracking |
| `Prompts/Nyne.prompt.md` | Documentation + tool prompt |

## Quick Usage

```python
from N5.scripts.enrichment.nyne_enricher import enrich_person_via_nyne

result = await enrich_person_via_nyne(
    email="someone@company.com",
    include_newsfeed=True
)
# Returns: {success, data, error, markdown}
```

## Credit Costs

| Endpoint | Credits |
|----------|---------|
| Person Enrichment | 6 |
| Person Lite | 3 |
| Newsfeed add-on | +6 |
| Company Enrichment | 6 |

Credits only charged when data is found.

## API Capabilities

### Person APIs
- **Enrichment** - Full profile from email/phone/LinkedIn
- **Newsfeed** - Recent social posts + engagement
- **Interests** - What they follow (sports, politics, hobbies)
- **Articles** - Interviews, podcasts, publications

### Company APIs
- **Enrichment** - Company info from domain/name
- **CheckSeller** - "Does X sell Y?" with evidence
- **Feature Checker** - Tech stack detection
- **Funding** - Full funding history + investors

## Integration with Aviato

Nyne complements Aviato (not replaces):
- **Aviato** = LinkedIn work history, connections
- **Nyne** = Social activity, interests, newsfeeds

Strategy: `enrich_with_fallback()` uses Nyne selectively based on Aviato results.



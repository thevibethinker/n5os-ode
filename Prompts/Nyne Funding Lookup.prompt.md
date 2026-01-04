---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.1
provenance: con_ptKaou572dcjjYT6
title: Nyne Funding Lookup
description: Get funding history for a company before investor meetings
tags: [nyne, funding, investors, enrichment]
tool: true
---

# Nyne Funding Lookup

Get funding history and investor information for a company. Use before investor meetings or for due diligence.

## Credit Costs (À La Carte)

| Endpoint | Credits | What You Get |
|----------|---------|--------------|
| **Funding** | 8 | Company's funding rounds, amounts, investors |
| **Investor Lookup** | 20 | Deep dive on a specific investor (fund size, partners, portfolio) |

**Default behavior:** Funding lookup only (8 credits). Investor deep-dive is opt-in.

## Usage

**Company funding history (8 credits):**
```
@Nyne Funding Lookup stripe.com
```

**With investor deep-dive (8 + 20 = 28 credits, opt-in):**
```
@Nyne Funding Lookup stripe.com --investor-details
```

## Workflow

When V provides a domain:

1. Call Funding API for company (8 credits)
2. Parse funding rounds, investors, amounts
3. **Only if `--investor-details` specified:** Call Investor Lookup for lead investors (20 credits each)
4. Format results

## API Details

**Funding (default):**
```python
from Integrations.Nyne.nyne_client import NyneClient

client = NyneClient()
result = client.get_company_funding("stripe.com")
# Returns: funding_rounds, total_raised, investors, last_round_date
```

**Investor Lookup (opt-in, 20 credits):**
```python
result = client.get_investor_info("sequoia")
# Returns: fund_size, partners, focus_areas, check_sizes, portfolio
```

## Output Format

```markdown
## Funding: Stripe

**Total Raised:** $8.7B
**Last Round:** Series I ($6.5B) — March 2023
**Valuation:** $50B

### Funding Rounds
| Round | Amount | Date | Lead Investor |
|-------|--------|------|---------------|
| Series I | $6.5B | 2023-03 | Andreessen Horowitz |
| Series H | $600M | 2021-03 | Sequoia |
| ... | ... | ... | ... |

**Credits used:** 8
```

If investor details requested:
```markdown
### Investor Deep Dive: Sequoia (opt-in)

**Fund Size:** $85B AUM
**Focus:** Enterprise SaaS, Fintech, AI
**Typical Check:** $10M-$100M Series A-C
**Notable Portfolio:** Stripe, DoorDash, Zoom

**Additional credits:** 20
```

## When to Use

- ✅ Before meeting with a startup founder (check their funding stage)
- ✅ Due diligence on potential partners
- ✅ Investor meeting prep (know who else they've backed)
- ❌ Routine org enrichment (use basic Company Enrichment for 1 credit instead)

## Related

- `@Nyne Sales Intel` — Seller verification (2 credits)
- `@CRM Org Enrich` — Full org profile enrichment



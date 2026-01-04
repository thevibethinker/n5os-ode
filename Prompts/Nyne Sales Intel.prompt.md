---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.1
provenance: con_ptKaou572dcjjYT6
title: Nyne Sales Intel
description: Check if a company sells a specific product/service before sales calls
tags: [nyne, sales, qualification, enrichment]
tool: true
---

# Nyne Sales Intel

Verify whether a company sells a specific product or service. Use before sales calls to check for competitive overlap or confirm product fit.

## Credit Costs (À La Carte)

| Check | Credits | When to Use |
|-------|---------|-------------|
| **CheckSeller** | 2 | "Does X sell Y?" — Primary use case |
| **Tech Stack** | 3 | Only if you specifically need to know their tech (opt-in) |

## Usage

**Basic seller check (2 credits):**
```
@Nyne Sales Intel acme.com "CRM software"
```

**With tech stack (5 credits total, opt-in):**
```
@Nyne Sales Intel acme.com "CRM software" --tech-check stripe,react
```

## Workflow

When V provides a domain and query:

1. Parse domain and product/service query
2. Call CheckSeller API (2 credits)
3. **Only if `--tech-check` specified:** Call Feature Checker for each technology (3 credits each)
4. Return verdict with evidence

## API Details

**CheckSeller (default):**
```python
from Integrations.Nyne.nyne_client import NyneClient

client = NyneClient()
result = client.check_company_sells("acme.com", "CRM software")
# Returns: {"verdict": "yes", "confidence": 0.92, "evidence": "..."}
```

**Tech Stack (opt-in only):**
```python
result = client.check_company_feature("acme.com", "stripe")
# Returns: {"found": true, "confidence": 0.95, "evidence": "..."}
```

## Output Format

```markdown
## Sales Intel: acme.com

**Query:** "Does Acme sell CRM software?"
**Verdict:** ✅ Yes (92% confidence)
**Evidence:** "Acme offers enterprise CRM solutions including..."
**Credits used:** 2
```

If tech stack requested:
```markdown
### Tech Stack (opt-in)
| Technology | Found | Evidence |
|------------|-------|----------|
| Stripe | ✅ Yes | Payment integration detected |
| React | ❌ No | Not detected |

**Additional credits:** 6 (2 technologies × 3 credits)
```

## Related

- `@Nyne Funding Lookup` — Funding and investor data (8 credits)
- `@CRM Org Enrich` — Full org profile enrichment



---
title: CRM Org Enrichment
description: Enrich an organization profile using Nyne (primary) + Aviato (fallback) data sources
version: 1.5
created: 2026-01-03
last_edited: 2026-01-03
tags: [crm, enrichment, organizations, nyne, aviato]
tool: true
---

# CRM Organization Enrichment Workflow

## Purpose

Enrich an organization profile with intelligence from Nyne and Aviato APIs. Creates or updates the org's markdown profile in `Personal/Knowledge/CRM/organizations/<slug>.md` and updates the SQLite record in `crm_v3.db`.

## Invocation

```
@CRM Org Enrich <domain or company name>
```

**Examples:**
- `@CRM Org Enrich nyne.ai`
- `@CRM Org Enrich "Acme Corporation"`
- `@CRM Org Enrich https://linkedin.com/company/acme-corp`

## Input Requirements

At least ONE of:
- **Domain** (preferred): `example.com`
- **Company name**: `"Acme Corporation"`
- **LinkedIn URL**: `https://linkedin.com/company/acme`

## Enrichment Tiers

| Tier | Trigger | Data Fetched | Credits |
|------|---------|--------------|---------|
| **Stub** | Auto-created from person enrichment | Name + domain only | 0 |
| **Light** | Low-priority org | Basic fields (industry, size, location) | 1-2 |
| **Full** | High-value org (sales, investor, partner) | Complete Nyne + Aviato enrichment | 6-12 |
| **Full-Intel** | Strategic research | Full + sales intel + funding + needs | ~10-15 |

## CLI Reference (Phase 6)

```bash
# Basic enrichment
python3 N5/scripts/enrichment/org_enricher.py --domain example.com

# With tier
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --tier full

# Advanced intel flags (Phase 6)
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --sales-intel "CRM software"
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --funding
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --needs "cost reduction"
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --tech-check "stripe,react"
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --investors  # ⚠️ 20 credits!
python3 N5/scripts/enrichment/org_enricher.py --domain example.com --full-intel  # All except investors

# Extract orgs from meeting (Phase 6)
python3 N5/scripts/enrichment/org_enricher.py --from-meeting /path/to/meeting/folder
```

### CLI Flags Summary

| Flag | Description | Credits |
|------|-------------|---------|
| `--domain`, `-d` | Company domain (e.g., nyne.ai) | - |
| `--company-name`, `-n` | Company name | - |
| `--linkedin-url`, `-l` | LinkedIn company page URL | - |
| `--tier`, `-t` | Enrichment tier: stub, light, full | varies |
| `--sales-intel PRODUCT` | Check if company sells PRODUCT | ~1 |
| `--funding` | Fetch funding history and rounds | ~1 |
| `--needs TOPIC` | Fetch pain points from SEC filings | 3 |
| `--investors` | Detailed investor profiles | ⚠️ 20 |
| `--full-intel` | All intel (NOT investors) | ~5 |
| `--tech-check TECHS` | Check tech stack (comma-separated) | ~1/tech |
| `--from-meeting PATH` | Extract orgs from meeting folder | 0 |
| `--force`, `-f` | Force re-enrichment | - |
| `--json` | Output as JSON | - |

## Workflow Steps

### 1. Parse Input

Extract domain, company name, or LinkedIn URL from user input.

```python
# Normalize input
if input.startswith('http'):
    linkedin_url = input
    domain = None
elif '.' in input and ' ' not in input:
    domain = input.lower().strip()
else:
    company_name = input
```

### 2. Check Existing Record

Query `crm_v3.db` for existing org:

```sql
SELECT * FROM organizations 
WHERE domain = ? OR slug = ? OR linkedin_url = ?;
```

If found with `enrichment_status = 'enriched'` and recent `last_enriched_at` (< 30 days):
→ Return cached data, skip re-enrichment unless `--force` specified.

### 3. Determine Enrichment Tier

**Full enrichment if:**
- User explicitly requests full: `@CRM Org Enrich nyne.ai --full`
- Org appears in multiple meetings (>2)
- Org is tagged as `relationship_type: sales_prospect | investor | partner`

**Light enrichment if:**
- First encounter with org
- Single meeting reference
- No explicit tier request

**Stub if:**
- Created automatically from person enrichment
- Only need name + domain for linking

### 4. Call Enrichment APIs

**Primary: Nyne Company Enrichment**

```python
from N5.scripts.enrichment.nyne_enricher import enrich_company_via_nyne

result = await enrich_company_via_nyne(
    domain=domain,
    company_name=company_name,
    linkedin_url=linkedin_url
)
```

**Returns:**
- `data.name` - Company name
- `data.domain` - Website domain
- `data.description` - Company description
- `data.industry` - Industry classification
- `data.founded` - Founding year
- `data.headcount` - Employee count range
- `data.location` - HQ location
- `data.funding` - Funding data (if available)
- `data.linkedin_url` - LinkedIn company page

**Secondary: Aviato Company Enrichment** (if Nyne sparse)

[Aviato company endpoint not yet integrated - use Nyne data only for now]

### 5. Update Database

```sql
INSERT INTO organizations (
    name, slug, domain, source, enrichment_status,
    last_enriched_at, linkedin_url, description,
    industry, founded_year, headcount_range, location
) VALUES (?, ?, ?, ?, 'enriched', datetime('now'), ?, ?, ?, ?, ?, ?)
ON CONFLICT(slug) DO UPDATE SET
    name = excluded.name,
    domain = excluded.domain,
    enrichment_status = 'enriched',
    last_enriched_at = datetime('now'),
    linkedin_url = excluded.linkedin_url,
    description = excluded.description,
    industry = excluded.industry,
    founded_year = excluded.founded_year,
    headcount_range = excluded.headcount_range,
    location = excluded.location,
    updated_at = datetime('now');
```

### 6. Generate Markdown Profile

Create/update `Personal/Knowledge/CRM/organizations/<slug>.md`:

```markdown
---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: <conversation_id>
slug: nyne-ai
domain: nyne.ai
aliases: [Nyne, Nyne Inc]
enrichment_sources: [nyne]
last_enriched: 2026-01-03
enrichment_tier: full
---

# Nyne

## Overview

**Industry:** Data & Analytics  
**Founded:** 2020  
**Size:** 11-50 employees  
**HQ:** San Francisco, CA  

Nyne provides AI-powered enrichment APIs for person and company data...

---

## Key People (Linked)

- [[michael-fanous]] — CEO

---

## Related Meetings

- [[2026-01-03_Michael-Fanous_discovery]]

---

## Intelligence Notes

[Meeting notes and observations accumulated here]
```

### 7. Update Linked Individuals

For each person in CRM with matching domain:

```sql
UPDATE profiles 
SET organization_id = (SELECT id FROM organizations WHERE slug = ?)
WHERE email LIKE '%@' || ?;
```

Update individual markdown files to add `organization: [[slug]]` to frontmatter.

### 8. Return Summary

Output:
- Organization profile path
- Enrichment tier applied
- Data sources used
- Credits consumed
- Linked individuals count

## Script Integration

This workflow wraps `N5/scripts/enrichment/org_enricher.py`:

```bash
python3 N5/scripts/enrichment/org_enricher.py \
    --domain nyne.ai \
    --tier full \
    --conversation-id con_xxx
```

## Meeting Integration (Phase 6)

Extract organization domains from a meeting manifest and create stubs:

```bash
python3 N5/scripts/enrichment/org_enricher.py \
    --from-meeting "/home/workspace/Personal/Meetings/2026-01-03_Acme-Discovery"
```

**What it does:**
1. Reads `manifest.json` from meeting folder
2. Extracts unique company domains from attendee emails
3. Filters out personal email domains (gmail.com, outlook.com, etc.)
4. Scans B06/B09 blocks for company references
5. Creates org stubs for any new companies
6. Returns summary of orgs found/created

**Excluded personal email domains:**
gmail.com, googlemail.com, outlook.com, hotmail.com, yahoo.com, icloud.com, me.com, mac.com, protonmail.com, proton.me, aol.com, live.com, msn.com, zoho.com, fastmail.com, tutanota.com, hey.com, pm.me

## Advanced Intel Use Cases

### Sales Intelligence
```bash
# Check if company sells specific products
python3 org_enricher.py --domain salesforce.com --sales-intel "CRM"
```
Returns: `sells: true/false`, confidence level, evidence

### Funding Research
```bash
# Get funding history before investor meeting
python3 org_enricher.py --domain startup.com --funding
```
Returns: Funding rounds, investors, valuations, total raised

### Company Needs (SEC Filings)
```bash
# Surface pain points from 10-K filings
python3 org_enricher.py --domain publiccompany.com --needs "regulatory challenges"
```
Returns: Pain points extracted from SEC filings with sources

### Tech Stack Detection
```bash
# Check what technologies they use
python3 org_enricher.py --domain techco.com --tech-check "stripe,react,aws"
```
Returns: Per-technology detection status with evidence

### Full Intel Package
```bash
# Run all intel (for strategic research)
python3 org_enricher.py --domain target.com --full-intel
```
Runs: Sales intel + funding + needs (skips investors due to cost)

### Investor Profiles (Use Sparingly!)
```bash
# Get detailed investor profiles (EXPENSIVE)
python3 org_enricher.py --domain portfolio-company.com --investors
```
⚠️ **Warning:** 20 credits per call. Use only for high-value targets.

## Credit Costs (Nyne)

| Operation | Credits | When to Use |
|-----------|---------|-------------|
| Basic Enrichment | 1-2 | Default for new orgs |
| Full Enrichment | 6 | High-value orgs |
| CheckSeller (--sales-intel) | ~1 | Sales qualification |
| Feature Checker (--tech-check) | ~1/tech | Integration planning |
| Funding Intel (--funding) | ~1 | Pre-investor meetings |
| Company Needs (--needs) | 3 | Enterprise sales prep |
| Investor Profiles (--investors) | **20** | ⚠️ Rarely, high-value only |
| Full Intel (--full-intel) | ~5 | Strategic research |

**Budget guidance:** 
- Only full-enrich orgs that V has active interest in
- Use `--full-intel` sparingly (strategic targets only)
- Never use `--investors` routinely — reserve for pre-funding conversations

## Error Handling

| Error | Action |
|-------|--------|
| Org not found in Nyne | Create stub with input data only |
| Rate limit (429) | Retry with exponential backoff |
| Invalid domain | Prompt user for correction |
| API credentials missing | Report and halt |

## Related Workflows

- `crm_enrich_profile.prompt.md` - Person enrichment (calls this for org stubs)
- `crm_query.prompt.md` - Query CRM data
- `Meeting Manifest Generation.prompt.md` - Triggers org stub creation

---

*v1.5 | Phase 6 of Nyne Integration | CLI Polish + Meeting Integration*



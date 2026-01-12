---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_CUmT8IYgH32g6X9K
---

# After-Action Report: Scheduled Agent & CRM System Cleanup

**Date:** 2026-01-12
**Type:** system-hygiene
**Conversation:** con_CUmT8IYgH32g6X9K

## Objective

Perform a thorough accounting of all scheduled agents, eliminate redundant/deprecated ones, and clean up the CRM system to reduce noise and improve data quality.

## What Happened

### Phase 1: Agent Audit & Cleanup

Conducted functional analysis of 44 scheduled agents, clustering by purpose:

| Cluster | Action | Result |
|---------|--------|--------|
| **Core Workflows** | Kept | Morning Digest, Stakeholder Auto-Creation |
| **Travel** | Consolidated | Kept Daily Flight Scanner, deleted Hourly/Weekly variants |
| **Luma (Deprecated)** | Deleted | 5 legacy agents from old event pipeline |
| **Health Check-ins** | Deleted | 4 old Bio-Log agents (superseded) |
| **CRM** | Deleted | Weekly Gmail Enrichment (redundant with on-demand) |
| **Maintenance** | Deleted | Weekly Cleanup, Monthly Audit (inactive, brittle) |

**Net result:** 44 → 30 agents

### Phase 2: Morning Digest Quality Audit

Spawned worker to audit Morning Digest quality issues. Findings:

1. **Reconnect rotation broken** — Same contacts shown daily (no `last_suggested_at` tracking)
2. **Context extraction weak** — Just showing names, not org/role
3. **Top 3 Today dead** — Fed by `must-contact.jsonl` which had 1 stale item from Oct
4. **73% of CRM unenriched** — Enrichment pipeline blocked

**Fixes deployed:**
- Added `last_suggested_at` column + rotation logic
- Improved context extraction (email domain → org inference)
- Removed Top 3 Today section entirely
- Deleted stale `must-contact.jsonl`

### Phase 3: Enrichment Pipeline Fix

Discovered enrichment was blocked by:
1. **Nyne rate limits (429)** — Batch processing impossible
2. **139 placeholder emails** — Contacts with `@placeholder.local` can't be enriched

**Resolution:**
- Removed Nyne from enrichment pipeline entirely (now Aviato-only)
- Deleted all 139 ghost profiles with placeholder emails
- Purged 68 failed enrichment queue jobs
- Cleaned 259 orphaned YAML files (CamelCase duplicates)

### Key Decisions

1. **Aviato-only enrichment** — Nyne's rate limits make it unsuitable for batch operations
2. **Ghost profile purge** — Placeholder emails are unenrichable; fresh start is cleaner than backfill
3. **No new scheduled agents** — V explicitly wants to avoid agent sprawl; enrichment will be on-demand
4. **Remove Top 3 Today** — Dead feature, `must-contact.jsonl` not being populated

### Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| Debug Report | `/home/.z/workspaces/con_CUmT8IYgH32g6X9K/MORNING_DIGEST_DEBUG_REPORT.md` | Full diagnostic of digest data sources |
| Placeholder Resolution Script | `N5/scripts/resolve_placeholder_emails.py` | Tool for future email lookups |
| Worker Assignment | `Records/Temporary/WORKER_ASSIGNMENT_20260104_192403_428844_6X9K.md` | Spawned audit worker |

## Lessons Learned

### Process
- **Agent sprawl is expensive** — Scheduled agents consume tokens even when outputs are ignored
- **Data quality > automation** — 73% unenriched profiles meant the CRM was mostly noise
- **Rate limits kill batch pipelines** — Nyne looked good in isolation but failed at scale

### Technical
- **Enrichment queue existed but wasn't being processed** — Infrastructure was built but no scheduled runner
- **YAML file duplication** — CamelCase vs underscore naming created orphaned files
- **List files decay** — `must-contact.jsonl` was 93 days stale with no refresh mechanism

## Next Steps

1. **Monitor next Morning Digest** — Verify rotation and context extraction work in production
2. **Consider Kondo→CRM pipeline** — LinkedIn contacts have profile URLs but no emails; could enrich via Aviato lookup
3. **Placeholder email strategy** — Gmail search for names is viable but manual; defer until needed

## Outcome

**Status:** Completed

**Before/After:**
- Scheduled agents: 44 → 30
- CRM profiles: 234 → 92 (real contacts only)
- Enrichment pipeline: Blocked → Aviato-only, functional
- Morning Digest: Stale/broken → Fixed rotation + context


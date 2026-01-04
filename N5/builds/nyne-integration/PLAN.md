---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.3
provenance: con_lTqPPi0AbxJepcf8
---

# Plan: Nyne API Integration

## Strategy
D + Selective + Fallback:
- All APIs (person, company, newsfeed, interests)
- Selective: Use Nyne for social data Aviato lacks
- Fallback: Use Nyne when Aviato returns sparse data

## Checklist

### Phase 1: Core Integration ✅
- [x] Research documentation
- [x] Set up environment variables (NYNE_API_KEY, NYNE_API_SECRET)
- [x] Create API client (`Integrations/Nyne/nyne_client.py`)
- [x] Create enricher module (`N5/scripts/enrichment/nyne_enricher.py`)
- [x] Create usage logging (`N5/logs/nyne_usage.jsonl`)
- [x] Test with real API calls
- [x] Create prompt documentation (`Prompts/Nyne.prompt.md`)
- [x] Create README (`Integrations/Nyne/README.md`)

### Phase 2: CRM Integration ✅
- [x] Update `crm_enrich_profile.prompt.md` to include Nyne
- [x] Update `crm_enrichment_worker.py` to call Nyne enricher
- [x] Add Nyne section to CRM profile markdown template
- [x] Test combined Aviato + Nyne enrichment

### Phase 3: Meeting Prep Integration ✅
- [x] Add Nyne newsfeed to meeting prep digest
- [x] Add Nyne interests to B08 (Stakeholder Intelligence) block
- [x] Create meeting-specific newsfeed refresh (`get_recent_social_activity`)
- [x] Implement 7-day caching for newsfeed data
- [x] Update templates with Social Presence section

### Phase 4: Company/Organization Enrichment ✅
- [x] System audit of existing org infrastructure (`ORG_SYSTEM_AUDIT.md`)
- [x] Create org profile template (`organizations/_TEMPLATE.md`)
- [x] Create org enrichment workflow (`org_enrich_profile.prompt.md`)
- [x] Create unified org enricher script (`org_enricher.py`)
- [x] Implement DB ↔ Markdown sync for organizations
- [x] Implement profile ↔ org linking by email domain
- [x] Implement tiered enrichment (stub/light/full)

### Phase 5: Advanced Company Intelligence (Future)
- [ ] Integrate CheckSeller API for sales intel
- [ ] Integrate Feature Checker API for tech stack detection
- [ ] Add funding data aggregation to org profiles
- [ ] Meeting manifest → org extraction pipeline

## Affected Files
- `Integrations/Nyne/nyne_client.py` ✅
- `N5/scripts/enrichment/nyne_enricher.py` ✅ (Phase 1 + 3)
- `N5/scripts/enrichment/org_enricher.py` ✅ (Phase 4)
- `N5/logs/nyne_usage.jsonl` ✅
- `Prompts/Nyne.prompt.md` ✅
- `N5/workflows/crm_enrich_profile.prompt.md` ✅ (Phase 2)
- `N5/workflows/org_enrich_profile.prompt.md` ✅ (Phase 4)
- `N5/scripts/crm_enrichment_worker.py` ✅ (Phase 2)
- `Prompts/Blocks/Generate_B08.prompt.md` ✅ (Phase 3)
- `Prompts/Meeting Prep Digest.prompt.md` ✅ (Phase 3)
- `N5/data/cache/nyne/` ✅ (Phase 3 - cache directory)
- `N5/builds/nyne-integration/ORG_SYSTEM_AUDIT.md` ✅ (Phase 4)
- `Personal/Knowledge/CRM/organizations/_TEMPLATE.md` ✅ (Phase 4)

## Status
Phases 1-4 complete. Phase 5 (Advanced Company Intelligence) optional/future.




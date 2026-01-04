---
created: 2026-01-03
last_edited: 2026-01-04
version: 1.0
provenance: con_42tkB0IedFz5klNv
---

# Build Plan: Events Pipeline Consolidation

## Objective
Consolidate the bifurcated events tracking system (alerts + site) into a single unified pipeline with bidirectional sync, reliable digests, and coordinated agents.

## Success Criteria
1. Single daily agent handles all event operations (discovery → scoring → export → digest → email)
2. Site decisions sync back to DB (`event_decisions.json` → `luma_events.db`)
3. Digest emails are reliable and actionable (fix missing `luma_digest.py`)
4. Reduce 6 fragmented agents to 1-2 coordinated agents
5. DB status field properly tracks: discovered → scored → approved/rejected → registered

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │  DAILY EVENTS AGENT (8am ET)         │
                    │  - Runs luma_unified_pipeline.py     │
                    └──────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ↓                             ↓                             ↓
┌───────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ Step 1: Ingest│          │ Step 2: Score    │          │ Step 3: Digest   │
│ - scrape luma │          │ - score new evts │          │ - generate top 5 │
│ - parse emails│          │ - update DB      │          │ - format email   │
│ - sync personal│         │ - export to JSON │          │ - send digest    │
└───────────────┘          └──────────────────┘          └──────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
           ┌───────────────┐                  ┌──────────────────┐
           │ Site (UI)     │  ←──────────→    │ DB (SSOT)        │
           │ Read: JSON    │   bidirectional  │ luma_events.db   │
           │ Write: JSON   │      sync        │                  │
           └───────────────┘                  └──────────────────┘
```

## Checklist

### Phase 1: Core Infrastructure ✅
- [x] 1.1 Create `luma_digest.py` - the missing digest generation script
- [x] 1.2 Create `luma_unified_pipeline.py` - single orchestrator for all operations
- [x] 1.3 Update DB schema to add proper status tracking (already has status column)

### Phase 2: Bidirectional Sync ☐
- [ ] 2.1 Add sync endpoint to site server: decisions → DB
- [ ] 2.2 Create `sync_decisions_to_db.py` script
- [ ] 2.3 Update site to call sync on every decision

### Phase 3: Agent Consolidation ☐
- [ ] 3.1 Create new unified "Daily Events Pipeline" agent
- [ ] 3.2 Disable old fragmented agents
- [ ] 3.3 Create cleanup agent for stale events (weekly)

### Phase 4: Site Enhancement ☐
- [ ] 4.1 Add score display to event cards
- [ ] 4.2 Add "sync status" indicator (last updated)
- [ ] 4.3 Add quick filters (high score, must-go organizers)

### Phase 5: Testing & Validation ☐
- [ ] 5.1 End-to-end test: scrape → score → digest → email
- [ ] 5.2 Test bidirectional sync
- [ ] 5.3 Verify agent runs correctly

## Affected Files

### New Files to Create
- `N5/scripts/luma_digest.py` - Digest generation
- `N5/scripts/luma_unified_pipeline.py` - Unified orchestrator
- `N5/scripts/sync_decisions_to_db.py` - Decision sync

### Files to Modify
- `Sites/events-calendar-staging/server.ts` - Add sync endpoint
- `Sites/events-calendar-staging/public/index.html` - Add score display
- `N5/data/luma_events.db` - Schema update (if needed)

### Files to Reference
- `N5/scripts/luma_scraper.py` - Existing scraper
- `N5/scripts/luma_scorer.py` - Existing scorer
- `N5/scripts/luma_email_discovery.py` - Existing email parser
- `N5/config/luma_scoring.json` - Scoring config
- `N5/config/allowlists.json` - Allowlist config

## Workers

| Worker ID | Phase | Component | Dependencies | Description |
|-----------|-------|-----------|--------------|-------------|
| worker_digest | 1 | luma_digest.py | none | Create the missing digest script |
| worker_pipeline | 1 | luma_unified_pipeline.py | none | Create unified orchestrator |
| worker_sync | 2 | bidirectional_sync | worker_pipeline | Add site ↔ DB sync |
| worker_agents | 3 | agent_consolidation | worker_pipeline | Consolidate agents |
| worker_site | 4 | site_enhancements | worker_sync | Enhance site UI |

## Key Decisions
1. **DB is SSOT** - `luma_events.db` is the single source of truth, JSON exports are derived
2. **Status flow**: `new` → `scored` → `approved`/`rejected`/`maybe` → `registered`
3. **Digest format**: Top 5 events with scores, organizer trust, quick-action links
4. **Agent schedule**: 8am ET daily for main pipeline, optional 6pm refresh for new discoveries

## Risk Mitigation
- Backup existing agents before disabling
- Keep old scripts as fallback during transition
- Test digest email in dry-run mode first





---
created: 2026-01-03
last_edited: 2026-01-04
version: 1.2
provenance: con_diyRS0JP1lxgMrGt
---

# Build Status: Events Pipeline Consolidation

## Current Phase: 1 COMPLETE ✅ → Ready for Phase 2

## Progress Summary

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Core Infrastructure | ✅ Complete | 3/3 (100%) |
| Phase 2: Bidirectional Sync | ☐ Not Started | 0/3 (0%) |
| Phase 3: Agent Consolidation | ☐ Not Started | 0/3 (0%) |
| Phase 4: Site Enhancement | ☐ Not Started | 0/3 (0%) |
| Phase 5: Testing & Validation | ☐ Not Started | 0/3 (0%) |

**Overall: 3/15 (20%)**

## Completed Items

### Phase 1.1: `luma_digest.py` ✅
- **Completed:** 2026-01-04T01:04:00Z
- **Artifact:** `N5/scripts/luma_digest.py`
- **Features:**
  - Reads events from `luma_events.db`
  - Filters upcoming events (configurable days ahead)
  - Sorts by score (highest first)
  - Score visual indicators (🔥/⭐/👀/📍)
  - Organizer trust from tally
  - Must-go organizer detection
  - Outputs in markdown, HTML, JSON formats
  - CLI: `python3 luma_digest.py --days 7 --top 5 --format markdown`
- **Tested:** ✅ All formats work

### Phase 1.2: `luma_unified_pipeline.py` ✅
- **Completed:** 2026-01-04T01:08:00Z
- **Artifact:** `N5/scripts/luma_unified_pipeline.py`
- **Features:**
  - Single orchestrator for full pipeline
  - Chains: Discovery → Scoring → Digest → Export → Email
  - Supports `--skip-scrape`, `--digest-only`, `--dry-run`
  - JSON output mode for programmatic use
  - PipelineResult object with summary stats
  - Configurable cities, days ahead, top N
- **Tested:** ✅ Dry-run, digest-only modes verified

### Phase 1.3: DB Schema Update ✅
- **Completed:** 2026-01-04T01:10:00Z
- **Changes:**
  - Added `workflow_status` column (new, scored, approved, rejected, registered)
  - Added index `idx_events_workflow_status`
  - Created view `v_pending_events` for pipeline operations
  - Backfilled existing events based on timestamps
- **Current distribution:**
  - `new`: 75 events
  - `scored`: 60 events

## Next Up (Phase 2: Bidirectional Sync)

1. **2.1:** Add sync endpoint to site server: decisions → DB
2. **2.2:** Create `sync_decisions_to_db.py` script
3. **2.3:** Update site to call sync on every decision

## Blockers

None currently.

## Commands Reference

```bash
# Full pipeline (discovery + scoring + digest)
python3 N5/scripts/luma_unified_pipeline.py

# Skip scraping, just score + digest
python3 N5/scripts/luma_unified_pipeline.py --skip-scrape

# Digest only from existing data
python3 N5/scripts/luma_unified_pipeline.py --digest-only --top 5

# Preview without changes
python3 N5/scripts/luma_unified_pipeline.py --dry-run

# Direct digest generation
python3 N5/scripts/luma_digest.py --preview --city nyc --num 5
```


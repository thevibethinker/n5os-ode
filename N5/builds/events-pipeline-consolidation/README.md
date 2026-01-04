---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
---

# Events Pipeline Consolidation

Consolidate bifurcated events tracking (alerts + site) into unified pipeline

## Objective

Single coordinated system with bidirectional sync, reliable digests, consolidated agents

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| worker_digest | luma_digest | pending | - | 2h |
| worker_pipeline | luma_unified_pipeline | pending | - | 3h |
| worker_sync | bidirectional_sync | pending | worker_pipeline | 2h |
| worker_agents | agent_consolidation | pending | worker_pipeline, worker_digest | 1h |
| worker_site | site_enhancements | pending | worker_sync | 2h |

## Key Decisions

- DB is SSOT - luma_events.db is source of truth, JSON exports are derived
- Status flow: new → scored → approved/rejected/maybe → registered
- Digest format: Top 5 events with scores, organizer trust, action links
- Single daily agent at 8am ET

## Relevant Files

- `N5/builds/events-pipeline-consolidation/PLAN.md`
- `N5/scripts/luma_scraper.py`
- `N5/scripts/luma_scorer.py`
- `N5/scripts/luma_email_discovery.py`
- `N5/config/luma_scoring.json`
- `N5/config/allowlists.json`
- `N5/data/luma_events.db`
- `Sites/events-calendar-staging/server.ts`

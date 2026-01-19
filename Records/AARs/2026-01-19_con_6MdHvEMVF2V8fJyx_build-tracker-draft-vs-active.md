---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_6MdHvEMVF2V8fJyx
conversation_id: con_6MdHvEMVF2V8fJyx
type: aar
tier: 3
---

# AAR: Build Tracker Draft vs Active Investigation

**Date:** 2026-01-19  
**Duration:** ~15 minutes  
**Type:** Debugging / Process Fix

## Summary

V noticed the Build Tracker dashboard wasn't clearly distinguishing between "draft" and "active" builds. Investigation confirmed the logic was correct, but revealed a process gap: single-thread builds (where Architect executes directly without workers) had no documented closure step, causing completed work to remain stuck in "draft" status.

## What Happened

1. **Initial Investigation**: Checked build-tracker dashboard at https://build-tracker-va.zocomputer.io/
2. **Verified Logic**: The `build_status.py` script correctly distinguishes:
   - **Draft**: `total_workers == 0` (plan exists, no workers defined)
   - **Active**: `total_workers > 0` AND `complete < total`
   - **Complete**: All workers done
3. **Found Gap**: `orchestrator-mece` had all work completed (deliverables created, checklist checked) but remained "draft" because nobody called `update_build.py close`
4. **Root Cause**: Single-thread builds bypass the worker completion flow, so there's no natural trigger for closure

## Actions Taken

1. **Fixed Process**: Added "Single-Thread Builds" section to `N5/prefs/operations/orchestrator-protocol.md` documenting:
   - When to use single-thread (< 5 files, < 30 min, low risk)
   - Execution flow including mandatory `update_build.py close` step
   - Common failure mode and prevention

2. **Closed `orchestrator-mece`**: Marked complete via `update_build.py close`

3. **Closed `notion-deals-sync`**: Marked abandoned (superseded by `crm-consolidation`)

## Artifacts Modified

| File | Change |
|------|--------|
| `N5/prefs/operations/orchestrator-protocol.md` | Added Single-Thread Builds section |
| `N5/builds/orchestrator-mece/meta.json` | status: draft → complete |
| `N5/builds/notion-deals-sync/meta.json` | status: draft → abandoned |
| `Sites/build-tracker/data/builds.json` | Regenerated with correct statuses |

## Key Insight

The build orchestrator system had good mechanics for multi-worker builds but lacked explicit guidance for the simpler case. When Architect executes directly, the "completion trigger" must be explicit — it won't happen automatically.

## What Went Well

- Dashboard logic was actually correct; just needed data refresh
- `build_status.py` already counts worker briefs in `workers/` directory when `meta.json` shows 0
- Quick identification of the process gap

## What Could Improve

- Architect persona should be updated to auto-close single-thread builds
- Consider adding a "stale draft" alert for builds with no activity > 7 days

## Follow-Up

- [ ] Consider updating Architect persona to mandate `update_build.py close` for single-thread builds
- [ ] Monitor for future "stuck draft" builds

## Tags

#build-tracker #process-fix #orchestrator #single-thread-builds

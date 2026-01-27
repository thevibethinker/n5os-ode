---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_T0QGg2ryaDjCTxVj
---

# Build Plan: pulse-dashboard-integration

## Open Questions

1. Should old-format builds (without `drops` key) still appear in dashboard? **Decision: Yes, with "legacy" badge**
2. Real-time updates via websocket or polling? **Decision: Polling (simpler, sufficient for now)**

---

## Objective

Integrate the new Pulse orchestration system with the existing Build Tracker dashboard (`Sites/build-tracker`) so V can monitor active builds visually.

---

## Alternatives Considered (Nemawashi)

### Option A: New Sync Script (Recommended)
- Create `Skills/pulse/scripts/pulse_dashboard_sync.py`
- Scans `N5/builds/*/meta.json` for Pulse-format builds
- Generates `builds.json` compatible with dashboard
- Dashboard calls on `/api/refresh`

**Pros:** Clean separation, reusable, follows existing pattern
**Cons:** Requires dashboard server update

### Option B: Direct Database Read
- Dashboard reads `N5/data/conversations.db` directly
- Joins with `meta.json` files

**Pros:** Real-time data
**Cons:** Couples dashboard to internal DB schema, more complex

### Option C: Replace Dashboard Entirely
- Build new Pulse-native dashboard from scratch

**Pros:** Clean slate
**Cons:** Wasteful—existing dashboard works, just needs new data source

**Decision: Option A** — simplest path, preserves existing investment

---

## Trap Doors

| Decision | Reversible? | Risk |
|----------|-------------|------|
| Terminology change (workers→drops) | ✅ Easy | Just string replacement |
| Data format change | ✅ Easy | Both formats can coexist |
| Delete old `build_status.py` | ⚠️ Already done | N/A - already deleted |

---

## Checklist

### Stream 1: Backend
- ☐ D1.1: Create `pulse_dashboard_sync.py` script
- ☐ D1.2: Update `server.ts` to call new sync script

### Stream 2: Frontend
- ☐ D2.1: Update React components for Pulse terminology

---

## Stream 1: Backend Integration

### D1.1: Sync Script

**Affected Files:**
- `Skills/pulse/scripts/pulse_dashboard_sync.py` (CREATE)

**Changes:**
1. Scan `N5/builds/*/meta.json` for files with `drops` key (new format)
2. Also scan for old format (with `workers/` folder) and mark as "legacy"
3. Generate `Sites/build-tracker/data/builds.json` with unified schema:
   ```json
   {
     "generated_at": "ISO timestamp",
     "builds": [
       {
         "slug": "...",
         "title": "...",
         "status": "pending|active|complete|failed",
         "format": "pulse|legacy",
         "streams": { "current": 1, "total": 2 },
         "drops": {
           "complete": 2,
           "running": 1,
           "pending": 3,
           "dead": 0,
           "failed": 0,
           "total": 6
         },
         "progress_pct": 33,
         "created_at": "...",
         "last_activity": "..."
       }
     ]
   }
   ```
4. CLI: `python3 pulse_dashboard_sync.py [--output PATH]`

**Unit Tests:**
- Run with empty builds dir → generates empty array
- Run with one Pulse build → correct format
- Run with mixed old/new → both appear with correct `format` flag

### D1.2: Server Update

**Affected Files:**
- `Sites/build-tracker/server.ts` (MODIFY)

**Changes:**
1. Update `/api/refresh` endpoint to call `pulse_dashboard_sync.py` instead of `build_status.py`
2. Keep `/api/builds` endpoint unchanged (reads from `builds.json`)

**Unit Tests:**
- Hit `/api/refresh` → new script runs, returns success
- Hit `/api/builds` → returns updated data

---

## Stream 2: Frontend Updates

### D2.1: Component Updates

**Affected Files:**
- `Sites/build-tracker/src/components/BuildCard.tsx` (MODIFY)
- `Sites/build-tracker/src/pages/BuildsPage.tsx` (MODIFY)

**Changes:**
1. Rename "Workers" → "Drops" in UI
2. Rename "Waves" → "Streams" in UI
3. Add badge for `format: "legacy"` builds
4. Update progress display: "Stream X/Y" instead of "Wave X/Y"
5. Show Drop status breakdown (complete/running/pending/dead/failed)

**Unit Tests:**
- Render BuildCard with Pulse data → shows Drops terminology
- Render BuildCard with legacy data → shows "Legacy" badge

---

## Success Criteria

- [ ] `pulse_dashboard_sync.py --help` works
- [ ] Running sync generates valid `builds.json`
- [ ] Dashboard shows `pulse-validation` build (if exists)
- [ ] Legacy builds appear with badge
- [ ] `/api/refresh` triggers sync successfully
- [ ] No console errors in browser

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Script path wrong in server.ts | Medium | Build fails | Verify path before commit |
| Frontend breaks on new schema | Low | Dashboard down | Test locally first |
| Old builds missing data | Medium | Incomplete display | Graceful fallbacks in sync script |

---

## MECE Validation

| Scope Item | Owner |
|------------|-------|
| `pulse_dashboard_sync.py` | D1.1 |
| `server.ts` changes | D1.2 |
| `BuildCard.tsx` changes | D2.1 |
| `BuildsPage.tsx` changes | D2.1 |

- No overlaps ✓
- No gaps ✓
- 3 Drops total (reasonable scope)

---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_fqLDr1f1Cc7X5sgZ
---

# Performance Dashboard v2 Debug Report

## Summary

Comprehensive QA validation completed for Performance Dashboard v2. Found and fixed **3 bugs** in the dashboard display logic.

## Bugs Found & Fixed

### Bug 1: Gap Day Display Truncation
**Location:** `performance_dashboard.py` line ~227  
**Problem:** `gap.get('day', '')[:3]` was slicing ISO date string `"2026-01-24"` to get `"202"` instead of converting to weekday name.  
**Fix:** Added `datetime.strptime()` conversion to get abbreviated weekday name (e.g., "Sat").

### Bug 2: Net Change Backlog Logic Inverted
**Location:** `performance_dashboard.py` line ~251  
**Problem:** When `net_change = completed - added`:
- Positive = clearing backlog (completed more than added)
- Negative = adding to backlog (added more than completed)

The display showed the opposite: "clearing backlog" when `net < 0`.

**Fix:** Corrected the conditional: `" (clearing backlog)" if net > 0 else " (adding to backlog)" if net < 0`.

### Bug 3: Signal Detection Same Inversion
**Location:** `performance_dashboard.py` line ~113  
**Problem:** The "✓ Clearing backlog" signal was triggered when `net_change < 0`, which is the wrong condition.  
**Fix:** Changed to `if tasks.get('net_change', 0) > 0:`.

## Data Flow Validation

| Data Source | Status | Data Points | Notes |
|-------------|--------|-------------|-------|
| Resting HR | ✓ OK | 6/7 days | From workouts.db |
| Activity | ✓ OK | 7/7 days | From workouts.db |
| Sleep | ✓ OK | 5/7 days | From workouts.db |
| Tasks | ✓ OK | N/A | From tasks.db |
| Content | ✓ OK | N/A | From content_library.db |
| Mood | ⚠️ Empty | 0 | No recent journal entries |
| Weather | ✓ OK | 8 days | From Open-Meteo API |
| Calendar | ✓ OK | 19 events | From calendar cache |

## Integration Tests

### Weather Integration (Open-Meteo API)
- ✓ API returns data for past 7-16 days
- ✓ Temperature unit correctly set to Fahrenheit
- ✓ Precipitation conversion mm→inches working
- ✓ WMO weather codes mapped to descriptions/emojis

### Calendar Integration
- ✓ Cache exists and recent (< 24 hours)
- ✓ [SKIP] tag filtering working
- ✓ Fragmentation calculation produces valid 0-1 scores
- ✓ Back-to-back detection working

### Signal Detection
- ✓ Low sleep detection triggers for < 6 hours
- ✓ RHR spike detection triggers for > avg + 5
- ✓ Low completion rate warning for < 50%
- ✓ Calendar fragmentation warning for > 0.6
- ✓ Positive signals for high activity, workout consistency

## Files Modified

1. `N5/scripts/performance_dashboard.py` - 3 bug fixes applied

## Sample Output (Post-Fix)

```
┌─ CALENDAR LOAD ─────────────────────────────────────────────────────┐
│  Back-to-back    2 instances    Longest gap: 8.2 hrs (Sat )          │
└──────────────────────────────────────────────────────────────────────┘

┌─ COGNITIVE/OUTPUT ──────────────────────────────────────────────────┐
│  Tasks Added        44 new          Net: -42 (adding to backlog)     │
└──────────────────────────────────────────────────────────────────────┘

┌─ SIGNALS ───────────────────────────────────────────────────────────┐
│  ⚠️  Low sleep on Mon (2.4 hrs)                                      │
│  ⚠️  Low task completion rate (4%)                                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Recommendations

1. **Mood data gap:** Consider adding bio-log prompts more frequently to populate mood tracking.
2. **Calendar cache refresh:** Scheduled task should update cache before dashboard generation.
3. **Missing calendar window:** The `longest_gap.window` field isn't being populated by calendar_metrics.py - could add time range display.

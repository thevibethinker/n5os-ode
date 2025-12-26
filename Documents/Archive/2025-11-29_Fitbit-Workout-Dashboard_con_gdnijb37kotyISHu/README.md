---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Fitbit Workout Dashboard Build

**Conversation:** con_gdnijb37kotyISHu  
**Date:** 2025-11-29  
**Duration:** ~1.5 hours  
**Status:** Completed

## Summary

Built a complete Fitbit-powered workout tracking and visualization system with:
- SQLite database schema for workouts, resting heart rate, and sleep
- Fitbit API sync scripts (OAuth2 flow, activity/HR/sleep endpoints)
- Matplotlib-based dashboard generator with 5 graph types
- Flask web UI for browser-based dashboard access
- Hosted as a persistent user service at https://workout-dashboard-va.zocomputer.io

## Goals Configured

- Weekly exercise minutes target: 90 minutes
- Weekly workout days target: 2 days
- No critical modalities (general fitness focus)

## What Was Built

### Core Scripts (Personal/Health/WorkoutTracker/)

1. **workout_tracker.py** - Database schema and helpers
   - `workouts` table (existing, extended)
   - `daily_resting_hr` table (new)
   - `daily_sleep` table (new)
   - Upsert helpers for all three

2. **fitbit_sync.py** - Fitbit API integration
   - OAuth2 flow (start-auth, finish-auth)
   - Activity sync (workout logs)
   - Resting heart rate sync (date range)
   - Sleep sync (daily sleep logs)
   - Token refresh handling

3. **workout_dashboard.py** - Graph generation
   - Weekly minutes vs goal (bar chart)
   - Weekly workout days vs goal (bar chart)
   - Rolling 7-day minutes (line chart)
   - Resting HR trend (line chart, ~60 days)
   - Sleep duration trend (line chart, ~60 days)

4. **dashboard_server.py** - Flask web UI
   - Auto-regenerates graphs on page load
   - Serves PNG graphs from /graphs/ directory
   - Displays text summaries

### Generated Graphs (Personal/Health/WorkoutTracker/graphs/)

- weekly_minutes.png
- weekly_days.png
- rolling_7d_minutes.png
- resting_hr_trend.png
- sleep_duration_trend.png

### User Service

- **Label:** workout-dashboard
- **URL:** https://workout-dashboard-va.zocomputer.io
- **Port:** 8010

## Data Synced

As of conversation end:
- 75 resting HR data points
- 20 sleep data points (minutes asleep/in bed)
- 20 workout records

## Known Limitations

- Fitbit API rate limit: 150 requests/hour per user
- Sleep score not available via API (Premium-only feature in Fitbit app)
- Sleep data shows minutes_asleep and minutes_in_bed, not sleep score

## Commands

```bash
# Sync recent Fitbit data (30 days)
python3 Personal/Health/WorkoutTracker/fitbit_sync.py sync-recent --days 30

# Regenerate dashboard graphs
python3 Personal/Health/WorkoutTracker/workout_dashboard.py --weeks 12 --weekly-minutes-goal 90 --weekly-days-goal 2

# Re-authenticate (if tokens expire)
python3 Personal/Health/WorkoutTracker/fitbit_sync.py start-auth
# Then follow URL, paste redirect URL back:
python3 Personal/Health/WorkoutTracker/fitbit_sync.py finish-auth --redirect-url 'https://localhost/...'
```

## Related Files

- `file 'Personal/Health/workouts.db'` - SQLite database
- `file 'Personal/Health/WorkoutTracker/fitbit_config.json'` - OAuth credentials

## Future Enhancements

- Per-modality breakdown graphs (walk vs strength vs cardio)
- Scheduled agent for daily/weekly sync + dashboard regeneration
- Markdown summary file auto-generation
- Sleep score if Fitbit ever exposes it via API


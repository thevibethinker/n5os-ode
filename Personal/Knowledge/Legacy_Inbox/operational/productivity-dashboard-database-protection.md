---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Productivity Dashboard Database Protection

## Critical File Location

**File:** `/home/workspace/productivity_tracker.db`  
**Purpose:** Production SQLite database for Arsenal Productivity Dashboard  
**Service:** productivity-dashboard (svc_J6eAPxM04_4)  
**Public URL:** https://productivity-dashboard-va.zocomputer.io

## ⚠️ DO NOT MOVE OR DELETE THIS FILE

This database MUST remain at `/home/workspace/productivity_tracker.db` for the dashboard service to function.

## Issue History

The database has been inadvertently moved or reset **THREE TIMES**:

1. **First incident:** Database moved from `/home/workspace/` → unknown location
2. **Second incident:** Database moved again
3. **Third incident (2025-11-03):** Database file present but schema/data missing

### Root Cause Unknown

The exact mechanism causing the database to be moved or cleared is still under investigation. Suspected culprits:
- Daily File Guardian task (runs 9:30 AM daily)
- File Flow Router (runs 7:00 AM daily) 
- Weekly Cleanup (runs Monday 7:00 AM)
- Other automated maintenance scripts

## Recovery Process

When the database is missing or empty:

1. **Check for copies:**
   - `/home/workspace/Records/Personal/productivity_tracker.db` (last known good: Oct 27, 2025)
   - `/home/workspace/N5/data/productivity_tracker.db`
   
2. **Restore from Records:**
   ```bash
   cp /home/workspace/Records/Personal/productivity_tracker.db /home/workspace/productivity_tracker.db
   ```

3. **Verify schema:**
   ```bash
   sqlite3 /home/workspace/productivity_tracker.db ".schema daily_stats"
   ```

4. **Restart service:**
   Update the RESTART env var in the productivity-dashboard service

5. **Test dashboard:**
   ```bash
   curl -s https://productivity-dashboard-va.zocomputer.io | head -20
   ```

## Prevention Measures

1. **Workspace root protection marker:** Created `/home/workspace/.n5_productivity_protected`
2. **This documentation:** Warns future AI instances about the issue
3. **Investigation needed:** Identify and fix the automation that's moving the file

## Database Schema

The database contains:
- `daily_stats` - Daily productivity metrics
- `team_status_history` - Team status tracking
- `career_stats` - Career-level aggregations

## Related Files

- Dashboard code: `file 'Sites/productivity-dashboard/index.tsx'`
- Scanner scripts: `file 'N5/scripts/productivity/'`
- Service config: productivity-dashboard user service

## Action Items

- [ ] Identify which automated script is moving/clearing the database
- [ ] Add explicit exclusion rules to that script
- [ ] Consider moving to a protected directory like N5/data or Personal/Data
- [ ] Set up automated backup/verification of this file

---

**Last incident:** 2025-11-03  
**Times recovered:** 3  
**Status:** Protected by documentation, investigation ongoing

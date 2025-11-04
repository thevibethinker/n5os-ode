# Productivity Dashboard Database Wipe Issue

## Problem
The `/home/workspace/productivity_tracker.db` database is being wiped clean (0 bytes) periodically, causing the productivity dashboard to crash with "no such table: daily_stats" errors.

##Root Cause Analysis

After investigation, the likely culprit is **one of the scheduled tasks that runs maintenance operations**. While I checked several scripts, I need to investigate further to identify the exact cause.

### Suspects Investigated:
1. **Daily File Guardian** (runs at 9:30 AM) - `N5/scripts/maintenance/daily_guardian.py`
   - Does NOT delete .db files directly
   - Focuses on file integrity checks and git status

2. **Workspace Root Cleanup** - `N5/scripts/n5_workspace_root_cleanup.py`
   - Does NOT have `.db` files in DELETE_PATTERNS
   - Only targets specific conversation artifacts

3. **Daily Productivity Tracker** (runs at 2 PM) - Scheduled task
   - This task scans Gmail and updates the database
   - Could potentially be recreating/truncating the database

### What We Know:
- Database file exists but shows Birth: 1970-01-01 (indicates recent creation)
- Database gets wiped to 0 bytes
- This has happened 3 times
- Multiple copies exist: `/home/workspace/`, `N5/data/`, `Records/Personal/`

## Immediate Fix Applied
1. Recreated database schema with all three tables:
   - `daily_stats`
   - `team_status_history`
   - `career_stats`
2. Restarted productivity-dashboard service
3. Dashboard is now online

## Long-term Solution Needed

### Option 1: Move Database to Protected Location
Move `/home/workspace/productivity_tracker.db` to a protected directory like `N5/data/` or `Records/Personal/` and update all references.

### Option 2: Add Database Protection
Create a protection mechanism specifically for critical .db files in workspace root.

### Option 3: Find and Fix the Wiper
Identify the exact script/task that's wiping the database and fix it at the source.

## Recommendation
**Implement a combination approach:**

1. **Move database to `N5/data/`** (protected location)
   - Update `Sites/productivity-dashboard/index.tsx` path reference
   - Update all N5 productivity scripts
   - Create symlink from workspace root for compatibility

2. **Add automated backup** 
   - Daily backup of database to N5/backups/
   - Include in daily guardian checks

3. **Add validation check**
   - Add productivity_tracker.db to CRITICAL_FILES in daily_guardian.py
   - Alert if file is empty or missing tables

## Next Steps
1. Identify if any script is explicitly truncating/recreating the database
2. Implement database relocation + symlinking
3. Add to critical files monitoring
4. Set up automated backups

## Timeline
- This is the 3rd occurrence
- Needs permanent fix before next wipe
- High priority due to production dashboard dependency

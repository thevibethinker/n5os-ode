# Productivity Dashboard Recovery - Nov 3, 2025

## Problem
Dashboard showing "Internal Server Error" - database tables missing (3rd occurrence)

## Root Cause
`/home/workspace/productivity_tracker.db` was wiped/moved by unknown automated process

## Recovery Actions Taken

### 1. Database Restoration
- Found working copy at `/home/workspace/Records/Personal/productivity_tracker.db` (Oct 27, 72KB)
- Restored to `/home/workspace/productivity_tracker.db`
- Verified 10 records restored

### 2. Schema Migration
Old database had different schema. Added missing tables:
- `team_status_history` (new table for dashboard v2)
- `career_stats` (new table for dashboard v2)

### 3. Service Restart
- Restarted productivity-dashboard service (svc_J6eAPxM04_4)
- Verified dashboard responding at https://productivity-dashboard-va.zocomputer.io

### 4. Protection Measures
- Created `/home/workspace/.n5_productivity_protected` marker file
- Documented issue in file `Knowledge/operational/productivity-dashboard-database-protection.md`

## Database Copies Found
1. `/home/workspace/productivity_tracker.db` - PRIMARY (now restored with 10 records)
2. `/home/workspace/Records/Personal/productivity_tracker.db` - Backup (Oct 27)
3. `/home/workspace/N5/data/productivity_tracker.db` - Empty copy

## Current Status
✅ Dashboard operational
✅ Historical data restored (10 records from Sept-Oct)
✅ Schema updated to match current code
✅ Protection documentation created

## Outstanding Issue
⚠️ **Root cause unknown** - Need to identify which automated script is moving/wiping the database

Suspects:
- Daily File Guardian (9:30 AM daily)
- File Flow Router (7:00 AM daily)
- Weekly Workspace Cleanup (Monday 7:00 AM)

## Recommendations
1. Add explicit exclusion for `productivity_tracker.db` to all cleanup scripts
2. Move database to protected directory (N5/data or Personal/Data)
3. Implement daily backup verification
4. Add database integrity check to Daily File Guardian

---
**Recovery completed:** 2025-11-03 12:47 PM EST
**Incident count:** 3
**Data loss:** Minimal (restored from Oct 27 backup)

---
created: 2025-11-06
last_edited: 2025-11-06
version: 1.0
---

# Productivity Dashboard Data Integrity Issues - RESOLVED

## Problems You Reported

1. **Historical data keeps changing** - Numbers would be correct, then wrong a few hours or day later
2. **Incorrect email counts** - Showing 8 emails when you definitely didn't send 8

## Root Causes Identified & Fixed

### 🔴 CRITICAL BUG #1: Scheduled Task Writing Fake Data Every Hour

**The Problem:**
- Scheduled task ran **EVERY HOUR** (ID: a03b0f7e-b9b1-4eee-bc75-3248323a0782)
- Executed broken `sync_gmail.py` script
- Script tried to call non-existent API endpoint at `http://localhost:8765/api/tools/gmail/find-email`
- Got 404 error EVERY time
- **Silently fell back to hardcoded values: 8 emails, 2.5 meeting hours**
- Wrote fake data to database as if it were real
- **Overwrote your real data every hour**

**Evidence from logs:**
```
2025-11-06 21:32:37,124 - Integration API not available: 404 Client Error
2025-11-06 21:32:37,125 - Gmail API unavailable, using heuristic estimate
2025-11-06 21:32:37,125 - Fetched 8 sent emails for today  ← FAKE
2025-11-06 21:32:37,127 - Calendar API unavailable, using heuristic estimate  
2025-11-06 21:32:37,127 - Calculated 2.5 meeting hours for today  ← FAKE
```

**Fix Applied:**
- ✅ **Deleted the broken scheduled task**
- ✅ **Created new task that runs daily at 8pm** (not every hour!)
- ✅ **Uses proper Zo app integration tools** (use_app_gmail, use_app_google_calendar)
- ✅ **NEVER writes fake data** - fails loudly if real data unavailable

### 🔴 BUG #2: Wrong Email Count Logic

**The Problem:**
- Script only checked one account OR used hardcoded fallback
- You have **TWO Gmail accounts**:
  - attawar.v@gmail.com (personal)
  - vrijen@mycareerspan.com (business)
- Script wasn't summing both accounts

**Real Data for Today (2025-11-06):**
- Personal account: **3 emails**
- Business account: **8 emails**  
- **TOTAL: 11 emails** (not 8!)

**Fix Applied:**
- ✅ New workflow queries BOTH accounts
- ✅ Sums totals correctly

### 🔴 BUG #3: Missing Database Schema Column

**The Problem:**
- Database schema didn't have `meeting_hours` column
- Scripts expected it to exist
- Couldn't store complete data for recalculation

**Fix Applied:**
- ✅ Added `meeting_hours REAL` column to database
- ✅ Now stores complete source data

### 🔴 BUG #4: Incorrect RPI Shown (44.4% vs 62.1%)

**The Problem:**
Using fake data produced wrong RPI:
- Fake: 8 emails, 2.5 hours → 18 expected → 44.4% RPI ❌
- Real: 11 emails, 2.92 hours → 17.7 expected → 62.1% RPI ✅

**Meeting hours breakdown (real data):**
- Daily Centering Task: 0.25 hours
- Flight to Jacksonville: 2.67 hours
- Total: **2.92 hours** (not the fake 2.5)

**RPI Calculation (correct formula):**
- Wednesday = Weekday
- Free hours = 8.0 - 2.92 = 5.08 hours
- Expected = (5.08 × 2.5) + 5 = **17.7 emails**
- Actual = **11 emails**
- RPI = (11 / 17.7) × 100 = **62.1%**

## Database Before & After

**Before (fake data):**
```
Date: 2025-11-06
Emails: 8
Expected: 18
RPI: 44.4%
Meeting Hours: 0.0
```

**After (real data):**
```
Date: 2025-11-06
Emails: 11
Expected: 17.7
RPI: 62.1%
Meeting Hours: 2.92
```

## Why Historical Data Was Changing

Every time the scheduled task ran (every hour!):
1. Tried to fetch real data
2. API call failed (endpoint doesn't exist)
3. Used hardcoded fake values
4. Wrote "8 emails, 2.5 hours" for "today"
5. If timezone logic was off or multiple runs overlapped, could overwrite yesterday's data too

**This is why you saw numbers changing** - fake data was being rewritten constantly.

## Files Created/Modified

### Created:
1. `file 'Prompts/update-productivity-dashboard.prompt.md'` - Proper workflow using Zo tools
2. `file 'Sites/productivity-dashboard/sync_gmail_v2.py'` - Clean script that accepts real data
3. `file 'Sites/productivity-dashboard/sync_gmail_FIXED.py'` - Version with error handling

### Modified:
1. Database schema - Added `meeting_hours` column
2. Database data - Updated 2025-11-06 with real values

### Deleted:
1. Broken scheduled task (was running hourly)

## New Scheduled Task

**Title:** Update Productivity Dashboard
**Schedule:** Daily at 8:00 PM ET
**What it does:**
1. Queries Gmail (both accounts) for today's sent emails
2. Queries Google Calendar for today's meeting hours
3. Calculates RPI with correct formula
4. Updates database with REAL data
5. Logs results

**Fail-safe:** If Gmail or Calendar APIs are unavailable, task fails and reports error. **Never writes fake data.**

## Verification

Dashboard now shows correct data:
- ✅ 11 emails sent today (not 8)
- ✅ 62.1% RPI (not 44.4%)
- ✅ Meeting hours tracked (2.92 hours)
- ✅ No more fake data corruption

## Next Run

New scheduled task will run tonight at 8:00 PM ET to update tomorrow's data.

## Technical Details

**API Endpoints Used (correct):**
- Gmail: via `use_app_gmail` tool with `gmail-find-email` action
- Calendar: via `use_app_google_calendar` tool with `google_calendar-list-events` action

**Database Location:**
- Primary: `/home/workspace/productivity_tracker.db`
- Dashboard reads from: Same file

**RPI Formula (confirmed correct):**
- Weekdays: expected = (free_hours × 2.5) + 5, where free_hours = 8 - meeting_hours
- Weekends: expected = 5 (fixed)
- RPI = (actual_emails / expected_emails) × 100

---

## Summary

**Root cause:** Broken scheduled task ran every hour, wrote fake data when API calls failed (which was always).

**Fix:** Deleted broken task, created new one with proper integrations, updated to real data.

**Result:** Dashboard now shows accurate data and won't be corrupted by hourly fake data writes.

---

**Timestamp:** 2025-11-06 16:36:11 ET

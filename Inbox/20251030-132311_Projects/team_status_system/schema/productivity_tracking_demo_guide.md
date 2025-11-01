# N5 Productivity Tracking System - Demo Guide
**Prepared for:** Video Recording  
**Date:** 2025-10-30  
**Status:** Ready for Demo

---

## System Overview

The N5 Productivity Tracking System is an intelligent productivity monitoring solution that:
- Tracks email output from Gmail
- Monitors meeting load from Google Calendar
- Calculates a Relative Productivity Index (RPI)
- Provides gamification with XP, levels, and streaks
- Displays real-time metrics via web dashboard

---

## Live Components

### 1. Web Dashboard
**URL:** https://productivity-dashboard-va.zocomputer.io  
**Local:** http://localhost:3000

**Features:**
- Real-time RPI display
- Arsenal FC themed design (red gradient)
- Email count and word count tracking
- Mobile-responsive layout
- API endpoints for data access

**API Endpoints:**
- `/` - Dashboard UI
- `/api/today` - Today's stats (JSON)
- `/api/week` - Last 7 days (JSON)

---

### 2. Database Schema
**Location:** `/home/workspace/productivity_tracker.db`

**Tables:**

**`daily_stats` (Primary Display)**
```sql
- date (UNIQUE)
- emails_sent
- expected_emails
- rpi (percentage)
- xp_earned
- level
- streak_days
- xp_multiplier
```

**`sent_emails` (Input)**
```sql
- gmail_id (UNIQUE)
- date
- subject
- word_count
- subject_category
```

**`expected_load` (Input)**
```sql
- date
- source (e.g., "google_calendar")
- hours (meeting hours)
- title
```

**`xp_ledger` (Transactions)**
```sql
- date
- xp_value
- source
- description
```

---

### 3. Core Scripts

**Location:** `file 'N5/scripts/productivity/'`

**`rpi_calculator.py` (Intelligence Layer)**
- Calculates RPI: `(actual_emails / expected_emails) × 100`
- Expected formula: `(meeting_hours × 3) + 5`
- Updates daily_stats with RPI, XP, level, streak
- Supports backfill and recalculation

**Usage:**
```bash
# Calculate today
python3 N5/scripts/productivity/rpi_calculator.py

# Specific date
python3 N5/scripts/productivity/rpi_calculator.py --date 2025-10-29

# Backfill baseline expectations
python3 N5/scripts/productivity/rpi_calculator.py --backfill --dry-run
python3 N5/scripts/productivity/rpi_calculator.py --backfill

# Recalculate historical
python3 N5/scripts/productivity/rpi_calculator.py --recalculate --dry-run
python3 N5/scripts/productivity/rpi_calculator.py --recalculate
```

**`email_scanner.py` (Data Collection)**
- Connects to Gmail API
- Scans sent emails
- Extracts word counts
- Categorizes by subject
- Updates sent_emails table

**`meeting_scanner.py` (Load Tracking)**
- Connects to Google Calendar API
- Scans scheduled meetings
- Calculates total meeting hours
- Updates expected_load table

**`xp_system.py` (Gamification)**
- Tracks XP transactions
- Calculates level progression: `level = floor(sqrt(total_xp / 100)) + 1`
- Manages XP multipliers based on performance
- Updates xp_ledger table

**`unreplied_tracker.py` (Follow-up)**
- Identifies unreplied threads
- Generates follow-up lists
- Tracks response rates

**`db_setup.py` (Infrastructure)**
- Creates database schema
- Initializes tables
- Sets up indexes

---

## RPI Performance Tiers

| RPI Range | Tier | XP Multiplier | Icon |
|-----------|------|---------------|------|
| ≥150% | Invincible Form | 1.5× | 🔥 |
| 125-150% | Top Performance | 1.25× | ⭐ |
| 100-125% | Meeting Expectations | 1.0× | ✅ |
| 75-100% | Catch Up Needed | 0.9× | ⚠️ |
| <75% | Behind Schedule | 0.75× | 🔻 |

---

## Recent Performance

```
Date       | Sent | Expected | RPI   | Level | Streak
-----------|------|----------|-------|-------|-------
2025-10-30 | 0    | 5.0      | 0.0%  | 1     | 0
2025-10-29 | 9    | 5.0      | 180%  | 1     | 1
```

---

## Demo Flow Recommendations

### Opening Shot
1. Show the dashboard at https://productivity-dashboard-va.zocomputer.io
2. Highlight the Arsenal theme and clean design
3. Point out RPI score and performance tier

### Terminal View
1. Show the database location: `productivity_tracker.db`
2. Run a quick query:
   ```bash
   sqlite3 productivity_tracker.db "SELECT date, emails_sent, ROUND(rpi,1) as rpi, level, streak_days FROM daily_stats ORDER BY date DESC LIMIT 7"
   ```

### Script Execution
1. Run RPI calculator:
   ```bash
   python3 N5/scripts/productivity/rpi_calculator.py
   ```
2. Show the output with performance tier
3. Explain the intelligence layer

### Architecture Overview
1. Show the scripts directory: `ls N5/scripts/productivity/`
2. Open `file 'N5/scripts/productivity/README.md'` for documentation
3. Explain the data flow:
   - Gmail/Calendar → Scanners → Database
   - RPI Calculator → Intelligence → Dashboard

### API Demo (Optional)
1. Hit the API endpoint:
   ```bash
   curl http://localhost:3000/api/today | jq
   ```
2. Show the JSON structure
3. Demonstrate week view:
   ```bash
   curl http://localhost:3000/api/week | jq
   ```

### Deep Dive (Optional)
1. Show the RPI formula explanation
2. Demonstrate backfill functionality
3. Explain streak system logic
4. Show XP progression table

---

## Key Talking Points

1. **Intelligent Baseline:** Not just counting emails - calculates expected output based on meeting load
2. **Context-Aware:** Adapts expectations to your calendar (heavy meeting day = higher expected emails)
3. **Gamification:** XP system, levels, streaks, multipliers make productivity tracking engaging
4. **Real-Time Dashboard:** Always-on web interface with clean, branded design
5. **Data-Driven:** SQLite backend with complete audit trail
6. **API-First:** JSON endpoints enable future integrations
7. **Flexible:** Supports historical recalculation and backfilling

---

## Files to Reference During Demo

- `file 'Sites/productivity-dashboard/index.tsx'` - Dashboard code
- `file 'N5/scripts/productivity/rpi_calculator.py'` - Core intelligence
- `file 'N5/scripts/productivity/README.md'` - Documentation
- Database: `/home/workspace/productivity_tracker.db`

---

## Quick Commands Reference

```bash
# View dashboard
open https://productivity-dashboard-va.zocomputer.io

# Calculate today's RPI
python3 N5/scripts/productivity/rpi_calculator.py

# Check recent stats
sqlite3 productivity_tracker.db "SELECT date, emails_sent, ROUND(rpi,1), level FROM daily_stats ORDER BY date DESC LIMIT 5"

# API check
curl http://localhost:3000/api/today | jq

# View logs
tail -f /dev/shm/productivity-dashboard.log
```

---

## Service Information

**Service Label:** productivity-dashboard  
**Service ID:** svc_J6eAPxM04_4  
**Port:** 3000  
**Public URL:** https://productivity-dashboard-va.zocomputer.io  
**Status:** ✅ Running

---

## Additional Context

### Related Documentation
- `file 'Documents/n5-productivity-integrations-roadmap.md'` - Future enhancements
- `file 'Knowledge/architectural/productivity_ai_age_philosophy.md'` - Design philosophy

### System Integration
- Gmail API for email tracking
- Google Calendar API for meeting load
- SQLite for data persistence
- Bun + Hono for web server
- Arsenal FC branding (red/white theme)

---

**Last Updated:** 2025-10-30 01:02 ET  
**Demo Ready:** ✅ Yes  
**All Systems:** ✅ Operational

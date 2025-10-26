# Productivity Tracking System

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** 2025-10-26

---

## Components

### Worker 1: Database Setup
**Script:** `db_setup.py`  
**Status:** ✅ Complete  
**Purpose:** SQLite database schema and tables

### Worker 2: Email Scanner
**Script:** `email_scanner.py`  
**Status:** ✅ Complete  
**Purpose:** Tracks sent emails from Gmail

### Worker 3: Meeting Scanner
**Script:** `meeting_scanner.py`  
**Status:** ✅ Complete  
**Purpose:** Scans Google Calendar for expected load

### Worker 4: XP System
**Script:** `xp_system.py`  
**Status:** ✅ Complete  
**Purpose:** Gamification layer with XP, levels, multipliers

### Worker 5: RPI Calculator
**Script:** `rpi_calculator.py`  
**Status:** ✅ Complete  
**Purpose:** Intelligence layer calculating Relative Productivity Index

---

## Quick Start: RPI Calculator

### Calculate RPI for Today
```bash
python3 N5/scripts/productivity/rpi_calculator.py
```

### Calculate RPI for Specific Date
```bash
python3 N5/scripts/productivity/rpi_calculator.py --date 2025-10-26
```

### Backfill Baseline Expectations
```bash
# Dry run first (recommended)
python3 N5/scripts/productivity/rpi_calculator.py --backfill --dry-run

# Actual backfill
python3 N5/scripts/productivity/rpi_calculator.py --backfill
```

### Recalculate All Historical RPI
```bash
# Dry run first (recommended)
python3 N5/scripts/productivity/rpi_calculator.py --recalculate --dry-run

# Actual recalculation
python3 N5/scripts/productivity/rpi_calculator.py --recalculate
```

---

## Understanding RPI

### Formula
```
RPI = (actual_emails / expected_emails) × 100

Where:
  expected_emails = (meeting_hours × 3) + 5
  
  - 3 emails/hour: Meeting follow-up assumption
  - 5 emails/day: Baseline minimum expectation
```

### Performance Tiers

| RPI Range | Tier | XP Multiplier | Icon |
|-----------|------|---------------|------|
| ≥150% | Invincible Form | 1.5× | 🔥 |
| 125-150% | Top Performance | 1.25× | ⭐ |
| 100-125% | Meeting Expectations | 1.0× | ✅ |
| 75-100% | Catch Up Needed | 0.9× | ⚠️ |
| <75% | Behind Schedule | 0.75× | 🔻 |

### Examples

**Scenario 1: Light Meeting Day**
- Meeting load: 1 hour
- Expected: (1 × 3) + 5 = 8 emails
- Actual: 12 emails sent
- RPI: (12 / 8) × 100 = **150% (Invincible Form 🔥)**

**Scenario 2: Heavy Meeting Day**
- Meeting load: 6 hours
- Expected: (6 × 3) + 5 = 23 emails
- Actual: 18 emails sent
- RPI: (18 / 23) × 100 = **78% (Catch Up Needed ⚠️)**

**Scenario 3: No Meetings**
- Meeting load: 0 hours
- Expected: (0 × 3) + 5 = 5 emails (baseline)
- Actual: 8 emails sent
- RPI: (8 / 5) × 100 = **160% (Invincible Form 🔥)**

---

## Streak System

### Rules
A streak continues when:
1. Current day has `emails_sent > 0`
2. Previous day had `emails_sent > 0` AND `rpi >= 80%`
3. Days are consecutive (no gaps)

A streak breaks when:
- Current day has `emails_sent == 0`
- Previous day had `rpi < 80%`
- There's a gap in dates

---

## Level Progression

Levels are calculated from cumulative XP:

```python
level = floor(sqrt(total_xp / 100)) + 1
```

### Example Progression
| Total XP | Level |
|----------|-------|
| 0-99 | 1 |
| 100-399 | 2 |
| 400-899 | 3 |
| 900-1599 | 4 |
| 1600-2499 | 5 |

---

## Database Queries

### View Recent RPI
```sql
SELECT 
    date,
    emails_sent,
    ROUND(expected_emails, 1) as expected,
    ROUND(rpi, 1) as rpi_pct,
    xp_earned,
    level,
    streak_days
FROM daily_stats
ORDER BY date DESC
LIMIT 10;
```

### View RPI Distribution
```sql
SELECT 
    CASE 
        WHEN rpi >= 150 THEN 'Invincible (≥150%)'
        WHEN rpi >= 125 THEN 'Top Performance (125-150%)'
        WHEN rpi >= 100 THEN 'Meeting Expectations (100-125%)'
        WHEN rpi >= 75 THEN 'Catch Up Needed (75-100%)'
        ELSE 'Behind Schedule (<75%)'
    END as tier,
    COUNT(*) as days,
    ROUND(AVG(rpi), 1) as avg_rpi
FROM daily_stats
WHERE emails_sent > 0
GROUP BY tier
ORDER BY avg_rpi DESC;
```

### View Current Streak
```sql
SELECT 
    date,
    emails_sent,
    ROUND(rpi, 1) as rpi,
    streak_days
FROM daily_stats
WHERE emails_sent > 0
ORDER BY date DESC
LIMIT 1;
```

---

## System Architecture

### Data Flow
```
Gmail API → email_scanner.py → sent_emails table
                                      ↓
Google Calendar → meeting_scanner.py → expected_load table
                                      ↓
                                xp_system.py → xp_ledger table
                                      ↓
                         rpi_calculator.py → daily_stats table
```

### Tables

**Input Tables:**
- `sent_emails` - Email output tracking
- `expected_load` - Meeting hours and expectations
- `xp_ledger` - XP transactions

**Output Table:**
- `daily_stats` - Aggregated RPI and metrics (SSOT)

---

## Maintenance

### Daily Operations
Run RPI calculator automatically (via cron or scheduled task):
```bash
0 23 * * * cd /home/workspace && python3 N5/scripts/productivity/rpi_calculator.py
```

### Weekly Health Check
```bash
# Verify data freshness
sqlite3 productivity_tracker.db "SELECT MAX(date) FROM daily_stats;"

# Check average RPI
sqlite3 productivity_tracker.db "SELECT ROUND(AVG(rpi), 1) FROM daily_stats WHERE date >= date('now', '-7 days');"
```

### Monthly Recalculation
```bash
# Recalculate all historical data
python3 N5/scripts/productivity/rpi_calculator.py --recalculate
```

---

## Troubleshooting

### No baseline expectations
**Problem:** Dates with emails but no expected_load entries  
**Solution:** Run backfill
```bash
python3 N5/scripts/productivity/rpi_calculator.py --backfill
```

### RPI seems wrong
**Problem:** Incorrect RPI calculation  
**Solution:** Recalculate historical data
```bash
python3 N5/scripts/productivity/rpi_calculator.py --recalculate
```

### Database locked
**Problem:** SQLite database is locked  
**Solution:** Close other connections, wait 30 seconds, retry

---

## Future Enhancements

1. **Email Type Tracking:** Break down by new/follow-up/response
2. **RPI Trends:** Moving averages and trend analysis
3. **Goal Setting:** Custom RPI targets and alerts
4. **Visualization:** Charts and performance dashboards
5. **Weekly/Monthly Rollups:** Aggregate statistics

---

## Support

**Documentation:** See worker specs in `N5/orchestration/productivity-tracker/`  
**Issues:** Report to orchestrator conversation (con_6NobvGrBPaGJQwZA)  
**Database:** `/home/workspace/productivity_tracker.db`

---

**Version:** 1.0  
**Last Updated:** 2025-10-26  
**Status:** ✅ Production Ready

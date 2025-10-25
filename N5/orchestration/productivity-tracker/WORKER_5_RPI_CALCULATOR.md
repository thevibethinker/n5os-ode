# Worker 5: RPI Calculator

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W5-RPI-CALCULATOR  
**Estimated Time:** 30 minutes  
**Dependencies:** Workers 1, 2, 3, 4 (All data sources + XP system)

---

## Mission

Integrate all data sources to calculate daily Relative Productivity Index (RPI), aggregate statistics, apply XP multipliers, and populate daily_stats table.

---

## Context

RPI is the core metric that makes this system smart. It integrates:
- Actual emails sent (from W2)
- Expected emails from meetings (from W3)
- Expected emails from incoming (from W2)
- Manual load events (future)
- XP calculation with RPI multipliers (from W4)

---

## Dependencies

- W1: Database
- W2: Email scanner
- W3: Meeting scanner
- W4: XP system

---

## Deliverables

1. `/home/workspace/N5/scripts/productivity/rpi_calculator.py`
2. Daily stats populated with accurate RPI
3. Integration test showing end-to-end flow

---

## Requirements

### RPI Formula

```python
expected_daily = (
    sum(load_events.expected_emails WHERE event_date = today) +
    10  # baseline when no load
)

actual_daily = count(emails WHERE sent_at = today AND is_substantial = true)

rpi = (actual_daily / expected_daily) * 100 if expected_daily > 0 else 100
```

### Daily Aggregation

For each date:
1. Count emails by type
2. Sum expected load
3. Calculate RPI
4. Calculate base XP
5. Apply RPI multiplier
6. Calculate level
7. Check streak
8. Check daily bonuses
9. Update daily_stats

---

## Implementation

```python
#!/usr/bin/env python3
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")
BASELINE_LOAD = 10  # Default expected emails when no meetings/incoming

def main(dry_run=False, date=None):
    try:
        target_date = date or datetime.now().date().isoformat()
        
        if dry_run:
            logger.info("[DRY RUN] Would calculate RPI for %s", target_date)
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Calculate for target date
        stats = calculate_daily_stats(cursor, target_date)
        
        # Update database
        upsert_daily_stats(cursor, target_date, stats)
        
        conn.commit()
        conn.close()
        
        logger.info("✓ RPI calculated for %s: %.1f%%", target_date, stats['rpi'])
        return 0
        
    except Exception as e:
        logger.error("RPI calculation failed: %s", e, exc_info=True)
        return 1

def calculate_daily_stats(cursor, date):
    # Count emails
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN email_type='new' THEN 1 ELSE 0 END) as new,
            SUM(CASE WHEN email_type='follow_up' THEN 1 ELSE 0 END) as followup,
            SUM(CASE WHEN email_type='response' THEN 1 ELSE 0 END) as response
        FROM emails
        WHERE DATE(sent_at) = ? AND is_substantial = 1
    """, (date,))
    email_stats = cursor.fetchone()
    
    # Sum expected load
    cursor.execute("""
        SELECT SUM(expected_emails) FROM load_events
        WHERE event_date = ?
    """, (date,))
    expected_load = cursor.fetchone()[0] or 0
    expected_total = max(expected_load, BASELINE_LOAD)
    
    # Calculate RPI
    actual = email_stats[0] or 0
    rpi = (actual / expected_total * 100) if expected_total > 0 else 100
    
    # Calculate XP (import from xp_system)
    from xp_system import calculate_level, get_rpi_multiplier
    
    base_xp = (
        (email_stats[1] or 0) * 10 +  # new
        (email_stats[2] or 0) * 8 +   # follow-up
        (email_stats[3] or 0) * 5     # response
    )
    
    multiplier, performance = get_rpi_multiplier(rpi)
    xp_earned = int(base_xp * multiplier)
    
    # Add daily bonuses
    if rpi >= 100:
        xp_earned += 50  # Clean Sheet
    if (email_stats[1] or 0) >= 3:
        xp_earned += 20  # Hat Trick
    
    # Calculate cumulative for level
    cursor.execute("SELECT SUM(xp_earned) FROM daily_stats WHERE date < ?", (date,))
    cumulative_xp = (cursor.fetchone()[0] or 0) + xp_earned
    level = calculate_level(cumulative_xp)
    
    # Calculate streak
    cursor.execute("""
        SELECT streak_days FROM daily_stats 
        WHERE date < ? ORDER BY date DESC LIMIT 1
    """, (date,))
    prev_streak = cursor.fetchone()
    streak = (prev_streak[0] + 1) if (prev_streak and rpi >= 100) else (1 if rpi >= 100 else 0)
    
    return {
        'emails_sent': actual,
        'emails_new': email_stats[1] or 0,
        'emails_followup': email_stats[2] or 0,
        'emails_response': email_stats[3] or 0,
        'expected_emails': expected_total,
        'rpi': rpi,
        'xp_earned': xp_earned,
        'xp_multiplier': multiplier,
        'level': level,
        'streak_days': streak
    }

def upsert_daily_stats(cursor, date, stats):
    cursor.execute("""
        INSERT OR REPLACE INTO daily_stats 
        (date, emails_sent, emails_new, emails_followup, emails_response,
         expected_emails, rpi, xp_earned, xp_multiplier, level, streak_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, stats['emails_sent'], stats['emails_new'], 
          stats['emails_followup'], stats['emails_response'],
          stats['expected_emails'], stats['rpi'], stats['xp_earned'],
          stats['xp_multiplier'], stats['level'], stats['streak_days']))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--date", help="YYYY-MM-DD")
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run, date=args.date))
```

---

## Testing

```bash
# Calculate today
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py

# Verify
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT * FROM daily_stats ORDER BY date DESC LIMIT 1;"
```

---

## Report Back

1. ✅ RPI calculator created
2. ✅ Daily stats aggregation working
3. ✅ XP multipliers applied correctly
4. ✅ Integration test passed
5. ✅ Ready for dashboard (W6) and automation (W7)

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:10 ET

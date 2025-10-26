# Worker 5: RPI Calculator & Daily Aggregator

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W5-RPI-CALCULATOR  
**Estimated Time:** 60 minutes  
**Dependencies:** W1 (Database - COMPLETE), W2 (Email Scanner - COMPLETE), W3 (Meeting Scanner - COMPLETE), W4 (XP System - COMPLETE)

---

## Mission

Build the intelligence layer that calculates Relative Productivity Index (RPI) by integrating email output, expected load, and XP multipliers to provide true productivity measurement.

---

## Context

**Current System State:**
- ✅ Database schema complete with `daily_stats` table
- ✅ Email scanner tracking sent emails (`sent_emails` table)
- ✅ Meeting scanner tracking expected load (`expected_load` table)
- ✅ XP system calculating gamification scores (`xp_ledger` table)
- ⏳ Need: Daily aggregation and RPI calculation to tie it all together

**Your Role:**
You're the brain that brings together all data sources to calculate the single most important metric: **True Productivity** (actual output relative to demand).

---

## Database Schema Reference

```sql
-- Input Tables (READ from these)

CREATE TABLE sent_emails (
    id INTEGER PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    thread_id TEXT,
    subject TEXT,
    sent_at TIMESTAMP NOT NULL,
    email_type TEXT,  -- 'new', 'follow_up', 'response'
    is_substantial BOOLEAN DEFAULT 1,
    recipient_count INTEGER,
    has_attachment BOOLEAN,
    metadata JSON
);

CREATE TABLE expected_load (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    source TEXT NOT NULL,  -- 'calendar', 'manual', 'incoming'
    type TEXT NOT NULL,    -- 'meeting', 'event', 'deadline'
    hours REAL NOT NULL,
    title TEXT,
    metadata JSON
);

CREATE TABLE xp_ledger (
    id INTEGER PRIMARY KEY,
    transaction_date TIMESTAMP NOT NULL,
    xp_amount INTEGER NOT NULL,
    xp_type TEXT NOT NULL,
    description TEXT,
    email_id INTEGER
);

-- Output Table (WRITE to this)

CREATE TABLE daily_stats (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    emails_new INTEGER DEFAULT 0,
    emails_followup INTEGER DEFAULT 0,
    emails_response INTEGER DEFAULT 0,
    expected_emails REAL DEFAULT 0,  -- Derived from expected_load
    rpi REAL DEFAULT 100,
    xp_earned INTEGER DEFAULT 0,
    xp_multiplier REAL DEFAULT 1.0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Deliverables

### 1. RPI Calculator Script

**File:** `/home/workspace/N5/scripts/productivity/rpi_calculator.py`

**Core Functions:**

```python
def calculate_rpi_for_date(date: str) -> dict:
    """
    Calculate RPI and all related metrics for a specific date.
    
    Process:
    1. Count actual emails sent (from sent_emails)
    2. Calculate expected load (from expected_load + baseline)
    3. Calculate RPI = (actual / expected) * 100
    4. Aggregate XP from xp_ledger
    5. Calculate streak (consecutive days with emails)
    6. Calculate level (from cumulative XP)
    
    Returns:
        {
            'date': '2025-10-26',
            'emails_sent': 5,
            'emails_new': 2,
            'emails_followup': 2,
            'emails_response': 1,
            'expected_load_hours': 4.5,
            'expected_emails': 13.5,  # hours * 3 emails/hour
            'rpi': 37.0,  # (5 / 13.5) * 100
            'xp_earned': 46,
            'xp_multiplier': 0.75,  # RPI <75%
            'level': 1,
            'streak_days': 0,  # RPI < 100%
            'performance_tier': 'Behind Schedule 🔻'
        }
    """

def calculate_expected_load(date: str, conn) -> dict:
    """
    Calculate expected email output for a date.
    
    Formula:
        expected_emails = (total_meeting_hours * 3) + baseline
        
    Where:
        - 3 emails/hour = assumption for meeting follow-up
        - baseline = 5 emails/day (minimum productivity expectation)
    
    Returns:
        {
            'expected_load_hours': 4.5,
            'expected_emails': 18.5,  # (4.5 * 3) + 5
            'load_breakdown': {
                'calendar': 4.0,
                'manual': 0.5,
                'baseline': 5.0
            }
        }
    """

def calculate_streak(date: str, emails_sent: int, rpi: float, conn) -> int:
    """
    Calculate current streak of productive days.
    
    Rules:
        - Streak continues if: emails_sent > 0 AND rpi >= 80%
        - Streak breaks if: emails_sent == 0 OR rpi < 80%
        - Must be consecutive calendar days
    
    Returns: int (current streak days)
    """

def aggregate_historical_rpi(start_date: str = None, end_date: str = None, dry_run: bool = False) -> dict:
    """
    Recalculate RPI for all historical dates.
    
    Process:
    1. Query all unique dates from sent_emails and expected_load
    2. For each date, calculate RPI
    3. Update daily_stats table
    4. Log progress every 50 days
    
    Returns summary stats.
    """

def backfill_baseline_expectations(dry_run: bool = False) -> int:
    """
    For dates with sent emails but no expected_load, insert baseline.
    
    Baseline: 5 emails/day expected (1.67 hours at 3 emails/hour)
    
    Returns count of dates backfilled.
    """
```

---

## RPI Calculation Logic

### Formula

```python
EMAILS_PER_HOUR = 3  # Assumption: meeting → 3 emails follow-up
BASELINE_EMAILS = 5   # Minimum daily expectation

expected_emails = (total_load_hours * EMAILS_PER_HOUR) + BASELINE_EMAILS
actual_emails = count(sent_emails WHERE is_substantial = true)

rpi = (actual_emails / expected_emails) * 100 if expected_emails > 0 else 100
```

### Examples

**Scenario 1: Low meeting day**
- Load: 1 hour meeting
- Expected: (1 * 3) + 5 = 8 emails
- Actual: 12 emails
- RPI: (12 / 8) * 100 = **150% (Invincible Form 🔥)**

**Scenario 2: Heavy meeting day**
- Load: 6 hours meetings
- Expected: (6 * 3) + 5 = 23 emails
- Actual: 18 emails
- RPI: (18 / 23) * 100 = **78% (Catch Up Needed ⚠️)**

**Scenario 3: No meetings**
- Load: 0 hours
- Expected: (0 * 3) + 5 = 5 emails (baseline)
- Actual: 8 emails
- RPI: (8 / 5) * 100 = **160% (Invincible Form 🔥)**

---

## Integration with XP System

### RPI Multipliers (from Worker 4)

```python
RPI_MULTIPLIERS = [
    (150, 1.5, "Invincible Form 🔥"),
    (125, 1.25, "Top Performance ⭐"),
    (100, 1.0, "Meeting Expectations ✅"),
    (75, 0.9, "Catch Up Needed ⚠️"),
    (0, 0.75, "Behind Schedule 🔻")
]
```

**Note:** XP calculation is already done by Worker 4. Your job is to:
1. Calculate RPI
2. Read XP from `xp_ledger` table (aggregate for the day)
3. Read XP multiplier that was applied
4. Store RPI in `daily_stats` table

**Do NOT recalculate XP.** Just aggregate existing XP transactions.

---

## Streak Calculation Logic

### Rules

```python
def calculate_streak(date: str, emails_sent: int, rpi: float, conn) -> int:
    """
    Streak continues if:
    - Previous day had emails_sent > 0
    - Previous day had RPI >= 80%
    - Current day has emails_sent > 0
    
    Streak breaks if:
    - Current day has emails_sent == 0
    - Previous day had RPI < 80%
    - Gap in dates > 1 day
    """
    
    if emails_sent == 0:
        return 0
    
    # Query previous day
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        SELECT date, emails_sent, rpi, streak_days
        FROM daily_stats
        WHERE date < ?
        ORDER BY date DESC
        LIMIT 1
    \"\"\", (date,))
    
    prev = cursor.fetchone()
    if not prev:
        return 1  # First day
    
    prev_date, prev_emails, prev_rpi, prev_streak = prev
    
    # Check if consecutive
    from datetime import datetime, timedelta
    current_dt = datetime.strptime(date, \"%Y-%m-%d\")
    prev_dt = datetime.strptime(prev_date, \"%Y-%m-%d\")
    
    if (current_dt - prev_dt).days != 1:
        return 1  # Gap, restart streak
    
    # Check streak rules
    if prev_emails > 0 and prev_rpi >= 80:
        return prev_streak + 1
    else:
        return 1  # Previous day broke streak
```

---

## Implementation Structure

```python
#!/usr/bin/env python3
\"\"\"
RPI Calculator & Daily Aggregator
Integrates email output, expected load, and XP to calculate true productivity

Principles Applied:
- P2 (SSOT): Reads from source tables, writes to daily_stats
- P7 (Dry-Run): --dry-run flag for safe testing
- P18 (Verify State): Database queries verify calculations
- P19 (Error Handling): Try/except around DB operations
- P21 (Document Assumptions): Formulas documented (3 emails/hour, baseline 5)
- P22 (Language Selection): Python for data aggregation + SQLite
\"\"\"

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format=\"%(asctime)sZ %(levelname)s %(message)s\"
)
logger = logging.getLogger(__name__)

DB_PATH = Path(\"/home/workspace/productivity_tracker.db\")

# === CONSTANTS ===

EMAILS_PER_HOUR = 3    # Meeting → follow-up email assumption
BASELINE_EMAILS = 5     # Daily minimum expectation
STREAK_RPI_THRESHOLD = 80  # RPI threshold to maintain streak

# [Core functions defined above]

def main(recalculate: bool = False, date: str = None, backfill: bool = False, dry_run: bool = False) -> int:
    \"\"\"
    Main execution:
    - If recalculate=True: Rebuild RPI for all dates
    - If backfill=True: Add baseline expectations for dates missing load
    - If date provided: Calculate RPI for specific date
    - Otherwise: Calculate RPI for today
    \"\"\"
    try:
        if backfill:
            logger.info(\"=== Backfilling Baseline Expectations ===\")
            count = backfill_baseline_expectations(dry_run=dry_run)
            logger.info(f\"✓ Backfilled {count} dates\")
            return 0
        
        if recalculate:
            logger.info(\"=== Recalculating All RPI ===\")
            result = aggregate_historical_rpi(dry_run=dry_run)
            logger.info(f\"✓ Processed {result['days']} days\")
            logger.info(f\"✓ Average RPI: {result['avg_rpi']:.1f}%\")
            return 0
        
        target_date = date or datetime.now().strftime(\"%Y-%m-%d\")
        logger.info(f\"=== Calculating RPI for {target_date} ===\")
        
        # Calculate and store RPI for date
        result = calculate_rpi_for_date(target_date, dry_run=dry_run)
        
        logger.info(f\"✓ {result['emails_sent']} emails sent\")
        logger.info(f\"✓ {result['expected_emails']:.1f} emails expected\")
        logger.info(f\"✓ RPI: {result['rpi']:.1f}% ({result['performance_tier']})\")
        logger.info(f\"✓ XP Multiplier: {result['xp_multiplier']}×\")
        
        return 0
        
    except Exception as e:
        logger.error(f\"Error: {e}\", exc_info=True)
        return 1

if __name__ == \"__main__\":
    parser = argparse.ArgumentParser(description=\"RPI Calculator & Daily Aggregator\")
    parser.add_argument(\"--recalculate\", action=\"store_true\", help=\"Recalculate RPI for all dates\")
    parser.add_argument(\"--backfill\", action=\"store_true\", help=\"Backfill baseline expectations\")
    parser.add_argument(\"--date\", help=\"Calculate RPI for specific date (YYYY-MM-DD)\")
    parser.add_argument(\"--dry-run\", action=\"store_true\", help=\"Show what would be done\")
    
    args = parser.parse_args()
    exit(main(
        recalculate=args.recalculate,
        date=args.date,
        backfill=args.backfill,
        dry_run=args.dry_run
    ))
```

---

## Testing Requirements

### 1. Unit Tests (Core Logic)

```bash
# Test expected load calculation
python3 -c "from rpi_calculator import calculate_expected_load; import sqlite3; conn=sqlite3.connect('/home/workspace/productivity_tracker.db'); print(calculate_expected_load('2025-10-26', conn))"

# Test RPI calculation
python3 -c "from rpi_calculator import calculate_rpi_for_date; print(calculate_rpi_for_date('2025-10-26'))"
```

### 2. Integration Test (Backfill)

```bash
# Dry run first
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --backfill --dry-run

# Actual backfill
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --backfill

# Verify baseline expectations
sqlite3 /home/workspace/productivity_tracker.db <<EOF
SELECT date, source, hours, title
FROM expected_load
WHERE source = 'baseline'
ORDER BY date DESC
LIMIT 10;
EOF
```

### 3. Integration Test (RPI Recalculation)

```bash
# Dry run first
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --recalculate --dry-run

# Actual recalculation
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --recalculate

# Verify daily_stats
sqlite3 /home/workspace/productivity_tracker.db <<EOF
SELECT date, emails_sent, expected_emails, rpi, xp_multiplier, streak_days
FROM daily_stats
ORDER BY date DESC
LIMIT 10;
EOF
```

### 4. Verify RPI Distribution

```bash
sqlite3 /home/workspace/productivity_tracker.db <<EOF
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
EOF
```

---

## Success Criteria

Worker 5 is complete when:

1. ✅ `rpi_calculator.py` script created with all core functions
2. ✅ Expected load calculation working (hours → emails conversion)
3. ✅ RPI calculation formula implemented
4. ✅ Baseline expectations backfill working
5. ✅ Streak calculation logic working (consecutive days + RPI threshold)
6. ✅ Level aggregation from XP ledger
7. ✅ XP multiplier reading from xp_ledger
8. ✅ Recalculation function processes all historical data
9. ✅ `daily_stats` table fully populated
10. ✅ Dry-run mode works
11. ✅ Database verification passes
12. ✅ RPI distribution reasonable (not all 0% or 100%)

---

## Critical Implementation Notes

### 1. **Do NOT Recalculate XP**

XP is already calculated by Worker 4 (`xp_system.py`). Your job is to:
- Read XP from `xp_ledger` table
- Aggregate transactions for each date
- Store aggregated XP in `daily_stats`

```python
# Aggregate XP for a date (DON'T recalculate)
cursor.execute("""
    SELECT SUM(xp_amount) 
    FROM xp_ledger 
    WHERE DATE(transaction_date) = ?
""", (date,))
xp_earned = cursor.fetchone()[0] or 0
```

### 2. **Baseline Expectations**

Many dates will have sent emails but no expected_load entries (no meetings that day). Handle this gracefully:

```python
if total_load_hours == 0:
    expected_emails = BASELINE_EMAILS  # 5 emails minimum
else:
    expected_emails = (total_load_hours * EMAILS_PER_HOUR) + BASELINE_EMAILS
```

### 3. **Date Handling**

All dates in SQLite are stored as strings in 'YYYY-MM-DD' format. Use:

```python
date_str = datetime.now().strftime("%Y-%m-%d")
```

### 4. **Performance Tier from RPI**

Import from xp_system or reimplement:

```python
def get_performance_tier(rpi: float) -> str:
    if rpi >= 150: return "Invincible Form 🔥"
    elif rpi >= 125: return "Top Performance ⭐"
    elif rpi >= 100: return "Meeting Expectations ✅"
    elif rpi >= 75: return "Catch Up Needed ⚠️"
    else: return "Behind Schedule 🔻"
```

---

## Principles Applied

- **P2 (SSOT):** daily_stats is single aggregated view
- **P7 (Dry-Run):** `--dry-run`, `--backfill`, `--recalculate` flags
- **P18 (Verify State):** Database queries verify RPI calculations
- **P19 (Error Handling):** Try/except around all DB operations
- **P21 (Document Assumptions):** 3 emails/hour, baseline 5, streak threshold 80%
- **P22 (Language Selection):** Python for data aggregation + date handling

---

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:10 ET  
**Updated:** 2025-10-26 11:39 ET  
**Status:** READY FOR EXECUTION

---

**Special Note:** This is the "intelligence" worker that ties everything together. Take your time to understand the relationships between tables. RPI is the KEY metric that makes this system valuable.

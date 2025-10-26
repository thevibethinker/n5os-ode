# Worker 4: Arsenal XP System

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W4-XP-SYSTEM  
**Estimated Time:** 60 minutes  
**Dependencies:** Worker 1 (Database Setup - COMPLETE), Worker 2 (Email Scanner - COMPLETE)

---

## Mission

Build Arsenal FC-themed gamification engine that calculates XP from email activity, applies RPI multipliers, tracks levels/ranks, unlocks achievements, and maintains streaks.

---

## Context

**Current System State:**
- ✅ Database schema complete (`xp_ledger`, `achievements`, `daily_stats` tables ready)
- ✅ Email scanner tracking sent/incoming emails
- ✅ Eras configured (Pre-Superhuman, Post-Superhuman, Post-Zo)
- ⏳ Need: XP calculation and gamification logic

**Your Role:**
Transform raw email data into engaging Arsenal FC-themed progression system.

---

## Database Schema Reference

```sql
-- XP Ledger (transactions)
CREATE TABLE xp_ledger (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    source TEXT NOT NULL,  -- 'email', 'bonus', 'achievement'
    activity_type TEXT,    -- 'new', 'follow_up', 'response', 'clean_sheet', etc.
    xp_amount INTEGER NOT NULL,
    multiplier REAL DEFAULT 1.0,
    rpi REAL,
    description TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Stats (aggregated)
CREATE TABLE daily_stats (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    emails_incoming INTEGER DEFAULT 0,
    expected_load_hours REAL DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    xp_cumulative INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    rpi REAL,
    streak_days INTEGER DEFAULT 0,
    achievements_unlocked INTEGER DEFAULT 0,
    metadata JSON
);

-- Achievements
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY,
    achievement_name TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    xp_value INTEGER DEFAULT 0,
    unlocked_at TIMESTAMP,
    unlock_count INTEGER DEFAULT 0
);
```

---

## Deliverables

### 1. XP Calculation Engine

**File:** `/home/workspace/N5/scripts/productivity/xp_system.py`

**Core Functions:**

```python
def calculate_email_xp(email_type: str, response_time_hours: float = None) -> dict:
    """
    Calculate XP for single email with breakdown.
    
    Returns:
        {
            'base_xp': 10,
            'speed_bonus': 5,  # If response <24h
            'total_xp': 15,
            'description': 'New email + Speed Bonus'
        }
    """

def calculate_daily_bonuses(date: str, stats: dict) -> list:
    """
    Calculate bonus XP for the day.
    
    Stats:
        - emails_sent: int
        - rpi: float (from RPI calculator, may be None)
        - streak_days: int
    
    Returns list of bonus transactions:
        [
            {'type': 'clean_sheet', 'xp': 50, 'description': 'RPI ≥100%'},
            {'type': 'hat_trick', 'xp': 20, 'description': '3+ new emails'},
            {'type': 'streak', 'xp': 30, 'description': '3-day streak'}
        ]
    """

def apply_rpi_multiplier(base_xp: int, rpi: float) -> dict:
    """
    Apply RPI-based multiplier to XP.
    
    Returns:
        {
            'base_xp': 100,
            'multiplier': 1.25,
            'bonus_xp': 25,
            'final_xp': 125,
            'tier': 'Top Performance'
        }
    """

def calculate_level_and_rank(total_xp: int) -> dict:
    """
    Calculate current level and Arsenal rank.
    
    Formula: level = floor(sqrt(total_xp / 100))
    
    Returns:
        {
            'level': 12,
            'rank': 'First Team Squad',
            'xp_current': 14400,
            'xp_next_level': 16900,
            'xp_to_next': 2500,
            'progress_pct': 85.2
        }
    """

def check_and_unlock_achievements(conn, date: str, stats: dict) -> list:
    """
    Check for newly unlocked achievements and update database.
    
    Returns list of newly unlocked achievements:
        [
            {'name': 'level_10', 'title': 'First Team Squad', 'xp': 100},
            {'name': 'week_streak', 'title': '7-Day Streak', 'xp': 50}
        ]
    """

def recalculate_all_xp(start_date: str = None, dry_run: bool = False) -> dict:
    """
    Recalculate XP for all historical data from sent_emails table.
    
    Process:
    1. Clear xp_ledger and reset daily_stats XP columns
    2. Iterate through sent_emails by date
    3. Calculate base XP + bonuses
    4. Apply RPI multipliers (if available)
    5. Update xp_ledger with transactions
    6. Update daily_stats with aggregated XP
    7. Check achievements
    
    Returns summary stats.
    """
```

---

## XP Values & Bonuses

### Base XP (Per Email)

```python
EMAIL_XP = {
    'new': 10,         # Initiating new thread
    'follow_up': 8,    # Follow-up in existing thread
    'response': 5      # Reply to incoming
}
```

### Speed Bonus

```python
SPEED_BONUS = 5  # Applied if response_time_hours < 24
```

### Daily Bonuses

```python
DAILY_BONUSES = {
    'clean_sheet': {
        'xp': 50,
        'condition': lambda stats: stats.get('rpi', 0) >= 100,
        'description': 'RPI ≥100% (Arsenal Clean Sheet)'
    },
    'hat_trick': {
        'xp': 20,
        'condition': lambda stats: stats.get('new_emails', 0) >= 3,
        'description': '3+ New Emails (Hat Trick)'
    },
    'goal_rush': {
        'xp': 50,
        'condition': lambda stats: stats.get('new_emails', 0) >= 5,
        'description': '5+ New Emails (Goal Rush)'
    }
}
```

### Streak Bonuses

```python
def calculate_streak_xp(streak_days: int) -> int:
    """10 XP per day in streak, capped at 100 XP"""
    return min(streak_days * 10, 100)
```

---

## RPI Multipliers

```python
RPI_MULTIPLIERS = [
    (150, 1.5, "Invincible Form 🔥"),
    (125, 1.25, "Top Performance ⭐"),
    (100, 1.0, "Meeting Expectations ✅"),
    (75, 0.9, "Catch Up Needed ⚠️"),
    (0, 0.75, "Behind Schedule 🔻")
]

def get_rpi_multiplier(rpi: float) -> tuple:
    """Returns (multiplier, tier_name)"""
    if rpi is None:
        return (1.0, "No RPI Data")
    
    for threshold, mult, tier in RPI_MULTIPLIERS:
        if rpi >= threshold:
            return (mult, tier)
    
    return (0.75, "Behind Schedule 🔻")
```

---

## Leveling System

### Formula

```python
import math

def calculate_level(total_xp: int) -> int:
    """level = floor(sqrt(total_xp / 100))"""
    return math.floor(math.sqrt(total_xp / 100))

def xp_for_level(level: int) -> int:
    """XP required to reach this level"""
    return level * level * 100

def xp_to_next_level(current_xp: int) -> dict:
    """Calculate progress to next level"""
    current_level = calculate_level(current_xp)
    next_level = current_level + 1
    
    xp_current_level = xp_for_level(current_level)
    xp_next_level = xp_for_level(next_level)
    
    xp_needed = xp_next_level - current_xp
    xp_progress = current_xp - xp_current_level
    xp_total_for_level = xp_next_level - xp_current_level
    
    progress_pct = (xp_progress / xp_total_for_level) * 100
    
    return {
        'current_level': current_level,
        'next_level': next_level,
        'xp_current': current_xp,
        'xp_next_level': xp_next_level,
        'xp_needed': xp_needed,
        'progress_pct': round(progress_pct, 1)
    }
```

### Arsenal Ranks

```python
ARSENAL_RANKS = [
    (1, 4, "Youth Academy ⚽", "Just getting started"),
    (5, 9, "Reserve Team 🎯", "Showing promise"),
    (10, 14, "First Team Squad 🔴", "Regular contributor"),
    (15, 19, "Regular Starter ⭐", "Key player"),
    (20, 24, "Club Captain 👑", "Leadership role"),
    (25, 999, "Arsenal Legend 🏆", "Hall of Fame")
]

def get_rank(level: int) -> dict:
    """Get Arsenal rank for level"""
    for min_lvl, max_lvl, title, desc in ARSENAL_RANKS:
        if min_lvl <= level <= max_lvl:
            return {
                'title': title,
                'description': desc,
                'level_range': (min_lvl, max_lvl)
            }
    return {'title': 'Youth Academy ⚽', 'description': 'Just getting started', 'level_range': (1, 4)}
```

---

## Achievement Definitions

Seed these into `achievements` table:

```python
ACHIEVEMENTS = [
    # Level Milestones
    ('level_5', 'Reserve Team', 'Reach Level 5', 50),
    ('level_10', 'First Team Squad', 'Reach Level 10', 100),
    ('level_15', 'Regular Starter', 'Reach Level 15', 150),
    ('level_20', 'Club Captain', 'Reach Level 20', 200),
    ('level_25', 'Arsenal Legend', 'Reach Level 25', 500),
    
    # Streak Achievements
    ('streak_3', '3-Day Streak', 'Email 3 days in a row', 20),
    ('streak_7', 'Week Warrior', 'Email 7 days in a row', 50),
    ('streak_30', 'Month Marathon', 'Email 30 days in a row', 200),
    
    # Output Achievements
    ('emails_100', 'Centurion', 'Send 100 emails', 100),
    ('emails_500', 'Goal Machine', 'Send 500 emails', 250),
    ('emails_1000', 'Legendary Striker', 'Send 1000 emails', 500),
    
    # Performance Achievements
    ('clean_sheet_10', '10 Clean Sheets', 'RPI ≥100% for 10 days', 100),
    ('invincible', 'Invincible', 'RPI ≥150% for 7 days straight', 300),
    ('hat_trick_artist', 'Hat Trick Artist', '5+ new emails in a day 10 times', 150)
]
```

---

## Implementation Structure

```python
#!/usr/bin/env python3
"""
Arsenal XP System - Gamification Engine
Calculates XP, levels, ranks, achievements from email data
"""

import argparse
import json
import logging
import math
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

# [Constants defined above]

# [Core functions defined above]

def main(recalculate: bool = False, date: str = None, dry_run: bool = False) -> int:
    """
    Main execution:
    - If recalculate=True: Rebuild all XP from scratch
    - If date provided: Calculate XP for specific date
    - Otherwise: Calculate XP for today
    """
    try:
        if recalculate:
            logger.info("=== Recalculating All XP ===")
            result = recalculate_all_xp(dry_run=dry_run)
            logger.info(f"✓ Processed {result['days']} days")
            logger.info(f"✓ {result['total_xp']} total XP")
            logger.info(f"✓ Level {result['final_level']}")
            return 0
        
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"=== Calculating XP for {target_date} ===")
        
        # Calculate and store XP for date
        result = calculate_day_xp(target_date, dry_run=dry_run)
        
        logger.info(f"✓ {result['emails_sent']} emails sent")
        logger.info(f"✓ {result['xp_earned']} XP earned")
        logger.info(f"✓ Level {result['level']} ({result['rank']})")
        
        if result.get('achievements'):
            logger.info(f"🏆 Unlocked: {', '.join(result['achievements'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arsenal XP System")
    parser.add_argument("--recalculate", action="store_true", help="Recalculate all XP from scratch")
    parser.add_argument("--date", help="Calculate XP for specific date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    exit(main(recalculate=args.recalculate, date=args.date, dry_run=args.dry_run))
```

---

## Testing Requirements

### 1. Unit Tests (Core Logic)

```bash
# Test XP calculation
python3 -c "from xp_system import calculate_email_xp; print(calculate_email_xp('new'))"
# Expected: {'base_xp': 10, 'speed_bonus': 0, 'total_xp': 10, ...}

# Test level calculation
python3 -c "from xp_system import calculate_level; print(calculate_level(10000))"
# Expected: 10 (sqrt(10000/100) = 10)

# Test RPI multiplier
python3 -c "from xp_system import get_rpi_multiplier; print(get_rpi_multiplier(150))"
# Expected: (1.5, 'Invincible Form 🔥')
```

### 2. Integration Test (Full Recalculation)

```bash
# Dry run first
python3 /home/workspace/N5/scripts/productivity/xp_system.py --recalculate --dry-run

# Actual run
python3 /home/workspace/N5/scripts/productivity/xp_system.py --recalculate

# Verify database
sqlite3 /home/workspace/productivity_tracker.db <<EOF
SELECT date, xp_earned, xp_cumulative, level 
FROM daily_stats 
WHERE xp_earned > 0
ORDER BY date DESC 
LIMIT 10;
EOF
```

### 3. Verify XP Ledger

```bash
sqlite3 /home/workspace/productivity_tracker.db <<EOF
SELECT date, source, activity_type, xp_amount, multiplier, description
FROM xp_ledger
ORDER BY created_at DESC
LIMIT 20;
EOF
```

---

## Success Criteria

Worker 4 is complete when:

1. ✅ `xp_system.py` script created with all core functions
2. ✅ Email XP calculation working (base + speed bonus)
3. ✅ Daily bonuses implemented (clean sheet, hat trick, streaks)
4. ✅ RPI multipliers integrated
5. ✅ Leveling formula working (sqrt progression)
6. ✅ Arsenal ranks mapped correctly
7. ✅ Achievement checking and unlocking works
8. ✅ Recalculation function processes all historical data
9. ✅ `xp_ledger` table populated with transactions
10. ✅ `daily_stats.xp_earned`, `xp_cumulative`, `level` updated
11. ✅ Dry-run mode works
12. ✅ Database verification passes

---

## Principles Applied

- **P2 (SSOT):** Database is single source; XP derived from email data
- **P7 (Dry-Run):** `--dry-run` flag for safe testing
- **P18 (Verify State):** Database queries verify XP calculations
- **P19 (Error Handling):** Try/except around DB operations
- **P21 (Document Assumptions):** Formulas and thresholds documented in code
- **P22 (Language Selection):** Python for data processing + SQLite

---

## Notes for Implementation

1. **Graceful RPI Handling:** RPI calculator (Worker 5) not built yet. Use `rpi = None` fallback → no multiplier (1.0×)

2. **Streak Calculation:** Requires checking consecutive days with emails_sent > 0. Query:
   ```sql
   SELECT date FROM daily_stats 
   WHERE emails_sent > 0 AND date < ? 
   ORDER BY date DESC
   ```

3. **Achievement Unlock Logic:** Check `unlocked_at IS NULL` before unlocking to prevent duplicates

4. **Performance:** Recalculation on large datasets may take time. Log progress every 100 days.

---

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:05 ET  
**Updated:** 2025-10-26 11:24 ET  
**Status:** READY FOR EXECUTION

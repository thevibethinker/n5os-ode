# W3: Integration Worker Handoff
**Worker ID:** W3-INTEGRATION  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Dependencies:** W1 (Schema), W2 (Calculator) must complete first  
**Estimated Time:** 45 minutes

---

## Your Mission

Wire the team status calculator into the existing `rpi_calculator.py` daily run so that team status updates automatically every time RPI is calculated.

You're the **bridge** between the pure logic (W2) and the production system. Your code runs daily via scheduled task and keeps V's career progression in sync with their performance.

---

## Context

V has a scheduled task that runs daily at a specific time:
1. Scans Gmail for sent emails → populates `sent_emails` table
2. Scans Google Calendar for meetings → populates `expected_load` table
3. Calculates RPI score → updates `daily_stats` table
4. Calculates XP, level, streak → updates `daily_stats` table

**Your job:** Add step 5:
5. Calculate team status using W2's calculator → update `team_status_history`, `status_transitions`, `career_stats` tables

---

## Current System

### Main Script: `rpi_calculator.py`

**File:** `/home/workspace/N5/scripts/productivity/rpi_calculator.py`

**Current Flow:**
```python
def main():
    today = get_today()
    
    # 1. Load email data
    emails_sent = count_emails_for_date(today)
    
    # 2. Load meeting data
    meeting_hours = sum_meeting_hours(today)
    
    # 3. Calculate expected emails
    expected = (meeting_hours * 3) + 5
    
    # 4. Calculate RPI
    rpi = (emails_sent / expected) * 100 if expected > 0 else 0
    
    # 5. Calculate XP, level, streak
    xp, multiplier, level = calculate_xp(rpi)
    streak = update_streak(rpi)
    
    # 6. Update database
    update_daily_stats(today, rpi, emails_sent, expected, xp, multiplier, level, streak)
    
    # 7. Log results
    logger.info(f"✓ RPI: {rpi}%")
    logger.info(f"✓ XP: {xp} (Multiplier: {multiplier}×)")
    logger.info(f"✓ Level: {level}")
    logger.info(f"✓ Streak: {streak} days")
```

**Your task:** Add team status calculation after XP calculation:

```python
    # 7. Calculate team status (NEW)
    status_decision = calculate_team_status(today)
    update_team_status(today, status_decision)
    
    # 8. Log results (UPDATED)
    logger.info(f"✓ Team Status: {status_decision.new_status or status_decision.current_status}")
    if status_decision.action != 'maintain':
        logger.info(f"✓ Status Change: {status_decision.action} - {status_decision.reason}")
```

---

## Your Deliverables

### 1. Modified `rpi_calculator.py`

**File:** `/home/workspace/N5/scripts/productivity/rpi_calculator.py`

Add these functions:

```python
def calculate_team_status(date: str) -> StatusDecision:
    """
    Calculate team status for given date using W2's calculator.
    
    Args:
        date: Date string (YYYY-MM-DD)
    
    Returns:
        StatusDecision object from team_status_calculator
    """
    # 1. Fetch last 7 days of daily_stats
    daily_records = fetch_performance_history(date, days=7)
    
    # 2. Fetch current team status
    current_status = fetch_current_status(date)
    
    # 3. Calculate elite unlock progress
    elite_progress = calculate_elite_progress(date)
    
    # 4. Call W2's calculator
    from team_status_calculator import TeamStatusCalculator
    calc = TeamStatusCalculator()
    decision = calc.calculate_status(daily_records, current_status, elite_progress)
    
    return decision


def update_team_status(date: str, decision: StatusDecision):
    """
    Update database tables with status decision.
    
    Updates:
    - team_status_history: new row for today
    - status_transitions: if status changed
    - career_stats: increment counters
    """
    # 1. Insert/update team_status_history
    insert_or_update_status_history(date, decision)
    
    # 2. If status changed, log transition
    if decision.action in ['promote', 'demote']:
        log_status_transition(date, decision)
    
    # 3. Update career stats (days in each status, total promotions/demotions)
    update_career_stats(date, decision)


def fetch_performance_history(date: str, days: int = 7) -> List[Dict]:
    """Fetch last N days of RPI data"""
    # Query daily_stats for last 7 days
    pass


def fetch_current_status(date: str) -> Dict:
    """Get current team status or initialize if new"""
    # Query team_status_history for most recent status
    # If no rows exist (first run), return default: 'squad_member'
    pass


def calculate_elite_progress(date: str) -> Dict:
    """Calculate elite tier unlock progress"""
    # Look back 8 weeks
    # Count weeks where top5_avg >= 125%
    # Check if invincible/legend already unlocked
    pass


def insert_or_update_status_history(date: str, decision: StatusDecision):
    """Insert new row in team_status_history"""
    pass


def log_status_transition(date: str, decision: StatusDecision):
    """Insert row in status_transitions table"""
    pass


def update_career_stats(date: str, decision: StatusDecision):
    """Update the single career_stats row"""
    # Increment appropriate day counter
    # If promotion/demotion, increment those counters
    # Update longest streaks if needed
    pass
```

### 2. Database Helper Module

**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/team_status_db.py`

Isolate all database operations in a reusable module:

```python
#!/usr/bin/env python3
"""
Database operations for team status system.
Keeps DB queries separate from business logic.
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

class TeamStatusDB:
    """Database interface for team status operations"""
    
    def __init__(self, db_path: str = '/home/workspace/productivity_tracker.db'):
        self.db_path = db_path
    
    def get_performance_history(self, end_date: str, days: int = 7) -> List[Dict]:
        """Fetch last N days of RPI data"""
        pass
    
    def get_current_status(self, date: str) -> Optional[Dict]:
        """Get most recent team status"""
        pass
    
    def get_elite_unlock_status(self, date: str) -> Dict:
        """Check if elite tiers unlocked"""
        pass
    
    def insert_status_history(self, date: str, status: str, metrics: Dict):
        """Insert new status history row"""
        pass
    
    def insert_status_transition(self, date: str, from_status: str, to_status: str, reason: str, metrics: Dict):
        """Log status change"""
        pass
    
    def update_career_stats(self, status: str, action: str):
        """Update career statistics"""
        pass
    
    def get_career_stats(self) -> Dict:
        """Fetch current career stats"""
        pass
```

### 3. Integration Tests

**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/test_integration.py`

Test the full pipeline:

```python
#!/usr/bin/env python3
"""
Integration tests for team status system.
Tests W2 calculator + W3 database integration working together.
"""

import unittest
import sqlite3
from datetime import datetime, timedelta
from team_status_calculator import TeamStatusCalculator
from team_status_db import TeamStatusDB

class TestIntegration(unittest.TestCase):
    """Test that calculator + database work together"""
    
    def setUp(self):
        # Create test database
        self.test_db = '/tmp/test_productivity.db'
        self.setup_test_database()
        self.db = TeamStatusDB(self.test_db)
        self.calc = TeamStatusCalculator()
    
    def test_first_run_initializes_status(self):
        """Test that first run creates default status"""
        # Should start at 'squad_member'
        pass
    
    def test_promotion_updates_all_tables(self):
        """Test that promotion updates history + transitions + career_stats"""
        pass
    
    def test_probation_prevents_immediate_demotion(self):
        """Test 7-day probation buffer"""
        pass
    
    def test_elite_unlock_tracked_correctly(self):
        """Test invincible unlock after 6/8 weeks"""
        pass
    
    # ... more tests

if __name__ == '__main__':
    unittest.main()
```

### 4. Dry-Run Mode

Add `--dry-run` flag to `rpi_calculator.py`:

```python
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Calculate but don\'t write to DB')
    parser.add_argument('--date', help='Calculate for specific date')
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🏃 DRY-RUN MODE: No database writes")
    
    main(dry_run=args.dry_run, date=args.date)
```

---

## Database Operations Details

### Query Patterns

**Fetch last 7 days:**
```sql
SELECT date, rpi, emails_sent, expected_emails, xp_earned, level, streak_days
FROM daily_stats
WHERE date >= date(?, '-7 days') AND date <= ?
ORDER BY date DESC
LIMIT 7
```

**Get current status:**
```sql
SELECT *
FROM team_status_history
WHERE date <= ?
ORDER BY date DESC
LIMIT 1
```

**Elite unlock check (8 weeks):**
```sql
SELECT date, top5_avg
FROM team_status_history
WHERE date >= date(?, '-56 days') AND date <= ?
  AND top5_avg >= 125.0
ORDER BY date DESC
```

**Insert status history:**
```sql
INSERT OR REPLACE INTO team_status_history
(date, status, days_in_status, previous_status, top5_avg, grace_days_used, 
 promotion_eligible, probation_days_remaining, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
```

**Insert transition:**
```sql
INSERT INTO status_transitions
(date, from_status, to_status, reason, top5_avg, created_at)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
```

**Update career stats:**
```sql
UPDATE career_stats
SET days_first_team = days_first_team + 1,
    total_promotions = total_promotions + 1,
    last_updated = ?
WHERE id = 1
```

---

## Edge Cases to Handle

### First Run (No Historical Data)
- `team_status_history` is empty
- Initialize at 'squad_member' status
- Set probation to 0 (no probation on first run)
- Log as 'system_init' reason

### Less Than 7 Days Data
- New user has only 3 days of RPI data
- Use available days for calculation
- Don't trigger demotions (not enough data)
- Allow promotions only after 7 days

### Missing Data Days
- What if V doesn't run calculator for 2 days?
- Backfill logic: calculate retroactively for missed days
- Or: only calculate for today, skip missed days

**Recommendation:** Only calculate for today. Don't backfill automatically (could trigger unexpected status changes). V can manually backfill if needed.

### Database Corruption
- What if status history has gaps?
- What if career_stats row doesn't exist?
- Graceful degradation: initialize with sane defaults

---

## Success Criteria

- [ ] `rpi_calculator.py` calls team status calculator
- [ ] Team status updates in `team_status_history` daily
- [ ] Status transitions logged when status changes
- [ ] Career stats updated correctly
- [ ] First run initializes properly (no crashes)
- [ ] Dry-run mode works (calculates but doesn't write)
- [ ] Integration tests pass
- [ ] Logging shows status changes clearly
- [ ] No performance regression (runs in <5 seconds)

---

## Testing Instructions

```bash
# Run dry-run to test without writing
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --dry-run

# Run for today (writes to DB)
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py

# Run for specific date (backfill)
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py --date 2025-10-29

# Check database updated
sqlite3 /home/workspace/productivity_tracker.db "SELECT * FROM team_status_history ORDER BY date DESC LIMIT 3"

# Run integration tests
python3 test_integration.py -v
```

---

## Dependencies

**Requires:**
- W1 (Schema) complete - tables exist
- W2 (Calculator) complete - calculator module available

**Provides to:**
- W4 (Email) - status_transitions triggers emails
- W5 (UI) - team_status_history powers dashboard
- W6 (QA) - integration to validate

---

## Return Format

When complete, return to orchestrator thread with:

**Subject:** W3 (Integration) - COMPLETE

**Body:**
```
Status: ✅ COMPLETE

Deliverables:
- Modified /home/workspace/N5/scripts/productivity/rpi_calculator.py
- New module: team_status_db.py
- Integration tests: test_integration.py

Test Results:
- [x] Dry-run mode tested
- [x] Full run tested (writes to DB)
- [x] Integration tests pass
- [x] First run initialization works
- [x] Status transitions logged correctly

Files Changed:
- /home/workspace/N5/scripts/productivity/rpi_calculator.py (+150 lines)
- /home/workspace/productivity_tracker.db (3 tables updated)

Performance:
- Execution time: X.X seconds (acceptable)

Notes:
[Any issues encountered, design decisions]

Ready for W4 (Email Worker) and W5 (UI Worker) to proceed.
```

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Connect the pieces. Make it run daily, reliably, correctly.  
**Priority:** HIGH - Blocks W4 and W5.

Good luck! 🔌

---
**Created:** 2025-10-30 01:33 ET

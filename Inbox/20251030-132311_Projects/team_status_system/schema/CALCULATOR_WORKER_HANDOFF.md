# W2: Calculator Worker Handoff
**Worker ID:** W2-CALCULATOR  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Dependencies:** W1 (Schema) must complete first  
**Estimated Time:** 45 minutes

---

## Your Mission

Build `team_status_calculator.py` - a standalone Python module that implements the **team status progression logic** using the "top 5 of 7" performance calculation.

This is the **brain** of the career progression system. You implement the rules that determine whether V gets promoted, demoted, or maintains their current team status.

---

## Context: What's the Bigger Picture?

V's productivity tracker calculates daily RPI (Response Productivity Index) scores. Now we're adding a career layer where V's status in an Arsenal FC team hierarchy changes based on sustained performance over 7-day windows.

**Your job:** Write the algorithm that:
1. Looks at last 7 days of RPI scores
2. Takes the best 5 days (2 grace days auto-excluded)
3. Calculates the average
4. Determines new status based on rules
5. Returns recommendation (promote/demote/maintain)

**Not your job:** Database integration (that's W3), email sending (that's W4), UI (that's W5). You build a pure calculation engine.

---

## Team Status Rules (You Implement These)

### Status Hierarchy (6 Tiers)

1. 🚫 **transfer_list** - Bottom tier, performance crisis
2. 🟠 **reserves** - Underperforming, needs improvement
3. 🟡 **squad_member** - New promotion, in probation
4. 🟢 **first_team** - Meeting expectations consistently
5. 🌟 **invincible** - Elite tier (requires unlock)
6. 🏆 **legend** - Pinnacle (requires sustained invincible)

### Core Mechanic: Top 5 of 7

Given last 7 days of RPI scores:
1. Sort scores descending
2. Take top 5 scores
3. Calculate average
4. This is the "performance metric" for status decisions

**Example:**
```
Last 7 days: [120, 95, 80, 150, 110, 60, 130]
Sorted: [150, 130, 120, 110, 95, 80, 60]
Top 5: [150, 130, 120, 110, 95]
Average: 121%
Grace days used: 2 (excluded 80 and 60)
```

### Movement Rules (Asymmetric)

**Promotion** (Easier - needs 3 consecutive days above threshold):
- From transfer_list → reserves: top5_avg ≥ 90%, 3 days trend up
- From reserves → squad_member: top5_avg ≥ 90%, 3 days above
- From squad_member → first_team: top5_avg ≥ 90%, probation complete (7 days)
- From first_team → invincible: **UNLOCK REQUIRED** (see below)
- From invincible → legend: **UNLOCK REQUIRED** (see below)

**Demotion** (Harder - needs 5 consecutive days below threshold):
- From any tier: top5_avg < 90%, 5 days trend down
- **Exception:** squad_member has 7-day probation (can't be demoted for 7 days after promotion)
- **Exception:** Invincible/Legend harder to lose (requires 7 days < 90%, not 5)

**Maintain** (Default):
- top5_avg between 85-100%: Stay at current level
- Not enough consecutive days to trigger promotion/demotion

### Elite Tier Unlocks

**Invincible Unlock:**
- Requires: 6 out of 8 weeks with top5_avg ≥ 125%
- Once unlocked, can be promoted from first_team → invincible
- Unlock is permanent (even if demoted later, can return to invincible)

**Legend Unlock:**
- Requires: 8 consecutive weeks as Invincible with top5_avg ≥ 125%
- Highest achievable status
- Once reached, very hard to lose (7 days < 80% required)

### Probation Period

When promoted to **squad_member**:
- 7-day probation begins
- Cannot be demoted during probation
- After 7 days, normal demotion rules apply
- Probation resets if demoted and promoted again

---

## Input Data Structure

You'll receive a list of daily performance records from the database:

```python
# Each record is a dict with these fields (from daily_stats table)
daily_records = [
    {
        'date': '2025-10-30',
        'rpi': 120.5,
        'emails_sent': 9,
        'expected_emails': 5,
        'xp_earned': 150.0,
        'level': 1,
        'streak_days': 1
    },
    # ... up to 7 days
]

# Current status info (from team_status_history table)
current_status = {
    'status': 'first_team',
    'days_in_status': 12,
    'probation_days_remaining': 0,
    'promotion_eligible': True
}

# Elite unlock tracking (calculated from historical data)
elite_progress = {
    'invincible_unlocked': False,
    'legend_unlocked': False,
    'recent_125_weeks': 4  # out of last 8 weeks
}
```

---

## Output Data Structure

Return a decision object:

```python
{
    'action': 'promote',  # 'promote' | 'demote' | 'maintain'
    'new_status': 'invincible',  # target status if action != 'maintain'
    'reason': 'sustained_excellence',  # Why this decision was made
    'top5_avg': 132.5,  # The calculated performance metric
    'grace_days_used': 2,  # How many days excluded
    'days_to_promotion': 0,  # If maintaining, days until promotion eligible
    'days_to_demotion': 3,  # If maintaining, days until demotion risk
    'probation_days_remaining': 7,  # If newly promoted to squad_member
    'elite_unlock_progress': {  # For dashboard display
        'invincible': {'unlocked': True, 'progress': '6/8 weeks'},
        'legend': {'unlocked': False, 'progress': '0/8 weeks'}
    },
    'warnings': []  # List of warning messages (e.g., "2nd grace day used")
}
```

---

## Your Deliverables

### 1. Main Module: `team_status_calculator.py`

**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/team_status_calculator.py`

**Structure:**
```python
#!/usr/bin/env python3
"""
Team Status Calculator - Career Progression Logic
Implements top-5-of-7 performance evaluation for N5 productivity tracking.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class StatusDecision:
    """Output of team status calculation"""
    action: str  # 'promote' | 'demote' | 'maintain'
    new_status: Optional[str]
    reason: str
    top5_avg: float
    grace_days_used: int
    days_to_promotion: int
    days_to_demotion: int
    probation_days_remaining: int
    elite_unlock_progress: Dict
    warnings: List[str]


class TeamStatusCalculator:
    """Core logic for team status progression"""
    
    # Status hierarchy
    STATUSES = [
        'transfer_list',
        'reserves',
        'squad_member',
        'first_team',
        'invincible',
        'legend'
    ]
    
    # Thresholds
    MAINTAIN_THRESHOLD = 90.0
    ELITE_THRESHOLD = 125.0
    PROMOTION_DAYS = 3
    DEMOTION_DAYS = 5
    PROBATION_DAYS = 7
    
    def calculate_top5_avg(self, rpi_scores: List[float]) -> tuple[float, int]:
        """
        Calculate top 5 of 7 average.
        Returns: (average, grace_days_used)
        """
        # Implementation here
        pass
    
    def check_promotion_eligible(
        self,
        current_status: str,
        days_in_status: int,
        top5_avg: float,
        elite_unlocked: Dict
    ) -> tuple[bool, str]:
        """
        Check if promotion is possible.
        Returns: (eligible, reason)
        """
        # Implementation here
        pass
    
    def check_demotion_risk(
        self,
        current_status: str,
        probation_remaining: int,
        top5_avg: float,
        consecutive_poor_days: int
    ) -> tuple[bool, str]:
        """
        Check if demotion should occur.
        Returns: (should_demote, reason)
        """
        # Implementation here
        pass
    
    def calculate_status(
        self,
        daily_records: List[Dict],
        current_status: Dict,
        elite_progress: Dict
    ) -> StatusDecision:
        """
        Main entry point: calculate new team status.
        
        Args:
            daily_records: Last 7 days of performance data
            current_status: Current team status info
            elite_progress: Elite tier unlock tracking
        
        Returns:
            StatusDecision with recommendation
        """
        # Implementation here
        pass


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    import json
    import sys
    
    parser = argparse.ArgumentParser(description='Calculate team status')
    parser.add_argument('--db', default='/home/workspace/productivity_tracker.db')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--date', help='Calculate for specific date (YYYY-MM-DD)')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    # Load data from DB, run calculation, print result
    # (This allows other workers to test your module)
    pass
```

### 2. Unit Tests: `test_team_status_calculator.py`

**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/test_team_status_calculator.py`

Test these scenarios:

**Edge Cases:**
- Less than 7 days of data (new user)
- All 7 days identical scores
- Exactly 5 days provided (no grace needed)
- All 7 days below threshold
- All 7 days above elite threshold

**Promotion Logic:**
- 3 consecutive days ≥90% from transfer_list
- Can't promote to invincible without unlock
- Probation completion allows squad_member → first_team

**Demotion Logic:**
- 5 consecutive days <90% triggers demotion
- Probation protects squad_member from demotion
- Elite tiers require 7 days <90% (not 5)

**Grace Days:**
- 2 worst days correctly excluded
- Warning when both grace days used

**Elite Unlocks:**
- Invincible unlock: 6/8 weeks ≥125%
- Legend unlock: 8 consecutive weeks as invincible ≥125%

```python
#!/usr/bin/env python3
import unittest
from team_status_calculator import TeamStatusCalculator, StatusDecision

class TestTopFiveCalculation(unittest.TestCase):
    def setUp(self):
        self.calc = TeamStatusCalculator()
    
    def test_top5_with_two_grace_days(self):
        scores = [120, 95, 80, 150, 110, 60, 130]
        avg, grace = self.calc.calculate_top5_avg(scores)
        self.assertAlmostEqual(avg, 121.0)
        self.assertEqual(grace, 2)
    
    # ... more tests

class TestPromotionLogic(unittest.TestCase):
    # ... tests

class TestDemotionLogic(unittest.TestCase):
    # ... tests

if __name__ == '__main__':
    unittest.main()
```

### 3. CLI Testing Script

**File:** `/home/.z/workspaces/con_MuvXIR7jXZjZxlND/test_calculator_cli.sh`

Bash script that runs common test scenarios:

```bash
#!/bin/bash
# Test suite for team_status_calculator.py

echo "🧪 Testing Team Status Calculator"
echo "=================================="

# Test 1: Current production data
echo "Test 1: Calculate for today"
python3 team_status_calculator.py --date 2025-10-30 --verbose

# Test 2: Dry-run mode
echo "Test 2: Dry-run (no DB writes)"
python3 team_status_calculator.py --dry-run

# Test 3: Edge case - new user
echo "Test 3: Simulate new user (3 days data)"
# ... more tests

echo "✅ All tests complete"
```

---

## Success Criteria

- [ ] `team_status_calculator.py` implements all rules correctly
- [ ] Top 5 of 7 calculation works (grace days excluded)
- [ ] Promotion logic follows asymmetric rules (3 days up)
- [ ] Demotion logic follows asymmetric rules (5 days down)
- [ ] Probation period prevents premature demotion
- [ ] Elite unlock requirements checked correctly
- [ ] Unit tests cover edge cases
- [ ] Unit tests pass (100% success rate)
- [ ] CLI interface works for manual testing
- [ ] Code is type-hinted and documented
- [ ] No database I/O in calculator (pure logic)

---

## Design Constraints

### Pure Logic Module
- **NO database access** in calculator code
- Calculator receives data, returns decision
- W3 (Integration Worker) handles DB reads/writes
- This keeps calculator testable in isolation

### Dry-Run Support
- CLI must support `--dry-run` flag
- Dry-run mode: calculate and print, don't write
- Allows safe testing with production data

### Asymmetric Movement
- Promotion should feel achievable (3 good days)
- Demotion should feel fair (5 bad days, with warning)
- This prevents "status flapping" (bouncing daily)

### Grace Day Philosophy
- Grace days are automatic (not manual selection)
- Always excludes 2 worst days from last 7
- If using both grace days, add warning to output

---

## Dependencies

**Requires:**
- W1 (Schema) complete - need table structures to understand data format
- Python 3.12
- SQLite 3 (for CLI testing only, not in calculator logic)

**Provides to:**
- W3 (Integration) - will call your `calculate_status()` function
- W5 (UI) - will display your decision output
- W6 (QA) - will validate your logic against historical data

---

## Testing Instructions

```bash
# Run unit tests
cd /home/.z/workspaces/con_MuvXIR7jXZjZxlND
python3 -m unittest test_team_status_calculator.py -v

# Test with real data
python3 team_status_calculator.py --date 2025-10-30 --verbose

# Test dry-run mode
python3 team_status_calculator.py --dry-run

# Run full test suite
bash test_calculator_cli.sh
```

---

## Example Usage (For Other Workers)

```python
from team_status_calculator import TeamStatusCalculator

calc = TeamStatusCalculator()

# Prepare input data (W3 will fetch this from DB)
daily_records = [
    {'date': '2025-10-30', 'rpi': 120.5, ...},
    {'date': '2025-10-29', 'rpi': 95.0, ...},
    # ... 7 days total
]

current_status = {
    'status': 'first_team',
    'days_in_status': 12,
    'probation_days_remaining': 0
}

elite_progress = {
    'invincible_unlocked': False,
    'recent_125_weeks': 4
}

# Calculate
decision = calc.calculate_status(daily_records, current_status, elite_progress)

# Use result
if decision.action == 'promote':
    print(f"🔼 PROMOTION to {decision.new_status}")
    print(f"Reason: {decision.reason}")
    print(f"Top 5 avg: {decision.top5_avg}%")
```

---

## Return Format

When complete, return to orchestrator thread with:

**Subject:** W2 (Calculator) - COMPLETE

**Body:**
```
Status: ✅ COMPLETE

Deliverables:
- team_status_calculator.py (450 lines)
- test_team_status_calculator.py (25 test cases)
- test_calculator_cli.sh (5 test scenarios)

Test Results:
- [x] All 25 unit tests pass
- [x] CLI tested with production data
- [x] Dry-run mode works
- [x] Edge cases handled

Key Design Decisions:
- [Document any ambiguities you resolved]
- [Any assumptions made]

Notes:
[Any blockers, questions, or recommendations]

Ready for W3 (Integration Worker) to wire into rpi_calculator.py.
```

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Build the brain. Make the rules fair, the math correct, the code testable.  
**Priority:** HIGH - W3 and W5 need your output.

Good luck! 🧮

---
**Created:** 2025-10-30 01:33 ET

# Worker 4: Arsenal XP System

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W4-XP-SYSTEM  
**Estimated Time:** 45 minutes  
**Dependencies:** Worker 1 (Database Setup)

---

## Mission

Implement Arsenal FC-themed XP calculation engine with leveling, achievements, bonuses, and streak tracking.

---

## Context

Gamification layer that:
- Calculates XP from emails (base + bonuses)
- Applies RPI multipliers
- Tracks levels using Arsenal ranks
- Unlocks achievements
- Maintains streaks

---

## Dependencies

Worker 1 complete

---

## Deliverables

1. `/home/workspace/N5/scripts/productivity/xp_system.py`
2. XP calculation tests passing
3. Achievement unlock logic working

---

## Requirements

### Base XP Values

- New email: 10 XP
- Follow-up: 8 XP
- Response: 5 XP

### Bonuses

- Speed (<24h response): +5 XP
- Clean Sheet (RPI≥100%): +50 XP/day
- Hat Trick (3+ new): +20 XP/day
- Streak: +10 XP per streak day

### Leveling Formula

```python
level = floor(sqrt(total_xp / 100))
```

### Arsenal Ranks

```python
RANKS = {
    (1, 4): "Youth Academy",
    (5, 9): "Reserve Team",
    (10, 14): "First Team Squad",
    (15, 19): "Regular Starter",
    (20, 24): "Club Captain",
    (25, 999): "Arsenal Legend"
}
```

### RPI Multipliers

- ≥150%: 1.5×
- ≥125%: 1.25×
- 100-124%: 1.0×
- 75-99%: 0.9×
- <75%: 0.75×

---

## Implementation

```python
#!/usr/bin/env python3
import sqlite3
import math
from datetime import datetime

DB_PATH = "/home/workspace/productivity_tracker.db"

def calculate_xp_for_email(email_type: str, response_time_hours: float = None) -> int:
    base = {
        'new': 10,
        'follow_up': 8,
        'response': 5
    }[email_type]
    
    bonus = 5 if (response_time_hours and response_time_hours < 24) else 0
    return base + bonus

def calculate_level(total_xp: int) -> int:
    return math.floor(math.sqrt(total_xp / 100))

def get_rank(level: int) -> str:
    if level < 5: return "Youth Academy"
    elif level < 10: return "Reserve Team"
    elif level < 15: return "First Team Squad"
    elif level < 20: return "Regular Starter"
    elif level < 25: return "Club Captain"
    else: return "Arsenal Legend"

def get_rpi_multiplier(rpi: float) -> tuple:
    if rpi >= 150: return (1.5, "Invincible Form")
    elif rpi >= 125: return (1.25, "Top Performance")
    elif rpi >= 100: return (1.0, "Meeting Expectations")
    elif rpi >= 75: return (0.9, "Catch Up Needed")
    else: return (0.75, "Behind Schedule")

def check_achievements(conn, total_xp, level, streak_days):
    cursor = conn.cursor()
    # Check level milestones
    level_achievements = {
        5: 'level_5',
        10: 'level_10',
        15: 'level_15',
        20: 'level_20',
        25: 'level_25'
    }
    
    if level in level_achievements:
        cursor.execute(
            "UPDATE achievements SET unlocked_at=? WHERE achievement_name=? AND unlocked_at IS NULL",
            (datetime.now(), level_achievements[level])
        )

if __name__ == "__main__":
    # Recalculate all XP from emails table
    # Update daily_stats
    # Check achievements
    pass
```

---

## Testing

```bash
python3 /home/workspace/N5/scripts/productivity/xp_system.py --recalculate
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT date, xp_earned, level, rpi FROM daily_stats ORDER BY date DESC LIMIT 7;"
```

---

## Report Back

1. ✅ XP system script created
2. ✅ Leveling formula working
3. ✅ Achievement tracking implemented
4. ✅ RPI multipliers integrated
5. ✅ Ready for RPI calculator integration

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:05 ET

# Team Status Calculator - Design Thinking

## Problem Space

Calculate daily team status from RPI performance using:
- Top 5 of 7 average (grace system)
- 6-tier system with asymmetric movement
- Promotion/demotion with consecutive-day logic
- Probation immunity for squad_member
- Elite unlock gates (2-in-7-days pattern)

## Core Algorithms

### 1. Top 5 of 7 Average
```
Input: [day1_rpi, day2_rpi, ..., day7_rpi]
Sort descending → Take first 5 → Average
Grace days = 7 - len(used_days)
Edge: <7 days available → use all, grace = 7 - count
```

### 2. Threshold Mapping
```
0-69% → transfer_list
70-89% → reserves  
90-99% → squad_member (probation tier)
100-124% → first_team
125-149% → invincible (requires unlock)
150%+ → legend (requires unlock + invincible)
```

### 3. Promotion Logic (EASIER)
```
Default: 1 day at threshold → immediate promotion
Exception: squad_member → first_team = 3 consecutive ≥90%
Reason: Probation period = prove consistency
```

### 4. Demotion Logic (HARDER)
```
first_team → squad_member: 3 consecutive <90%
squad_member → reserves: 5 consecutive <90% (but probation immunity blocks this)
reserves → transfer_list: 3 consecutive <70%
elite → tier_below: 5 consecutive below threshold

Probation immunity: squad_member has 7-day grace, cannot demote during
```

### 5. Consecutive Tracking
```
If today's top5 < threshold for demotion:
    consecutive_poor_days++
Else:
    consecutive_poor_days = 0  (reset counter)

Check: if consecutive_poor >= required_days → DEMOTE
```

### 6. Elite Unlock
```
Invincible: Need 2 days ≥125% within 7-day rolling window
Legend: Need invincible status + 2 days ≥150% within 7-day window

Once unlocked: Can move freely between tiers
Without unlock: Stuck at first_team ceiling
```

## State Machine

```
Current State → Check Promotion → Check Demotion → Check Elite → New State

Counters updated:
- days_in_status (increment if same, reset if change)
- consecutive_poor_days (increment if poor, reset if good)
- probation_days_remaining (decrement if >0, clamp at 0)
```

## Edge Cases

1. **First run:** No history → Start at 'first_team' (V's starting position)
2. **<7 days data:** Use all available, grace_days = 7 - count
3. **Missing RPI:** Treat as 0.0 (counts as poor day)
4. **Exact threshold:** 0.90 exactly → No change (favor stability)
5. **Probation overflow:** Clamp at 0, never negative

## Data Flow

```
1. Fetch last 7 days RPI from daily_stats
2. Calculate top5_avg + grace_days_used
3. Fetch current status from team_status_history
4. Determine base status from threshold
5. Check promotion eligibility
6. Check demotion eligibility (respecting probation immunity)
7. Check elite unlock gates
8. Apply movement rules
9. Update counters
10. Return structured dict for W3 to write
```

## Return Structure

```python
{
    'date': '2025-10-30',
    'status': 'first_team',
    'days_in_status': 1,
    'previous_status': 'squad_member',
    'top5_avg': 1.05,
    'grace_days_used': 2,
    'consecutive_poor_days': 0,
    'probation_days_remaining': 0,
    'reason': 'Promoted: 3 consecutive days ≥90% (probation complete)',
    'changed': True
}
```

## Trap Doors Identified

1. **Off-by-one in consecutive counting** → Use explicit reset logic
2. **Probation decrement during demotion** → Decrement AFTER demotion check
3. **Elite unlock without gate check** → Explicit query for 2-in-7 pattern
4. **Grace days calculation with <7 data** → Handle edge case explicitly
5. **Threshold boundary (0.90 exactly)** → Use >= for tier, < for demotion

## Testing Strategy

1. Unit test: top5_avg calculation
2. Unit test: threshold mapping
3. Integration: promotion scenarios (immediate + probation)
4. Integration: demotion scenarios (consecutive tracking)
5. Integration: probation immunity
6. Integration: elite unlock (2-in-7 pattern)
7. Edge: first day, <7 days data, missing RPI

---

**Design complete.** Ready to implement.

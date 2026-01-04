---
created: 2026-01-04
last_edited: 2026-01-04
version: 1.0
provenance: con_CpbfkOMMrbJlpLzL
---

# Workout Prescription Engine

## Purpose
Synthesize V's 10K Training Plan + Jair Lee Strength Program into a single daily workout prescription, adjusted by Fitbit readiness data.

## Checklist

### Phase 1: Core Engine
- [x] Create `training_cycle` table in workouts.db
- [x] Create `daily_prescription` table
- [x] Build `workout_prescriber.py` script
- [x] Test with today's date (2026-01-04 = Day 1, Week 1)

### Phase 2: Readiness Integration
- [x] Add readiness scoring (RHR baseline, sleep efficiency, sleep duration)
- [x] Add adjustment logic (reduce intensity if readiness low)
- [x] Test with historical data

### Phase 3: On-Demand Interface
- [x] Add CLI for "what should I do today?"
- [ ] Return structured output for daily digest integration

---

## Source Plans

### 10K Plan (Priority: PRIMARY)
| Day | Workout Type | Duration |
|-----|--------------|----------|
| Monday | Strength | 45m |
| Tuesday | Engine Building (Zone 2) | 30-40m |
| Wednesday | Recovery Walk / Mobility | 20m |
| Thursday | 20% Interval (4x4) | 35m |
| Friday | Strength | 45m |
| Saturday | Engine Building (Long) | 50-60m |
| Sunday | Rest / Light Walk | - |

### Jair Lee Plan (Priority: SECONDARY - informs strength days)
| Day | Focus |
|-----|-------|
| Day 1 | Upper Body |
| Day 2 | Lower Body |
| Day 3 | Core + Cardio + Mobility |
| Day 4 | Upper Body #2 |
| Day 5 | Lower Body #2 |
| Day 6 | Restorative / Active Recovery |
| Day 7 | Long Run + Mobility |

### Synthesis Logic
- **Strength days (Mon/Fri)**: Use Jair's Upper/Lower split alternating
  - Week 1: Mon=Upper (Day 1), Fri=Lower (Day 2)
  - Week 2: Mon=Upper#2 (Day 4), Fri=Lower#2 (Day 5)
- **Cardio days**: Follow 10K plan exactly
- **Recovery days**: Merge (Wed mobility + Jair Day 6 principles)

---

## Readiness Logic

### Inputs (from workouts.db)
- `daily_resting_hr.resting_hr` — compare to 14-day baseline
- `sleep_sessions.efficiency` — target >85%
- `sleep_sessions.duration_min` — target >420min (7hr)

### Readiness Score (0-100)
```
rhr_score = max(0, 100 - (current_rhr - baseline_rhr) * 10)
sleep_eff_score = efficiency
sleep_dur_score = min(100, (duration_min / 420) * 100)

readiness = (rhr_score * 0.4) + (sleep_eff_score * 0.3) + (sleep_dur_score * 0.3)
```

### Adjustment Rules
| Readiness | Adjustment |
|-----------|------------|
| 80-100 | Full prescription |
| 60-79 | Reduce intensity (Zone 3→Zone 2, cut intervals) |
| 40-59 | Active recovery only |
| <40 | Full rest recommended |

---

## Affected Files

### Phase 1
- `Personal/Health/workouts.db` (schema additions)
- `Personal/Health/WorkoutTracker/workout_prescriber.py` (new)

---

## Cycle Start
- **Cycle Start Date**: 2026-01-04 (Sunday)
- **Week 1 Day 1**: 2026-01-04



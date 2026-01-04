---
created: 2026-01-04
last_edited: 2026-01-04
version: 2.0
provenance: con_CpbfkOMMrbJlpLzL
---

# Workout Prescription Engine - STATUS

## Current State: ✅ v2.0 Complete (LLM-Powered)

### Architecture
**Python handles DATA:**
- Cycle position calculation (week, day)
- Fitbit readiness data (RHR, sleep, recent workouts)
- Reading plan markdown files

**LLM handles INTELLIGENCE:**
- Interprets the actual plan documents
- Synthesizes 10K + Jair programs contextually
- Adjusts for readiness and recent activity
- Generates actionable prescription

### Completed
- ☑ Data gathering layer (cycle info, Fitbit, workout history)
- ☑ Plan file reading (10K_Prep_Plan.md, Jair-Lee-Training-Program-Phase1.md)
- ☑ LLM integration via /zo/ask API
- ☑ Readiness scoring (RHR baseline comparison + sleep quality)
- ☑ CLI interface (today, specific date, --status, --data-only)

### Remaining
- ☐ Daily digest hook (auto-include in morning digest)
- ☐ Workout logging (record completed sessions to strength_sessions)
- ☐ Compliance tracking

---

## How to Use

```bash
# Today's prescription (calls LLM)
python3 Personal/Health/WorkoutTracker/workout_prescriber.py

# Specific date
python3 Personal/Health/WorkoutTracker/workout_prescriber.py 2026-01-05

# Show cycle status (no LLM call)
python3 Personal/Health/WorkoutTracker/workout_prescriber.py --status

# Show gathered data without LLM (debug mode)
python3 Personal/Health/WorkoutTracker/workout_prescriber.py --data-only
```

---

## Plan Files
- `Personal/Health/WorkoutTracker/10K_Prep_Plan.md` — Primary schedule
- `Personal/Health/WorkoutTracker/Jair-Lee-Training-Program-Phase1.md` — Strength details

The LLM reads these files directly. When plans change, the prescriptions update automatically.

---

## Readiness Thresholds (informed by LLM)
| Score | Level | Guidance |
|-------|-------|----------|
| 80-100 | Optimal | Full prescription |
| 70-79 | Good | Minor adjustments possible |
| 50-69 | Moderate | Reduce intensity |
| 40-49 | Low | Active recovery only |
| <40 | Depleted | Rest recommended |



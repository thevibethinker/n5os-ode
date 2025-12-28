---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
provenance: con_SBNtQa0x2OL8SlKM
---

# Health Dashboard v2.0 — Information-Dense Redesign

## Design Philosophy
- **Dense, not decorative** — Every pixel earns its place
- **Trends over snapshots** — Sparklines inline with every metric
- **Deltas with direction** — Show change from baseline, color-coded
- **Data integrity visible** — Know what's missing, not just what's there
- **Coach, don't just report** — One actionable insight at a time

---

## Layout: Single-Page Grid

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 COACH: "RHR down 3% this week. Recovery is strong—push today"│
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│ RECOVERY         │ PERFORMANCE      │ CONSISTENCY      │
├──────────────────┼──────────────────┼──────────────────┤
│ RHR: 75.2 ↓2.3   │ Vol: 12.4km ↑18% │ Streak: 7 days   │
│ ▁▂▂▃▂▂▁▁▂▁ 30d   │ ▁▁▂▃▄▅▆▅▆▇ 30d   │ ████████░░ 80%   │
│                  │                  │                  │
│ Sleep: 7.2h (86%)│ Pace: 10.8 ↓0.4  │ This wk: 5/7     │
│ ▅▂▇▄▁▃▇ 7d       │ ▇▆▅▅▄▄▃▃▂▂ 30d   │ Last wk: 4/7     │
│                  │                  │                  │
│ HRV: -- (no data)│ Longest: 3.9km   │ Integrity: 71%   │
└──────────────────┴──────────────────┴──────────────────┘

┌──────────────────┬──────────────────┐
│ BODY             │ DATA HEALTH      │
├──────────────────┼──────────────────┤
│ Weight: 92.0 ↓1.1│ RHR: 100d ✓      │
│ ░░░░░░░░▇▇ 30d   │ Activity: 47d ✓  │
│ (sparse: 2 pts)  │ Sleep: 60d ✓     │
│                  │ Weight: 2d ⚠     │
│ BF%: 28.4%       │ Checkins: 1d ⚠   │
│ (need more data) │ Last sync: 2d ago│
└──────────────────┴──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ RECENT SESSIONS (compact table)                                 │
├─────────┬────────┬────────┬────────┬────────┬──────────────────┤
│ Date    │ Type   │ Dist   │ Pace   │ HR     │ vs Avg           │
├─────────┼────────┼────────┼────────┼────────┼──────────────────┤
│ 12/26   │ Run    │ 3.92km │ 11.3   │ --     │ +1.5km ↑         │
│ 12/25   │ Run    │ 2.80km │ 10.9   │ --     │ +0.4km ↑         │
│ 12/24   │ Run    │ 1.79km │ 14.8   │ --     │ -0.6km ↓         │
│ 12/23   │ Run    │ 0.66km │ 16.9   │ 129    │ -1.7km ↓         │
│ 12/21   │ Run    │ 2.56km │ 9.9    │ 157    │ +0.2km ↑         │
└─────────┴────────┴────────┴────────┴────────┴──────────────────┘
```

---

## Metrics Specification

### Recovery Panel
| Metric | Source | Calculation | Sparkline |
|--------|--------|-------------|-----------|
| RHR | daily_resting_hr.resting_hr | 7d rolling avg | 30d trend |
| Sleep | sleep_sessions.duration_min/60 | Last night + 7d avg efficiency | 7d bars |
| HRV | daily_resting_hr.hrv | Latest value | 7d trend (if data) |

### Performance Panel
| Metric | Source | Calculation | Sparkline |
|--------|--------|-------------|-----------|
| Weekly Volume | workouts.distance_km | SUM(last 7d) vs prior 7d | 30d weekly bars |
| Avg Pace | workouts.duration_min/distance_km | 7d rolling avg | 30d trend (lower=better) |
| Longest Run | workouts.distance_km | MAX(last 30d) | -- |

### Consistency Panel
| Metric | Source | Calculation | Display |
|--------|--------|-------------|---------|
| Streak | workouts.date | Consecutive days with workout | Number + bar |
| This Week | workouts | COUNT(DISTINCT date) last 7d | X/7 |
| Integrity | daily_checkins | worked_out / wanted_to_work_out | % |

### Body Panel
| Metric | Source | Calculation | Notes |
|--------|--------|-------------|-------|
| Weight | daily_weight.weight_kg | Latest + delta from 7d ago | Flag if sparse |
| Body Fat | daily_weight.body_fat_pct | Latest | Flag if sparse |

### Data Health Panel
| Metric | Calculation | Status |
|--------|-------------|--------|
| Per-table coverage | COUNT(DISTINCT date) | ✓ if >30d, ⚠ if <7d |
| Days since last sync | MAX(date) | ⚠ if >2d |
| Gaps | Missing dates in last 30d | List if >3 |

---

## Coaching Logic (Priority Order)

1. **Recovery Alert** (RHR >3bpm above 30d baseline)
   → "Resting HR elevated. Consider rest or light activity."

2. **Sleep Deficit** (Last night <6h or efficiency <80%)
   → "Sleep was short/poor. Hydrate and avoid intensity."

3. **Streak at Risk** (No workout yesterday, streak >3)
   → "Streak at risk. Even 10 min counts."

4. **PR Opportunity** (RHR low + sleep good + recent volume up)
   → "Recovery strong, volume building. Good day for a push."

5. **Consistency Win** (7d integrity >80%)
   → "Consistency is high. Keep the rhythm."

6. **Default**
   → "Systems nominal. Stay the course."

---

## Implementation Notes

- Use **Recharts** sparklines (already in deps)
- Single component: `<HealthDashboard />` replaces current multi-card layout
- API: Add `/api/health/dashboard` that returns all metrics in one call
- Color tokens: `--success` (green), `--warning` (amber), `--danger` (red)
- Mobile: Stack panels vertically, keep density

---

## Questions for V

1. Do you want to see intraday HR data (minute-by-minute during workouts)?
2. Should weight/BF be hidden entirely until more data exists?
3. Any other metrics you're tracking outside this DB?


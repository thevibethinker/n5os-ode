---
created: 2025-12-26
last_edited: 2025-12-26
version: 2.0
provenance: con_SBNtQa0x2OL8SlKM
---

# PLAN: Workout Dashboard v2.0 — Constructive Growth Dashboard

## Design Philosophy
- **NOT** hiding problems or toxic positivity
- **Frame everything through growth**: show baseline → current → target
- **Mood as hero element**: Bio-Log emoji integration
- **Goal-oriented**: 10K readiness for Feb 23

## Checklist
- [ ] Phase 1: Bio-Log API Integration
- [ ] Phase 2: 10K Readiness Calculator
- [ ] Phase 3: Dashboard UI Overhaul
- [ ] Phase 4: Deploy & Verify

---

## Phase 1: Bio-Log API Integration
**Affected Files:**
- `file 'Sites/workout-legal/server.ts'`

**Changes:**
- Add new endpoint `/api/bio/today` returning:
  - Today's mood emoji (from `bio_snapshots`)
  - Today's reflection note
  - Associated vitals (RHR, steps at time of log)
- Add new endpoint `/api/bio/week` returning:
  - Last 7 days of mood emojis with dates
- Connect to `N5/data/journal.db` (Bio-Log database)

**Test:**
- `curl /api/bio/today` returns `{ emoji: "😤", note: "...", date: "..." }`
- `curl /api/bio/week` returns array of 7 objects

---

## Phase 2: 10K Readiness Calculator
**Affected Files:**
- `file 'Sites/workout-legal/server.ts'`

**Changes:**
- Add endpoint `/api/goals/10k-readiness` returning:
  - `percentage` (0-100)
  - `longestRun` (km)
  - `weeklyVolume` (km)
  - `streak` (days)
  - `rhrDelta` (from baseline)
  - `weeksRemaining` (until Feb 23)
  - `nextMilestone` (text)

**Formula:**
```
readiness = (
  (longestRun / 10) * 0.30 +           // 30% longest run vs 10K
  (weeklyVolume / 25) * 0.25 +         // 25% weekly volume vs 25km target
  min(streak / 14, 1) * 0.25 +         // 25% consistency (capped at 14 days)
  (rhrDrop / 15) * 0.20                // 20% RHR improvement (capped at 15 bpm drop)
) * 100
```

**Test:**
- `curl /api/goals/10k-readiness` returns valid JSON with percentage

---

## Phase 3: Dashboard UI Overhaul
**Affected Files:**
- `file 'Sites/workout-legal/src/pages/Dashboard.tsx'`
- `file 'Sites/workout-legal/src/components/section-cards.tsx'`
- `file 'Sites/workout-legal/src/hooks/use-health-data.ts'`

**New Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  [😤]  "Day 7"                        Dec 26, 2025      │
│  ───────────────────────────────────────────────────────│
│  Last 7 days: 😤 😌 😐 😤 😌 😤 😴                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  10K READINESS: Feb 23                                  │
│  ████████░░░░░░░░░░░░░░░░░░░░  34%                     │
│  8 weeks out · Building base · On track                 │
│  Next milestone: Complete a 5K without stopping         │
└─────────────────────────────────────────────────────────┘

┌────────────────────┬────────────────────┬───────────────┐
│ RHR: 88 → 75 bpm   │ Distance: 16.7 km  │ Streak: 7     │
│ Target: 65         │ This month         │ days          │
│ Lever: Sleep       │ ↑ from 8 km prev   │ 🔥            │
└────────────────────┴────────────────────┴───────────────┘

┌─────────────────────────────────────────────────────────┐
│  INSIGHT                                                │
│  "Pace isn't the focus yet — you're building the       │
│   aerobic base. Keep showing up."                       │
└─────────────────────────────────────────────────────────┘
```

**Changes:**
- Strip out SaaS-style layout
- Create `MoodHero` component (emoji + streak + 7-day row)
- Create `ReadinessBar` component (progress bar + milestone)
- Refactor `SectionCards` to show baseline → current → target
- Update `CoachingCard` to be constructive growth focused

---

## Phase 4: Deploy & Verify
**Actions:**
- Run `bun run build`
- Restart `workout-legal` service
- Visual verification via screenshot

**Success Criteria:**
- [ ] Mood emoji displays from Bio-Log
- [ ] 7-day mood row renders
- [ ] 10K readiness percentage shows and is reasonable
- [ ] RHR shows Sep baseline → current
- [ ] No "Total Revenue" or placeholder data visible
- [ ] Coaching insight is constructive (not generic)

---

## Data Sources

| Data | Source | Table |
|------|--------|-------|
| Mood emoji | `N5/data/journal.db` | `bio_snapshots` |
| RHR baseline/current | `Personal/Health/workouts.db` | `daily_resting_hr` |
| Run history | `Personal/Health/workouts.db` | `workouts` |
| Activity | `Personal/Health/workouts.db` | `daily_activity_summary` |
| Sleep | `Personal/Health/workouts.db` | `sleep_sessions` |


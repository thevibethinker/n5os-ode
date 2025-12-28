---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_wne5ccsJoVnFSW6f
---

# Personal Performance Intelligence System

## Overview

A holistic system that correlates **biometric data** (Fitbit), **cognitive output** (meetings, transcripts), and **environmental factors** to provide V with actionable insights about optimal performance patterns.

**Goal:** Answer questions like:
- Which meetings stress me out?
- What times of day am I performing optimally?
- Does my 2pm energy drop hypothesis hold?
- How do sleep, HRV, and meeting density interact?

**Future-Proofing:** Architected to integrate genomic data when available.

---

## Architecture

### Data Sources (Current)

| Source | Location | Granularity | Status |
|--------|----------|-------------|--------|
| Fitbit HR | `Personal/Health/workouts.db:intraday_heart_rate` | Per-minute | ✅ 39K+ readings |
| Fitbit Daily | `Personal/Health/workouts.db:daily_resting_hr` | Daily | ✅ HRV, RHR |
| Fitbit Activity | `Personal/Health/workouts.db:daily_activity_summary` | Daily | ✅ Steps, Active Min |
| Fitbit Sleep | `Personal/Health/workouts.db:daily_sleep` | Nightly | ✅ Score, Duration |
| Calendar | Google Calendar API | Per-event | ✅ Connected |
| Transcripts | `Personal/Meetings/*/transcript.md` | Per-meeting | ✅ Existing |
| Bio-Logs | `N5/data/journal.db:bio_snapshots` | 3x daily | ✅ Mood, Diet |
| Wellness DV | `N5/data/wellness.db` | Daily | ✅ Triangulated |

### Data Sources (Future)

| Source | Integration Path | Status |
|--------|------------------|--------|
| Genomic Data | Import to `Personal/Health/genomics.db` | 🔜 Pending |
| Screen Time | Apple/Android export → parse | 🔜 Optional |
| Location | Calendar location field / manual | 🔜 Optional |

---

## Components to Build

### Component A: Meeting-HR Correlator
**Purpose:** Link calendar events with intraday heart rate to detect stress patterns.

**Schema:** `N5/data/performance.db:meeting_hr_correlation`
```sql
CREATE TABLE meeting_hr_correlation (
    id INTEGER PRIMARY KEY,
    meeting_date TEXT NOT NULL,
    meeting_title TEXT,
    meeting_type TEXT,  -- internal/external/solo
    attendees TEXT,     -- JSON array
    start_time TEXT,
    end_time TEXT,
    duration_minutes INTEGER,
    -- HR Metrics
    hr_baseline_before REAL,  -- 30min before meeting avg
    hr_during_avg REAL,
    hr_during_max REAL,
    hr_spike_delta REAL,      -- hr_during_avg - hr_baseline_before
    hr_recovery_minutes INTEGER, -- time to return to baseline
    -- Context
    time_of_day TEXT,  -- morning/afternoon/evening
    day_of_week TEXT,
    hrv_daily REAL,
    sleep_score_prev_night REAL,
    -- Derived
    stress_indicator TEXT,  -- low/medium/high based on spike
    UNIQUE(meeting_date, start_time)
);
```

**Script:** `N5/scripts/correlate_meeting_hr.py`
- Pulls calendar events for date range
- Joins with intraday_heart_rate
- Calculates baseline (30min pre-meeting avg)
- Calculates during-meeting stats
- Computes spike delta and recovery time
- Classifies stress level

### Component B: Time-of-Day Performance Analyzer
**Purpose:** Test the "2pm energy drop" hypothesis with data.

**Schema:** `N5/data/performance.db:hourly_performance`
```sql
CREATE TABLE hourly_performance (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,  -- 0-23
    -- HR Metrics
    hr_avg REAL,
    hr_variance REAL,
    -- Activity
    had_meeting INTEGER,  -- 0/1
    meeting_count INTEGER,
    -- Contextual
    day_of_week TEXT,
    is_workday INTEGER,
    -- Sleep context (from previous night)
    sleep_score REAL,
    hrv_morning REAL,
    UNIQUE(date, hour)
);
```

**Script:** `N5/scripts/analyze_hourly_performance.py`
- Aggregates intraday HR by hour
- Overlays meeting schedule
- Computes variance (high variance = stress/engagement)
- Links to previous night's sleep

### Component C: Transcript Wellness Scanner (B27 Block)
**Purpose:** Extract stress/wellness indicators from meeting transcripts.

**Output:** New intelligence block `B27_WELLNESS_INDICATORS.md`

**Metrics to Extract:**
1. **Speech Density:** Words per minute (proxy for pressure)
2. **Sentiment Trajectory:** Does mood shift during meeting?
3. **Physical Mentions:** "tired", "headache", "energized"
4. **Stress Language:** "urgent", "deadline", "pressure", "worried"
5. **V's Talk Ratio:** % of meeting V is speaking

**Integration:** Add to `Prompts/Blocks/Generate_B27.prompt.md`

### Component D: Performance Dashboard Generator
**Purpose:** Weekly synthesis report correlating all data.

**Output:** `Personal/Health/Reports/weekly_performance_YYYY-WW.md`

**Sections:**
1. **Weekly Summary:** HRV trend, sleep avg, meeting hours
2. **Time-of-Day Analysis:** Best/worst performance hours
3. **Meeting Stress Report:** Top 3 stressful meetings with HR data
4. **Correlation Insights:** "High meeting density + low sleep → HRV drop"
5. **Recommendations:** "Block 2-3pm for recovery on Thursdays"

---

## Implementation Order

| Phase | Component | Complexity | Dependencies |
|-------|-----------|------------|--------------|
| 1 | Meeting-HR Correlator | Medium | Calendar API, intraday HR |
| 2 | Time-of-Day Analyzer | Low | Intraday HR, meeting data |
| 3 | B27 Wellness Block | Medium | Transcript pipeline |
| 4 | Performance Dashboard | Medium | All above |

---

## Trap Doors Identified

1. **Database Choice:** Using SQLite (`performance.db`) - consistent with existing pattern. Cost to reverse: Low.
2. **HR Baseline Window:** 30 minutes pre-meeting. May need tuning. Easy to adjust.
3. **Stress Thresholds:** Will need calibration to V's personal ranges.

---

## Success Criteria

- [ ] Can query "which meetings spiked my HR this week?"
- [ ] Can visualize hourly performance patterns
- [ ] 2pm hypothesis tested with data
- [ ] Weekly report generated automatically
- [ ] Architected for genomic data integration

---

## Genomic Integration Path (Future)

When genomic data arrives:
1. Parse into `Personal/Health/genomics.db` with relevant SNPs
2. Add columns to `hourly_performance` for genetic predispositions
3. Correlate: "Your COMT gene suggests afternoon cortisol sensitivity"
4. Personalized recommendations based on genetic+biometric


---
created: 2026-01-25
last_edited: 2026-01-25
version: 1.0
provenance: con_H2rUeFjHpuRueJYI
---

# Performance Intelligence Dashboard v2 — Build Plan

## Open Questions

1. **Weather API**: Which provider? OpenWeatherMap (free tier) vs WeatherAPI vs Open-Meteo (fully free, no key)?
   - **Decision**: Use Open-Meteo — no API key required, free, sufficient for daily weather correlation
   
2. **Calendar exclusion tag**: Should we use existing `[SKIP]` tag or create a new `[NO-METRIC]` tag?
   - **Decision**: Use `[SKIP]` from existing V-OS tag system. Events with `[SKIP]` in description = excluded from meeting load calculations.
   
3. **Dashboard output format**: Plain text (current) vs HTML vs Markdown with charts?
   - **Decision**: Rich Markdown with ASCII sparklines and clear sections. Later: HTML version for web display.

4. **Sleep quality data**: Fitbit API endpoint check needed — is `sleep_score` available?
   - **Parking**: Check during Phase 1, work around if unavailable.

---

## Checklist

### Phase 1: Data Layer Consolidation
- [ ] Audit and document all data source schemas
- [ ] Create unified `performance_data.py` module with consistent interfaces
- [ ] Integrate workouts.db fully (workouts, resting HR, activity, sleep)
- [ ] Add content_library.db integration (weekly consumption stats)
- [ ] Add tasks.db integration (completion rate, pending count)
- [ ] Create data freshness/reliability scoring

### Phase 2: Calendar Integration
- [ ] Build Google Calendar loader with meeting extraction
- [ ] Implement `[SKIP]` tag detection for exclusion
- [ ] Calculate metrics: meeting count, total hours, fragmentation score, back-to-back count
- [ ] Store weekly calendar snapshots for comparison

### Phase 3: Weather Integration
- [ ] Integrate Open-Meteo API (NYC coordinates)
- [ ] Capture daily: temp high/low, conditions, precipitation
- [ ] Store alongside other daily metrics

### Phase 4: Dashboard Generator Rewrite
- [ ] Design new dashboard format (see wireframe below)
- [ ] Implement trend indicators (↑↓→) and sparklines
- [ ] Add week-over-week comparisons
- [ ] Add "Signals" section for anomaly detection
- [ ] Add reliability indicators for each data section

### Phase 5: Testing & Polish
- [ ] Run dashboard on historical data
- [ ] Validate all data sources populate correctly
- [ ] Add error handling for missing/sparse data
- [ ] Update scheduled agent to use new script

---

## Phase Details

### Phase 1: Data Layer Consolidation

**Affected Files:**
- `N5/scripts/performance_data.py` (NEW)
- `N5/scripts/performance_dashboard.py` (MODIFY)

**Changes:**
Create a clean data access layer that abstracts all sources:

```python
# performance_data.py - interfaces
def get_weekly_resting_hr(days=7) -> dict  # avg, min, max, trend, data_points
def get_weekly_activity(days=7) -> dict    # steps, active_min, workouts, data_points
def get_weekly_sleep(days=7) -> dict       # avg_hours, min, max, data_points
def get_weekly_tasks(days=7) -> dict       # completed, added, pending, completion_rate
def get_weekly_content(days=7) -> dict     # items_added, by_type, sources
def get_data_freshness() -> dict           # last_update per source, staleness flags
```

**Data Sources:**
| Source | DB | Table | Key Columns |
|--------|-----|-------|-------------|
| Resting HR | workouts.db | daily_resting_hr | date, resting_hr |
| Activity | workouts.db | daily_activity_summary | date, steps, active_minutes, calories |
| Sleep | workouts.db | daily_sleep | date, minutes_asleep, sleep_score |
| Workouts | workouts.db | workouts | date, workout_type, duration_min, hr_avg |
| Tasks | tasks.db | tasks | status, created_at, completed_at |
| Content | content_library.db | items | type, source, created_at |

**Unit Tests:**
- Test each getter returns expected dict structure
- Test with empty data (graceful handling)
- Test date range filtering

---

### Phase 2: Calendar Integration

**Affected Files:**
- `N5/scripts/calendar_metrics.py` (NEW)
- `N5/scripts/performance_data.py` (MODIFY - add calendar interface)

**Changes:**
```python
# calendar_metrics.py
def fetch_week_events(start_date, end_date) -> list[dict]
def filter_real_meetings(events) -> list[dict]  # excludes [SKIP] tagged
def calculate_metrics(events) -> dict:
    # meeting_count, total_hours, fragmentation_score, back_to_back_count
    # busiest_day, quietest_day
```

**Exclusion Logic:**
- Check event description for `[SKIP]` tag
- Check event title for known block patterns: "Focus time", "Block", "Hold"
- All-day events excluded by default
- Events < 10 min excluded (travel buffers)

**Fragmentation Score:**
```
fragmentation = 1 - (largest_uninterrupted_block / total_working_hours)
# Higher = more fragmented day
```

**Unit Tests:**
- Test [SKIP] detection in various positions
- Test fragmentation calculation
- Test with zero meetings (edge case)

---

### Phase 3: Weather Integration

**Affected Files:**
- `N5/scripts/weather_data.py` (NEW)
- `N5/scripts/performance_data.py` (MODIFY - add weather interface)

**Changes:**
```python
# weather_data.py
COORDS = {"lat": 40.7128, "lon": -74.0060}  # NYC default

def fetch_daily_weather(date) -> dict:
    # temp_high, temp_low, conditions, precipitation_mm
    
def fetch_week_weather(days=7) -> list[dict]
```

**API:** Open-Meteo (no key required)
```
https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode
```

**Unit Tests:**
- Test API response parsing
- Test fallback on API failure

---

### Phase 4: Dashboard Generator Rewrite

**Affected Files:**
- `N5/scripts/performance_dashboard.py` (REWRITE)

**New Dashboard Format:**

```
════════════════════════════════════════════════════════════════════
  WEEKLY PERFORMANCE INTELLIGENCE  │  Week of Jan 20-26, 2026
════════════════════════════════════════════════════════════════════

┌─ VITALS ────────────────────────────────────────────────────────┐
│                                                                  │
│  Resting HR      73 bpm avg    ▁▂▂▃▂▂▃    ↓ vs last week (76)  │
│  Sleep           6.8 hrs avg   ▃▅▂▆▄▅▄    → stable              │
│  Activity        8,240 steps   ▂▄▆▃▅▇▄    ↑ +12% vs last week  │
│  Workouts        3 sessions    █░█░█░░                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ CALENDAR LOAD ─────────────────────────────────────────────────┐
│                                                                  │
│  Meetings        12 (8.5 hrs)   [████████░░] 42% of work time   │
│  Fragmentation   0.67 (HIGH)    Most fragmented: Tuesday        │
│  Back-to-back    4 instances    Longest gap: 2.5 hrs (Thu PM)   │
│                                                                  │
│  Excluded: 3 events tagged [SKIP]                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ COGNITIVE/OUTPUT ──────────────────────────────────────────────┐
│                                                                  │
│  Tasks Completed    8 of 12 due    (67% completion rate)        │
│  Tasks Added        5 new          Net: -3 (clearing backlog)   │
│  Pending Backlog    36 tasks       ↓ from 39 last week          │
│                                                                  │
│  Content Consumed   7 items        3 articles, 2 links, 2 posts │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ ENVIRONMENT ───────────────────────────────────────────────────┐
│                                                                  │
│  Weather (NYC)   42°F avg   ☁️ Mostly cloudy, 0.2" precip       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ SIGNALS ───────────────────────────────────────────────────────┐
│                                                                  │
│  ⚠️  RHR elevated Wed-Thu (+5 bpm). Check recovery/sleep.       │
│  ✓  Strong activity week despite high meeting load.             │
│  ⚠️  Tuesday was highly fragmented (6 meetings, no 1hr+ gap).   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ DATA QUALITY ──────────────────────────────────────────────────┐
│  Resting HR: ✓ 7/7 days  │  Sleep: ⚠️ 5/7 days  │  Tasks: ✓     │
│  Calendar: ✓             │  Weather: ✓          │  Content: ✓   │
└──────────────────────────────────────────────────────────────────┘

Generated: 2026-01-26 06:00 ET
```

**Signals Logic:**
- RHR > personal_baseline + 5 → flag
- Sleep < 6 hrs any day → flag
- Fragmentation > 0.6 → flag
- Task completion < 50% → flag
- 3+ back-to-back meetings → flag

**Unit Tests:**
- Test each section renders with sample data
- Test with sparse data (graceful degradation)
- Test signal detection thresholds

---

### Phase 5: Testing & Polish

**Affected Files:**
- All above files
- `N5/agents/weekly_performance_dashboard.md` (MODIFY - update agent)

**Changes:**
- Add comprehensive error handling
- Add `--debug` flag to show raw data
- Add `--week YYYY-MM-DD` flag to generate historical dashboards
- Update scheduled agent to use new script

**Unit Tests:**
- End-to-end test with mocked data
- Test scheduled agent invocation

---

## Success Criteria

1. **Data Integration**: Dashboard pulls from 6+ data sources (HR, activity, sleep, calendar, tasks, content, weather)
2. **Calendar Filtering**: Events with `[SKIP]` tag correctly excluded from metrics
3. **Reliability Transparency**: Dashboard shows data quality for each section
4. **Actionable Signals**: At least 3 signal types detect anomalies automatically
5. **Historical Support**: Can generate dashboard for any past week with `--week` flag
6. **No Regressions**: All current functionality preserved

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google Calendar API rate limits | Could fail mid-week | Cache events locally, only fetch delta |
| Sparse sleep data | Dashboard looks incomplete | Show "Insufficient data" gracefully, don't show section if <3 days |
| Weather API downtime | Missing environment context | Cache last known, show staleness indicator |
| Fitbit sync gaps | RHR/activity missing days | Use available days, show coverage |

---

## Alternatives Considered

### Alt 1: Web-based dashboard (HTML + charts)
- **Pros**: Richer visualization, interactive
- **Cons**: More complex, requires hosting, overkill for weekly snapshot
- **Decision**: Defer. Start with rich Markdown, add HTML export later if needed.

### Alt 2: Pull all data into unified performance.db
- **Pros**: Single query point, faster dashboard generation
- **Cons**: Data duplication, sync complexity, migrations
- **Decision**: Rejected. Keep sources of truth separate, use access layer.

### Alt 3: Real-time dashboard (always up to date)
- **Pros**: Check anytime, no waiting for weekly report
- **Cons**: More infrastructure, query overhead, less "weekly summary" feel
- **Decision**: Defer. Weekly cadence matches current workflow.

---

## Trap Doors (Irreversible Decisions)

1. **Schema changes to existing DBs**: None planned — read-only access to existing tables
2. **Calendar data model**: If we store calendar snapshots, that schema is a commitment — design carefully

---

## Execution Approach

**Single-worker build** — This is cohesive enough to execute in one thread with phases.

Estimated time: 4-5 hours active work across 2-3 sessions.

---

## Handoff Notes

Ready for Builder. Start with Phase 1 (data layer), validate each phase before proceeding.

Test command after Phase 1:
```bash
python3 /home/workspace/N5/scripts/performance_data.py --test
```

---
title: Vibe Trainer Report
description: Generate a progress report and update the Vibe Trainer dashboard
tags: [health, fitness, wellness, coach]
tool: true
---

# Vibe Trainer Progress Report Generator

Generate a comprehensive progress report based on V's recent wellness data and update the public dashboard.

## Data Sources to Pull

1. **Fitbit Data** (last 7-14 days):
   ```bash
   sqlite3 /home/workspace/Personal/Health/workouts.db "SELECT date, steps, distance_km, resting_hr, very_active_minutes FROM daily_activity_summary ORDER BY date DESC LIMIT 14"
   ```

2. **Coaching Notes**:
   - Read `file 'Personal/Health/COACHING_NOTES.md'` for accumulated observations

3. **Genetic Profile**:
   - Reference `file 'Personal/Health/V_GENETIC_PROFILE.md'` for genetic context

4. **BioLog** (optional, if mood context needed):
   ```bash
   sqlite3 /home/workspace/N5/data/journal.db "SELECT * FROM bio_snapshots ORDER BY created_at DESC LIMIT 7"
   ```

## Report Structure

Generate a report with these sections:

### Where You Are
- Current training phase
- Days to race/goal
- Current week in program

### This Week's Numbers
- Average steps
- Average resting HR (and trend: improving/stable/declining)
- Workouts logged
- Active minutes per day
- Average distance

### Recent Wins
- 3-5 concrete achievements from the data
- Be specific (dates, numbers)

### Patterns Noticed
- Data-driven observations
- ALWAYS connect to genetic profile where relevant

### Focus Next Period
- 1-2 specific, actionable items

### Honest Assessment
- Direct, no-BS take on where things stand
- What's working, what isn't
- What to watch for

## Output

1. **Save markdown report** to:
   `file 'Personal/Health/progress_reports/YYYY-MM-DD_progress.md'`

2. **Update dashboard JSON** at:
   `file 'Sites/vibe-trainer/src/data/latest_report.json'`
   
   Use this schema:
   ```json
   {
     "generated_at": "ISO timestamp",
     "report_period": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" },
     "current_phase": {
       "name": "Phase name",
       "program": "Program name",
       "race_goal": "Goal description",
       "days_to_race": number,
       "current_week": "Week description"
     },
     "metrics": {
       "avg_steps": number,
       "avg_resting_hr": number,
       "resting_hr_trend": "improving|stable|declining",
       "active_minutes_avg": number,
       "avg_distance_km": number,
       "workouts_logged": number
     },
     "recent_wins": ["string array"],
     "patterns_noticed": [
       { "pattern": "string", "genetic_connection": "string" }
     ],
     "focus_next_period": ["string array"],
     "honest_assessment": "string",
     "genetic_profile": {
       "actn3": "string",
       "comt": "string",
       "caffeine": "string",
       "lactose": "string"
     }
   }
   ```

3. **Update COACHING_NOTES.md** with a new observation entry

## Dashboard URL

**Live at:** https://vibe-trainer-va.zocomputer.io/


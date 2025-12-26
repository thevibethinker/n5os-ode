---
created: 2025-12-10
last_edited: 2025-12-10
version: 1
---
# Worker Assignment: Journal System Enhancements

## Context

V and I just built a journaling/reflection system with:
- SQLite database at `N5/data/journal.db`
- CLI tool at `N5/scripts/journal.py`
- 5 reflection prompts in `Prompts/reflections/`
- New "Vibe Coach" persona (ID: `9790ca46-ae01-4ad5-b2eb-a5e72aeb22e7`)

Now we need to add enhancements.

## Required Enhancements

### 1. Pattern Analytics Script
**Priority: High**

Create `N5/scripts/journal_analytics.py` that:
- Analyzes entries for mood trends over time
- Identifies recurring themes/words
- Tracks temptation triggers and outcomes
- Surfaces patterns like "You mentioned X frequently on Mondays"
- Can be run on-demand or as part of weekly synthesis

### 2. Scheduled Reminder Agents
**Priority: High**

Create scheduled tasks for:
- **Morning Pages**: Daily at 8:00 AM ET — Send SMS reminder to V
- **Evening Reflection**: TBD timing (suggest 9:00 PM ET as default, can be adjusted)

Use `create_scheduled_task` tool. The instruction should:
- Send a gentle nudge via SMS
- Not be pushy — warm invitation energy matching Vibe Coach

### 3. Temptation Follow-Up Loop
**Priority: High**

When a temptation check-in is logged:
- Schedule a follow-up check-in 2 hours later
- This could be a simple SMS: "Hey, checking in from earlier. How are you doing now?"

Implementation options:
- Add a flag/hook in the journal CLI `add` command for temptation entries
- Or create a separate script that monitors for new temptation entries

### 4. Tag Taxonomy System
**Priority: Medium**

Enhance the journal system with structured tags:
- `mood:anxious`, `mood:calm`, `mood:energized`
- `trigger:work`, `trigger:social`, `trigger:fatigue`
- `theme:relationships`, `theme:career`, `theme:health`

Update CLI to:
- Accept structured tags
- Query by tag category
- Suggest tags based on content (optional LLM enhancement)

### 5. Cross-Reflection Synthesis
**Priority: Medium**

Create `N5/scripts/journal_synthesis.py` that:
- Generates weekly/monthly digests
- Identifies patterns across entries
- Highlights insights like:
  - "Your mood has been higher on days you did morning pages"
  - "Temptation entries cluster around Thursday evenings"
- Could run as a scheduled weekly task

### 6. Calendar Integration
**Priority: Medium**

For evening reflections, pre-populate context:
- Fetch today's calendar events via `use_app_google_calendar`
- Include in the evening reflection prompt as context
- "You had meetings with X, Y, Z today..."

## Database Location

`N5/data/journal.db`

Current schema:
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entry_type TEXT NOT NULL DEFAULT 'journal',
    content TEXT NOT NULL,
    mood TEXT,
    tags TEXT,
    word_count INTEGER DEFAULT 0
);
```

May need to extend for:
- Structured tags (could stay as comma-separated or normalize to separate table)
- Follow-up tracking for temptation entries

## Existing Files

- `N5/scripts/journal.py` — Main CLI
- `Prompts/reflections/*.prompt.md` — Reflection rubrics
- `Prompts/Journal.prompt.md` — Main journal prompt

## Success Criteria

1. ✅ Pattern analytics script works and surfaces useful insights
2. ✅ Morning Pages reminder scheduled for 8 AM daily via SMS
3. ✅ Evening reflection reminder scheduled (9 PM ET)
4. ✅ Temptation follow-up loop implemented (hourly monitor)
5. ✅ Tag system enhanced with structured categories
6. ✅ Weekly synthesis script created
7. ✅ All scripts tested and documented

## Notes

- V uses dictation on desktop, so voice input is handled externally
- Keep the Vibe Coach energy in any SMS/notifications — warm, not nagging
- This is a personal system, so optimize for V's workflow

---

## Execution Summary

**Worker executed:** 2025-12-15 08:32 ET

### Completed Items

| Enhancement | Implementation | Status |
|------------|----------------|--------|
| 1. Pattern Analytics | `N5/scripts/journal_analytics.py` - analyzes mood, tags, temptations | ✅ Pre-existing |
| 2. Morning Pages Reminder | Scheduled task `f421bdc2...` - 8 AM daily SMS | ✅ Pre-existing |
| 3. Evening Reflection | Scheduled task `068d70a9...` - 9 PM daily SMS with calendar context | ✅ Pre-existing |
| 4. Temptation Follow-Up | `N5/scripts/monitor_temptations.py` + hourly scheduled task `d8c9b5c2...` | ✅ Pre-existing |
| 5. Tag Taxonomy | Enhanced `journal.py` with `tags` command and `by_tag()` query function | ✅ Enhanced |
| 6. Weekly Synthesis | Created `N5/scripts/journal_synthesis.py` - generates weekly/monthly digests | ✅ New |
| 7. Calendar Integration | Evening reflection task fetches Google Calendar events | ✅ Pre-existing |

### New Scripts Created

1. **`N5/scripts/journal_synthesis.py`** - Weekly/monthly digest generator
   - Analyzes mood patterns
   - Tracks entry types by day of week
   - Deep temptation pattern analysis (by hour, by weekday)
   - Tag usage and structured category tracking
   - Word count statistics
   - Human-readable insights generation
   - Saves digests to `N5/digests/`

### Enhancements Made

1. **`N5/scripts/journal.py`** - Added:
   - `tags` subcommand to list all tags and categories
   - `by_tag()` function to filter entries by tag or category
   - Support for structured tag queries (e.g., `mood:`, `trigger:work`)

### Verification

```bash
# Synthesis report (working)
python3 N5/scripts/journal_synthesis.py --period weekly

# Tags command (working)
python3 N5/scripts/journal.py tags

# Analytics report (working)
python3 N5/scripts/journal_analytics.py --days 7
```

All enhancements verified functional.



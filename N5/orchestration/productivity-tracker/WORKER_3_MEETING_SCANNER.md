# Worker 3: Meeting Scanner

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W3-MEETING-SCANNER  
**Estimated Time:** 45 minutes  
**Dependencies:** Worker 1 (Database Setup - COMPLETE)

---

## Mission

Build Google Calendar scanner that tracks expected load (meetings, blocked time) and stores data in productivity_tracker.db to calculate True RPI (actual output vs. demand).

---

## Context

The productivity tracker needs to measure **relative productivity** - not just "emails sent" but "emails sent given available time". This worker implements the demand-side of the equation:

- **Expected Load** = Meetings + external obligations that consume your time
- **Available Time** = Business hours - Expected Load
- **True RPI** = (Actual Output / Available Time) × baseline_factor

This is crucial because:
- Sending 20 emails on a day with 0 meetings is different from 20 emails on a day with 6 hours of meetings
- True RPI accounts for this: same output, less available time = higher productivity

---

## Dependencies

**Must exist before starting:**
- ✅ Database schema (Worker 1 complete)
- ✅ `productivity_tracker.db` at `/home/workspace/productivity_tracker.db`
- ✅ Google Calendar integration available via `use_app_google_calendar`

**Files you'll reference:**
- `file 'N5/orchestration/productivity-tracker/productivity-tracker-design.md'` (architecture)
- `file 'N5/scripts/productivity/db_setup.py'` (schema reference)
- `file 'N5/scripts/productivity/email_scanner.py'` (pattern to follow)

---

## Deliverables

1. **`/home/workspace/N5/scripts/productivity/meeting_scanner.py`**
   - Executable Python script with shebang, logging, argparse
   - Scans Google Calendar for meetings/events
   - Stores to `expected_load` table
   - Calculates daily time consumption
   - Supports `--date YYYY-MM-DD` (single day) and `--start/--end` (range)
   - Includes `--dry-run` flag

2. **Test results**
   - Successful scan of last 7 days
   - Verification of data in database
   - Log output showing meetings found and time consumed

3. **Brief README update**
   - Add meeting_scanner.py usage to `/home/workspace/N5/scripts/productivity/README.md`

---

## Requirements

### Database Schema Reference

```sql
CREATE TABLE expected_load (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    source TEXT NOT NULL,  -- 'calendar', 'manual', 'recurring'
    type TEXT NOT NULL,    -- 'meeting', 'blocked_time', 'travel', 'other'
    hours REAL NOT NULL,
    title TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Google Calendar Integration

Use the `use_app_google_calendar` tool with `google_calendar-list-events`:

```python
# Example pattern:
configured_props = {
    "calendarId": "primary",
    "timeMin": "2025-10-18T00:00:00Z",
    "timeMax": "2025-10-25T23:59:59Z",
    "timeZone": "America/New_York"
}
```

**Note:** You're an LLM agent - call `list_app_tools('google_calendar')` first to see available tools, then use `use_app_google_calendar(tool_name, configured_props)` within your logic.

### Meeting Processing Rules

1. **Include:**
   - Accepted meetings
   - Tentative meetings (count as load)
   - All-day events that block time
   - Recurring meetings

2. **Exclude:**
   - Declined meetings
   - Cancelled events
   - Events you created but no one else attended (self-blocks)

3. **Time Calculation:**
   - Round to nearest 0.25 hours (15 min increments)
   - Cap single meeting at 4 hours (all-day events → 4 hours)
   - Include travel time if in event metadata
   - Business hours: 9am-6pm ET (9 hours)

4. **Metadata Storage:**
   Store as JSON:
   ```json
   {
     "event_id": "calendar_event_id",
     "attendees": 5,
     "organizer": "email@domain.com",
     "location": "Zoom / Office",
     "recurring": true
   }
   ```

---

## Implementation Guide

### Script Structure

```python
#!/usr/bin/env python3
"""
Meeting Scanner - Google Calendar Expected Load Tracker
Scans Google Calendar and stores meeting time consumption
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

def main(date: str = None, start_date: str = None, end_date: str = None, dry_run: bool = False) -> int:
    """Scan Google Calendar and store expected load."""
    try:
        # Date validation
        if not date and not (start_date and end_date):
            # Default: scan last 7 days
            end = datetime.now()
            start = end - timedelta(days=7)
        elif date:
            start = end = datetime.strptime(date, "%Y-%m-%d")
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info(f"Scanning meetings: {start.date()} to {end.date()}")
        
        # Fetch events from Google Calendar
        events = fetch_calendar_events(start, end, dry_run)
        
        if not events:
            logger.info("No events found in date range")
            return 0
        
        # Process and store
        daily_load = process_events(events)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would store {len(daily_load)} daily load records")
            for date, hours in daily_load.items():
                logger.info(f"[DRY RUN]   {date}: {hours:.2f} hours")
            return 0
        
        store_expected_load(daily_load)
        
        logger.info(f"✓ Stored {len(daily_load)} days of expected load")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

def fetch_calendar_events(start: datetime, end: datetime, dry_run: bool) -> list:
    """Fetch events from Google Calendar.
    
    Note: This is pseudocode showing the logic. As an LLM agent,
    you'll need to implement this by calling list_app_tools and
    use_app_google_calendar appropriately.
    """
    # Your implementation here using Zo's app tools
    pass

def process_events(events: list) -> dict:
    """Process events into daily time consumption.
    
    Returns:
        Dict mapping date strings to total hours
    """
    daily_load = {}
    
    for event in events:
        # Skip declined/cancelled
        if is_declined_or_cancelled(event):
            continue
        
        # Calculate duration
        duration_hours = calculate_duration(event)
        
        # Get date
        event_date = extract_date(event)
        
        # Aggregate
        if event_date not in daily_load:
            daily_load[event_date] = 0.0
        daily_load[event_date] += duration_hours
    
    return daily_load

def store_expected_load(daily_load: dict) -> None:
    """Store daily load to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for date_str, hours in daily_load.items():
        cursor.execute("""
            INSERT OR REPLACE INTO expected_load (date, source, type, hours, title, metadata)
            VALUES (?, 'calendar', 'meeting', ?, 'Daily meeting load', ?)
        """, (date_str, hours, json.dumps({"scanned_at": datetime.now(timezone.utc).isoformat()})))
    
    conn.commit()
    conn.close()

# Helper functions
def is_declined_or_cancelled(event: dict) -> bool:
    """Check if event should be excluded."""
    # Implementation
    pass

def calculate_duration(event: dict) -> float:
    """Calculate event duration in hours (rounded to 0.25)."""
    # Implementation
    pass

def extract_date(event: dict) -> str:
    """Extract date string YYYY-MM-DD from event."""
    # Implementation
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan Google Calendar for expected load")
    parser.add_argument("--date", help="Single date YYYY-MM-DD")
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    exit(main(date=args.date, start_date=args.start, end_date=args.end, dry_run=args.dry_run))
```

### Key Patterns

1. **Error Handling:** Wrap all operations in try/except
2. **Logging:** Log all significant events with timestamps
3. **Dry Run:** Respect `--dry-run` flag throughout
4. **State Verification:** Check database writes
5. **Timezone Handling:** Always use ET (America/New_York) for consistency

---

## Testing

### Validation Checklist

```bash
# 1. Dry run test
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py --dry-run

# 2. Scan last 7 days
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py

# 3. Verify database writes
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT date, hours, title FROM expected_load ORDER BY date DESC LIMIT 10;"

# 4. Test specific date
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py --date 2025-10-24

# 5. Test date range
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py \
  --start 2025-10-18 --end 2025-10-25
```

### Success Criteria

- [ ] Script runs without errors
- [ ] Dry run shows expected meetings
- [ ] Database contains expected_load records
- [ ] Hours calculated correctly (rounded to 0.25)
- [ ] Declined meetings excluded
- [ ] All-day events capped at 4 hours
- [ ] Logging shows meeting count and time totals
- [ ] README.md updated with usage

---

## Report Back

When complete, report:

1. ✅ meeting_scanner.py created and tested
2. ✅ Last 7 days scanned successfully
3. ✅ Database verification passed
4. ✅ Example output showing meetings found and hours tracked
5. ✅ README.md updated

**Format:**
```
Worker 3 (Meeting Scanner): COMPLETE

Deliverables:
- /home/workspace/N5/scripts/productivity/meeting_scanner.py (executable, 250 lines)
- Database verified: 7 days of expected_load data stored
- Test results: 23 meetings found, 18.5 hours tracked across 7 days

Example:
  2025-10-24: 3.0 hours (4 meetings)
  2025-10-23: 2.5 hours (3 meetings)
  ...

Ready for Worker 4 (XP System).
```

---

## Architecture Principles Compliance

- **P0 (Rule-of-Two):** Loading design doc + email_scanner.py pattern only
- **P2 (SSOT):** Database is single source of truth
- **P7 (Dry-Run):** Implemented with `--dry-run` flag
- **P18 (Verify State):** Database verification included
- **P19 (Error Handling):** Try/except with logging
- **P22 (Language Selection):** Python chosen for Gmail/Calendar API SDKs and data processing

---

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 20:37 ET  
**Status:** READY FOR EXECUTION

# Worker 3: Meeting Scanner

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W3-MEETING-SCANNER  
**Estimated Time:** 45 minutes  
**Dependencies:** Worker 1 (Database Setup)

---

## Mission

Build Google Calendar integration that scans meetings, calculates expected follow-up emails (load), and classifies stakeholder types for productivity tracking.

---

## Context

Meetings generate follow-up obligations. The meeting scanner:
- Tracks all calendar events via Google Calendar API
- Calculates expected emails: 1:1 meetings = 1.0, group meetings = 0.5/attendee
- Classifies stakeholder type from attendee domains/patterns
- Stores as load_events for RPI calculation

---

## Dependencies

Worker 1 complete (database exists)

---

## Deliverables

1. `/home/workspace/N5/scripts/productivity/meeting_scanner.py`
2. Test scan output showing meeting→load conversion
3. Stakeholder classification accuracy > 80%

---

## Requirements

### Load Calculation

- 1:1 meeting (2 attendees): 1.0 expected email
- Small group (3-5): 0.5 per external attendee
- Large group (6+): 0.3 per external attendee
- All-day events: 0 (usually conferences/blocking)
- Declined events: 0

### Stakeholder Classification

```python
STAKEHOLDER_PATTERNS = {
    'customer': ['client domains', 'B2B contact patterns'],
    'partner': ['partner org domains'],
    'coach': ['careerspan.com + role=coach'],
    'job_seeker': ['careerspan.com + role=client'],
    'internal': ['careerspan.com + role=team'],
    'other': ['default']
}
```

### Script Args

- `--scan-range`: today|week|month|historical|YYYY-MM-DD:YYYY-MM-DD
- `--dry-run`
- `--calendar-id`: default "primary"

---

## Implementation Template

```python
#!/usr/bin/env python3
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

def main(dry_run=False, scan_range="today"):
    # Use use_app_google_calendar("google_calendar-list-events")
    # Classify each meeting
    # Calculate expected_emails
    # Insert into load_events
    pass

def calculate_expected_emails(attendee_count: int, is_all_day: bool) -> float:
    if is_all_day:
        return 0
    if attendee_count <= 2:
        return 1.0
    elif attendee_count <= 5:
        return (attendee_count - 1) * 0.5
    else:
        return (attendee_count - 1) * 0.3

def classify_stakeholder(attendee_emails: list) -> str:
    # Domain-based classification
    # Pattern matching
    return 'other'

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scan-range", default="today")
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run, scan_range=args.scan_range))
```

---

## Testing

```bash
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py --scan-range week
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT event_type, stakeholder_type, SUM(expected_emails) FROM load_events WHERE event_type='meeting' GROUP BY stakeholder_type;"
```

---

## Report Back

1. ✅ Script created
2. ✅ Meeting load calculation working
3. ✅ Stakeholder classification implemented
4. ✅ Load events populated in database
5. ✅ Ready for RPI calculator

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-25 00:00 ET

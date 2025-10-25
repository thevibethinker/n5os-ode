# Worker 2: Email Scanner Core

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W2-EMAIL-SCANNER  
**Estimated Time:** 90 minutes  
**Dependencies:** Worker 1 (Database Setup)

---

## Mission

Build Gmail API integration script that scans sent emails, classifies them (new/follow-up/response), tracks incoming emails for load calculation, and stores substantial emails in database with proper era tagging.

---

## Context

The email scanner is the core data collection component. It must:
- Scan Gmail "SENT" folder via Zo's Gmail integration
- Classify email type based on thread analysis
- Extract metadata (subject tags, word count, response time)
- Filter trivial emails (auto-responses, <50 words)
- Track incoming substantial emails for RPI load calculation
- Tag emails with correct era (pre_superhuman, post_superhuman, post_zo)
- Support both historical baseline scan and incremental daily scans

---

## Dependencies

- Worker 1 complete (database exists)
- Gmail API access via `use_app_gmail`

---

## Deliverables

1. `/home/workspace/N5/scripts/productivity/email_scanner.py` - Main scanner script
2. Historical baseline scan complete (all 3 eras)
3. Test results showing classification accuracy
4. Log output showing scan progress

---

## Requirements

### Functional Requirements

**Email Classification Logic:**
- **New:** First email in thread where I'm sender
- **Follow-up:** Subsequent email in thread where I previously sent
- **Response:** Email in thread where someone else initiated

**Substantial Email Filter:**
- Word count ≥ 50 words
- Excludes: auto-replies, out-of-office, calendar invites
- Excludes: emails matching patterns like "Thanks!", "Got it", "Sounds good"

**Era Tagging:**
- Pre-Superhuman: Before 2024-11-12
- Post-Superhuman: 2024-11-12 to 2025-10-24
- Post-Zo: 2025-10-25 onwards

**Subject Tag Extraction:**
- Extract `[Tag]` from subject line
- Examples: `[Client]`, `[Careerspan]`, `[Personal]`

**Incoming Email Tracking:**
- Scan INBOX for substantial emails received
- Used for RPI load calculation (0.5 weight per email)
- Only track emails requiring response

### Technical Requirements

- Use `use_app_gmail` tool with `gmail-list-messages` and `gmail-get-message`
- Support `--scan-range` args: `today`, `week`, `month`, `historical`, `YYYY-MM-DD:YYYY-MM-DD`
- Support `--dry-run` mode
- Handle Gmail API rate limits gracefully
- Log progress every 50 emails
- Detect duplicates via gmail_message_id
- UTF-8 email handling

---

## Implementation Guide

### Script Structure

```python
#!/usr/bin/env python3
"""
Email Scanner - Gmail API Integration
Scans sent emails and classifies them for productivity tracking
"""

import sqlite3
import logging
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

# Era definitions
ERAS = {
    'pre_superhuman': ('2020-01-01', '2024-11-11'),
    'post_superhuman': ('2024-11-12', '2025-10-24'),
    'post_zo': ('2025-10-25', None)
}

def main(dry_run: bool = False, scan_range: str = "today") -> int:
    """Scan emails from Gmail"""
    try:
        start_date, end_date = parse_scan_range(scan_range)
        logger.info("Scanning emails from %s to %s", start_date, end_date or "now")
        
        if dry_run:
            logger.info("[DRY RUN] Would scan Gmail SENT folder")
            return 0
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Scan sent emails
        sent_count = scan_sent_emails(cursor, start_date, end_date)
        
        # Scan incoming emails for load tracking
        incoming_count = scan_incoming_emails(cursor, start_date, end_date)
        
        conn.commit()
        conn.close()
        
        logger.info("✓ Scanned %d sent emails, %d incoming emails", sent_count, incoming_count)
        return 0
        
    except Exception as e:
        logger.error("Email scan failed: %s", e, exc_info=True)
        return 1

def parse_scan_range(scan_range: str) -> tuple:
    """Convert scan_range to (start_date, end_date)"""
    today = datetime.now().date()
    
    if scan_range == "today":
        return (today.isoformat(), today.isoformat())
    elif scan_range == "week":
        week_ago = today - timedelta(days=7)
        return (week_ago.isoformat(), today.isoformat())
    elif scan_range == "month":
        month_ago = today - timedelta(days=30)
        return (month_ago.isoformat(), today.isoformat())
    elif scan_range == "historical":
        return ("2020-01-01", today.isoformat())
    elif ":" in scan_range:
        start, end = scan_range.split(":")
        return (start, end)
    else:
        return (scan_range, scan_range)

def scan_sent_emails(cursor, start_date, end_date) -> int:
    """
    Scan sent emails from Gmail
    NOTE: This is pseudocode. Actual implementation requires
    calling use_app_gmail tool which must be done by LLM, not script.
    
    Real implementation approach:
    1. LLM calls use_app_gmail to get message list
    2. LLM calls use_app_gmail to get each message details
    3. Script processes and stores in database
    
    For now, script provides helper functions for classification.
    """
    # TODO: Implement via LLM tool calls in actual execution
    # Script provides classification logic below
    pass

def classify_email(thread_msgs: list, current_msg: dict, my_email: str) -> str:
    """
    Classify email as 'new', 'follow_up', or 'response'
    
    Args:
        thread_msgs: All messages in thread (chronological)
        current_msg: The message being classified
        my_email: User's email address
    
    Returns:
        'new', 'follow_up', or 'response'
    """
    thread_msgs_before = [m for m in thread_msgs if m['date'] < current_msg['date']]
    
    if not thread_msgs_before:
        # First message in thread
        if current_msg['from'] == my_email:
            return 'new'
        else:
            return 'response'  # Shouldn't happen for SENT folder
    
    # Check if I've sent before in this thread
    my_previous_sends = [m for m in thread_msgs_before if m['from'] == my_email]
    
    if my_previous_sends:
        return 'follow_up'
    else:
        return 'response'

def is_substantial(email_body: str, subject: str) -> bool:
    """Filter out trivial emails"""
    # Word count check
    words = len(email_body.split())
    if words < 50:
        return False
    
    # Pattern matching for trivial content
    trivial_patterns = [
        r'^(thanks?|thank you|got it|sounds good|ok|okay)!?$',
        r'(out of office|automatic reply)',
        r'(calendar invitation|meeting invite)',
    ]
    
    body_lower = email_body.lower().strip()
    for pattern in trivial_patterns:
        if re.search(pattern, body_lower, re.IGNORECASE):
            return False
    
    return True

def extract_subject_tag(subject: str) -> str:
    """Extract [Tag] from subject line"""
    match = re.search(r'\[([^\]]+)\]', subject)
    return match.group(1) if match else None

def determine_era(email_date: str) -> str:
    """Determine which era the email belongs to"""
    date_obj = datetime.fromisoformat(email_date).date()
    
    for era_name, (start, end) in ERAS.items():
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date() if end else datetime.now().date()
        
        if start_date <= date_obj <= end_date:
            return era_name
    
    return 'post_zo'  # Default to current era

def calculate_response_time(thread_msgs: list, current_msg: dict) -> float:
    """Calculate response time in hours"""
    # Find previous message from someone else
    prev_msg = None
    for msg in reversed(thread_msgs):
        if msg['date'] < current_msg['date'] and msg['from'] != current_msg['from']:
            prev_msg = msg
            break
    
    if prev_msg:
        delta = current_msg['date'] - prev_msg['date']
        return delta.total_seconds() / 3600
    
    return None

def scan_incoming_emails(cursor, start_date, end_date) -> int:
    """
    Scan incoming emails for load tracking
    Similar approach: LLM calls tools, script processes
    """
    # TODO: Implement via LLM tool calls
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scan-range", default="today", 
                       help="today|week|month|historical|YYYY-MM-DD:YYYY-MM-DD")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run, scan_range=args.scan_range))
```

### Gmail API Integration Pattern

Since Python scripts can't directly call Zo tools, the actual implementation requires:

1. **Hybrid approach:** LLM calls `use_app_gmail` tools, script provides logic
2. **LLM execution steps:**
   - Call `gmail-list-messages` with date filters
   - For each message: call `gmail-get-message`
   - Use script's classification functions
   - Insert into database

3. **Alternative:** Create wrapper script that outputs commands for LLM to execute

---

## Testing

### Test Classification Logic
```python
# Test data
test_cases = [
    {
        'thread': [],
        'current': {'from': 'v@careerspan.com', 'date': '2025-10-25'},
        'expected': 'new'
    },
    {
        'thread': [{'from': 'client@example.com', 'date': '2025-10-24'}],
        'current': {'from': 'v@careerspan.com', 'date': '2025-10-25'},
        'expected': 'response'
    },
    {
        'thread': [
            {'from': 'v@careerspan.com', 'date': '2025-10-24'},
            {'from': 'client@example.com', 'date': '2025-10-24'}
        ],
        'current': {'from': 'v@careerspan.com', 'date': '2025-10-25'},
        'expected': 'follow_up'
    }
]
```

### Verify Database Entries
```bash
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT era, email_type, COUNT(*) FROM emails GROUP BY era, email_type;"
```

### Check Era Distribution
```bash
sqlite3 /home/workspace/productivity_tracker.db \
  "SELECT era, COUNT(*), MIN(sent_at), MAX(sent_at) FROM emails GROUP BY era;"
```

---

## Report Back

When complete, report:
1. ✅ Script created at `/home/workspace/N5/scripts/productivity/email_scanner.py`
2. ✅ Historical baseline scan complete
3. ✅ Email counts by era:
   - Pre-Superhuman: X emails
   - Post-Superhuman: Y emails
   - Post-Zo: Z emails (likely 0 initially)
4. ✅ Classification working (new/follow-up/response)
5. ✅ Substantial email filtering working
6. ✅ Incoming email tracking implemented
7. ✅ Ready for RPI calculator (Worker 5)

**Note:** If Gmail API access requires special setup, document blockers for orchestrator.

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-24 23:55 ET

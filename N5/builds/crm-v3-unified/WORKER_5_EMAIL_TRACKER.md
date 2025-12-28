# Worker 5: Email Tracker (Gmail Sent Items)

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W5-EMAIL-TRACKER  
**Estimated Time:** 30 minutes  
**Dependencies:** Worker 1 ✅, Worker 2 ✅, Worker 3 ✅, Worker 4 ✅, Worker 4B ✅  
**Can Run Parallel With:** Worker 6 (CLI Interface)

---

## Mission

Build Gmail "Sent Items" tracker that monitors V's sent emails, detects meaningful replies (excludes spam responses), and creates low-priority enrichment jobs for contacts not yet in CRM V3 database.

**Goal:** Capture organic relationship building through email exchanges automatically.

---

## Context

**Architecture:** CRM V3 uses multi-source ingestion. Email replies
[truncated]
n enrichment_queue
        VALUES (profile_id, scheduled_for='now + 7 days', checkpoint='checkpoint_1', priority=25, trigger_source='gmail_reply', trigger_metadata=JSON with thread_id)
    5. Return profile_id, job_id
    6. Log to intelligence_sources table
```

---

## Implementation Steps

### Step 1: Gmail Sent Items Poller (15 min)

**File:** `N5/scripts/crm_gmail_tracker.py`

```python
#!/usr/bin/env python3
"""
Gmail Sent Items Tracker for CRM V3
Monitors sent folder, detects replies to external contacts, queues enrichment.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = '/home/workspace/N5/data/crm_v3.db'

# Import from Worker 3's helpers
from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job

def get_sent_emails_since(since_timestamp: str) -> List[Dict]:
    """
    Fetch sent emails from Gmail using use_app_gmail tool.
    
    This function should use Zo's internal API to call use_app_gmail
    with the 'gmail-list-messages' action.
    
    For Worker 5 implementation: Use subprocess to call `zo` CLI
    or implement API call to Zo's use_app_gmail endpoint.
    
    Returns list of email dicts with:
    - message_id
    - thread_id
    - to_email
    - subject
    - sent_at
    - snippet (preview)
    """
    # TODO: Implement Gmail API call via Zo tools
    # For now, return empty list (stub)
    return []

def is_spam_response(subject: str, snippet: str) -> bool:
    """
    Detect spam/unwanted responses.
    
    Rules:
    - Subject contains: "unsubscribe", "out of office", "autoreply", "delivery failure"
    - Snippet contains spam trigger phrases
    
    Returns True if spam, False if legitimate
    """
    spam_keywords = [
        'unsubscribe', 'out of office', 'autoreply', 
        'automatic reply', 'delivery failure', 'mailer-daemon',
        'do not reply', 'noreply', 'delivery status notification'
    ]
    
    text = f"{subject} {snippet}".lower()
    return any(keyword in text for keyword in spam_keywords)

def process_sent_email(email: Dict) -> Optional[int]:
    """
    Process single sent email.
    
    Returns profile_id if processed, None if skipped
    """
    to_email = email['to_email']
    subject = email['subject']
    snippet = email['snippet']
    
    # 1. Spam check
    if is_spam_response(subject, snippet):
        return None
    
    # 2. Check if profile exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM profiles WHERE email = ?", (to_email,))
    row = cursor.fetchone()
    
    if row:
        # Profile exists, skip
        conn.close()
        return None
    
    # 3. Create profile
    name = to_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
    profile_id = get_or_create_profile(to_email, name, source='gmail_reply')
    
    # 4. Schedule low-priority enrichment (7 days out)
    scheduled_for = (datetime.now() + timedelta(days=7)).isoformat()
    metadata = json.dumps({
        'thread_id': email['thread_id'],
        'subject': subject,
        'sent_at': email['sent_at']
    })
    
    schedule_enrichment_job(
        profile_id=profile_id,
        scheduled_for=scheduled_for,
        checkpoint='checkpoint_1',
        priority=25,  # Low priority
        trigger_source='gmail_reply',
        trigger_metadata=metadata
    )
    
    conn.close()
    return profile_id

def main():
    """Main tracker loop"""
    # Get last run timestamp from state file
    state_file = '/home/workspace/N5/data/gmail_tracker_state.json'
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            last_run = state.get('last_run')
    except FileNotFoundError:
        # First run: start from 7 days ago
        last_run = (datetime.now() - timedelta(days=7)).isoformat()
    
    # Fetch sent emails
    emails = get_sent_emails_since(last_run)
    
    processed_count = 0
    for email in emails:
        result = process_sent_email(email)
        if result:
            processed_count += 1
    
    # Update state
    with open(state_file, 'w') as f:
        json.dump({
            'last_run': datetime.now().isoformat(),
            'processed_count': processed_count
        }, f)
    
    print(f"Processed {processed_count} new contacts from {len(emails)} sent emails")

if __name__ == '__main__':
    main()
```

### Step 2: Scheduled Task (5 min)

**Register as recurring task:**

```python
# Use create_scheduled_task via Zo
# Instruction: "Run Gmail sent items tracker for CRM enrichment"
# RRULE: "FREQ=DAILY;BYHOUR=8;BYMINUTE=0"  # Daily at 8 AM
# Command: python3 /home/workspace/N5/scripts/crm_gmail_tracker.py
```

### Step 3: Spam Filter Enhancement (5 min)

**Optional:** Add machine learning-based spam detection if needed

### Step 4: Testing (5 min)

```bash
# Test spam detection
python3 -c "
from crm_gmail_tracker import is_spam_response
assert is_spam_response('Out of Office', '') == True
assert is_spam_response('Re: Meeting next week', 'Looking forward to it') == False
print('✓ Spam filter working')
"

# Test profile creation
python3 /home/workspace/N5/scripts/crm_gmail_tracker.py

# Check results
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT COUNT(*) FROM profiles WHERE source='gmail_reply';"
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT COUNT(*) FROM enrichment_queue WHERE trigger_source='gmail_reply';"
```

---

## Success Criteria

1. ✅ Gmail tracker script created and executable
2. ✅ Spam filter working (excludes auto-replies, unsubscribes, etc.)
3. ✅ Profile creation working (new contacts from sent emails)
4. ✅ Low-priority enrichment jobs queued (7 days out, priority 25)
5. ✅ Scheduled task registered (daily at 8 AM)

---

## Validation Commands

```bash
# Test imports
python3 -c "from crm_gmail_tracker import is_spam_response, process_sent_email; print('✓ Imports successful')"

# Run tracker (dry-run mode)
python3 /home/workspace/N5/scripts/crm_gmail_tracker.py

# Verify queue
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT COUNT(*), trigger_source, priority FROM enrichment_queue GROUP BY trigger_source, priority;"

# Check scheduled task
# Use list_scheduled_tasks to verify registration
```

---

## Deliverables

**Report back to Orchestrator:**

1. Script created and tested
2. Spam filter validation results
3. Profile creation count (if any test emails processed)
4. Scheduled task ID
5. Any issues or blockers

**Ready for Worker 7:** After Workers 5 & 6 both complete, Worker 7 (integration testing) can begin.

---

## Notes

**Gmail API Integration:**
- Use `use_app_gmail` with `gmail-list-messages` action
- Filter by `in:sent` and `after:{timestamp}`
- Extract recipient emails from `To:` field
- Worker can use Zo CLI or internal API

**Priority Levels:**
- Calendar (3 days before): Priority 75
- Calendar (morning-of): Priority 100
- Gmail replies: Priority 25 (lowest, 7 days out)

**Architecture Context:**
- `file 'N5/builds/crm-v3-unified/crm-v3-design.md'` - Full CRM V3 architecture
- `file 'N5/scripts/crm_calendar_helpers.py'` - Shared helper functions
- `file 'N5/data/crm_v3.db'` - Database

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-18 04:20 ET  
**Status:** Ready to Execute  
**Parallel Worker:** W6 (CLI Interface)


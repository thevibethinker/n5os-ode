# CRM Gmail Tracker Agent Instruction

**Purpose:** Daily automated task to monitor Gmail sent folder and create CRM profiles for new contacts

**Scheduled:** Daily at 8:00 AM ET

---

## Task Execution Steps

### 1. Load State
```bash
STATE_FILE="/home/workspace/N5/data/gmail_tracker_state.json"

# Get last_run timestamp (or default to 7 days ago)
if [ -f "$STATE_FILE" ]; then
    LAST_RUN=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['last_run'])")
else
    LAST_RUN=$(python3 -c "from datetime import datetime, timedelta; print((datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d'))")
fi
```

### 2. Fetch Gmail Sent Emails
Use `use_app_gmail` with `gmail-find-email` action:

```python
# Search query: sent emails after last run
after_date = LAST_RUN  # Format: YYYY/MM/DD
search_query = f"in:sent after:{after_date}"

use_app_gmail(
    tool_name='gmail-find-email',
    configured_props={
        'q': search_query,
        'maxResults': 50,
        'metadataOnly': False
    },
    email='attawar.v@gmail.com'
)
```

### 3. Process Messages
Save Gmail response to temp file, then run tracker script:

```bash
# Save Gmail response
echo "$GMAIL_RESPONSE" > /tmp/gmail_sent_messages.json

# Run tracker with Gmail data
python3 /home/workspace/N5/scripts/crm_gmail_tracker.py --gmail-data /tmp/gmail_sent_messages.json
```

### 4. Report Results
Extract and report:
- Number of emails checked
- New profiles created  
- Enrichment jobs queued
- Any errors encountered

---

## Expected Behavior

**Spam Filtering:**
- Skip emails with "out of office", "autoreply", "unsubscribe" in subject/snippet
- Skip noreply@* addresses
- Skip mailer-daemon, postmaster addresses

**Profile Creation:**
- Only create profiles for emails NOT already in CRM
- Generate name from email prefix (e.g., john.doe@company.com → "John Doe")
- Set source='gmail_reply'
- Create stub YAML file in N5/crm_v3/profiles/

**Enrichment Scheduling:**
- Schedule 7 days out (low priority)
- Priority: 25 (lowest in system)
- Checkpoint: checkpoint_1
- Metadata: thread_id, subject, sent_at

---

## Error Handling

- Gmail API failures → Log error, continue (don't crash)
- Database errors → Log error, skip profile, continue
- Invalid email formats → Skip, log warning

---

## Success Criteria

✓ Runs daily without manual intervention
✓ Processes sent emails since last run
✓ Creates profiles for new contacts only
✓ Queues low-priority enrichment jobs
✓ Logs all activity to /home/workspace/N5/logs/gmail_tracker.log

---

## Monitoring

Check logs:
```bash
tail -f /home/workspace/N5/logs/gmail_tracker.log
```

Check state:
```bash
cat /home/workspace/N5/data/gmail_tracker_state.json
```

Query results:
```bash
sqlite3 /home/workspace/N5/data/crm_v3.db "
SELECT COUNT(*) FROM profiles WHERE source='gmail_reply';
"

sqlite3 /home/workspace/N5/data/crm_v3.db "
SELECT COUNT(*) FROM enrichment_queue 
WHERE trigger_source='gmail_reply' AND status='queued';
"
```


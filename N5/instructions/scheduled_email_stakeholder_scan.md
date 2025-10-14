# Scheduled Email Stakeholder Scan

**Purpose:** Discover new stakeholders from meeting-related emails in Gmail  
**Frequency:** Every 20 minutes during active hours (8 AM - 10 PM ET)  
**Execution:** Automated via scheduled task

---

## Instructions for Zo Agent

Execute the following steps to scan Gmail for new stakeholders:

### Step 1: Load Scanner State & Context

```python
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from background_email_scanner import (
    load_state,
    save_state,
    load_existing_stakeholders,
    build_gmail_query,
    parse_email_for_participants,
    queue_stakeholder_for_creation,
    log
)

# Load current state
state = load_state()
existing = load_existing_stakeholders()
query = build_gmail_query(state['last_scan_time'])

print(f"Gmail Query: {query}")
print(f"Existing Stakeholders: {len(existing)}")
```

### Step 2: Fetch Emails from Gmail

Use `use_app_gmail` to fetch meeting-related emails:

```python
# Call Gmail API
gmail_result = use_app_gmail('gmail-find-email', {
    'q': query,
    'maxResults': 50,
    'metadataOnly': False
})

emails = gmail_result.get('messages', [])
print(f"Retrieved {len(emails)} emails")
```

### Step 3: Process & Queue Discoveries

```python
from datetime import datetime, timezone

discovered = []
processed_ids = set(state.get('processed_message_ids', []))

for email in emails:
    if email['id'] in processed_ids:
        continue
    
    participants = parse_email_for_participants(email)
    
    for p in participants:
        if p['email'] not in existing:
            queue_stakeholder_for_creation(p)
            discovered.append(p)
            existing.add(p['email'])
    
    processed_ids.add(email['id'])

# Update state
state['last_scan_time'] = datetime.now(timezone.utc).isoformat()
state['processed_message_ids'] = list(processed_ids)[-1000:]
state['discovered_count'] += len(discovered)
save_state(state)

print(f"✅ Discovered {len(discovered)} new stakeholders")
for p in discovered:
    print(f"  - {p['email']} ({p.get('name', 'unknown')}) @ {p.get('organization', 'unknown')}")
```

---

## Alternative: Direct Python Execution

If the agent environment supports it, run:

```bash
cd /home/workspace/N5/scripts
python3 scheduled_email_scan.py
```

*This requires Gmail API access to be available in the execution context.*

---

## Monitoring

**Log File:** `N5/logs/email_scanner.log`  
**State File:** `N5/.state/email_scanner_state.json`  
**Queue Location:** `Knowledge/crm/profiles/.pending_updates/`

---

**Last Updated:** 2025-10-13  
**Related:** `file 'N5/scripts/background_email_scanner.py'`

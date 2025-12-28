# Worker 4: Calendar Webhook Integration

**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Task ID:** W4-CALENDAR-WEBHOOK  
**Estimated Time:** 60 minutes  
**Dependencies:** Worker 1 ✅ Complete, Worker 2 ✅ Complete, Worker 3 ✅ Complete

---

## Mission

Build Google Calendar webhook integration that triggers profile enrichment 3 days before meetings and generates morning-of meeting briefs, with automatic webhook renewal and health monitoring.

---

## Context

**Workers 1-3 Status:** ✅ Complete (64 min actual, under 135 min budget)

This worker creates the **calendar-first trigger** that shifts CRM from reactive to proactive. Instead of post-meeting cleanup, we now prep BEFORE meetings with enriched profiles.

**Architecture Reference:** `file 'N5/builds/crm-v3-unified/crm-v3-design.md'` (Sections: Calendar-First Trigger Pattern, Enrichment Timeline)

---

## Requirements

### 1. Google Calendar Webhook Setup

**Goal:** Receive push notifications when calendar events are created/updated/deleted

**Implementation:**
```python
# N5/scripts/crm_calendar_webhook_setup.py

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def setup_calendar_webhook():
    """
    Register webhook with Google Calendar Watch API.
    Receives notifications at: https://va.zo.computer/webhooks/calendar
    """
    creds = load_google_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # Setup push notification channel
    request_body = {
        'id': generate_unique_channel_id(),  # UUID
        'type': 'web_hook',
        'address': 'https://va.zo.computer/webhooks/calendar',
        'expiration': calculate_expiration_ms()  # Max 7 days
    }
    
    response = service.events().watch(
        calendarId='primary',
        body=request_body
    ).execute()
    
    # Store webhook metadata
    store_webhook_metadata(response)
    
    return response
```

**Deliverables:**
- `crm_calendar_webhook_setup.py` - Initial setup
- Store channel ID + expiration in database or config file

---

### 2. Webhook Endpoint Handler

**Goal:** Receive and process Google Calendar notifications

**Implementation:**
```python
# N5/scripts/crm_calendar_webhook_handler.py

async def handle_calendar_notification(notification):
    """
    Process incoming Google Calendar webhook notification.
    
    Steps:
    1. Validate notification signature
    2. Fetch updated event details from Calendar API
    3. Extract attendees with emails
    4. Create/update calendar_events table
    5. Queue enrichment jobs for new/updated attendees
    """
    
    # Validate webhook
    if not validate_google_webhook(notification):
        return {'status': 'invalid'}
    
    # Fetch event details
    event_id = extract_event_id(notification)
    event = fetch_calendar_event(event_id)
    
    # Process event
    if event['status'] == 'cancelled':
        handle_event_cancellation(event)
    else:
        process_event_attendees(event)
    
    return {'status': 'processed'}


def process_event_attendees(event):
    """
    Extract attendees and create enrichment jobs.
    
    Timeline:
    - Checkpoint 1 (3 days before): priority 75, full enrichment
    - Checkpoint 2 (morning-of @ 7 AM): priority 100, delta + brief
    """
    meeting_time = parse_event_start_time(event)
    attendees = extract_attendees_with_emails(event)
    
    for attendee in attendees:
        # Get or create profile
        profile_id = get_or_create_profile(
            email=attendee['email'],
            name=attendee.get('displayName', 'Unknown'),
            source='calendar_webhook'
        )
        
        # Queue checkpoint 1 (3 days before)
        schedule_enrichment_job(
            profile_id=profile_id,
            scheduled_for=meeting_time - timedelta(days=3),
            checkpoint='checkpoint_1',
            priority=75,
            trigger_source='calendar_webhook',
            trigger_metadata={'event_id': event['id']}
        )
        
        # Queue checkpoint 2 (morning-of @ 7 AM)
        morning_of = meeting_time.replace(hour=7, minute=0)
        if morning_of < meeting_time:  # Only if meeting is after 7 AM
            schedule_enrichment_job(
                profile_id=profile_id,
                scheduled_for=morning_of,
                checkpoint='checkpoint_2',
                priority=100,
                trigger_source='calendar_webhook',
                trigger_metadata={'event_id': event['id']}
            )
```

**Deliverables:**
- `crm_calendar_webhook_handler.py` - Notification processor
- Register endpoint as user service (HTTP)

---

### 3. Webhook Renewal Worker

**Goal:** Auto-renew webhook before 7-day expiration

**Implementation:**
```python
# N5/scripts/crm_calendar_webhook_renewal.py

import asyncio
from datetime import datetime, timedelta

async def webhook_renewal_worker():
    """
    Background worker that renews calendar webhook before expiration.
    Runs daily, checks if renewal needed (< 2 days remaining).
    """
    while True:
        try:
            webhook_data = load_webhook_metadata()
            expiration = datetime.fromtimestamp(
                webhook_data['expiration'] / 1000
            )
            
            time_remaining = expiration - datetime.utcnow()
            
            # Renew if < 2 days remaining
            if time_remaining < timedelta(days=2):
                logger.info("Renewing calendar webhook...")
                new_webhook = setup_calendar_webhook()
                logger.info(f"Webhook renewed until {new_webhook['expiration']}")
            
            # Check daily
            await asyncio.sleep(86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Webhook renewal failed: {e}")
            send_sms_alert(f"⚠️ Calendar webhook renewal failed: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour
```

**Deliverables:**
- `crm_calendar_webhook_renewal.py` - Auto-renewal worker
- Register as user service (background process)

---

### 4. Health Monitoring

**Goal:** Detect webhook failures and alert V via SMS

**Implementation:**
```python
# N5/scripts/crm_calendar_health_monitor.py

async def health_monitor():
    """
    Monitor webhook health and alert on failures.
    
    Checks:
    1. Webhook expiration status
    2. Last notification received time
    3. Event processing errors
    """
    while True:
        try:
            # Check 1: Webhook expiration
            webhook_data = load_webhook_metadata()
            expiration = datetime.fromtimestamp(
                webhook_data['expiration'] / 1000
            )
            
            if expiration < datetime.utcnow():
                send_sms_alert("🚨 Calendar webhook EXPIRED!")
            
            # Check 2: Last notification (should be < 24 hours for active calendar)
            last_notification = get_last_webhook_notification_time()
            if datetime.utcnow() - last_notification > timedelta(days=1):
                logger.warning("No webhook notifications in 24 hours")
            
            # Check 3: Processing errors
            recent_errors = get_recent_webhook_errors(hours=24)
            if len(recent_errors) > 5:
                send_sms_alert(f"⚠️ {len(recent_errors)} webhook errors in 24h")
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes
```

**Deliverables:**
- `crm_calendar_health_monitor.py` - Health checker
- Register as user service (background process)

---

### 5. Webhook User Service Registration

**Goal:** Deploy webhook endpoint as permanent user service

**Commands:**
```bash
# Register webhook endpoint (HTTP service)
python3 -c "
from zo_tools import register_user_service

register_user_service(
    label='crm-calendar-webhook',
    protocol='http',
    local_port=8765,
    entrypoint='python3 /home/workspace/N5/scripts/crm_calendar_webhook_handler.py',
    workdir='/home/workspace',
    env_vars={'PYTHONUNBUFFERED': '1'}
)
"

# Register renewal worker (background service)
python3 -c "
from zo_tools import register_user_service

register_user_service(
    label='crm-webhook-renewal',
    protocol='tcp',
    local_port=8766,  # Internal monitoring port
    entrypoint='python3 /home/workspace/N5/scripts/crm_calendar_webhook_renewal.py',
    workdir='/home/workspace',
    env_vars={'PYTHONUNBUFFERED': '1'}
)
"

# Register health monitor (background service)
python3 -c "
from zo_tools import register_user_service

register_user_service(
    label='crm-webhook-health',
    protocol='tcp',
    local_port=8767,
    entrypoint='python3 /home/workspace/N5/scripts/crm_calendar_health_monitor.py',
    workdir='/home/workspace',
    env_vars={'PYTHONUNBUFFERED': '1'}
)
"
```

---

## Validation Tests

### Test 1: Webhook Setup
```bash
python3 /home/workspace/N5/scripts/crm_calendar_webhook_setup.py
# Expected: Channel ID + expiration returned, stored in config
```

### Test 2: Manual Notification Simulation
```bash
# Simulate incoming webhook notification
curl -X POST https://va.zo.computer/webhooks/calendar \
  -H "Content-Type: application/json" \
  -d '{"resourceId": "test123", "resourceUri": "..."}'

# Check logs for processing
tail -f /dev/shm/crm-calendar-webhook.log
```

### Test 3: Event Processing
```bash
# Create test calendar event with attendee
# Verify:
# 1. Profile created in database
# 2. Two enrichment jobs queued (checkpoint_1, checkpoint_2)
sqlite3 /home/workspace/N5/data/crm_v3.db "SELECT * FROM enrichment_queue WHERE trigger_source='calendar_webhook';"
```

### Test 4: Renewal Worker
```bash
# Manually trigger renewal
python3 /home/workspace/N5/scripts/crm_calendar_webhook_renewal.py --force-renew

# Verify new expiration timestamp
```

### Test 5: Health Monitor
```bash
# Check health monitor logs
tail -f /dev/shm/crm-webhook-health.log

# Verify SMS alerts work (force an error condition)
```

---

## Success Criteria

✅ **Setup Complete:**
- [ ] Webhook registered with Google Calendar
- [ ] Channel ID + expiration stored
- [ ] Endpoint deployed as user service

✅ **Event Processing:**
- [ ] Receives webhook notifications
- [ ] Extracts attendees correctly
- [ ] Creates profiles for new attendees
- [ ] Queues enrichment jobs (2 checkpoints)

✅ **Maintenance:**
- [ ] Auto-renewal worker running
- [ ] Health monitor active
- [ ] SMS alerts configured

✅ **Testing:**
- [ ] Manual notification test passes
- [ ] Real calendar event test passes
- [ ] Renewal logic verified
- [ ] Health checks working

---

## Edge Cases to Handle

1. **Weekend/Holiday Meetings:** Checkpoint 1 (3 days before) might land on Friday for Monday meetings
2. **Early Morning Meetings:** Meetings before 7 AM should use day-before checkpoint 2
3. **Event Updates:** Handle time changes (reschedule enrichment jobs)
4. **Event Cancellations:** Cancel queued enrichment jobs
5. **Multiple Calendars:** Currently only watches 'primary', may need extension

---

## Configuration File

Create `N5/config/calendar_webhook.yaml`:
```yaml
webhook:
  endpoint: "https://va.zo.computer/webhooks/calendar"
  channel_id: null  # Set by setup script
  expiration_ms: null  # Set by setup script
  resource_id: null  # Set by setup script

enrichment:
  checkpoint_1_days_before: 3
  checkpoint_1_priority: 75
  checkpoint_2_hour: 7  # 7 AM
  checkpoint_2_priority: 100

renewal:
  check_interval_hours: 24
  renew_threshold_days: 2

health:
  check_interval_hours: 1
  alert_on_errors_count: 5
  alert_on_no_notifications_hours: 24
```

---

## Handoff Instructions

**Report back with:**
1. All deliverables created (file paths)
2. User services registered (service IDs)
3. Webhook channel ID + expiration
4. Test execution results
5. Any issues or blockers encountered

**Ready for Worker 5:** After validation passes, Workers 5 & 6 can run in parallel.

---

**Orchestrator Contact:** con_RxzhtBdWYFsbQueb  
**Created:** 2025-11-18 03:10 ET  
**Status:** Ready to Execute  
**Workers 1-3 Validation:** ✅ Complete (42% progress)


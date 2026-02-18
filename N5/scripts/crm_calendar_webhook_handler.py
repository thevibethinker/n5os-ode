#!/usr/bin/env python3
"""
CRM Calendar Webhook Handler

HTTP endpoint that receives Google Calendar push notifications and processes them.

Architecture:
- Runs as user service (HTTP) on port 8778
- Receives POST requests from Google Calendar
- Validates webhook authenticity (resourceId verification)
- Fetches updated event details from Calendar API
- Extracts attendees and queues enrichment jobs
- Updates calendar_events table with webhook sync state

Endpoint:
    POST https://va.zo.computer/webhooks/calendar
    
Google Push Notification Format:
    Headers:
      - X-Goog-Channel-ID: Channel identifier
      - X-Goog-Message-Number: Message sequence
      - X-Goog-Resource-ID: Resource identifier
      - X-Goog-Resource-State: sync | exists | not_exists
      - X-Goog-Resource-URI: Resource URL
      
    Body: "" (empty for sync notifications, contains resource for other states)
"""

import json
import sys
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Add scripts path for imports
sys.path.append('/home/workspace/N5/scripts')

# Try importing required modules
try:
    from aiohttp import web, ClientSession
    from aiohttp.web_runner import AppRunner, TCPSite
except ImportError:
    print("Error: aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)

try:
    from crm_calendar_helpers import (
        load_google_credentials,
        load_config,
        get_or_create_profile,
        schedule_enrichment_job,
        extract_event_id_from_uri,
        setup_logging,
        send_sms_alert
    )
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    sys.exit(1)

# Google Calendar API configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']

# Event status mapping
EVENT_STATUS_MAP = {
    'confirmed': 'active',
    'tentative': 'tentative',
    'cancelled': 'cancelled'
}

# Application state
app_state = {
    'service': None,
    'config': None,
    'logger': None,
    'valid_resource_ids': set(),
    'last_notification_time': None,
    'notification_count': 0
}


def build_calendar_service():
    """Build Google Calendar API service using configured credentials."""
    try:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as import_err:
            raise RuntimeError(
                "google-api-python-client not installed. "
                "Run: pip install google-api-python-client"
            ) from import_err

        service_account_info = load_google_credentials()
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)
        app_state['logger'].info("✓ Calendar service built successfully")
        return service
    except Exception as e:
        app_state['logger'].error(f"Failed to build Calendar service: {e}")
        raise


def validate_webhook_headers(headers):
    """
    Validate webhook notification headers from Google.
    
    Google Calendar push notifications include several headers that help
    validate authenticity. We primarily verify the resource ID matches
    what we expect for this channel.
    
    Args:
        headers (dict): HTTP request headers
        
    Returns:
        tuple: (is_valid, error_message, metadata)
    """
    required_headers = [
        'X-Goog-Channel-ID',
        'X-Goog-Message-Number',
        'X-Goog-Resource-ID',
        'X-Goog-Resource-State',
        'X-Goog-Resource-URI'
    ]
    
    # Check all required headers present
    missing = [h for h in required_headers if h not in headers]
    if missing:
        return False, f"Missing required headers: {', '.join(missing)}", None
    
    # Extract metadata
    metadata = {
        'channel_id': headers['X-Goog-Channel-ID'],
        'message_number': headers['X-Goog-Message-Number'],
        'resource_id': headers['X-Goog-Resource-ID'],
        'resource_state': headers['X-Goog-Resource-State'],
        'resource_uri': headers['X-Goog-Resource-URI']
    }
    
    # For sync messages, body is empty and we don't validate resource_id yet
    if metadata['resource_state'] == 'sync':
        return True, None, metadata
    
    # Verify resource_id matches expected webhook
    if metadata['resource_id'] not in app_state['valid_resource_ids']:
        # Try to load from database if not in memory
        from crm_calendar_helpers import load_webhook_resource_id
        expected_resource_id = load_webhook_resource_id()
        
        if expected_resource_id and metadata['resource_id'] == expected_resource_id:
            # Cache for future validations
            app_state['valid_resource_ids'].add(expected_resource_id)
            return True, None, metadata
        elif not expected_resource_id:
            # First webhook, accept it
            app_state['valid_resource_ids'].add(metadata['resource_id'])
            return True, None, metadata
        else:
            return False, f"Invalid resource ID: {metadata['resource_id']}", metadata
    
    return True, None, metadata


def fetch_calendar_event(service, event_id):
    """
    Fetch full event details from Google Calendar API.
    
    Args:
        service: Google Calendar API service
        event_id (str): Calendar event ID
        
    Returns:
        dict: Event details or None if not found
    """
    try:
        app_state['logger'].info(f"Fetching event details: {event_id}")
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        app_state['logger'].info(f"✓ Event fetched: {event.get('summary', 'Untitled')}")
        return event
        
    except Exception as e:
        app_state['logger'].error(f"Failed to fetch event {event_id}: {e}")
        return None


def extract_attendees_from_event(event):
    """
    Extract attendee information from calendar event.
    
    Args:
        event (dict): Google Calendar event object
        
    Returns:
        list: Attendees with email and display name
    """
    attendees = []
    
    # Get event creator
    if 'creator' in event and 'email' in event['creator']:
        creator = event['creator']
        attendees.append({
            'email': creator['email'],
            'displayName': creator.get('displayName', creator['email'].split('@')[0]),
            'responseStatus': 'accepted',
            'is_organizer': True
        })
    
    # Get attendees list
    if 'attendees' in event:
        for attendee in event['attendees']:
            if 'email' in attendee:
                # Skip the organizer if already added
                if any(a['email'] == attendee['email'] for a in attendees):
                    continue
                    
                attendees.append({
                    'email': attendee['email'],
                    'displayName': attendee.get('displayName', attendee['email'].split('@')[0]),
                    'responseStatus': attendee.get('responseStatus', 'needsAction'),
                    'is_organizer': False
                })
    
    # Filter out declined attendees
    attendees = [a for a in attendees if a['responseStatus'] != 'declined']
    
    app_state['logger'].info(f"✓ Extracted {len(attendees)} attendee(s) from event")
    return attendees


def parse_event_times(event):
    """
    Parse start and end times from Google Calendar event.
    
    Handles both date-time (specific times) and date (all-day events) formats.
    
    Args:
        event (dict): Google Calendar event object
        
    Returns:
        tuple: (start_datetime, end_datetime, is_all_day)
    """
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Handle date-time (specific time)
    if 'dateTime' in start:
        from dateutil.parser import parse
        
        start_dt = parse(start['dateTime'])
        end_dt = parse(end['dateTime'])
        is_all_day = False
    
    # Handle date (all-day event)
    elif 'date' in start:
        from datetime import datetime
        
        start_dt = datetime.strptime(start['date'], '%Y-%m-%d')
        end_dt = datetime.strptime(end['date'], '%Y-%m-%d')
        is_all_day = True
    else:
        raise ValueError("Event has no start time")
    
    return start_dt, end_dt, is_all_day


def store_calendar_event(event, attendees, webhook_received_at):
    """
    Store or update calendar event in canonical n5_core schema.

    Writes:
    - calendar_events (id, google_event_id, title, start_time, end_time, ...)
    - event_attendees (event_id, person_id, email, response_status, is_organizer)
    """
    try:
        start_dt, end_dt, _ = parse_event_times(event)
        event_id = event['id']
        event_title = event.get('summary', 'Untitled Event')

        with sqlite3.connect('/home/workspace/N5/data/n5_core.db') as conn:
            cursor = conn.cursor()

            # Upsert event in canonical schema
            cursor.execute(
                """
                INSERT INTO calendar_events
                    (id, google_event_id, title, start_time, end_time, location, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    google_event_id=excluded.google_event_id,
                    title=excluded.title,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    location=excluded.location,
                    description=excluded.description
                """,
                (
                    event_id,
                    event_id,
                    event_title,
                    start_dt.isoformat(),
                    end_dt.isoformat(),
                    event.get('location'),
                    event.get('description'),
                ),
            )

            # Replace attendee links for this event
            cursor.execute("DELETE FROM event_attendees WHERE event_id = ?", (event_id,))
            for attendee in attendees:
                email = attendee.get('email')
                if not email:
                    continue
                display_name = attendee.get('displayName', email.split('@')[0])
                person_id = get_or_create_profile(email=email, name=display_name, source='calendar_webhook')
                cursor.execute(
                    """
                    INSERT INTO event_attendees (event_id, person_id, email, response_status, is_organizer)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        person_id,
                        email.strip().lower(),
                        attendee.get('responseStatus', 'needsAction'),
                        1 if attendee.get('is_organizer') else 0,
                    ),
                )

            conn.commit()

        app_state['logger'].info(
            f"✓ Synced event {event_id} with {len(attendees)} attendee(s) at {webhook_received_at}"
        )
        return {'action': 'upserted', 'event_id': event_id}

    except Exception as e:
        app_state['logger'].error(f"Failed to store calendar event: {e}")
        raise

def queue_enrichment_jobs(event, attendees):
    """
    Queue enrichment jobs for event attendees.
    
    Creates two checkpoint jobs:
    1. Checkpoint 1: 3 days before meeting (priority 75) - full enrichment
    2. Checkpoint 2: Morning of meeting at 7 AM (priority 100) - delta + brief
    
    Args:
        event (dict): Google Calendar event
        attendees (list): Attendee list with email and name
    """
    try:
        start_dt, end_dt, is_all_day = parse_event_times(event)
        app_state['logger'].info(f"Event starts: {start_dt.isoformat()}")
        
        queued_jobs = []
        
        for attendee in attendees:
            email = attendee['email']
            name = attendee.get('displayName', email.split('@')[0])
            
            app_state['logger'].info(f"Processing attendee: {name} ({email})")
            
            # Get or create profile
            profile_id = get_or_create_profile(
                email=email,
                name=name,
                source='calendar_webhook'
            )
            
            if not profile_id:
                app_state['logger'].warning(f"Could not get/create profile for {email}")
                continue
            
            # Check if attendee is declining or tentative
            response_status = attendee.get('responseStatus', 'needsAction')
            if response_status == 'declined':
                app_state['logger'].info(f"Skipping {email} - response status: {response_status}")
                continue
            
            # Queue Checkpoint 1: 3 days before meeting
            checkpoint_1_time = start_dt - timedelta(days=3)
            
            # Skip if meeting is within 3 days
            if checkpoint_1_time <= datetime.utcnow():
                app_state['logger'].info(f"Meeting within 3 days, skipping checkpoint 1 for {email}")
            else:
                job_1_id = schedule_enrichment_job(
                    profile_id=profile_id,
                    scheduled_for=checkpoint_1_time.isoformat(),
                    checkpoint='checkpoint_1',
                    priority=75,
                    trigger_source='calendar_webhook',
                    trigger_metadata={
                        'event_id': event['id'],
                        'event_summary': event.get('summary', 'Untitled'),
                        'event_start': start_dt.isoformat(),
                        'attendee_email': email,
                        'checkpoint': 1
                    }
                )
                
                if job_1_id:
                    queued_jobs.append({
                        'profile_id': profile_id,
                        'email': email,
                        'checkpoint': 1,
                        'scheduled_for': checkpoint_1_time.isoformat(),
                        'job_id': job_1_id
                    })
                    app_state['logger'].info(f"✓ Queued checkpoint 1 job for {email}")
            
            # Queue Checkpoint 2: Morning of meeting (7 AM)
            # Calculate morning of (meeting day, 7 AM)
            morning_of = start_dt.replace(hour=7, minute=0, second=0, microsecond=0)
            
            # If meeting is before 7 AM, use previous day 7 AM
            if start_dt.hour < 7:
                morning_of = (start_dt - timedelta(days=1)).replace(
                    hour=7, minute=0, second=0, microsecond=0
                )
            
            # Only queue if morning_of is before meeting time
            if morning_of < start_dt:
                job_2_id = schedule_enrichment_job(
                    profile_id=profile_id,
                    scheduled_for=morning_of.isoformat(),
                    checkpoint='checkpoint_2',
                    priority=100,
                    trigger_source='calendar_webhook',
                    trigger_metadata={
                        'event_id': event['id'],
                        'event_summary': event.get('summary', 'Untitled'),
                        'event_start': start_dt.isoformat(),
                        'attendee_email': email,
                        'checkpoint': 2
                    }
                )
                
                if job_2_id:
                    queued_jobs.append({
                        'profile_id': profile_id,
                        'email': email,
                        'checkpoint': 2,
                        'scheduled_for': morning_of.isoformat(),
                        'job_id': job_2_id
                    })
                    app_state['logger'].info(f"✓ Queued checkpoint 2 job for {email}")
            else:
                app_state['logger'].info(f"Meeting before 7 AM, using day-before checkpoint for {email}")
        
        app_state['logger'].info(f"✓ Total jobs queued: {len(queued_jobs)}")
        return queued_jobs
        
    except Exception as e:
        app_state['logger'].error(f"Failed to queue enrichment jobs: {e}")
        raise


def update_sync_state(resource_id):
    """Update application state with sync information"""
    app_state['last_notification_time'] = datetime.utcnow().isoformat()
    app_state['notification_count'] += 1
    app_state['valid_resource_ids'].add(resource_id)


async def handle_webhook_notification(request):
    """
    Handle incoming Google Calendar webhook notification.
    
    This is the main endpoint that receives push notifications from Google.
    """
    webhook_received_at = datetime.utcnow().isoformat()
    
    try:
        # Extract and validate headers
        headers = dict(request.headers)
        is_valid, error_msg, metadata = validate_webhook_headers(headers)
        
        if not is_valid:
            app_state['logger'].warning(f"Invalid webhook: {error_msg}")
            return web.json_response(
                {'status': 'invalid', 'error': error_msg},
                status=400
            )
        
        # Log notification
        app_state['logger'].info(
            f"Webhook received - State: {metadata['resource_state']}, "
            f"Channel: {metadata['channel_id'][:8]}..., "
            f"Message #: {metadata['message_number']}"
        )
        
        # Handle sync notification (initial setup)
        if metadata['resource_state'] == 'sync':
            app_state['logger'].info("Processing sync notification")
            update_sync_state(metadata['resource_id'])
            
            return web.json_response({
                'status': 'sync_acknowledged',
                'channel_id': metadata['channel_id']
            })
        
        # Handle event notification
        if metadata['resource_state'] in ['exists', 'updated']:
            # Extract event ID from resource URI
            event_id = extract_event_id_from_uri(metadata['resource_uri'])
            
            if not event_id:
                app_state['logger'].error(f"Could not extract event ID from: {metadata['resource_uri']}")
                return web.json_response(
                    {'status': 'error', 'message': 'Invalid event ID'},
                    status=400
                )
            
            # Fetch event details from Google Calendar
            event = fetch_calendar_event(app_state['service'], event_id)
            
            if not event:
                return web.json_response(
                    {'status': 'error', 'message': 'Event not found'},
                    status=404
                )
            
            # Extract attendees
            attendees = extract_attendees_from_event(event)
            
            if not attendees:
                app_state['logger'].info(f"No attendees found for event: {event.get('summary', 'Untitled')}")
                return web.json_response({
                    'status': 'processed',
                    'event_id': event_id,
                    'message': 'No attendees to process'
                })
            
            # Store or update calendar event in database
            sync_result = store_calendar_event(event, attendees, webhook_received_at)
            
            # Queue enrichment jobs for attendees
            jobs_queued = queue_enrichment_jobs(event, attendees)
            
            # Update sync state
            update_sync_state(metadata['resource_id'])
            
            return web.json_response({
                'status': 'processed',
                'event_id': event_id,
                'event_action': sync_result['action'],
                'attendees_processed': len(attendees),
                'jobs_queued': len(jobs_queued)
            })
        
        # Handle event deletion
        if metadata['resource_state'] == 'not_exists':
            event_id = extract_event_id_from_uri(metadata['resource_uri'])
            app_state['logger'].info(f"Event deleted: {event_id}")
            
            # TODO: Cancel queued enrichment jobs for this event
            # This would require tracking event_id in enrichment_queue
            
            update_sync_state(metadata['resource_id'])
            
            return web.json_response({
                'status': 'processed',
                'event_id': event_id,
                'action': 'deleted'
            })
        
        # Unknown state
        app_state['logger'].warning(f"Unknown resource state: {metadata['resource_state']}")
        return web.json_response({
            'status': 'ignored',
            'resource_state': metadata['resource_state']
        })
        
    except Exception as e:
        app_state['logger'].error(f"Error processing webhook: {e}", exc_info=True)
        
        # Send SMS alert for critical errors after some threshold
        app_state['error_count'] = app_state.get('error_count', 0) + 1
        if app_state['error_count'] > 5:
            send_sms_alert(f"🚨 Webhook handler critical errors: {app_state['error_count']}")
        
        return web.json_response(
            {'status': 'error', 'message': str(e)},
            status=500
        )


async def health_check(request):
    """Simple health check endpoint for monitoring"""
    return web.json_response({
        'status': 'healthy',
        'uptime': getattr(app_state, 'start_time', datetime.utcnow().isoformat()),
        'notification_count': app_state.get('notification_count', 0),
        'last_notification': app_state.get('last_notification_time')
    })


async def get_stats(request):
    """Get handler statistics"""
    return web.json_response({
        'state': {
            'notification_count': app_state.get('notification_count', 0),
            'last_notification_time': app_state.get('last_notification_time'),
            'valid_resource_ids': len(app_state.get('valid_resource_ids', set())),
            'service_available': app_state.get('service') is not None
        }
    })


async def start_background_tasks(app):
    """Initialize background tasks and application state"""
    app_state['start_time'] = datetime.utcnow().isoformat()
    app_state['error_count'] = 0
    app_state['config'] = load_config()
    app_state['logger'] = setup_logging('/dev/shm/crm-calendar-webhook.log')
    app_state['service'] = build_calendar_service()
    app_state['logger'].info("✓ Webhook handler initialized")


async def cleanup_background_tasks(app):
    """Cleanup background tasks on shutdown"""
    if app_state.get('logger'):
        app_state['logger'].info("Shutting down webhook handler")


def create_webhook_app():
    """Create and configure the webhook application"""
    app = web.Application()
    
    # Add routes
    app.router.add_post('/webhooks/calendar', handle_webhook_notification)
    app.router.add_get('/health', health_check)
    app.router.add_get('/stats', get_stats)
    
    # Add startup/cleanup handlers
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    return app


async def main():
    """Main entry point for webhook handler service"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CRM Calendar Webhook Handler')
    parser.add_argument('--port', type=int, default=8778, help='Port to listen on (default: 8778)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Start service
    app = create_webhook_app()
    runner = AppRunner(app)
    await runner.setup()
    
    site = TCPSite(runner, args.host, args.port)
    await site.start()
    
    print(f"=" * 70)
    print(f"CRM Calendar Webhook Handler")
    print(f"=" * 70)
    print(f"Listening on: http://{args.host}:{args.port}")
    print(f"Webhook endpoint: http://{args.host}:{args.port}/webhooks/calendar")
    print(f"Health check: http://{args.host}:{args.port}/health")
    print(f"Stats: http://{args.host}:{args.port}/stats")
    print(f"=" * 70)
    print("Press Ctrl+C to stop")
    print(f"=" * 70)
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWebhook handler stopped")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


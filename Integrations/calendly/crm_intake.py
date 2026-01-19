#!/usr/bin/env python3
"""
CRM Intake from Calendly Booking

When someone books via Calendly:
1. Create or update their CRM profile
2. Queue Gmail enrichment (check for prior contact)
3. Queue general enrichment (Aviato, LinkedIn, etc.)
4. Log the upcoming meeting context

This is the "gatekeeping" function - every Calendly booker gets a CRM profile.
"""

import argparse
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/home/workspace')
sys.path.insert(0, '/home/workspace/N5/scripts')

from N5.lib.paths import CRM_DB
from crm_calendar_helpers import (
    get_or_create_profile,
    schedule_enrichment_job,
    get_db_connection
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


def infer_category(event_type: str) -> str:
    """Infer CRM category from Calendly event type name."""
    event_lower = event_type.lower()
    
    if any(kw in event_lower for kw in ['investor', 'pitch', 'funding', 'raise']):
        return 'INVESTOR'
    elif any(kw in event_lower for kw in ['advisor', 'mentor', 'coaching']):
        return 'ADVISOR'
    elif any(kw in event_lower for kw in ['community', 'event', 'podcast', 'interview']):
        return 'COMMUNITY'
    else:
        return 'NETWORKING'


def add_meeting_context(profile_id: int, event_type: str, scheduled_time: str):
    """Add upcoming meeting context to profile notes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current yaml_path
    cursor.execute("SELECT yaml_path FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return
    
    yaml_path = Path(row[0])
    if not yaml_path.exists():
        return
    
    # Append meeting context
    timestamp = datetime.now().isoformat()
    meeting_note = f"""
## Calendly Booking [{timestamp[:10]}]
- **Event Type:** {event_type}
- **Scheduled:** {scheduled_time}
- **Source:** Calendly webhook
"""
    
    with open(yaml_path, 'a') as f:
        f.write(meeting_note)
    
    logger.info(f"Added meeting context to profile {profile_id}")


def queue_gmail_enrichment(profile_id: int, email: str):
    """Queue Gmail thread search for this contact."""
    # Schedule enrichment job with gmail checkpoint
    schedule_enrichment_job(
        profile_id=profile_id,
        scheduled_for=datetime.now().isoformat(),
        checkpoint='checkpoint_gmail',
        priority=90,  # High priority for upcoming meetings
        trigger_source='calendly_booking'
    )
    logger.info(f"Queued Gmail enrichment for {email}")


def main():
    parser = argparse.ArgumentParser(description='CRM Intake from Calendly Booking')
    parser.add_argument('--email', required=True, help='Invitee email')
    parser.add_argument('--name', required=True, help='Invitee name')
    parser.add_argument('--event-type', default='Meeting', help='Calendly event type name')
    parser.add_argument('--scheduled-time', default='', help='Scheduled meeting time (ISO)')
    
    args = parser.parse_args()
    
    email = args.email.strip().lower()
    name = args.name.strip()
    event_type = args.event_type
    scheduled_time = args.scheduled_time
    
    if not email:
        logger.error("No email provided")
        sys.exit(1)
    
    # Infer category from event type
    category = infer_category(event_type)
    
    # Check if profile exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM profiles WHERE email = ?", (email,))
    existing = cursor.fetchone()
    conn.close()
    
    if existing:
        profile_id = existing[0]
        existing_name = existing[1]
        logger.info(f"Profile exists: {existing_name} (ID: {profile_id})")
        print(f"✓ Existing profile: {existing_name} (ID: {profile_id})")
    else:
        # Create new profile
        profile_id = get_or_create_profile(
            email=email,
            name=name,
            source='calendly_booking'
        )
        
        # Update category
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE profiles SET category = ? WHERE id = ?", (category, profile_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Created profile: {name} (ID: {profile_id}, Category: {category})")
        print(f"✓ Created profile: {name} (ID: {profile_id})")
    
    # Add meeting context to profile
    if scheduled_time:
        add_meeting_context(profile_id, event_type, scheduled_time)
    
    # Queue enrichment (Aviato, LinkedIn, etc.)
    schedule_enrichment_job(
        profile_id=profile_id,
        scheduled_for=datetime.now().isoformat(),
        checkpoint='checkpoint_2',  # Standard enrichment checkpoint
        priority=100,  # High priority
        trigger_source='calendly_booking'
    )
    print(f"✓ Queued enrichment for {email}")
    
    # Queue Gmail enrichment (search for prior threads)
    queue_gmail_enrichment(profile_id, email)
    print(f"✓ Queued Gmail thread search for {email}")
    
    # Log summary
    summary = {
        "action": "calendly_intake",
        "profile_id": profile_id,
        "email": email,
        "name": name,
        "event_type": event_type,
        "category": category,
        "is_new": existing is None,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"Intake complete: {json.dumps(summary)}")
    

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CRM Intake from Calendly Booking

When someone books via Calendly:
1. Create or update their CRM profile in the `people` table
2. Log an interaction in the `interactions` table
3. Optionally queue enrichment via N5's enrichment pipeline

This is the "gatekeeping" function — every Calendly booker gets a CRM record.
"""

import argparse
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/workspace')

from N5.lib.paths import CRM_DB
from N5.lib.db import get_crm_db, crm_transaction

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
    elif any(kw in event_lower for kw in ['careerspan', 'product', 'feedback', 'demo']):
        return 'CUSTOMER'
    else:
        return 'NETWORKING'


def get_or_create_person(email: str, name: str, category: str, source: str = 'calendly') -> int:
    """Look up or create a person in the `people` table. Returns person ID."""
    conn = get_crm_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM people WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row:
        person_id = row[0]
        logger.info(f"Found existing person: {row[1]} (ID: {person_id})")
        return person_id

    with crm_transaction() as tx:
        c = tx.cursor()
        c.execute("SELECT id FROM people WHERE email = ?", (email,))
        if (r := c.fetchone()):
            return r[0]

        today = datetime.now().strftime("%Y-%m-%d")
        slug = name.lower().replace(' ', '-').replace("'", "")
        slug = ''.join(ch for ch in slug if ch.isalnum() or ch == '-')
        md_path = f"CRM/People/{slug}.md"
        full_md_path = Path(f"/home/workspace/{md_path}")
        full_md_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_md_path.exists():
            stub = f"""---
created: {today}
last_edited: {today}
version: 1.0
provenance: calendly_intake
---

# {name}

## Contact
- **Email:** {email}
- **Category:** {category}
- **Source:** Calendly booking

## Notes

*Awaiting enrichment.*
"""
            full_md_path.write_text(stub)
            logger.info(f"Created markdown stub at {md_path}")

        c.execute("""
            INSERT INTO people
            (full_name, email, category, status, priority, source_db, markdown_path,
             first_contact_date, last_contact_date, created_at, updated_at)
            VALUES (?, ?, ?, 'active', 'medium', 'calendly', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (name, email, category, md_path, today, today))

        person_id = c.lastrowid
        logger.info(f"Created person: {name} (ID: {person_id})")
        return person_id


def log_booking_interaction(person_id: int, event_type: str, scheduled_time: str):
    """Record the booking as an interaction in the CRM."""
    with crm_transaction() as tx:
        c = tx.cursor()
        now = datetime.now().isoformat()
        summary = f"Calendly booking: {event_type}"
        if scheduled_time:
            summary += f" (scheduled {scheduled_time})"

        c.execute("""
            INSERT INTO interactions
            (person_id, type, direction, summary, source_ref, occurred_at, created_at)
            VALUES (?, 'meeting_scheduled', 'inbound', ?, 'calendly_webhook', ?, ?)
        """, (person_id, summary, scheduled_time or now, now))

        logger.info(f"Logged booking interaction for person {person_id}")


def main():
    parser = argparse.ArgumentParser(description='CRM Intake from Calendly Booking')
    parser.add_argument('--email', required=True, help='Invitee email')
    parser.add_argument('--name', required=True, help='Invitee name')
    parser.add_argument('--event-type', default='Meeting', help='Calendly event type name')
    parser.add_argument('--scheduled-time', default='', help='Scheduled meeting time (ISO)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without writing')

    args = parser.parse_args()

    email = args.email.strip().lower()
    name = args.name.strip()
    event_type = args.event_type
    scheduled_time = args.scheduled_time

    if not email:
        logger.error("No email provided")
        sys.exit(1)

    category = infer_category(event_type)

    if args.dry_run:
        print(f"[DRY RUN] Would create/find person: {name} <{email}>")
        print(f"[DRY RUN] Category: {category}")
        print(f"[DRY RUN] Would log interaction: {event_type} at {scheduled_time}")
        return

    try:
        person_id = get_or_create_person(email, name, category)
        print(f"✓ Person ready: {name} (ID: {person_id})")

        log_booking_interaction(person_id, event_type, scheduled_time)
        print(f"✓ Interaction logged for {email}")

        summary = {
            "action": "calendly_intake",
            "person_id": person_id,
            "email": email,
            "name": name,
            "event_type": event_type,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Intake complete: {json.dumps(summary)}")

    except Exception as e:
        logger.error(f"CRM intake failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Auto-Create Stakeholder Profiles from Calendar Events

Scans upcoming calendar, detects external stakeholders, creates profiles with email history.
Creates entries in both unified n5_core.db and markdown profiles.

UPDATED 2026-01-19: Now uses unified n5_core.db for all database operations.

Usage:
    python3 auto_create_stakeholder_profiles.py --dry-run
    python3 auto_create_stakeholder_profiles.py --live
    python3 auto_create_stakeholder_profiles.py --meeting-folder <path>
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from unified database paths
from db_paths import get_db_connection, PEOPLE_TABLE, INTERACTIONS_TABLE
from crm_paths import CRM_INDIVIDUALS, MEETINGS_ROOT

WORKSPACE = Path("/home/workspace")
CRM_DIR = CRM_INDIVIDUALS
MEETINGS_INBOX = MEETINGS_ROOT / "Inbox"


def is_external_email(email: str) -> bool:
    """Check if email is external (not Careerspan or V's personal)."""
    if not email:
        return False
    email_lower = email.lower()
    internal_domains = ['careerspan.com', 'careerspan.io', 'howie.ai']
    internal_addresses = ['attawar.v@gmail.com', 'vrijen@']
    
    for domain in internal_domains:
        if domain in email_lower:
            return False
    for addr in internal_addresses:
        if addr in email_lower:
            return False
    return True


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    clean = re.sub(r'[^\w\s-]', '', name.lower())
    return re.sub(r'\s+', '-', clean.strip())


def infer_organization_from_email(email: str) -> str:
    """Infer organization from email domain."""
    if not email or '@' not in email:
        return "[Unknown]"
    domain = email.split('@')[1].lower()
    
    # Skip common personal domains
    personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
    if domain in personal_domains:
        return "[Personal Email]"
    
    # Clean domain to organization name
    org = domain.split('.')[0].title()
    return org


def find_person_by_email(email: str) -> dict | None:
    """Find person in unified database by email."""
    conn = get_db_connection(readonly=True)
    try:
        row = conn.execute(
            f"SELECT id, full_name, email, markdown_path, company FROM {PEOPLE_TABLE} WHERE email = ?",
            (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def find_person_by_name(name: str) -> dict | None:
    """Find person in unified database by name."""
    conn = get_db_connection(readonly=True)
    try:
        row = conn.execute(
            f"SELECT id, full_name, email, markdown_path, company FROM {PEOPLE_TABLE} WHERE LOWER(full_name) = LOWER(?)",
            (name,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_person_in_db(
    name: str,
    email: str = None,
    company: str = None,
    markdown_path: str = None,
    first_contact_date: str = None
) -> int:
    """Create a person record in the unified database.
    
    Returns the new person's ID.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            f"""INSERT INTO {PEOPLE_TABLE} 
               (full_name, email, company, markdown_path, first_contact_date, source_db, status)
               VALUES (?, ?, ?, ?, ?, 'auto_create_stakeholder', 'active')""",
            (name, email, company, markdown_path, first_contact_date)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_person_markdown_path(person_id: int, markdown_path: str):
    """Update the markdown_path for an existing person."""
    conn = get_db_connection()
    try:
        conn.execute(
            f"UPDATE {PEOPLE_TABLE} SET markdown_path = ? WHERE id = ?",
            (markdown_path, person_id)
        )
        conn.commit()
    finally:
        conn.close()


def create_interaction(
    person_id: int,
    interaction_type: str,
    summary: str,
    source_ref: str,
    occurred_at: str
) -> int:
    """Create an interaction record."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            f"""INSERT INTO {INTERACTIONS_TABLE} 
               (person_id, type, summary, source_ref, occurred_at)
               VALUES (?, ?, ?, ?, ?)""",
            (person_id, interaction_type, summary, source_ref, occurred_at)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def create_markdown_profile(
    name: str,
    email: str = None,
    organization: str = None,
    role: str = None,
    meeting_context: str = None
) -> Path:
    """Create a markdown CRM profile.
    
    Returns the path to the created file.
    """
    slug = generate_slug(name)
    profile_path = CRM_DIR / f"{slug}.md"
    
    # Don't overwrite existing profiles
    if profile_path.exists():
        logger.info(f"Profile already exists: {profile_path}")
        return profile_path
    
    # Ensure directory exists
    CRM_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    content = f"""---
created: {today}
last_edited: {today}
version: 1.0
provenance: auto_create_stakeholder_profiles
---

# {name}

**Organization:** {organization or '[Unknown]'}
**Role:** {role or '[To be determined]'}
**Email:** {email or '[Not provided]'}
**Status:** active

## Meeting Context

{meeting_context or '*Auto-created from calendar event.*'}

## Interaction History

*Profile auto-created on {today}.*
"""
    
    profile_path.write_text(content, encoding='utf-8')
    logger.info(f"✓ Created markdown profile: {profile_path}")
    return profile_path


def process_meeting_attendees(meeting_folder: Path, dry_run: bool = False) -> list:
    """Process a meeting folder and create profiles for external attendees.
    
    Returns list of created/found person records.
    """
    manifest_path = meeting_folder / "manifest.json"
    if not manifest_path.exists():
        logger.warning(f"No manifest.json in {meeting_folder}")
        return []
    
    manifest = json.loads(manifest_path.read_text())
    attendees = manifest.get('attendees', [])
    meeting_id = manifest.get('meeting_id', meeting_folder.name)
    meeting_date = manifest.get('start_time', manifest.get('date', datetime.now().isoformat()))
    meeting_title = manifest.get('title', manifest.get('summary', 'Meeting'))
    
    results = []
    
    for attendee in attendees:
        email = attendee.get('email')
        name = attendee.get('displayName') or attendee.get('name', '')
        
        if not email:
            continue
        
        # Skip internal attendees
        if not is_external_email(email):
            logger.debug(f"Skipping internal: {email}")
            continue
        
        # Check if already exists
        existing = find_person_by_email(email)
        if existing:
            logger.info(f"Already exists: {name} ({email}) - ID {existing['id']}")
            results.append(existing)
            continue
        
        # Also check by name
        if name:
            existing = find_person_by_name(name)
            if existing:
                logger.info(f"Found by name: {name} - ID {existing['id']}")
                results.append(existing)
                continue
        
        if dry_run:
            logger.info(f"[DRY-RUN] Would create: {name} ({email})")
            continue
        
        # Create new profile
        organization = infer_organization_from_email(email)
        
        # Create markdown profile
        profile_path = create_markdown_profile(
            name=name or email.split('@')[0],
            email=email,
            organization=organization,
            meeting_context=f"First seen in meeting: {meeting_title}"
        )
        
        # Create DB entry
        markdown_rel_path = str(profile_path.relative_to(WORKSPACE))
        person_id = create_person_in_db(
            name=name or email.split('@')[0],
            email=email,
            company=organization if organization != "[Unknown]" else None,
            markdown_path=markdown_rel_path,
            first_contact_date=meeting_date[:10] if meeting_date else None
        )
        
        # Record the meeting as an interaction
        create_interaction(
            person_id=person_id,
            interaction_type='meeting',
            summary=f"Meeting: {meeting_title}",
            source_ref=str(meeting_folder),
            occurred_at=meeting_date
        )
        
        logger.info(f"✓ Created profile for {name} ({email}) - DB ID: {person_id}")
        results.append({
            'id': person_id,
            'full_name': name,
            'email': email,
            'markdown_path': markdown_rel_path
        })
    
    return results


def scan_calendar_for_new_stakeholders(
    days_ahead: int = 7,
    use_app_google_calendar=None
) -> list:
    """Scan calendar for upcoming meetings with external stakeholders.
    
    Returns list of dicts with stakeholder info for those not already in DB.
    """
    logger.info(f"Scanning calendar for next {days_ahead} days...")
    
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days_ahead)).isoformat()
    
    if use_app_google_calendar is None:
        logger.warning("use_app_google_calendar not provided - this must be called by Zo AI")
        return [{
            '_instruction': 'This function must be called by Zo AI with use_app_google_calendar tool',
            '_steps': [
                'Call use_app_google_calendar(tool_name="google_calendar-list-events", configured_props={...})',
                f'timeMin: {time_min}',
                f'timeMax: {time_max}',
                'calendarId: "primary"',
                'singleEvents: True',
                'orderBy: "startTime"',
                'maxResults: 250',
                'Then pass results to process_calendar_events()'
            ]
        }]
    
    try:
        logger.info(f"Fetching calendar events from {time_min[:19]} to {time_max[:19]}")
        
        events_response = use_app_google_calendar(
            tool_name='google_calendar-list-events',
            configured_props={
                'calendarId': 'primary',
                'timeMin': time_min,
                'timeMax': time_max,
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 250
            }
        )
        
        return process_calendar_events(events_response)
        
    except Exception as e:
        logger.error(f"Failed to fetch calendar: {e}")
        return []


def process_calendar_events(events_response: dict) -> list:
    """Process calendar events and extract new external stakeholders."""
    new_stakeholders = []
    events = events_response.get('items', [])
    
    for event in events:
        attendees = event.get('attendees', [])
        event_id = event.get('id')
        summary = event.get('summary', 'Untitled')
        start = event.get('start', {})
        meeting_date = start.get('dateTime') or start.get('date')
        
        for attendee in attendees:
            email = attendee.get('email')
            name = attendee.get('displayName', email.split('@')[0] if email else 'Unknown')
            
            if not email or not is_external_email(email):
                continue
            
            # Check if already exists
            existing = find_person_by_email(email)
            if existing:
                continue
            
            new_stakeholders.append({
                'email': email,
                'name': name,
                'calendar_event_id': event_id,
                'meeting_date': meeting_date,
                'meeting_summary': summary,
                'attendees': attendees
            })
    
    return new_stakeholders


def main(dry_run: bool = True, meeting_folder: str = None, use_app_google_calendar=None):
    """Main orchestration."""
    logger.info("=== Auto-Create Stakeholder Profiles ===")
    
    if dry_run:
        logger.info("DRY RUN MODE - No files will be created")
    
    if meeting_folder:
        # Process specific meeting folder
        folder = Path(meeting_folder)
        if not folder.exists():
            logger.error(f"Meeting folder not found: {folder}")
            return 1
        
        results = process_meeting_attendees(folder, dry_run=dry_run)
        logger.info(f"\n=== Summary ===")
        logger.info(f"Processed attendees: {len(results)}")
        return 0
    
    # Scan calendar
    new_stakeholders = scan_calendar_for_new_stakeholders(
        days_ahead=7,
        use_app_google_calendar=use_app_google_calendar
    )
    
    if new_stakeholders and '_instruction' in new_stakeholders[0]:
        logger.warning("Cannot execute: Requires Zo runtime with tool access")
        logger.info("Instructions for manual execution:")
        for step in new_stakeholders[0]['_steps']:
            logger.info(f"  {step}")
        return 1
    
    if not new_stakeholders:
        logger.info("✓ No new external stakeholders found in upcoming meetings")
        return 0
    
    logger.info(f"Found {len(new_stakeholders)} potential new stakeholders")
    
    profiles_created = []
    
    for stakeholder in new_stakeholders:
        email = stakeholder['email']
        name = stakeholder['name']
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create profile for: {name} ({email})")
            continue
        
        # Create profile
        organization = infer_organization_from_email(email)
        
        profile_path = create_markdown_profile(
            name=name,
            email=email,
            organization=organization,
            meeting_context=f"First seen in: {stakeholder.get('meeting_summary', 'Calendar event')}"
        )
        
        markdown_rel_path = str(profile_path.relative_to(WORKSPACE))
        person_id = create_person_in_db(
            name=name,
            email=email,
            company=organization if organization not in ["[Unknown]", "[Personal Email]"] else None,
            markdown_path=markdown_rel_path,
            first_contact_date=stakeholder.get('meeting_date', '')[:10]
        )
        
        profiles_created.append({
            'name': name,
            'email': email,
            'person_id': person_id,
            'markdown_path': markdown_rel_path
        })
        logger.info(f"✓ Created: {name} ({email}) - ID {person_id}")
    
    # Summary
    logger.info(f"\n=== Summary ===")
    logger.info(f"Profiles created: {len(profiles_created)}")
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-create stakeholder profiles')
    parser.add_argument('--live', action='store_true', help='Run in live mode (default: dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
    parser.add_argument('--meeting-folder', type=str, help='Process specific meeting folder')
    args = parser.parse_args()
    
    dry_run = not args.live if not args.dry_run else True
    
    exit_code = main(dry_run=dry_run, meeting_folder=args.meeting_folder)
    sys.exit(exit_code)

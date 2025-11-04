#!/usr/bin/env python3
"""
Auto-Create Stakeholder Profiles from Calendar Events
Scans upcoming calendar, detects external stakeholders, creates profiles with email history.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from stakeholder_manager import (
    StakeholderIndex, 
    is_external_email,
    generate_slug,
    create_profile_file,
    infer_organization_from_email
)

WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "N5/data/profiles.db"


def scan_calendar_for_new_stakeholders(
    days_ahead: int = 7,
    use_app_google_calendar=None
) -> list:
    """
    Args:
        dry_run: If True, only report what would be created
        use_app_google_calendar: Zo's Google Calendar tool (must be provided)
    
    Scan calendar for upcoming meetings with external stakeholders.
    Returns list of dicts with stakeholder info for those not already in DB.
    
    Args:
        days_ahead: Number of days ahead to scan (default: 7)
        use_app_google_calendar: Zo's Google Calendar tool function (injected)
    
    Returns:
        List of dicts with keys: email, name, calendar_event_id, meeting_date,
        meeting_summary, description, attendees
    """
    
    logger.info(f"Scanning calendar for next {days_ahead} days...")
    
    # Calculate time range in RFC3339 format with timezone
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days_ahead)).isoformat()
    
    # If running standalone (not called by Zo), return instructions
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
        
        # Fetch upcoming events using Zo's Google Calendar tool
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
        
        events = events_response.get('items', [])
        logger.info(f"Retrieved {len(events)} calendar events")
        
    except Exception as e:
        logger.error(f"Failed to fetch calendar events: {e}")
        return []
    
    # Process events to extract new stakeholders
    return process_calendar_events(events)


def process_calendar_events(events: list) -> list:
    """
    Process calendar events to extract new external stakeholders.
    Checks database to avoid duplicates.
    
    Args:
        events: List of calendar event dicts from Google Calendar API
    
    Returns:
        List of new stakeholder dicts
    """
    # Connect to database for deduplication
    db_path = Path("/home/workspace/N5/data/profiles.db")
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_stakeholders = []
    seen_emails = set()
    
    for event in events:
        attendees = event.get('attendees', [])
        if not attendees:
            continue
        
        # Extract meeting details
        start_time = event.get('start', {})
        meeting_date = start_time.get('dateTime') or start_time.get('date', '')
        meeting_summary = event.get('summary', 'Untitled Meeting')
        event_id = event.get('id', '')
        description = event.get('description', '')
        
        # Process each attendee
        for attendee in attendees:
            email = attendee.get('email', '').lower().strip()
            if not email:
                continue
            
            display_name = attendee.get('displayName', '')
            # Generate name from email if no display name
            if not display_name:
                name_part = email.split('@')[0]
                display_name = name_part.replace('.', ' ').replace('_', ' ').title()
            name = display_name
            
            # Skip if not external email
            if not is_external_email(email):
                logger.debug(f"Skipping internal email: {email}")
                continue
            
            # Skip if already processed in this session
            if email in seen_emails:
                continue
            
            # Check database for existing profile
            cursor.execute('SELECT id, profile_path FROM profiles WHERE email = ?', (email,))
            existing = cursor.fetchone()
            if existing:
                logger.debug(f"Skipping {email} - already in database (profile: {existing[1]})")
                continue
            
            # New stakeholder found!
            seen_emails.add(email)
            
            stakeholder_data = {
                'email': email,
                'name': name,
                'calendar_event_id': event_id,
                'meeting_date': meeting_date,
                'meeting_summary': meeting_summary,
                'description': description,
                'attendees': [a.get('email') for a in attendees if a.get('email')]
            }
            
            new_stakeholders.append(stakeholder_data)
            logger.info(f"✓ New stakeholder: {name} ({email}) in '{meeting_summary}' on {meeting_date[:10]}")
    
    conn.close()
    
    logger.info(f"Found {len(new_stakeholders)} new external stakeholders (from {len(events)} events)")
    return new_stakeholders



def fetch_email_history(email: str, max_results: int = 100) -> dict:
    """
    Fetch full email history with a stakeholder.
    
    NOTE: This is a stub. Actual implementation should use:
    - use_app_gmail('gmail-find-email', {'q': f'from:{email} OR to:{email}', 'maxResults': max_results})
    - Parse results
    - Return structured data
    
    Returns: {
        'messages': [...],
        'first_email_date': 'YYYY-MM-DD',
        'last_email_date': 'YYYY-MM-DD',
        'thread_count': N,
        'summary': 'LLM-generated summary'
    }
    """
    
    logger.info(f"Fetching email history for {email} (max {max_results} results)...")
    
    # Placeholder
    return {
        'messages': [],
        'first_email_date': None,
        'last_email_date': None,
        'thread_count': 0,
        'summary': 'No emails found'
    }


def analyze_stakeholder_with_llm(
    name: str,
    email: str,
    calendar_event: dict,
    email_history: dict
) -> dict:
    """
    Use LLM to analyze stakeholder and generate profile fields.
    
    This function should:
    1. Construct a prompt with all available data
    2. Ask LLM to infer:
       - Organization (from email domain, signature, context)
       - Role/title (from email signature, LinkedIn if found)
       - Lead type (LD-INV/LD-HIR/LD-COM/LD-NET/LD-GEN)
       - How we met (earliest email context)
       - Relationship type (partnership, hiring, etc.)
       - Interaction summary (synthesize email thread)
    3. Return structured data
    
    Returns: {
        'organization': str,
        'role': str,
        'lead_type': str,  # LD-* tag
        'lead_type_confidence': 'high' | 'medium' | 'low',
        'relationship_context': str,
        'interaction_summary': str,
        'questions_for_v': [str],  # Questions to ask V if uncertain
        'linkedin_url': str | None,
        'first_contact_date': str
    }
    """
    
    logger.info(f"Analyzing stakeholder with LLM: {name} ({email})...")
    
    # NOTE: In actual implementation, this would call the LLM with a carefully
    # constructed prompt containing:
    # - Calendar event details
    # - All email messages (or summary if too long)
    # - Instructions to infer fields
    # - Instructions to flag uncertainties
    
    # Placeholder: Basic inference
    organization = infer_organization_from_email(email)
    
    analysis = {
        'organization': organization,
        'role': '[To be determined]',
        'lead_type': 'LD-GEN',  # Default to general if uncertain
        'lead_type_confidence': 'low',
        'relationship_context': f"First contact via calendar invite: {calendar_event.get('meeting_summary', 'Meeting')}",
        'interaction_summary': email_history.get('summary', 'No prior email history found'),
        'questions_for_v': [],
        'linkedin_url': None,
        'first_contact_date': email_history.get('first_email_date') or calendar_event.get('meeting_date')
    }
    
    # Add questions if confidence is low
    if analysis['lead_type_confidence'] in ['low', 'medium']:
        analysis['questions_for_v'].append(
            f"What lead type best describes {name}? (LD-INV=investor, LD-HIR=hiring, LD-COM=community, LD-NET=networking, LD-GEN=general)"
        )
    
    if analysis['role'] == '[To be determined]':
        analysis['questions_for_v'].append(
            f"What is {name}'s role/title at {organization}?"
        )
    
    return analysis


def create_stakeholder_profile_auto(
    email: str,
    name: str,
    calendar_event: dict
) -> Path:
    """
    Orchestrate full stakeholder profile creation:
    1. Check if profile already exists (in profiles.db)
    2. Fetch email history from Gmail
    3. Analyze with LLM
    4. Create profile file
    5. Track in profiles.db
    6. Return profile path
    """
    
    # Check if already exists in profiles.db
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT profile_path FROM profiles WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            logger.info(f"Profile already exists for {email}: {existing[0]}")
            return WORKSPACE / existing[0]
        
        logger.info(f"Creating new profile for {name} ({email})...")
        
        # Fetch email history from Gmail
        try:
            email_history = fetch_email_history(email, max_results=100)
        except Exception as e:
            logger.warning(f"Could not fetch email history: {e}")
            email_history = {
                'messages': [],
                'first_email_date': None,
                'last_email_date': None,
                'thread_count': 0,
                'summary': 'Email fetch failed'
            }
        
        # Analyze with LLM
        try:
            analysis = analyze_stakeholder_with_llm(
                name=name,
                email=email,
                calendar_event=calendar_event,
                email_history=email_history
            )
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}", exc_info=True)
            # Fallback to basic inference
            analysis = {
                'organization': infer_organization_from_email(email),
                'role': '[To be determined]',
                'lead_type': 'LD-GEN',
                'lead_type_confidence': 'low',
                'relationship_context': f"First contact via calendar invite: {calendar_event.get('meeting_summary', 'Meeting')}",
                'interaction_summary': email_history.get('summary', 'No prior email history'),
                'questions_for_v': [],
                'linkedin_url': None,
                'first_contact_date': email_history.get('first_email_date') or calendar_event.get('meeting_date')
            }
        
        # Create profile file using stakeholder_manager
        profile_path = create_profile_file(
            email=email,
            name=name,
            organization=analysis['organization'],
            role=analysis['role'],
            lead_type=analysis['lead_type'],
            relationship_context=analysis['relationship_context'],
            interaction_summary=analysis['interaction_summary'],
            first_contact_date=analysis['first_contact_date'],
            email_threads=[],
            calendar_ids=[calendar_event.get('calendar_event_id')]
        )
        
        # Track in profiles.db
        meeting_date = calendar_event.get('meeting_date', datetime.now().date().isoformat())
        created_at = datetime.now().isoformat()
        profile_rel_path = profile_path.relative_to(WORKSPACE)
        
        cursor.execute("""
            INSERT INTO profiles (email, name, organization, profile_path, meeting_date, created_at, enrichment_count)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (email, name, analysis['organization'], str(profile_rel_path), meeting_date, created_at))
        
        profile_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"✓ Profile created and tracked: {profile_path} (DB ID: {profile_id})")
        
        # Log questions for V if any
        if analysis.get('questions_for_v'):
            logger.info("")
            logger.info(f"Questions for V about {name}:")
            for q in analysis['questions_for_v']:
                logger.info(f"  - {q}")
        
        return profile_path
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to create profile: {e}", exc_info=True)
        raise
    finally:
        conn.close()



def main(dry_run: bool = True, use_app_google_calendar=None):
    """
    Main orchestration:
    1. Scan calendar for upcoming meetings
    2. Filter for external stakeholders
    3. Create profiles for any new ones
    4. Report summary
    """
    
    logger.info("=== Auto-Create Stakeholder Profiles ===")
    
    if dry_run:
        logger.info("DRY RUN MODE - No files will be created")
    
    # Scan calendar
    new_stakeholders = scan_calendar_for_new_stakeholders(
        days_ahead=7,
        use_app_google_calendar=use_app_google_calendar
    )
    
    # Check if instructions were returned (no tool access)
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
    
    # Process each
    profiles_created = []
    questions_log = []
    
    for stakeholder in new_stakeholders:
        email = stakeholder['email']
        name = stakeholder['name']
        
        if not is_external_email(email):
            logger.info(f"Skipping internal email: {email}")
            continue
        
        if not dry_run:
            profile_path = create_stakeholder_profile_auto(
                email=email,
                name=name,
                calendar_event=stakeholder
            )
            profiles_created.append(profile_path)
        else:
            logger.info(f"[DRY RUN] Would create profile for: {name} ({email})")
    
    # Summary
    logger.info(f"\n=== Summary ===")
    logger.info(f"Profiles created: {len(profiles_created)}")
    
    if questions_log:
        logger.info(f"\nQuestions for V:")
        for q in questions_log:
            logger.info(f"  {q}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-create stakeholder profiles')
    parser.add_argument('--live', action='store_true', help='Run in live mode (default: dry-run)')
    args = parser.parse_args()
    
    main(dry_run=not args.live)

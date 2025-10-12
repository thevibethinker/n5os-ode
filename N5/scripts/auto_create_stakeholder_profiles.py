#!/usr/bin/env python3
"""
Auto-Create Stakeholder Profiles from Calendar Events
Scans upcoming calendar, detects external stakeholders, creates profiles with email history.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
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


def scan_calendar_for_new_stakeholders(days_ahead: int = 7) -> list:
    """
    Scan calendar for upcoming meetings with external stakeholders.
    Returns list of (email, name, calendar_event) tuples.
    
    NOTE: This is a stub. The actual implementation should use
    use_app_google_calendar to fetch events. Here we just document the logic.
    """
    
    logger.info(f"Scanning calendar for next {days_ahead} days...")
    
    # Placeholder: In practice, this would call:
    # - use_app_google_calendar('google_calendar-list-events', {...})
    # - Parse attendees
    # - Filter for external emails
    # - Return list of new stakeholders
    
    new_stakeholders = []
    
    # Example return format:
    # new_stakeholders.append({
    #     'email': 'person@domain.com',
    #     'name': 'Person Name',
    #     'calendar_event_id': 'abc123',
    #     'meeting_date': '2025-10-14',
    #     'meeting_summary': 'Meeting Title',
    #     'description': 'Calendar description field',
    #     'attendees': ['person@domain.com', 'vrijen@mycareerspan.com']
    # })
    
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
    1. Check if profile already exists
    2. Fetch email history
    3. Analyze with LLM
    4. Create profile file
    5. Return questions for V if any
    """
    
    # Check if already exists
    index = StakeholderIndex()
    existing = index.find_by_email(email)
    
    if existing:
        logger.info(f"Profile already exists for {email}: {existing['file']}")
        return WORKSPACE / existing['file']
    
    logger.info(f"Creating new profile for {name} ({email})...")
    
    # Fetch email history
    email_history = fetch_email_history(email, max_results=100)
    
    # Analyze with LLM
    analysis = analyze_stakeholder_with_llm(
        name=name,
        email=email,
        calendar_event=calendar_event,
        email_history=email_history
    )
    
    # Create profile
    profile_path = create_profile_file(
        email=email,
        name=name,
        organization=analysis['organization'],
        role=analysis['role'],
        lead_type=analysis['lead_type'],
        relationship_context=analysis['relationship_context'],
        interaction_summary=analysis['interaction_summary'],
        first_contact_date=analysis['first_contact_date'],
        email_threads=[],  # Would populate from email_history
        calendar_ids=[calendar_event.get('calendar_event_id')]
    )
    
    # Log questions for V
    if analysis['questions_for_v']:
        logger.info(f"Questions for V about {name}:")
        for q in analysis['questions_for_v']:
            logger.info(f"  - {q}")
    
    return profile_path


def main(dry_run: bool = True):
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
    new_stakeholders = scan_calendar_for_new_stakeholders(days_ahead=7)
    
    if not new_stakeholders:
        logger.info("No new external stakeholders found in upcoming meetings")
        return
    
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

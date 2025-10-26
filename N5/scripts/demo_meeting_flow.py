#!/usr/bin/env python3
"""
Demo: Full Meeting Prep Flow
Demonstrates how state tracking + profile management work together
"""

from meeting_state_manager import (
    load_state,
    add_processed_event,
    is_event_processed
)

from stakeholder_profile_manager import (
    create_stakeholder_profile,
    find_stakeholder_profile,
    append_meeting_to_profile
)


def process_calendar_event(event, gmail_context):
    """
    Process a calendar event: create/update profile, track state
    
    Args:
        event: dict - Calendar event from Google Calendar API
        gmail_context: dict - Email threads from Gmail API
    
    Returns:
        str: Profile path or None if already processed
    """
    
    event_id = event['id']
    
    # Step 1: Check if already processed
    if is_event_processed(event_id):
        print(f"⏭️  Event {event_id} already processed, skipping")
        return None
    
    print(f"🔍 Processing new event: {event['summary']}")
    
    # Step 2: Extract attendee info
    attendee = event['attendees'][0]  # Primary attendee
    attendee_email = attendee['email']
    attendee_name = attendee.get('displayName', attendee_email)
    
    # Step 3: Extract V-OS tags
    tags = extract_tags(event)
    print(f"   Tags: {tags}")
    
    # Step 4: Determine stakeholder info
    stakeholder_type = determine_stakeholder_type(tags)
    organization = extract_organization(event['summary'])
    
    # Step 5: Look up existing profile
    existing_profile = find_stakeholder_profile(attendee_email)
    
    if existing_profile:
        print(f"   ✓ Found existing profile: {existing_profile}")
        # Update existing profile with new meeting
        append_meeting_to_profile(existing_profile, event, tags)
        profile_path = existing_profile
    else:
        print(f"   ✓ Creating new profile for {attendee_name}")
        # Create new profile
        profile_path = create_stakeholder_profile(
            name=attendee_name,
            email=attendee_email,
            organization=organization,
            stakeholder_type=stakeholder_type,
            meeting=event,
            tags=tags,
            email_context=gmail_context
        )
    
    # Step 6: Mark event as processed
    add_processed_event(event_id, {
        'title': event['summary'],
        'priority': 'urgent' if tags.get('priority') == 'critical' else 'normal',
        'stakeholder_profiles': [profile_path]
    })
    
    print(f"   ✅ Event processed, profile: {profile_path}")
    return profile_path


def extract_tags(event):
    """Extract V-OS tags from event description"""
    import re
    description = event.get('description', '')
    
    tags = {
        'stakeholder': '',
        'timing': '',
        'priority': 'normal',
        'accommodation': 'A-0'
    }
    
    # Extract stakeholder type
    for tag in ['LD-INV', 'LD-HIR', 'LD-COM', 'LD-NET', 'LD-GEN']:
        if tag in description:
            tags['stakeholder'] = tag
            break
    
    # Extract timing
    timing_match = re.search(r'\[(D\d+\+?)\]', description)
    if timing_match:
        tags['timing'] = timing_match.group(1)
    
    # Check for priority marker
    if '*' in description.split('\n')[0]:
        tags['priority'] = 'critical'
    
    return tags


def determine_stakeholder_type(tags):
    """Map V-OS tag to stakeholder type"""
    type_map = {
        'LD-INV': 'Investor',
        'LD-HIR': 'Candidate',
        'LD-COM': 'Community',
        'LD-NET': 'Partner',
        'LD-GEN': 'General'
    }
    return type_map.get(tags.get('stakeholder', ''), 'General')


def extract_organization(summary):
    """Extract organization from meeting summary"""
    # Simple heuristic: look for " - Name (Org)" pattern
    import re
    match = re.search(r'-\s+([A-Z][^-]+)$', summary)
    if match:
        parts = match.group(1).strip().split()
        if len(parts) > 1:
            return ' '.join(parts[1:])
    return ''


def demo():
    """Demonstrate the full flow with mock data"""
    
    print("=" * 60)
    print("DEMO: Full Meeting Prep Flow")
    print("=" * 60)
    print()
    
    # Mock calendar event
    mock_event = {
        'id': 'demo_event_12345',
        'summary': 'Series A Discussion - Jane Smith',
        'description': '''[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest.''',
        'start': {'dateTime': '2025-10-15T14:00:00-04:00'},
        'attendees': [
            {
                'email': 'jane@acmeventures.com',
                'displayName': 'Jane Smith',
                'responseStatus': 'accepted'
            }
        ]
    }
    
    # Mock Gmail context
    mock_gmail = {
        'threads': [
            {
                'date': '2025-10-10',
                'subject': 'Introduction - Vrijen Attawar',
                'snippet': 'Jane replied to intro, expressed interest'
            }
        ]
    }
    
    # Process the event
    profile_path = process_calendar_event(mock_event, mock_gmail)
    
    print()
    print("=" * 60)
    print(f"✅ Demo complete! Profile: {profile_path}")
    print("=" * 60)


if __name__ == "__main__":
    demo()

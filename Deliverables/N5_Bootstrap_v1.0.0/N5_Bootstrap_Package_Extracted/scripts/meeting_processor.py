#!/usr/bin/env python3
"""
Meeting Processor
Main orchestrator for meeting prep pipeline
Coordinates API integration, state tracking, and profile management
"""

import sys
from pathlib import Path

# Import our modules
from meeting_state_manager import (
    load_state,
    add_processed_event,
    is_event_processed
)

from stakeholder_profile_manager import (
    create_stakeholder_profile,
    find_stakeholder_profile,
    append_meeting_to_profile,
    STAKEHOLDER_TYPE_MAP
)

from meeting_api_integrator import MeetingAPIIntegrator


class MeetingProcessor:
    """
    Main processor for meeting prep pipeline
    """
    
    def __init__(self, api_integrator: MeetingAPIIntegrator):
        """
        Initialize processor
        
        Args:
            api_integrator: MeetingAPIIntegrator instance with API tools
        """
        self.api = api_integrator
    
    def process_upcoming_meetings(self, days_ahead: int = 7) -> dict:
        """
        Process all upcoming meetings from calendar
        
        Args:
            days_ahead: Number of days ahead to process
        
        Returns:
            Dict with processing results
        """
        print("=" * 60)
        print("MEETING PROCESSOR: Processing Upcoming Meetings")
        print("=" * 60)
        print()
        
        results = {
            'total_events': 0,
            'new_events': 0,
            'already_processed': 0,
            'new_profiles': 0,
            'updated_profiles': 0,
            'errors': 0,
            'processed_event_ids': []
        }
        
        # Step 1: Fetch calendar events
        events = self.api.fetch_upcoming_meetings(days_ahead)
        results['total_events'] = len(events)
        
        if not events:
            print("No upcoming meetings with V-OS tags found.\n")
            return results
        
        print()
        
        # Step 2: Process each event
        for event in events:
            try:
                event_result = self.process_single_event(event)
                
                # Update results
                if event_result['processed']:
                    results['new_events'] += 1
                    results['processed_event_ids'].append(event_result['event_id'])
                    
                    if event_result['profile_created']:
                        results['new_profiles'] += 1
                    elif event_result['profile_updated']:
                        results['updated_profiles'] += 1
                else:
                    results['already_processed'] += 1
            
            except Exception as e:
                print(f"   ✗ Error processing event: {e}")
                results['errors'] += 1
                continue
        
        # Step 3: Print summary
        print()
        print("=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total events found:      {results['total_events']}")
        print(f"New events processed:    {results['new_events']}")
        print(f"Already processed:       {results['already_processed']}")
        print(f"New profiles created:    {results['new_profiles']}")
        print(f"Existing profiles updated: {results['updated_profiles']}")
        print(f"Errors:                  {results['errors']}")
        print("=" * 60)
        print()
        
        return results
    
    def process_single_event(self, event: dict) -> dict:
        """
        Process a single calendar event
        
        Args:
            event: Calendar event from API
        
        Returns:
            Dict with processing result
        """
        # Extract structured details
        details = self.api.extract_event_details(event)
        
        event_id = details['id']
        summary = details['summary']
        tags = details['tags']
        
        print(f"📅 {summary}")
        print(f"   ID: {event_id}")
        print(f"   Tags: {tags}")
        
        result = {
            'event_id': event_id,
            'processed': False,
            'profile_created': False,
            'profile_updated': False,
            'profile_path': None
        }
        
        # Step 1: Check if already processed
        if is_event_processed(event_id):
            print(f"   ⏭️  Already processed, skipping\n")
            return result
        
        # Step 2: Get primary attendee (first non-self attendee)
        attendees = details['attendees']
        if not attendees:
            print(f"   ⚠️  No attendees found, skipping\n")
            return result
        
        primary_attendee = attendees[0]
        attendee_email = primary_attendee['email']
        attendee_name = primary_attendee['name']
        
        print(f"   👤 Primary attendee: {attendee_name} ({attendee_email})")
        
        # Step 3: Search Gmail for email context
        gmail_context = self.api.search_gmail_for_attendee(attendee_email, max_results=5)
        
        # Step 4: Look up existing profile
        existing_profile = find_stakeholder_profile(attendee_email)
        
        if existing_profile:
            print(f"   ✓ Found existing profile: {existing_profile}")
            # Update existing profile
            append_meeting_to_profile(existing_profile, details, tags)
            profile_path = existing_profile
            result['profile_updated'] = True
        else:
            print(f"   ✓ Creating new profile...")
            # Determine stakeholder type and organization
            stakeholder_type = self._determine_stakeholder_type(tags)
            organization = self._extract_organization(summary, attendee_name)
            
            # Create new profile
            profile_path = create_stakeholder_profile(
                name=attendee_name,
                email=attendee_email,
                organization=organization,
                stakeholder_type=stakeholder_type,
                meeting=details,
                tags=tags,
                email_context=gmail_context
            )
            result['profile_created'] = True
        
        result['profile_path'] = profile_path
        
        # Step 5: Mark event as processed
        add_processed_event(event_id, {
            'title': summary,
            'priority': 'urgent' if tags.get('priority') == 'critical' else 'normal',
            'stakeholder_profiles': [profile_path]
        })
        
        result['processed'] = True
        print(f"   ✅ Event processed\n")
        
        return result
    
    def _determine_stakeholder_type(self, tags: dict) -> str:
        """Determine stakeholder type from tags"""
        stakeholder_tag = tags.get('stakeholder', '')
        return STAKEHOLDER_TYPE_MAP.get(stakeholder_tag, 'General')
    
    def _extract_organization(self, summary: str, attendee_name: str) -> str:
        """
        Extract organization from meeting summary
        
        Args:
            summary: Meeting title
            attendee_name: Name of attendee
        
        Returns:
            Organization name or empty string
        """
        # Try to extract organization from summary
        # Common patterns:
        # - "Meeting - Name (Organization)"
        # - "Meeting - Name - Organization"
        # - "Meeting with Name at Organization"
        
        import re
        
        # Pattern 1: Name (Organization)
        match = re.search(rf'{re.escape(attendee_name)}\s*\(([^)]+)\)', summary)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: After " - " following name
        parts = summary.split(' - ')
        for i, part in enumerate(parts):
            if attendee_name in part and i + 1 < len(parts):
                return parts[i + 1].strip()
        
        # Pattern 3: After " at "
        match = re.search(r'\s+at\s+([A-Z][^,]+)', summary)
        if match:
            return match.group(1).strip()
        
        return ''


def demo_with_mock_api():
    """Demo processor with mock API (for testing without real API calls)"""
    
    class MockAPI:
        def fetch_upcoming_meetings(self, days_ahead):
            return [
                {
                    'id': 'mock_event_123',
                    'summary': 'Series A Discussion - Jane Smith (Acme Ventures)',
                    'description': '[LD-INV] [D5+] *\n\nPurpose: Discuss funding\nContext: Strong interest',
                    'start': {'dateTime': '2025-10-15T14:00:00-04:00'},
                    'attendees': [
                        {'email': 'jane@acmeventures.com', 'displayName': 'Jane Smith'}
                    ]
                }
            ]
        
        def extract_event_details(self, event):
            return {
                'id': event['id'],
                'summary': event['summary'],
                'description': event['description'],
                'start': event['start'],
                'attendees': [{'email': a['email'], 'name': a['displayName'], 'responseStatus': 'accepted'} for a in event['attendees']],
                'tags': {'stakeholder': 'LD-INV', 'timing': 'D5+', 'priority': 'critical', 'accommodation': 'A-0'},
                'purpose': 'Discuss funding',
                'context': 'Strong interest'
            }
        
        def search_gmail_for_attendee(self, email, max_results):
            return {
                'threads': [
                    {'date': '2025-10-10', 'subject': 'Introduction', 'snippet': 'Nice to meet you'}
                ]
            }
    
    processor = MeetingProcessor(MockAPI())
    return processor.process_upcoming_meetings()


if __name__ == "__main__":
    print("Meeting Processor module loaded")
    print("\nTo use:")
    print("1. Create API integrator with Zo's tools")
    print("2. Create processor: processor = MeetingProcessor(api_integrator)")
    print("3. Process meetings: processor.process_upcoming_meetings()")
    print("\nOr run demo: demo_with_mock_api()")

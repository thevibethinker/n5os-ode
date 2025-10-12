#!/usr/bin/env python3
"""
Integration tests for full meeting prep flow
Tests state tracking + stakeholder profile system working together
"""

import shutil
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from meeting_state_manager import (
    load_state,
    add_processed_event,
    is_event_processed,
    get_processed_event,
    STATE_FILE
)

from stakeholder_profile_manager import (
    create_stakeholder_profile,
    find_stakeholder_profile,
    append_meeting_to_profile,
    MEETINGS_DIR
)


# ============================================================================
# MOCK DATA - Simulating real calendar events and Gmail context
# ============================================================================

MOCK_CALENDAR_EVENT_1 = {
    'id': 'cal_abc123xyz',
    'summary': 'Series A Discussion - Jane Smith',
    'description': '''[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest in Careerspan's ed-tech traction, wants to discuss funding terms and timeline.

---
Please send pitch deck in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...''',
    'start': {
        'dateTime': '2025-10-15T14:00:00-04:00'
    },
    'attendees': [
        {
            'email': 'jane@acmeventures.com',
            'displayName': 'Jane Smith',
            'responseStatus': 'accepted'
        }
    ]
}

MOCK_CALENDAR_EVENT_2 = {
    'id': 'cal_def456uvw',
    'summary': 'Engineering Interview - Alex Chen',
    'description': '''[LD-HIR] [D3]

Purpose: Technical interview for Senior Engineer role

Context: Alex applied via LinkedIn, strong backend experience with Python/Django, previous startup experience.''',
    'start': {
        'dateTime': '2025-10-16T10:00:00-04:00'
    },
    'attendees': [
        {
            'email': 'alex.chen@gmail.com',
            'displayName': 'Alex Chen',
            'responseStatus': 'accepted'
        }
    ]
}

MOCK_CALENDAR_EVENT_3 = {
    'id': 'cal_ghi789rst',
    'summary': 'Follow-up: Series A Discussion',
    'description': '''[LD-INV] [D3]

Purpose: Review term sheet

Context: Follow-up to previous discussion, Jane sent term sheet draft for review.''',
    'start': {
        'dateTime': '2025-10-20T14:00:00-04:00'
    },
    'attendees': [
        {
            'email': 'jane@acmeventures.com',
            'displayName': 'Jane Smith',
            'responseStatus': 'accepted'
        }
    ]
}

MOCK_GMAIL_CONTEXT_JANE = {
    'threads': [
        {
            'date': '2025-10-10',
            'subject': 'Introduction - Vrijen Attawar (Careerspan)',
            'snippet': 'Jane replied to intro, expressed interest in ed-tech traction'
        },
        {
            'date': '2025-10-12',
            'subject': 'Re: Introduction - Pitch Deck',
            'snippet': 'Jane requested pitch deck, mentioned she loves mission-driven founders'
        }
    ]
}

MOCK_GMAIL_CONTEXT_ALEX = {
    'threads': [
        {
            'date': '2025-10-08',
            'subject': 'Application: Senior Engineer Position',
            'snippet': 'Alex applied via LinkedIn with impressive resume'
        }
    ]
}


def cleanup_all():
    """Remove all test files"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    backup = STATE_FILE.with_suffix('.json.backup')
    if backup.exists():
        backup.unlink()
    
    if MEETINGS_DIR.exists():
        for item in MEETINGS_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)


def extract_tags(event: dict) -> dict:
    """Extract V-OS tags from event description"""
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
    import re
    timing_match = re.search(r'\[(D\d+\+?)\]', description)
    if timing_match:
        tags['timing'] = timing_match.group(1)
    
    # Check for priority
    if '*' in description.split('\n')[0]:  # Priority marker in first line
        tags['priority'] = 'critical'
    
    return tags


def test_full_flow_new_stakeholder():
    """Test: New calendar event → Create profile → Mark processed"""
    print("=" * 60)
    print("Test 1: Full flow with new stakeholder")
    print("=" * 60)
    
    cleanup_all()
    
    # Step 1: Detect new event
    event = MOCK_CALENDAR_EVENT_1
    event_id = event['id']
    
    print(f"1. Detected new event: {event['summary']}")
    assert not is_event_processed(event_id), "Event should not be processed yet"
    print("   ✓ Event not in processed list")
    
    # Step 2: Extract tags
    tags = extract_tags(event)
    print(f"2. Extracted tags: {tags}")
    assert tags['stakeholder'] == 'LD-INV', "Should identify as investor"
    assert tags['priority'] == 'critical', "Should be critical priority"
    
    # Step 3: Look up stakeholder by email
    attendee_email = event['attendees'][0]['email']
    attendee_name = event['attendees'][0]['displayName']
    
    existing_profile = find_stakeholder_profile(attendee_email)
    print(f"3. Looked up stakeholder by email: {attendee_email}")
    assert existing_profile is None, "Should not find existing profile"
    print("   ✓ No existing profile found")
    
    # Step 4: Create new stakeholder profile
    print("4. Creating new stakeholder profile...")
    profile_path = create_stakeholder_profile(
        name=attendee_name,
        email=attendee_email,
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=event,
        tags=tags,
        email_context=MOCK_GMAIL_CONTEXT_JANE
    )
    
    assert profile_path is not None, "Profile should be created"
    print(f"   ✓ Profile created: {profile_path}")
    
    # Step 5: Mark event as processed
    print("5. Marking event as processed...")
    add_processed_event(event_id, {
        'title': event['summary'],
        'priority': 'urgent' if tags['priority'] == 'critical' else 'normal',
        'stakeholder_profiles': [profile_path]
    })
    
    assert is_event_processed(event_id), "Event should be marked as processed"
    print("   ✓ Event marked as processed")
    
    # Step 6: Verify state persistence
    state = load_state()
    assert event_id in state['processed_events'], "Event should be in state"
    assert profile_path in state['processed_events'][event_id]['stakeholder_profiles']
    print("   ✓ State persisted correctly")
    
    print("\n✅ Test 1 PASSED: Full flow with new stakeholder\n")


def test_full_flow_existing_stakeholder():
    """Test: Second meeting with same stakeholder → Update profile → No duplicate"""
    print("=" * 60)
    print("Test 2: Full flow with existing stakeholder")
    print("=" * 60)
    
    cleanup_all()
    
    # Create first meeting (setup)
    event1 = MOCK_CALENDAR_EVENT_1
    tags1 = extract_tags(event1)
    profile_path1 = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=event1,
        tags=tags1,
        email_context=MOCK_GMAIL_CONTEXT_JANE
    )
    add_processed_event(event1['id'], {
        'title': event1['summary'],
        'priority': 'urgent',
        'stakeholder_profiles': [profile_path1]
    })
    
    print("Setup: Created first meeting profile")
    
    # Now process second meeting
    event3 = MOCK_CALENDAR_EVENT_3
    event_id = event3['id']
    
    print(f"\n1. Detected new event: {event3['summary']}")
    assert not is_event_processed(event_id), "New event should not be processed"
    
    # Look up stakeholder
    attendee_email = event3['attendees'][0]['email']
    existing_profile = find_stakeholder_profile(attendee_email)
    
    print(f"2. Looked up stakeholder by email: {attendee_email}")
    assert existing_profile is not None, "Should find existing profile"
    print(f"   ✓ Found existing profile: {existing_profile}")
    
    # Update profile with new meeting
    tags3 = extract_tags(event3)
    print("3. Appending meeting to existing profile...")
    append_meeting_to_profile(existing_profile, event3, tags3)
    print("   ✓ Meeting appended to profile")
    
    # Mark as processed
    add_processed_event(event_id, {
        'title': event3['summary'],
        'priority': 'normal',
        'stakeholder_profiles': [existing_profile]
    })
    
    # Verify no duplicate profiles
    jane_profiles = list(MEETINGS_DIR.glob("*jane*"))
    assert len(jane_profiles) == 1, "Should only have one profile for Jane"
    print(f"4. Verified no duplicate profiles: {len(jane_profiles)} profile(s)")
    
    # Verify both events processed
    assert is_event_processed(event1['id']), "First event should be processed"
    assert is_event_processed(event3['id']), "Third event should be processed"
    print("5. Both events marked as processed")
    
    print("\n✅ Test 2 PASSED: Full flow with existing stakeholder\n")


def test_multiple_different_stakeholders():
    """Test: Multiple events with different stakeholders"""
    print("=" * 60)
    print("Test 3: Multiple different stakeholders")
    print("=" * 60)
    
    cleanup_all()
    
    events = [
        (MOCK_CALENDAR_EVENT_1, 'Jane Smith', 'jane@acmeventures.com', 'Acme Ventures', MOCK_GMAIL_CONTEXT_JANE),
        (MOCK_CALENDAR_EVENT_2, 'Alex Chen', 'alex.chen@gmail.com', '', MOCK_GMAIL_CONTEXT_ALEX)
    ]
    
    profile_paths = []
    
    for event, name, email, org, gmail_context in events:
        print(f"\nProcessing: {event['summary']}")
        
        # Check if processed
        assert not is_event_processed(event['id']), "Event should not be processed"
        
        # Look up stakeholder
        existing_profile = find_stakeholder_profile(email)
        
        if existing_profile:
            print(f"  → Found existing profile, updating...")
            tags = extract_tags(event)
            append_meeting_to_profile(existing_profile, event, tags)
            profile_path = existing_profile
        else:
            print(f"  → No existing profile, creating new...")
            tags = extract_tags(event)
            stakeholder_type = 'Investor' if 'LD-INV' in tags['stakeholder'] else 'Candidate'
            profile_path = create_stakeholder_profile(
                name=name,
                email=email,
                organization=org,
                stakeholder_type=stakeholder_type,
                meeting=event,
                tags=tags,
                email_context=gmail_context
            )
        
        # Mark as processed
        add_processed_event(event['id'], {
            'title': event['summary'],
            'priority': 'urgent' if tags.get('priority') == 'critical' else 'normal',
            'stakeholder_profiles': [profile_path]
        })
        
        profile_paths.append(profile_path)
        print(f"  ✓ Processed successfully")
    
    # Verify state
    state = load_state()
    assert len(state['processed_events']) == 2, "Should have 2 processed events"
    print(f"\n✓ Verified state: {len(state['processed_events'])} events processed")
    
    # Verify profiles created
    all_profiles = list(MEETINGS_DIR.glob("*/profile.md"))
    assert len(all_profiles) == 2, "Should have 2 profiles"
    print(f"✓ Verified profiles: {len(all_profiles)} profiles created")
    
    print("\n✅ Test 3 PASSED: Multiple different stakeholders\n")


def test_duplicate_prevention():
    """Test: Same event ID processed twice → Should skip second time"""
    print("=" * 60)
    print("Test 4: Duplicate prevention")
    print("=" * 60)
    
    cleanup_all()
    
    event = MOCK_CALENDAR_EVENT_1
    event_id = event['id']
    
    # Process first time
    print("1. Processing event first time...")
    tags = extract_tags(event)
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=event,
        tags=tags,
        email_context=MOCK_GMAIL_CONTEXT_JANE
    )
    add_processed_event(event_id, {
        'title': event['summary'],
        'priority': 'urgent',
        'stakeholder_profiles': [profile_path]
    })
    
    assert is_event_processed(event_id), "Event should be processed"
    print("   ✓ Event processed")
    
    # Try to process again
    print("2. Checking if event already processed...")
    if is_event_processed(event_id):
        print("   ✓ Event already processed, skipping")
    else:
        raise AssertionError("Should have detected duplicate!")
    
    # Verify only one profile
    jane_profiles = list(MEETINGS_DIR.glob("*jane*"))
    assert len(jane_profiles) == 1, "Should only have one profile"
    print(f"3. Verified no duplicate profiles: {len(jane_profiles)} profile(s)")
    
    print("\n✅ Test 4 PASSED: Duplicate prevention works\n")


def run_all_integration_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("INTEGRATION TESTS: Meeting Prep Full Flow")
    print("=" * 60)
    print()
    
    tests = [
        test_full_flow_new_stakeholder,
        test_full_flow_existing_stakeholder,
        test_multiple_different_stakeholders,
        test_duplicate_prevention
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n✅ System Ready:")
        print("   - State tracking working")
        print("   - Profile creation working")
        print("   - Profile lookup working")
        print("   - Duplicate prevention working")
        print("   - Ready for API integration (Phase 2B Priority 2)")
    
    # Cleanup
    cleanup_all()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)

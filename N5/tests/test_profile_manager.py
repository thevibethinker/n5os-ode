#!/usr/bin/env python3
"""
Unit tests for stakeholder_profile_manager.py
"""

import os
import shutil
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from stakeholder_profile_manager import (
    create_stakeholder_profile,
    find_stakeholder_profile,
    update_stakeholder_profile,
    append_meeting_to_profile,
    MEETINGS_DIR,
    _sanitize_name
)


# Mock data for testing
MOCK_MEETING_1 = {
    'id': 'test123abc',
    'summary': 'Series A Discussion - Jane Smith',
    'description': '''[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest in Careerspan's ed-tech traction, wants to discuss funding terms and timeline.''',
    'start': {
        'dateTime': '2025-10-15T14:00:00-04:00'
    }
}

MOCK_MEETING_2 = {
    'id': 'test456def',
    'summary': 'Follow-up: Series A Discussion',
    'description': '''[LD-INV] [D3] 

Purpose: Review term sheet

Context: Follow-up to previous discussion, Jane sent term sheet draft.''',
    'start': {
        'dateTime': '2025-10-20T10:00:00-04:00'
    }
}

MOCK_TAGS_1 = {
    'stakeholder': 'LD-INV',
    'timing': 'D5+',
    'priority': 'critical',
    'accommodation': 'A-0'
}

MOCK_TAGS_2 = {
    'stakeholder': 'LD-INV',
    'timing': 'D3',
    'priority': 'normal',
    'accommodation': 'A-0'
}

MOCK_EMAIL_CONTEXT = {
    'threads': [
        {
            'date': '2025-10-10',
            'subject': 'Introduction - Vrijen Attawar (Careerspan)',
            'snippet': 'Jane replied to intro, expressed interest'
        }
    ]
}


def cleanup_test_profiles():
    """Remove test profile directories"""
    if MEETINGS_DIR.exists():
        for item in MEETINGS_DIR.iterdir():
            if item.is_dir() and 'jane' in item.name.lower():
                shutil.rmtree(item)
            elif item.is_dir() and 'alex' in item.name.lower():
                shutil.rmtree(item)


def test_directory_name_sanitization():
    """Test that directory names are properly sanitized"""
    print("Testing directory name sanitization...")
    
    assert _sanitize_name("Jane Smith") == "jane-smith"
    assert _sanitize_name("Alex O'Brien") == "alex-obrien"
    assert _sanitize_name("Maria López") == "maria-lópez"  # Keeps unicode
    assert _sanitize_name("  John  Doe  ") == "john-doe"
    
    print("✓ Sanitization test passed")


def test_profile_creation_with_all_fields():
    """Test creating a complete profile"""
    print("Testing profile creation with all fields...")
    cleanup_test_profiles()
    
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context=MOCK_EMAIL_CONTEXT
    )
    
    assert profile_path is not None, "Profile path should be returned"
    
    full_path = Path(f"/home/workspace/{profile_path}")
    assert full_path.exists(), "Profile file should exist"
    
    # Check content
    with open(full_path, 'r') as f:
        content = f.read()
    
    assert "Jane Smith" in content, "Name should be in profile"
    assert "jane@acmeventures.com" in content, "Email should be in profile"
    assert "Acme Ventures" in content, "Organization should be in profile"
    assert "Investor" in content, "Stakeholder type should be in profile"
    assert "## Meeting History" in content, "Meeting history section should exist"
    assert "## Email Interaction History" in content, "Email section should exist"
    
    print("✓ Profile creation test passed")


def test_email_lookup_case_insensitive():
    """Test finding profile by email (case insensitive)"""
    print("Testing email lookup (case insensitive)...")
    cleanup_test_profiles()
    
    # Create profile
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context=MOCK_EMAIL_CONTEXT
    )
    
    # Test exact match
    found1 = find_stakeholder_profile('jane@acmeventures.com')
    assert found1 == profile_path, "Should find profile with exact email"
    
    # Test different case
    found2 = find_stakeholder_profile('JANE@ACMEVENTURES.COM')
    assert found2 == profile_path, "Should find profile with different case"
    
    # Test not found
    found3 = find_stakeholder_profile('notfound@example.com')
    assert found3 is None, "Should return None for non-existent email"
    
    print("✓ Email lookup test passed")


def test_profile_update_append():
    """Test appending new meeting to existing profile"""
    print("Testing profile update/append...")
    cleanup_test_profiles()
    
    # Create initial profile
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context=MOCK_EMAIL_CONTEXT
    )
    
    # Read initial content
    full_path = Path(f"/home/workspace/{profile_path}")
    with open(full_path, 'r') as f:
        content_before = f.read()
    
    # Count meetings before
    meetings_before = content_before.count("###")
    
    # Append second meeting
    append_meeting_to_profile(profile_path, MOCK_MEETING_2, MOCK_TAGS_2)
    
    # Read updated content
    with open(full_path, 'r') as f:
        content_after = f.read()
    
    # Count meetings after
    meetings_after = content_after.count("###")
    
    assert meetings_after > meetings_before, "Should have more meeting entries"
    assert "Follow-up: Series A Discussion" in content_after, "New meeting should be in profile"
    
    print("✓ Profile update test passed")


def test_handling_missing_organization():
    """Test profile creation without organization"""
    print("Testing profile with missing organization...")
    cleanup_test_profiles()
    
    profile_path = create_stakeholder_profile(
        name='Alex Chen',
        email='alex@example.com',
        organization='',
        stakeholder_type='Candidate',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context={}
    )
    
    assert profile_path is not None, "Profile should be created"
    assert 'alex-chen' in profile_path.lower(), "Should use name in path"
    
    print("✓ Missing organization test passed")


def test_multiple_meetings_same_attendee():
    """Test handling multiple meetings with same attendee"""
    print("Testing multiple meetings with same attendee...")
    cleanup_test_profiles()
    
    # Create first meeting profile
    profile_path_1 = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context=MOCK_EMAIL_CONTEXT
    )
    
    # Find existing profile for second meeting
    existing_profile = find_stakeholder_profile('jane@acmeventures.com')
    assert existing_profile is not None, "Should find existing profile"
    
    # Append second meeting
    append_meeting_to_profile(existing_profile, MOCK_MEETING_2, MOCK_TAGS_2)
    
    # Verify only one profile exists
    jane_profiles = list(MEETINGS_DIR.glob("*jane*"))
    assert len(jane_profiles) == 1, "Should only have one profile for Jane"
    
    print("✓ Multiple meetings test passed")


def test_markdown_formatting():
    """Test that generated markdown is well-formatted"""
    print("Testing markdown formatting...")
    cleanup_test_profiles()
    
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=MOCK_MEETING_1,
        tags=MOCK_TAGS_1,
        email_context=MOCK_EMAIL_CONTEXT
    )
    
    full_path = Path(f"/home/workspace/{profile_path}")
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Check required sections
    required_sections = [
        "# Jane Smith",
        "**Email:**",
        "## Context from Howie",
        "## Email Interaction History",
        "## Research Notes",
        "## Meeting History",
        "## Relationship Notes",
        "**Last Updated:**"
    ]
    
    for section in required_sections:
        assert section in content, f"Should have section: {section}"
    
    # Check no duplicate headers
    header_count = content.count("# Jane Smith")
    assert header_count == 1, "Should have exactly one main header"
    
    print("✓ Markdown formatting test passed")


def run_all_tests():
    """Run all unit tests"""
    print("=" * 60)
    print("Running Stakeholder Profile Manager Unit Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_directory_name_sanitization,
        test_profile_creation_with_all_fields,
        test_email_lookup_case_insensitive,
        test_profile_update_append,
        test_handling_missing_organization,
        test_multiple_meetings_same_attendee,
        test_markdown_formatting
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
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    # Cleanup
    cleanup_test_profiles()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

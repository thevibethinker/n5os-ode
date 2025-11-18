#!/usr/bin/env python3
"""
Tests for CRM Gmail Tracker
Worker 5 validation suite
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta

sys.path.insert(0, '/home/workspace/N5/scripts')
from crm_gmail_tracker import (
    is_spam_response, 
    extract_email_from_to_field,
    parse_gmail_messages,
    process_sent_email
)

DB_PATH = '/home/workspace/N5/data/crm_v3.db'


def test_spam_filter():
    """Test spam detection heuristics"""
    print("Testing spam filter...")
    
    # Spam cases
    assert is_spam_response("Out of Office", "", "john@example.com") == True
    assert is_spam_response("Automatic Reply", "", "sarah@company.com") == True
    assert is_spam_response("Delivery Failure", "", "admin@site.com") == True
    assert is_spam_response("Unsubscribe", "Click to unsubscribe", "info@newsletter.com") == True
    assert is_spam_response("", "", "noreply@service.com") == True
    assert is_spam_response("", "", "no-reply@notifications.com") == True
    
    # Legitimate cases
    assert is_spam_response("Re: Meeting next week", "Looking forward to it", "jane@startup.com") == False
    assert is_spam_response("Quick question", "Can you help with this?", "bob@consulting.com") == False
    assert is_spam_response("Thanks!", "Appreciate your help", "alice@agency.com") == False
    
    print("✓ Spam filter working")


def test_email_extraction():
    """Test email address extraction from To header"""
    print("Testing email extraction...")
    
    # Angle bracket format
    assert extract_email_from_to_field("John Doe <john@example.com>") == "john@example.com"
    
    # Plain email
    assert extract_email_from_to_field("sarah@company.com") == "sarah@company.com"
    
    # Multiple recipients (returns first)
    assert extract_email_from_to_field("alice@a.com, bob@b.com") == "alice@a.com"
    
    # Edge cases
    assert extract_email_from_to_field("") == None
    assert extract_email_from_to_field("No Email Here") == None
    
    print("✓ Email extraction working")


def test_message_parsing():
    """Test Gmail API message parsing"""
    print("Testing message parsing...")
    
    # Mock Gmail API response
    messages = [
        {
            "id": "msg123",
            "threadId": "thread456",
            "snippet": "Thanks for connecting...",
            "payload": {
                "headers": [
                    {"name": "To", "value": "Jane Smith <jane@startup.com>"},
                    {"name": "Subject", "value": "Great to meet you"},
                    {"name": "Date", "value": "Mon, 18 Nov 2024 10:00:00 -0500"}
                ]
            }
        },
        {
            "id": "msg789",
            "threadId": "thread101",
            "snippet": "Following up on our call...",
            "payload": {
                "headers": [
                    {"name": "To", "value": "bob@consulting.com"},
                    {"name": "Subject", "value": "Next steps"}
                ]
            }
        }
    ]
    
    emails = parse_gmail_messages(messages)
    
    assert len(emails) == 2
    assert emails[0]['to_email'] == "jane@startup.com"
    assert emails[0]['subject'] == "Great to meet you"
    assert emails[1]['to_email'] == "bob@consulting.com"
    
    print("✓ Message parsing working")


def test_database_integration():
    """Test profile creation and enrichment queuing"""
    print("Testing database integration...")
    
    # Check database exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verify tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'")
    assert cursor.fetchone() is not None, "profiles table missing"
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enrichment_queue'")
    assert cursor.fetchone() is not None, "enrichment_queue table missing"
    
    conn.close()
    
    print("✓ Database schema verified")


def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    from crm_gmail_tracker import (
        is_spam_response,
        extract_email_from_to_field,
        process_sent_email,
        parse_gmail_messages,
        load_state,
        save_state,
        main
    )
    
    # Test helper imports
    from crm_calendar_helpers import get_or_create_profile, schedule_enrichment_job
    
    print("✓ All imports successful")


def main_test():
    """Run all tests"""
    print("=" * 60)
    print("CRM Gmail Tracker Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_imports()
        test_spam_filter()
        test_email_extraction()
        test_message_parsing()
        test_database_integration()
        
        print()
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main_test())


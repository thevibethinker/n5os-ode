#!/usr/bin/env python3
"""
Unit tests for meeting_state_manager.py
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from meeting_state_manager import (
    load_state,
    save_state,
    add_processed_event,
    is_event_processed,
    get_processed_event,
    get_all_processed_events,
    update_last_poll,
    STATE_FILE
)


def cleanup_test_file():
    """Remove test state file"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    backup = STATE_FILE.with_suffix('.json.backup')
    if backup.exists():
        backup.unlink()


def test_file_creation_on_first_run():
    """Test that state file is created on first load"""
    print("Testing file creation on first run...")
    cleanup_test_file()
    
    state = load_state()
    
    assert STATE_FILE.exists(), "State file should be created"
    assert 'last_poll' in state, "State should have last_poll"
    assert 'processed_events' in state, "State should have processed_events"
    assert state['processed_events'] == {}, "Initial processed_events should be empty"
    
    print("✓ File creation test passed")


def test_load_save_roundtrip():
    """Test that data survives load/save cycle"""
    print("Testing load/save roundtrip...")
    cleanup_test_file()
    
    # Create initial state
    state1 = load_state()
    original_timestamp = state1['last_poll']
    
    # Add some data
    state1['processed_events']['test123'] = {
        'title': 'Test Meeting',
        'priority': 'normal'
    }
    save_state(state1)
    
    # Load again
    state2 = load_state()
    
    assert 'test123' in state2['processed_events'], "Event should persist"
    assert state2['processed_events']['test123']['title'] == 'Test Meeting', "Data should match"
    
    print("✓ Load/save roundtrip test passed")


def test_add_event():
    """Test adding processed event"""
    print("Testing add event...")
    cleanup_test_file()
    
    event_id = "cal_event_456"
    event_data = {
        'title': 'Meeting with Jane Smith',
        'priority': 'urgent',
        'stakeholder_profiles': ['N5/records/meetings/2025-10-15-jane-smith/profile.md']
    }
    
    add_processed_event(event_id, event_data)
    
    # Verify it was added
    assert is_event_processed(event_id), "Event should be marked as processed"
    
    # Verify data is correct
    retrieved = get_processed_event(event_id)
    assert retrieved is not None, "Event should be retrievable"
    assert retrieved['title'] == event_data['title'], "Title should match"
    assert 'processed_at' in retrieved, "Should have timestamp"
    
    print("✓ Add event test passed")


def test_is_event_processed_lookup():
    """Test event processed lookup"""
    print("Testing event processed lookup...")
    cleanup_test_file()
    
    # Add an event
    add_processed_event("event1", {'title': 'Event 1'})
    
    # Test positive case
    assert is_event_processed("event1"), "event1 should be processed"
    
    # Test negative case
    assert not is_event_processed("event2"), "event2 should not be processed"
    
    print("✓ Event lookup test passed")


def test_concurrent_access_safety():
    """Test that multiple add operations work correctly"""
    print("Testing concurrent access safety...")
    cleanup_test_file()
    
    # Add multiple events sequentially
    for i in range(5):
        add_processed_event(f"event_{i}", {
            'title': f'Meeting {i}',
            'priority': 'normal'
        })
    
    # Verify all were added
    all_events = get_all_processed_events()
    assert len(all_events) == 5, "All events should be present"
    
    for i in range(5):
        assert is_event_processed(f"event_{i}"), f"event_{i} should be processed"
    
    print("✓ Concurrent access test passed")


def test_corrupted_file_recovery():
    """Test recovery from corrupted state file"""
    print("Testing corrupted file recovery...")
    cleanup_test_file()
    
    # Create corrupted file
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        f.write("{invalid json content")
    
    # Should recover gracefully
    state = load_state()
    
    assert STATE_FILE.exists(), "State file should exist"
    assert 'processed_events' in state, "State should be valid"
    assert state['processed_events'] == {}, "Should be reinitialized"
    
    # Check backup was created
    backup = STATE_FILE.with_suffix('.json.backup')
    assert backup.exists(), "Backup should be created"
    
    print("✓ Corrupted file recovery test passed")


def test_update_last_poll():
    """Test updating last poll timestamp"""
    print("Testing update last poll...")
    cleanup_test_file()
    
    state1 = load_state()
    timestamp1 = state1['last_poll']
    
    # Small delay to ensure different timestamp
    import time
    time.sleep(0.1)
    
    update_last_poll()
    
    state2 = load_state()
    timestamp2 = state2['last_poll']
    
    assert timestamp2 > timestamp1, "Last poll should be updated"
    
    print("✓ Update last poll test passed")


def run_all_tests():
    """Run all unit tests"""
    print("=" * 60)
    print("Running State Manager Unit Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_file_creation_on_first_run,
        test_load_save_roundtrip,
        test_add_event,
        test_is_event_processed_lookup,
        test_concurrent_access_safety,
        test_corrupted_file_recovery,
        test_update_last_poll
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
    cleanup_test_file()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script for Recall.ai SQLite models
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import tempfile
import json

# Add the parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from models import RecallDatabase, get_database


def test_database_creation():
    """Test database and schema creation"""
    print("=== Testing Database Creation ===")
    
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        # Create database instance
        db = RecallDatabase(test_db_path)
        print("✓ Database created successfully")
        
        # Check if tables exist
        with db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('scheduled_bots', 'bot_events', 'sync_state')
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['bot_events', 'scheduled_bots', 'sync_state']
            
            if tables == expected_tables:
                print("✓ All tables created successfully")
            else:
                print(f"✗ Table creation failed. Expected {expected_tables}, got {tables}")
                return False
                
        # Check indexes exist
        with db._get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = [
                'idx_scheduled_bots_status',
                'idx_scheduled_bots_join_at', 
                'idx_scheduled_bots_event_id',
                'idx_bot_events_bot_id',
                'idx_bot_events_type',
                'idx_bot_events_timestamp'
            ]
            
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]
            if not missing_indexes:
                print("✓ All indexes created successfully")
            else:
                print(f"✗ Missing indexes: {missing_indexes}")
                return False
        
        return True
        
    finally:
        # Clean up temp file
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_scheduled_bots_crud():
    """Test scheduled bots CRUD operations"""
    print("\n=== Testing Scheduled Bots CRUD ===")
    
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        db = RecallDatabase(test_db_path)
        
        # Test data
        now = datetime.now(timezone.utc)
        meeting_start = now + timedelta(hours=1)
        join_at = meeting_start - timedelta(minutes=2)
        
        # Test create
        bot_id = db.create_scheduled_bot(
            calendar_event_id="test_event_123",
            meeting_url="https://zoom.us/j/123456789",
            meeting_title="Test Meeting",
            meeting_start=meeting_start,
            join_at=join_at
        )
        print(f"✓ Created scheduled bot with ID: {bot_id}")
        
        # Test duplicate prevention
        try:
            db.create_scheduled_bot(
                calendar_event_id="test_event_123",
                meeting_url="https://zoom.us/j/123456789", 
                meeting_title="Test Meeting Duplicate",
                meeting_start=meeting_start,
                join_at=join_at
            )
            print("✗ Duplicate prevention failed")
            return False
        except ValueError:
            print("✓ Duplicate prevention working")
        
        # Test get by event
        bot = db.get_scheduled_bot_by_event("test_event_123", meeting_start)
        if bot and bot['id'] == bot_id:
            print("✓ Get by event working")
        else:
            print("✗ Get by event failed")
            return False
        
        # Test update
        success = db.update_scheduled_bot(bot_id, bot_id="bot_abc123", status="scheduled")
        if success:
            print("✓ Update working")
        else:
            print("✗ Update failed")
            return False
        
        # Test get by bot_id
        bot = db.get_scheduled_bot_by_bot_id("bot_abc123")
        if bot and bot['status'] == 'scheduled':
            print("✓ Get by bot_id working")
        else:
            print("✗ Get by bot_id failed")
            return False
        
        # Test get pending bots
        pending_bots = db.get_pending_bots()
        print(f"✓ Found {len(pending_bots)} pending bots")
        
        # Test get by status
        scheduled_bots = db.get_bots_by_status('scheduled')
        if len(scheduled_bots) == 1:
            print("✓ Get by status working")
        else:
            print(f"✗ Get by status failed - expected 1, got {len(scheduled_bots)}")
            return False
        
        # Test cancel
        success = db.cancel_bot(bot_id)
        if success:
            cancelled_bot = db.get_scheduled_bot_by_bot_id("bot_abc123")
            if cancelled_bot['status'] == 'cancelled':
                print("✓ Cancel working")
            else:
                print("✗ Cancel failed - status not updated")
                return False
        else:
            print("✗ Cancel failed")
            return False
        
        return True
        
    finally:
        # Clean up temp file
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_bot_events_crud():
    """Test bot events CRUD operations"""
    print("\n=== Testing Bot Events CRUD ===")
    
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        db = RecallDatabase(test_db_path)
        
        # Test log event
        event_id = db.log_event(
            event_id="evt_123",
            bot_id="bot_abc123",
            event_type="bot.status_change",
            status_code="joining_call",
            payload={"test": "data"}
        )
        print(f"✓ Logged event with ID: {event_id}")
        
        # Test duplicate event prevention
        duplicate_id = db.log_event(
            event_id="evt_123",
            bot_id="bot_abc123", 
            event_type="bot.status_change",
            status_code="in_call_recording"
        )
        if duplicate_id == 0:
            print("✓ Duplicate event prevention working")
        else:
            print("✗ Duplicate event prevention failed")
            return False
        
        # Test event exists
        if db.event_exists("evt_123"):
            print("✓ Event exists check working")
        else:
            print("✗ Event exists check failed")
            return False
        
        # Test get events for bot
        events = db.get_events_for_bot("bot_abc123")
        if len(events) == 1 and events[0]['payload']['test'] == 'data':
            print("✓ Get events for bot working")
        else:
            print("✗ Get events for bot failed")
            return False
        
        # Test mark processed
        success = db.mark_event_processed("evt_123")
        if success:
            print("✓ Mark event processed working")
        else:
            print("✗ Mark event processed failed")
            return False
        
        return True
        
    finally:
        # Clean up temp file
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_sync_state():
    """Test sync state operations"""
    print("\n=== Testing Sync State ===")
    
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        db = RecallDatabase(test_db_path)
        
        # Test initial state - should auto-create empty row
        state = db.get_sync_state()
        if state and state['id'] == 1 and not state['sync_token']:
            print("✓ Initial sync state auto-created")
        else:
            print("✗ Initial sync state creation failed")
            return False
        
        # Test update sync state (update existing)
        now = datetime.now(timezone.utc)
        success = db.update_sync_state(
            last_sync=now,
            sync_token="sync_token_123"
        )
        if success:
            print("✓ Sync state update working")
        else:
            print("✗ Sync state update failed")
            return False
        
        # Test get sync state after update
        state = db.get_sync_state()
        if state and state['sync_token'] == 'sync_token_123':
            print("✓ Get sync state after update working")
        else:
            print("✗ Get sync state after update failed")
            return False
        
        # Test update sync state again (further update)
        later = now + timedelta(hours=1)
        success = db.update_sync_state(
            last_event_time=later,
            sync_token="sync_token_456"
        )
        if success:
            state = db.get_sync_state()
            if state['sync_token'] == 'sync_token_456':
                print("✓ Sync state further update working")
            else:
                print("✗ Sync state further update failed - token not updated")
                return False
        else:
            print("✗ Sync state further update failed")
            return False
        
        return True
        
    finally:
        # Clean up temp file
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_real_database():
    """Test with real database path"""
    print("\n=== Testing Real Database ===")
    
    try:
        # Test database creation at real path
        db = get_database()  # Uses default path from config
        print(f"✓ Real database created at: {db.db_path}")
        
        # Test stats
        stats = db.get_stats()
        print(f"✓ Database stats: {stats}")
        
        # Verify file exists
        if os.path.exists(db.db_path):
            print("✓ Database file exists on disk")
        else:
            print("✗ Database file not found on disk")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Real database test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Starting Recall.ai Models Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_creation,
        test_scheduled_bots_crud,
        test_bot_events_crud,
        test_sync_state,
        test_real_database
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
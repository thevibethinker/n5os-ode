#!/usr/bin/env python3
"""
Unit tests for conversation_sync.py

Run with: python3 test_conversation_sync.py
"""

import unittest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from conversation_sync import ConversationSync


class TestConversationSync(unittest.TestCase):
    """Test ConversationSync functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary directories
        self.temp_workspace = Path(tempfile.mkdtemp())
        self.temp_db = Path(tempfile.mktemp(suffix=".db"))
        
        # Override paths for testing
        ConversationSync.WORKSPACE_BASE = self.temp_workspace
        ConversationSync.DB_PATH = self.temp_db
        
        self.syncer = ConversationSync()
    
    def tearDown(self):
        """Clean up after each test."""
        if self.syncer:
            self.syncer.close()
        
        if self.temp_workspace.exists():
            shutil.rmtree(self.temp_workspace)
        
        if self.temp_db.exists():
            self.temp_db.unlink()
    
    def create_test_session_state(self, convo_id: str, type: str = "build", status: str = "active"):
        """Helper to create a test SESSION_STATE.md file."""
        workspace = self.temp_workspace / convo_id
        workspace.mkdir(parents=True, exist_ok=True)
        
        session_state = workspace / "SESSION_STATE.md"
        session_state.write_text(f"""---
conversation_id: {convo_id}
type: {type}
mode: testing
status: {status}
created: 2025-11-11T10:00:00Z
last_updated: 2025-11-11T11:00:00Z
---

# SESSION STATE

## Metadata
- **Type:** {type.title()}
- **Mode:** testing
- **Focus:** Test conversation focus
- **Objective:** Test objective
- **Status:** {status}

## Progress
- **Overall:** 50%

## Tags
#test #unit-test #sync
""")
        return session_state
    
    def test_db_schema_creation(self):
        """Test that database schema is created correctly."""
        cursor = self.syncer.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
        )
        self.assertIsNotNone(cursor.fetchone())
    
    def test_parse_session_state_success(self):
        """Test parsing a valid SESSION_STATE.md file."""
        convo_id = "con_TEST001"
        self.create_test_session_state(convo_id)
        
        data = self.syncer.parse_session_state(convo_id)
        
        self.assertIsNotNone(data)
        self.assertEqual(data["id"], convo_id)
        self.assertEqual(data["type"], "build")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["focus"], "Test conversation focus")
        self.assertEqual(data["objective"], "Test objective")
        self.assertEqual(data["progress_pct"], 50)
    
    def test_parse_session_state_missing(self):
        """Test parsing when SESSION_STATE.md doesn't exist."""
        data = self.syncer.parse_session_state("con_NONEXISTENT")
        self.assertIsNone(data)
    
    def test_sync_conversation_insert(self):
        """Test syncing a new conversation."""
        convo_id = "con_TEST002"
        self.create_test_session_state(convo_id)
        
        success = self.syncer.sync_conversation(convo_id)
        
        self.assertTrue(success)
        
        # Verify it's in the database
        cursor = self.syncer.conn.execute("SELECT * FROM conversations WHERE id = ?", (convo_id,))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["id"], convo_id)
        self.assertEqual(row["type"], "build")
        self.assertEqual(row["status"], "active")
    
    def test_sync_conversation_update(self):
        """Test syncing updates to an existing conversation."""
        convo_id = "con_TEST003"
        
        # First sync
        self.create_test_session_state(convo_id, type="build", status="active")
        self.syncer.sync_conversation(convo_id)
        
        # Update and sync again
        self.create_test_session_state(convo_id, type="build", status="complete")
        self.syncer.sync_conversation(convo_id)
        
        # Verify update
        cursor = self.syncer.conn.execute("SELECT status FROM conversations WHERE id = ?", (convo_id,))
        row = cursor.fetchone()
        
        self.assertEqual(row["status"], "complete")
    
    def test_sync_all(self):
        """Test syncing multiple conversations."""
        # Create multiple test conversations
        self.create_test_session_state("con_TEST004", "build", "active")
        self.create_test_session_state("con_TEST005", "research", "complete")
        self.create_test_session_state("con_TEST006", "discussion", "active")
        
        count = self.syncer.sync_all()
        
        self.assertEqual(count, 3)
        
        # Verify all are in database
        cursor = self.syncer.conn.execute("SELECT COUNT(*) as cnt FROM conversations")
        row = cursor.fetchone()
        self.assertEqual(row["cnt"], 3)
    
    def test_query_by_type(self):
        """Test querying conversations by type."""
        self.create_test_session_state("con_TEST007", "build", "active")
        self.create_test_session_state("con_TEST008", "research", "active")
        self.create_test_session_state("con_TEST009", "build", "complete")
        
        self.syncer.sync_all()
        
        results = self.syncer.query(type="build")
        
        self.assertEqual(len(results), 2)
        for conv in results:
            self.assertEqual(conv["type"], "build")
    
    def test_query_by_status(self):
        """Test querying conversations by status."""
        self.create_test_session_state("con_TEST010", "build", "active")
        self.create_test_session_state("con_TEST011", "research", "complete")
        self.create_test_session_state("con_TEST012", "discussion", "active")
        
        self.syncer.sync_all()
        
        results = self.syncer.query(status="active")
        
        self.assertEqual(len(results), 2)
        for conv in results:
            self.assertEqual(conv["status"], "active")
    
    def test_query_combined_filters(self):
        """Test querying with multiple filters."""
        self.create_test_session_state("con_TEST013", "build", "active")
        self.create_test_session_state("con_TEST014", "build", "complete")
        self.create_test_session_state("con_TEST015", "research", "active")
        
        self.syncer.sync_all()
        
        results = self.syncer.query(type="build", status="active")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "con_TEST013")
    
    def test_tags_extraction(self):
        """Test that tags are extracted and stored as JSON."""
        convo_id = "con_TEST016"
        self.create_test_session_state(convo_id)
        
        self.syncer.sync_conversation(convo_id)
        
        cursor = self.syncer.conn.execute("SELECT tags FROM conversations WHERE id = ?", (convo_id,))
        row = cursor.fetchone()
        
        self.assertIsNotNone(row["tags"])
        self.assertIn("#test", row["tags"])
    
    def test_progress_extraction(self):
        """Test that progress percentage is extracted correctly."""
        convo_id = "con_TEST017"
        self.create_test_session_state(convo_id)
        
        self.syncer.sync_conversation(convo_id)
        
        cursor = self.syncer.conn.execute("SELECT progress_pct FROM conversations WHERE id = ?", (convo_id,))
        row = cursor.fetchone()
        
        self.assertEqual(row["progress_pct"], 50)
    
    def test_title_generation(self):
        """Test that title is generated from focus or objective."""
        convo_id = "con_TEST018"
        self.create_test_session_state(convo_id)
        
        data = self.syncer.parse_session_state(convo_id)
        
        self.assertEqual(data["title"], "Test conversation focus")


def run_tests():
    """Run all tests and print results."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConversationSync)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)


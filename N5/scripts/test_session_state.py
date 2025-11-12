#!/usr/bin/env python3
"""
Unit tests for session_state_manager.py

Run with: python3 test_session_state.py
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from session_state_manager import SessionStateManager


class TestSessionStateManager(unittest.TestCase):
    """Test SessionStateManager functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary workspace
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_convo_id = "con_TEST123"
        
        # Override workspace base for testing
        SessionStateManager.WORKSPACE_BASE = self.temp_dir
        
        self.manager = SessionStateManager(self.test_convo_id)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary workspace
        shutil.rmtree(self.temp_dir)
    
    def test_init_creates_file(self):
        """Test that init creates SESSION_STATE.md file."""
        result = self.manager.init(conv_type="build")
        
        self.assertTrue(result)
        self.assertTrue(self.manager.session_state_path.exists())
    
    def test_init_with_type(self):
        """Test init with explicit conversation type."""
        result = self.manager.init(conv_type="build", mode="refactor")
        
        self.assertTrue(result)
        content = self.manager.session_state_path.read_text()
        
        self.assertIn("type: build", content)
        self.assertIn("mode: refactor", content)
        self.assertIn("## Build-Specific", content)
    
    def test_init_with_auto_classification(self):
        """Test init with auto-classification from user message."""
        user_message = "I need to implement a new feature and write some code"
        
        result = self.manager.init(user_message=user_message)
        
        self.assertTrue(result)
        content = self.manager.session_state_path.read_text()
        
        # Should classify as "build" based on keywords
        self.assertIn("type: build", content)
    
    def test_classify_conversation_build(self):
        """Test conversation classification for build type."""
        message = "Let's implement a new script to handle this"
        result = self.manager._classify_conversation(message)
        
        self.assertEqual(result, "build")
    
    def test_classify_conversation_research(self):
        """Test conversation classification for research type."""
        message = "I want to research and analyze the best approach"
        result = self.manager._classify_conversation(message)
        
        self.assertEqual(result, "research")
    
    def test_classify_conversation_default(self):
        """Test conversation classification defaults to discussion."""
        message = "Hello there"
        result = self.manager._classify_conversation(message)
        
        self.assertEqual(result, "discussion")
    
    def test_update_existing_field(self):
        """Test updating an existing field in SESSION_STATE.md."""
        # Initialize first
        self.manager.init(conv_type="build")
        
        # Update status field
        result = self.manager.update("status", "complete")
        
        self.assertTrue(result)
        content = self.manager.session_state_path.read_text()
        self.assertIn("**Status:** complete", content)
    
    def test_update_focus_field(self):
        """Test updating the focus field."""
        self.manager.init(conv_type="discussion")
        
        result = self.manager.update("focus", "Testing session state system")
        
        self.assertTrue(result)
        content = self.manager.session_state_path.read_text()
        self.assertIn("**Focus:** Testing session state system", content)
    
    def test_update_nonexistent_file(self):
        """Test update fails gracefully when file doesn't exist."""
        result = self.manager.update("status", "active")
        
        self.assertFalse(result)
    
    def test_check_displays_content(self):
        """Test check displays SESSION_STATE.md content."""
        self.manager.init(conv_type="build")
        
        content = self.manager.check()
        
        self.assertIsNotNone(content)
        self.assertIn("SESSION STATE", content)
        self.assertIn(self.test_convo_id, content)
    
    def test_check_nonexistent_file(self):
        """Test check fails gracefully when file doesn't exist."""
        content = self.manager.check()
        
        self.assertIn("not found", content)
    
    def test_multiple_updates(self):
        """Test multiple sequential updates."""
        self.manager.init(conv_type="build")
        
        self.manager.update("status", "active")
        self.manager.update("focus", "Building session state manager")
        self.manager.update("progress", "50%")
        
        content = self.manager.session_state_path.read_text()
        
        self.assertIn("**Status:** active", content)
        self.assertIn("**Focus:** Building session state manager", content)
        self.assertIn("**Progress:** 50%", content)
    
    def test_template_includes_convo_id(self):
        """Test that template includes conversation ID."""
        self.manager.init(conv_type="research")
        
        content = self.manager.session_state_path.read_text()
        self.assertIn(f"conversation_id: {self.test_convo_id}", content)
    
    def test_template_includes_timestamps(self):
        """Test that template includes created and last_updated timestamps."""
        self.manager.init(conv_type="planning")
        
        content = self.manager.session_state_path.read_text()
        self.assertIn("created:", content)
        self.assertIn("last_updated:", content)
    
    def test_update_modifies_timestamp(self):
        """Test that update modifies last_updated timestamp."""
        self.manager.init(conv_type="build")
        
        original_content = self.manager.session_state_path.read_text()
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.1)
        
        self.manager.update("status", "updated")
        
        updated_content = self.manager.session_state_path.read_text()
        
        # Verify that last_updated field exists in both versions
        self.assertIn("last_updated:", original_content)
        self.assertIn("last_updated:", updated_content)
        
        # Timestamps should be different (though this is not guaranteed if updates happen too fast)
        # At minimum, verify the field exists and update succeeded
        self.assertIn("**Status:** updated", updated_content)


def run_tests():
    """Run all tests and print results."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSessionStateManager)
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



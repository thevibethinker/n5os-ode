#!/usr/bin/env python3
"""
Unit tests for SessionStateManager API methods.

Tests the new read API:
- get_field()
- get_metadata()
- get_section()
- append_to_section()
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session_state_manager import SessionStateManager


class TestSessionStateManagerAPI(unittest.TestCase):
    """Test SessionStateManager read/write API methods."""
    
    def setUp(self):
        """Create temporary workspace for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_base = Path(self.temp_dir)
        
        # Patch the WORKSPACE_BASE for testing
        SessionStateManager.WORKSPACE_BASE = self.workspace_base
        
        # Create test conversation
        self.test_convo_id = "con_TEST123"
        self.manager = SessionStateManager(self.test_convo_id)
        
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_session_state(self):
        """Test that init creates SESSION_STATE.md with correct structure."""
        success = self.manager.init(conv_type="build")
        
        self.assertTrue(success)
        self.assertTrue(self.manager.session_state_path.exists())
        
        content = self.manager.session_state_path.read_text()
        self.assertIn("conversation_id: con_TEST123", content)
        self.assertIn("type: build", content)
        self.assertIn("## Metadata", content)
    
    def test_get_field_basic(self):
        """Test get_field() retrieves field values correctly."""
        self.manager.init(conv_type="research", mode="deep_dive")
        
        # Test retrieving fields
        self.assertEqual(self.manager.get_field("Type"), "Research")
        self.assertEqual(self.manager.get_field("Mode"), "deep_dive")
        self.assertEqual(self.manager.get_field("Status"), "active")
        
        # Test case insensitivity
        self.assertEqual(self.manager.get_field("type"), "Research")
        self.assertEqual(self.manager.get_field("STATUS"), "active")
    
    def test_get_field_not_found(self):
        """Test get_field() returns 'Not specified' for missing fields."""
        self.manager.init(conv_type="build")
        
        result = self.manager.get_field("NonexistentField")
        self.assertEqual(result, "Not specified")
    
    def test_get_field_before_init(self):
        """Test get_field() handles missing SESSION_STATE.md gracefully."""
        # Don't initialize, just try to read
        result = self.manager.get_field("Focus")
        self.assertEqual(result, "Not specified")
    
    def test_get_metadata(self):
        """Test get_metadata() returns all metadata fields."""
        self.manager.init(conv_type="build", mode="refactor")
        
        # Update some fields
        self.manager.update("Focus", "Refactoring spawn_worker.py")
        self.manager.update("Status", "in_progress")
        
        metadata = self.manager.get_metadata()
        
        self.assertIn("focus", metadata)
        self.assertIn("objective", metadata)
        self.assertIn("status", metadata)
        self.assertIn("type", metadata)
        self.assertIn("mode", metadata)
        
        self.assertEqual(metadata["focus"], "Refactoring spawn_worker.py")
        self.assertEqual(metadata["type"], "Build")
        self.assertEqual(metadata["status"], "in_progress")
    
    def test_get_section_basic(self):
        """Test get_section() extracts section content correctly."""
        self.manager.init(conv_type="research")
        
        # Add content to a section
        content = self.manager.session_state_path.read_text()
        content = content.replace(
            "## Topics\n- TBD",
            "## Topics\n- Machine Learning\n- Neural Networks\n- Deep Learning"
        )
        self.manager.session_state_path.write_text(content)
        
        section = self.manager.get_section("Topics")
        
        self.assertIn("Machine Learning", section)
        self.assertIn("Neural Networks", section)
        self.assertIn("Deep Learning", section)
        self.assertNotIn("## Topics", section)  # Header not included
    
    def test_get_section_not_found(self):
        """Test get_section() returns empty string for missing sections."""
        self.manager.init(conv_type="build")
        
        section = self.manager.get_section("NonexistentSection")
        self.assertEqual(section, "")
    
    def test_get_section_stops_at_next_section(self):
        """Test get_section() stops at the next section header."""
        self.manager.init(conv_type="build")
        
        # Get Progress section (should stop at Covered)
        section = self.manager.get_section("Progress")
        
        self.assertIn("Overall", section)
        self.assertIn("Current Phase", section)
        self.assertNotIn("Session initialized", section)  # From Covered section
    
    def test_append_to_section_existing(self):
        """Test append_to_section() adds content to existing section."""
        self.manager.init(conv_type="build")
        
        # Append to Topics section
        success = self.manager.append_to_section("Topics", "- New topic added")
        
        self.assertTrue(success)
        
        section = self.manager.get_section("Topics")
        self.assertIn("New topic added", section)
    
    def test_append_to_section_creates_new(self):
        """Test append_to_section() creates new section if missing."""
        self.manager.init(conv_type="build")
        
        # Append to non-existent section
        success = self.manager.append_to_section("Test Section", "Test content here")
        
        self.assertTrue(success)
        
        content = self.manager.session_state_path.read_text()
        self.assertIn("## Test Section", content)
        self.assertIn("Test content here", content)
    
    def test_append_to_section_multiple_times(self):
        """Test multiple appends to same section."""
        self.manager.init(conv_type="build")
        
        self.manager.append_to_section("Covered", "- First item")
        self.manager.append_to_section("Covered", "- Second item")
        self.manager.append_to_section("Covered", "- Third item")
        
        section = self.manager.get_section("Covered")
        
        self.assertIn("First item", section)
        self.assertIn("Second item", section)
        self.assertIn("Third item", section)
    
    def test_clean_field_value(self):
        """Test _clean_field_value() removes markdown artifacts."""
        # Test with markdown formatting
        self.manager.init(conv_type="build")
        
        # Manually create field with markdown artifacts
        content = self.manager.session_state_path.read_text()
        content = content.replace(
            "- **Focus:** TBD",
            "- **Focus:** **Bold text**"
        )
        self.manager.session_state_path.write_text(content)
        
        focus = self.manager.get_field("Focus")
        
        # Should strip asterisks
        self.assertEqual(focus, "Bold text")
    
    def test_get_objective_with_goal_field(self):
        """Test _get_objective() prioritizes Goal field over Objective field."""
        self.manager.init(conv_type="build")
        
        # Add Goal field to content
        content = self.manager.session_state_path.read_text()
        content = content.replace(
            "## Metadata",
            "## Metadata\n\nGoal: Complete integration by EOD"
        )
        self.manager.session_state_path.write_text(content)
        
        metadata = self.manager.get_metadata()
        
        self.assertEqual(metadata["objective"], "Complete integration by EOD")
    
    def test_get_objective_skips_placeholder(self):
        """Test _get_objective() skips placeholder Goal questions."""
        self.manager.init(conv_type="build")
        
        # Add placeholder Goal
        content = self.manager.session_state_path.read_text()
        content = content.replace(
            "## Metadata",
            "## Metadata\n\nGoal: What should we achieve?"
        )
        self.manager.session_state_path.write_text(content)
        
        # Update Objective field
        self.manager.update("Objective", "Real objective here")
        
        metadata = self.manager.get_metadata()
        
        # Should use Objective, not placeholder Goal
        self.assertEqual(metadata["objective"], "Real objective here")


class TestSessionStateManagerIntegration(unittest.TestCase):
    """Integration tests for SessionStateManager with real workflows."""
    
    def setUp(self):
        """Create temporary workspace for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_base = Path(self.temp_dir)
        
        # Patch the WORKSPACE_BASE for testing
        SessionStateManager.WORKSPACE_BASE = self.workspace_base
        
        self.test_convo_id = "con_INTEGRATION_TEST"
        self.manager = SessionStateManager(self.test_convo_id)
    
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow: init -> update -> read -> append."""
        # 1. Initialize
        self.manager.init(conv_type="build", mode="refactor")
        
        # 2. Update fields
        self.manager.update("Focus", "Testing session state manager")
        self.manager.update("Status", "in_progress")
        
        # 3. Read metadata
        metadata = self.manager.get_metadata()
        self.assertEqual(metadata["focus"], "Testing session state manager")
        self.assertEqual(metadata["status"], "in_progress")
        
        # 4. Append to section
        self.manager.append_to_section("Progress", "- Created tests")
        self.manager.append_to_section("Progress", "- All tests passing")
        
        # 5. Read section
        progress = self.manager.get_section("Progress")
        self.assertIn("Created tests", progress)
        self.assertIn("All tests passing", progress)
        
        # 6. Check file was updated
        self.assertTrue(self.manager.session_state_path.exists())
        content = self.manager.session_state_path.read_text()
        self.assertIn("Testing session state manager", content)
        self.assertIn("All tests passing", content)


if __name__ == "__main__":
    unittest.main()


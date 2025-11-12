#!/usr/bin/env python3
"""
Integration tests for spawn_worker.py using SessionStateManager API.

Tests that spawn_worker correctly:
- Reads parent SESSION_STATE via API
- Updates parent SESSION_STATE via API
- Extracts sections via API
- Handles edge cases gracefully
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from spawn_worker import WorkerSpawner
from session_state_manager import SessionStateManager


class TestSpawnWorkerAPIIntegration(unittest.TestCase):
    """Test spawn_worker integration with SessionStateManager API."""
    
    def setUp(self):
        """Create temporary workspace for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_base = Path(self.temp_dir)
        self.user_workspace = Path(self.temp_dir) / "workspace"
        self.user_workspace.mkdir(parents=True, exist_ok=True)
        
        # Create Records/Temporary for worker assignments
        (self.user_workspace / "Records" / "Temporary").mkdir(parents=True, exist_ok=True)
        
        # Patch paths for testing
        SessionStateManager.WORKSPACE_BASE = self.workspace_base
        
        # Monkey-patch spawn_worker paths
        import spawn_worker
        spawn_worker.WORKSPACE = self.user_workspace
        spawn_worker.CONVERSATION_WORKSPACE_BASE = self.workspace_base
        
        # Create test parent conversation
        self.parent_id = "con_PARENT123"
        self.parent_workspace = self.workspace_base / self.parent_id
        self.parent_workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize parent SESSION_STATE
        self.parent_manager = SessionStateManager(self.parent_id)
        self.parent_manager.init(conv_type="build", mode="integration")
        
        # Set up parent state
        self.parent_manager.update("Focus", "Building worker spawner")
        self.parent_manager.update("Status", "active")
        
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_parent_session_state(self):
        """Test that WorkerSpawner correctly reads parent state via API."""
        spawner = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Test instruction",
            dry_run=True
        )
        
        parent_state = spawner.read_parent_session_state()
        
        self.assertEqual(parent_state["focus"], "Building worker spawner")
        self.assertEqual(parent_state["status"], "active")
        self.assertEqual(parent_state["conversation_type"], "Build")
    
    def test_gather_context_with_timeline(self):
        """Test that gather_context extracts Timeline section via API."""
        # Add Timeline section to parent
        self.parent_manager.append_to_section("Timeline", """
**06:00** - Started integration work
**06:15** - Extended SessionStateManager API
**06:30** - Updated spawn_worker to use API
""")
        
        spawner = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Test instruction",
            dry_run=True
        )
        
        context = spawner.gather_context()
        
        self.assertIn("timeline_summary", context)
        self.assertIn("Started integration work", context["timeline_summary"])
        self.assertIn("Extended SessionStateManager API", context["timeline_summary"])
    
    def test_update_parent_session_state(self):
        """Test that update_parent_session_state uses API correctly."""
        spawner = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Test instruction",
            dry_run=False  # Actually write
        )
        
        # Create fake worker file
        worker_file = self.user_workspace / "Records" / "Temporary" / "WORKER_TEST.md"
        worker_file.write_text("Test content")
        
        # Update parent session state
        success = spawner.update_parent_session_state(worker_file)
        
        self.assertTrue(success)
        
        # Verify via API
        spawned_section = self.parent_manager.get_section("Spawned Workers")
        self.assertIn("WORKER_TEST.md", spawned_section)
        self.assertIn("spawned", spawned_section)
    
    def test_full_spawn_workflow(self):
        """Test complete spawn workflow with API integration."""
        # Add some recent files to parent workspace
        (self.parent_workspace / "test_file.py").write_text("# Test Python file")
        (self.parent_workspace / "notes.md").write_text("# Test notes")
        
        spawner = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Run integration tests",
            dry_run=False
        )
        
        # Run full spawn
        result = spawner.spawn()
        
        self.assertEqual(result, 0)  # Success
        
        # Verify worker assignment was created
        assignment_files = list((self.user_workspace / "Records" / "Temporary").glob("WORKER_ASSIGNMENT_*.md"))
        self.assertEqual(len(assignment_files), 1)
        
        assignment_content = assignment_files[0].read_text()
        
        # Verify assignment includes parent context
        self.assertIn("Building worker spawner", assignment_content)
        self.assertIn("Run integration tests", assignment_content)
        self.assertIn(self.parent_id, assignment_content)
        
        # Verify parent SESSION_STATE was updated
        spawned_section = self.parent_manager.get_section("Spawned Workers")
        self.assertIn(assignment_files[0].name, spawned_section)
    
    def test_spawn_with_empty_focus(self):
        """Test spawn handles empty focus gracefully."""
        # Create parent with empty focus
        empty_parent_id = "con_EMPTY_TEST"
        empty_manager = SessionStateManager(empty_parent_id)
        empty_manager.init(conv_type="discussion")
        
        spawner = WorkerSpawner(
            parent_convo_id=empty_parent_id,
            instruction="Test with empty state",
            dry_run=True
        )
        
        parent_state = spawner.read_parent_session_state()
        
        # Should have default values
        self.assertIn("objective", parent_state)
        self.assertIn("focus", parent_state)
    
    def test_spawn_with_goal_field(self):
        """Test spawn correctly reads Goal field via _get_objective."""
        # Add Goal field to parent
        content = self.parent_manager.session_state_path.read_text()
        content = content.replace(
            "## Metadata",
            "## Metadata\n\nGoal: Complete all tests successfully"
        )
        self.parent_manager.session_state_path.write_text(content)
        
        spawner = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Test with Goal field",
            dry_run=True
        )
        
        parent_state = spawner.read_parent_session_state()
        
        self.assertEqual(parent_state["objective"], "Complete all tests successfully")
    
    def test_multiple_spawns_to_same_parent(self):
        """Test multiple worker spawns update parent correctly."""
        # First spawn
        spawner1 = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="First worker",
            dry_run=False
        )
        spawner1.spawn()
        
        # Second spawn
        spawner2 = WorkerSpawner(
            parent_convo_id=self.parent_id,
            instruction="Second worker",
            dry_run=False
        )
        spawner2.spawn()
        
        # Verify both workers in Spawned Workers section
        spawned_section = self.parent_manager.get_section("Spawned Workers")
        
        # Should have 2 worker entries
        worker_entries = [line for line in spawned_section.split("\n") if "WORKER_ASSIGNMENT" in line]
        self.assertEqual(len(worker_entries), 2)


class TestSpawnWorkerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Create temporary workspace for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_base = Path(self.temp_dir)
        self.user_workspace = Path(self.temp_dir) / "workspace"
        self.user_workspace.mkdir(parents=True, exist_ok=True)
        
        # Patch paths
        SessionStateManager.WORKSPACE_BASE = self.workspace_base
        
        import spawn_worker
        spawn_worker.WORKSPACE = self.user_workspace
        spawn_worker.CONVERSATION_WORKSPACE_BASE = self.workspace_base
    
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_spawn_nonexistent_parent(self):
        """Test spawn fails gracefully for nonexistent parent."""
        spawner = WorkerSpawner(
            parent_convo_id="con_DOESNOTEXIST",
            instruction="Test",
            dry_run=False
        )
        
        result = spawner.spawn()
        
        self.assertEqual(result, 1)  # Failure
    
    def test_spawn_parent_without_session_state(self):
        """Test spawn fails if parent lacks SESSION_STATE.md."""
        # Create parent workspace but no SESSION_STATE
        parent_id = "con_NOSTATE"
        parent_workspace = self.workspace_base / parent_id
        parent_workspace.mkdir(parents=True, exist_ok=True)
        
        spawner = WorkerSpawner(
            parent_convo_id=parent_id,
            instruction="Test",
            dry_run=False
        )
        
        result = spawner.spawn()
        
        self.assertEqual(result, 1)  # Failure


if __name__ == "__main__":
    unittest.main()


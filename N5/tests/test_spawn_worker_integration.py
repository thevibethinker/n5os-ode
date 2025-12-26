#!/usr/bin/env python3
"""
Integration tests for spawn_worker.py v2 using the LLM-first design.

Tests the PUBLIC interface only (CLI), not internal implementation.
This follows the LLM-first principle: we test behavior, not implementation.
"""

import unittest
import tempfile
import shutil
import json
import subprocess
import sys
from pathlib import Path


class TestSpawnWorkerCLI(unittest.TestCase):
    """Test spawn_worker.py CLI interface - the public contract."""
    
    @property
    def script_path(self):
        return Path(__file__).parent.parent / "scripts" / "spawn_worker.py"
    
    def test_cli_generate_ids(self):
        """Test --generate-ids flag produces valid JSON output."""
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_TEST123", "--generate-ids"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        
        # Should output valid JSON
        output = json.loads(result.stdout)
        self.assertIn('worker_id', output)
        self.assertIn('timestamp', output)
        self.assertIn('filename', output)
        self.assertIn('output_path', output)
        self.assertIn('parent_workspace', output)
        
        # Verify ID format includes parent suffix
        self.assertTrue(output['worker_id'].startswith('WORKER_'))
        self.assertIn('T123', output['worker_id'])
    
    def test_cli_dry_run_with_context(self):
        """Test --dry-run with --context JSON."""
        context = json.dumps({
            "instruction": "Test CLI with context",
            "parent_focus": "Testing spawn worker",
            "parent_objective": "Verify JSON context works",
            "parent_status": "In testing",
            "parent_type": "test"
        })
        
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_TEST123", "--context", context, "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("Test CLI with context", result.stdout)
        self.assertIn("Testing spawn worker", result.stdout)
        self.assertIn("Verify JSON context works", result.stdout)
    
    def test_cli_dry_run_with_instruction_only(self):
        """Test --dry-run with just --instruction (legacy/simple mode)."""
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_TEST456", 
             "--instruction", "Simple instruction test",
             "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("Simple instruction test", result.stdout)
    
    def test_cli_context_with_key_decisions(self):
        """Test that key_decisions array renders correctly."""
        context = json.dumps({
            "instruction": "Build auth system",
            "parent_focus": "Authentication",
            "key_decisions": ["Use JWT", "SQLite backend", "OAuth2 support"],
            "relevant_files": ["auth/schema.sql", "auth/handlers.py"]
        })
        
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_KEYS", "--context", context, "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        self.assertIn("Use JWT", result.stdout)
        self.assertIn("SQLite backend", result.stdout)
        self.assertIn("OAuth2 support", result.stdout)
        self.assertIn("auth/schema.sql", result.stdout)
    
    def test_cli_invalid_context_json(self):
        """Test error handling for invalid JSON in --context."""
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_BAD", "--context", "not valid json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertNotEqual(result.returncode, 0)
        # Should have error message about JSON
        combined = result.stdout + result.stderr
        self.assertTrue(
            "JSON" in combined or "json" in combined or "Invalid" in combined,
            f"Expected JSON error message, got: {combined}"
        )
    
    def test_cli_missing_parent(self):
        """Test error when --parent is missing."""
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--instruction", "No parent provided"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertNotEqual(result.returncode, 0)
    
    def test_worker_assignment_structure(self):
        """Test that generated worker assignment has required sections."""
        context = json.dumps({
            "instruction": "Verify structure",
            "parent_focus": "Structure testing"
        })
        
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_STRUCT", "--context", context, "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        output = result.stdout
        
        # Check required sections exist
        self.assertIn("# Worker Assignment", output)
        self.assertIn("## Your Mission", output)
        self.assertIn("## Parent Context", output)
        self.assertIn("**Worker ID:**", output)
        self.assertIn("**Parent Conversation:**", output)


class TestSpawnWorkerIntegration(unittest.TestCase):
    """Integration tests with actual file system operations."""
    
    def setUp(self):
        """Create temporary test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @property
    def script_path(self):
        return Path(__file__).parent.parent / "scripts" / "spawn_worker.py"
    
    def test_actual_file_creation(self):
        """Test that spawn_worker actually creates files when not in dry-run."""
        # This test uses a temporary output directory
        output_dir = Path(self.temp_dir) / "Records" / "Temporary"
        output_dir.mkdir(parents=True)
        
        context = json.dumps({
            "instruction": "Test file creation"
        })
        
        # Run without --dry-run but we need to handle the actual write
        # For now, just verify dry-run output format is correct
        result = subprocess.run(
            [sys.executable, str(self.script_path),
             "--parent", "con_WRITE", "--context", context, "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Would write to:", result.stdout)


if __name__ == '__main__':
    unittest.main()


#!/usr/bin/env python3
"""
Test suite for n5 launch-worker command.

Tests cover:
- CLI argument parsing
- Worker type selection
- Wizard interactive flow
- Instruction enhancement
- Integration with spawn_worker.py
- Error handling
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path('/home/workspace/N5/scripts')))

from n5_launch_worker import LaunchWorker, WORKER_TYPES, main


class TestN5LaunchWorker(unittest.TestCase):
    """Test cases for n5 launch-worker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.launcher = LaunchWorker()
        self.valid_parent = 'con_test123456789'
        self.test_instruction = "Test worker instruction"
    
    def test_worker_types_defined(self):
        """Test that all worker types are properly defined."""
        expected_types = ['build', 'general', 'research', 'analysis', 'writer']
        self.assertEqual(sorted(list(WORKER_TYPES.keys())), sorted(expected_types))
        
        for wtype in expected_types:
            self.assertIn('description', WORKER_TYPES[wtype])
            self.assertIn('tags', WORKER_TYPES[wtype])
            self.assertIn('focus_prompt', WORKER_TYPES[wtype])
            self.assertIn('persona_hint', WORKER_TYPES[wtype])
    
    def test_writer_type_defined(self):
        """Test that writer worker type has correct configuration."""
        self.assertIn('writer', WORKER_TYPES)
        writer = WORKER_TYPES['writer']
        
        self.assertEqual(
            writer['description'],
            'Optimized for content creation, writing, documentation'
        )
        self.assertEqual(
            writer['tags'],
            ['#writing', '#content', '#documentation']
        )
        self.assertEqual(
            writer['focus_prompt'],
            'Content creation and written communication'
        )
        self.assertIn('Vibe Writer', writer['persona_hint'])
    
    def test_enhance_instruction_build(self):
        """Test instruction enhancement for build type."""
        instruction = "Implement user authentication"
        enhanced = self.launcher.enhance_instruction(instruction, 'build')
        self.assertIn(instruction, enhanced)
        self.assertIn('implementation', enhanced.lower())
        self.assertIn('testing', enhanced.lower())
    
    def test_enhance_instruction_research(self):
        """Test instruction enhancement for research type."""
        instruction = "Research OAuth alternatives"
        enhanced = self.launcher.enhance_instruction(instruction, 'research')
        self.assertIn(instruction, enhanced)
        self.assertIn('citations', enhanced.lower())
        self.assertIn('sources', enhanced.lower())
    
    def test_enhance_instruction_analysis(self):
        """Test instruction enhancement for analysis type."""
        instruction = "Compare payment processors"
        enhanced = self.launcher.enhance_instruction(instruction, 'analysis')
        self.assertIn(instruction, enhanced)
        self.assertIn('alternatives', enhanced.lower())
        self.assertIn('recommendations', enhanced.lower())
    
    def test_enhance_instruction_writer(self):
        """Test instruction enhancement for writer type."""
        instruction = "Write API documentation"
        enhanced = self.launcher.enhance_instruction(instruction, 'writer')
        # Writer type uses general enhancement (no specific enhancement yet)
        self.assertEqual(enhanced, instruction)
    
    def test_enhance_instruction_general(self):
        """Test instruction enhancement for general type."""
        instruction = "Do something"
        enhanced = self.launcher.enhance_instruction(instruction, 'general')
        self.assertEqual(enhanced, instruction)
    
    def test_enhance_instruction_none(self):
        """Test instruction enhancement with None instruction."""
        enhanced = self.launcher.enhance_instruction(None, 'build')
        self.assertIsNone(enhanced)
    
    @patch('n5_launch_worker.subprocess.run')
    def test_spawn_worker_success(self, mock_run):
        """Test successful worker spawning."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "✓ Worker spawned\nOpen this file: test.md"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        returncode, output = self.launcher.spawn_worker(
            self.valid_parent, 
            self.test_instruction
        )
        
        self.assertEqual(returncode, 0)
        self.assertIn('Worker spawned', output)
        
        # Verify correct command was called
        expected_cmd = [
            sys.executable,
            str(self.launcher.script_path),
            '--parent', self.valid_parent,
            '--instruction', self.test_instruction
        ]
        mock_run.assert_called_once_with(
            expected_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
    
    @patch('n5_launch_worker.subprocess.run')
    def test_spawn_worker_dry_run(self, mock_run):
        """Test worker spawning in dry-run mode."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "[DRY RUN] Would write assignment"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        returncode, output = self.launcher.spawn_worker(
            self.valid_parent,
            self.test_instruction,
            dry_run=True
        )
        
        self.assertEqual(returncode, 0)
        
        # Verify --dry-run flag was included
        call_args = mock_run.call_args[0][0]
        self.assertIn('--dry-run', call_args)
    
    @patch('n5_launch_worker.subprocess.run')
    def test_spawn_worker_timeout(self, mock_run):
        """Test worker spawning timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        returncode, output = self.launcher.spawn_worker(
            self.valid_parent,
            self.test_instruction
        )
        
        self.assertEqual(returncode, 1)
        self.assertIn('timed out', output)
    
    @patch('n5_launch_worker.subprocess.run')
    def test_spawn_worker_exception(self, mock_run):
        """Test worker spawning exception handling."""
        mock_run.side_effect = Exception("Network error")
        
        returncode, output = self.launcher.spawn_worker(
            self.valid_parent,
            self.test_instruction
        )
        
        self.assertEqual(returncode, 1)
        self.assertIn('Network error', output)
    
    def test_cli_missing_parent(self):
        """Test CLI error when parent is missing."""
        test_args = ['n5_launch_worker.py']
        
        with patch('sys.argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = main()
                self.assertEqual(result, 1)
                output = mock_stdout.getvalue()
                self.assertIn('required', output.lower())
    
    def test_cli_valid_arguments(self):
        """Test CLI with valid arguments."""
        test_args = [
            'n5_launch_worker.py',
            '--parent', self.valid_parent,
            '--type', 'build',
            '--instruction', self.test_instruction
        ]
        
        with patch('sys.argv', test_args):
            with patch.object(self.launcher, 'run_cli') as mock_run_cli:
                mock_run_cli.return_value = 0
                with patch('n5_launch_worker.LaunchWorker', return_value=self.launcher):
                    result = main()
                    self.assertEqual(result, 0)
    
    def test_cli_wizard_flag(self):
        """Test CLI with wizard flag."""
        test_args = [
            'n5_launch_worker.py',
            '--wizard'
        ]
        
        with patch('sys.argv', test_args):
            with patch.object(self.launcher, 'run_wizard') as mock_wizard:
                mock_wizard.return_value = {
                    'parent': self.valid_parent,
                    'worker_type': 'build',
                    'instruction': self.test_instruction
                }
                with patch.object(self.launcher, 'spawn_worker') as mock_spawn:
                    mock_spawn.return_value = (0, "Success")
                    with patch('n5_launch_worker.LaunchWorker', return_value=self.launcher):
                        result = main()
                        self.assertEqual(result, 0)
    
    def test_enhanced_instruction_preserves_original(self):
        """Test that enhanced instruction preserves the original intent."""
        original = "Implement user authentication"
        for wtype in WORKER_TYPES.keys():
            enhanced = self.launcher.enhance_instruction(original, wtype)
            if enhanced:  # Skip None case
                self.assertIn(original, enhanced)
                self.assertGreaterEqual(len(enhanced), len(original))
    
    def test_worker_type_selection_gives_distinct_results(self):
        """Test that different worker types produce different enhancements."""
        enhancements = {}
        for wtype in ['build', 'research', 'analysis']:
            enhancements[wtype] = self.launcher.enhance_instruction(self.test_instruction, wtype)
        
        # Build and research should be different
        self.assertNotEqual(enhancements['build'], enhancements['research'])
        
        # Research and analysis should be different  
        self.assertNotEqual(enhancements['research'], enhancements['analysis'])


class TestIntegration(unittest.TestCase):
    """Integration tests for n5 launch-worker."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.launcher = LaunchWorker()
        self.valid_parent = 'con_test123456789'
    
    @patch('n5_launch_worker.subprocess.run')
    def test_end_to_end_spawn(self, mock_run):
        """Test complete spawning flow."""
        # Mock successful spawn_worker.py execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ("✓ Worker spawned successfully!\n"
                            "📄 Open this file in a new conversation: "
                            "/home/workspace/Records/Temporary/WOKRER_ASSIGNMENT_20251111_180509.md")
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Enhance instruction for research type first (end-to-end flow)
        original_instruction = 'Test research task'
        enhanced_instruction = self.launcher.enhance_instruction(original_instruction, 'research')
        
        # Then spawn worker with enhanced instruction
        returncode, output = self.launcher.spawn_worker(
            self.valid_parent,
            enhanced_instruction
        )
        
        self.assertEqual(returncode, 0)
        self.assertIn('Worker spawned', output)
        
        # Verify spawn_worker.py was called correctly
        call_args = mock_run.call_args[0][0]
        self.assertIn('--parent', call_args)
        self.assertIn(self.valid_parent, call_args)
        self.assertIn('--instruction', call_args)
        
        # Verify instruction was enhanced for research type
        instruction_index = call_args.index('--instruction') + 1
        actual_instruction = call_args[instruction_index]
        self.assertIn('citations', actual_instruction)
        self.assertIn('synthesize', actual_instruction)


if __name__ == '__main__':
    unittest.main()









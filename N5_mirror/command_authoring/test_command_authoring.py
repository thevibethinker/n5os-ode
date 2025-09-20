#!/usr/bin/env python3
"""
Unit tests for the N5 Command Authoring System.
Tests all modules with telemetry logging included.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
import logging
from unittest.mock import patch, mock_open
from subprocess import run, PIPE

# Import modules to test
from .conversation_parser import parse_conversation, validate_segments
from .llm_scoping_agent import scope_and_clarify_segments, query_llm
from .command_structure_generator import generate_command_structure
from .validation_enhancement import validate_and_enhance_command
from .conflict_resolution_engine import resolve_conflicts_and_suggest
from .safe_export_handler import safe_export_command, validate_export_integrity


class TestConversationParser(unittest.TestCase):
    """Test conversation parser module."""
    
    def setUp(self):
        """Set up test logging."""
        logging.basicConfig(level=logging.DEBUG)
    
    def test_parse_simple_conversation(self):
        """Test parsing simple conversation text."""
        input_text = """
        Task: Create a file processing command
        This should process log files and extract errors.
        
        Steps:
        1. Read log files
        2. Parse for error patterns
        3. Export results
        """
        
        segments = parse_conversation(input_text)
        
        self.assertIsInstance(segments, list)
        self.assertGreater(len(segments), 0)
        
        # Check segment structure
        for segment in segments:
            self.assertIn('type', segment)
            self.assertIn('content', segment)
            self.assertIn('timestamp', segment)
    
    def test_parse_empty_input(self):
        """Test parsing empty input."""
        segments = parse_conversation("")
        self.assertEqual(segments, [])
        
        segments = parse_conversation(None)
        self.assertEqual(segments, [])
    
    def test_validate_segments(self):
        """Test segment validation."""
        valid_segments = [
            {'type': 'task', 'content': 'Do something', 'timestamp': '2023-01-01T00:00:00'}
        ]
        self.assertTrue(validate_segments(valid_segments))
        
        invalid_segments = [
            {'type': 'task', 'content': ''}  # Missing timestamp
        ]
        self.assertFalse(validate_segments(invalid_segments))
        
        # Test empty segments
        self.assertFalse(validate_segments([]))


class TestLLMScopingAgent(unittest.TestCase):
    """Test LLM scoping agent module."""
    
    def test_query_llm_basic(self):
        """Test basic LLM query functionality."""
        response = query_llm("Test prompt")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_query_llm_scoping(self):
        """Test LLM query with scoping keywords."""
        response = query_llm("scope these steps for a file processing task")
        self.assertIn('steps', response.lower())
        self.assertIn('Parse', response or '')
    
    def test_scope_and_clarify_segments(self):
        """Test scoping and clarification of segments."""
        segments = [
            {'type': 'task', 'content': 'Process files', 'timestamp': '2023-01-01T00:00:00'},
            {'type': 'context', 'content': 'Handle log files', 'timestamp': '2023-01-01T00:01:00'}
        ]
        
        result = scope_and_clarify_segments(segments)
        
        self.assertIsInstance(result, dict)
        self.assertIn('scoped_steps', result)
        self.assertIn('confidence', result)
        self.assertIsInstance(result['scoped_steps'], list)
    
    def test_scope_empty_segments(self):
        """Test scoping with empty segments."""
        result = scope_and_clarify_segments([])
        self.assertIn('error', result)


class TestCommandStructureGenerator(unittest.TestCase):
    """Test command structure generator module."""
    
    def test_generate_command_structure(self):
        """Test command structure generation."""
        scoped_draft = {
            'original_segments': [
                {'type': 'task', 'content': 'Process files', 'timestamp': '2023-01-01T00:00:00'}
            ],
            'scoped_steps': [
                {'id': 1, 'description': 'Read input files', 'type': 'action', 'details': ['Handle file I/O']},
                {'id': 2, 'description': 'Process data', 'type': 'action', 'details': ['Transform data']}
            ],
            'confidence': 0.8
        }
        
        result = generate_command_structure(scoped_draft)
        
        self.assertIsInstance(result, dict)
        self.assertIn('command', result)
        self.assertIn('steps', result)
        self.assertIn('retries', result)
        self.assertIn('timeout', result)
        self.assertIsInstance(result['steps'], list)
        
        # Check steps structure
        for step in result['steps']:
            self.assertIn('id', step)
            self.assertIn('name', step)
            self.assertIn('description', step)
            self.assertIn('action', step)
    
    def test_generate_with_error_draft(self):
        """Test generation with errored draft."""
        error_draft = {'error': 'Test error'}
        result = generate_command_structure(error_draft)
        self.assertIn('error', result)
    
    def test_generate_minimal_structure(self):
        """Test generation with minimal input."""
        minimal_draft = {
            'original_segments': [],
            'scoped_steps': [],
            'confidence': 0.5
        }
        
        result = generate_command_structure(minimal_draft)
        # Should generate fallback structure
        self.assertIn('error', result)
        self.assertIn('fallback_structure', result)


class TestValidationEnhancement(unittest.TestCase):
    """Test validation and enhancement module."""
    
    def test_validate_and_enhance_command(self):
        """Test command validation and enhancement."""
        command = {
            'id': 'test-123',
            'command': 'test_command',
            'version': '1.0.0',
            'created_at': '2023-01-01T00:00:00Z',
            'source': 'test',
            'description': 'Test command',
            'steps': [
                {
                    'id': 1,
                    'name': 'test_step',
                    'description': 'Test step',
                    'type': 'action',
                    'action': 'execute'
                }
            ],
            'retries': {'global_retries': 1},
            'timeout': 60
        }
        
        result = validate_and_enhance_command(command)
        
        self.assertIsInstance(result, dict)
        self.assertIn('validation', result)
        
        validation = result['validation']
        self.assertIn('results', validation)
        self.assertIn('status', validation)
        
        # Check enhancements were applied
        self.assertIn('metadata', result)
        self.assertIn('monitoring', result)
        self.assertIn('security', result)
    
    def test_validate_invalid_command(self):
        """Test validation of invalid command."""
        invalid_command = {
            'command': 'test',
            # Missing required fields
        }
        
        result = validate_and_enhance_command(invalid_command)
        validation = result.get('validation', {})
        results = validation.get('results', {})
        
        self.assertGreater(len(results.get('errors', [])), 0)
    
    def test_validate_error_command(self):
        """Test validation of command with error."""
        error_command = {'error': 'Test error'}
        result = validate_and_enhance_command(error_command)
        self.assertIn('error', result)


class TestConflictResolutionEngine(unittest.TestCase):
    """Test conflict resolution engine module."""
    
    def setUp(self):
        """Set up temporary commands file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        # Add some existing commands
        existing_commands = [
            {'id': 'existing-1', 'command': 'existing_command', 'description': 'Existing command'},
            {'id': 'existing-2', 'command': 'another_command', 'description': 'Another command'}
        ]
        
        for cmd in existing_commands:
            self.temp_file.write(json.dumps(cmd) + '\n')
        
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_resolve_conflicts_no_conflicts(self):
        """Test conflict resolution with no conflicts."""
        command = {
            'id': 'new-123',
            'command': 'unique_command',
            'description': 'A unique command',
            'steps': [],
            'tags': [],
            'category': 'test'
        }
        
        result = resolve_conflicts_and_suggest(command, self.temp_file.name)
        
        self.assertIsInstance(result, dict)
        self.assertIn('conflict_resolution', result)
        
        resolution = result['conflict_resolution']
        self.assertIn('scan_results', resolution)
        self.assertIn('status', resolution)
    
    def test_resolve_conflicts_with_duplicates(self):
        """Test conflict resolution with duplicate names."""
        command = {
            'id': 'new-123',
            'command': 'existing_command',  # Same as existing
            'description': 'A duplicate command',
            'steps': [],
            'tags': [],
            'category': 'test'
        }
        
        result = resolve_conflicts_and_suggest(command, self.temp_file.name)
        
        resolution = result['conflict_resolution']
        scan_results = resolution['scan_results']
        
        self.assertGreater(scan_results.get('conflicts_found', 0), 0)
        self.assertGreater(len(scan_results.get('duplicate_names', [])), 0)
    
    def test_resolve_conflicts_nonexistent_file(self):
        """Test conflict resolution with non-existent commands file."""
        command = {
            'id': 'new-123',
            'command': 'test_command',
            'description': 'Test command',
            'steps': []
        }
        
        result = resolve_conflicts_and_suggest(command, 'nonexistent.jsonl')
        
        # Should handle gracefully
        self.assertIn('conflict_resolution', result)


class TestSafeExportHandler(unittest.TestCase):
    """Test safe export handler module."""
    
    def setUp(self):
        """Set up temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_file = os.path.join(self.temp_dir, 'commands.jsonl')
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_safe_export_command(self):
        """Test safe command export."""
        command = {
            'id': 'test-123',
            'command': 'test_command',
            'version': '1.0.0',
            'description': 'Test command for export',
            'steps': []
        }
        
        result = safe_export_command(command, self.commands_file)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('command_id', result)
        self.assertIn('file_path', result)
        
        # Check file was created
        self.assertTrue(os.path.exists(self.commands_file))
        
        # Check content
        with open(self.commands_file, 'r') as f:
            content = f.read().strip()
            exported_command = json.loads(content)
            self.assertEqual(exported_command['id'], 'test-123')
    
    def test_export_multiple_commands(self):
        """Test exporting multiple commands."""
        commands = [
            {'id': 'cmd-1', 'command': 'command1', 'steps': []},
            {'id': 'cmd-2', 'command': 'command2', 'steps': []},
        ]
        
        for cmd in commands:
            result = safe_export_command(cmd, self.commands_file)
            self.assertTrue(result.get('success', False))
        
        # Check both commands are in file
        with open(self.commands_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            self.assertEqual(len(lines), 2)
            
            cmd1 = json.loads(lines[0])
            cmd2 = json.loads(lines[1])
            self.assertEqual(cmd1['id'], 'cmd-1')
            self.assertEqual(cmd2['id'], 'cmd-2')
    
    def test_validate_export_integrity(self):
        """Test export integrity validation."""
        command = {'id': 'test-123', 'command': 'test_command', 'steps': []}
        
        # Export command
        safe_export_command(command, self.commands_file)
        
        # Validate integrity
        validation = validate_export_integrity(Path(self.commands_file), 'test-123')
        
        self.assertTrue(validation.get('file_exists', False))
        self.assertTrue(validation.get('file_valid', False))
        self.assertTrue(validation.get('command_found', False))
        self.assertEqual(validation.get('total_commands', 0), 1)
    
    def test_export_error_command(self):
        """Test export of command with error."""
        error_command = {'error': 'Test error'}
        result = safe_export_command(error_command, self.commands_file)
        self.assertIn('error', result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.commands_file = os.path.join(self.temp_dir, 'commands.jsonl')
        logging.basicConfig(level=logging.INFO)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_flow(self):
        """Test complete end-to-end flow."""
        input_text = """
        Task: Create a log analysis command
        
        This command should:
        1. Read log files from a directory
        2. Parse for error patterns
        3. Generate summary report
        4. Export results to CSV
        
        Handle errors gracefully and provide logging.
        """
        
        # Step 1: Parse conversation
        segments = parse_conversation(input_text)
        self.assertGreater(len(segments), 0)
        
        # Step 2: LLM scoping
        scoped_draft = scope_and_clarify_segments(segments)
        self.assertNotIn('error', scoped_draft)
        
        # Step 3: Generate structure
        structured_command = generate_command_structure(scoped_draft)
        self.assertNotIn('error', structured_command)
        
        # Step 4: Validate and enhance
        validated_command = validate_and_enhance_command(structured_command)
        self.assertIn('validation', validated_command)
        
        # Step 5: Resolve conflicts
        resolved_command = resolve_conflicts_and_suggest(validated_command, self.commands_file)
        self.assertIn('conflict_resolution', resolved_command)
        
        # Step 6: Export
        export_result = safe_export_command(resolved_command, self.commands_file)
        self.assertTrue(export_result.get('success', False))
        
        # Verify final result
        self.assertTrue(os.path.exists(self.commands_file))
        
        with open(self.commands_file, 'r') as f:
            exported_command = json.loads(f.read().strip())
            self.assertIn('command', exported_command)
            self.assertIn('steps', exported_command)
            self.assertIsInstance(exported_command['steps'], list)
    
    def test_error_handling(self):
        """Test error handling throughout the pipeline."""
        # Test with problematic input
        input_text = ""  # Empty input
        
        segments = parse_conversation(input_text)
        self.assertEqual(segments, [])
        
        # Pipeline should handle empty segments gracefully
        scoped_draft = scope_and_clarify_segments(segments)
        self.assertIn('error', scoped_draft)
        
        # Subsequent steps should handle errors
        structured_command = generate_command_structure(scoped_draft)
        self.assertIn('error', structured_command)


class TestCommandAuthoringIntegration(unittest.TestCase):
    def setUp(self):
        self.conversation_path = '/home/workspace/N5/tmp_execution/sample_conversation.txt'
        self.command_author_path = '/home/workspace/N5/scripts/author-command/author-command'
        self.telemetry_file = Path('/home/workspace/command_authoring_telemetry.json')

    def test_full_pipeline_success(self):
        result = run(['python3', self.command_author_path, self.conversation_path], stdout=PIPE, stderr=PIPE, text=True)
        self.assertEqual(result.returncode, 0, f"Command execution failed: {result.stderr}")
        self.assertIn('Command authoring completed successfully', result.stdout)

    def test_telemetry_file_created(self):
        if self.telemetry_file.exists():
            self.telemetry_file.unlink()

        run(['python3', self.command_author_path, self.conversation_path], stdout=PIPE, stderr=PIPE, text=True)
        self.assertTrue(self.telemetry_file.exists(), "Telemetry file not created")

        with open(self.telemetry_file, 'r') as f:
            data = json.load(f)
        self.assertIn('metrics', data)
        self.assertIn('performance_report', data)


def run_all_tests():
    """Run all tests with telemetry logging."""
    # Set up logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log test results
    logging.info(f"Tests run: {result.testsRun}")
    logging.info(f"Failures: {len(result.failures)}")
    logging.info(f"Errors: {len(result.errors)}")
    
    if result.failures:
        logging.error("Test failures occurred")
        for test, traceback in result.failures:
            logging.error(f"FAILED: {test}")
            logging.error(traceback)
    
    if result.errors:
        logging.error("Test errors occurred")
        for test, traceback in result.errors:
            logging.error(f"ERROR: {test}")
            logging.error(traceback)
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    logging.info(f"Overall test result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Comprehensive unit tests for Jobs Command Authoring framework integration.

Tests cover:
- Command entry points and integration flows
- Telemetry and logging functionality
- Dry-run capabilities and validation
- Error handling and recovery
- Atomic operations and rollback
- CLI wrapper integration
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add N5 to path for imports
sys.path.append('/home/workspace')

from N5.command_authoring.jobs_scrape_command import JobsScrapeCommand, jobs_scrape_command_entry
from N5.command_authoring.jobs_add_command import JobsAddCommand, jobs_add_command_entry  
from N5.command_authoring.jobs_review_command import JobsReviewCommand, jobs_review_command_entry

class TestJobsScrapeCommand(unittest.TestCase):
    """Test suite for jobs-scrape Command Authoring integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.command = JobsScrapeCommand()
        self.temp_dir = tempfile.mkdtemp()
        self.companies_file = os.path.join(self.temp_dir, 'companies.txt')
        
        # Create test companies file
        with open(self.companies_file, 'w') as f:
            f.write("stripe\\nairbnb\\nuber\\n")
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_command_initialization(self):
        """Test command initialization and telemetry setup."""
        self.assertIsNotNone(self.command.command_id)
        self.assertIsNotNone(self.command.start_time)
        self.assertIsInstance(self.command.telemetry, dict)
        self.assertEqual(self.command.telemetry['command_id'], self.command.command_id)
        self.assertIn('start_time', self.command.telemetry)
        self.assertIn('metrics', self.command.telemetry)
        self.assertIn('errors', self.command.telemetry)
        self.assertIn('warnings', self.command.telemetry)
        self.assertIn('stages', self.command.telemetry)
    
    def test_validate_inputs_valid_file(self):
        """Test input validation with valid companies file."""
        result = self.command.validate_inputs(self.companies_file, ['backend', 'frontend'])
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['companies']), 3)
        self.assertIn('stripe', result['companies'])
        self.assertIn('airbnb', result['companies'])
        self.assertIn('uber', result['companies'])
        self.assertEqual(result['role_filters'], ['backend', 'frontend'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_inputs_missing_file(self):
        """Test input validation with missing file."""
        missing_file = os.path.join(self.temp_dir, 'missing.txt')
        result = self.command.validate_inputs(missing_file, [])
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('not found', result['errors'][0].lower())
    
    def test_validate_inputs_empty_file(self):
        """Test input validation with empty file."""
        empty_file = os.path.join(self.temp_dir, 'empty.txt')
        with open(empty_file, 'w') as f:
            f.write('')
        
        result = self.command.validate_inputs(empty_file, [])
        
        self.assertFalse(result['valid'])
        self.assertIn('empty', result['errors'][0].lower())
    
    def test_dry_run_simulation(self):
        """Test dry-run simulation functionality."""
        companies = ['stripe', 'airbnb']
        role_filters = ['backend']
        
        result = self.command.dry_run_simulation(companies, role_filters)
        
        self.assertIsInstance(result, dict)
        self.assertIn('estimated_operations', result)
        self.assertIn('estimated_duration_minutes', result)
        self.assertIn('risk_assessment', result)
        self.assertIn('companies_to_process', result)
        self.assertEqual(result['companies_count'], 2)
        self.assertEqual(result['role_filters'], role_filters)
    
    @patch('N5.command_authoring.jobs_scrape_command.scrape_flow')
    def test_execute_scraping_success(self, mock_scrape_flow):
        """Test successful scraping execution."""
        mock_scrape_flow.return_value = {
            'new_jobs': 5,
            'rejected': 2,
            'errors': []
        }
        
        companies = ['stripe']
        role_filters = ['backend']
        
        result = self.command.execute_scraping(companies, role_filters)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['companies_processed'], 1)
        self.assertEqual(result['jobs_added'], 5)
        self.assertEqual(result['jobs_rejected'], 2)
        self.assertEqual(len(result['errors']), 0)
    
    @patch('N5.command_authoring.jobs_scrape_command.scrape_flow')
    def test_execute_scraping_with_errors(self, mock_scrape_flow):
        """Test scraping execution with errors."""
        mock_scrape_flow.side_effect = Exception("Network error")
        
        companies = ['stripe']
        role_filters = ['backend']
        
        result = self.command.execute_scraping(companies, role_filters)
        
        self.assertTrue(result['success'])  # Command handles individual errors gracefully
        self.assertEqual(result['companies_processed'], 0)
        self.assertEqual(result['companies_failed'], 1)
        self.assertGreater(len(result['errors']), 0)
    
    def test_command_entry_dry_run(self):
        """Test command entry point with dry run."""
        result = jobs_scrape_command_entry(self.companies_file, "", True, False)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['dry_run'])
        self.assertIn('simulation_result', result)
        self.assertIn('telemetry', result)
    
    def test_command_entry_validation_failure(self):
        """Test command entry point with validation failure."""
        missing_file = os.path.join(self.temp_dir, 'missing.txt')
        result = jobs_scrape_command_entry(missing_file, "", False, False)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('telemetry', result)

class TestJobsAddCommand(unittest.TestCase):
    """Test suite for jobs-add Command Authoring integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.command = JobsAddCommand()
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock target file path
        self.original_target_file = self.command.target_file
        self.command.target_file = Path(os.path.join(self.temp_dir, 'jobs-private.jsonl'))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.command.target_file = self.original_target_file
    
    def test_command_initialization(self):
        """Test command initialization and telemetry setup."""
        self.assertIsNotNone(self.command.command_id)
        self.assertIsNotNone(self.command.start_time)
        self.assertIsInstance(self.command.telemetry, dict)
        self.assertEqual(self.command.telemetry['command_id'], self.command.command_id)
    
    def test_parse_job_string_valid(self):
        """Test job string parsing with valid input."""
        job_string = "Senior Backend Engineer@Stripe SF 200k"
        result = self.command.parse_job_string(job_string)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['job_data']['title'], 'Senior Backend Engineer')
        self.assertEqual(result['job_data']['company'], 'Stripe')
        self.assertEqual(result['job_data']['location'], 'SF')
        self.assertEqual(result['job_data']['salary'], '200k')
        self.assertEqual(len(result['errors']), 0)
    
    def test_parse_job_string_minimal(self):
        """Test job string parsing with minimal input."""
        job_string = "Developer@Uber"
        result = self.command.parse_job_string(job_string)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['job_data']['title'], 'Developer')
        self.assertEqual(result['job_data']['company'], 'Uber')
        self.assertEqual(result['job_data']['location'], '')
        self.assertEqual(result['job_data']['salary'], '')
    
    def test_parse_job_string_invalid_format(self):
        """Test job string parsing with invalid format."""
        job_string = "Senior Backend Engineer"  # Missing @
        result = self.command.parse_job_string(job_string)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('@', result['errors'][0])
    
    def test_parse_job_string_empty(self):
        """Test job string parsing with empty input."""
        job_string = ""
        result = self.command.parse_job_string(job_string)
        
        self.assertFalse(result['valid'])
        self.assertIn('empty', result['errors'][0].lower())
    
    def test_create_job_record(self):
        """Test job record creation."""
        job_data = {
            'title': 'Backend Engineer',
            'company': 'Stripe',
            'location': 'SF',
            'salary': '150k'
        }
        
        job_record = self.command.create_job_record(job_data)
        
        self.assertIsNotNone(job_record['uid'])
        self.assertEqual(job_record['title'], 'Backend Engineer')
        self.assertEqual(job_record['company'], 'Stripe')
        self.assertEqual(job_record['location'], 'SF')
        self.assertEqual(job_record['salary'], '150k')
        self.assertEqual(job_record['status'], 'PENDING')
        self.assertEqual(job_record['source'], 'manual_add')
        self.assertIn('captured_at', job_record)
        self.assertIn('added_by_command', job_record)
        self.assertIn('metadata', job_record)
    
    def test_validate_job_record_valid(self):
        """Test job record validation with valid record."""
        job_record = {
            'uid': 'test-uid',
            'title': 'Engineer',
            'company': 'Test Co',
            'location': '',
            'salary': '',
            'status': 'PENDING',
            'captured_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        result = self.command.validate_job_record(job_record)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['risk_assessment'], 'low')
    
    def test_validate_job_record_missing_fields(self):
        """Test job record validation with missing required fields."""
        job_record = {
            'title': 'Engineer'
            # Missing required fields
        }
        
        result = self.command.validate_job_record(job_record)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_dry_run_simulation(self):
        """Test dry-run simulation."""
        job_record = {
            'uid': 'test-uid',
            'title': 'Engineer',
            'company': 'Test Co',
            'status': 'PENDING'
        }
        
        result = self.command.dry_run_simulation(job_record)
        
        self.assertIsInstance(result, dict)
        self.assertIn('would_add_job', result)
        self.assertIn('target_file', result)
        self.assertIn('risk_assessment', result)
        self.assertIn('preview_record', result)
    
    def test_safe_append_job_new_file(self):
        """Test safe job appending to new file."""
        job_record = {
            'uid': 'test-uid',
            'title': 'Engineer',
            'company': 'Test Co',
            'status': 'PENDING'
        }
        
        result = self.command.safe_append_job(job_record)
        
        self.assertTrue(result['success'])
        self.assertFalse(result['backup_created'])  # No backup needed for new file
        self.assertGreater(result['bytes_written'], 0)
        
        # Verify file was created and contains the job
        self.assertTrue(self.command.target_file.exists())
        with open(self.command.target_file, 'r') as f:
            saved_job = json.loads(f.readline().strip())
            self.assertEqual(saved_job['uid'], 'test-uid')
    
    def test_command_entry_dry_run(self):
        """Test command entry point with dry run."""
        job_string = "Engineer@TestCorp"
        result = jobs_add_command_entry(job_string, True, False)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['dry_run'])
        self.assertIn('job_record', result)
        self.assertIn('simulation_result', result)
        self.assertIn('telemetry', result)
    
    def test_command_entry_validation_failure(self):
        """Test command entry point with validation failure."""
        job_string = "Invalid Format"  # Missing @
        result = jobs_add_command_entry(job_string, False, False)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('telemetry', result)

class TestJobsReviewCommand(unittest.TestCase):
    """Test suite for jobs-review Command Authoring integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.command = JobsReviewCommand()
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock file paths
        self.original_scraped_file = self.command.scraped_jobs_file
        self.original_private_file = self.command.private_jobs_file
        self.command.scraped_jobs_file = Path(os.path.join(self.temp_dir, 'jobs-scraped.jsonl'))
        self.command.private_jobs_file = Path(os.path.join(self.temp_dir, 'jobs-private.jsonl'))
        
        # Create test data
        self.test_jobs = [
            {"uid": "job1", "title": "Engineer", "company": "Stripe", "status": "PENDING"},
            {"uid": "job2", "title": "Designer", "company": "Uber", "status": "OK"},
            {"uid": "job3", "title": "Manager", "company": "Airbnb", "status": "PENDING"}
        ]
        
        with open(self.command.scraped_jobs_file, 'w') as f:
            for job in self.test_jobs:
                f.write(json.dumps(job) + '\n')
    
    def tearDown(self):\n        \"\"\"Clean up test environment.\"\"\"\n        import shutil\n        shutil.rmtree(self.temp_dir, ignore_errors=True)\n        self.command.scraped_jobs_file = self.original_scraped_file\n        self.command.private_jobs_file = self.original_private_file\n    \n    def test_command_initialization(self):\n        \"\"\"Test command initialization and telemetry setup.\"\"\"\n        self.assertIsNotNone(self.command.command_id)\n        self.assertIsNotNone(self.command.start_time)\n        self.assertIsInstance(self.command.telemetry, dict)\n        self.assertEqual(self.command.telemetry['command_id'], self.command.command_id)\n        self.assertIn('review_actions', self.command.telemetry)\n        self.assertIn('session_state', self.command.__dict__)\n    \n    def test_load_jobs_for_review(self):\n        \"\"\"Test loading jobs for review.\"\"\"\n        result = self.command.load_jobs_for_review()\n        \n        self.assertTrue(result['success'])\n        self.assertEqual(len(result['scraped_jobs']), 3)\n        self.assertEqual(len(result['pending_scraped']), 2)  # 2 PENDING jobs\n        self.assertEqual(result['total_pending'], 2)\n        self.assertTrue(result['files_found']['scraped'])\n    \n    def test_load_jobs_no_files(self):\n        \"\"\"Test loading jobs when no files exist.\"\"\"\n        # Remove test files\n        os.remove(self.command.scraped_jobs_file)\n        \n        result = self.command.load_jobs_for_review()\n        \n        self.assertTrue(result['success'])  # Not an error, just no work\n        self.assertEqual(result['total_pending'], 0)\n        self.assertFalse(result['files_found']['scraped'])\n    \n    def test_process_review_decision_approve(self):\n        \"\"\"Test processing approve decision.\"\"\"\n        job = {\"uid\": \"test\", \"title\": \"Engineer\", \"company\": \"Test\", \"status\": \"PENDING\"}\n        \n        result = self.command.process_review_decision(job, 'approve')\n        \n        self.assertTrue(result['success'])\n        self.assertEqual(result['action_taken'], 'approve')\n        self.assertEqual(result['old_status'], 'PENDING')\n        self.assertEqual(result['new_status'], 'OK')\n        self.assertEqual(result['updated_job']['status'], 'OK')\n        self.assertIn('reviewed_at', result['updated_job'])\n        self.assertEqual(self.command.session_state['jobs_approved'], 1)\n    \n    def test_process_review_decision_reject(self):\n        \"\"\"Test processing reject decision.\"\"\"\n        job = {\"uid\": \"test\", \"title\": \"Engineer\", \"company\": \"Test\", \"status\": \"PENDING\"}\n        \n        result = self.command.process_review_decision(job, 'reject')\n        \n        self.assertTrue(result['success'])\n        self.assertEqual(result['action_taken'], 'reject')\n        self.assertEqual(result['updated_job']['status'], 'REJECTED')\n        self.assertEqual(self.command.session_state['jobs_rejected'], 1)\n    \n    def test_process_review_decision_skip(self):\n        \"\"\"Test processing skip decision.\"\"\"\n        job = {\"uid\": \"test\", \"title\": \"Engineer\", \"company\": \"Test\", \"status\": \"PENDING\"}\n        \n        result = self.command.process_review_decision(job, 'skip')\n        \n        self.assertTrue(result['success'])\n        self.assertEqual(result['action_taken'], 'skip')\n        self.assertEqual(result['updated_job']['status'], 'PENDING')  # Unchanged\n        self.assertEqual(self.command.session_state['jobs_skipped'], 1)\n    \n    def test_log_review_action(self):\n        \"\"\"Test review action logging.\"\"\"\n        self.command.log_review_action('approve', 'test-uid', 'Engineer', 'TestCorp')\n        \n        self.assertEqual(len(self.command.telemetry['review_actions']), 1)\n        action = self.command.telemetry['review_actions'][0]\n        self.assertEqual(action['action'], 'approve')\n        self.assertEqual(action['job_uid'], 'test-uid')\n        self.assertEqual(action['job_title'], 'Engineer')\n        self.assertEqual(action['job_company'], 'TestCorp')\n    \n    @patch('N5.command_authoring.jobs_review_command.input')\n    def test_get_review_decision_approve(self, mock_input):\n        \"\"\"Test getting review decision - approve.\"\"\"\n        mock_input.return_value = 'a'\n        job = {\"title\": \"Engineer\", \"company\": \"Test\"}\n        \n        decision = self.command.get_review_decision(job)\n        \n        self.assertEqual(decision, 'approve')\n    \n    @patch('N5.command_authoring.jobs_review_command.input')\n    def test_get_review_decision_quit(self, mock_input):\n        \"\"\"Test getting review decision - quit.\"\"\"\n        mock_input.return_value = 'q'\n        job = {\"title\": \"Engineer\", \"company\": \"Test\"}\n        \n        decision = self.command.get_review_decision(job)\n        \n        self.assertEqual(decision, 'quit')\n\nclass TestCLIWrapperIntegration(unittest.TestCase):\n    \"\"\"Test suite for CLI wrapper integration with Command Authoring framework.\"\"\"\n    \n    def setUp(self):\n        \"\"\"Set up test environment.\"\"\"\n        self.temp_dir = tempfile.mkdtemp()\n        self.companies_file = os.path.join(self.temp_dir, 'companies.txt')\n        \n        with open(self.companies_file, 'w') as f:\n            f.write(\"stripe\\n\")\n    \n    def tearDown(self):\n        \"\"\"Clean up test environment.\"\"\"\n        import shutil\n        shutil.rmtree(self.temp_dir, ignore_errors=True)\n    \n    @patch('N5.command_authoring.jobs_scrape_command.jobs_scrape_command_entry')\n    def test_scrape_cli_wrapper_dry_run(self, mock_entry):\n        \"\"\"Test scrape CLI wrapper integration with dry run.\"\"\"\n        mock_entry.return_value = {\n            'success': True,\n            'dry_run': True,\n            'simulation_result': {'estimated_operations': 10}\n        }\n        \n        # Import and test the wrapper\n        from N5.jobs.commands.scrape import main\n        \n        with patch('sys.argv', ['scrape.py', self.companies_file, '--dry-run']):\n            try:\n                main()\n            except SystemExit as e:\n                self.assertEqual(e.code, None)  # Success exit\n        \n        mock_entry.assert_called_once()\n        args, kwargs = mock_entry.call_args\n        self.assertTrue(kwargs.get('dry_run'))\n    \n    @patch('N5.command_authoring.jobs_add_command.jobs_add_command_entry')\n    def test_add_cli_wrapper(self, mock_entry):\n        \"\"\"Test add CLI wrapper integration.\"\"\"\n        mock_entry.return_value = {\n            'success': True,\n            'job_record': {'uid': 'test', 'title': 'Engineer', 'company': 'Test'}\n        }\n        \n        from N5.jobs.commands.add_oneoff import main\n        \n        with patch('sys.argv', ['add_oneoff.py', 'Engineer@TestCorp']):\n            try:\n                main()\n            except SystemExit as e:\n                self.assertEqual(e.code, None)  # Success exit\n        \n        mock_entry.assert_called_once()\n    \n    @patch('N5.command_authoring.jobs_review_command.jobs_review_command_entry')\n    def test_review_cli_wrapper(self, mock_entry):\n        \"\"\"Test review CLI wrapper integration.\"\"\"\n        mock_entry.return_value = {\n            'success': True,\n            'session_summary': {'jobs_reviewed': 2, 'jobs_approved': 1}\n        }\n        \n        from N5.jobs.commands.review import main\n        \n        with patch('sys.argv', ['review.py']):\n            try:\n                main()\n            except SystemExit as e:\n                self.assertEqual(e.code, None)  # Success exit\n        \n        mock_entry.assert_called_once()\n\nclass TestTelemetryAndLogging(unittest.TestCase):\n    \"\"\"Test suite for telemetry and logging functionality.\"\"\"\n    \n    def test_jobs_scrape_telemetry(self):\n        \"\"\"Test telemetry collection in jobs scrape command.\"\"\"\n        command = JobsScrapeCommand()\n        \n        # Test stage logging\n        command.log_stage_start('test_stage')\n        self.assertIn('test_stage', command.telemetry['stages'])\n        self.assertEqual(command.telemetry['stages']['test_stage']['status'], 'in_progress')\n        \n        command.log_stage_complete('test_stage', {'metric1': 100})\n        self.assertEqual(command.telemetry['stages']['test_stage']['status'], 'completed')\n        self.assertEqual(command.telemetry['stages']['test_stage']['metrics']['metric1'], 100)\n        \n        # Test error logging\n        command.log_error('Test error', 'test_stage')\n        self.assertEqual(len(command.telemetry['errors']), 1)\n        self.assertEqual(command.telemetry['errors'][0]['error'], 'Test error')\n        \n        # Test warning logging\n        command.log_warning('Test warning', 'test_stage')\n        self.assertEqual(len(command.telemetry['warnings']), 1)\n        self.assertEqual(command.telemetry['warnings'][0]['warning'], 'Test warning')\n    \n    def test_jobs_add_telemetry(self):\n        \"\"\"Test telemetry collection in jobs add command.\"\"\"\n        command = JobsAddCommand()\n        \n        # Test telemetry finalization\n        telemetry = command.finalize_telemetry({'test': 'result'})\n        \n        self.assertIn('end_time', telemetry)\n        self.assertIn('duration_seconds', telemetry)\n        self.assertIn('final_status', telemetry)\n        self.assertIn('execution_summary', telemetry)\n    \n    def test_jobs_review_telemetry(self):\n        \"\"\"Test telemetry collection in jobs review command.\"\"\"\n        command = JobsReviewCommand()\n        \n        # Test review action logging\n        command.log_review_action('approve', 'uid123', 'Engineer', 'TestCorp')\n        \n        self.assertEqual(len(command.telemetry['review_actions']), 1)\n        action = command.telemetry['review_actions'][0]\n        self.assertEqual(action['action'], 'approve')\n        self.assertEqual(action['job_uid'], 'uid123')\n        \n        # Test session state tracking\n        self.assertIn('jobs_reviewed', command.session_state)\n        self.assertIn('jobs_approved', command.session_state)\n        self.assertIn('jobs_rejected', command.session_state)\n        self.assertIn('jobs_skipped', command.session_state)\n\nif __name__ == '__main__':\n    # Run all tests\n    unittest.main(verbosity=2)"
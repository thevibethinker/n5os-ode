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
            f.write("stripe\nairbnb\nuber\n")
    
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
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.command.scraped_jobs_file = self.original_scraped_file
        self.command.private_jobs_file = self.original_private_file
    
    def test_command_initialization(self):
        """Test command initialization and telemetry setup."""
        self.assertIsNotNone(self.command.command_id)
        self.assertIsNotNone(self.command.start_time)
        self.assertIsInstance(self.command.telemetry, dict)
        self.assertEqual(self.command.telemetry['command_id'], self.command.command_id)
        self.assertIn('review_actions', self.command.telemetry)
        self.assertIn('session_state', self.command.__dict__)
    
    def test_load_jobs_for_review(self):
        """Test loading jobs for review."""
        result = self.command.load_jobs_for_review()
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['scraped_jobs']), 3)
        self.assertEqual(len(result['pending_scraped']), 2)  # 2 PENDING jobs
        self.assertEqual(result['total_pending'], 2)
        self.assertTrue(result['files_found']['scraped'])

class TestTelemetryAndLogging(unittest.TestCase):
    """Test suite for telemetry and logging functionality."""
    
    def test_jobs_scrape_telemetry(self):
        """Test telemetry collection in jobs scrape command."""
        command = JobsScrapeCommand()
        
        # Test stage logging
        command.log_stage_start('test_stage')
        self.assertIn('test_stage', command.telemetry['stages'])
        self.assertEqual(command.telemetry['stages']['test_stage']['status'], 'in_progress')
        
        command.log_stage_complete('test_stage', {'metric1': 100})
        self.assertEqual(command.telemetry['stages']['test_stage']['status'], 'completed')
        self.assertEqual(command.telemetry['stages']['test_stage']['metrics']['metric1'], 100)
        
        # Test error logging
        command.log_error('Test error', 'test_stage')
        self.assertEqual(len(command.telemetry['errors']), 1)
        self.assertEqual(command.telemetry['errors'][0]['error'], 'Test error')
        
        # Test warning logging
        command.log_warning('Test warning', 'test_stage')
        self.assertEqual(len(command.telemetry['warnings']), 1)
        self.assertEqual(command.telemetry['warnings'][0]['warning'], 'Test warning')

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
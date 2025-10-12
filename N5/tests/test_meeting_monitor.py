#!/usr/bin/env python3
"""
Unit tests for Meeting Monitor (Priority 3)
Tests polling loop, urgent detection, and digest generation.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import pytz

# Add N5/scripts to path
script_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(script_dir))

from meeting_monitor import MeetingMonitor


class TestMeetingMonitor(unittest.TestCase):
    """Test MeetingMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_calendar = Mock()
        self.mock_gmail = Mock()
        self.et_tz = pytz.timezone('America/New_York')
        
        # Create monitor with short interval for testing
        self.monitor = MeetingMonitor(
            calendar_tool=self.mock_calendar,
            gmail_tool=self.mock_gmail,
            poll_interval_minutes=1,  # Short for testing
            lookahead_days=7
        )
    
    def test_initialization(self):
        """Test monitor initializes correctly."""
        self.assertEqual(self.monitor.poll_interval_minutes, 1)
        self.assertEqual(self.monitor.lookahead_days, 7)
        self.assertEqual(self.monitor.cycle_count, 0)
        self.assertEqual(self.monitor.total_processed, 0)
        self.assertEqual(self.monitor.urgent_count, 0)
    
    def test_detect_urgent_meetings_none(self):
        """Test urgent detection with no urgent meetings."""
        results = {
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Normal Meeting',
                    'start_time': '2025-10-15 02:00 PM',
                    'attendee_email': 'jane@example.com',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        urgent = self.monitor.detect_urgent_meetings(results)
        self.assertEqual(len(urgent), 0)
    
    def test_detect_urgent_meetings_with_urgent(self):
        """Test urgent detection with urgent meeting."""
        results = {
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Urgent Meeting',
                    'start_time': '2025-10-15 02:00 PM',
                    'attendee_email': 'ceo@bigcorp.com',
                    'profile_dir': '2025-10-15-ceo-bigcorp',
                    'tags': {
                        'is_critical': True,
                        'stakeholder_tags': ['LD-INV'],
                        'timing_tags': ['D5+']
                    }
                },
                {
                    'event_id': 'event2',
                    'summary': 'Normal Meeting',
                    'start_time': '2025-10-16 10:00 AM',
                    'attendee_email': 'john@example.com',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        urgent = self.monitor.detect_urgent_meetings(results)
        self.assertEqual(len(urgent), 1)
        self.assertEqual(urgent[0]['event_id'], 'event1')
        self.assertEqual(urgent[0]['summary'], 'Urgent Meeting')
        self.assertTrue(urgent[0]['tags']['is_critical'])
    
    def test_generate_digest_section_no_events(self):
        """Test digest generation with no new events."""
        results = {
            'new_events': 0,
            'total_events': 5,
            'already_processed': 5
        }
        
        section = self.monitor.generate_digest_section(results)
        self.assertIn('No new meetings', section)
        self.assertIn('📅 Meeting Prep Intelligence', section)
    
    def test_generate_digest_section_with_urgent(self):
        """Test digest generation with urgent meeting."""
        results = {
            'new_events': 2,
            'urgent_count': 1,
            'urgent_meetings': [
                {
                    'event_id': 'event1',
                    'summary': 'Series A Discussion',
                    'start_time': '2025-10-15 02:00 PM ET',
                    'attendee_email': 'jane@acme.com',
                    'profile_dir': '2025-10-15-jane-smith-acme',
                    'tags': {
                        'is_critical': True,
                        'stakeholder_tags': ['LD-INV'],
                        'timing_tags': ['D5+']
                    }
                }
            ],
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Series A Discussion',
                    'start_time': '2025-10-15 02:00 PM ET',
                    'attendee_email': 'jane@acme.com',
                    'profile_dir': '2025-10-15-jane-smith-acme',
                    'tags': {
                        'is_critical': True,
                        'stakeholder_tags': ['LD-INV']
                    }
                },
                {
                    'event_id': 'event2',
                    'summary': 'Normal Meeting',
                    'start_time': '2025-10-16 10:00 AM ET',
                    'attendee_email': 'john@example.com',
                    'profile_dir': '2025-10-16-john-doe',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.monitor.generate_digest_section(results)
        
        # Check structure
        self.assertIn('📅 Meeting Prep Intelligence', section)
        self.assertIn('🚨 Urgent Meetings', section)
        self.assertIn('[URGENT]', section)
        self.assertIn('Series A Discussion', section)
        self.assertIn('jane@acme.com', section)
        self.assertIn('Normal Priority Meetings', section)
        self.assertIn('Normal Meeting', section)
        self.assertIn('john@example.com', section)
        
        # Check summary
        self.assertIn('2 new meeting', section)
        self.assertIn('1 urgent', section)
    
    def test_generate_digest_section_normal_only(self):
        """Test digest generation with only normal meetings."""
        results = {
            'new_events': 1,
            'urgent_count': 0,
            'urgent_meetings': [],
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Team Sync',
                    'start_time': '2025-10-15 10:00 AM ET',
                    'attendee_email': 'team@company.com',
                    'profile_dir': '2025-10-15-team-sync',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.monitor.generate_digest_section(results)
        
        self.assertIn('Team Sync', section)
        self.assertNotIn('🚨 Urgent', section)
        self.assertNotIn('[URGENT]', section)
        self.assertIn('1 new meeting', section)
        self.assertIn('0 urgent', section)
    
    @patch('meeting_monitor.MeetingProcessor')
    def test_run_single_cycle_success(self, mock_processor_class):
        """Test running a single monitoring cycle."""
        # Mock processor
        mock_processor = Mock()
        mock_processor.process_upcoming_meetings.return_value = {
            'total_events': 1,
            'new_events': 1,
            'already_processed': 0,
            'new_profiles': 1,
            'errors': 0,
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Test Meeting',
                    'start_time': '2025-10-15 02:00 PM ET',
                    'attendee_email': 'test@example.com',
                    'tags': {'is_critical': False}
                }
            ]
        }
        mock_processor_class.return_value = mock_processor
        
        # Create new monitor to use mocked processor
        monitor = MeetingMonitor(
            self.mock_calendar, self.mock_gmail,
            poll_interval_minutes=1
        )
        monitor.processor = mock_processor
        
        # Run cycle
        result = monitor.run_single_cycle()
        
        # Verify
        self.assertEqual(monitor.cycle_count, 1)
        self.assertEqual(result['new_events'], 1)
        self.assertEqual(result['urgent_count'], 0)
        self.assertIn('digest_section', result)
    
    @patch('meeting_monitor.MeetingProcessor')
    def test_run_single_cycle_with_errors(self, mock_processor_class):
        """Test cycle with processing errors."""
        mock_processor = Mock()
        mock_processor.process_upcoming_meetings.return_value = {
            'total_events': 2,
            'new_events': 1,
            'already_processed': 0,
            'errors': 1,
            'processed_details': []
        }
        mock_processor_class.return_value = mock_processor
        
        monitor = MeetingMonitor(
            self.mock_calendar, self.mock_gmail
        )
        monitor.processor = mock_processor
        
        result = monitor.run_single_cycle()
        
        self.assertEqual(result['errors'], 1)
    
    @patch('meeting_monitor.time.sleep')
    @patch('meeting_monitor.MeetingProcessor')
    def test_run_continuous_limited_cycles(self, mock_processor_class, mock_sleep):
        """Test running continuous loop with cycle limit."""
        mock_processor = Mock()
        mock_processor.process_upcoming_meetings.return_value = {
            'total_events': 0,
            'new_events': 0,
            'already_processed': 0,
            'errors': 0
        }
        mock_processor_class.return_value = mock_processor
        
        monitor = MeetingMonitor(
            self.mock_calendar, self.mock_gmail,
            poll_interval_minutes=1
        )
        monitor.processor = mock_processor
        
        # Run 3 cycles
        summary = monitor.run_continuous(max_cycles=3)
        
        # Verify
        self.assertEqual(summary['total_cycles'], 3)
        self.assertEqual(len(summary['cycle_results']), 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Sleep between cycles, not after last
    
    def test_urgent_meeting_tracking(self):
        """Test that urgent meetings are tracked correctly."""
        results = {
            'new_events': 2,
            'processed_details': [
                {
                    'event_id': 'urgent1',
                    'summary': 'Urgent 1',
                    'start_time': '2025-10-15 02:00 PM',
                    'attendee_email': 'urgent@example.com',
                    'tags': {'is_critical': True}
                },
                {
                    'event_id': 'urgent2',
                    'summary': 'Urgent 2',
                    'start_time': '2025-10-16 10:00 AM',
                    'attendee_email': 'urgent2@example.com',
                    'tags': {'is_critical': True}
                }
            ]
        }
        
        urgent = self.monitor.detect_urgent_meetings(results)
        self.assertEqual(len(urgent), 2)
        
        # Verify all urgent meetings captured
        urgent_ids = [m['event_id'] for m in urgent]
        self.assertIn('urgent1', urgent_ids)
        self.assertIn('urgent2', urgent_ids)


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMeetingMonitor)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

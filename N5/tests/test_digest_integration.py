#!/usr/bin/env python3
"""
Unit tests for Digest Integration (Priority 3)
Tests digest formatting and file operations.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime
import pytz
import tempfile
import shutil

# Add N5/scripts to path
script_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(script_dir))

from digest_integration import DigestFormatter, format_for_digest


class TestDigestFormatter(unittest.TestCase):
    """Test DigestFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = DigestFormatter()
        self.et_tz = pytz.timezone('America/New_York')
        
        # Create temp directory for digest files
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test files."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_format_meeting_section_no_events(self):
        """Test formatting with no new events."""
        results = {
            'new_events': 0,
            'total_events': 5
        }
        
        section = self.formatter.format_meeting_section(results)
        
        self.assertIn('📅 Meeting Prep Intelligence', section)
        self.assertIn('No new meetings', section)
    
    def test_format_meeting_section_with_urgent(self):
        """Test formatting with urgent meetings."""
        results = {
            'new_events': 2,
            'urgent_count': 1,
            'urgent_meetings': [
                {
                    'event_id': 'event1',
                    'summary': 'Critical Meeting',
                    'start_time': '2025-10-15 02:00 PM ET',
                    'attendee_email': 'vip@company.com',
                    'profile_dir': '2025-10-15-vip-company',
                    'tags': {
                        'is_critical': True,
                        'stakeholder_tags': ['LD-INV']
                    }
                }
            ],
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Critical Meeting',
                    'start_time': '2025-10-15 02:00 PM ET',
                    'attendee_email': 'vip@company.com',
                    'profile_dir': '2025-10-15-vip-company',
                    'tags': {'is_critical': True}
                },
                {
                    'event_id': 'event2',
                    'summary': 'Normal Meeting',
                    'start_time': '2025-10-16 10:00 AM ET',
                    'attendee_email': 'normal@company.com',
                    'profile_dir': '2025-10-16-normal-company',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.formatter.format_meeting_section(results)
        
        # Check structure
        self.assertIn('📅 Meeting Prep Intelligence', section)
        self.assertIn('🚨 Urgent', section)
        self.assertIn('[URGENT]', section)
        self.assertIn('Critical Meeting', section)
        self.assertIn('📋 Normal Priority', section)
        self.assertIn('Normal Meeting', section)
        
        # Check summary
        self.assertIn('2 new meeting', section)
        self.assertIn('1 urgent', section)
    
    def test_format_meeting_section_normal_only(self):
        """Test formatting with only normal priority meetings."""
        results = {
            'new_events': 1,
            'urgent_count': 0,
            'urgent_meetings': [],
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Team Meeting',
                    'start_time': '2025-10-15 10:00 AM ET',
                    'attendee_email': 'team@company.com',
                    'profile_dir': '2025-10-15-team-meeting',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.formatter.format_meeting_section(results)
        
        self.assertIn('Team Meeting', section)
        self.assertNotIn('🚨 Urgent', section)
        self.assertNotIn('[URGENT]', section)
        self.assertIn('1 new meeting', section)
        self.assertIn('0 urgent', section)
    
    def test_format_meeting_section_without_summary(self):
        """Test formatting without summary footer."""
        results = {
            'new_events': 1,
            'urgent_count': 0,
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Meeting',
                    'start_time': '2025-10-15 10:00 AM',
                    'attendee_email': 'test@example.com',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.formatter.format_meeting_section(results, include_summary=False)
        
        self.assertIn('Meeting', section)
        self.assertNotIn('1 new meeting', section)  # Summary should be missing
    
    def test_format_daily_summary_no_meetings(self):
        """Test daily summary with no meetings."""
        all_results = [
            {'new_events': 0, 'urgent_count': 0},
            {'new_events': 0, 'urgent_count': 0},
            {'new_events': 0, 'urgent_count': 0}
        ]
        
        summary = self.formatter.format_daily_summary(all_results)
        
        self.assertIn('Daily Summary', summary)
        self.assertIn('No new meetings detected today', summary)
    
    def test_format_daily_summary_with_meetings(self):
        """Test daily summary with multiple meetings across cycles."""
        all_results = [
            {
                'new_events': 2,
                'urgent_count': 1,
                'processed_details': [
                    {
                        'event_id': 'event1',
                        'summary': 'Urgent Meeting',
                        'start_time': '2025-10-15 02:00 PM',
                        'attendee_email': 'urgent@example.com',
                        'profile_dir': '2025-10-15-urgent',
                        'tags': {'is_critical': True}
                    },
                    {
                        'event_id': 'event2',
                        'summary': 'Normal Meeting',
                        'start_time': '2025-10-16 10:00 AM',
                        'attendee_email': 'normal@example.com',
                        'profile_dir': '2025-10-16-normal',
                        'tags': {'is_critical': False}
                    }
                ]
            },
            {
                'new_events': 1,
                'urgent_count': 0,
                'processed_details': [
                    {
                        'event_id': 'event3',
                        'summary': 'Another Meeting',
                        'start_time': '2025-10-17 03:00 PM',
                        'attendee_email': 'another@example.com',
                        'profile_dir': '2025-10-17-another',
                        'tags': {'is_critical': False}
                    }
                ]
            }
        ]
        
        summary = self.formatter.format_daily_summary(all_results)
        
        # Check header
        self.assertIn('Daily Summary', summary)
        self.assertIn('2 monitoring cycles', summary)
        self.assertIn('3', summary)  # Total new meetings
        self.assertIn('1 urgent', summary)
        
        # Check meetings listed
        self.assertIn('🚨 Urgent Meetings', summary)
        self.assertIn('Urgent Meeting', summary)
        self.assertIn('📋 Upcoming Meetings', summary)
        self.assertIn('Normal Meeting', summary)
        self.assertIn('Another Meeting', summary)
    
    def test_format_daily_summary_deduplicates(self):
        """Test that daily summary deduplicates same event across cycles."""
        all_results = [
            {
                'new_events': 1,
                'urgent_count': 0,
                'processed_details': [
                    {
                        'event_id': 'event1',
                        'summary': 'UniqueTestMeeting',
                        'start_time': '2025-10-15 10:00 AM',
                        'attendee_email': 'test@example.com',
                        'profile_dir': '2025-10-15-test',
                        'tags': {'is_critical': False}
                    }
                ]
            },
            {
                'new_events': 0,  # Same meeting seen again
                'urgent_count': 0,
                'processed_details': [
                    {
                        'event_id': 'event1',  # Same ID
                        'summary': 'UniqueTestMeeting',
                        'start_time': '2025-10-15 10:00 AM',
                        'attendee_email': 'test@example.com',
                        'profile_dir': '2025-10-15-test',
                        'tags': {'is_critical': False}
                    }
                ]
            }
        ]
        
        summary = self.formatter.format_daily_summary(all_results)
        
        # Should aggregate correctly: 1 new meeting total (not 2)
        self.assertIn('**New Meetings:** 1', summary)
        
        # Should only show meeting once in the list
        count = summary.count('UniqueTestMeeting')
        self.assertEqual(count, 1, "Meeting should appear exactly once in the list")
    
    def test_format_for_digest_helper(self):
        """Test the quick helper function."""
        results = {
            'new_events': 1,
            'urgent_count': 0,
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Test',
                    'start_time': '2025-10-15 10:00 AM',
                    'attendee_email': 'test@example.com',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = format_for_digest(results)
        
        self.assertIn('📅 Meeting Prep Intelligence', section)
        self.assertIn('Test', section)
    
    def test_get_digest_filepath(self):
        """Test digest filepath generation."""
        test_date = datetime(2025, 10, 15, 10, 0, 0, tzinfo=self.et_tz)
        
        filepath = self.formatter.get_digest_filepath(test_date)
        
        self.assertTrue(str(filepath).endswith('digest-2025-10-15.md'))
    
    def test_profile_links_formatted_correctly(self):
        """Test that profile links use correct file mention syntax."""
        results = {
            'new_events': 1,
            'urgent_count': 0,
            'processed_details': [
                {
                    'event_id': 'event1',
                    'summary': 'Meeting',
                    'start_time': '2025-10-15 10:00 AM',
                    'attendee_email': 'john@example.com',
                    'profile_dir': '2025-10-15-john-doe-example',
                    'tags': {'is_critical': False}
                }
            ]
        }
        
        section = self.formatter.format_meeting_section(results)
        
        # Check for proper file mention syntax
        self.assertIn("`file 'N5/records/meetings/", section)
        self.assertIn("/profile.md'`", section)


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDigestFormatter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

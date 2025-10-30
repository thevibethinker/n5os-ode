#!/usr/bin/env python3
"""
Meeting Monitor - Priority 3
Polling loop that checks calendar every 15 minutes for new meetings with N5OS tags.
Detects urgent meetings, generates digest content, and coordinates processing.
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path
import pytz

# Add N5/scripts to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from meeting_processor import MeetingProcessor
from meeting_api_integrator import MeetingAPIIntegrator


class MeetingMonitor:
    """Continuous monitoring system for calendar events with N5OS tags."""
    
    def __init__(self, calendar_tool, gmail_tool, poll_interval_minutes=15, 
                 lookahead_days=7, log_file=None):
        """
        Initialize the meeting monitor.
        
        Args:
            calendar_tool: Zo's use_app_google_calendar function
            gmail_tool: Zo's use_app_gmail function
            poll_interval_minutes: How often to poll (default 15)
            lookahead_days: How far ahead to look for meetings (default 7)
            log_file: Path to log file (default: N5/logs/meeting_monitor.log)
        """
        self.poll_interval_minutes = poll_interval_minutes
        self.lookahead_days = lookahead_days
        self.et_tz = pytz.timezone('America/New_York')
        
        # Set up logging
        if log_file is None:
            log_dir = Path(__file__).parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / 'meeting_monitor.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s ET [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize processor
        api = MeetingAPIIntegrator(calendar_tool, gmail_tool)
        self.processor = MeetingProcessor(api)
        
        self.cycle_count = 0
        self.total_processed = 0
        self.urgent_count = 0
        
    def run_single_cycle(self):
        """
        Run a single monitoring cycle.
        
        Returns:
            dict: Processing results with urgent meeting detection
        """
        self.cycle_count += 1
        cycle_start = datetime.now(self.et_tz)
        
        self.logger.info(f"=== Cycle {self.cycle_count} started at {cycle_start.strftime('%Y-%m-%d %I:%M %p ET')} ===")
        
        try:
            # Process upcoming meetings
            results = self.processor.process_upcoming_meetings(self.lookahead_days)
            
            # Detect urgent meetings
            urgent_meetings = self.detect_urgent_meetings(results)
            results['urgent_meetings'] = urgent_meetings
            results['urgent_count'] = len(urgent_meetings)
            
            # Update totals
            self.total_processed += results['new_events']
            self.urgent_count += results['urgent_count']
            
            # Log results
            self.logger.info(
                f"Cycle complete: {results['total_events']} events checked, "
                f"{results['new_events']} new, {results['already_processed']} already processed, "
                f"{results['urgent_count']} urgent"
            )
            
            if results['errors'] > 0:
                self.logger.warning(f"Encountered {results['errors']} errors during processing")
            
            # Generate digest section if new events
            if results['new_events'] > 0:
                digest_section = self.generate_digest_section(results)
                results['digest_section'] = digest_section
            
            cycle_end = datetime.now(self.et_tz)
            duration = (cycle_end - cycle_start).total_seconds()
            self.logger.info(f"Cycle duration: {duration:.1f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'cycle': self.cycle_count,
                'timestamp': cycle_start.isoformat()
            }
    
    def detect_urgent_meetings(self, results):
        """
        Identify urgent meetings from processing results.
        
        Urgent meetings have priority marker '*' in N5OS tags.
        
        Args:
            results: Processing results from MeetingProcessor
            
        Returns:
            list: List of urgent meeting details
        """
        urgent = []
        
        if 'processed_details' in results:
            for detail in results['processed_details']:
                tags = detail.get('tags', {})
                if tags.get('is_critical', False):
                    urgent.append({
                        'event_id': detail['event_id'],
                        'summary': detail['summary'],
                        'start_time': detail['start_time'],
                        'attendee_email': detail['attendee_email'],
                        'profile_dir': detail.get('profile_dir', ''),
                        'tags': tags
                    })
        
        return urgent
    
    def generate_digest_section(self, results):
        """
        Generate a markdown section for the daily digest.
        
        Args:
            results: Processing results including urgent meetings
            
        Returns:
            str: Markdown formatted digest section
        """
        lines = []
        lines.append("## 📅 Meeting Prep Intelligence")
        lines.append("")
        
        if results['new_events'] == 0:
            lines.append("*No new meetings detected this cycle.*")
            return "\n".join(lines)
        
        lines.append(f"### Upcoming Meetings (Next {self.lookahead_days} Days)")
        lines.append("")
        
        # Show urgent meetings first
        if results.get('urgent_count', 0) > 0:
            lines.append("#### 🚨 Urgent Meetings")
            lines.append("")
            for meeting in results['urgent_meetings']:
                lines.append(f"**[URGENT] {meeting['start_time']} - {meeting['summary']}**")
                lines.append(f"- Stakeholder: {meeting['attendee_email']}")
                if meeting['profile_dir']:
                    profile_path = f"Personal/Meetings/{meeting['profile_dir']}/profile.md"
                    lines.append(f"- Profile: `file '{profile_path}'`")
                lines.append(f"- Tags: {', '.join([f'[{tag}]' for tag in meeting['tags'].get('stakeholder_tags', [])])}")
                lines.append("")
        
        # Show all new meetings
        if 'processed_details' in results and len(results['processed_details']) > 0:
            non_urgent = [d for d in results['processed_details'] 
                         if not d.get('tags', {}).get('is_critical', False)]
            
            if non_urgent:
                if results.get('urgent_count', 0) > 0:
                    lines.append("#### 📋 Normal Priority Meetings")
                    lines.append("")
                
                for detail in non_urgent:
                    lines.append(f"**{detail['start_time']} - {detail['summary']}**")
                    lines.append(f"- Stakeholder: {detail['attendee_email']}")
                    if detail.get('profile_dir'):
                        profile_path = f"Personal/Meetings/{detail['profile_dir']}/profile.md"
                        lines.append(f"- Profile: `file '{profile_path}'`")
                    lines.append("")
        
        # Summary
        lines.append("---")
        lines.append(
            f"*Detected {results['new_events']} new meeting(s) this cycle. "
            f"{results['urgent_count']} urgent, {results['new_events'] - results['urgent_count']} normal priority.*"
        )
        
        return "\n".join(lines)
    
    def run_continuous(self, max_cycles=None):
        """
        Run continuous monitoring loop.
        
        Args:
            max_cycles: Maximum number of cycles to run (None = infinite)
            
        Returns:
            dict: Summary of all cycles
        """
        self.logger.info(
            f"Starting continuous monitoring: "
            f"poll every {self.poll_interval_minutes} min, "
            f"look ahead {self.lookahead_days} days"
        )
        
        cycle_results = []
        
        try:
            while max_cycles is None or self.cycle_count < max_cycles:
                # Run cycle
                result = self.run_single_cycle()
                cycle_results.append(result)
                
                # Check if we should stop
                if max_cycles and self.cycle_count >= max_cycles:
                    break
                
                # Sleep until next cycle
                self.logger.info(f"Sleeping for {self.poll_interval_minutes} minutes...")
                time.sleep(self.poll_interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user (Ctrl+C)")
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring loop: {str(e)}", exc_info=True)
        
        # Generate summary
        summary = {
            'total_cycles': self.cycle_count,
            'total_processed': self.total_processed,
            'total_urgent': self.urgent_count,
            'cycle_results': cycle_results
        }
        
        self.logger.info(
            f"=== Monitoring Summary ===\n"
            f"Total cycles: {self.cycle_count}\n"
            f"Total meetings processed: {self.total_processed}\n"
            f"Total urgent meetings: {self.urgent_count}"
        )
        
        return summary


def main():
    """
    Main entry point for standalone execution.
    This is a demo - in production, Zo will call this with API tools.
    """
    print("Meeting Monitor - Priority 3")
    print("=" * 50)
    print("This script requires Zo API tools to run.")
    print("Use run_meeting_monitor.py with Zo instead.")
    print("=" * 50)


if __name__ == '__main__':
    main()

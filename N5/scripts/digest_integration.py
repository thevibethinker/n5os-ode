#!/usr/bin/env python3
"""
Digest Integration - Priority 3
Formats meeting prep intelligence for inclusion in daily digest.
"""

from datetime import datetime
from pathlib import Path
import pytz


class DigestFormatter:
    """Format meeting monitor results for daily digest."""
    
    def __init__(self):
        self.et_tz = pytz.timezone('America/New_York')
    
    def format_meeting_section(self, monitor_results, include_summary=True):
        """
        Format monitoring results as a digest section.
        
        Args:
            monitor_results: Results from MeetingMonitor.run_single_cycle()
            include_summary: Include summary footer (default True)
            
        Returns:
            str: Markdown formatted section for digest
        """
        if 'digest_section' in monitor_results:
            # Monitor already generated the section
            return monitor_results['digest_section']
        
        # Generate section from results
        lines = []
        lines.append("## 📅 Meeting Prep Intelligence")
        lines.append("")
        
        if monitor_results.get('new_events', 0) == 0:
            lines.append("*No new meetings detected this cycle.*")
            lines.append("")
            return "\n".join(lines)
        
        # Format meetings
        lines.append(f"### New Meetings Detected")
        lines.append("")
        
        # Urgent first
        urgent_count = monitor_results.get('urgent_count', 0)
        if urgent_count > 0:
            lines.append("#### 🚨 Urgent")
            lines.append("")
            
            for meeting in monitor_results.get('urgent_meetings', []):
                lines.append(f"**[URGENT] {meeting['summary']}**")
                lines.append(f"- Time: {meeting['start_time']}")
                lines.append(f"- Stakeholder: {meeting['attendee_email']}")
                
                if meeting.get('profile_dir'):
                    profile_path = f"Personal/Meetings/{meeting['profile_dir']}/profile.md"
                    lines.append(f"- Profile: `file '{profile_path}'`")
                
                lines.append("")
        
        # Normal priority
        if 'processed_details' in monitor_results:
            normal = [d for d in monitor_results['processed_details']
                     if not d.get('tags', {}).get('is_critical', False)]
            
            if normal:
                if urgent_count > 0:
                    lines.append("#### 📋 Normal Priority")
                    lines.append("")
                
                for detail in normal:
                    lines.append(f"**{detail['summary']}**")
                    lines.append(f"- Time: {detail['start_time']}")
                    lines.append(f"- Stakeholder: {detail['attendee_email']}")
                    
                    if detail.get('profile_dir'):
                        profile_path = f"Personal/Meetings/{detail['profile_dir']}/profile.md"
                        lines.append(f"- Profile: `file '{profile_path}'`")
                    
                    lines.append("")
        
        # Summary
        if include_summary:
            lines.append("---")
            lines.append(
                f"*{monitor_results['new_events']} new meeting(s). "
                f"{urgent_count} urgent, "
                f"{monitor_results['new_events'] - urgent_count} normal.*"
            )
            lines.append("")
        
        return "\n".join(lines)
    
    def format_daily_summary(self, all_cycle_results):
        """
        Format a full day's monitoring results.
        
        Args:
            all_cycle_results: List of results from multiple cycles
            
        Returns:
            str: Markdown formatted daily summary
        """
        lines = []
        lines.append("## 📅 Meeting Prep Intelligence - Daily Summary")
        lines.append("")
        
        # Aggregate stats
        total_new = sum(r.get('new_events', 0) for r in all_cycle_results)
        total_urgent = sum(r.get('urgent_count', 0) for r in all_cycle_results)
        total_cycles = len(all_cycle_results)
        
        if total_new == 0:
            lines.append("*No new meetings detected today.*")
            lines.append("")
            return "\n".join(lines)
        
        lines.append(f"**Today's Activity:** {total_cycles} monitoring cycles")
        lines.append(f"**New Meetings:** {total_new} ({total_urgent} urgent)")
        lines.append("")
        
        # Collect all unique meetings
        all_meetings = []
        for result in all_cycle_results:
            if 'processed_details' in result:
                all_meetings.extend(result['processed_details'])
        
        # Deduplicate by event_id
        seen_ids = set()
        unique_meetings = []
        for m in all_meetings:
            if m['event_id'] not in seen_ids:
                unique_meetings.append(m)
                seen_ids.add(m['event_id'])
        
        # Sort by start time
        unique_meetings.sort(key=lambda m: m['start_time'])
        
        # Display urgent first
        urgent_meetings = [m for m in unique_meetings 
                          if m.get('tags', {}).get('is_critical', False)]
        
        if urgent_meetings:
            lines.append("### 🚨 Urgent Meetings")
            lines.append("")
            
            for m in urgent_meetings:
                lines.append(f"**[URGENT] {m['start_time']} - {m['summary']}**")
                lines.append(f"- Stakeholder: {m['attendee_email']}")
                
                if m.get('profile_dir'):
                    profile_path = f"Personal/Meetings/{m['profile_dir']}/profile.md"
                    lines.append(f"- Profile: `file '{profile_path}'`")
                
                lines.append("")
        
        # Display normal priority
        normal_meetings = [m for m in unique_meetings 
                          if not m.get('tags', {}).get('is_critical', False)]
        
        if normal_meetings:
            lines.append("### 📋 Upcoming Meetings")
            lines.append("")
            
            for m in normal_meetings:
                lines.append(f"**{m['start_time']} - {m['summary']}**")
                lines.append(f"- Stakeholder: {m['attendee_email']}")
                
                if m.get('profile_dir'):
                    profile_path = f"Personal/Meetings/{m['profile_dir']}/profile.md"
                    lines.append(f"- Profile: `file '{profile_path}'`")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def get_digest_filepath(self, date=None):
        """
        Get the filepath for today's digest file.
        
        Args:
            date: datetime object (default: today)
            
        Returns:
            Path: Path to digest file
        """
        if date is None:
            date = datetime.now(self.et_tz)
        
        digest_dir = Path(__file__).parent.parent / 'records' / 'digests'
        digest_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"digest-{date.strftime('%Y-%m-%d')}.md"
        return digest_dir / filename
    
    def append_to_digest(self, section_content, date=None):
        """
        Append meeting section to today's digest file.
        
        Args:
            section_content: Markdown content to append
            date: datetime object (default: today)
            
        Returns:
            Path: Path to updated digest file
        """
        filepath = self.get_digest_filepath(date)
        
        # Create or append
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(section_content)
            f.write("\n\n")
        
        return filepath


def format_for_digest(monitor_results):
    """
    Quick helper to format monitor results for digest.
    
    Args:
        monitor_results: Results from MeetingMonitor
        
    Returns:
        str: Formatted markdown section
    """
    formatter = DigestFormatter()
    return formatter.format_meeting_section(monitor_results)

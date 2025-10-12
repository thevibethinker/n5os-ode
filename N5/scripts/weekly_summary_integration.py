#!/usr/bin/env python3
"""
Weekly Summary System - Zo Integration Wrapper
Designed to be executed BY Zo with direct app tool access
"""

import json
import re
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
DIGESTS_DIR = ROOT / "digests"
STATE_DIR = ROOT / "records" / "weekly_summaries"
STATE_FILE = STATE_DIR / ".state.json"
LOG_FILE = ROOT / "logs" / "weekly_summary.log"

# Ensure directories
DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Internal domains to exclude
INTERNAL_DOMAINS = ['@mycareerspan.com', '@theapply.ai']


class WeeklySummaryIntegration:
    """Zo-integrated weekly summary generator"""
    
    def __init__(self, calendar_tool, gmail_tool):
        """
        Initialize with Zo app tools
        
        Args:
            calendar_tool: Function to call use_app_google_calendar
            gmail_tool: Function to call use_app_gmail
        """
        self.calendar_tool = calendar_tool
        self.gmail_tool = gmail_tool
    
    def gather_calendar_events(
        self,
        time_min: str,
        time_max: str
    ) -> List[Dict]:
        """Get calendar events for date range"""
        log.info(f"Querying calendar: {time_min} to {time_max}")
        
        result = self.calendar_tool(
            tool_name='google_calendar-list-events',
            configured_props={
                'calendarId': 'primary',
                'timeMin': time_min,
                'timeMax': time_max,
                'singleEvents': True,
                'maxResults': 100
            }
        )
        
        events = result.get('ret', [])
        log.info(f"Retrieved {len(events)} total events")
        
        return events
    
    def filter_external_events(self, events: List[Dict]) -> List[Dict]:
        """Filter to external events only"""
        external = []
        
        for event in events:
            # Check organizer
            organizer = event.get('organizer', {}).get('email', '')
            organizer_external = not any(d in organizer for d in INTERNAL_DOMAINS)
            
            # Check attendees
            attendees = event.get('attendees', [])
            has_external = False
            
            for attendee in attendees:
                email = attendee.get('email', '')
                if email and not any(d in email for d in INTERNAL_DOMAINS):
                    if email != 'vrijen@mycareerspan.com':
                        has_external = True
                        break
            
            # Include if organizer is external OR has external attendees
            if organizer_external or has_external:
                external.append(event)
        
        log.info(f"Filtered to {len(external)} external events")
        return external
    
    def extract_n5os_tags(self, event: Dict) -> List[str]:
        """Extract N5OS tags from event description"""
        description = event.get('description', '')
        if not description:
            return []
        
        # Pattern for tags
        tag_pattern = r'\[([^\]]+)\]'
        tags = re.findall(tag_pattern, description)
        
        # Check for asterisk
        if '*' in description and '*' not in tags:
            tags.append('*')
        
        return tags
    
    def extract_participants(self, events: List[Dict]) -> Dict[str, List[str]]:
        """
        Extract participants from events
        
        Returns:
            Dict mapping event_id -> list of external participant emails
        """
        event_participants = {}
        
        for event in events:
            event_id = event.get('id', '')
            participants = []
            
            # Check attendees
            for attendee in event.get('attendees', []):
                email = attendee.get('email', '')
                if email and not any(d in email for d in INTERNAL_DOMAINS):
                    if email != 'vrijen@mycareerspan.com':
                        participants.append(email)
            
            # Check organizer
            organizer = event.get('organizer', {}).get('email', '')
            if organizer and not any(d in organizer for d in INTERNAL_DOMAINS):
                if organizer not in participants:
                    participants.append(organizer)
            
            if participants:
                event_participants[event_id] = participants
        
        return event_participants
    
    def get_all_participants(self, event_participants: Dict) -> List[str]:
        """Get unique list of all participants"""
        all_participants = set()
        for participants in event_participants.values():
            all_participants.update(participants)
        return sorted(list(all_participants))
    
    def gather_emails_for_participant(
        self,
        email: str,
        lookback_days: int = 30
    ) -> List[Dict]:
        """Get emails for a specific participant"""
        try:
            # Calculate date
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=lookback_days)
            after_date = start_date.strftime('%Y/%m/%d')
            
            # Query Gmail
            query = f"(from:{email} OR to:{email}) after:{after_date}"
            log.info(f"  Querying Gmail for {email}...")
            
            result = self.gmail_tool(
                tool_name='gmail-find-email',
                configured_props={
                    'q': query,
                    'maxResults': 50,
                    'withTextPayload': True
                }
            )
            
            messages = result.get('ret', [])
            log.info(f"    Found {len(messages)} emails")
            
            return messages
            
        except Exception as e:
            log.error(f"  Error fetching emails for {email}: {e}")
            return []
    
    def analyze_email_volume(
        self,
        emails_by_participant: Dict[str, List[Dict]]
    ) -> List[Tuple[str, int]]:
        """Identify high-activity contacts"""
        activity = []
        
        for email, messages in emails_by_participant.items():
            if len(messages) >= 2:  # Threshold for "high activity"
                activity.append((email, len(messages)))
        
        # Sort by volume
        activity.sort(key=lambda x: x[1], reverse=True)
        return activity
    
    def generate_digest(
        self,
        week_start: datetime,
        week_end: datetime,
        external_events: List[Dict],
        emails_by_participant: Dict[str, List[Dict]],
        high_activity: List[Tuple[str, int]]
    ) -> str:
        """Generate markdown digest"""
        lines = []
        
        # Header
        week_str = f"{week_start.strftime('%b %d')}-{week_end.strftime('%d, %Y')}"
        lines.append(f"# Weekly Summary — Week of {week_str}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"**External Events:** {len(external_events)}")
        lines.append(f"**Email Contacts Analyzed:** {len(emails_by_participant)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Calendar section
        lines.append("## 📅 Calendar Overview")
        lines.append("")
        
        # Group events by day
        events_by_day = defaultdict(list)
        for event in external_events:
            start = event.get('start', {})
            dt_str = start.get('dateTime', '')
            if dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                day_key = dt.strftime('%Y-%m-%d')
                events_by_day[day_key].append(event)
        
        # Display by day
        for day in sorted(events_by_day.keys()):
            dt = datetime.fromisoformat(day + 'T00:00:00')
            day_name = dt.strftime('%A, %B %d')
            lines.append(f"### {day_name}")
            lines.append("")
            
            for event in events_by_day[day]:
                # Format time
                start_time = event.get('start', {}).get('dateTime', '')
                if start_time:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%I:%M %p').lstrip('0')
                else:
                    time_str = "All day"
                
                # Get details
                summary = event.get('summary', 'Untitled')
                tags = self.extract_n5os_tags(event)
                
                # Get participants
                attendees = event.get('attendees', [])
                participants = []
                for att in attendees:
                    email = att.get('email', '')
                    if email and not any(d in email for d in INTERNAL_DOMAINS):
                        if email != 'vrijen@mycareerspan.com':
                            participants.append(email)
                
                # Build line
                line = f"- **{time_str}** - {summary}"
                if tags:
                    line += f" `{' '.join(tags)}`"
                lines.append(line)
                
                # Show participants if any
                if participants:
                    lines.append(f"  - External: {', '.join(participants)}")
                
                # Show email count if available
                for p in participants:
                    if p in emails_by_participant:
                        email_count = len(emails_by_participant[p])
                        lines.append(f"  - Recent emails with {p.split('@')[0]}: {email_count}")
            
            lines.append("")
        
        # Email activity section
        if emails_by_participant:
            lines.append("---")
            lines.append("")
            lines.append("## 📧 Email Activity (Last 30 Days)")
            lines.append("")
            
            if high_activity:
                lines.append("### High Activity Contacts")
                lines.append("")
                for email, count in high_activity[:5]:
                    lines.append(f"- **{email}** ({count} emails)")
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by N5 Weekly Summary System v1.0*")
        
        return '\n'.join(lines)
    
    def save_digest(self, content: str, week_start: datetime):
        """Save digest to file"""
        filename = f"weekly-summary-{week_start.strftime('%Y-%m-%d')}.md"
        filepath = DIGESTS_DIR / filename
        
        filepath.write_text(content)
        log.info(f"Saved digest: {filepath}")
        
        return filepath
    
    def update_state(
        self,
        week_start: datetime,
        week_end: datetime,
        event_count: int,
        email_count: int,
        digest_path: Path
    ):
        """Update state file"""
        # Load existing
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
        else:
            state = {'generation_history': []}
        
        # Add entry
        state['last_generated'] = datetime.now(timezone.utc).isoformat()
        state['generation_history'].append({
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'events_included': event_count,
            'emails_analyzed': email_count,
            'status': 'success',
            'digest_path': str(digest_path.relative_to(ROOT))
        })
        
        # Keep last 10
        state['generation_history'] = state['generation_history'][-10:]
        
        # Save
        STATE_FILE.write_text(json.dumps(state, indent=2))
        log.info(f"Updated state file: {STATE_FILE}")


def run_weekly_summary(
    calendar_tool,
    gmail_tool,
    week_start_date: str,
    lookback_days: int = 30,
    send_email: bool = False
):
    """
    Main execution function called by Zo
    
    Args:
        calendar_tool: Zo's use_app_google_calendar function
        gmail_tool: Zo's use_app_gmail function
        week_start_date: ISO date string (YYYY-MM-DD) for Monday of target week
        lookback_days: Email lookback window
        send_email: Whether to send email or just save to file
    """
    log.info("=" * 70)
    log.info("WEEKLY SUMMARY GENERATION - FULL RUN")
    log.info("=" * 70)
    
    generator = WeeklySummaryIntegration(calendar_tool, gmail_tool)
    
    # Parse dates
    week_start = datetime.fromisoformat(week_start_date).replace(tzinfo=timezone.utc)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59)
    
    log.info(f"Week: {week_start.date()} to {week_end.date()}")
    log.info(f"Email lookback: {lookback_days} days")
    log.info("")
    
    # Step 1: Calendar
    log.info("Phase 1: Gathering calendar events...")
    time_min = week_start.strftime('%Y-%m-%dT00:00:00Z')
    time_max = week_end.strftime('%Y-%m-%dT23:59:59Z')
    
    all_events = generator.gather_calendar_events(time_min, time_max)
    external_events = generator.filter_external_events(all_events)
    
    log.info(f"  ✓ Found {len(external_events)} external events")
    log.info("")
    
    # Step 2: Extract participants
    log.info("Phase 2: Extracting participants...")
    event_participants = generator.extract_participants(external_events)
    all_participants = generator.get_all_participants(event_participants)
    
    log.info(f"  ✓ Identified {len(all_participants)} unique participants")
    log.info("")
    
    # Step 3: Gather emails
    log.info("Phase 3: Gathering email activity...")
    emails_by_participant = {}
    
    for participant in all_participants:
        emails = generator.gather_emails_for_participant(participant, lookback_days)
        if emails:
            emails_by_participant[participant] = emails
    
    log.info(f"  ✓ Analyzed emails for {len(emails_by_participant)} contacts")
    log.info("")
    
    # Step 4: Analyze activity
    log.info("Phase 4: Analyzing email patterns...")
    high_activity = generator.analyze_email_volume(emails_by_participant)
    
    log.info(f"  ✓ Identified {len(high_activity)} high-activity contacts")
    log.info("")
    
    # Step 5: Generate digest
    log.info("Phase 5: Generating digest...")
    digest_content = generator.generate_digest(
        week_start,
        week_end,
        external_events,
        emails_by_participant,
        high_activity
    )
    
    log.info("  ✓ Digest generated")
    log.info("")
    
    # Step 6: Save and deliver
    log.info("Phase 6: Saving and delivering...")
    digest_path = generator.save_digest(digest_content, week_start)
    
    # Update state
    generator.update_state(
        week_start,
        week_end,
        len(external_events),
        len(emails_by_participant),
        digest_path
    )
    
    log.info("")
    log.info("=" * 70)
    log.info("WEEKLY SUMMARY COMPLETE")
    log.info("=" * 70)
    log.info(f"Digest saved to: {digest_path}")
    
    if send_email:
        log.info("Email delivery: ENABLED (would send via send_email_to_user)")
    else:
        log.info("Email delivery: SKIPPED (--no-email flag)")
    
    return {
        'digest_path': str(digest_path),
        'events': len(external_events),
        'participants': len(all_participants),
        'emails_analyzed': len(emails_by_participant),
        'high_activity_contacts': len(high_activity),
        'content': digest_content
    }


if __name__ == '__main__':
    print("=" * 70)
    print("Weekly Summary Integration v1.0")
    print("=" * 70)
    print("")
    print("This script is designed to be called BY Zo with app tools.")
    print("It cannot run standalone - Zo must execute it with tool access.")
    print("")
    print("Example Zo execution:")
    print("  run_weekly_summary(")
    print("      calendar_tool=use_app_google_calendar,")
    print("      gmail_tool=use_app_gmail,")
    print("      week_start_date='2025-10-14',")
    print("      lookback_days=30,")
    print("      send_email=False")
    print("  )")
    print("")

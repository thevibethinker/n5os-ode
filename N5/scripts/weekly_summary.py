#!/usr/bin/env python3
"""
Weekly Summary System - Main Orchestrator

Generates weekly calendar and email summaries for advance visibility
and builds compounding relationship dossiers over time.

Version: 1.0.0
Aligned with: Architectural Principles v2.0
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from email_analyzer import EmailAnalyzer

# Paths
ROOT = Path(__file__).resolve().parents[1]
DIGESTS_DIR = ROOT / "digests"
STATE_DIR = ROOT / "records" / "weekly_summaries"
STATE_FILE = STATE_DIR / ".state.json"
LOG_FILE = ROOT / "logs" / "weekly_summary.log"

# Ensure directories exist
DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class WeeklySummaryGenerator:
    """Generate weekly summaries with calendar and email analysis"""
    
    def __init__(
        self,
        calendar_tool=None,
        gmail_tool=None,
        dry_run: bool = False
    ):
        """
        Initialize weekly summary generator
        
        Args:
            calendar_tool: Zo's Google Calendar API tool
            gmail_tool: Zo's Gmail API tool
            dry_run: If True, preview without writes/API calls
        """
        self.calendar_tool = calendar_tool
        self.gmail_tool = gmail_tool
        self.dry_run = dry_run
        self.email_analyzer = EmailAnalyzer(gmail_tool)
        
    def generate_summary(
        self,
        week_start: Optional[datetime] = None,
        lookback_days: int = 30
    ) -> str:
        """
        Generate weekly summary
        
        Args:
            week_start: Start of week (Monday), defaults to next Monday
            lookback_days: Days to analyze emails (default: 30)
            
        Returns:
            Markdown digest content
        """
        log.info("=" * 60)
        log.info("Weekly Summary Generation Started")
        log.info("=" * 60)
        
        # Determine week range
        if not week_start:
            week_start = self._get_next_monday()
        week_end = week_start + timedelta(days=6)
        
        log.info(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        log.info(f"Email lookback: {lookback_days} days")
        log.info(f"Dry-run mode: {self.dry_run}")
        log.info("")
        
        # Phase 1: Gather calendar events
        log.info("Phase 1: Gathering calendar events...")
        calendar_events = self._gather_calendar_events(week_start, week_end)
        log.info(f"  ✓ Found {len(calendar_events)} external events with N5OS tags")
        
        # Phase 2: Extract participants
        log.info("Phase 2: Extracting meeting participants...")
        participants = self._extract_participants(calendar_events)
        log.info(f"  ✓ Identified {len(participants)} unique participants")
        
        # Phase 3: Gather email activity
        log.info("Phase 3: Gathering email activity...")
        email_data = self._gather_email_activity(participants, lookback_days)
        log.info(f"  ✓ Analyzed emails for {len(email_data)} contacts")
        
        # Phase 4: Analyze emails
        log.info("Phase 4: Analyzing email patterns...")
        email_analysis = self.email_analyzer.analyze_email_activity(email_data)
        high_activity = self.email_analyzer.identify_high_activity_contacts(email_analysis)
        key_threads = self.email_analyzer.identify_key_threads(email_data)
        log.info(f"  ✓ Identified {len(high_activity)} high-activity contacts")
        log.info(f"  ✓ Surfaced {len(key_threads)} key email threads")
        
        # Phase 5: Generate digest
        log.info("Phase 5: Generating digest markdown...")
        digest_content = self._generate_digest(
            week_start=week_start,
            week_end=week_end,
            calendar_events=calendar_events,
            email_analysis=email_analysis,
            high_activity=high_activity,
            key_threads=key_threads
        )
        log.info("  ✓ Digest generated")
        
        # Phase 6: Deliver (if not dry-run)
        if not self.dry_run:
            log.info("Phase 6: Delivering digest...")
            self._deliver_digest(digest_content, week_start)
            log.info("  ✓ Digest delivered and saved")
            
            # Update state
            self._update_state(week_start, len(calendar_events), len(email_data))
            log.info("  ✓ State file updated")
        else:
            log.info("Phase 6: Skipped (dry-run mode)")
        
        log.info("")
        log.info("=" * 60)
        log.info("Weekly Summary Generation Complete")
        log.info("=" * 60)
        
        return digest_content
    
    def _get_next_monday(self) -> datetime:
        """Get next Monday's date"""
        today = datetime.now(timezone.utc).date()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target is today or in the past
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        return datetime.combine(next_monday, datetime.min.time(), tzinfo=timezone.utc)
    
    def _gather_calendar_events(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict]:
        """
        Gather calendar events for date range
        
        Only returns external events with N5OS tags
        """
        if self.dry_run or not self.calendar_tool:
            log.info("  (Dry-run: would query Google Calendar API)")
            return []
        
        try:
            # Query Google Calendar
            results = self.calendar_tool('google_calendar-list-events', {
                'calendarId': 'primary',
                'timeMin': start.isoformat(),
                'timeMax': end.isoformat(),
                'singleEvents': True,
                'orderBy': 'startTime'
            })
            
            events = results.get('items', [])
            
            # Filter for external events with N5OS tags
            external_events = []
            for event in events:
                if self._is_external_event(event) and self._has_n5os_tags(event):
                    external_events.append(event)
            
            return external_events
            
        except Exception as e:
            log.error(f"  Error fetching calendar events: {e}")
            return []
    
    def _is_external_event(self, event: Dict) -> bool:
        """Check if event has external attendees"""
        attendees = event.get('attendees', [])
        if not attendees:
            return False
        
        internal_domains = ['@mycareerspan.com', '@theapply.ai']
        
        for attendee in attendees:
            email = attendee.get('email', '')
            if not any(domain in email for domain in internal_domains):
                return True
        
        return False
    
    def _has_n5os_tags(self, event: Dict) -> bool:
        """Check if event has N5OS tags"""
        description = event.get('description', '')
        
        # Look for N5OS tag patterns [LD-XXX], [!!], etc.
        import re
        n5os_pattern = r'\[(LD-[A-Z]{3}|!!|D\d+[+-]?|A-[A-Z]|[A-Z]{3})\]'
        return bool(re.search(n5os_pattern, description))
    
    def _extract_participants(self, events: List[Dict]) -> List[str]:
        """Extract unique participant emails from events"""
        participants = set()
        internal_domains = ['@mycareerspan.com', '@theapply.ai']
        
        for event in events:
            for attendee in event.get('attendees', []):
                email = attendee.get('email', '')
                if email and not any(domain in email for domain in internal_domains):
                    participants.add(email)
        
        return list(participants)
    
    def _gather_email_activity(
        self,
        participants: List[str],
        lookback_days: int
    ) -> Dict[str, List[Dict]]:
        """Gather email activity for participants + CRM contacts"""
        if self.dry_run:
            log.info(f"  (Dry-run: would query Gmail for {len(participants)} participants)")
            return {}
        
        # Add CRM contacts (hardcoded for now, could load from file)
        crm_contacts = [
            'hamoon@futurefit.ai',  # Example CRM contact
        ]
        
        all_contacts = list(set(participants + crm_contacts))
        
        return self.email_analyzer.get_emails_for_multiple_people(
            all_contacts,
            lookback_days
        )
    
    def _generate_digest(
        self,
        week_start: datetime,
        week_end: datetime,
        calendar_events: List[Dict],
        email_analysis: Dict,
        high_activity: List[Tuple],
        key_threads: List[Dict]
    ) -> str:
        """Generate markdown digest"""
        lines = []
        
        # Header
        week_str = f"{week_start.strftime('%b %d')}-{week_end.strftime('%d, %Y')}"
        lines.append(f"# Weekly Summary — Week of {week_str}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"**External Events:** {len(calendar_events)}")
        lines.append(f"**Email Contacts Analyzed:** {len(email_analysis)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Calendar Overview
        lines.append("## 📅 Calendar Overview")
        lines.append("")
        
        if not calendar_events:
            lines.append("No external events with N5OS tags scheduled for this week.")
            lines.append("")
        else:
            # Group by day
            events_by_day = self._group_events_by_day(calendar_events)
            
            for day_str, day_events in sorted(events_by_day.items()):
                day_name = datetime.fromisoformat(day_str).strftime('%A, %B %d')
                lines.append(f"### {day_name}")
                for event in day_events:
                    lines.extend(self._format_calendar_event(event, email_analysis))
                lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Email Activity
        lines.append("## 📧 Email Activity (Last 30 Days)")
        lines.append("")
        
        if not high_activity:
            lines.append("No significant email activity with meeting participants.")
            lines.append("")
        else:
            lines.append("### High Activity Contacts")
            for i, (email, data) in enumerate(high_activity[:5], 1):
                name = self._extract_name_from_email(email)
                count = data.get('email_count', 0)
                last_contact = data.get('last_contact', 'Unknown')
                topics = ', '.join(data.get('topics', [])[:3])
                
                lines.append(f"{i}. **{name}** ({count} emails)")
                if topics:
                    lines.append(f"   - Topics: {topics}")
                lines.append(f"   - Last contact: {last_contact}")
                lines.append("")
        
        if key_threads:
            lines.append("### Key Email Threads")
            for thread in key_threads[:5]:
                participant = self._extract_name_from_email(thread['participant'])
                subject = thread.get('subject', 'No subject')
                lines.append(f"- **\"{subject}\"** with {participant}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Week Ahead Summary
        lines.append("## 📊 Week Ahead Summary")
        lines.append("")
        lines.append(f"**External meetings:** {len(calendar_events)}")
        
        # Count N5OS tags
        tag_counts = self._count_n5os_tags(calendar_events)
        if tag_counts:
            lines.append("**N5OS tag breakdown:**")
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- `{tag}`: {count} meeting(s)")
        
        # Busiest day
        if calendar_events:
            events_by_day = self._group_events_by_day(calendar_events)
            busiest = max(events_by_day.items(), key=lambda x: len(x[1]))
            busiest_day = datetime.fromisoformat(busiest[0]).strftime('%A')
            busiest_count = len(busiest[1])
            lines.append(f"**Busiest day:** {busiest_day} ({busiest_count} meetings)")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by N5 Weekly Summary System v1.0*")
        
        return '\n'.join(lines)
    
    def _group_events_by_day(self, events: List[Dict]) -> Dict[str, List[Dict]]:
        """Group events by day"""
        by_day = {}
        for event in events:
            start = event.get('start', {})
            date_str = start.get('dateTime', start.get('date', ''))
            if date_str:
                day = date_str.split('T')[0]
                if day not in by_day:
                    by_day[day] = []
                by_day[day].append(event)
        return by_day
    
    def _format_calendar_event(
        self,
        event: Dict,
        email_analysis: Dict
    ) -> List[str]:
        """Format single calendar event"""
        lines = []
        
        # Time and title
        start = event.get('start', {})
        time_str = start.get('dateTime', '')
        if time_str:
            time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            time_display = time_obj.strftime('%I:%M %p')
        else:
            time_display = 'All day'
        
        summary = event.get('summary', 'No title')
        
        # Extract N5OS tags
        description = event.get('description', '')
        import re
        tags = re.findall(r'\[([^\]]+)\]', description)
        tags_str = ' '.join(f'`[{tag}]`' for tag in tags) if tags else ''
        
        # Get attendee names
        attendees = event.get('attendees', [])
        external_attendees = [
            a.get('email', '') for a in attendees
            if '@mycareerspan.com' not in a.get('email', '') and 
               '@theapply.ai' not in a.get('email', '')
        ]
        attendee_names = ', '.join(self._extract_name_from_email(e) for e in external_attendees[:2])
        
        lines.append(f"- **{time_display}** - {attendee_names} | {summary} | {tags_str}")
        
        # Add email context if available
        for email in external_attendees:
            if email in email_analysis:
                data = email_analysis[email]
                email_count = data.get('email_count', 0)
                last_contact = data.get('last_contact', 'Unknown')
                lines.append(f"  - Recent emails: {email_count} (last: {last_contact})")
                break
        
        return lines
    
    def _count_n5os_tags(self, events: List[Dict]) -> Dict[str, int]:
        """Count occurrences of N5OS tags"""
        tag_counts = {}
        import re
        
        for event in events:
            description = event.get('description', '')
            tags = re.findall(r'\[([^\]]+)\]', description)
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return tag_counts
    
    def _extract_name_from_email(self, email: str) -> str:
        """Extract name from email address"""
        if '@' in email:
            local_part = email.split('@')[0]
            # Replace dots/underscores with spaces and title case
            name = local_part.replace('.', ' ').replace('_', ' ').title()
            return name
        return email
    
    def _deliver_digest(self, content: str, week_start: datetime):
        """Save digest and email to V"""
        # Save to file
        filename = f"weekly-summary-{week_start.strftime('%Y-%m-%d')}.md"
        filepath = DIGESTS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log.info(f"  Saved digest: {filepath}")
        
        # Email to V (would use send_email_to_user tool)
        log.info("  Email delivery: Would send via send_email_to_user")
        # In actual implementation:
        # send_email_to_user(
        #     subject=f"Weekly Summary - {week_start.strftime('%b %d, %Y')}",
        #     markdown_body=content
        # )
    
    def _update_state(
        self,
        week_start: datetime,
        event_count: int,
        email_count: int
    ):
        """Update state file"""
        # Load existing state
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {
                'generation_history': []
            }
        
        # Add this generation
        week_end = week_start + timedelta(days=6)
        state['last_generated'] = datetime.now(timezone.utc).isoformat()
        state['generation_history'].append({
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'events_included': event_count,
            'emails_analyzed': email_count,
            'status': 'success',
            'digest_path': f"N5/digests/weekly-summary-{week_start.strftime('%Y-%m-%d')}.md"
        })
        
        # Keep last 10 entries
        state['generation_history'] = state['generation_history'][-10:]
        
        # Save
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate weekly summary with calendar and email analysis"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without API calls or writes'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect next week (for scheduled tasks)'
    )
    parser.add_argument(
        '--week-of',
        type=str,
        help='Generate for specific week (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--lookback-days',
        type=int,
        default=30,
        help='Email analysis window (default: 30)'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email delivery (save to file only)'
    )
    
    args = parser.parse_args()
    
    # Determine week start
    week_start = None
    if args.week_of:
        week_start = datetime.fromisoformat(args.week_of).replace(tzinfo=timezone.utc)
    
    # For now, in standalone mode, we can't access Zo tools
    # This would be called FROM Zo with tools injected
    print("Weekly Summary System v1.0.0")
    print("=" * 60)
    print("NOTE: This script is designed to be called by Zo")
    print("      with access to Google Calendar and Gmail APIs.")
    print("")
    print("To run manually:")
    print("  1. Ensure you have API access")
    print("  2. Call from Zo context with tools available")
    print("")
    print(f"Dry-run: {args.dry_run}")
    print(f"Auto mode: {args.auto}")
    print(f"Week of: {args.week_of if args.week_of else 'next Monday'}")
    print(f"Email lookback: {args.lookback_days} days")
    print("=" * 60)
    
    # In dry-run mode, show what would happen
    if args.dry_run:
        generator = WeeklySummaryGenerator(dry_run=True)
        digest = generator.generate_summary(week_start, args.lookback_days)
        print("\nDRY-RUN PREVIEW:")
        print("-" * 60)
        print(digest[:500] + "...(truncated)")
        print("-" * 60)
        print("\nTo run for real, remove --dry-run flag and call from Zo.")
    else:
        print("\nError: Must be called from Zo context with API tools.")
        print("Try running with --dry-run to see preview.")
        sys.exit(1)


if __name__ == "__main__":
    main()

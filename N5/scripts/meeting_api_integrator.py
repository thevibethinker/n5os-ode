#!/usr/bin/env python3
"""
Meeting API Integrator - Google Calendar and Gmail Integration
"""

import os
import json
import logging
import pytz
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Parse timezone from config
if TIMEZONE == 'UTC':
    TZ = pytz.UTC
else:
    TZ = pytz.timezone(TIMEZONE)


class MeetingAPIIntegrator:
    """
    Integrates with Google Calendar and Gmail APIs to fetch meeting data
    """
    
    def __init__(self, calendar_tool, gmail_tool):
        """
        Initialize with Zo's app tool functions
        
        Args:
            calendar_tool: Function to call Google Calendar API
            gmail_tool: Function to call Gmail API
        """
        self.calendar_tool = calendar_tool
        self.gmail_tool = gmail_tool
    
    def fetch_upcoming_meetings(self, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming meetings from Google Calendar
        
        Args:
            days_ahead: Number of days ahead to look for meetings
        
        Returns:
            List of calendar events with N5OS tags
        """
        # Calculate time range
        now = datetime.now(TZ)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days_ahead)).isoformat()
        
        print(f"🔍 Fetching calendar events from {now.strftime('%Y-%m-%d')} to {(now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')}")
        
        try:
            # Call Google Calendar API
            result = self.calendar_tool(
                tool_name='google_calendar-list-events',
                configured_props={
                    'calendarId': 'primary',
                    'timeMin': time_min,
                    'timeMax': time_max,
                    'singleEvents': True,
                    'orderBy': 'startTime',
                    'maxResults': 50
                }
            )
            
            # Parse result
            if isinstance(result, str):
                result = json.loads(result)
            
            events = result.get('items', [])
            print(f"   ✓ Found {len(events)} calendar events")
            
            # Filter events with N5OS tags
            tagged_events = []
            for event in events:
                if self._has_vos_tags(event):
                    tagged_events.append(event)
            
            print(f"   ✓ {len(tagged_events)} events have N5OS tags")
            return tagged_events
        
        except Exception as e:
            print(f"   ✗ Error fetching calendar events: {e}")
            return []
    
    def _has_vos_tags(self, event: Dict) -> bool:
        """Check if event has N5OS tags in description"""
        description = event.get('description', '')
        
        # Look for N5OS stakeholder tags
        vos_tags = ['LD-INV', 'LD-HIR', 'LD-COM', 'LD-NET', 'LD-GEN']
        return any(tag in description for tag in vos_tags)
    
    def extract_event_details(self, event: Dict) -> Dict:
        """
        Extract structured details from calendar event
        
        Args:
            event: Raw calendar event from API
        
        Returns:
            Structured event details
        """
        # Extract basic info
        event_id = event.get('id', '')
        summary = event.get('summary', 'Untitled Meeting')
        description = event.get('description', '')
        start_time = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
        
        # Extract attendees
        attendees = []
        for attendee in event.get('attendees', []):
            # Skip self
            if attendee.get('self', False):
                continue
            attendees.append({
                'email': attendee.get('email', ''),
                'name': attendee.get('displayName', attendee.get('email', '')),
                'responseStatus': attendee.get('responseStatus', 'needsAction')
            })
        
        # Extract N5OS tags
        tags = self._extract_vos_tags(description)
        
        # Extract Purpose and Context
        purpose, context = self._extract_purpose_context(description)
        
        return {
            'id': event_id,
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time},
            'attendees': attendees,
            'tags': tags,
            'purpose': purpose,
            'context': context
        }
    
    def _extract_vos_tags(self, description: str) -> Dict:
        """Extract N5OS tags from description"""
        tags = {
            'stakeholder': '',
            'timing': '',
            'priority': 'normal',
            'accommodation': 'A-0'
        }
        
        # Extract stakeholder type
        for tag in ['LD-INV', 'LD-HIR', 'LD-COM', 'LD-NET', 'LD-GEN']:
            if tag in description:
                tags['stakeholder'] = tag
                break
        
        # Extract timing (e.g., D5+, D3)
        timing_match = re.search(r'\[(D\d+\+?)\]', description)
        if timing_match:
            tags['timing'] = timing_match.group(1)
        
        # Check for priority marker (*)
        first_line = description.split('\n')[0] if description else ''
        if '*' in first_line:
            tags['priority'] = 'critical'
        
        # Extract accommodation (A-0, A-1, A-2)
        accom_match = re.search(r'\[(A-[012])\]', description)
        if accom_match:
            tags['accommodation'] = accom_match.group(1)
        
        return tags
    
    def _extract_purpose_context(self, description: str) -> tuple:
        """Extract Purpose and Context from description"""
        purpose = "TBD"
        context = "TBD"
        
        lines = description.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('Purpose:'):
                purpose = line.replace('Purpose:', '').strip()
            elif line.startswith('Context:'):
                # Context might span multiple lines
                context_lines = [line.replace('Context:', '').strip()]
                j = i + 1
                while j < len(lines) and lines[j].strip() and not lines[j].startswith('---'):
                    context_lines.append(lines[j].strip())
                    j += 1
                context = ' '.join(context_lines)
        
        return purpose, context
    
    def search_gmail_for_attendee(self, attendee_email: str, max_results: int = 10) -> Dict:
        """
        Search Gmail for email threads with attendee
        
        Args:
            attendee_email: Email address to search for
            max_results: Maximum number of email threads to return
        
        Returns:
            Dict with email context
        """
        print(f"   📧 Searching Gmail for: {attendee_email}")
        
        try:
            # Search for emails with this attendee
            result = self.gmail_tool(
                tool_name='gmail-find-email',
                configured_props={
                    'q': f'from:{attendee_email} OR to:{attendee_email}',
                    'maxResults': max_results,
                    'withTextPayload': True
                }
            )
            
            # Parse result
            if isinstance(result, str):
                result = json.loads(result)
            
            messages = result.get('messages', [])
            print(f"      ✓ Found {len(messages)} email threads")
            
            # Extract thread summaries
            threads = []
            for msg in messages[:max_results]:
                thread = self._extract_email_summary(msg)
                if thread:
                    threads.append(thread)
            
            return {'threads': threads}
        
        except Exception as e:
            print(f"      ✗ Error searching Gmail: {e}")
            return {'threads': []}
    
    def _extract_email_summary(self, message: Dict) -> Optional[Dict]:
        """Extract summary from email message"""
        try:
            # Get date
            internal_date = message.get('internalDate', '0')
            date = datetime.fromtimestamp(int(internal_date) / 1000, tz=TZ)
            date_str = date.strftime('%Y-%m-%d')
            
            # Get subject
            headers = message.get('payload', {}).get('headers', [])
            subject = 'No Subject'
            for header in headers:
                if header.get('name', '').lower() == 'subject':
                    subject = header.get('value', 'No Subject')
                    break
            
            # Get snippet
            snippet = message.get('snippet', '')
            
            # Limit snippet length
            if len(snippet) > 200:
                snippet = snippet[:200] + '...'
            
            return {
                'date': date_str,
                'subject': subject,
                'snippet': snippet
            }
        
        except Exception as e:
            print(f"      ⚠️  Error extracting email summary: {e}")
            return None


def create_integrator_from_zo_tools(use_app_google_calendar, use_app_gmail):
    """
    Factory function to create integrator with Zo's app tools
    
    Args:
        use_app_google_calendar: Zo's Google Calendar tool function
        use_app_gmail: Zo's Gmail tool function
    
    Returns:
        MeetingAPIIntegrator instance
    """
    return MeetingAPIIntegrator(
        calendar_tool=use_app_google_calendar,
        gmail_tool=use_app_gmail
    )


if __name__ == "__main__":
    print("Meeting API Integrator module loaded")
    print("Use create_integrator_from_zo_tools() to create instance with Zo's tools")

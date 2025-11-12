#!/usr/bin/env python3
"""
Meeting Prep Digest V2 - Energizing, Possibility-Focused Format
Integrates LinkedIn intelligence and Careerspan value mapping for actionable meeting briefs.

Author: N5 OS
Version: 2.0.0
Date: 2025-10-14
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
import json
import re

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))

# Import existing helpers from original meeting_prep_digest
try:
    from meeting_prep_digest import (
        fetch_calendar_events,
        filter_external_meetings,
        get_last_3_interactions,
        get_stakeholder_profile_path,
        is_internal_email,
        ET_TZ,
        research_stakeholder
    )
    HELPERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import original helpers: {e}")
    HELPERS_AVAILABLE = False
    
    # Stub functions
    def fetch_calendar_events(date): return []
    def filter_external_meetings(meetings): return meetings
    def get_last_3_interactions(email): return []
    def get_stakeholder_profile_path(email): return None
    def is_internal_email(email): return False

# Import new modules
from n5_linkedin_intel import LinkedInIntel
from n5_careerspan_value_mapper import CareerSpanValueMapper

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Constants
DIGESTS_DIR = Path("/home/workspace/N5/digests")
PROFILES_DIR = Path("/home/workspace/Knowledge/crm/individuals")


class MeetingPrepDigestV2:
    """
    Generate energizing, possibility-focused meeting prep digests.
    
    Key Features:
    - LinkedIn intelligence (posts, DMs, profile changes)
    - Careerspan value mapping (how we can help them)
    - Strategic moves (concrete actions)
    - Auto-profile enrichment
    - Clean, scannable format
    """
    
    def __init__(self, view_webpage_tool: Optional[Callable] = None):
        """
        Initialize digest generator.
        
        Args:
            view_webpage_tool: Function to fetch webpages (for LinkedIn scraping)
                             Signature: view_webpage_tool(url: str) -> Dict
        """
        self.view_webpage_tool = view_webpage_tool
        self.linkedin_intel = LinkedInIntel(view_webpage_tool=view_webpage_tool)
        self.value_mapper = CareerSpanValueMapper()
        self.profiles_dir = Path("/home/workspace/Knowledge/crm/individuals")
    
    def generate_digest(
        self,
        target_date: str,
        enrich_profiles: bool = True,
        dry_run: bool = False
    ) -> Optional[Path]:
        """
        Main entry point: Generate meeting prep digest for target date.
        
        Args:
            target_date: Date string (YYYY-MM-DD)
            enrich_profiles: Whether to auto-enrich profiles with new intel
            dry_run: Preview without saving
        
        Returns:
            Path to saved digest file (or None if dry-run)
        """
        logger.info(f"Generating meeting prep digest for {target_date}")
        
        # Fetch calendar events
        meetings = self._fetch_meetings(target_date)
        
        if not meetings:
            logger.info("No external meetings found")
            content = self._format_empty_digest(target_date)
        else:
            logger.info(f"Found {len(meetings)} external meetings")
            content = self._generate_digest_content(meetings, target_date, enrich_profiles, dry_run)
        
        if dry_run:
            logger.info("[DRY RUN] Would save digest")
            print(content)
            return None
        
        # Save digest
        output_path = DIGESTS_DIR / f"daily-meeting-prep-{target_date}.md"
        DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        logger.info(f"Saved digest: {output_path}")
        
        return output_path
    
    def _fetch_meetings(self, target_date: str) -> List[Dict]:
        """Fetch calendar events and filter to external meetings."""
        if not HELPERS_AVAILABLE:
            logger.warning("Using stub calendar data - implement Google Calendar API integration")
            return []
        
        try:
            # Parse date
            date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            # Fetch from calendar
            all_meetings = fetch_calendar_events(date_obj)
            
            # Filter to external only
            external_meetings = filter_external_meetings(all_meetings)
            
            logger.info(f"Filtered to {len(external_meetings)} external meeting(s)")
            return external_meetings
            
        except Exception as e:
            logger.error(f"Error fetching meetings: {e}", exc_info=True)
            return []
    
    def _generate_digest_content(
        self,
        meetings: List[Dict],
        target_date: str,
        enrich_profiles: bool,
        dry_run: bool
    ) -> str:
        """Generate the full digest markdown content."""
        
        # Parse date for formatting
        date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        formatted_date = date_obj.strftime('%b %d')
        
        # Generate briefs for each meeting
        briefs = []
        for meeting in meetings:
            brief = self._generate_meeting_brief(meeting, enrich_profiles, dry_run)
            if brief:
                briefs.append(brief)
        
        # Format digest
        lines = []
        
        # Header
        lines.append(f"# Your Meetings — {day_name}, {formatted_date}\n")
        
        if not briefs:
            lines.append("**No external meetings today**\n")
        else:
            # Summary stats
            total = len(briefs)
            lines.append(f"**{total} conversation{'s' if total > 1 else ''}**\n")
        
        lines.append("---\n")
        
        # Meeting briefs
        for brief in briefs:
            lines.append(brief)
            lines.append("\n---\n")
        
        # Footer
        lines.append("\n## Digest Info\n")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        lines.append(f"**Intelligence sources:** Calendar, Gmail, CRM profiles, LinkedIn activity")
        lines.append(f"**Meetings analyzed:** {total if briefs else 0}")
        
        return '\n'.join(lines)
    
    def _generate_meeting_brief(
        self,
        meeting: Dict,
        enrich_profiles: bool,
        dry_run: bool
    ) -> Optional[str]:
        """Generate a single meeting brief with intelligence."""
        
        # Extract meeting info
        time = meeting.get('start_time', 'TBD')
        title = meeting.get('summary', 'Untitled Meeting')
        attendees = meeting.get('attendees', [])
        description = meeting.get('description', '')
        
        # Get primary attendee (first external)
        primary_attendee = None
        for att in attendees:
            email = att.get('email', '')
            if email and not is_internal_email(email):
                primary_attendee = att
                break
        
        if not primary_attendee:
            logger.warning(f"No external attendee found for: {title}")
            return None
        
        attendee_email = primary_attendee.get('email', '')
        attendee_name = primary_attendee.get('displayName', attendee_email.split('@')[0])
        
        # Load profile
        profile_data = self._load_profile(attendee_email)
        if not profile_data:
            logger.warning(f"No profile found for {attendee_email}")
            return self._format_basic_brief(time, attendee_name, title, description)
        
        # Gather intelligence
        email_intel = self._get_email_intelligence(attendee_email)
        linkedin_intel = self._get_linkedin_intelligence(profile_data, attendee_email)
        
        # Generate possibilities (how Careerspan can help)
        possibilities = self.value_mapper.generate_possibilities(
            profile_data,
            linkedin_intel,
            email_intel
        )
        
        # Enrich profile if requested
        if enrich_profiles and not dry_run:
            self._enrich_profile(attendee_email, linkedin_intel, dry_run=dry_run)
        
        # Format brief
        return self._format_enriched_brief(
            time=time,
            name=attendee_name,
            title=title,
            profile_data=profile_data,
            linkedin_intel=linkedin_intel,
            email_intel=email_intel,
            possibilities=possibilities
        )
    
    def _load_profile(self, email: str) -> Optional[Dict]:
        """Load stakeholder profile from CRM."""
        profile_path = get_stakeholder_profile_path(email) if HELPERS_AVAILABLE else None
        
        if not profile_path or not profile_path.exists():
            # Try manual search
            for pf in self.profiles_dir.glob("*.md"):
                content = pf.read_text()
                if email.lower() in content.lower():
                    profile_path = pf
                    break
            else:
                return None
        
        # Parse profile
        content = profile_path.read_text()
        profile_data = {
            'name': profile_path.stem.replace('-', ' ').title(),
            'current_role': self._extract_field(content, 'Current Role'),
            'organization': self._extract_field(content, 'Organization'),
            'relationship_status': self._extract_field(content, 'Relationship Status'),
            'goals': self._extract_list(content, 'Goals'),
            'last_interaction': self._extract_field(content, 'Last Interaction'),
            'raw_content': content
        }
        
        return profile_data
    
    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract a field value from markdown profile."""
        pattern = rf'\*\*{field_name}:\*\*\s*(.+?)(?:\n|$)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract list items from markdown section."""
        items = []
        in_section = False
        
        for line in content.split('\n'):
            if f'## {section_name}' in line:
                in_section = True
                continue
            if in_section:
                if line.startswith('##'):
                    break
                if line.strip().startswith('-'):
                    items.append(line.strip('- ').strip())
        
        return items
    
    def _get_email_intelligence(self, email: str) -> List[Dict]:
        """Get recent email interactions."""
        if not HELPERS_AVAILABLE:
            return []
        
        try:
            interactions = get_last_3_interactions(email)
            return interactions
        except Exception as e:
            logger.error(f"Error fetching email intel: {e}")
            return []
    
    def _get_linkedin_intelligence(self, profile_data: Dict, email: str) -> Dict:
        """Get LinkedIn intelligence (posts, DMs, goals)."""
        # Extract LinkedIn URL from profile
        linkedin_url = self._extract_linkedin_url(profile_data.get('raw_content', ''))
        
        if not linkedin_url or not self.view_webpage_tool:
            logger.info(f"No LinkedIn data available for {email}")
            return {'posts': [], 'messages': [], 'goals': [], 'profile_summary': {}}
        
        try:
            # Fetch LinkedIn data
            posts = self.linkedin_intel.get_recent_posts(linkedin_url)
            messages = self.linkedin_intel.get_linkedin_messages(email, profile_data.get('name', ''))
            goals = self.linkedin_intel.detect_person_goals(linkedin_url, posts)
            profile_summary = self.linkedin_intel.get_profile_summary(linkedin_url)
            
            return {
                'posts': posts,
                'messages': messages,
                'goals': goals,
                'profile_summary': profile_summary
            }
        except Exception as e:
            logger.error(f"Error fetching LinkedIn intel: {e}", exc_info=True)
            return {'posts': [], 'messages': [], 'goals': [], 'profile_summary': {}}
    
    def _extract_linkedin_url(self, content: str) -> Optional[str]:
        """Extract LinkedIn URL from profile content."""
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
        match = re.search(pattern, content)
        return match.group(0) if match else None
    
    def _enrich_profile(self, email: str, linkedin_intel: Dict, dry_run: bool = False):
        """Enrich profile with new LinkedIn intelligence."""
        try:
            success, changes = self.linkedin_intel.enrich_stakeholder_profile(
                email,
                linkedin_intel,
                dry_run=dry_run
            )
            
            if success and changes:
                logger.info(f"Enriched profile for {email}: {changes}")
        except Exception as e:
            logger.error(f"Error enriching profile: {e}")
    
    def _format_basic_brief(self, time: str, name: str, title: str, description: str) -> str:
        """Format a basic brief when no profile exists."""
        lines = []
        lines.append(f"## {time} — {name}")
        lines.append(f"\n**Meeting:** {title}")
        
        if description:
            lines.append(f"\n**Context:**\n{description[:200]}...")
        
        lines.append("\n⚠️ *No profile found - create one to enable full intelligence*")
        
        return '\n'.join(lines)
    
    def _format_enriched_brief(
        self,
        time: str,
        name: str,
        title: str,
        profile_data: Dict,
        linkedin_intel: Dict,
        email_intel: List[Dict],
        possibilities: Dict
    ) -> str:
        """Format a full enriched meeting brief."""
        lines = []
        
        # Header
        org = profile_data.get('organization', '')
        role = profile_data.get('current_role', '')
        header = f"{name}"
        if org:
            header += f" ({org})"
        
        lines.append(f"## {time} — {header}")
        
        if role:
            lines.append(f"*{role}*\n")
        
        # What's Possible (How Careerspan Can Help)
        lines.append("### 🎯 How Careerspan Can Help\n")
        
        value_props = possibilities.get('value_propositions', [])
        if value_props:
            for vp in value_props[:2]:  # Top 2
                goal = vp.get('goal', '')
                solutions = vp.get('solutions', [])
                value = vp.get('value', '')
                
                if goal:
                    lines.append(f"**Their goal:** {goal}")
                if solutions:
                    lines.append(f"**Careerspan solution:** {solutions[0]}")
                if value:
                    lines.append(f"**Value:** {value}")
                lines.append("")
        else:
            lines.append("*Explore their goals and map to Careerspan capabilities*\n")
        
        # Fresh Intel
        lines.append("### 📱 Fresh Intel\n")
        
        # LinkedIn posts
        posts = linkedin_intel.get('posts', [])
        if posts:
            lines.append("**Recent LinkedIn activity:**")
            for post in posts[:2]:  # Top 2
                date = post.get('date', 'Recently')
                preview = post.get('content', '')[:100]
                themes = post.get('themes', [])
                lines.append(f"- {date}: \"{preview}...\"")
                if themes:
                    lines.append(f"  *Themes: {', '.join(themes)}*")
            lines.append("")
        
        # LinkedIn DMs
        messages = linkedin_intel.get('messages', [])
        if messages:
            lines.append("**Recent LinkedIn DMs:**")
            for msg in messages[:2]:
                preview = msg.get('preview', '')[:80]
                lines.append(f"- \"{preview}...\"")
            lines.append("")
        
        # Email context
        if email_intel:
            lines.append("**Recent emails:**")
            for email in email_intel[:2]:
                subject = email.get('subject', 'No subject')
                date = email.get('date', 'Recent')
                lines.append(f"- {date}: {subject}")
            lines.append("")
        
        # Strategic Moves
        lines.append("### 💡 Strategic Moves\n")
        
        moves = possibilities.get('strategic_moves', [])
        if moves:
            for move in moves:
                lines.append(f"- {move}")
        else:
            lines.append("- Ask about their current challenges")
            lines.append("- Share relevant Careerspan capabilities")
            lines.append("- Identify next steps")
        
        return '\n'.join(lines)
    
    def _format_empty_digest(self, target_date: str) -> str:
        """Format digest when no meetings found."""
        date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        formatted_date = date_obj.strftime('%b %d')
        
        lines = []
        lines.append(f"# Your Meetings — {day_name}, {formatted_date}\n")
        lines.append("**No external meetings today** 🎉\n")
        lines.append("---\n")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}")
        
        return '\n'.join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Meeting Prep Digest V2 - Energizing Format")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime('%Y-%m-%d'),
        help="Target date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Skip profile enrichment"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without saving"
    )
    
    args = parser.parse_args()
    
    # Note: In production, view_webpage_tool should be injected by the caller
    # For standalone use, it remains None and LinkedIn features are disabled
    generator = MeetingPrepDigestV2(view_webpage_tool=None)
    
    try:
        output_path = generator.generate_digest(
            args.date,
            enrich_profiles=not args.no_enrich,
            dry_run=args.dry_run
        )
        
        if output_path:
            print(f"✓ Digest saved: {output_path}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to generate digest: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

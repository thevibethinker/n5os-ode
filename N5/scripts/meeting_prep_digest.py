#!/usr/bin/env python3
"""
Meeting Prep Digest Generator

Generates daily meeting intelligence digest with attendee research and email context.
Filters for external stakeholders only, excludes daily recurring meetings.

Usage:
    meeting-prep-digest [--date YYYY-MM-DD] [--dry-run]

Author: N5 OS
Version: 3.0.0 (V-OS Tag Support)
Date: 2025-10-11
"""

import argparse
import json
import logging
import re
import sys
import pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
INTERNAL_DOMAINS = ["mycareerspan.com", "theapply.ai"]
DIGESTS_DIR = Path("/home/workspace/N5/digests")
MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")

# Timezone
ET_TZ = pytz.timezone('America/New_York')

# V-OS Tag System (Howie Integration)
# Lead/Stakeholder types with mappings
LEAD_TYPES = {
    "LD-INV": {"stakeholder": "investor", "type": "discovery", "priority": "critical"},
    "LD-HIR": {"stakeholder": "job_seeker", "type": "discovery"},
    "LD-COM": {"stakeholder": "community", "type": "partnership"},
    "LD-NET": {"stakeholder": "partner", "type": "discovery"},
    "LD-GEN": {"stakeholder": "prospect", "type": "discovery"}
}

# V-OS Tag Categories
TIMING_TAGS = ["!!", "D5", "D5+", "D10"]
STATUS_TAGS = ["OFF", "AWA", "TERM"]
COORD_TAGS = ["LOG", "ILS"]
WEEKEND_TAGS = ["WEX", "WEP"]
ACCOMMODATION_TAGS = ["A-0", "A-1", "A-2"]
PRIORITY_TAGS = ["GPT-I", "GPT-E", "GPT-F"]
FOLLOWUP_TAGS = ["F-", "FL-", "FM-"]

# Daily meeting patterns to exclude
DAILY_PATTERNS = [
    r"daily.*standup",
    r"daily.*sync",
    r"daily.*check",
    r"daily.*team",
    r"morning.*standup",
    r"morning.*sync"
]

# Special event patterns to skip
SKIP_EVENT_PATTERNS = [
    r"\[dw\]",  # Deep work blocks
    r"meeting buffer",
    r"buffer"
]


def get_et_timestamp() -> str:
    """Get current timestamp in ET timezone."""
    now_et = datetime.now(ET_TZ)
    return now_et.strftime('%Y-%m-%d %H:%M:%S %Z')


def validate_date(date_str: str) -> datetime.date:
    """Validate and parse date string."""
    if date_str == "today":
        return datetime.now(ET_TZ).date()
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or 'today'")


def is_daily_recurring(meeting_title: str) -> bool:
    """Check if meeting title matches daily recurring patterns."""
    title_lower = meeting_title.lower()
    return any(re.search(pattern, title_lower, re.IGNORECASE) for pattern in DAILY_PATTERNS)


def should_skip_event(meeting_title: str, description: str, tags: Dict[str, Any]) -> bool:
    """Check if event should be skipped (internal/buffer/postponed/inactive)."""
    title_lower = meeting_title.lower()
    
    # Skip deep work blocks
    if re.search(r'\[dw\]', title_lower, re.IGNORECASE):
        return True
    
    # Skip meeting buffers
    if 'buffer' in title_lower:
        return True
    
    # Skip postponed or inactive events
    if tags.get('status') in ['postponed', 'inactive']:
        return True
    
    return False


def extract_vos_tags(description: str) -> Dict[str, Any]:
    """
    Extract V-OS tags from calendar description.
    Returns structured dict with stakeholder, type, priority, etc.
    
    V-OS Tag Categories:
    - Lead types: [LD-INV], [LD-HIR], [LD-COM], [LD-NET], [LD-GEN]
    - Timing: [!!], [D5], [D5+], [D10]
    - Status: [OFF], [AWA], [TERM]
    - Coordination: [LOG], [ILS]
    - Weekend: [WEX], [WEP]
    - Accommodation: [A-0], [A-1], [A-2]
    - Priority preferences: [GPT-I], [GPT-E], [GPT-F]
    - Follow-up: [F-X], [FL-X], [FM-X]
    
    Activation: Asterisk * at END of tag block indicates active tags
    """
    tags = {
        "stakeholder": None,
        "type": None,
        "priority": "non-critical",
        "status": None,
        "schedule": None,
        "coordination": [],
        "accommodation": None,
        "weekend": None,
        "priority_pref": None,
        "followup": None,
        "active": False
    }
    
    if not description:
        return tags
    
    # Check for activation asterisk
    if '*' in description:
        tags["active"] = True
    
    # Extract lead type (determines stakeholder + type + maybe priority)
    lead_match = re.search(r'\[LD-(INV|HIR|COM|NET|GEN)\]', description, re.IGNORECASE)
    if lead_match:
        lead_key = f"LD-{lead_match.group(1).upper()}"
        if lead_key in LEAD_TYPES:
            lead_info = LEAD_TYPES[lead_key]
            tags["stakeholder"] = lead_info.get("stakeholder")
            tags["type"] = lead_info.get("type")
            if lead_info.get("priority"):
                tags["priority"] = lead_info["priority"]
    
    # Extract timing (!! = critical)
    if re.search(r'\[!!\]', description):
        tags["priority"] = "critical"
        tags["schedule"] = "immediate"
    
    # Extract schedule timing
    if re.search(r'\[D5\]', description):
        tags["schedule"] = "within_5d"
    elif re.search(r'\[D5\+\]', description):
        tags["schedule"] = "5d_plus"
    elif re.search(r'\[D10\]', description):
        tags["schedule"] = "10d_plus"
    
    # Extract status
    if re.search(r'\[OFF\]', description):
        tags["status"] = "postponed"
    elif re.search(r'\[AWA\]', description):
        tags["status"] = "awaiting"
    elif re.search(r'\[TERM\]', description):
        tags["status"] = "inactive"
    
    # Extract coordination
    if re.search(r'\[LOG\]', description):
        tags["coordination"].append("logan")
    if re.search(r'\[ILS\]', description):
        tags["coordination"].append("ilse")
    
    # Extract accommodation
    acc_match = re.search(r'\[A-([012])\]', description)
    if acc_match:
        acc_level = acc_match.group(1)
        if acc_level == "0":
            tags["accommodation"] = "minimal"
        elif acc_level == "1":
            tags["accommodation"] = "baseline"
        elif acc_level == "2":
            tags["accommodation"] = "full"
    
    # Extract weekend
    if re.search(r'\[WEX\]', description):
        tags["weekend"] = "allowed"
    elif re.search(r'\[WEP\]', description):
        tags["weekend"] = "preferred"
    
    # Extract priority preferences
    if re.search(r'\[GPT-I\]', description):
        tags["priority_pref"] = "internal"
    elif re.search(r'\[GPT-E\]', description):
        tags["priority_pref"] = "external"
    elif re.search(r'\[GPT-F\]', description):
        tags["priority_pref"] = "founders"
    
    # Extract follow-up patterns (F-X, FL-X, FM-X where X is number)
    followup_match = re.search(r'\[(F|FL|FM)-(\d+)\]', description)
    if followup_match:
        followup_type = followup_match.group(1)
        followup_days = followup_match.group(2)
        tags["followup"] = {"type": followup_type, "days": int(followup_days)}
    
    return tags


def is_internal_email(email: str) -> bool:
    """Check if email domain is internal."""
    email = email.lower().strip()
    if '@' not in email:
        return False
    domain = email.split('@')[1]
    return domain in INTERNAL_DOMAINS


def extract_external_attendees(attendees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract only external attendees from attendees list."""
    return [
        attendee for attendee in attendees
        if attendee.get('email') and not is_internal_email(attendee['email'])
    ]


def get_stakeholder_profile_path(email: str, name: str = None) -> Optional[Path]:
    """
    Look for existing stakeholder profile in meetings directory.
    
    Searches for:
    - Meeting folders matching email or name
    - stakeholder-profile.md files
    """
    if not MEETINGS_DIR.exists():
        return None
    
    # Search for folders with this stakeholder
    email_local = email.split('@')[0].lower() if email else ""
    name_slug = name.lower().replace(' ', '-') if name else ""
    
    for meeting_folder in MEETINGS_DIR.iterdir():
        if not meeting_folder.is_dir():
            continue
        
        folder_name = meeting_folder.name.lower()
        
        # Check if folder name contains email local or name
        if email_local and email_local in folder_name:
            profile_path = meeting_folder / "stakeholder-profile.md"
            if profile_path.exists():
                return profile_path
        
        if name_slug and name_slug in folder_name:
            profile_path = meeting_folder / "stakeholder-profile.md"
            if profile_path.exists():
                return profile_path
            
            # Also check INTELLIGENCE subfolder
            intel_profile = meeting_folder / "INTELLIGENCE" / "stakeholder-profile.md"
            if intel_profile.exists():
                return intel_profile
    
    return None


def get_last_3_interactions(email: str) -> List[Dict[str, str]]:
    """
    Get last 3 email interactions with this stakeholder.
    
    NOTE: This is a stub. In production, use Gmail API:
    - list_app_tools(app_slug="gmail")
    - use_app_gmail(tool_name="gmail-search-messages", configured_props={"q": f"from:{email} OR to:{email}", "maxResults": 3})
    
    Returns list of {date, subject, context} dicts
    """
    logger.warning(f"Gmail API integration needed - using mock data for {email}")
    
    # Mock data for now
    return [
        {
            "date": "2025-10-08",
            "subject": "Re: Partnership discussion",
            "context": "Confirmed interest in pilot, requested job descriptions"
        },
        {
            "date": "2025-09-15",
            "subject": "Introduction via mutual connection",
            "context": "Initial intro, discussed recruiting challenges"
        },
        {
            "date": "2025-09-02",
            "subject": "Following up on coffee chat",
            "context": "Shared product demo, explored use cases"
        }
    ]


def research_stakeholder(attendee: Dict[str, Any], description: str = "") -> Dict[str, Any]:
    """
    Research a single external stakeholder.
    
    Priority order:
    1. Last 3 email interactions
    2. Calendar description context
    3. Existing stakeholder profile
    4. Past meeting notes
    
    Returns enriched attendee dict with research
    """
    email = attendee.get('email', '')
    name = attendee.get('name', email.split('@')[0] if email else 'Unknown')
    
    logger.info(f"Researching stakeholder: {name} ({email})")
    
    research = {
        "email": email,
        "name": name,
        "last_interactions": [],
        "calendar_context": "",
        "profile_summary": None,
        "past_notes": None
    }
    
    # 1. Get last 3 email interactions
    research["last_interactions"] = get_last_3_interactions(email)
    
    # 2. Extract context from calendar description
    if description:
        # Look for context clues in description
        lines = description.split('\n')
        context_lines = [
            line for line in lines 
            if not line.strip().startswith('#') and len(line.strip()) > 20
        ]
        if context_lines:
            research["calendar_context"] = context_lines[0][:200]  # First substantial line, max 200 chars
    
    # 3. Check for existing stakeholder profile
    profile_path = get_stakeholder_profile_path(email, name)
    if profile_path:
        logger.info(f"Found existing profile: {profile_path}")
        research["profile_path"] = str(profile_path)
        # In production, extract key points from profile
        research["profile_summary"] = f"Existing profile available at {profile_path.relative_to(Path('/home/workspace'))}"
    
    return research


def generate_bluf(meeting: Dict[str, Any], research: List[Dict[str, Any]]) -> str:
    """Generate Bottom Line Up Front summary for meeting using V-OS tag context."""
    title = meeting.get('title', 'Meeting')
    attendee_names = [r['name'] for r in research]
    tags = meeting.get('tags', {})
    
    stakeholder = tags.get('stakeholder')
    meeting_type = tags.get('type')
    accommodation = tags.get('accommodation')
    
    # Stakeholder-specific BLUFs
    if stakeholder == 'investor':
        bluf = f"Investor meeting: {title.lower()} with {' & '.join(attendee_names)}"
    elif stakeholder == 'job_seeker':
        bluf = f"Hiring discussion: evaluate fit for {' & '.join(attendee_names)}"
    elif stakeholder == 'community':
        bluf = f"Community partnership: explore collaboration with {' & '.join(attendee_names)}"
    elif stakeholder == 'partner':
        bluf = f"Partnership discussion: {title.lower()} with {' & '.join(attendee_names)}"
    elif meeting_type == 'discovery':
        bluf = f"Discovery: understand needs and fit for {' & '.join(attendee_names)}"
    else:
        bluf = f"Connect with {' & '.join(attendee_names)} to {title.lower()}"
    
    # Add accommodation context
    if accommodation == 'full':
        bluf += " — Focus: understand their needs and constraints"
    elif accommodation == 'minimal':
        bluf += " — Focus: establish clear value and requirements"
    
    return bluf


def generate_meeting_section(meeting: Dict[str, Any], research: List[Dict[str, Any]]) -> str:
    """Generate streamlined BLUF-format section for one meeting with V-OS tag context."""
    title = meeting.get('title', 'Meeting')
    start_time = meeting.get('start_time', '')
    end_time = meeting.get('end_time', '')
    tags = meeting.get('tags', {})
    description = meeting.get('description', '')
    
    # Format time
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        time_str = start_dt.strftime('%H:%M')
    except:
        time_str = "TBD"
    
    # Build tag string for display (V-OS format)
    tag_parts = []
    if tags.get('stakeholder'):
        tag_parts.append(f"{tags['stakeholder']}")
    if tags.get('type'):
        tag_parts.append(f"{tags['type']}")
    if tags.get('priority') == 'critical':
        tag_parts.append("CRITICAL")
    tag_str = " · ".join(tag_parts) if tag_parts else ""
    
    # Generate BLUF
    bluf = generate_bluf(meeting, research)
    
    # Build section
    section = f"## {time_str} — {title}"
    if tag_str:
        section += f" ({tag_str})"
    section += "\n\n"
    
    section += f"**BLUF:** {bluf}\n\n"
    
    # Last 3 interactions per stakeholder
    section += "**Last 3 interactions:**\n"
    for attendee_research in research:
        name = attendee_research['name']
        interactions = attendee_research.get('last_interactions', [])
        
        if interactions:
            for interaction in interactions[:3]:
                section += f"- {interaction['date']} — {interaction['context']}\n"
        else:
            section += f"- (No recent email history with {name})\n"
    
    section += "\n"
    
    # Calendar context (exclude tags, show purpose)
    if description:
        # Extract purpose line if present
        purpose_match = re.search(r'Purpose:\s*(.+)', description, re.IGNORECASE)
        if purpose_match:
            section += f"**Calendar context:** {purpose_match.group(1).strip()}\n\n"
        else:
            # Extract just the substantial content, not tags
            desc_lines = [
                line for line in description.split('\n')
                if line.strip() 
                and not line.strip().startswith('#')
                and not re.match(r'\[.*\]', line.strip())  # Skip tag lines
                and not line.strip().startswith('---')  # Skip separators
            ]
            if desc_lines:
                section += f"**Calendar context:** {desc_lines[0][:200]}\n\n"
    
    # Check for existing profiles
    profiles_found = [r for r in research if r.get('profile_path')]
    if profiles_found:
        section += "**Past notes:** "
        profile_links = [f"`file '{r['profile_path']}'`" for r in profiles_found]
        section += ", ".join(profile_links) + "\n\n"
    
    # Prep actions (V-OS context-aware)
    section += "**Prep actions:**\n"
    action_num = 1
    
    # Priority-based protection
    if tags.get('priority') == 'critical':
        section += f"{action_num}. ⚠️ CRITICAL: Protect this time block — do not reschedule\n"
        action_num += 1
    
    # Accommodation-based prep
    if tags.get('accommodation') == 'full':
        section += f"{action_num}. Prepare 3+ options showing flexibility\n"
        action_num += 1
    elif tags.get('accommodation') == 'minimal':
        section += f"{action_num}. Prepare 1-2 clear options with non-negotiables\n"
        action_num += 1
    elif tags.get('type') == 'discovery':
        section += f"{action_num}. Prepare 3 questions to qualify fit\n"
        action_num += 1
    elif tags.get('type') == 'partnership':
        section += f"{action_num}. Prepare partnership framework and value proposition\n"
        action_num += 1
    else:
        section += f"{action_num}. Review last interaction and prepare 1-2 specific asks\n"
        action_num += 1
    
    section += f"{action_num}. Set explicit outcome: what decision or next step do you need?\n"
    
    # Coordination notes
    if 'logan' in tags.get('coordination', []):
        section += "\n**Note:** Coordinate with Logan on scheduling and agenda\n"
    if 'ilse' in tags.get('coordination', []):
        section += "\n**Note:** Coordinate with Ilse on scheduling and agenda\n"
    
    # Weekend note
    if tags.get('weekend') == 'preferred':
        section += "\n**Note:** ☀️ Weekend meeting — likely high engagement from their side\n"
    elif tags.get('weekend') == 'allowed':
        section += "\n**Note:** Weekend availability confirmed\n"
    
    section += "\n---\n\n"
    
    return section


def generate_digest(meetings: List[Dict[str, Any]], target_date: datetime.date) -> str:
    """Generate complete daily meeting prep digest."""
    content = f"# Daily Meeting Prep — {target_date}\n\n"
    content += f"**Generated:** {get_et_timestamp()}\n\n"
    
    # Table of contents
    content += "## Today's External Stakeholder Meetings\n\n"
    
    if not meetings:
        content += "*No external stakeholder meetings scheduled for today.*\n\n"
        content += "✨ You have a clear day for deep work!\n\n"
        return content
    
    content += f"**Total:** {len(meetings)} meeting(s)\n\n"
    
    # TOC (chronological)
    for i, meeting in enumerate(meetings, 1):
        start_time = meeting.get('start_time', '')
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            time_str = start_dt.strftime('%H:%M')
        except:
            time_str = "TBD"
        
        title = meeting.get('title', 'Meeting')
        external_count = len(meeting.get('external_attendees', []))
        content += f"{i}. **{time_str}** — {title} ({external_count} external)\n"
    
    content += "\n---\n\n"
    
    # Individual meeting sections
    for meeting in meetings:
        # Research each external attendee
        external_attendees = meeting.get('external_attendees', [])
        research_results = []
        
        for attendee in external_attendees:
            research = research_stakeholder(attendee, meeting.get('description', ''))
            research_results.append(research)
        
        # Generate meeting section
        section = generate_meeting_section(meeting, research_results)
        content += section
    
    # Footer
    content += "---\n\n"
    content += f"*Generated by `meeting-prep-digest` v2.0.0 — {get_et_timestamp()}*\n"
    
    return content


def generate_empty_digest(target_date: datetime.date) -> str:
    """Generate digest when no external meetings found."""
    content = f"# Daily Meeting Prep — {target_date}\n\n"
    content += f"**Generated:** {get_et_timestamp()}\n\n"
    content += "## Today's External Stakeholder Meetings\n\n"
    content += "*No external stakeholder meetings scheduled for today.*\n\n"
    content += "✨ You have a clear day for deep work!\n\n"
    content += "---\n\n"
    content += f"*Generated by `meeting-prep-digest` v2.0.0 — {get_et_timestamp()}*\n"
    return content


def save_digest(content: str, target_date: datetime.date):
    """Save digest to file."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"daily-meeting-prep-{target_date}.md"
    filepath = DIGESTS_DIR / filename
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    logger.info(f"✓ Saved digest: {filepath}")


def fetch_calendar_events(target_date: datetime.date) -> List[Dict[str, Any]]:
    """
    Fetch calendar events from Google Calendar for target date.
    
    NOTE: This is a stub. In production, use Google Calendar API:
    - list_app_tools(app_slug="google_calendar")
    - use_app_google_calendar(
          tool_name="google_calendar-list-events",
          configured_props={
              "calendarId": "primary",
              "timeMin": f"{target_date}T00:00:00-04:00",
              "timeMax": f"{target_date}T23:59:59-04:00",
              "timeZone": "America/New_York"
          }
      )
    
    Returns list of meeting objects with attendees, title, time, description, etc.
    """
    logger.warning("Using mock calendar data - implement Google Calendar API integration")
    
    # Mock data structure
    return [
        {
            "event_id": "evt1",
            "title": "Aniket Partnership Follow-up",
            "start_time": f"{target_date}T09:00:00-04:00",
            "end_time": f"{target_date}T09:30:00-04:00",
            "description": "#stakeholder:partner #type:follow-up\nDiscuss pilot job descriptions and next steps",
            "attendees": [
                {"email": "vrijen@mycareerspan.com", "name": "Vrijen Attawar", "is_organizer": True},
                {"email": "aniket@example.com", "name": "Aniket", "status": "accepted"}
            ]
        }
    ]


def filter_external_meetings(meetings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter meetings to include only:
    1. Meetings with at least one external attendee
    2. Non-daily recurring meetings
    3. Not postponed/inactive (V-OS status tags)
    4. Not internal/buffer events
    
    Returns filtered and enriched list, sorted chronologically.
    """
    filtered = []
    
    for meeting in meetings:
        title = meeting.get('title', '')
        description = meeting.get('description', '')
        
        # Skip daily recurring meetings
        if is_daily_recurring(title):
            logger.info(f"Skipping daily recurring: {title}")
            continue
        
        # Extract V-OS tags from description
        tags = extract_vos_tags(description)
        
        # Skip if should be excluded based on tags/title
        if should_skip_event(title, description, tags):
            logger.info(f"Skipping event: {title} (status: {tags.get('status')})")
            continue
        
        # Extract external attendees
        attendees = meeting.get('attendees', [])
        external_attendees = extract_external_attendees(attendees)
        
        if not external_attendees:
            logger.info(f"Skipping internal-only meeting: {title}")
            continue
        
        # Extract tags from description
        description = meeting.get('description', '')
        tags = extract_vos_tags(description)
        
        # Enrich meeting with external attendees and tags
        meeting['external_attendees'] = external_attendees
        meeting['tags'] = tags
        
        filtered.append(meeting)
    
    # Sort chronologically
    filtered.sort(key=lambda m: m.get('start_time', ''))
    
    logger.info(f"Filtered to {len(filtered)} external meeting(s)")
    
    return filtered


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="today", help="Target date (YYYY-MM-DD or 'today')")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    
    args = parser.parse_args()
    
    try:
        # Parse and validate target date
        target_date = validate_date(args.date)
        
        logger.info(f"Generating meeting prep digest for {target_date}")
        
        # Execute workflow
        meetings = fetch_calendar_events(target_date)
        external_meetings = filter_external_meetings(meetings)
        
        if not external_meetings:
            logger.info("No external meetings found for this date")
            if not args.dry_run:
                digest_content = generate_empty_digest(target_date)
                save_digest(digest_content, target_date)
            else:
                print("\n" + generate_empty_digest(target_date))
            return 0
        
        # Generate digest
        digest_content = generate_digest(external_meetings, target_date)
        
        if args.dry_run:
            logger.info("DRY RUN - Digest preview:")
            print("\n" + digest_content)
        else:
            save_digest(digest_content, target_date)
            logger.info(f"✓ Digest generated: {DIGESTS_DIR / f'daily-meeting-prep-{target_date}.md'}")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

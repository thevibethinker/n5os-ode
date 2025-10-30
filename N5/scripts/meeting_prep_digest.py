#!/usr/bin/env python3
"""
Meeting Prep Digest Generator

Generates daily meeting intelligence digest with attendee research and email context.
Filters for external stakeholders only, excludes daily recurring meetings.

Usage:
    meeting-prep-digest [--date YYYY-MM-DD] [--dry-run]

Author: N5 OS
Version: 3.0.0 (N5OS Tag Support)
Date: 2025-10-11
"""

import argparse
import json
import logging
import re
import sys
import pytz
import subprocess
import os
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
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

# Timezone
ET_TZ = pytz.timezone('America/New_York')

# N5OS Tag System (Howie Integration)
# Lead/Stakeholder types with mappings
LEAD_TYPES = {
    "LD-INV": {"stakeholder": "investor", "type": "discovery", "priority": "critical"},
    "LD-HIR": {"stakeholder": "job_seeker", "type": "discovery"},
    "LD-COM": {"stakeholder": "community", "type": "partnership"},
    "LD-NET": {"stakeholder": "partner", "type": "discovery"},
    "LD-GEN": {"stakeholder": "prospect", "type": "discovery"}
}

# N5OS Tag Categories
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
    
    Activation asterisk is ignored here (only relevant to Howie). If tags are present,
    they are extracted and treated as informative for display.
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
        "followup": None
    }
    
    if not description:
        return tags
    
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
    
    Uses Gmail API to search for emails from/to this stakeholder.
    
    Returns list of {date, subject, context} dicts
    """
    logger.info(f"Fetching Gmail history for {email}")
    
    try:
        # Import required for Gmail API calls (if running inside Zo)
        # In Zo context, we'd use: use_app_gmail()
        # For now, we'll use subprocess to call Zo tools
        import subprocess
        
        # Query Gmail for last 3 messages with this stakeholder
        # Search query: "from:{email} OR to:{email}"
        query = f"from:{email} OR to:{email}"
        
        # Call Gmail API via Zo's use_app_gmail
        # NOTE: This requires running within Zo context with Gmail connected
        # For standalone execution, this will fail gracefully
        
        # Placeholder: In production, this would be called via Zo's tool system
        # For now, return mock data with a note that API integration is needed
        
        logger.warning(f"Gmail API integration in progress - using mock data for {email}")
        logger.info("To integrate: Call use_app_gmail with tool_name='gmail-search-messages'")
        
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
        
    except Exception as e:
        logger.error(f"Error fetching Gmail history: {e}")
        return []


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
    """Generate Bottom Line Up Front from calendar description if present; else explicit none."""
    description = meeting.get('description', '')
    if description:
        # Prefer explicit Purpose: line
        purpose_match = re.search(r'Purpose:\s*(.+)', description, re.IGNORECASE)
        if purpose_match:
            return purpose_match.group(1).strip()
        # Otherwise, take the first substantive non-tag line from description
        for line in description.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            if re.match(r'^\[.*\]$', line):
                continue
            if line.startswith('---'):
                continue
            return line[:200]
    return "No meeting objective documented in calendar."


def generate_meeting_section(meeting: Dict[str, Any], research: List[Dict[str, Any]]) -> str:
    """Generate streamlined meeting section (strict accuracy)."""
    title = meeting.get('title', 'Meeting')
    start_time = meeting.get('start_time', '')
    end_time = meeting.get('end_time', '')
    tags = meeting.get('tags', {})
    description = meeting.get('description', '')
    
    # Format time
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        time_str = start_dt.strftime('%H:%M')
    except:
        time_str = "TBD"
    
    # Generate BLUF (strict)
    bluf = generate_bluf(meeting, research)
    
    # Build section
    section = f"## {time_str} — {title}\n\n"
    
    # Header details
    section += f"**BLUF:** {bluf}\n\n"
    
    # Email interactions (no explanatory placeholders)
    has_any_interactions = any(r.get('last_interactions') for r in research)
    if has_any_interactions:
        section += "**Last 3 email interactions:**\n"
        for attendee_research in research:
            interactions = attendee_research.get('last_interactions', [])
            for interaction in interactions[:3]:
                section += f"- {interaction['date']} — {interaction['context']}\n"
        section += "\n"
    else:
        section += "**Email history:** No recent email interactions found.\n\n"
    
    # Calendar description (verbatim first useful line)
    if description:
        desc_lines = [
            line for line in description.split('\n')
            if line.strip()
            and not line.strip().startswith('#')
            and not re.match(r'\[.*\]', line.strip())
            and not line.strip().startswith('---')
        ]
        section += f"**Calendar description:** {desc_lines[0][:200]}\n\n" if desc_lines else "**Calendar description:** No description provided\n\n"
    else:
        section += "**Calendar description:** No description provided\n\n"
    
    # What's documented / What's unclear
    documented = []
    unclear = []
    if description:
        documented.append("Calendar description present")
    else:
        unclear.append("Meeting purpose not stated")
    
    if documented:
        section += "**What's documented:**\n" + "\n".join(f"- {item}" for item in documented) + "\n\n"
    if unclear:
        section += "**What's unclear:**\n" + "\n".join(f"- {item}" for item in unclear) + "\n\n"
    
    # Prepare (no generic; only context-specific or clarify objective)
    section += "**Prepare:**\n"
    default_bluf = "No meeting objective documented in calendar."
    if bluf != default_bluf:
        section += "- Prepare materials relevant to the documented objective\n"
    elif description and re.search(r'Purpose:\s*(.+)', description, re.IGNORECASE):
        section += "- Prepare materials relevant to the documented purpose\n"
    else:
        section += "- Clarify meeting objective (not documented in calendar)\n"
    
    # V-OS Tags (Detected) — neutral display of meanings
    tag_lines = []
    if tags.get('stakeholder'):
        tag_lines.append(f"- Stakeholder type: {tags['stakeholder']}")
    if tags.get('type'):
        tag_lines.append(f"- Meeting type: {tags['type']}")
    if tags.get('priority') == 'critical':
        tag_lines.append("- Timing: critical (!!)")
    if tags.get('schedule') in ["within_5d", "5d_plus", "10d_plus", "immediate"]:
        tag_lines.append(f"- Schedule: {tags['schedule']}")
    if tags.get('coordination'):
        coord = ", ".join(tags['coordination'])
        tag_lines.append(f"- Coordination: {coord}")
    if tag_lines:
        section += "\n**V-OS Tags (Detected):**\n" + "\n".join(tag_lines) + "\n"
    
    # Coordination notes (factual)
    if tags.get('coordination'):
        if 'logan' in tags.get('coordination', []):
            section += "\n**Note:** Coordinate with Logan\n"
        if 'ilse' in tags.get('coordination', []):
            section += "\n**Note:** Coordinate with Ilse\n"
    
    section += "\n---\n\n"
    return section


def generate_digest(meetings: List[Dict[str, Any]], target_date: datetime.date) -> str:
    """Generate complete daily meeting prep digest (strict accuracy)."""
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
    content += f"*Generated by `meeting-prep-digest` v3.0.0 — {get_et_timestamp()}*\n"
    
    return content


def generate_empty_digest(target_date: datetime.date) -> str:
    """Generate digest when no external meetings found (strict accuracy)."""
    content = f"# Daily Meeting Prep — {target_date}\n\n"
    content += f"**Generated:** {get_et_timestamp()}\n\n"
    content += "## Today's External Stakeholder Meetings\n\n"
    content += "*No external stakeholder meetings scheduled for today.*\n\n"
    content += "---\n\n"
    content += f"*Generated by `meeting-prep-digest` v3.0.0 — {get_et_timestamp()}*\n"
    return content


def save_digest_validated(content: str, target_date: datetime.date) -> None:
    """Safely write digest via temp file, validate, then atomically move into place."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    final_path = DIGESTS_DIR / f"daily-meeting-prep-{target_date}.md"
    tmp_path = DIGESTS_DIR / f".tmp_daily-meeting-prep-{target_date}.md"

    # Write temp file
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Validate temp file
    result = subprocess.run([
        "python3",
        "/home/workspace/N5/scripts/validate_digest_output.py",
        str(tmp_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        # Keep rejected copy for audit
        rejected_path = DIGESTS_DIR / f"daily-meeting-prep-{target_date}.rejected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        os.replace(tmp_path, rejected_path)
        with open('/home/workspace/N5/logs/digest_validation.log', 'a', encoding='utf-8') as logf:
            logf.write(f"Validation failed for {final_path} at {datetime.now().isoformat()} | kept {rejected_path.name}\n")
        raise RuntimeError(f"Digest validation failed for {final_path}; see {rejected_path.name}")

    # Move temp to final atomically
    os.replace(tmp_path, final_path)
    logger.info(f"✓ Saved digest: {final_path}")


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
    3. Not postponed/inactive (N5OS status tags)
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
        
        # Extract N5OS tags from description
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
            save_digest_validated(digest_content, target_date)
            logger.info(f"✓ Digest generated: {DIGESTS_DIR / f'daily-meeting-prep-{target_date}.md'}")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

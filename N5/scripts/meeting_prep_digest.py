#!/usr/bin/env python3
"""
Meeting Prep Digest Generator

Generates daily meeting intelligence digest with attendee research and email context.

Usage:
    meeting-prep-digest [--date YYYY-MM-DD] [--dry-run]

Author: N5 OS
Version: 1.0.1
Date: 2025-10-09
"""

import argparse
import json
import logging
import sys
import pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
INTERNAL_DOMAINS = ["mycareerspan.com", "apply.ai"]
PERSONAL_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
DIGESTS_DIR = Path("/home/workspace/N5/digests")

# Timezone
ET_TZ = pytz.timezone('America/New_York')

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
                # Still create empty digest
                digest_content = generate_empty_digest(target_date)
                save_digest(digest_content, target_date)
            return 0
        
        # Research attendees
        researched_meetings = []
        for meeting in external_meetings:
            researched_meeting = research_meeting_attendees(meeting)
            researched_meetings.append(researched_meeting)
        
        # Generate digest
        digest_content = generate_digest(researched_meetings, target_date)
        
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


def fetch_calendar_events(target_date: datetime.date) -> List[Dict[str, Any]]:
    """
    Fetch calendar events from Google Calendar for target date.
    
    Returns list of meeting objects with attendees, title, time, etc.
    """
    logger.info("Fetching calendar events...")
    
    # NOTE: This is a stub. In production, use list_app_tools + use_app_google_calendar
    # Example pseudo-code:
    # tools = list_app_tools(app_slug="google_calendar")
    # events = use_app_google_calendar(
    #     tool_name="google_calendar-list-events",
    #     configured_props={
    #         "calendarId": "primary",
    #         "timeMin": f"{target_date}T00:00:00Z",
    #         "timeMax": f"{target_date}T23:59:59Z"
    #     }
    # )
    
    # For now, return mock data structure
    logger.warning("Using mock calendar data - implement Google Calendar API integration")
    
    return [
        {
            "event_id": "evt1",
            "title": "Community Partnerships - Theresa Martinez",
            "start_time": f"{target_date}T08:45:00",
            "end_time": f"{target_date}T09:30:00",
            "attendees": [
                {"email": "vrijen@mycareerspan.com", "name": "Vrijen Attawar", "is_organizer": True},
                {"email": "theresa.martinez@northwell.org", "name": "Theresa Martinez", "is_organizer": False}
            ],
            "description": "Discussion about Q4 partnership opportunities",
            "location": "Zoom"
        },
        {
            "event_id": "evt2",
            "title": "Team Sync",
            "start_time": f"{target_date}T10:00:00",
            "end_time": f"{target_date}T10:30:00",
            "attendees": [
                {"email": "vrijen@mycareerspan.com", "name": "Vrijen", "is_organizer": True},
                {"email": "logan@mycareerspan.com", "name": "Logan", "is_organizer": False}
            ],
            "description": "Weekly team sync",
            "location": ""
        }
    ]


def filter_external_meetings(meetings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter for external meetings only.
    
    Excludes:
    - All-internal meetings (all attendees @mycareerspan.com or @apply.ai)
    - Internal 1:1s (2 attendees, both internal)
    - All-day events
    - Declined meetings
    """
    logger.info(f"Filtering {len(meetings)} meetings...")
    
    external_meetings = []
    
    for meeting in meetings:
        # Check if all attendees are internal
        attendees = meeting.get("attendees", [])
        internal_count = sum(1 for att in attendees if is_internal_email(att["email"]))
        total_count = len(attendees)
        
        # Skip if all internal
        if internal_count == total_count:
            logger.debug(f"Skipping internal meeting: {meeting['title']}")
            continue
        
        # Skip if internal 1:1 (2 attendees, both internal)
        if total_count == 2 and internal_count == 2:
            logger.debug(f"Skipping internal 1:1: {meeting['title']}")
            continue
        
        # Get external attendees
        external_attendees = [
            att for att in attendees
            if not is_internal_email(att["email"])
        ]
        
        meeting["external_attendees"] = external_attendees
        meeting["is_internal_meeting"] = (internal_count == total_count)
        
        external_meetings.append(meeting)
        logger.info(f"External meeting: {meeting['title']} ({len(external_attendees)} external)")
    
    return external_meetings


def is_internal_email(email: str) -> bool:
    """Check if email is internal (@mycareerspan.com or @apply.ai)."""
    domain = email.split("@")[-1].lower()
    return domain in INTERNAL_DOMAINS


def research_meeting_attendees(meeting: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research each external attendee:
    1. Auto-detect entity type (person/company/org)
    2. Gmail scan for past interactions
    3. Light web research (LinkedIn, company, news)
    4. Auto-inject context from meeting title
    """
    logger.info(f"Researching attendees for: {meeting['title']}")
    
    meeting["researched_attendees"] = []
    
    for attendee in meeting["external_attendees"]:
        logger.info(f"  Researching: {attendee['name']} <{attendee['email']}>")
        
        # Auto-detect entity type
        entity_type, confidence = detect_entity_type(
            attendee["email"],
            attendee["name"],
            meeting["title"],
            meeting.get("description", "")
        )
        
        # Gmail scan
        gmail_history = scan_gmail_history(attendee["email"])
        
        # Light web research
        web_research = perform_light_research(attendee["name"], attendee["email"], entity_type)
        
        # Auto-inject context
        context = auto_inject_context(meeting["title"], meeting.get("description", ""))
        
        research_result = {
            "attendee": attendee,
            "entity_type": entity_type,
            "entity_confidence": confidence,
            "gmail_history": gmail_history,
            "web_research": web_research,
            "auto_context": context,
            "clarification_needed": confidence < 0.5
        }
        
        meeting["researched_attendees"].append(research_result)
    
    return meeting


def detect_entity_type(email: str, name: str, title: str, description: str) -> Tuple[str, float]:
    """
    Auto-detect entity type: person, company, org, or unclear.
    
    Returns: (entity_type, confidence)
    """
    domain = email.split("@")[-1].lower()
    
    # Rule 1: Personal email domains → person
    if domain in PERSONAL_EMAIL_DOMAINS:
        return ("person", 0.9)
    
    # Rule 2: Organization indicators in name
    org_indicators = ["corp", "inc", "llc", "ltd", "foundation", "university", "institute"]
    name_lower = name.lower()
    for indicator in org_indicators:
        if indicator in name_lower:
            return ("company", 0.8)
    
    # Rule 3: Name format (First Last → person)
    name_parts = name.split()
    if len(name_parts) == 2:
        if name_parts[0][0].isupper() and name_parts[1][0].isupper():
            return ("person", 0.7)
    
    # Rule 4: Meeting title/description parsing
    text = f"{title} {description}".lower()
    if any(word in text for word in ["partnership", "meeting with", "coaching", "1:1"]):
        # Likely person if personalized meeting
        return ("person", 0.6)
    
    # Default: person with low confidence (most meeting attendees are people)
    return ("person", 0.5)


def scan_gmail_history(email: str) -> Dict[str, Any]:
    """
    Scan Gmail for past interactions with this email address.
    
    Returns summary of email history.
    """
    logger.info(f"    Scanning Gmail history...")
    
    # NOTE: Stub for Gmail API integration
    # In production: use list_app_tools + use_app_gmail
    # Example pseudo-code:
    # tools = list_app_tools(app_slug="gmail")
    # threads = use_app_gmail(
    #     tool_name="gmail-search-messages",
    #     configured_props={"query": f"from:{email} OR to:{email}"}
    # )
    
    logger.warning("Using mock Gmail data - implement Gmail API integration")
    
    return {
        "search_window": "90 days",
        "thread_count": 2,
        "last_contact": "2025-10-01",
        "summary_bullets": [
            "Last contact: Oct 1 - Partnership proposal Q4 timeline discussion",
            "Awaiting response on community program scope",
            "2 prior emails: Sept 15 (intro), Sept 20 (follow-up)"
        ],
        "overall_context": "Partnership exploration for Q4 community health initiative. Theresa requested budget breakdown; V sent preliminary numbers."
    }


def perform_light_research(name: str, email: str, entity_type: str) -> Dict[str, Any]:
    """
    Perform light web research: LinkedIn, company site, recent news.
    """
    logger.info(f"    Performing light web research...")
    
    # NOTE: Stub for web research
    # In production: use web_search, read_webpage, web_research tools
    # Example pseudo-code:
    # linkedin_query = f"{name} LinkedIn"
    # linkedin_results = web_search(query=linkedin_query, time_range="anytime")
    # profile_data = read_webpage(linkedin_results[0]['url'])
    
    logger.warning("Using mock web research data - implement web_search/read_webpage integration")
    
    if entity_type == "person":
        return {
            "linkedin_profile": f"{name}: Senior professional with 10+ years experience",
            "company_info": "Works at Example Corp",
            "recent_activity": "Posted about industry trends in Sept 2025",
            "source_urls": ["https://linkedin.com/in/example", "https://examplecorp.com"]
        }
    else:
        return {
            "company_overview": f"{name}: Leading company in their sector",
            "key_facts": "Founded 2015, 500+ employees",
            "recent_news": "Announced new product launch in Sept 2025",
            "source_urls": ["https://examplecorp.com", "https://crunchbase.com/example"]
        }


def auto_inject_context(title: str, description: str) -> str:
    """
    Parse meeting title/description for context keywords.
    """
    context_map = {
        "partnership": ["partnership", "partner", "collaborate", "collaboration"],
        "coaching": ["coaching", "coach", "1:1", "one-on-one", "mentoring"],
        "fundraising": ["fundraising", "investor", "vc", "funding", "pitch"],
        "sales": ["demo", "sales", "prospect", "customer"],
        "advisory": ["advisory", "advisor", "board", "advise"]
    }
    
    text = f"{title} {description}".lower()
    
    detected = []
    for context_type, keywords in context_map.items():
        if any(keyword in text for keyword in keywords):
            detected.append(context_type)
    
    if detected:
        return ", ".join(detected).capitalize()
    
    return None


def generate_digest(researched_meetings: List[Dict[str, Any]], target_date: datetime.date) -> str:
    """Generate the digest markdown content."""
    
    lines = []
    lines.append(f"# Daily Meeting Prep Digest - {target_date.strftime('%B %d, %Y')}")
    lines.append("")
    lines.append(f"**Generated:** {get_et_timestamp()}")
    lines.append(f"**Meetings Today:** {len(researched_meetings)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Meeting details
    for idx, meeting in enumerate(researched_meetings, 1):
        start_time = datetime.fromisoformat(meeting["start_time"]).strftime("%H:%M")
        
        lines.append(f"## {idx}. {meeting['title']} - {start_time}")
        lines.append("")
        
        # For each external attendee
        for research in meeting["researched_attendees"]:
            attendee = research["attendee"]
            
            lines.append(f"**Attendee:** {attendee['name']}")
            lines.append(f"**Email:** {attendee['email']}")
            
            entity_type = research["entity_type"]
            confidence = research["entity_confidence"]
            if confidence < 0.5:
                lines.append(f"**Type:** {entity_type} (clarification needed)")
            else:
                lines.append(f"**Type:** {entity_type} (auto-detected)")
            lines.append("")
            
            # Gmail history
            gmail = research["gmail_history"]
            lines.append(f"### Email History (Past {gmail['search_window']})")
            for bullet in gmail["summary_bullets"]:
                lines.append(f"- {bullet}")
            lines.append("")
            lines.append(f"**Overall Context:** {gmail['overall_context']}")
            lines.append("")
            
            # Web research
            web = research["web_research"]
            lines.append("### Quick Research")
            if "linkedin_profile" in web:
                lines.append(f"- **LinkedIn:** {web['linkedin_profile']}")
                lines.append(f"- **Company:** {web['company_info']}")
                lines.append(f"- **Recent Activity:** {web['recent_activity']}")
            else:
                lines.append(f"- **Overview:** {web['company_overview']}")
                lines.append(f"- **Key Facts:** {web['key_facts']}")
                lines.append(f"- **Recent News:** {web['recent_news']}")
            lines.append("")
            
            # Auto-injected context
            if research["auto_context"]:
                lines.append(f"**Auto-Injected Context:** {research['auto_context']}")
                lines.append("")
            
            # Clarification prompt
            if research["clarification_needed"]:
                lines.append(f"⚠️ **Clarification needed:** Unable to confidently identify attendee type. Please verify: Is {attendee['name']} a person or organization?")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Summary stats
    total_external = sum(len(m["researched_attendees"]) for m in researched_meetings)
    clarifications_needed = sum(
        1 for m in researched_meetings
        for r in m["researched_attendees"]
        if r["clarification_needed"]
    )
    
    lines.append("## Summary Stats")
    lines.append(f"- External meetings: {len(researched_meetings)}")
    lines.append(f"- People researched: {total_external}")
    lines.append(f"- Clarifications needed: {clarifications_needed}")
    lines.append(f"- Gmail threads reviewed: {total_external}")
    lines.append("")
    
    if clarifications_needed > 0:
        lines.append("**Action Items:**")
        lines.append(f"- [ ] Clarify {clarifications_needed} unclear attendee(s)")
        lines.append("")
    
    return "\n".join(lines)


def generate_empty_digest(target_date: datetime.date) -> str:
    """Generate empty digest when no external meetings found."""
    lines = []
    lines.append(f"# Daily Meeting Prep Digest - {target_date.strftime('%B %d, %Y')}")
    lines.append("")
    lines.append(f"**Generated:** {get_et_timestamp()}")
    lines.append(f"**Meetings Today:** 0")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## No External Meetings Today")
    lines.append("")
    lines.append("No external meetings found on your calendar for this date.")
    lines.append("")
    lines.append("**Summary Stats:**")
    lines.append("- External meetings: 0")
    lines.append("- People researched: 0")
    lines.append("")
    return "\n".join(lines)


def save_digest(content: str, target_date: datetime.date):
    """Save digest to file."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"daily-meeting-prep-{target_date}.md"
    filepath = DIGESTS_DIR / filename
    
    filepath.write_text(content)
    logger.info(f"Saved digest to: {filepath}")


if __name__ == "__main__":
    sys.exit(main())

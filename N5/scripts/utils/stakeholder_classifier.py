#!/usr/bin/env python3
"""
Stakeholder Classifier v2 for N5 Meeting System
Classifies meetings based on participant types and content.
Supports both external (FOUNDER, INVESTOR, etc.) and internal meeting types.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional

# Load internal domain configuration
def load_internal_config() -> Dict:
    """Load internal domain configuration from N5/prefs/internal_domains.json"""
    config_path = Path(__file__).parent.parent.parent / "prefs" / "internal_domains.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to hardcoded defaults
        return {
            "internal_domains": ["mycareerspan.com", "theapply.ai"],
            "personal_emails": ["vrijenattawar@gmail.com"],
            "exclude_from_participant_count": ["zo.computer", "zocomputer.com"]
        }

INTERNAL_CONFIG = load_internal_config()

# Backward compatibility
INTERNAL_DOMAINS = INTERNAL_CONFIG.get("internal_domains", ["mycareerspan.com", "theapply.ai"])


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    email = email.strip().lower()
    if '@' in email:
        return email.split('@')[1]
    return ''


def is_external_email(email: str) -> bool:
    """Check if email is external (not Careerspan team or V's personal email)."""
    if not email:
        return True
    
    email_lower = email.lower().strip()
    
    # Check internal domains
    for domain in INTERNAL_CONFIG.get("internal_domains", []):
        if email_lower.endswith(f"@{domain}"):
            return False
    
    # Check personal emails
    if email_lower in [e.lower() for e in INTERNAL_CONFIG.get("personal_emails", [])]:
        return False
    
    # Check excluded domains (like zo.computer) - these are neither internal nor external
    for excluded in INTERNAL_CONFIG.get("exclude_from_participant_count", []):
        if excluded in email_lower:
            return False
    
    return True


def is_internal_email(email: str) -> bool:
    """
    Check if email domain is internal.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email domain is in INTERNAL_DOMAINS or is V's personal email, False otherwise
    """
    return not is_external_email(email)


def extract_emails_from_text(text: str) -> List[str]:
    """
    Extract email addresses from text using regex.
    
    Args:
        text: Text that may contain email addresses
        
    Returns:
        List of email addresses found
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_emails_from_participants(participants: str) -> List[str]:
    """
    Extract email addresses from participant string or list.
    
    Args:
        participants: String containing participant info (names, emails)
        
    Returns:
        List of email addresses found
    """
    if isinstance(participants, list):
        participants = ' '.join(participants)
    
    return extract_emails_from_text(participants)


def classify_participants(emails: List[str]) -> Dict[str, List[str]]:
    """
    Classify emails as internal or external.
    
    Args:
        emails: List of email addresses
        
    Returns:
        Dict with 'internal' and 'external' keys, each containing list of emails
    """
    classification = {
        'internal': [],
        'external': []
    }
    
    for email in emails:
        if is_internal_email(email):
            classification['internal'].append(email)
        else:
            classification['external'].append(email)
    
    return classification


def has_n5os_tag(event_description: str) -> bool:
    """Check if event description contains N5OS hashtag"""
    if not event_description:
        return False
    return bool(re.search(r'#n5os\b', event_description, re.IGNORECASE))


def is_internal_meeting(participants: str, event_description: str = "") -> bool:
    """
    Determine if meeting is internal (all Careerspan team members).
    
    Priority:
    1. Check for #N5OS tag in event description
    2. Check if all participants are internal domains/emails
    
    Args:
        participants: Participant string or list
        event_description: Optional event description that may contain #N5OS tag
        
    Returns:
        True if internal meeting, False otherwise
    """
    # Priority 1: N5OS tag
    if has_n5os_tag(event_description):
        return True
    
    # Priority 2: Check participant domains
    emails = extract_emails_from_text(participants)
    if not emails:
        return False
    
    # Filter out excluded domains (like zo.computer)
    filtered_emails = []
    for email in emails:
        email_lower = email.lower()
        if not any(excluded in email_lower for excluded in 
                  INTERNAL_CONFIG.get("exclude_from_participant_count", [])):
            filtered_emails.append(email)
    
    if not filtered_emails:
        return False
    
    # Check if ALL participants are internal
    internal_count = sum(1 for e in filtered_emails if is_internal_email(e))
    return internal_count == len(filtered_emails)


def classify_internal_meeting_type(
    participants: str,
    event_description: str = "",
    transcript: str = "",
    duration_minutes: Optional[int] = None
) -> str:
    """
    Classify internal meeting into specific subtype.
    
    Returns:
    - INTERNAL_STANDUP_COFOUNDER: Co-founder standups (2-3 participants, includes V + Logan/Ilse)
    - INTERNAL_STANDUP_TEAM: Team standups (coordination, updates)
    - INTERNAL_STRATEGIC: Strategic planning, retrospectives, deep dives
    """
    emails = extract_emails_from_text(participants)
    
    # Filter out excluded domains for participant count
    filtered_emails = [e for e in emails 
                      if not any(excluded in e.lower() for excluded in 
                               INTERNAL_CONFIG.get("exclude_from_participant_count", []))]
    participant_count = len(filtered_emails)
    
    # Check for strategic indicators
    strategic_keywords = [
        'planning', 'strategy', 'retrospective', 'quarterly', 'okr', 
        'roadmap', 'strategic', 'vision', 'deep dive', 'workshop'
    ]
    combined_text = f"{event_description} {transcript}".lower()
    has_strategic_keywords = any(kw in combined_text for kw in strategic_keywords)
    is_long_meeting = duration_minutes and duration_minutes > 60
    
    if has_strategic_keywords or is_long_meeting:
        return "INTERNAL_STRATEGIC"
    
    # Check for co-founder standup
    # Look for Vrijen + one of (Logan, Ilse) with small participant count
    emails_str = ' '.join(emails).lower()
    vrijen_present = any(identifier in emails_str 
                        for identifier in ['vrijen', 'vrijenattawar'])
    logan_present = 'logan' in emails_str
    ilse_present = 'ilse' in emails_str
    
    founder_present = logan_present or ilse_present
    
    if participant_count <= 3 and vrijen_present and founder_present:
        return "INTERNAL_STANDUP_COFOUNDER"
    
    # Default: team standup
    return "INTERNAL_STANDUP_TEAM"


def classify_external_stakeholder_type(participants: str, transcript: str = "") -> str:
    """
    Classify external stakeholder type.
    
    Returns one of:
    - FOUNDER: Startup founders, entrepreneurs
    - INVESTOR: VCs, angels, investment professionals
    - CUSTOMER: Paying customers, enterprise clients
    - COMMUNITY: Community members, partners, collaborators
    - NETWORKING: General networking, exploratory conversations
    """
    # This is placeholder logic - you may want to enhance this based on
    # email domains, transcript content, or CRM data
    
    combined_text = f"{participants} {transcript}".lower()
    
    # Check for investor keywords
    investor_keywords = ['vc', 'venture', 'capital', 'investor', 'investment', 'fund', 'partner']
    if any(kw in combined_text for kw in investor_keywords):
        return "INVESTOR"
    
    # Check for founder keywords
    founder_keywords = ['founder', 'ceo', 'co-founder', 'startup', 'building']
    if any(kw in combined_text for kw in founder_keywords):
        return "FOUNDER"
    
    # Check for customer keywords
    customer_keywords = ['customer', 'client', 'procurement', 'buying', 'enterprise']
    if any(kw in combined_text for kw in customer_keywords):
        return "CUSTOMER"
    
    # Check for community keywords
    community_keywords = ['community', 'partner', 'collaboration', 'ecosystem']
    if any(kw in combined_text for kw in community_keywords):
        return "COMMUNITY"
    
    # Default: networking
    return "NETWORKING"


def classify_meeting(
    participants: str,
    event_description: str = "",
    transcript: str = "",
    duration_minutes: Optional[int] = None
) -> str:
    """
    Classify meeting type based on participants, content, and context.
    
    Returns one of:
    - INTERNAL_STANDUP_COFOUNDER
    - INTERNAL_STANDUP_TEAM
    - INTERNAL_STRATEGIC
    - FOUNDER
    - INVESTOR
    - CUSTOMER
    - COMMUNITY
    - NETWORKING
    """
    # Check if internal meeting first
    if is_internal_meeting(participants, event_description):
        return classify_internal_meeting_type(
            participants, event_description, transcript, duration_minutes
        )
    
    # Otherwise, classify as external stakeholder type
    return classify_external_stakeholder_type(participants, transcript)


def get_participant_details(participants: str or List[str], transcript: str = None,
                           event_description: str = "") -> Dict:
    """
    Get detailed participant classification.
    
    Args:
        participants: Participant string or list
        transcript: Optional full transcript
        event_description: Optional event description
        
    Returns:
        Dict with meeting_type, internal_emails, external_emails, all_emails, etc.
    """
    emails = extract_emails_from_participants(participants)
    
    if transcript:
        transcript_emails = extract_emails_from_text(transcript)
        emails.extend(transcript_emails)
    
    emails = list(set(email.lower() for email in emails))
    
    classification = classify_participants(emails)
    meeting_type = classify_meeting(participants, event_description, transcript)
    
    return {
        'meeting_type': meeting_type,
        'internal_emails': classification['internal'],
        'external_emails': classification['external'],
        'all_emails': emails,
        'total_participants': len(emails),
        'is_internal': is_internal_meeting(participants, event_description),
        'has_n5os_tag': has_n5os_tag(event_description)
    }


# CLI testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stakeholder_classifier_v2.py <email1> [email2] ...")
        print("\nExample:")
        print("  python stakeholder_classifier_v2.py vrijen@mycareerspan.com alex@example.com")
        print("\nTest with event description:")
        print("  python stakeholder_classifier_v2.py --event '#N5OS standup' vrijen@mycareerspan.com")
        sys.exit(1)
    
    args = sys.argv[1:]
    event_desc = ""
    
    # Check for --event flag
    if args[0] == '--event' and len(args) > 1:
        event_desc = args[1]
        emails = args[2:]
    else:
        emails = args
    
    print(f"\n📧 Analyzing {len(emails)} email(s)...\n")
    
    if event_desc:
        print(f"📅 Event Description: {event_desc}")
        print(f"   N5OS Tag: {'✅ DETECTED' if has_n5os_tag(event_desc) else '❌ NOT FOUND'}\n")
    
    for email in emails:
        internal = is_internal_email(email)
        status = "✅ INTERNAL" if internal else "🌐 EXTERNAL"
        print(f"{status}: {email}")
    
    classification = classify_participants(emails)
    print(f"\n📊 Classification:")
    print(f"   Internal: {len(classification['internal'])} participant(s)")
    print(f"   External: {len(classification['external'])} participant(s)")
    
    participants_str = ' '.join(emails)
    meeting_type = classify_meeting(participants_str, event_desc)
    print(f"\n🏷️  Meeting Type: {meeting_type}")
    
    # Show detailed participant details
    details = get_participant_details(participants_str, event_description=event_desc)
    print(f"\n📋 Detailed Analysis:")
    print(f"   Is Internal Meeting: {details['is_internal']}")
    print(f"   Has N5OS Tag: {details['has_n5os_tag']}")
    print(f"   Total Participants: {details['total_participants']}")

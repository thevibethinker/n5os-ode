#!/usr/bin/env python3
"""
Stakeholder Classifier
Classifies meetings as internal or external based on participant email domains.
"""
import re
from typing import List, Dict

# Internal email domains (from N5/prefs/operations/careerspan.md)
INTERNAL_DOMAINS = ['mycareerspan.com', 'theapply.ai']


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    email = email.strip().lower()
    if '@' in email:
        return email.split('@')[1]
    return ''


def is_internal_email(email: str) -> bool:
    """
    Check if email domain is internal.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email domain is in INTERNAL_DOMAINS, False otherwise
    """
    domain = extract_domain(email)
    return domain in INTERNAL_DOMAINS


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


def classify_meeting(participants: str or List[str], transcript: str = None) -> str:
    """
    Classify meeting as 'internal' or 'external'.
    
    Logic:
    - If ALL participants are internal → 'internal'
    - If ANY participant is external → 'external'
    - If no emails found, fallback to 'external' (safer default)
    
    Args:
        participants: Participant string or list
        transcript: Optional full transcript to extract emails from
        
    Returns:
        'internal' or 'external'
    """
    # Extract emails from participants
    emails = extract_emails_from_participants(participants)
    
    # If transcript provided, try extracting from there too
    if transcript:
        transcript_emails = extract_emails_from_text(transcript)
        emails.extend(transcript_emails)
    
    # Remove duplicates
    emails = list(set(email.lower() for email in emails))
    
    # If no emails found, default to external (safer)
    if not emails:
        return 'external'
    
    # Classify all emails
    classification = classify_participants(emails)
    
    # If ANY external participant, meeting is external
    if classification['external']:
        return 'external'
    
    # If we have internal participants and no external, it's internal
    if classification['internal']:
        return 'internal'
    
    # Fallback (shouldn't reach here)
    return 'external'


def get_participant_details(participants: str or List[str], transcript: str = None) -> Dict:
    """
    Get detailed participant classification.
    
    Args:
        participants: Participant string or list
        transcript: Optional full transcript
        
    Returns:
        Dict with meeting_type, internal_emails, external_emails, all_emails
    """
    emails = extract_emails_from_participants(participants)
    
    if transcript:
        transcript_emails = extract_emails_from_text(transcript)
        emails.extend(transcript_emails)
    
    emails = list(set(email.lower() for email in emails))
    
    classification = classify_participants(emails)
    meeting_type = classify_meeting(participants, transcript)
    
    return {
        'meeting_type': meeting_type,
        'internal_emails': classification['internal'],
        'external_emails': classification['external'],
        'all_emails': emails,
        'total_participants': len(emails)
    }


# CLI testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stakeholder_classifier.py <email1> [email2] ...")
        print("\nExample:")
        print("  python stakeholder_classifier.py vrijen@mycareerspan.com alex@example.com")
        sys.exit(1)
    
    emails = sys.argv[1:]
    
    print(f"\n📧 Analyzing {len(emails)} email(s)...\n")
    
    for email in emails:
        internal = is_internal_email(email)
        status = "✅ INTERNAL" if internal else "🌐 EXTERNAL"
        print(f"{status}: {email}")
    
    classification = classify_participants(emails)
    print(f"\n📊 Classification:")
    print(f"   Internal: {len(classification['internal'])} participant(s)")
    print(f"   External: {len(classification['external'])} participant(s)")
    
    meeting_type = 'internal' if not classification['external'] else 'external'
    print(f"\n🏷️  Meeting Type: {meeting_type.upper()}")

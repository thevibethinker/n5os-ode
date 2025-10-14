#!/usr/bin/env python3
"""
Background Email Scanner - Runs every ~20 minutes
Discovers new stakeholders from meeting-related emails in Gmail

Uses:
- Google Gmail API (service account credentials)
- LLM-based participant extraction (no regex)
- Proper queue ordering by priority score
- Comprehensive calendar invite detection
"""

# ======================================================================
# DEPRECATED - Use Knowledge/crm/profiles/ and crm_query.py instead
# This script is part of the legacy stakeholder system.
# Retained for historical reference only.
# ======================================================================


import logging
import json
import sys
import argparse
import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from email.utils import parseaddr
import re

# Google API imports
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
try:
    from stakeholder_manager import (
        is_external_email,
        generate_slug,
        infer_organization_from_email
    )
except ImportError:
    # Fallback implementations
    def is_external_email(email: str) -> bool:
        if not email or '@' not in email:
            return False
        domain = email.split('@')[1].lower()
        return domain not in ['mycareerspan.com', 'theapply.ai', 'zo.computer']
    
    def generate_slug(name: str, organization: str = "") -> str:
        base = name.lower().replace(' ', '-')
        if organization:
            org_slug = organization.lower().replace(' ', '-').replace('.', '')[:20]
            base = f"{base}-{org_slug}"
        return re.sub(r'[^a-z0-9-]', '', base)
    
    def infer_organization_from_email(email: str) -> str:
        if '@' not in email:
            return "Unknown"
        domain = email.split('@')[1].lower()
        if domain in ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']:
            return "[Personal email]"
        name = domain.split('.')[0]
        return name.replace('-', ' ').replace('_', ' ').title()

# Setup logging
LOG_FILE = Path("/home/workspace/N5/logs/email_scanner.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Configuration
CRM_PROFILES_DIR = Path("/home/workspace/Knowledge/crm/individuals")
INDEX_FILE = CRM_PROFILES_DIR / "index.jsonl"
PENDING_DIR = CRM_PROFILES_DIR / ".pending_updates"
STATE_FILE = Path("/home/workspace/N5/.state/email_scanner_state.json")
CREDENTIALS_PATH = Path("/home/workspace/N5/config/credentials/google_service_account.json")

# Ensure directories exist
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
PENDING_DIR.mkdir(parents=True, exist_ok=True)

# Internal domains (exclude from stakeholder discovery)
INTERNAL_DOMAINS = {
    "mycareerspan.com",
    "theapply.ai",
    "zo.computer"
}


def get_gmail_service():
    """Initialize Gmail API service with service account credentials"""
    try:
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        credentials = service_account.Credentials.from_service_account_file(
            str(CREDENTIALS_PATH),
            scopes=SCOPES
        )
        
        # Delegate to the user's email
        # Note: Service account must have domain-wide delegation enabled
        delegated_credentials = credentials.with_subject('va@mycareerspan.com')
        
        service = build('gmail', 'v1', credentials=delegated_credentials)
        log.info("Gmail API service initialized successfully")
        return service
        
    except Exception as e:
        log.error(f"Failed to initialize Gmail API: {e}", exc_info=True)
        raise


def load_state() -> Dict:
    """Load last scan timestamp and processed message IDs"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                log.info(f"Loaded state: last_scan={state.get('last_scan_time', 'never')}, "
                        f"processed_count={len(state.get('processed_message_ids', []))}")
                return state
        except Exception as e:
            log.error(f"Error loading state: {e}")
            return _default_state()
    else:
        log.info("No existing state found, starting fresh")
        return _default_state()


def _default_state() -> Dict:
    """Default state structure"""
    # Start from 7 days ago on first run (to catch recent activity)
    initial_time = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    return {
        "last_scan_time": initial_time,
        "processed_message_ids": [],
        "discovered_count": 0,
        "last_discoveries": []
    }


def save_state(state: Dict):
    """Save scanner state"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        log.info(f"State saved: {STATE_FILE}")
    except Exception as e:
        log.error(f"Error saving state: {e}")


def load_existing_stakeholders() -> Set[str]:
    """Load existing stakeholder emails from index"""
    existing = set()
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if 'email' in entry:
                            existing.add(entry['email'].lower())
            log.info(f"Loaded {len(existing)} existing stakeholder emails")
        except Exception as e:
            log.error(f"Error loading stakeholder index: {e}")
    return existing


def build_gmail_query(last_scan_time: str) -> str:
    """Build Gmail search query for meeting-related emails"""
    try:
        dt = datetime.fromisoformat(last_scan_time.replace('Z', '+00:00'))
        # Gmail uses epoch seconds for after: queries
        epoch_seconds = int(dt.timestamp())
    except:
        # Fallback: 24 hours ago
        epoch_seconds = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())
    
    # Comprehensive meeting detection query
    # Includes: calendar invites (ICS), meeting platforms, scheduling tools
    query_parts = [
        f'after:{epoch_seconds}',
        '(',
        'subject:(invite OR invitation OR meeting OR calendar OR scheduled)',
        'OR filename:invite.ics',
        'OR filename:*.ics', 
        'OR zoom.us',
        'OR meet.google.com',
        'OR calendly.com',
        'OR when2meet.com',
        'OR "added you to"',
        'OR "invited you to"',
        ')',
        # Exclude internal senders
        *[f'-from:*@{domain}' for domain in INTERNAL_DOMAINS]
    ]
    
    query = ' '.join(query_parts)
    return query


def extract_email_content(msg_data: Dict) -> Dict:
    """Extract readable content from Gmail message"""
    result = {
        'subject': '',
        'from': '',
        'to': '',
        'cc': '',
        'body': '',
        'headers': {}
    }
    
    # Get headers
    headers = msg_data.get('payload', {}).get('headers', [])
    for header in headers:
        name = header['name'].lower()
        value = header['value']
        result['headers'][name] = value
        
        if name == 'subject':
            result['subject'] = value
        elif name == 'from':
            result['from'] = value
        elif name == 'to':
            result['to'] = value
        elif name == 'cc':
            result['cc'] = value
    
    # Get body
    payload = msg_data.get('payload', {})
    
    def extract_text_from_part(part):
        """Recursively extract text from message parts"""
        text = ""
        mime_type = part.get('mimeType', '')
        
        if 'data' in part.get('body', {}):
            data = part['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if 'text' in mime_type:
                text += decoded
        
        # Recurse into multipart
        if 'parts' in part:
            for subpart in part['parts']:
                text += extract_text_from_part(subpart)
        
        return text
    
    result['body'] = extract_text_from_part(payload)
    
    return result


def parse_email_addresses(header_value: str) -> List[str]:
    """Extract email addresses from header (From/To/Cc)"""
    if not header_value:
        return []
    
    emails = []
    # Split by comma, handle "Name <email>" format
    parts = header_value.split(',')
    for part in parts:
        _, email = parseaddr(part.strip())
        if email and '@' in email:
            emails.append(email.lower())
    
    return emails


def llm_extract_participants(email_content: Dict) -> str:
    """
    Use LLM (via scheduled task context) to extract participant information.
    This is a PLACEHOLDER that will be filled by the Zo agent during scheduled execution.
    
    Returns JSON string with extracted participants
    """
    # This function is called BY the Zo agent which has LLM access
    # The agent will inject the actual LLM extraction here
    
    prompt = f"""Extract external meeting participants from this email.

Email Subject: {email_content['subject']}
From: {email_content['from']}
To: {email_content['to']}
Cc: {email_content['cc']}

Body excerpt:
{email_content['body'][:2000]}

Extract:
1. All external participant names and emails (not from mycareerspan.com, theapply.ai, zo.computer)
2. Their likely organization/affiliation
3. Meeting context (what type of meeting, purpose if mentioned)

Return ONLY valid JSON array:
[
  {{"name": "Full Name", "email": "email@domain.com", "organization": "Company Name", "context": "brief context"}}
]

If no external participants, return []
"""
    
    # PLACEHOLDER - Agent will replace this with actual LLM call
    # For now, return empty to indicate this needs agent injection
    return "[]"


def parse_email_for_participants_mechanical(email_content: Dict) -> List[Dict]:
    """
    Mechanical extraction: parse headers for email addresses.
    This is the fallback if LLM extraction is not available.
    """
    participants = []
    seen_emails = set()
    
    # Collect all email addresses from headers
    all_emails = []
    all_emails.extend(parse_email_addresses(email_content['from']))
    all_emails.extend(parse_email_addresses(email_content['to']))
    all_emails.extend(parse_email_addresses(email_content['cc']))
    
    for email in all_emails:
        if not email or email in seen_emails:
            continue
        if not is_external_email(email):
            continue
        
        seen_emails.add(email)
        
        # Extract name from "Name <email>" format if available
        name = None
        for header_val in [email_content['from'], email_content['to'], email_content['cc']]:
            if email in header_val:
                parsed_name, _ = parseaddr(header_val)
                if parsed_name and parsed_name != email:
                    name = parsed_name
                    break
        
        participant = {
            "email": email,
            "name": name,
            "organization": infer_organization_from_email(email),
            "context": email_content['subject'][:100],
            "extraction_method": "mechanical"
        }
        participants.append(participant)
    
    return participants


def calculate_priority_score(participant: Dict, email_content: Dict) -> int:
    """Calculate priority score for queue ordering"""
    score = 50  # Base score
    
    # Boost if name extracted
    if participant.get('name'):
        score += 20
    
    # Boost if organization identified
    org = participant.get('organization', '')
    if org and org != '[Personal email]' and org != 'Unknown':
        score += 15
    
    # Boost for upcoming meetings (keywords in subject)
    subject = email_content.get('subject', '').lower()
    if any(word in subject for word in ['tomorrow', 'upcoming', 'scheduled', 'confirmed']):
        score += 25
    
    # Boost if from external (more reliable)
    if participant['email'] in email_content.get('from', '').lower():
        score += 10
    
    return score


def queue_stakeholder_for_creation(participant: Dict, priority_score: int):
    """Queue a new stakeholder discovery for profile creation with priority"""
    try:
        slug = generate_slug(
            participant.get('name') or participant['email'].split('@')[0],
            participant.get('organization', '')
        )
        
        # Filename includes priority for sorting: {priority:03d}_{slug}_{timestamp}.json
        timestamp = int(datetime.now().timestamp())
        queue_file = PENDING_DIR / f"{priority_score:03d}_{slug}_{timestamp}.json"
        
        # Add metadata
        participant['priority_score'] = priority_score
        participant['queued_at'] = datetime.now(timezone.utc).isoformat()
        
        with open(queue_file, 'w') as f:
            json.dump(participant, f, indent=2)
        
        log.info(f"Queued (priority={priority_score}): {participant['email']} -> {queue_file.name}")
        
    except Exception as e:
        log.error(f"Error queuing stakeholder {participant.get('email')}: {e}")


def scan_gmail_for_meetings(dry_run: bool = False, use_llm: bool = True) -> Dict:
    """
    Scan Gmail for meeting-related emails
    
    Args:
        dry_run: Preview mode, don't make changes
        use_llm: Use LLM extraction (requires agent context), fallback to mechanical if False
    
    Returns:
        Dict with discovered stakeholders and metadata
    """
    log.info("=== Email Scanner: Starting Background Scan ===")
    
    # Load state and existing stakeholders
    state = load_state()
    existing_stakeholders = load_existing_stakeholders()
    processed_ids = set(state.get('processed_message_ids', []))
    
    # Build query
    query = build_gmail_query(state['last_scan_time'])
    log.info(f"Gmail query: {query}")
    
    if dry_run:
        log.info("[DRY RUN] Would scan Gmail with above query")
        log.info(f"[DRY RUN] Would check against {len(existing_stakeholders)} existing stakeholders")
        log.info(f"[DRY RUN] Would queue new discoveries to {PENDING_DIR}")
        log.info(f"[DRY RUN] LLM extraction: {'enabled' if use_llm else 'disabled'}")
        return {
            "status": "dry_run",
            "new_stakeholders": 0,
            "emails_scanned": 0
        }
    
    discovered_stakeholders = []
    emails_scanned = 0
    
    try:
        # Initialize Gmail API
        service = get_gmail_service()
        
        # Search for messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        log.info(f"Found {len(messages)} messages to process")
        
        for msg_ref in messages:
            msg_id = msg_ref['id']
            
            # Skip if already processed
            if msg_id in processed_ids:
                log.debug(f"Skipping already processed message: {msg_id}")
                continue
            
            # Fetch full message
            msg_data = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract content
            email_content = extract_email_content(msg_data)
            log.info(f"Processing: {email_content['subject'][:60]}")
            
            # Extract participants
            if use_llm:
                # LLM extraction (requires agent context)
                llm_result = llm_extract_participants(email_content)
                try:
                    participants = json.loads(llm_result)
                    for p in participants:
                        p['extraction_method'] = 'llm'
                except json.JSONDecodeError:
                    log.warning(f"LLM extraction failed for {msg_id}, falling back to mechanical")
                    participants = parse_email_for_participants_mechanical(email_content)
            else:
                # Mechanical extraction (fallback)
                participants = parse_email_for_participants_mechanical(email_content)
            
            # Process participants
            for participant in participants:
                email = participant['email']
                
                # Skip if already exists
                if email in existing_stakeholders:
                    log.debug(f"Skipping existing stakeholder: {email}")
                    continue
                
                # Skip duplicates within this scan
                if email in [p['email'] for p in discovered_stakeholders]:
                    continue
                
                # Calculate priority and queue
                priority = calculate_priority_score(participant, email_content)
                participant['source_email_id'] = msg_id
                participant['discovered_at'] = datetime.now(timezone.utc).isoformat()
                
                queue_stakeholder_for_creation(participant, priority)
                discovered_stakeholders.append(participant)
                existing_stakeholders.add(email)  # Prevent duplicates in same scan
            
            processed_ids.add(msg_id)
            emails_scanned += 1
        
    except HttpError as e:
        log.error(f"Gmail API error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Gmail API: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        log.error(f"Error during Gmail scan: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Update state
    state['last_scan_time'] = datetime.now(timezone.utc).isoformat()
    state['processed_message_ids'] = list(processed_ids)[-1000:]  # Keep last 1000
    state['discovered_count'] += len(discovered_stakeholders)
    state['last_discoveries'] = [
        {"email": p['email'], "name": p.get('name'), "org": p.get('organization'), "priority": p.get('priority_score')}
        for p in discovered_stakeholders[:10]
    ]
    
    save_state(state)
    
    result = {
        "status": "success",
        "timestamp": state['last_scan_time'],
        "new_stakeholders": len(discovered_stakeholders),
        "emails_scanned": emails_scanned,
        "discoveries": discovered_stakeholders
    }
    
    if len(discovered_stakeholders) > 0:
        log.info(f"🎯 Discovered {len(discovered_stakeholders)} new stakeholder(s)")
        for p in discovered_stakeholders[:5]:  # Log first 5
            log.info(f"  - {p['email']} ({p.get('name', 'name unknown')}) @ {p.get('organization', 'org unknown')} [priority={p.get('priority_score')}]")
    
    log.info(f"✅ Scan complete: {emails_scanned} emails processed, "
            f"{len(discovered_stakeholders)} new stakeholders discovered")
    log.info(f"Next scan in ~20 minutes")
    
    return result


def main(dry_run: bool = False, use_llm: bool = True) -> int:
    """Main execution"""
    try:
        result = scan_gmail_for_meetings(dry_run=dry_run, use_llm=use_llm)
        
        if dry_run:
            log.info("[DRY RUN] Scan simulation complete")
            return 0
        
        # Success logging
        if result['status'] == 'success':
            return 0
        elif result['status'] == 'error':
            log.error(f"Scan failed: {result.get('error', 'Unknown error')}")
            return 1
        else:
            log.warning(f"Scan completed with status: {result['status']}")
            return 0
            
    except Exception as e:
        log.error(f"Fatal error during email scan: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Background email scanner for stakeholder discovery")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be scanned without executing")
    parser.add_argument("--no-llm", action="store_true", help="Use mechanical extraction instead of LLM")
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run, use_llm=not args.no_llm))

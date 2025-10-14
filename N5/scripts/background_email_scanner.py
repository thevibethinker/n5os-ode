#!/usr/bin/env python3
"""
Background Email Scanner - Runs every ~20 minutes
Discovers new stakeholders from meeting-related emails in Gmail

Purpose:
- Scan Gmail for calendar invites, meeting confirmations, and follow-ups
- Extract external participant information (name, email, organization)
- Queue new stakeholders for profile creation
- Track last scan time to avoid reprocessing
- Log discoveries for monitoring
"""

import logging
import json
import sys
import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
try:
    from stakeholder_manager import (
        StakeholderIndex,
        is_external_email,
        generate_slug,
        infer_organization_from_email
    )
except ImportError:
    logger.warning("Could not import stakeholder_manager utilities, using fallbacks")
    
    def is_external_email(email: str) -> bool:
        """Fallback: Check if email is external"""
        if not email or '@' not in email:
            return False
        domain = email.split('@')[1].lower()
        return domain not in ['mycareerspan.com', 'theapply.ai', 'zo.computer']
    
    def generate_slug(name: str, organization: str = "") -> str:
        """Fallback: Generate slug from name and org"""
        base = name.lower().replace(' ', '-')
        if organization:
            org_slug = organization.lower().replace(' ', '-').replace('.', '')[:20]
            base = f"{base}-{org_slug}"
        return re.sub(r'[^a-z0-9-]', '', base)
    
    def infer_organization_from_email(email: str) -> str:
        """Fallback: Extract organization from email domain"""
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
STAKEHOLDER_DIR = Path("/home/workspace/N5/stakeholders")
INDEX_FILE = STAKEHOLDER_DIR / "index.jsonl"
PENDING_DIR = STAKEHOLDER_DIR / ".pending_updates"
STATE_FILE = Path("/home/workspace/N5/.state/email_scanner_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
PENDING_DIR.mkdir(parents=True, exist_ok=True)

# Internal domains (exclude from stakeholder discovery)
INTERNAL_DOMAINS = {
    "mycareerspan.com",
    "theapply.ai",
    "zo.computer"
}

# Gmail search keywords for meeting-related emails
MEETING_KEYWORDS = [
    "calendar invite",
    "meeting invitation", 
    "zoom.us",
    "meet.google.com",
    "calendly.com",
    "when2meet.com",
    "invited you to",
    "has invited you",
    "meeting scheduled",
    "meeting confirmed",
    "calendar event"
]


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
    # Start from 24 hours ago on first run
    initial_time = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
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


def extract_emails_from_text(text: str) -> List[str]:
    """Extract all email addresses from text"""
    if not text:
        return []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return [e.lower() for e in emails if is_external_email(e)]


def extract_name_from_email_context(email: str, text: str) -> Optional[str]:
    """Try to extract name from email context in text"""
    if not text or not email:
        return None
    
    # Look for patterns like "Name <email>" or "email (Name)"
    patterns = [
        rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*<{re.escape(email)}>',
        rf'{re.escape(email)}\s*\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\)',
        rf'From:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*<{re.escape(email)}>'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def parse_email_for_participants(email_data: Dict) -> List[Dict]:
    """
    Parse email data to extract external participants
    
    Returns list of dicts: {"email": str, "name": Optional[str], "context": str}
    """
    participants = []
    
    # Get email body (snippet or full)
    body = email_data.get('snippet', '') + '\n' + email_data.get('body', '')
    
    # Extract all external emails
    external_emails = extract_emails_from_text(body)
    
    for email in external_emails:
        # Try to find associated name
        name = extract_name_from_email_context(email, body)
        
        participant = {
            "email": email,
            "name": name,
            "organization": infer_organization_from_email(email),
            "source_email_id": email_data.get('id', ''),
            "discovered_at": datetime.now(timezone.utc).isoformat()
        }
        participants.append(participant)
    
    return participants


def queue_stakeholder_for_creation(participant: Dict):
    """Queue a new stakeholder discovery for profile creation"""
    try:
        slug = generate_slug(
            participant.get('name') or participant['email'].split('@')[0],
            participant.get('organization', '')
        )
        
        queue_file = PENDING_DIR / f"{slug}_{int(datetime.now().timestamp())}.json"
        
        with open(queue_file, 'w') as f:
            json.dump(participant, f, indent=2)
        
        log.info(f"Queued stakeholder: {participant['email']} -> {queue_file.name}")
        
    except Exception as e:
        log.error(f"Error queuing stakeholder {participant.get('email')}: {e}")


def build_gmail_query(last_scan_time: str) -> str:
    """Build Gmail search query for meeting-related emails"""
    # Convert ISO timestamp to Gmail format (YYYY/MM/DD)
    try:
        dt = datetime.fromisoformat(last_scan_time.replace('Z', '+00:00'))
        date_str = dt.strftime('%Y/%m/%d')
    except:
        # Fallback: yesterday
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    
    # Build query with keywords
    keyword_query = ' OR '.join([f'"{kw}"' for kw in MEETING_KEYWORDS[:5]])  # Limit for query length
    
    # Exclude internal domains
    exclude_query = ' '.join([f'-from:*@{domain}' for domain in INTERNAL_DOMAINS])
    
    query = f'after:{date_str} ({keyword_query}) {exclude_query}'
    
    return query


def scan_gmail_for_meetings(dry_run: bool = False) -> Dict:
    """
    Scan Gmail for meeting-related emails
    
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
        log.info("[DRY RUN] Would queue new discoveries to {PENDING_DIR}")
        return {
            "status": "dry_run",
            "new_stakeholders": 0,
            "emails_scanned": 0
        }
    
    discovered_stakeholders = []
    emails_scanned = 0
    
    try:
        # NOTE: This is where actual Gmail API integration would go
        # The script is designed to be called BY the Zo agent which has access to use_app_gmail
        # When running as a scheduled task, it will be executed in a context where Gmail API is available
        
        # For now, this is a DOCUMENTED PLACEHOLDER
        # The Zo agent will need to wrap this script or inject Gmail data
        
        log.info("Gmail API integration point - awaiting agent context")
        log.info("To complete: Agent should call use_app_gmail('gmail-find-email', {'q': query, 'maxResults': 50})")
        
        # PLACEHOLDER - Agent will inject email data here
        emails = []  # Would come from use_app_gmail
        
        for email in emails:
            # Skip if already processed
            if email['id'] in processed_ids:
                continue
            
            # Extract participants
            participants = parse_email_for_participants(email)
            
            for participant in participants:
                # Skip if already exists
                if participant['email'] in existing_stakeholders:
                    continue
                
                # Queue for creation
                queue_stakeholder_for_creation(participant)
                discovered_stakeholders.append(participant)
                existing_stakeholders.add(participant['email'])  # Prevent duplicates in same scan
            
            processed_ids.add(email['id'])
            emails_scanned += 1
        
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
        {"email": p['email'], "name": p.get('name'), "org": p.get('organization')}
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
        for p in discovered_stakeholders:
            log.info(f"  - {p['email']} ({p.get('name', 'name unknown')}) @ {p.get('organization', 'org unknown')}")
    
    log.info(f"✅ Scan complete: {emails_scanned} emails processed, "
            f"{len(discovered_stakeholders)} new stakeholders discovered")
    log.info(f"Next scan in ~20 minutes")
    
    return result


def main(dry_run: bool = False) -> int:
    """Main execution"""
    try:
        result = scan_gmail_for_meetings(dry_run=dry_run)
        
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
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run))

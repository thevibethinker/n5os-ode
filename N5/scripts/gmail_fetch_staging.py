#!/usr/bin/env python3
"""
Gmail Fetch to Staging - Phase 1 of Option B Architecture

Fetches meeting-related emails from Gmail via service account and writes
minimal parsed data to staging directory for LLM processing.

Architecture:
  Phase 1 (this script): Service Account → Gmail API → Staging JSON
  Phase 2 (scheduled task): Read Staging → LLM Extract → Knowledge/Records
"""

import logging
import json
import sys
import argparse
import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from email.utils import parseaddr
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger(__name__)

# Configuration
WORKSPACE_ROOT = Path("/home/workspace")
CREDS_FILE = WORKSPACE_ROOT / "N5/config/credentials/google_service_account.json"
STATE_FILE = WORKSPACE_ROOT / "N5/.state/email_scanner_state.json"
STAGING_ROOT = WORKSPACE_ROOT / "Records/Temporary/email_staging"
USER_EMAIL = "vrijen@mycareerspan.com"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email domains to exclude (internal)
INTERNAL_DOMAINS = ['mycareerspan.com', 'theapply.ai', 'zo.computer']


def load_state() -> Dict:
    """Load scanner state"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_scan_time": None,
        "processed_message_ids": [],
        "discovered_count": 0
    }


def save_state(state: Dict) -> None:
    """Save scanner state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))
    log.info(f"✓ State saved: {len(state['processed_message_ids'])} messages processed")


def build_gmail_query(last_scan_time: Optional[str]) -> str:
    """Build Gmail search query for meeting-related emails"""
    
    # Time filter
    if last_scan_time:
        try:
            dt = datetime.fromisoformat(last_scan_time.replace('Z', '+00:00'))
            days_ago = (datetime.now(timezone.utc) - dt).days
            if days_ago < 30:
                time_filter = f"newer_than:{days_ago}d"
            else:
                time_filter = "newer_than:30d"
        except:
            time_filter = "newer_than:7d"
    else:
        time_filter = "newer_than:7d"
    
    # Meeting indicators - use simpler query
    query = f"(meeting OR calendar OR invite OR invitation OR zoom OR scheduled) {time_filter}"
    
    return query


def extract_email_addresses(header_value: str) -> List[str]:
    """Extract email addresses from header"""
    emails = []
    if not header_value:
        return emails
    
    for part in header_value.split(','):
        _, email = parseaddr(part.strip())
        if email and '@' in email:
            emails.append(email.lower())
    
    return emails


def is_external_email(email: str) -> bool:
    """Check if email is external"""
    if not email or '@' not in email:
        return False
    domain = email.split('@')[1].lower()
    return domain not in INTERNAL_DOMAINS


def get_message_body(payload: Dict) -> str:
    """Extract email body text"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    elif 'body' in payload:
        data = payload.get('body', {}).get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    return body[:3000]  # Limit body size


def parse_email_minimal(service, message_id: str) -> Optional[Dict]:
    """
    Fetch and parse email with minimal processing.
    No LLM extraction - just structural data for staging.
    """
    try:
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] 
                   for h in msg['payload'].get('headers', [])}
        
        # Extract basic fields
        subject = headers.get('Subject', '')
        from_email = extract_email_addresses(headers.get('From', ''))[0] if headers.get('From') else ''
        to_emails = extract_email_addresses(headers.get('To', ''))
        cc_emails = extract_email_addresses(headers.get('Cc', ''))
        date = headers.get('Date', '')
        
        # Get body
        body = get_message_body(msg['payload'])
        
        # Check if contains external participants
        all_emails = [from_email] + to_emails + cc_emails
        external_emails = [e for e in all_emails if is_external_email(e)]
        
        if not external_emails:
            log.debug(f"   No external participants in {message_id}")
            return None
        
        return {
            "message_id": message_id,
            "subject": subject,
            "from": from_email,
            "to": to_emails,
            "cc": cc_emails,
            "date": date,
            "body": body,
            "external_emails": external_emails,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HttpError as e:
        log.error(f"   HTTP error fetching {message_id}: {e}")
        return None
    except Exception as e:
        log.error(f"   Error parsing {message_id}: {e}")
        return None


def write_staging_file(email_data: Dict) -> Path:
    """Write email data to staging directory"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    staging_dir = STAGING_ROOT / today
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"msg_{email_data['message_id']}_{timestamp}.json"
    filepath = staging_dir / filename
    
    filepath.write_text(json.dumps(email_data, indent=2))
    return filepath


def cleanup_old_staging(days: int = 60) -> int:
    """Remove staging files older than N days"""
    if not STAGING_ROOT.exists():
        return 0
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    removed = 0
    
    for date_dir in STAGING_ROOT.iterdir():
        if not date_dir.is_dir():
            continue
        
        try:
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if dir_date < cutoff:
                for f in date_dir.iterdir():
                    f.unlink()
                date_dir.rmdir()
                removed += 1
                log.info(f"   Removed old staging: {date_dir.name}")
        except ValueError:
            continue
    
    return removed


def fetch_gmail_to_staging(dry_run: bool = False) -> Dict:
    """
    Main function: Fetch Gmail messages and write to staging.
    No LLM processing in this phase.
    """
    log.info("=== Gmail Fetch to Staging (Phase 1) ===")
    
    # Load state
    state = load_state()
    processed_ids = set(state.get('processed_message_ids', []))
    
    # Cleanup old staging files
    if not dry_run:
        removed = cleanup_old_staging(days=60)
        if removed:
            log.info(f"✓ Cleaned up {removed} old staging directories")
    
    # Connect to Gmail
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(CREDS_FILE), scopes=SCOPES
        )
        delegated_creds = credentials.with_subject(USER_EMAIL)
        service = build('gmail', 'v1', credentials=delegated_creds)
        log.info(f"✓ Gmail API connected: {USER_EMAIL}")
    except Exception as e:
        log.error(f"Failed to connect to Gmail: {e}")
        return {"status": "error", "error": str(e)}
    
    # Build query
    query = build_gmail_query(state.get('last_scan_time'))
    log.info(f"Query: {query}")
    
    # Fetch messages
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        log.info(f"✓ Found {len(messages)} messages")
        
        if not messages:
            return {"status": "success", "new_messages": 0, "staged": 0}
        
    except HttpError as e:
        log.error(f"Gmail query failed: {e}")
        return {"status": "error", "error": str(e)}
    
    # Process messages
    new_count = 0
    staged_count = 0
    
    for msg in messages:
        msg_id = msg['id']
        
        if msg_id in processed_ids:
            continue
        
        new_count += 1
        log.info(f"Processing {msg_id} ({new_count}/{len(messages)})")
        
        # Parse email
        email_data = parse_email_minimal(service, msg_id)
        
        if not email_data:
            processed_ids.add(msg_id)
            continue
        
        log.info(f"   Subject: {email_data['subject'][:60]}")
        log.info(f"   External: {len(email_data['external_emails'])} participants")
        
        if dry_run:
            log.info(f"   [DRY RUN] Would stage: {email_data['message_id']}")
        else:
            # Write to staging
            filepath = write_staging_file(email_data)
            log.info(f"   ✓ Staged: {filepath.name}")
            staged_count += 1
        
        processed_ids.add(msg_id)
    
    # Update state
    if not dry_run:
        state['last_scan_time'] = datetime.now(timezone.utc).isoformat()
        state['processed_message_ids'] = list(processed_ids)[-1000:]  # Keep last 1000
        save_state(state)
    
    log.info(f"\n✓ Complete: {new_count} new messages, {staged_count} staged")
    
    return {
        "status": "success",
        "new_messages": new_count,
        "staged": staged_count
    }


def main(dry_run: bool = False) -> int:
    """Main execution"""
    try:
        result = fetch_gmail_to_staging(dry_run=dry_run)
        
        if result['status'] == 'success':
            return 0
        else:
            log.error(f"Fetch failed: {result.get('error')}")
            return 1
            
    except Exception as e:
        log.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gmail fetch to staging (Phase 1)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run))

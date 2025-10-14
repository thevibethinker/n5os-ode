#!/usr/bin/env python3
"""
Scheduled Email Scan Wrapper
Runs background_email_scanner.py with Gmail API access via Zo agent context

This script is called by scheduled tasks and injects Gmail data into the scanner.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Import the scanner
sys.path.insert(0, str(Path(__file__).parent))
from background_email_scanner import (
    load_state,
    save_state,
    load_existing_stakeholders,
    build_gmail_query,
    parse_email_for_participants,
    queue_stakeholder_for_creation,
    log
)

def fetch_gmail_emails(query: str, max_results: int = 50) -> list:
    """
    Fetch emails from Gmail using agent context
    
    NOTE: This function needs to be implemented with actual use_app_gmail integration
    The scheduled task should be configured to run this via Zo agent which has Gmail access
    """
    
    # PLACEHOLDER: This would be called by Zo agent with:
    # use_app_gmail('gmail-find-email', {
    #     'q': query,
    #     'maxResults': max_results,
    #     'metadataOnly': False
    # })
    
    log.info(f"Gmail API integration needed: query='{query}', max_results={max_results}")
    log.info("Scheduled task should be executed by Zo agent with Gmail access")
    
    return []

def run_scan_with_gmail_access():
    """Run email scan with Gmail API access"""
    try:
        log.info("=== Scheduled Email Scan: Starting ===")
        
        # Load state
        state = load_state()
        existing_stakeholders = load_existing_stakeholders()
        
        # Build query
        query = build_gmail_query(state['last_scan_time'])
        
        # Fetch emails from Gmail
        log.info(f"Fetching emails with query: {query}")
        emails = fetch_gmail_emails(query)
        
        if not emails:
            log.info("No new emails found")
            state['last_scan_time'] = datetime.now(timezone.utc).isoformat()
            save_state(state)
            return 0
        
        log.info(f"Retrieved {len(emails)} emails from Gmail")
        
        # Process emails
        discovered_stakeholders = []
        processed_ids = set(state.get('processed_message_ids', []))
        
        for email in emails:
            if email['id'] in processed_ids:
                continue
            
            participants = parse_email_for_participants(email)
            
            for participant in participants:
                if participant['email'] not in existing_stakeholders:
                    queue_stakeholder_for_creation(participant)
                    discovered_stakeholders.append(participant)
                    existing_stakeholders.add(participant['email'])
            
            processed_ids.add(email['id'])
        
        # Update state
        state['last_scan_time'] = datetime.now(timezone.utc).isoformat()
        state['processed_message_ids'] = list(processed_ids)[-1000:]
        state['discovered_count'] += len(discovered_stakeholders)
        save_state(state)
        
        log.info(f"✅ Scan complete: {len(emails)} emails processed, "
                f"{len(discovered_stakeholders)} new stakeholders discovered")
        
        return 0
        
    except Exception as e:
        log.error(f"Error during scheduled scan: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_scan_with_gmail_access())

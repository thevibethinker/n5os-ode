#!/usr/bin/env python3
"""
Meeting Email Scanner for Stakeholder Discovery

Scans Gmail for meeting-related emails, extracts external participants,
performs basic enrichment, and stages contacts for tag suggestion.

Part of: N5 Stakeholder Auto-Tagging System (Phase 1A)
Version: 1.0.0
"""

import logging
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
log = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
STAGING_DIR = N5_ROOT / "records" / "crm" / "staging"
STATE_FILE = STAGING_DIR / ".scan_state.json"


class MeetingEmailScanner:
    """
    Scan Gmail for meeting invitations and extract external stakeholders
    """
    
    def __init__(self, gmail_tool=None, calendar_tool=None, lookback_days=90):
        """
        Initialize email scanner
        
        Args:
            gmail_tool: Zo's Gmail API tool (use_app_gmail)
            calendar_tool: Zo's Calendar API tool (use_app_google_calendar)
            lookback_days: How far back to scan (default: 90 days)
        """
        self.gmail_tool = gmail_tool
        self.calendar_tool = calendar_tool
        self.lookback_days = lookback_days
        
        # Internal domains (exclude from external stakeholders)
        self.internal_domains = {
            "mycareerspan.com",
            "careerspan.com",
            "zo.computer",
            "gmail.com",  # V's personal email
        }
        
        # Known VC domains for basic enrichment
        self.vc_domains = {
            "a16z.com", "sequoiacap.com", "greylock.com", "bessemer.com",
            "accel.com", "nea.com", "khoslaventures.com", "foundationcapital.com",
            "benchmark.com", "lightspeedvp.com", "generalcatalyst.com",
            "indexventures.com", "unionlabs.com", "craft.co"
        }
        
        # Recruiting/HR company keywords
        self.recruiting_keywords = [
            "recruiting", "talent", "hire", "hiring", "staffing", 
            "jobs", "careers", "headhunter"
        ]
        
        # Ensure directories exist
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    def scan_for_meeting_participants(self) -> Dict:
        """
        Main scanning function: find meeting emails and extract participants
        
        Returns:
            dict: Summary of scan results
        """
        log.info(f"Starting meeting email scan (lookback: {self.lookback_days} days)")
        
        # Step 1: Find meeting-related emails
        meeting_emails = self._find_meeting_emails()
        log.info(f"Found {len(meeting_emails)} meeting-related emails")
        
        # Step 2: Extract external participants
        participants = self._extract_external_participants(meeting_emails)
        log.info(f"Extracted {len(participants)} unique external participants")
        
        # Step 3: Basic enrichment (domain analysis)
        enriched_contacts = self._enrich_contacts(participants)
        log.info(f"Enriched {len(enriched_contacts)} contacts")
        
        # Step 4: Stage contacts for tag suggestion
        staged = self._stage_contacts(enriched_contacts)
        log.info(f"Staged {len(staged)} new contacts")
        
        # Step 5: Save scan state
        self._save_scan_state({
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "lookback_days": self.lookback_days,
            "meeting_emails_found": len(meeting_emails),
            "participants_extracted": len(participants),
            "contacts_staged": len(staged)
        })
        
        summary = {
            "meeting_emails": len(meeting_emails),
            "unique_participants": len(participants),
            "enriched_contacts": len(enriched_contacts),
            "newly_staged": len(staged),
            "staging_dir": str(STAGING_DIR)
        }
        
        log.info("Scan complete")
        return summary
    
    def _find_meeting_emails(self) -> List[Dict]:
        """
        Search Gmail for meeting-related emails
        
        Returns:
            List of email message dicts
        """
        if not self.gmail_tool:
            log.warning("Gmail tool not available")
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=self.lookback_days)
            after_date = start_date.strftime('%Y/%m/%d')
            
            # Search queries for meeting invitations
            meeting_queries = [
                f"(subject:meeting OR subject:call OR subject:intro) after:{after_date}",
                f"(subject:\"set up\" OR subject:\"schedule\") after:{after_date}",
                f"\"calendar invite\" after:{after_date}",
                f"\"Google Meet\" OR \"Zoom\" after:{after_date}",
            ]
            
            all_emails = []
            seen_ids = set()
            
            for query in meeting_queries:
                log.info(f"Searching: {query[:50]}...")
                
                results = self.gmail_tool('gmail-find-email', {
                    'q': query,
                    'maxResults': 50,
                    'withTextPayload': True
                })
                
                if results and results.get('messages'):
                    for message in results['messages']:
                        msg_id = message.get('id')
                        if msg_id and msg_id not in seen_ids:
                            all_emails.append(message)
                            seen_ids.add(msg_id)
            
            log.info(f"Total unique meeting emails found: {len(all_emails)}")
            return all_emails
            
        except Exception as e:
            log.error(f"Error finding meeting emails: {e}")
            return []
    
    def _extract_external_participants(self, emails: List[Dict]) -> Dict[str, Dict]:
        """
        Extract external email addresses and basic info from messages
        
        Args:
            emails: List of Gmail message dicts
            
        Returns:
            Dict mapping email -> participant info
        """
        participants = {}
        
        for email_msg in emails:
            # Extract headers
            headers = email_msg.get('payload', {}).get('headers', [])
            
            # Get From, To, CC headers
            from_addr = self._extract_header(headers, 'From')
            to_addrs = self._extract_header(headers, 'To')
            cc_addrs = self._extract_header(headers, 'Cc')
            
            # Parse all email addresses
            all_addresses = []
            if from_addr:
                all_addresses.extend(self._parse_email_addresses(from_addr))
            if to_addrs:
                all_addresses.extend(self._parse_email_addresses(to_addrs))
            if cc_addrs:
                all_addresses.extend(self._parse_email_addresses(cc_addrs))
            
            # Filter to external only
            for addr_info in all_addresses:
                email = addr_info['email'].lower()
                
                # Skip if internal
                if self._is_internal_email(email):
                    continue
                
                # Add or update participant
                if email not in participants:
                    participants[email] = {
                        'email': email,
                        'name': addr_info.get('name', ''),
                        'domain': email.split('@')[1] if '@' in email else '',
                        'first_seen': datetime.now(timezone.utc).isoformat(),
                        'email_count': 0,
                        'meeting_contexts': []
                    }
                
                # Increment email count
                participants[email]['email_count'] += 1
                
                # Extract subject as meeting context
                subject = self._extract_header(headers, 'Subject')
                if subject and subject not in participants[email]['meeting_contexts']:
                    participants[email]['meeting_contexts'].append(subject)
        
        return participants
    
    def _enrich_contacts(self, participants: Dict[str, Dict]) -> List[Dict]:
        """
        Basic enrichment: domain analysis, company inference
        
        Args:
            participants: Dict of participant info
            
        Returns:
            List of enriched contact dicts
        """
        enriched = []
        
        for email, info in participants.items():
            contact = info.copy()
            
            # Extract company from domain
            domain = contact['domain']
            company = self._infer_company_from_domain(domain)
            contact['company'] = company
            
            # Check if VC firm
            if domain in self.vc_domains:
                contact['inferred_stakeholder_type'] = 'investor'
                contact['confidence'] = 0.85
                contact['reasoning'] = 'Known VC firm domain'
            
            # Check if recruiting/HR company
            elif any(kw in domain.lower() for kw in self.recruiting_keywords):
                contact['inferred_stakeholder_type'] = 'job_seeker'
                contact['confidence'] = 0.70
                contact['reasoning'] = 'Recruiting/HR company domain'
            
            # Check if corporate email
            elif '.' in domain and not domain.endswith(('.gov', '.edu', '.org')):
                contact['inferred_stakeholder_type'] = 'prospect'
                contact['confidence'] = 0.50
                contact['reasoning'] = 'Corporate email domain'
            
            else:
                contact['inferred_stakeholder_type'] = 'unknown'
                contact['confidence'] = 0.30
                contact['reasoning'] = 'Unable to infer from domain'
            
            # Always mark as new relationship
            contact['inferred_relationship'] = 'new'
            
            # Enrichment metadata
            contact['enrichment_level'] = 'basic'
            contact['enrichment_timestamp'] = datetime.now(timezone.utc).isoformat()
            contact['data_sources'] = ['email_metadata', 'domain_analysis']
            
            enriched.append(contact)
        
        return enriched
    
    def _stage_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """
        Save contacts to staging area for tag suggestion
        
        Args:
            contacts: List of enriched contact dicts
            
        Returns:
            List of newly staged contacts (excluding duplicates)
        """
        newly_staged = []
        
        # Load existing staged contacts
        existing = self._load_existing_staged()
        existing_emails = {c['email'] for c in existing}
        
        for contact in contacts:
            email = contact['email']
            
            # Skip if already staged
            if email in existing_emails:
                log.debug(f"Skipping duplicate: {email}")
                continue
            
            # Save to staging
            filename = self._generate_staging_filename(email)
            filepath = STAGING_DIR / filename
            
            try:
                with open(filepath, 'w') as f:
                    json.dump(contact, f, indent=2)
                
                newly_staged.append(contact)
                log.info(f"Staged: {email} ({contact.get('company', 'Unknown')})")
                
            except Exception as e:
                log.error(f"Error staging {email}: {e}")
        
        return newly_staged
    
    # Helper methods
    
    def _extract_header(self, headers: List[Dict], name: str) -> Optional[str]:
        """Extract header value by name"""
        for header in headers:
            if header.get('name') == name:
                return header.get('value', '')
        return None
    
    def _parse_email_addresses(self, header_value: str) -> List[Dict]:
        """
        Parse email addresses from header value
        
        Format: "Name <email@domain.com>, Other Name <other@domain.com>"
        
        Returns:
            List of {'name': str, 'email': str} dicts
        """
        if not header_value:
            return []
        
        addresses = []
        
        # Regex to match "Name <email>" or just "email"
        pattern = r'(?:"?([^"<]+)"?\s*)?<?([\w\.-]+@[\w\.-]+)>?'
        
        for match in re.finditer(pattern, header_value):
            name = match.group(1)
            email = match.group(2)
            
            if email:
                addresses.append({
                    'name': name.strip() if name else '',
                    'email': email.strip().lower()
                })
        
        return addresses
    
    def _is_internal_email(self, email: str) -> bool:
        """Check if email is internal (should be excluded)"""
        if not email or '@' not in email:
            return True
        
        domain = email.split('@')[1].lower()
        return domain in self.internal_domains
    
    def _infer_company_from_domain(self, domain: str) -> str:
        """Infer company name from email domain"""
        if not domain:
            return "Unknown"
        
        # Remove TLD and subdomains
        parts = domain.split('.')
        if len(parts) >= 2:
            company_name = parts[-2]  # e.g., "acme" from "mail.acme.com"
        else:
            company_name = parts[0]
        
        # Capitalize
        return company_name.title()
    
    def _generate_staging_filename(self, email: str) -> str:
        """Generate staging filename from email"""
        # Replace @ and . with underscores
        safe_name = email.replace('@', '_').replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{timestamp}_{safe_name}.json"
    
    def _load_existing_staged(self) -> List[Dict]:
        """Load all existing staged contacts"""
        existing = []
        
        if not STAGING_DIR.exists():
            return existing
        
        for filepath in STAGING_DIR.glob("*.json"):
            # Skip state file
            if filepath.name.startswith('.'):
                continue
            
            try:
                with open(filepath, 'r') as f:
                    contact = json.load(f)
                    existing.append(contact)
            except Exception as e:
                log.warning(f"Error loading {filepath.name}: {e}")
        
        return existing
    
    def _save_scan_state(self, state: Dict):
        """Save scan state to file"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
            log.info(f"Scan state saved to {STATE_FILE}")
        except Exception as e:
            log.error(f"Error saving scan state: {e}")
    
    def load_scan_state(self) -> Optional[Dict]:
        """Load previous scan state"""
        if not STATE_FILE.exists():
            return None
        
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error loading scan state: {e}")
            return None


def run_scan_with_zo_tools(use_app_gmail, use_app_google_calendar, lookback_days=90):
    """
    Run meeting email scan with Zo's API tools
    
    Args:
        use_app_gmail: Zo's Gmail tool function
        use_app_google_calendar: Zo's Calendar tool function
        lookback_days: Days to look back (default: 90)
        
    Returns:
        dict: Scan summary
    """
    scanner = MeetingEmailScanner(
        gmail_tool=use_app_gmail,
        calendar_tool=use_app_google_calendar,
        lookback_days=lookback_days
    )
    
    summary = scanner.scan_for_meeting_participants()
    
    return summary


def main():
    """CLI entry point"""
    print("Meeting Email Scanner v1.0.0")
    print("=" * 60)
    print("Part of: N5 Stakeholder Auto-Tagging System (Phase 1A)")
    print("")
    print("This script is designed to be called by Zo with API tools.")
    print("It cannot run standalone.")
    print("")
    print("Usage from Zo:")
    print("  from scan_meeting_emails import run_scan_with_zo_tools")
    print("  summary = run_scan_with_zo_tools(use_app_gmail, use_app_google_calendar)")
    print("")
    print(f"Staging directory: {STAGING_DIR}")
    print(f"State file: {STATE_FILE}")
    print("")


if __name__ == "__main__":
    main()

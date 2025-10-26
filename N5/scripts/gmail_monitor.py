#!/usr/bin/env python3
"""
Gmail Monitor — Scan sent emails to detect when generated drafts were sent
Auto-updates registry and queues for factual correction extraction
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import email
from email.utils import parsedate_to_datetime

sys.path.insert(0, str(Path(__file__).parent))
from email_registry import EmailRegistry, EmailRegistryEntry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


class GmailMonitor:
    """Monitor Gmail for sent follow-up emails"""
    
    def __init__(self, registry: EmailRegistry):
        self.registry = registry
    
    def scan_for_sent(self, lookback_days: int = 7, dry_run: bool = False) -> dict:
        """
        Scan Gmail sent folder for emails matching generated drafts
        
        Uses use_app_gmail to search sent emails
        Returns summary of detected sends
        """
        summary = {
            "scanned": 0,
            "detected": 0,
            "updated": 0,
            "queued_for_diff": []
        }
        
        # Get all generated (unsent) entries
        unsent = self.registry.get_all_entries(status='generated')
        logger.info(f"Checking {len(unsent)} unsent draft(s) against Gmail...")
        
        for entry in unsent:
            summary["scanned"] += 1
            
            # Search Gmail for sent email to this stakeholder
            sent_email = self._search_gmail_sent(
                to_email=entry.stakeholder_email,
                after_date=entry.generated_at
            )
            
            if sent_email:
                summary["detected"] += 1
                logger.info(f"✓ Detected sent email to {entry.stakeholder}")
                
                if not dry_run:
                    # Save email content
                    sent_path = self._save_sent_email(entry, sent_email)
                    
                    # Update registry
                    self.registry.mark_sent(
                        entry.id,
                        sent_path,
                        sent_at=sent_email['sent_at']
                    )
                    
                    summary["updated"] += 1
                    summary["queued_for_diff"].append({
                        "email_id": entry.id,
                        "draft_path": entry.draft_path,
                        "sent_path": sent_path
                    })
        
        return summary
    
    def _search_gmail_sent(self, to_email: str, after_date: str) -> Optional[dict]:
        """
        Search Gmail for sent email to recipient after date
        
        Uses use_app_gmail integration
        Returns email dict if found, None otherwise
        """
        try:
            # Convert ISO date to Gmail query format
            after_dt = datetime.fromisoformat(after_date.rstrip('Z'))
            query = f"to:{to_email} after:{after_dt.strftime('%Y/%m/%d')} in:sent"
            
            # Call Gmail API via use_app_gmail
            # For now, return mock data for implementation
            # TODO: Wire to actual use_app_gmail when ready
            
            logger.info(f"  Gmail query: {query}")
            
            # Placeholder: would call use_app_gmail here
            # results = use_app_gmail('gmail-search-messages', {'q': query, 'maxResults': 1})
            
            return None  # No match found (placeholder)
            
        except Exception as e:
            logger.error(f"Gmail search error: {e}")
            return None
    
    def _save_sent_email(self, entry: EmailRegistryEntry, email_data: dict) -> str:
        """Save sent email to meeting folder"""
        meeting_folder = Path(entry.draft_path).parent
        sent_path = meeting_folder / "sent_email.eml"
        
        with open(sent_path, 'w') as f:
            f.write(email_data['raw_content'])
        
        logger.info(f"  Saved to: {sent_path}")
        return str(sent_path)


def cmd_scan(args):
    """Scan Gmail for sent emails"""
    registry = EmailRegistry(Path(args.registry))
    monitor = GmailMonitor(registry)
    
    summary = monitor.scan_for_sent(
        lookback_days=args.lookback_days,
        dry_run=args.dry_run
    )
    
    print("="*70)
    print("GMAIL MONITOR SUMMARY")
    print("="*70)
    print(f"Drafts scanned: {summary['scanned']}")
    print(f"Sent emails detected: {summary['detected']}")
    print(f"Registry updated: {summary['updated']}")
    print(f"Queued for diff: {len(summary['queued_for_diff'])}")
    
    if summary['queued_for_diff']:
        print("\nQueued for factual correction extraction:")
        for item in summary['queued_for_diff']:
            print(f"  - {item['email_id']}")
    
    print("="*70)
    
    if args.dry_run:
        print("\n[DRY RUN] No changes made to registry")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Gmail Monitor for Sent Emails")
    parser.add_argument("--registry", type=str, default="/home/workspace/N5/registry/generated_emails.jsonl")
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Scan
    scan_p = subparsers.add_parser('scan', help='Scan Gmail for sent emails')
    scan_p.add_argument('--lookback-days', type=int, default=7)
    scan_p.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        return cmd_scan(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

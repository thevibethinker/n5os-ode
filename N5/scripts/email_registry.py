#!/usr/bin/env python3
"""
Email Registry — Track generated follow-up emails and their send status
Facts-based validation system, not lessons
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("/home/workspace/N5/registry/generated_emails.jsonl")


@dataclass
class EmailRegistryEntry:
    """Single generated email tracking entry"""
    id: str
    meeting_id: str
    stakeholder: str
    stakeholder_email: str
    generated_at: str
    draft_path: str
    status: str = "generated"  # generated | sent | abandoned
    sent_at: Optional[str] = None
    sent_email_path: Optional[str] = None
    corrections_applied: bool = False
    follow_up_after: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.follow_up_after is None:
            # Default: 48hr follow-up
            gen_time = datetime.fromisoformat(self.generated_at.rstrip('Z'))
            self.follow_up_after = (gen_time + timedelta(hours=48)).isoformat() + 'Z'


class EmailRegistry:
    """Manage generated email tracking registry"""
    
    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self.registry_path = Path(registry_path) if isinstance(registry_path, str) else registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
    def create_entry(self, entry: EmailRegistryEntry) -> EmailRegistryEntry:
        """Add new entry to registry"""
        with open(self.registry_path, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')
        logger.info(f"✓ Registered email: {entry.id} for {entry.stakeholder}")
        return entry
    
    def get_entry(self, email_id: str) -> Optional[EmailRegistryEntry]:
        """Retrieve entry by ID"""
        if not self.registry_path.exists():
            return None
        
        with open(self.registry_path) as f:
            for line in f:
                data = json.loads(line.strip())
                if data['id'] == email_id:
                    return EmailRegistryEntry(**data)
        return None
    
    def get_all_entries(self, status: Optional[str] = None) -> List[EmailRegistryEntry]:
        """Get all entries, optionally filtered by status"""
        if not self.registry_path.exists():
            return []
        
        entries = []
        with open(self.registry_path) as f:
            for line in f:
                data = json.loads(line.strip())
                if status is None or data['status'] == status:
                    entries.append(EmailRegistryEntry(**data))
        return entries
    
    def update_entry(self, email_id: str, updates: Dict) -> bool:
        """Update entry (rewrite file with changes)"""
        if not self.registry_path.exists():
            return False
        
        lines = []
        found = False
        
        with open(self.registry_path) as f:
            for line in f:
                data = json.loads(line.strip())
                if data['id'] == email_id:
                    data.update(updates)
                    found = True
                lines.append(json.dumps(data))
        
        if found:
            with open(self.registry_path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            logger.info(f"✓ Updated {email_id}: {updates}")
        
        return found
    
    def mark_sent(self, email_id: str, sent_email_path: str, sent_at: Optional[str] = None) -> bool:
        """Mark email as sent"""
        if sent_at is None:
            sent_at = datetime.utcnow().isoformat() + 'Z'
        
        return self.update_entry(email_id, {
            'status': 'sent',
            'sent_at': sent_at,
            'sent_email_path': sent_email_path
        })
    
    def mark_corrections_applied(self, email_id: str) -> bool:
        """Mark corrections as applied (clears validation gate)"""
        return self.update_entry(email_id, {'corrections_applied': True})
    
    def get_unsent(self, check_follow_up: bool = True) -> List[EmailRegistryEntry]:
        """Get unsent emails, optionally filtered by follow_up_after deadline"""
        now = datetime.utcnow().isoformat() + 'Z'
        unsent = self.get_all_entries(status='generated')
        
        if check_follow_up:
            return [e for e in unsent if e.follow_up_after and e.follow_up_after < now]
        return unsent


def cmd_create(args):
    """Create new registry entry"""
    registry = EmailRegistry(args.registry)
    
    entry = EmailRegistryEntry(
        id=args.id,
        meeting_id=args.meeting_id,
        stakeholder=args.stakeholder,
        stakeholder_email=args.email,
        generated_at=args.generated_at or (datetime.utcnow().isoformat() + 'Z'),
        draft_path=args.draft_path,
        tags=args.tags.split(',') if args.tags else []
    )
    
    registry.create_entry(entry)
    print(json.dumps(asdict(entry), indent=2))
    return 0


def cmd_mark_sent(args):
    """Mark email as sent"""
    registry = EmailRegistry(args.registry)
    
    if registry.mark_sent(args.id, args.sent_path, args.sent_at):
        print(f"✓ Marked {args.id} as sent")
        return 0
    else:
        print(f"✗ Email {args.id} not found")
        return 1


def cmd_check_unsent(args):
    """Check for unsent emails needing follow-up"""
    registry = EmailRegistry(args.registry)
    unsent = registry.get_unsent(check_follow_up=True)
    
    if not unsent:
        print("✓ No overdue follow-ups")
        return 0
    
    print(f"⚠ {len(unsent)} emails need follow-up:\n")
    for entry in unsent:
        gen_time = datetime.fromisoformat(entry.generated_at.rstrip('Z'))
        days_ago = (datetime.utcnow() - gen_time).days
        
        print(f"- {entry.stakeholder} ({entry.meeting_id})")
        print(f"  Generated: {days_ago} days ago")
        print(f"  Draft: {entry.draft_path}")
        print()
    
    return 0


def cmd_list(args):
    """List all entries"""
    registry = EmailRegistry(args.registry)
    entries = registry.get_all_entries(status=args.status)
    
    print(json.dumps([asdict(e) for e in entries], indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Email Registry Manager")
    parser.add_argument("--registry", type=str, default=str(REGISTRY_PATH))
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Create
    create_p = subparsers.add_parser('create', help='Create new entry')
    create_p.add_argument('--id', required=True)
    create_p.add_argument('--meeting-id', required=True)
    create_p.add_argument('--stakeholder', required=True)
    create_p.add_argument('--email', required=True)
    create_p.add_argument('--draft-path', required=True)
    create_p.add_argument('--generated-at', default=None)
    create_p.add_argument('--tags', default=None)
    
    # Mark sent
    sent_p = subparsers.add_parser('mark-sent', help='Mark as sent')
    sent_p.add_argument('--id', required=True)
    sent_p.add_argument('--sent-path', required=True)
    sent_p.add_argument('--sent-at', default=None)
    
    # Check unsent
    subparsers.add_parser('check-unsent', help='Check for unsent emails')
    
    # List
    list_p = subparsers.add_parser('list', help='List entries')
    list_p.add_argument('--status', default=None)
    
    args = parser.parse_args()
    
    if args.command == 'create':
        return cmd_create(args)
    elif args.command == 'mark-sent':
        return cmd_mark_sent(args)
    elif args.command == 'check-unsent':
        return cmd_check_unsent(args)
    elif args.command == 'list':
        return cmd_list(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

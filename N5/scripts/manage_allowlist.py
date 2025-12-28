#!/usr/bin/env python3
"""
Manage Allowlists
Add senders to specific allowlists based on trigger codes.

Trigger codes:
  n5:events     → Add to events allowlist
  n5:newsletter → Add to newsletters allowlist
  n5:jobs       → Add to jobs allowlist

Usage:
  # Process a forwarded email file (extracts original sender)
  python3 manage_allowlist.py --input pending_emails.json
  
  # Add a sender directly
  python3 manage_allowlist.py --add events --sender "hello@example.com"
  
  # List all senders in an allowlist
  python3 manage_allowlist.py --list events
"""
import json
import argparse
import re
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path(__file__).parent.parent / "config" / "allowlists.json"

TRIGGER_MAP = {
    "n5:events": "events",
    "n5:newsletter": "newsletters",
    "n5:newsletters": "newsletters",
    "n5:jobs": "jobs",
    "n5:job": "jobs"
}


def load_config():
    if not CONFIG_FILE.exists():
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "allowlists": {
                "events": {"trigger": "n5:events", "senders": [], "domains": []},
                "newsletters": {"trigger": "n5:newsletter", "senders": [], "domains": []},
                "jobs": {"trigger": "n5:jobs", "senders": [], "domains": []}
            }
        }
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config):
    config["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def extract_email(from_header):
    """Extract email from 'Name <email@domain.com>' format."""
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1).lower()
    if '@' in from_header:
        return from_header.strip().lower()
    return None


def extract_original_sender(email_body):
    """Extract the original sender from a forwarded email."""
    patterns = [
        r'From:\s*([^\n]+)',
        r'---------- Forwarded message ---------\s*From:\s*([^\n]+)',
        r'Begin forwarded message:\s*From:\s*([^\n]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            return extract_email(match.group(1))
    return None


def add_sender(config, allowlist_type, sender):
    """Add a sender to an allowlist."""
    if allowlist_type not in config["allowlists"]:
        print(f"Unknown allowlist: {allowlist_type}")
        return False
    
    senders = config["allowlists"][allowlist_type]["senders"]
    if sender not in senders:
        senders.append(sender)
        print(f"Added {sender} to {allowlist_type} allowlist")
        return True
    else:
        print(f"{sender} already in {allowlist_type} allowlist")
        return False


def process_email_file(config, input_file):
    """Process a JSON file containing forwarded emails."""
    with open(input_file) as f:
        emails = json.load(f)
    
    added = 0
    for email in emails:
        subject = email.get("subject", "")
        body = email.get("body", "") or email.get("snippet", "")
        
        # Determine which allowlist from subject trigger
        allowlist_type = None
        for trigger, al_type in TRIGGER_MAP.items():
            if trigger.lower() in subject.lower():
                allowlist_type = al_type
                break
        
        if not allowlist_type:
            print(f"No trigger code found in subject: {subject[:50]}...")
            continue
        
        # Extract original sender
        sender = extract_original_sender(body)
        if not sender:
            # Fall back to the direct sender if not forwarded
            sender = extract_email(email.get("from", ""))
        
        if sender:
            if add_sender(config, allowlist_type, sender):
                added += 1
    
    return added


def list_allowlist(config, allowlist_type):
    """List all senders in an allowlist."""
    if allowlist_type not in config["allowlists"]:
        print(f"Unknown allowlist: {allowlist_type}")
        return
    
    al = config["allowlists"][allowlist_type]
    print(f"\n=== {allowlist_type.upper()} ALLOWLIST ===")
    print(f"Trigger: {al.get('trigger', 'N/A')}")
    print(f"Description: {al.get('description', 'N/A')}")
    print(f"\nSenders ({len(al.get('senders', []))}):")
    for s in sorted(al.get("senders", [])):
        print(f"  - {s}")
    print(f"\nDomains ({len(al.get('domains', []))}):")
    for d in sorted(al.get("domains", [])):
        print(f"  - @{d}")


def main():
    parser = argparse.ArgumentParser(description="Manage allowlists")
    parser.add_argument("--input", help="JSON file with forwarded emails to process")
    parser.add_argument("--add", help="Allowlist type to add to (events/newsletters/jobs)")
    parser.add_argument("--sender", help="Sender email to add")
    parser.add_argument("--list", dest="list_type", help="List senders in an allowlist")
    
    args = parser.parse_args()
    config = load_config()
    
    if args.list_type:
        list_allowlist(config, args.list_type)
        return
    
    if args.add and args.sender:
        add_sender(config, args.add, args.sender)
        save_config(config)
        return
    
    if args.input:
        added = process_email_file(config, args.input)
        if added > 0:
            save_config(config)
        print(f"\nProcessed: {added} new senders added")
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()


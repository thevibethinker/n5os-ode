#!/usr/bin/env python3
"""
Gmail Batch Enrichment - Request Generator

This script scans enriched profiles and generates Gmail enrichment requests
for Zo to process using use_app_gmail tool.

Architecture:
- Python script: Deterministic file scanning and request generation
- Zo: Semantic Gmail search and analysis using tools

Usage:
    python3 gmail_batch_enrichment.py --generate    # Generate requests
    python3 gmail_batch_enrichment.py --list        # List pending requests
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
REQUESTS_DIR = '/home/workspace/N5/data/gmail_enrichment_requests'

def ensure_requests_dir():
    """Ensure requests directory exists"""
    Path(REQUESTS_DIR).mkdir(parents=True, exist_ok=True)

def generate_gmail_enrichment_requests():
    """
    Generate Gmail enrichment request files for profiles.
    Zo will process these using use_app_gmail tool.
    """
    ensure_requests_dir()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get profiles that need Gmail enrichment
    c.execute("""
        SELECT id, email, name, yaml_path
        FROM profiles
        WHERE email IS NOT NULL
        AND email != ''
        ORDER BY last_contact_at DESC
        LIMIT 10
    """)
    
    profiles = c.fetchall()
    conn.close()
    
    if not profiles:
        print("No profiles found needing Gmail enrichment")
        return
    
    print(f"Generating Gmail enrichment requests for {len(profiles)} profiles...")
    
    for profile in profiles:
        request_file = Path(REQUESTS_DIR) / f"profile_{profile['id']}_gmail.json"
        
        # Skip if already exists
        if request_file.exists():
            print(f"  ⏭️  Profile {profile['id']} - request already exists")
            continue
        
        request = {
            "profile_id": profile['id'],
            "email": profile['email'],
            "name": profile['name'],
            "yaml_path": profile['yaml_path'],
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "enrichment_type": "gmail_threads"
        }
        
        with open(request_file, 'w') as f:
            json.dump(request, f, indent=2)
        
        print(f"  ✓ Profile {profile['id']} ({profile['email']}) - request created")
    
    print(f"\n✓ Generated {len(profiles)} Gmail enrichment requests")
    print(f"  Location: {REQUESTS_DIR}")
    print("\nNext: Have Zo process these requests using use_app_gmail tool")

def list_pending_requests():
    """List all pending Gmail enrichment requests"""
    ensure_requests_dir()
    
    request_files = list(Path(REQUESTS_DIR).glob("profile_*_gmail.json"))
    
    if not request_files:
        print("No pending Gmail enrichment requests")
        return
    
    print(f"Pending Gmail Enrichment Requests ({len(request_files)}):\n")
    
    for req_file in sorted(request_files):
        with open(req_file) as f:
            req = json.load(f)
        
        status = req.get('status', 'unknown')
        email = req.get('email', 'unknown')
        profile_id = req.get('profile_id', '?')
        
        status_icon = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'error': '❌'
        }.get(status, '❓')
        
        print(f"  {status_icon} Profile {profile_id}: {email} [{status}]")

def main():
    parser = argparse.ArgumentParser(description='Gmail Batch Enrichment Request Generator')
    parser.add_argument('--generate', action='store_true', help='Generate enrichment requests')
    parser.add_argument('--list', action='store_true', help='List pending requests')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_gmail_enrichment_requests()
    elif args.list:
        list_pending_requests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()



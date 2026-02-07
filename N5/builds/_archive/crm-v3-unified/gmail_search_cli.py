#!/usr/bin/env python3
"""
Gmail Search CLI - Standalone Gmail Search for CRM Enrichment

This is a BRIDGE script that allows the Python enrichment worker to search Gmail.
It saves results to a JSON file that can be formatted by other tools.

Usage:
    python3 gmail_search_cli.py search@example.com output.json

Architecture:
- This script will be called BY the enrichment worker (Python -> Python)
- It uses os.system to trigger a Zo command that performs the Gmail search
- Results are written to the output file specified

NOTE: This requires Zo to be available as a CLI tool OR requires manual Gmail API setup.
For now, this is a placeholder showing the integration pattern.
"""

import sys
import json
import subprocess
from pathlib import Path


def search_gmail_via_subprocess(email: str, output_file: str) -> bool:
    """
    Trigger Gmail search by creating a script for Zo to execute.
    
    This is a workaround - ideally we'd have Zo CLI or API access.
    For now, we create a marker file that indicates a search is needed.
    """
    # Create a pending request file
    request = {
        "action": "gmail_search",
        "email": email,
        "query": f"from:{email} OR to:{email}",
        "gmail_account": "attawar.v@gmail.com",
        "output_file": output_file,
        "status": "pending"
    }
    
    request_file = f"/tmp/crm_gmail_search_{email.replace('@', '_').replace('.', '_')}.json"
    
    with open(request_file, 'w') as f:
        json.dump(request, f, indent=2)
    
    print(f"✓ Created Gmail search request: {request_file}")
    print(f"  Target: {email}")
    print(f"  Output: {output_file}")
    print()
    print("⚠️  MANUAL STEP REQUIRED:")
    print(f"  Ask Zo to execute: @crm-gmail-enrichment {email}")
    print(f"  Or manually search Gmail and save results to: {output_file}")
    
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: gmail_search_cli.py <email> <output_file>")
        print()
        print("Example:")
        print("  python3 gmail_search_cli.py john@example.com /tmp/gmail_results.json")
        sys.exit(1)
    
    email = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"Gmail Search CLI")
    print(f"=" * 50)
    
    success = search_gmail_via_subprocess(email, output_file)
    
    if success:
        print("\n✓ Request created successfully")
        sys.exit(0)
    else:
        print("\n✗ Failed to create request")
        sys.exit(1)


if __name__ == "__main__":
    main()


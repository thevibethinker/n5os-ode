#!/usr/bin/env python3
"""
Content Library Enhancement Script
- Add key findings to existing entries
- Generate summaries
- Enhance metadata
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

LIBRARY_PATH = Path("/home/workspace/Personal/Content-Library/content-library.json")

def load_library():
    with open(LIBRARY_PATH, 'r') as f:
        return json.load(f)

def save_library(library):
    with open(LIBRARY_PATH, 'w') as f:
        json.dump(library, f, indent=2, sort_keys=True)
    print(f"Library saved ({len(library['entries'])} entries)")

def add_key_findings(entry_id, findings):
    """Add key findings to an entry"""
    library = load_library()
    
    if entry_id not in library['entries']:
        print(f"ERROR: Entry {entry_id} not found")
        return False
    
    entry = library['entries'][entry_id]
    
    if 'key_findings' not in entry:
        entry['key_findings'] = []
    
    entry['key_findings'].extend(findings)
    entry['key_findings'] = entry['key_findings'][:10]  # Max 10 findings
    
    library['metadata']['last_updated'] = datetime.now().isoformat()
    save_library(library)
    
    print(f"\n✓ Added {len(findings)} key findings to {entry_id}")
    return True

def set_summary(entry_id, summary):
    """Add/edit summary for an entry"""
    library = load_library()
    
    if entry_id not in library['entries']:
        print(f"ERROR: Entry {entry_id} not found")
        return False
    
    entry = library['entries'][entry_id]
    entry['summary'] = summary[:500]  # Max 500 chars
    
    library['metadata']['last_updated'] = datetime.now().isoformat()
    save_library(library)
    
    print(f"\n✓ Updated summary for {entry_id}")
    return True

def list_entries(limit=10):
    """List recent entries"""
    library = load_library()
    
    print(f"\nContent Library ({len(library['entries'])} entries)")
    print("=" * 60)
    
    entries = list(library['entries'].items())
    
    # Sort by date_added (newest first)
    entries.sort(key=lambda x: x[1].get('date_added', ''), reverse=True)
    
    for entry_id, entry in entries[:limit]:
        print(f"\n{entry_id}")
        print(f"  Title: {entry['title'][:60]}...")
        print(f"  Type: {entry['content_type']}")
        print(f"  Source: {entry['provenance']['source_type']}")
        print(f"  Topics: {', '.join(entry.get('topics', [])[:3])}")
        print(f"  Findings: {len(entry.get('key_findings', []))}")

def show_entry(entry_id):
    """Show full entry details"""
    library = load_library()
    
    if entry_id not in library['entries']:
        print(f"ERROR: Entry {entry_id} not found")
        return False
    
    entry = library['entries'][entry_id]
    
    print(f"\n{'=' * 70}")
    print(f"Entry: {entry_id}")
    print(f"{'=' * 70}")
    print(json.dumps(entry, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Enhance content library entries')
    parser.add_argument('--list', action='store_true', help='List recent entries')
    parser.add_argument('--show', help='Show specific entry')
    parser.add_argument('--add-findings', help='Entry ID to add findings to')
    parser.add_argument('--findings', nargs='+', help='Key findings (space-separated)')
    parser.add_argument('--summary', help='Entry ID to update summary')
    parser.add_argument('--summary-text', help='Summary text (use quotes)')
    
    args = parser.parse_args()
    
    if args.list:
        list_entries()
    elif args.show:
        show_entry(args.show)
    elif args.add_findings and args.findings:
        add_key_findings(args.add_findings, args.findings)
    elif args.summary and args.summary_text:
        set_summary(args.summary, args.summary_text)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()


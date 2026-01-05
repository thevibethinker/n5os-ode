#!/usr/bin/env python3
"""
review_triage.py - Display and manage the idea triage list.

Usage:
  python3 review_triage.py list              # Show all triage items
  python3 review_triage.py delete <id>       # Remove item from triage
  python3 review_triage.py promote <id>      # Move to lab (calls start_lab_session.py)
  python3 review_triage.py stats             # Show triage statistics

This script is the backend for the "review triage" workflow in Idea Lab.
"""

import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

TRIAGE_FILE = Path("/home/workspace/Lists/idea-triage.jsonl")
START_SESSION_SCRIPT = Path("/home/workspace/N5/scripts/start_lab_session.py")


def load_triage():
    """Load all items from triage list."""
    if not TRIAGE_FILE.exists():
        return []
    items = []
    with open(TRIAGE_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items


def save_triage(items):
    """Save items back to triage list."""
    with open(TRIAGE_FILE, 'w') as f:
        for item in items:
            f.write(json.dumps(item) + '\n')


def list_triage():
    """Display all triage items in a review-friendly format."""
    items = load_triage()
    
    if not items:
        print("Triage list is empty.")
        print("\nTo add ideas to triage, use @Idea Lab and choose 'Add to triage'.")
        return
    
    print(f"=== IDEA TRIAGE REVIEW ({len(items)} items) ===\n")
    
    for i, item in enumerate(items, 1):
        created = item.get('promoted_at', item.get('created_at', 'unknown'))[:10]
        tags = ', '.join(item.get('tags', [])) or 'none'
        
        print(f"[{i}] {item.get('title', 'Untitled')}")
        print(f"    ID: {item.get('id', 'no-id')}")
        print(f"    Added: {created} | Tags: {tags}")
        if item.get('body'):
            body_preview = item['body'][:100] + '...' if len(item.get('body', '')) > 100 else item.get('body', '')
            print(f"    Preview: {body_preview}")
        print()
    
    print("Actions:")
    print("  - Keep: No action needed")
    print("  - Delete: python3 N5/scripts/review_triage.py delete <id>")
    print("  - Promote: python3 N5/scripts/review_triage.py promote <id>")


def delete_item(idea_id):
    """Remove an item from the triage list."""
    items = load_triage()
    original_count = len(items)
    
    items = [item for item in items if item.get('id') != idea_id]
    
    if len(items) == original_count:
        print(f"Error: ID '{idea_id}' not found in triage.")
        return False
    
    save_triage(items)
    print(f"✓ Removed '{idea_id}' from triage.")
    print(f"  Remaining items: {len(items)}")
    return True


def promote_item(idea_id):
    """Promote an item from triage to the lab (start session)."""
    items = load_triage()
    
    # Find the item
    target = None
    for item in items:
        if item.get('id') == idea_id:
            target = item
            break
    
    if not target:
        print(f"Error: ID '{idea_id}' not found in triage.")
        return False
    
    # Call start_lab_session.py with --from-triage flag
    print(f"Promoting '{target.get('title', 'Untitled')}' to Lab...")
    result = subprocess.run(
        ['python3', str(START_SESSION_SCRIPT), '--from-triage', idea_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
        # Remove from triage after successful promotion
        items = [item for item in items if item.get('id') != idea_id]
        save_triage(items)
        print(f"✓ Removed from triage (now in active exploration).")
        return True
    else:
        print(f"Error promoting: {result.stderr}")
        return False


def show_stats():
    """Show triage statistics."""
    items = load_triage()
    
    if not items:
        print("Triage is empty.")
        return
    
    # Age analysis
    now = datetime.now()
    ages = []
    for item in items:
        try:
            created = datetime.fromisoformat(item.get('promoted_at', item.get('created_at', '')).replace('Z', '+00:00'))
            age = (now - created.replace(tzinfo=None)).days
            ages.append(age)
        except:
            pass
    
    # Tag frequency
    tag_counts = {}
    for item in items:
        for tag in item.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print(f"=== TRIAGE STATS ===")
    print(f"Total items: {len(items)}")
    if ages:
        print(f"Oldest: {max(ages)} days | Newest: {min(ages)} days | Avg: {sum(ages)//len(ages)} days")
    if tag_counts:
        print(f"Top tags: {', '.join(sorted(tag_counts.keys(), key=lambda k: -tag_counts[k])[:5])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage idea triage list")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    subparsers.add_parser('list', help='Show all triage items')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Remove item from triage')
    delete_parser.add_argument('id', help='UUID of item to delete')
    
    # Promote command
    promote_parser = subparsers.add_parser('promote', help='Move item to lab')
    promote_parser.add_argument('id', help='UUID of item to promote')
    
    # Stats command
    subparsers.add_parser('stats', help='Show triage statistics')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_triage()
    elif args.command == 'delete':
        delete_item(args.id)
    elif args.command == 'promote':
        promote_item(args.id)
    elif args.command == 'stats':
        show_stats()
    else:
        parser.print_help()


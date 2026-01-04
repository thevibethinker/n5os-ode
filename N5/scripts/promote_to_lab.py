#!/usr/bin/env python3
"""
promote_to_lab.py - Adds an idea to the triage list for later exploration.

LAZY FOLDER CREATION: This script does NOT create exploration folders.
Folders are created on-demand by start_lab_session.py when V actually
starts exploring.

Usage:
  python3 promote_to_lab.py <idea_id>
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

IDEAS_LIST = Path("/home/workspace/Lists/ideas.jsonl")
TRIAGE_LIST = Path("/home/workspace/Lists/idea-triage.jsonl")

def find_idea(idea_id: str) -> dict | None:
    """Find idea by ID in ideas.jsonl."""
    if not IDEAS_LIST.exists():
        return None
    for line in IDEAS_LIST.read_text().strip().split('\n'):
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get('id') == idea_id:
            return obj
    return None

def add_to_triage(idea: dict):
    """Add idea to triage list."""
    triage_entry = {
        "id": idea.get("id"),
        "title": idea.get("title"),
        "body": idea.get("body", ""),
        "tags": idea.get("tags", []),
        "priority": idea.get("priority", "medium"),
        "added_to_triage": datetime.now().isoformat(),
        "status": "pending"
    }
    
    with open(TRIAGE_LIST, 'a') as f:
        f.write(json.dumps(triage_entry) + '\n')
    
    return triage_entry

def promote_idea(idea_id: str):
    """Add idea to triage list (no folder creation)."""
    idea = find_idea(idea_id)
    if not idea:
        print(f"Error: Idea ID {idea_id} not found.")
        return
    
    entry = add_to_triage(idea)
    print(f"✓ Added to triage: {entry['title']}")
    print(f"  ID: {entry['id']}")
    print(f"  Status: pending")
    print(f"  To start exploring: python3 N5/scripts/start_lab_session.py --from-triage {idea_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("idea_id", help="The UUID of the idea to promote to triage")
    args = parser.parse_args()
    promote_idea(args.idea_id)




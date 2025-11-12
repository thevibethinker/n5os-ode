#!/usr/bin/env python3
"""
Meeting Registry Manager

Schema-validated operations for meeting_gdrive_registry.jsonl.
Prevents duplicate entries and validates against schema.

Usage:
    # Add entry
    python3 meeting_registry_manager.py add \
        --gdrive-id <id> \
        --meeting-id <id> \
        [--source <source>] \
        [--converted] \
        [--conversion-method <method>]
    
    # Check if exists
    python3 meeting_registry_manager.py check --gdrive-id <id>
    
    # List all entries
    python3 meeting_registry_manager.py list
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
SCHEMA_PATH = Path("/home/workspace/N5/schemas/meeting_gdrive_registry.schema.json")


def load_schema() -> Dict:
    """Load validation schema."""
    if SCHEMA_PATH.exists():
        return json.loads(SCHEMA_PATH.read_text())
    return {}


def validate_entry(entry: Dict, schema: Dict) -> bool:
    """
    Basic schema validation.
    For full validation, use jsonschema library.
    """
    required = schema.get("required", [])
    for field in required:
        if field not in entry:
            print(f"Validation error: Missing required field '{field}'", file=sys.stderr)
            return False
    return True


def load_registry() -> List[Dict]:
    """Load all registry entries."""
    if not REGISTRY_PATH.exists():
        return []
    
    entries = []
    with open(REGISTRY_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def check_exists(gdrive_id: str) -> bool:
    """Check if gdrive_id already in registry."""
    entries = load_registry()
    return any(e.get("gdrive_id") == gdrive_id for e in entries)


def add_entry(
    gdrive_id: str,
    meeting_id: str,
    source: str = "manual",
    converted: bool = False,
    conversion_method: Optional[str] = None
) -> bool:
    """
    Add new entry to registry with validation.
    Returns True if added, False if duplicate/error.
    """
    # Check duplicate
    if check_exists(gdrive_id):
        print(f"Entry already exists: {gdrive_id}", file=sys.stderr)
        return False
    
    # Build entry
    entry = {
        "gdrive_id": gdrive_id,
        "meeting_id": meeting_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": source
    }
    
    if converted:
        entry["converted"] = True
        if conversion_method:
            entry["conversion_method"] = conversion_method
    
    # Validate
    schema = load_schema()
    if schema and not validate_entry(entry, schema):
        return False
    
    # Append
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Added: {meeting_id} ({gdrive_id})")
    return True


def list_entries(limit: int = None):
    """List registry entries."""
    entries = load_registry()
    
    if limit:
        entries = entries[-limit:]
    
    print(f"Registry: {len(entries)} total entries\n")
    
    for entry in entries:
        print(f"• {entry.get('meeting_id', 'N/A')}")
        print(f"  Drive ID: {entry.get('gdrive_id', 'N/A')}")
        print(f"  Timestamp: {entry.get('ts', 'N/A')}")
        if entry.get("converted"):
            print(f"  Converted: {entry.get('conversion_method', 'unknown')}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Meeting Registry Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add entry")
    add_parser.add_argument("--gdrive-id", required=True)
    add_parser.add_argument("--meeting-id", required=True)
    add_parser.add_argument("--source", default="manual")
    add_parser.add_argument("--converted", action="store_true")
    add_parser.add_argument("--conversion-method")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if exists")
    check_parser.add_argument("--gdrive-id", required=True)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--limit", type=int)
    
    args = parser.parse_args()
    
    if args.command == "add":
        success = add_entry(
            args.gdrive_id,
            args.meeting_id,
            args.source,
            args.converted,
            args.conversion_method
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        exists = check_exists(args.gdrive_id)
        print(f"{'EXISTS' if exists else 'NOT FOUND'}: {args.gdrive_id}")
        sys.exit(0 if exists else 1)
    
    elif args.command == "list":
        list_entries(args.limit)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

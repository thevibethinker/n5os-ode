#!/usr/bin/env python3
"""
Meeting Google Drive Registry Manager
Manages the registry of meetings ingested from Google Drive
"""

import argparse
import json
import sys
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
TRANSACTION_LOG = Path("/home/workspace/N5/data/meeting_registry_txlog.jsonl")
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


def check_gdrive_id(registry_file: Path, gdrive_id: str) -> bool:
    """Check if a gdrive_id already exists in the registry"""
    if not registry_file.exists():
        return False
    
    with open(registry_file, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry.get('gdrive_id') == gdrive_id:
                return True
    return False


def log_transaction(action: str, data: Dict, result: str):
    """Log transaction for audit trail."""
    tx = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "data": data,
        "result": result
    }
    TRANSACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TRANSACTION_LOG, "a") as f:
        f.write(json.dumps(tx) + "\n")


def atomic_append(entry: Dict) -> bool:
    """Atomically append entry to registry using temp file."""
    try:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=REGISTRY_PATH.parent,
            prefix=".registry_temp_"
        )
        
        # Copy existing + new entry
        lines = []
        if REGISTRY_PATH.exists():
            lines = REGISTRY_PATH.read_text().splitlines()
        lines.append(json.dumps(entry))
        
        # Write atomically
        os.write(temp_fd, "\n".join(lines).encode() + b"\n")
        os.fsync(temp_fd)
        os.close(temp_fd)
        
        # Atomic rename
        os.rename(temp_path, REGISTRY_PATH)
        return True
    except Exception as e:
        print(f"✗ Atomic write failed: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return False


def add_entry(args):
    """Add entry with duplicate prevention and transaction logging."""
    # Check for duplicates FIRST
    if check_gdrive_id(REGISTRY_PATH, args.gdrive_id):
        print(f"⚠️  Duplicate: {args.gdrive_id} already exists in registry")
        log_transaction("add", {"gdrive_id": args.gdrive_id}, "duplicate_prevented")
        sys.exit(2)
    
    entry = {
        "gdrive_id": args.gdrive_id,
        "meeting_id": args.meeting_id,
        "ts": args.ts or datetime.now(timezone.utc).isoformat()
    }
    
    if args.folder_name:
        entry["folder_name"] = args.folder_name
    if args.source:
        entry["source"] = args.source
    if args.converted is not None:
        entry["converted"] = args.converted
    if args.conversion_method:
        entry["conversion_method"] = args.conversion_method
    
    # Validate against schema
    schema = load_schema()
    if schema and not validate_entry(entry, schema):
        log_transaction("add", entry, "validation_failed")
        return False
    
    # Atomic write
    success = atomic_append(entry)
    
    if success:
        print(f"✓ Added: {args.meeting_id} ({args.gdrive_id})")
        log_transaction("add", entry, "success")
    else:
        print(f"✗ Failed to add: {args.meeting_id}")
        log_transaction("add", entry, "write_failed")
    
    return success


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
    parser = argparse.ArgumentParser(description="Manage meeting Google Drive registry")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new registry entry')
    add_parser.add_argument('--gdrive-id', required=True, help='Google Drive file ID')
    add_parser.add_argument('--meeting-id', required=True, help='Meeting identifier')
    add_parser.add_argument('--ts', help='Timestamp (ISO 8601)')
    add_parser.add_argument('--folder-name', help='Folder name in Personal/Meetings/')
    add_parser.add_argument('--source', help='Ingestion source/method')
    add_parser.add_argument('--converted', action='store_true', help='File was converted')
    add_parser.add_argument('--conversion-method', choices=['pandoc', 'manual', 'other'], help='Conversion method')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if gdrive_id exists')
    check_parser.add_argument('--gdrive-id', required=True, help='Google Drive file ID to check')
    
    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--limit", type=int)
    
    args = parser.parse_args()
    
    if args.command == "add":
        success = add_entry(args)
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        registry_file = Path('/home/workspace/N5/data/meeting_gdrive_registry.jsonl')
        if check_gdrive_id(registry_file, args.gdrive_id):
            print(f"✓ Found: {args.gdrive_id} already in registry")
            sys.exit(0)
        else:
            print(f"✗ Not found: {args.gdrive_id} not in registry")
            sys.exit(1)
    
    elif args.command == "list":
        list_entries(args.limit)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()




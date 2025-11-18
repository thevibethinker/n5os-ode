#!/usr/bin/env python3
"""
Meeting Metadata Manager with Google ID Tracking
Bulletproof tracking system using immutable Google identifiers
"""

import json
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
SCHEMA_PATH = Path("/home/workspace/N5/schemas/meeting_metadata.schema.json")


def create_metadata(
    folder_name: str,
    drive_file_id: str,
    drive_file_name: str,
    calendar_event_id: Optional[str] = None,
    source: str = "fireflies",
    converted_from: str = "docx",
    file_size_bytes: int = 0
) -> Dict:
    """Create metadata with Google IDs for tracking."""
    
    metadata = {
        "folder_name": folder_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "google_identifiers": {
            "drive_file_id": drive_file_id,
            "drive_file_name": drive_file_name
        },
        "processing_status": "ingested",
        "transcript": {
            "source": source,
            "file_size_bytes": file_size_bytes,
            "converted_from": converted_from
        },
        "participants": [],
        "smart_blocks_generated": [],
        "verification": {
            "registry_entry_exists": False
        }
    }
    
    # Add calendar event ID if provided
    if calendar_event_id:
        metadata["google_identifiers"]["calendar_event_id"] = calendar_event_id
    
    return metadata


def write_metadata(meeting_folder: Path, metadata: Dict) -> bool:
    """Write metadata.json to meeting folder."""
    try:
        metadata_path = meeting_folder / "_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        return True
    except Exception as e:
        print(f"✗ Failed to write metadata: {e}", file=sys.stderr)
        return False


def read_metadata(meeting_folder: Path) -> Optional[Dict]:
    """Read metadata from meeting folder."""
    metadata_path = meeting_folder / "_metadata.json"
    if not metadata_path.exists():
        return None
    
    try:
        return json.loads(metadata_path.read_text())
    except Exception as e:
        print(f"✗ Failed to read metadata: {e}", file=sys.stderr)
        return None


def verify_google_ids(meeting_folder: Path) -> Dict:
    """
    Verify meeting using Google IDs triangulation.
    Returns status dict with verification results.
    """
    metadata = read_metadata(meeting_folder)
    if not metadata:
        return {"status": "error", "reason": "no_metadata"}
    
    google_ids = metadata.get("google_identifiers", {})
    drive_id = google_ids.get("drive_file_id")
    
    if not drive_id:
        return {"status": "error", "reason": "missing_drive_id"}
    
    # Check if Drive ID exists in registry
    registry_found = False
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("gdrive_id") == drive_id:
                    registry_found = True
                    break
    
    # Check transcript integrity
    transcript_path = meeting_folder / "transcript.md"
    transcript_valid = transcript_path.exists() and transcript_path.stat().st_size > 100
    
    verification = {
        "status": "valid" if (registry_found and transcript_valid) else "incomplete",
        "drive_id": drive_id,
        "registry_found": registry_found,
        "transcript_valid": transcript_valid,
        "folder_name": metadata.get("folder_name")
    }
    
    return verification


def find_folder_by_drive_id(drive_file_id: str) -> Optional[Path]:
    """Find meeting folder by Google Drive file ID."""
    for folder in MEETINGS_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        
        metadata = read_metadata(folder)
        if metadata:
            google_ids = metadata.get("google_identifiers", {})
            if google_ids.get("drive_file_id") == drive_file_id:
                return folder
    
    return None


def scan_all_meetings() -> Dict:
    """Scan all meetings and verify Google ID tracking."""
    results = {
        "total": 0,
        "with_metadata": 0,
        "with_drive_id": 0,
        "with_calendar_id": 0,
        "verified": 0,
        "missing_metadata": [],
        "missing_drive_id": [],
        "invalid": []
    }
    
    for folder in MEETINGS_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith('.') or folder.name == 'Inbox':
            continue
        
        results["total"] += 1
        
        metadata = read_metadata(folder)
        if not metadata:
            results["missing_metadata"].append(folder.name)
            continue
        
        results["with_metadata"] += 1
        
        google_ids = metadata.get("google_identifiers", {})
        if google_ids.get("drive_file_id"):
            results["with_drive_id"] += 1
        else:
            results["missing_drive_id"].append(folder.name)
        
        if google_ids.get("calendar_event_id"):
            results["with_calendar_id"] += 1
        
        # Verify
        verification = verify_google_ids(folder)
        if verification["status"] == "valid":
            results["verified"] += 1
        else:
            results["invalid"].append({
                "folder": folder.name,
                "reason": verification.get("reason", "incomplete")
            })
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeting Metadata Manager with Google ID Tracking")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create metadata for meeting')
    create_parser.add_argument('--folder', required=True, help='Meeting folder name')
    create_parser.add_argument('--drive-id', required=True, help='Google Drive file ID')
    create_parser.add_argument('--drive-name', required=True, help='Original Drive filename')
    create_parser.add_argument('--calendar-id', help='Google Calendar event ID (optional)')
    create_parser.add_argument('--source', default='fireflies', help='Transcript source')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify meeting by Drive ID')
    verify_parser.add_argument('--drive-id', required=True, help='Google Drive file ID')
    
    # Scan command
    subparsers.add_parser('scan', help='Scan all meetings for Google ID tracking status')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        folder_path = MEETINGS_DIR / args.folder
        if not folder_path.exists():
            print(f"✗ Folder does not exist: {args.folder}")
            sys.exit(1)
        
        metadata = create_metadata(
            folder_name=args.folder,
            drive_file_id=args.drive_id,
            drive_file_name=args.drive_name,
            calendar_event_id=args.calendar_id,
            source=args.source
        )
        
        if write_metadata(folder_path, metadata):
            print(f"✓ Created metadata for {args.folder}")
            print(f"  Drive ID: {args.drive_id}")
            if args.calendar_id:
                print(f"  Calendar ID: {args.calendar_id}")
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'verify':
        folder = find_folder_by_drive_id(args.drive_id)
        if folder:
            verification = verify_google_ids(folder)
            print(f"✓ Found: {folder.name}")
            print(f"  Status: {verification['status']}")
            print(f"  Registry: {'✓' if verification['registry_found'] else '✗'}")
            print(f"  Transcript: {'✓' if verification['transcript_valid'] else '✗'}")
            sys.exit(0 if verification['status'] == 'valid' else 1)
        else:
            print(f"✗ No folder found with Drive ID: {args.drive_id}")
            sys.exit(1)
    
    elif args.command == 'scan':
        results = scan_all_meetings()
        print("=" * 80)
        print("GOOGLE ID TRACKING STATUS")
        print("=" * 80)
        print(f"Total meetings: {results['total']}")
        print(f"With metadata: {results['with_metadata']}")
        print(f"With Drive ID: {results['with_drive_id']}")
        print(f"With Calendar ID: {results['with_calendar_id']}")
        print(f"Fully verified: {results['verified']}")
        print()
        
        if results['missing_metadata']:
            print(f"⚠️  Missing metadata ({len(results['missing_metadata'])}):")
            for name in results['missing_metadata'][:10]:
                print(f"  - {name}")
            if len(results['missing_metadata']) > 10:
                print(f"  ... and {len(results['missing_metadata']) - 10} more")
        
        if results['missing_drive_id']:
            print(f"\n⚠️  Missing Drive ID ({len(results['missing_drive_id'])}):")
            for name in results['missing_drive_id'][:10]:
                print(f"  - {name}")
        
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()


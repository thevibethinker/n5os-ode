#!/usr/bin/env python3
"""
Cleanup placeholder meetings from the system.

Purpose: Remove the 9 identified meetings with placeholder Smart Blocks,
         clean them from registry, and ensure request files exist for reprocessing.

Usage: python3 cleanup_placeholder_meetings.py [--dry-run]
"""

import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Paths
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_FILE = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
REQUESTS_DIR = Path("/home/workspace/N5/inbox/meeting_requests/processed")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")

# The 9 identified placeholder meetings (hardcoded for safety)
FLUBBED_MEETINGS = [
    "2025-10-29_external-mihir-makwana-x-vrijen",
    "2025-10-29_external-quick-chat-vrijen-attawar",
    "2025-10-29_internal-daily-team-stand-up-02",
    "2025-10-29_internal-daily-team-stand-up-143753",
    "2025-10-29_internal-daily-team-stand-up-143925",
    "2025-10-30_external-dbn-ctum-szz",
    "2025-10-30_external-ikk-nkrd-kgn",
    "2025-10-30_external-ilya",
    "2025-10-30_external-jake-gates",
]


def backup_registry():
    """Create timestamped backup of registry."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"meeting_gdrive_registry_{timestamp}.jsonl"
    
    if REGISTRY_FILE.exists():
        shutil.copy2(REGISTRY_FILE, backup_path)
        print(f"✓ Backed up registry to: {backup_path}")
        return backup_path
    else:
        print("⚠️  Registry file doesn't exist yet")
        return None


def load_registry():
    """Load registry entries."""
    entries = []
    if REGISTRY_FILE.exists():
        for line in REGISTRY_FILE.read_text().splitlines():
            if line.strip():
                entries.append(json.loads(line))
    return entries


def save_registry(entries):
    """Save registry entries back to file."""
    with REGISTRY_FILE.open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def ensure_request_file(meeting_id, meeting_dir):
    """Ensure request file exists for meeting, creating if needed."""
    request_file = REQUESTS_DIR / f"{meeting_id}_request.json"
    
    if request_file.exists():
        print(f"  ✓ Request file exists: {request_file.name}")
        return True
    
    # Try to extract from metadata
    metadata_file = meeting_dir / "_metadata.json"
    if not metadata_file.exists():
        print(f"  ✗ No metadata file, cannot create request")
        return False
    
    try:
        metadata = json.loads(metadata_file.read_text())
        gdrive_id = metadata.get("gdrive_id")
        
        if not gdrive_id:
            print(f"  ✗ No gdrive_id in metadata")
            return False
        
        request_data = {
            "meeting_id": meeting_id,
            "gdrive_id": gdrive_id,
            "gdrive_link": metadata.get("gdrive_link", f"https://drive.google.com/file/d/{gdrive_id}/view"),
            "original_filename": metadata.get("original_filename", ""),
        }
        
        REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
        request_file.write_text(json.dumps(request_data, indent=2) + "\n")
        print(f"  ✓ Created request file: {request_file.name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error creating request: {e}")
        return False


def cleanup_meeting(meeting_id, dry_run=False):
    """Clean up a single placeholder meeting."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {meeting_id}")
    
    meeting_dir = MEETINGS_DIR / meeting_id
    
    if not meeting_dir.exists():
        print(f"  ⚠️  Meeting folder doesn't exist")
        return False
    
    # 1. Ensure request file exists
    ensure_request_file(meeting_id, meeting_dir)
    
    # 2. Delete Smart Block files
    b_files = list(meeting_dir.glob("B*.md"))
    if not dry_run:
        for b_file in b_files:
            b_file.unlink()
        print(f"  ✓ Deleted {len(b_files)} Smart Block files")
    else:
        print(f"  Would delete {len(b_files)} Smart Block files")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Cleanup placeholder meetings")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Meeting Placeholder Cleanup")
    print("=" * 60)
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No changes will be made\n")
    
    # Step 1: Backup registry
    backup_path = backup_registry()
    
    # Step 2: Load registry
    print(f"\n📋 Loading registry...")
    registry_entries = load_registry()
    print(f"   Current entries: {len(registry_entries)}")
    
    # Step 3: Cleanup each meeting
    print(f"\n🧹 Cleaning up {len(FLUBBED_MEETINGS)} placeholder meetings...")
    
    cleaned_count = 0
    request_count = 0
    
    for meeting_id in FLUBBED_MEETINGS:
        if cleanup_meeting(meeting_id, dry_run=args.dry_run):
            cleaned_count += 1
            
            # Check if request exists
            request_file = REQUESTS_DIR / f"{meeting_id}_request.json"
            if request_file.exists():
                request_count += 1
    
    # Step 4: Remove from registry
    print(f"\n📝 Removing from registry...")
    original_count = len(registry_entries)
    
    if not args.dry_run:
        # Filter out the flubbed meetings
        cleaned_registry = [
            entry for entry in registry_entries
            if entry.get("meeting_id") not in FLUBBED_MEETINGS
        ]
        
        removed_count = original_count - len(cleaned_registry)
        save_registry(cleaned_registry)
        print(f"   Removed {removed_count} entries")
        print(f"   Registry now has {len(cleaned_registry)} entries")
    else:
        would_remove = sum(1 for e in registry_entries if e.get("meeting_id") in FLUBBED_MEETINGS)
        print(f"   Would remove {would_remove} entries")
        print(f"   Registry would have {original_count - would_remove} entries")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"   Cleaned meetings: {cleaned_count}/{len(FLUBBED_MEETINGS)}")
    print(f"   Request files ready: {request_count}/{len(FLUBBED_MEETINGS)}")
    if backup_path:
        print(f"   Registry backup: {backup_path}")
    print(f"={'=' * 60}")
    
    if not args.dry_run:
        print(f"\n✅ Cleanup complete!")
        print(f"   Next: Process {request_count} meetings with fixed consumer task")
    else:
        print(f"\n🧪 Dry run complete. Run without --dry-run to execute.")


if __name__ == "__main__":
    main()

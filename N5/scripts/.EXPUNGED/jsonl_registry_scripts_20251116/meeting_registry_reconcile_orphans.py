#!/usr/bin/env python3
"""
Reconcile orphaned meeting folders by adding synthetic registry entries
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")

def load_registry():
    """Load all folder names from registry."""
    if not REGISTRY_PATH.exists():
        return set()
    
    folders = set()
    with open(REGISTRY_PATH) as f:
        for line in f:
            entry = json.loads(line.strip())
            if "folder_name" in entry:
                folders.add(entry["folder_name"])
            if "meeting_id" in entry:
                folders.add(entry["meeting_id"])
    return folders

def is_valid_meeting_folder(folder: Path) -> bool:
    """Check if folder is a valid meeting (has transcript or processed marker)."""
    if not folder.is_dir():
        return False
    
    # Skip special directories
    if folder.name.startswith('.') or folder.name in ['Inbox', '_ARCHIVE_2024']:
        return False
    
    # Check for transcript or .processed marker
    has_transcript = (folder / "transcript.md").exists()
    has_processed = (folder / ".processed").exists()
    has_blocks = len(list(folder.glob("B*.md"))) > 0
    
    return has_transcript or has_processed or has_blocks

def get_orphaned_folders():
    """Find folders not in registry."""
    registry_folders = load_registry()
    orphans = []
    
    for folder in MEETINGS_DIR.iterdir():
        if is_valid_meeting_folder(folder):
            if folder.name not in registry_folders:
                orphans.append(folder)
    
    return orphans

def add_synthetic_entry(folder: Path, dry_run=False):
    """Add synthetic registry entry for orphaned folder."""
    synthetic_id = f"manual-{folder.name}"
    
    cmd = [
        "python3",
        "/home/workspace/N5/scripts/meeting_registry_manager.py",
        "add",
        "--gdrive-id", synthetic_id,
        "--meeting-id", folder.name,
        "--folder-name", folder.name,
        "--source", "reconciliation",
        "--converted"
    ]
    
    if dry_run:
        print(f"  Would run: {' '.join(cmd)}")
        return True
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("=" * 80)
    print("ORPHAN RECONCILIATION")
    print("=" * 80)
    print()
    
    orphans = get_orphaned_folders()
    
    print(f"Found {len(orphans)} orphaned folders")
    print()
    
    if len(orphans) == 0:
        print("✓ No orphans to reconcile")
        return
    
    print("Orphaned folders:")
    for folder in orphans[:10]:
        print(f"  - {folder.name}")
    if len(orphans) > 10:
        print(f"  ... and {len(orphans) - 10} more")
    print()
    
    # Dry run first
    print("DRY RUN (no changes):")
    print("-" * 80)
    for folder in orphans[:5]:
        print(f"• {folder.name}")
        add_synthetic_entry(folder, dry_run=True)
    print()
    
    response = input(f"Add synthetic entries for {len(orphans)} folders? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    print()
    print("Adding synthetic entries...")
    print("-" * 80)
    
    success_count = 0
    for folder in orphans:
        if add_synthetic_entry(folder):
            print(f"✓ {folder.name}")
            success_count += 1
        else:
            print(f"✗ {folder.name} (failed)")
    
    print()
    print("=" * 80)
    print(f"COMPLETE: {success_count}/{len(orphans)} entries added")
    print("=" * 80)

if __name__ == "__main__":
    main()


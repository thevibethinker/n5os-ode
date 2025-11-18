#!/usr/bin/env python3
"""
Meeting Registry Reconciliation Tool
Reconciles existing meeting folders with Drive IDs and registry entries
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
RECONCILE_LOG = Path("/home/workspace/N5/logs/registry_reconcile.log")


def load_registry() -> Dict[str, Dict]:
    """Load registry into memory indexed by folder_name and gdrive_id."""
    by_folder = {}
    by_gdrive_id = {}
    
    if not REGISTRY_PATH.exists():
        return {"by_folder": by_folder, "by_gdrive_id": by_gdrive_id}
    
    with open(REGISTRY_PATH, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                folder = entry.get("folder_name") or entry.get("meeting_id")
                if folder:
                    by_folder[folder] = entry
                gdrive_id = entry.get("gdrive_id")
                if gdrive_id:
                    by_gdrive_id[gdrive_id] = entry
    
    return {"by_folder": by_folder, "by_gdrive_id": by_gdrive_id}


def scan_meeting_folders() -> Set[str]:
    """Scan Personal/Meetings for all folder names."""
    folders = set()
    
    if not MEETINGS_DIR.exists():
        return folders
    
    for item in MEETINGS_DIR.iterdir():
        if item.is_dir() and item.name not in ['.stfolder', 'Inbox', '_ARCHIVE_2024']:
            folders.add(item.name)
    
    return folders


def find_orphaned_folders(registry: Dict, folders: Set[str]) -> List[str]:
    """Find folders that exist but aren't in registry."""
    registered_folders = set(registry["by_folder"].keys())
    orphaned = folders - registered_folders
    return sorted(list(orphaned))


def find_orphaned_registry(registry: Dict, folders: Set[str]) -> List[Dict]:
    """Find registry entries without corresponding folders."""
    orphaned = []
    
    for folder_name, entry in registry["by_folder"].items():
        if folder_name not in folders:
            orphaned.append(entry)
    
    return orphaned


def find_duplicates(registry: Dict) -> Dict[str, List]:
    """Find duplicate entries (same folder or same gdrive_id appearing multiple times)."""
    folder_counts = {}
    gdrive_counts = {}
    
    with open(REGISTRY_PATH, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                folder = entry.get("folder_name") or entry.get("meeting_id")
                if folder:
                    folder_counts[folder] = folder_counts.get(folder, 0) + 1
                
                gdrive_id = entry.get("gdrive_id")
                if gdrive_id and not gdrive_id.startswith("manual-"):
                    gdrive_counts[gdrive_id] = gdrive_counts.get(gdrive_id, 0) + 1
    
    duplicates = {
        "folders": {k: v for k, v in folder_counts.items() if v > 1},
        "gdrive_ids": {k: v for k, v in gdrive_counts.items() if v > 1}
    }
    
    return duplicates


def generate_report():
    """Generate comprehensive reconciliation report."""
    print("=" * 80)
    print("MEETING REGISTRY RECONCILIATION REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # Load data
    registry = load_registry()
    folders = scan_meeting_folders()
    
    print(f"📊 Summary:")
    print(f"   Registry entries: {len(registry['by_folder'])}")
    print(f"   Meeting folders: {len(folders)}")
    print(f"   Drive IDs tracked: {len(registry['by_gdrive_id'])}")
    print()
    
    # Find orphaned folders
    orphaned_folders = find_orphaned_folders(registry, folders)
    if orphaned_folders:
        print(f"⚠️  Orphaned Folders ({len(orphaned_folders)}):")
        print("   (Folders exist but not in registry)")
        for folder in orphaned_folders[:10]:
            print(f"   - {folder}")
        if len(orphaned_folders) > 10:
            print(f"   ... and {len(orphaned_folders) - 10} more")
        print()
    
    # Find orphaned registry entries
    orphaned_registry = find_orphaned_registry(registry, folders)
    if orphaned_registry:
        print(f"⚠️  Orphaned Registry Entries ({len(orphaned_registry)}):")
        print("   (Registry entries without folders)")
        for entry in orphaned_registry[:10]:
            folder = entry.get("folder_name") or entry.get("meeting_id")
            print(f"   - {folder}")
        if len(orphaned_registry) > 10:
            print(f"   ... and {len(orphaned_registry) - 10} more")
        print()
    
    # Find duplicates
    duplicates = find_duplicates(registry)
    if duplicates["folders"] or duplicates["gdrive_ids"]:
        print(f"🔴 Duplicates Found:")
        if duplicates["folders"]:
            print(f"   Duplicate folders: {len(duplicates['folders'])}")
            for folder, count in list(duplicates["folders"].items())[:5]:
                print(f"   - {folder} (appears {count} times)")
        if duplicates["gdrive_ids"]:
            print(f"   Duplicate Drive IDs: {len(duplicates['gdrive_ids'])}")
            for gdrive_id, count in list(duplicates["gdrive_ids"].items())[:5]:
                print(f"   - {gdrive_id} (appears {count} times)")
        print()
    
    # Health score
    total_issues = len(orphaned_folders) + len(orphaned_registry) + len(duplicates["folders"]) + len(duplicates["gdrive_ids"])
    
    if total_issues == 0:
        print("✅ HEALTHY: No issues found!")
    elif total_issues < 10:
        print(f"🟡 MINOR ISSUES: {total_issues} issues found")
    else:
        print(f"🔴 ATTENTION NEEDED: {total_issues} issues found")
    
    print()
    print("=" * 80)
    
    return total_issues


def main():
    """Run reconciliation report."""
    issues = generate_report()
    sys.exit(1 if issues > 0 else 0)


if __name__ == "__main__":
    main()


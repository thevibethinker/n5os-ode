#!/usr/bin/env python3
"""
Meeting Ingestion - Archive Script

Moves completed meetings from Inbox to weekly folders with internal/external routing.

Usage:
    python3 archive.py [--dry-run] [--execute]
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS = Path("/home/workspace/Personal/Meetings")


def get_week_folder(date_str: str) -> str:
    """Get Week-of-YYYY-MM-DD folder name (Monday of that week)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        monday = date - timedelta(days=date.weekday())
        return f"Week-of-{monday.strftime('%Y-%m-%d')}"
    except:
        return "Week-of-Unknown"


def clean_folder_name(name: str) -> str:
    """Clean a meeting folder name for archival."""
    for suffix in ["_[P]", "_[M]", "_[B]", "_[C]", "_[R]"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    name = name.replace("_", "-")
    name = "-".join(part for part in name.split("-") if part)
    
    return name


def find_complete_meetings() -> list[dict]:
    """Find all meetings with status=processed in Inbox (ready for archival)."""
    complete = []
    
    if not INBOX.exists():
        return complete
    
    for folder in INBOX.iterdir():
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue
        
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue
        
        try:
            manifest = json.loads(manifest_path.read_text())
            
            # Support both v3 manifests and legacy manifests
            if manifest.get("status") == "processed":
                # v3 manifest structure
                meeting_type = manifest.get("meeting", {}).get("type", "external")
                date = manifest.get("meeting", {}).get("date", "unknown")
            elif manifest.get("status") == "complete":
                # Legacy manifest structure
                meeting_type = manifest.get("meeting_type", "external")
                date = manifest.get("date", manifest.get("meeting_date", "unknown"))
            else:
                # Not ready for archival
                continue
            
            complete.append({
                "path": folder,
                "name": folder.name,
                "date": date,
                "meeting_type": meeting_type,
                "manifest": manifest
            })
        except Exception as e:
            logger.warning(f"Could not read manifest for {folder.name}: {e}")
    
    return complete


def archive_meeting(meeting: dict, dry_run: bool = False) -> dict:
    """Archive a single meeting to its weekly folder with internal/external routing."""
    folder = meeting["path"]
    date_str = meeting["date"]
    meeting_type = meeting["meeting_type"]
    
    week_name = get_week_folder(date_str)
    week_dir = MEETINGS / week_name
    
    # Route to internal/ or external/ subfolder based on meeting_type
    subfolder = "internal" if meeting_type == "internal" else "external"
    type_dir = week_dir / subfolder
    
    clean_name = clean_folder_name(folder.name)
    target_path = type_dir / clean_name
    
    result = {
        "from": str(folder),
        "to": str(target_path),
        "week": week_name,
        "type": meeting_type,
        "subfolder": subfolder
    }
    
    if dry_run:
        result["dry_run"] = True
        logger.info(f"  Would move: {folder.name}")
        logger.info(f"    → {week_name}/{subfolder}/{clean_name}")
        return result
    
    # Create week directory and type subdirectory
    type_dir.mkdir(parents=True, exist_ok=True)
    
    if target_path.exists():
        logger.info(f"  Target exists, merging: {target_path.name}")
        merged = 0
        for item in folder.iterdir():
            dest = target_path / item.name
            if not dest.exists():
                if item.is_file():
                    shutil.copy2(str(item), str(dest))
                else:
                    shutil.copytree(str(item), str(dest))
                merged += 1
            elif item.is_file() and dest.is_file():
                if item.stat().st_size > dest.stat().st_size:
                    shutil.copy2(str(item), str(dest))
        
        shutil.rmtree(folder)
        result["merged"] = True
        result["merged_count"] = merged
        logger.info(f"  Merged {merged} items, removed source")
    else:
        shutil.move(str(folder), str(target_path))
        logger.info(f"  Moved to: {target_path}")
    
    # Update manifest status and timestamp
    manifest_path = target_path / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            
            # Handle v3 manifest format
            if manifest.get("$schema") == "manifest-v3":
                manifest["status"] = "archived"
                if "timestamps" not in manifest:
                    manifest["timestamps"] = {}
                manifest["timestamps"]["archived_at"] = datetime.utcnow().isoformat() + "Z"
                
                # Add status history entry
                if "status_history" not in manifest:
                    manifest["status_history"] = []
                manifest["status_history"].append({
                    "status": "archived",
                    "at": datetime.utcnow().isoformat() + "Z"
                })
            else:
                # Legacy format
                manifest["status"] = "archived"
                manifest["archived_at"] = datetime.utcnow().isoformat() + "Z"
            
            manifest_path.write_text(json.dumps(manifest, indent=2))
        except Exception as e:
            logger.warning(f"Could not update manifest for {target_path.name}: {e}")
    
    result["success"] = True
    return result


def archive_all(dry_run: bool = True) -> dict:
    """Archive all complete meetings."""
    print(f"\n{'='*60}")
    print(f"MEETING ARCHIVAL {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*60}\n")
    
    complete = find_complete_meetings()
    
    print(f"Found {len(complete)} meetings ready for archival in Inbox\n")
    
    if not complete:
        return {"archived": 0, "results": []}
    
    by_week_and_type = defaultdict(lambda: defaultdict(list))
    for meeting in complete:
        week = get_week_folder(meeting["date"])
        meeting_type = meeting["meeting_type"]
        by_week_and_type[week][meeting_type].append(meeting)
    
    results = []
    
    for week in sorted(by_week_and_type.keys()):
        week_meetings = by_week_and_type[week]
        total_week_meetings = sum(len(meetings) for meetings in week_meetings.values())
        print(f"--- {week} ({total_week_meetings} meetings) ---")
        
        for meeting_type in sorted(week_meetings.keys()):
            meetings = week_meetings[meeting_type]
            if meetings:
                print(f"  {meeting_type.upper()}: {len(meetings)} meetings")
                
                for meeting in meetings:
                    result = archive_meeting(meeting, dry_run=dry_run)
                    results.append(result)
        
        print()
    
    succeeded = len([r for r in results if r.get("success") or r.get("dry_run")])
    failed = len([r for r in results if not r.get("success") and not r.get("dry_run")])
    
    print(f"{'='*60}")
    print(f"SUMMARY:")
    print(f"  Archived: {succeeded}")
    print(f"  Failed:   {failed}")
    print(f"{'='*60}\n")
    
    return {
        "archived": succeeded,
        "failed": failed,
        "results": results
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive completed meetings")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview without executing (default)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform archival")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    results = archive_all(dry_run=dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
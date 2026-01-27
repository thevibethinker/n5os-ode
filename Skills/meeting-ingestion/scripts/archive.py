#!/usr/bin/env python3
"""
Meeting Ingestion - Archive Script

Archives processed meetings from Inbox to weekly folders.
Replaces Weekly Meeting Organization agent (9b813d5c).

Uses manifest.json status field to determine readiness:
- ready_for_followup, crm_synced, complete: always ready
- intelligence_generated: ready if has FOLLOW_UP_EMAIL.md or marked no follow-up needed
- manifest_generated, mg2_in_progress: not ready (still processing)

Usage:
    python3 archive.py [--dry-run] [--execute]
"""

import json
import logging
import shutil
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Core paths
INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS = Path("/home/workspace/Personal/Meetings")

# Meeting readiness patterns (from manifest.json status)
READY_STATUSES = {
    'ready_for_followup',
    'crm_synced',
    'complete',
    'processed'
}

# Status values that indicate a meeting is still being processed
PROCESSING_STATUSES = {'manifest_generated', 'mg2_in_progress'}

# Status values that need follow-up email checks
NEEDS_FOLLOWUP_CHECK_STATUSES = {'intelligence_generated'}


def get_manifest_status(meeting_dir: Path) -> tuple[str, dict]:
    """
    Read manifest.json and return (status, manifest_data).
    
    Returns:
        Tuple of (status_string, manifest_dict)
        If no manifest exists, returns ('no_manifest', {})
    """
    manifest_path = meeting_dir / "manifest.json"
    if not manifest_path.exists():
        return ('no_manifest', {})
    
    try:
        with open(manifest_path) as f:
            data = json.load(f)
            return (data.get('status', 'unknown'), data)
    except Exception as e:
        logger.warning(f"Failed to read manifest for {meeting_dir.name}: {e}")
        return ('error', {})


def has_follow_up_email(meeting_dir: Path) -> bool:
    """Check if FOLLOW_UP_EMAIL.md exists in meeting folder."""
    return (meeting_dir / "FOLLOW_UP_EMAIL.md").exists()


def is_marked_no_followup(meeting_dir: Path, manifest: dict) -> bool:
    """Check if meeting is explicitly marked as not needing follow-up email."""
    # Check manifest for explicit marking
    system_states = manifest.get('system_states', {})
    followup_state = system_states.get('follow_up_email', {})
    if followup_state.get('status') == 'not_needed':
        return True
    
    # Check meeting_type for internal meetings
    if manifest.get('meeting_type', '').lower() == 'internal':
        return True
    
    return False


def is_ready_for_archival(meeting_dir: Path) -> tuple[bool, str]:
    """
    Check if a meeting folder is ready to be moved to Week-of folder.
    
    A meeting is ready when:
    1. It has a manifest.json
    2. Either:
       a) Status is in READY_STATUSES (fully complete), OR
       b) Status is 'intelligence_generated' AND has FOLLOW_UP_EMAIL.md, OR
       c) Status is 'intelligence_generated' AND marked as not needing follow-up
    
    Returns:
        Tuple of (is_ready: bool, reason: str)
    """
    status, manifest = get_manifest_status(meeting_dir)
    
    if status == 'no_manifest':
        return (False, "no manifest.json - awaiting MG-1")
    
    if status == 'error':
        return (False, "manifest.json parse error")
    
    # Fully processed - always ready
    if status in READY_STATUSES:
        return (True, f"status={status}")
    
    # Intelligence generated - check for follow-up email
    if status in NEEDS_FOLLOWUP_CHECK_STATUSES:
        if has_follow_up_email(meeting_dir):
            return (True, f"status={status} + has FOLLOW_UP_EMAIL.md")
        if is_marked_no_followup(meeting_dir, manifest):
            return (True, f"status={status} + marked no follow-up needed")
        # Not ready - needs MG-5
        return (False, f"status={status} - awaiting MG-5 (no FOLLOW_UP_EMAIL.md)")
    
    if status in PROCESSING_STATUSES:
        return (False, f"status={status} - still processing")
    
    # Unknown status - be conservative
    return (False, f"unknown status={status}")


def get_week_folder_name(date_str: str) -> str:
    """Get week folder name like 'Week-of-2025-12-01' (Monday of that week)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        monday = date - timedelta(days=date.weekday())
        return f"Week-of-{monday.strftime('%Y-%m-%d')}"
    except:
        return "Unknown-Week"


def extract_readable_name(folder_name: str, manifest_path: Path = None) -> str:
    """Extract a clean, readable meeting name."""
    # Try to get title from manifest first
    if manifest_path and manifest_path.exists():
        try:
            with open(manifest_path) as f:
                data = json.load(f)
                if data.get("meeting_title"):
                    title = data["meeting_title"]
                    # Clean title
                    title = title.replace("_", " ").strip()
                    if len(title) > 5:
                        return title[:60]
        except:
            pass
    
    # Extract from folder name
    name = folder_name
    
    # Remove date prefix
    if name.startswith("2025-") or name.startswith("2026-"):
        parts = name.split("_", 1)
        if len(parts) > 1:
            name = parts[1]
    
    # Remove state suffix (legacy)
    for suffix in ["_[P]", "_[M]", "_[C]", "_[B]"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Clean up concatenated emails
    if "_" in name and "com" in name.lower():
        parts = name.split("_")
        if len(parts) > 1:
            first_part = parts[0]
            if len(first_part) > 50 and "com" in first_part.lower():
                cleaned = []
                current = ""
                for char in first_part:
                    current += char
                    if current.endswith("com") or current.endswith("ai") or current.endswith("org"):
                        name_part = current.rstrip("comaiorg")
                        if name_part:
                            cleaned.append(name_part.title())
                        current = ""
                if cleaned:
                    name = "_".join(cleaned[:2])
    
    # Replace underscores with spaces, title case
    name = name.replace("_", " ").strip()
    
    # Clean up common patterns
    name = name.replace("mycareerspancom", "").replace("theapplyai", "")
    name = name.replace("gmailcom", "").replace("  ", " ").strip()
    
    # Title case and limit length
    if name:
        name = " ".join(word.capitalize() for word in name.split())
    
    return name[:60] if name else "Unknown"


def flatten_nested_duplicates(meeting_dir: Path, dry_run: bool = True):
    """Move content from nested duplicate folders up to parent."""
    changes = []
    
    nested_dirs = [d for d in meeting_dir.iterdir() if d.is_dir() and d.name.startswith(("2025-", "2026-"))]
    
    for nested in nested_dirs:
        for item in nested.iterdir():
            if item.is_file():
                target = meeting_dir / item.name
                if not target.exists():
                    changes.append(f"  MOVE: {item.name} → parent")
                    if not dry_run:
                        shutil.move(str(item), str(target))
        
        deep_nested = [d for d in nested.iterdir() if d.is_dir() and d.name.startswith(("2025-", "2026-"))]
        for dn in deep_nested:
            for item in dn.iterdir():
                if item.is_file():
                    target = meeting_dir / item.name
                    if not target.exists():
                        changes.append(f"  MOVE: {dn.name}/{item.name} → parent")
                        if not dry_run:
                            shutil.move(str(item), str(target))
        
        if not dry_run:
            try:
                for dn in deep_nested:
                    if not list(dn.iterdir()):
                        dn.rmdir()
                if not list(nested.iterdir()):
                    nested.rmdir()
            except:
                pass
        else:
            changes.append(f"  DELETE: empty nested folder {nested.name}")
    
    return changes


def scan_completed_meetings(dry_run: bool = False) -> list[dict]:
    """
    Scan Inbox for meetings ready for archival.
    
    Returns:
        List of dicts with meeting info and ready status
    """
    if not INBOX.exists():
        logger.info("Inbox directory does not exist")
        return []
    
    results = []
    
    for item in INBOX.iterdir():
        if not (item.is_dir() and not item.name.startswith((".", "_"))):
            continue
        
        ready, reason = is_ready_for_archival(item)
        
        results.append({
            "folder_name": item.name,
            "path": str(item),
            "ready": ready,
            "reason": reason
        })
    
    return results


def archive_meeting(meeting_dir: Path, target_folder: Path, dry_run: bool = False) -> dict:
    """
    Archive a single meeting to its target week folder.
    
    Args:
        meeting_dir: Source meeting directory
        target_folder: Destination week folder (Path object)
        dry_run: If True, only preview the move
    
    Returns:
        Dict with archive results
    """
    date_str = meeting_dir.name[:10]
    manifest_path = meeting_dir / "manifest.json"
    
    # Clean up nested duplicates first
    nested_changes = flatten_nested_duplicates(meeting_dir, dry_run)
    
    # Extract readable name
    clean_name = extract_readable_name(meeting_dir.name, manifest_path)
    new_name = f"{date_str}_{clean_name.replace(' ', '-')}"
    new_path = target_folder / new_name
    
    result = {
        "from": str(meeting_dir),
        "to": str(new_path),
        "week": target_folder.name,
        "nested_fixes": nested_changes
    }
    
    if dry_run:
        result["dry_run"] = True
        return result
    
    # Ensure target folder exists
    target_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if destination already exists (merge scenario)
        if new_path.exists():
            logger.info(f"Merging {meeting_dir.name} into existing {new_path.name}")
            merged_count = 0
            for item in meeting_dir.iterdir():
                target = new_path / item.name
                if not target.exists():
                    if item.is_file():
                        shutil.copy2(str(item), str(target))
                    else:
                        shutil.copytree(str(item), str(target))
                    merged_count += 1
                else:
                    # Keep larger file if sizes differ
                    if item.is_file() and target.is_file():
                        if item.stat().st_size > target.stat().st_size:
                            shutil.copy2(str(item), str(target))
                            logger.info(f"  Replaced {item.name} (larger file)")
            
            logger.info(f"Removing source folder after merge: {meeting_dir}")
            shutil.rmtree(meeting_dir)
            logger.info(f"  Merged {merged_count} items, source removed")
            result["merged"] = True
        else:
            # Simple move
            shutil.move(str(meeting_dir), str(new_path))
            logger.info(f"Moved {meeting_dir.name} to {new_path}")
            result["merged"] = False
        
        result["success"] = True
        
    except Exception as e:
        error_msg = f"Failed to archive {meeting_dir.name}: {e}"
        logger.error(error_msg)
        result["success"] = False
        result["error"] = str(e)
    
    return result


def main(dry_run: bool = True) -> dict:
    """
    Main archival function.
    
    Args:
        dry_run: If True, only preview changes
    
    Returns:
        Dict with archival results
    """
    print(f"\n{'='*60}")
    print(f"MEETING ARCHIVAL {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*60}\n")
    
    # Scan for completed meetings
    meetings = scan_completed_meetings(dry_run=dry_run)
    
    ready_meetings = [m for m in meetings if m["ready"]]
    skipped_meetings = [m for m in meetings if not m["ready"]]
    
    # Display scan results
    print(f"Scan Results:")
    print(f"  Total meetings in Inbox: {len(meetings)}")
    print(f"  Ready for archival:     {len(ready_meetings)}")
    print(f"  Skipped (processing):  {len(skipped_meetings)}\n")
    
    # Show ready meetings
    if ready_meetings:
        print("Meetings ready for archival:")
        for m in ready_meetings:
            print(f"  ✓ {m['folder_name']} ({m['reason']})")
        print()
    
    # Show skipped meetings
    if skipped_meetings:
        print("Skipped (still processing):")
        for m in skipped_meetings:
            print(f"  ⏳ {m['folder_name']} ({m['reason']})")
        print()
    
    if not ready_meetings:
        print("No meetings ready for archival.")
        return {
            "total_scanned": len(meetings),
            "archived": 0,
            "skipped": len(skipped_meetings),
            "results": []
        }
    
    # Group ready meetings by week
    by_week = defaultdict(list)
    for meeting_info in ready_meetings:
        meeting_dir = Path(meeting_info["path"])
        date_str = meeting_dir.name[:10]
        week_name = get_week_folder_name(date_str)
        by_week[week_name].append(meeting_dir)
    
    # Archive each meeting
    results = []
    for week_name in sorted(by_week.keys()):
        week_dir = MEETINGS / week_name
        
        print(f"--- {week_name} ({len(by_week[week_name])} meetings) ---")
        
        if not dry_run:
            week_dir.mkdir(parents=True, exist_ok=True)
        else:
            if not week_dir.exists():
                print(f"  CREATE FOLDER: {week_name}")
        
        for meeting_dir in by_week[week_name]:
            print(f"\n  {meeting_dir.name}")
            result = archive_meeting(meeting_dir, week_dir, dry_run=dry_run)
            print(f"    → {week_name}/{Path(result['to']).name}")
            
            if result.get("nested_fixes"):
                print(f"    Nested fixes:")
                for fix in result["nested_fixes"]:
                    print(f"      {fix}")
            
            results.append(result)
    
    # Summary
    successful = len([r for r in results if r.get("success", False)])
    failed = len([r for r in results if not r.get("success", True)])
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Total scanned:  {len(meetings)}")
    print(f"  Archived:       {successful}")
    print(f"  Failed:         {failed}")
    print(f"  Skipped:        {len(skipped_meetings)}")
    print(f"{'='*60}\n")
    
    return {
        "total_scanned": len(meetings),
        "archived": successful,
        "skipped": len(skipped_meetings),
        "failed": failed,
        "results": results
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive processed meetings to weekly folders")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview changes without executing (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually perform archival")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    main(dry_run=dry_run)

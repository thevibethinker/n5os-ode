#!/usr/bin/env python3
"""
Meeting Weekly Organizer - Inbox-focused meeting organizer for V's OOO briefings

CHANGELOG:
- CRITICAL: Now uses manifest.json status field instead of folder suffixes
- Status awareness: ready_for_followup vs still processing (manifest_generated, mg2_in_progress)  
- Not ready: 'manifest_generated', 'mg2_completed' (still processing)
- Restricted to Inbox-only processing (never scans root Meetings folder)

This script safely identifies meetings ready for weekly roundup by reading their
manifest.json status field and respecting ongoing MG processing.
"""

import json
import logging
import shutil
import argparse
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Core paths
INBOX = Path(STAGING_DIR)
MEETINGS = Path(MEETINGS_DIR)

# Meeting readiness patterns (now from manifest.json status)
READY_STATUSES = {
    'ready_for_followup',
    'crm_synced',
    'complete'
}

# Status values that indicate a meeting is still being processed
PROCESSING_STATUSES = {'manifest_generated', 'mg2_in_progress'}

# Status values that need follow-up email checks
NEEDS_FOLLOWUP_CHECK_STATUSES = {'intelligence_generated'}


def send_alert(message: str):
    """Send SMS alert for failures."""
    if ENABLE_SMS:
        try:
            import subprocess
            result = subprocess.run(
                ["python3", f"{WORKSPACE}/N5/scripts/send_sms_notification.py", 
                 "--message", f"⚠️ Meeting Organizer: {message}"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.error(f"Failed to send SMS alert: {result.stderr}")
        except Exception as e:
            logger.error(f"SMS alert failed: {e}")


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
    """Check if FOLLOW_UP_EMAIL.md exists in the meeting folder."""
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
       a) Status is 'processed' (fully complete), OR
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
                    # Clean the title
                    title = title.replace("_", " ").strip()
                    if len(title) > 5:
                        return title[:60]
        except:
            pass
    
    # Extract from folder name
    name = folder_name
    
    # Remove date prefix
    if name.startswith("2025-"):
        parts = name.split("_", 1)
        if len(parts) > 1:
            name = parts[1]
    
    # Remove state suffix (legacy)
    for suffix in ["_[P]", "_[M]", "_[C]"]:
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
    
    nested_dirs = [d for d in meeting_dir.iterdir() if d.is_dir() and d.name.startswith("2025-")]
    
    for nested in nested_dirs:
        for item in nested.iterdir():
            if item.is_file():
                target = meeting_dir / item.name
                if not target.exists():
                    changes.append(f"  MOVE: {item.name} → parent")
                    if not dry_run:
                        shutil.move(str(item), str(target))
        
        deep_nested = [d for d in nested.iterdir() if d.is_dir() and d.name.startswith("2025-")]
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


def cleanup_empty_stub_directories(dry_run: bool = True):
    """Remove empty or single-file meeting directories at root level."""
    cleaned = []
    
    for item in MEETINGS.iterdir():
        if not (item.is_dir() and item.name.startswith("2025-")):
            continue
        
        if item.name.startswith("Week-of-"):
            continue
        
        contents = list(item.iterdir())
        
        if len(contents) == 0:
            cleaned.append(f"DELETE: {item.name} (empty)")
            if not dry_run:
                logger.info(f"Removing empty stub directory: {item.name}")
                item.rmdir()
        
        elif len(contents) == 1:
            single_file = contents[0]
            if single_file.is_file():
                cleaned.append(f"DELETE: {item.name} (1 file: {single_file.name})")
                if not dry_run:
                    logger.info(f"Removing single-file stub directory: {item.name}")
                    single_file.unlink()
                    item.rmdir()
    
    return cleaned


def reorganize(dry_run: bool = True):
    """Main reorganization function.

    CRITICAL: Only process Inbox. Uses manifest.json status to determine readiness.
    """
    print(f"\n{'='*60}")
    print(f"MEETING REORGANIZATION v2.0 {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*60}\n")
    
    all_meetings = []
    skipped = []
    
    # Collect from Inbox - check manifest.json status
    for item in INBOX.iterdir():
        if item.is_dir() and not item.name.startswith((".", "_")):
            ready, reason = is_ready_for_archival(item)
            if ready:
                all_meetings.append(("inbox", item))
                print(f"  ✓ Ready: {item.name} ({reason})")
            else:
                skipped.append((item.name, reason))
                print(f"  ⏳ Skipping: {item.name} ({reason})")
    
    print(f"\nFound {len(all_meetings)} meetings ready to process")
    print(f"Skipped {len(skipped)} meetings (still processing)\n")
    
    if not all_meetings:
        print("No meetings ready for archival.")
        return []
    
    # Group by week
    by_week = defaultdict(list)
    for source, meeting_dir in all_meetings:
        date_str = meeting_dir.name[:10]
        week = get_week_folder_name(date_str)
        by_week[week].append((source, meeting_dir))
    
    total_changes = []
    
    for week in sorted(by_week.keys()):
        week_dir = MEETINGS / week
        print(f"\n--- {week} ({len(by_week[week])} meetings) ---")
        
        if not dry_run:
            week_dir.mkdir(exist_ok=True)
        else:
            if not week_dir.exists():
                print(f"  CREATE FOLDER: {week}")
        
        for source, meeting_dir in by_week[week]:
            date_str = meeting_dir.name[:10]
            manifest_path = meeting_dir / "manifest.json"
            
            clean_name = extract_readable_name(meeting_dir.name, manifest_path)
            new_name = f"{date_str}_{clean_name.replace(' ', '-')}"
            new_path = week_dir / new_name
            
            print(f"\n  {meeting_dir.name}")
            print(f"    → {week}/{new_name}")
            
            if source == "inbox":
                nested_changes = flatten_nested_duplicates(meeting_dir, dry_run)
                if nested_changes:
                    print(f"    Nested fixes:")
                    for c in nested_changes:
                        print(f"      {c}")
            
            if not dry_run:
                try:
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
                                if item.is_file() and target.is_file():
                                    if item.stat().st_size > target.stat().st_size:
                                        shutil.copy2(str(item), str(target))
                                        logger.info(f"  Replaced {item.name} (larger file)")
                        
                        logger.info(f"Removing source folder after merge: {meeting_dir}")
                        shutil.rmtree(meeting_dir)
                        logger.info(f"  Merged {merged_count} items, source removed")
                    else:
                        shutil.move(str(meeting_dir), str(new_path))
                        logger.info(f"Moved {meeting_dir.name} to {new_path}")
                except Exception as e:
                    error_msg = f"Failed to move/merge {meeting_dir.name}: {e}"
                    logger.error(error_msg)
                    send_alert(error_msg)
            
            total_changes.append({
                "from": str(meeting_dir),
                "to": str(new_path),
                "week": week
            })
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(total_changes)} meetings organized into {len(by_week)} weekly folders")
    print(f"{'='*60}")
    
    stub_cleanup = cleanup_empty_stub_directories(dry_run)
    if stub_cleanup:
        print(f"\n--- Stub Directory Cleanup ---")
        for entry in stub_cleanup:
            print(f"  {entry}")
        print(f"\nCleaned up {len(stub_cleanup)} stub directories")
    
    return total_changes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize meetings into weekly folders")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview changes without executing (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually perform reorganization")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    reorganize(dry_run=dry_run)



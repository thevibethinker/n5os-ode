#!/usr/bin/env python3
"""
MG-6: Meeting State Transition (manifest_generated → processed)

Purpose: Transition meetings from early processing states to 'processed' status
after block generation is complete. This makes them ready for the Weekly Organizer.

v2.0 (2025-12-26): Now uses manifest.json status field instead of folder suffixes.
- Looks for: status = 'manifest_generated' or 'mg2_completed' or 'intelligence_generated'
- Validates: blocks_generated flags show completion
- Transitions to: status = 'processed'
"""

import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

# Statuses that indicate meeting is ready for transition to 'processed'
TRANSITION_READY_STATUSES = {'intelligence_generated', 'mg2_completed'}

# Statuses that are too early (still being processed)
EARLY_STATUSES = {'manifest_generated'}


def get_manifest(folder_path: Path) -> tuple[bool, dict | str]:
    """Read manifest.json from a meeting folder.
    
    Returns:
        Tuple of (success: bool, manifest_dict or error_string)
    """
    manifest_path = folder_path / "manifest.json"
    if not manifest_path.exists():
        return False, "manifest.json missing"
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return True, manifest
    except Exception as e:
        return False, f"error reading manifest: {e}"


def check_blocks_complete(manifest: dict) -> tuple[bool, str]:
    """Check if required blocks have been generated.
    
    Returns:
        Tuple of (is_complete: bool, reason: str)
    """
    blocks = manifest.get("blocks_generated", {})
    
    # Minimum required blocks for a meeting to be considered processed
    # At minimum, we need the transcript to be processed
    if blocks.get("transcript_processed"):
        return True, "transcript processed"
    
    # Check for any block generation
    if blocks.get("all_blocks") or blocks.get("brief") or blocks.get("stakeholder_intelligence"):
        return True, "blocks generated"
    
    return False, "no blocks generated yet"


def update_manifest_status(folder_path: Path, new_status: str) -> bool:
    """Update the status field in manifest.json.
    
    Returns:
        True if successful, False otherwise
    """
    manifest_path = folder_path / "manifest.json"
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        old_status = manifest.get('status', 'unknown')
        manifest['status'] = new_status
        manifest['last_updated_by'] = 'MG-6_Transition'
        manifest['last_updated_at'] = datetime.now(timezone.utc).isoformat()
        manifest['transition_history'] = manifest.get('transition_history', [])
        manifest['transition_history'].append({
            'from': old_status,
            'to': new_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent': 'MG-6'
        })
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Failed to update manifest for {folder_path.name}: {e}")
        return False


def run_transition():
    """Main transition logic."""
    print(f"\n{'='*60}")
    print(f"[M] → [P] State Transition")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")
    
    if not INBOX.exists():
        logger.error(f"Inbox path {INBOX} does not exist.")
        return 1
    
    # Find all meeting folders (exclude quarantine and hidden)
    meeting_folders = sorted([
        d for d in INBOX.iterdir() 
        if d.is_dir() and not d.name.startswith((".", "_"))
    ])
    
    print(f"Scanning for meetings in [M] state...")
    
    stats = {
        "transitioned": 0,
        "already_processed": 0,
        "not_ready": 0,
        "errors": 0,
        "details": []
    }
    
    candidates = []
    
    for folder in meeting_folders:
        success, manifest_or_error = get_manifest(folder)
        
        if not success:
            logger.debug(f"Skipping {folder.name}: {manifest_or_error}")
            continue
        
        manifest = manifest_or_error
        status = manifest.get('status', 'unknown')
        
        # Already processed - skip
        if status == 'processed':
            stats["already_processed"] += 1
            continue
        
        # Check if ready for transition
        if status in TRANSITION_READY_STATUSES:
            blocks_ok, blocks_reason = check_blocks_complete(manifest)
            if blocks_ok:
                candidates.append((folder, manifest, status, blocks_reason))
            else:
                stats["not_ready"] += 1
                stats["details"].append(f"⏳ {folder.name}: {status} but {blocks_reason}")
        
        elif status in EARLY_STATUSES:
            stats["not_ready"] += 1
            stats["details"].append(f"⏳ {folder.name}: {status} (awaiting block generation)")
    
    if not candidates:
        print("✓ No meetings in [M] state")
        if stats["already_processed"] > 0:
            print(f"  ({stats['already_processed']} already processed)")
        if stats["not_ready"] > 0:
            print(f"  ({stats['not_ready']} not ready yet)")
        return 0
    
    print(f"\nFound {len(candidates)} meetings ready for transition:\n")
    
    for folder, manifest, old_status, reason in candidates:
        print(f"  📁 {folder.name}")
        print(f"     Status: {old_status} → processed")
        print(f"     Reason: {reason}")
        
        if update_manifest_status(folder, 'processed'):
            stats["transitioned"] += 1
            print(f"     ✓ Transitioned successfully")
        else:
            stats["errors"] += 1
            print(f"     ✗ Failed to update manifest")
        print()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  Transitioned: {stats['transitioned']}")
    print(f"  Already processed: {stats['already_processed']}")
    print(f"  Not ready: {stats['not_ready']}")
    if stats['errors'] > 0:
        print(f"  Errors: {stats['errors']}")
    
    if stats["details"]:
        print(f"\nDetails:")
        for detail in stats["details"]:
            print(f"  {detail}")
    
    return 0


if __name__ == "__main__":
    sys.exit(run_transition())


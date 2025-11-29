#!/usr/bin/env python3
"""
[M] → [P] State Transition Script

Safely transitions meeting folders from [M] (manifest generated) state to [P] (processed) state.
Uses Python-based rename to avoid shell escaping issues.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Constants
INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
LOG_DIR = Path("/home/workspace/N5/runtime/meeting_pipeline")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def find_meetings_in_m_state() -> List[Path]:
    """Find all meetings in [M] state."""
    if not INBOX.exists():
        print(f"❌ Error: Inbox not found at {INBOX}")
        return []
    
    m_meetings = []
    for folder in INBOX.iterdir():
        if folder.is_dir() and folder.name.endswith("_[M]"):
            m_meetings.append(folder)
    
    return sorted(m_meetings)


def validate_readiness(folder: Path) -> Tuple[bool, str]:
    """
    Validate that a meeting is ready for [M] → [P] transition.
    
    Returns:
        (is_ready, reason)
    """
    # Check manifest exists
    manifest = folder / "manifest.json"
    if not manifest.exists():
        return False, "manifest.json not found"
    
    # Check manifest is valid JSON
    try:
        with open(manifest) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False, "manifest.json is invalid JSON"
    
    # Basic validation: meeting_date and meeting_title should exist
    if not data.get("meeting_date"):
        return False, "manifest missing meeting_date"
    
    if not data.get("meeting_title"):
        return False, "manifest missing meeting_title"
    
    return True, "ready"


def transition_to_p_state(folder: Path) -> Tuple[bool, str]:
    """
    Transition a meeting folder from [M] to [P] state.
    
    Returns:
        (success, message)
    """
    # Generate new name
    old_name = folder.name
    new_name = old_name.replace("_[M]", "_[P]")
    new_path = folder.parent / new_name
    
    # Check if destination already exists
    if new_path.exists():
        return False, f"Destination already exists: {new_name}"
    
    try:
        # Use shutil.move to handle cross-device links
        shutil.move(str(folder), str(new_path))
        return True, f"Renamed: {old_name} → {new_name}"
    except Exception as e:
        return False, f"Error renaming: {e}"


def main():
    """Main execution."""
    print(f"\n{'='*60}")
    print(f"[M] → [P] State Transition")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Find meetings in [M] state
    print("Scanning for meetings in [M] state...")
    m_meetings = find_meetings_in_m_state()
    
    if not m_meetings:
        print("✓ No meetings in [M] state")
        return 0
    
    print(f"Found {len(m_meetings)} meeting(s) in [M] state\n")
    
    # Process each meeting
    results = {
        "transitioned": [],
        "skipped": [],
        "errors": []
    }
    
    for folder in m_meetings:
        print(f"Processing: {folder.name}")
        
        # Validate readiness
        is_ready, reason = validate_readiness(folder)
        
        if not is_ready:
            print(f"  ⚠️  Skipped: {reason}")
            results["skipped"].append({
                "folder": folder.name,
                "reason": reason
            })
            continue
        
        # Transition to [P]
        success, message = transition_to_p_state(folder)
        
        if success:
            print(f"  ✓ {message}")
            results["transitioned"].append({
                "old_name": folder.name,
                "new_name": folder.name.replace("_[M]", "_[P]")
            })
        else:
            print(f"  ❌ {message}")
            results["errors"].append({
                "folder": folder.name,
                "error": message
            })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Total meetings found: {len(m_meetings)}")
    print(f"Successfully transitioned: {len(results['transitioned'])}")
    print(f"Skipped (not ready): {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")
    
    # Write log
    log_file = LOG_DIR / f"m_to_p_transition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(m_meetings),
                "transitioned": len(results["transitioned"]),
                "skipped": len(results["skipped"]),
                "errors": len(results["errors"])
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nLog saved: {log_file}")
    
    # Exit code
    if results["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


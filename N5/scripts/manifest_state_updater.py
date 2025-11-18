#!/usr/bin/env python3
"""
Update manifest.json system states for [M] → [P] transition tracking

Usage:
  python3 manifest_state_updater.py <meeting_folder> <system_name> <status> [--output-file FILE] [--task-name NAME]

Example:
  python3 manifest_state_updater.py /path/to/meeting follow_up_email complete --output-file FOLLOW_UP_EMAIL.md --task-name MG-3
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

VALID_SYSTEMS = ["intelligence_blocks", "follow_up_email", "warm_intro", "blurbs"]
VALID_STATUSES = ["not_started", "in_progress", "complete", "not_applicable", "failed"]

def update_manifest_state(meeting_folder, system_name, status, output_file=None, task_name=None):
    """Update system state in manifest.json and evaluate state transition readiness"""
    
    manifest_path = Path(meeting_folder) / "manifest.json"
    
    if not manifest_path.exists():
        print(f"❌ Error: manifest.json not found in {meeting_folder}", file=sys.stderr)
        return False
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Initialize system_states if not present
    if "system_states" not in manifest:
        manifest["system_states"] = {
            "intelligence_blocks": {"status": "not_started"},
            "follow_up_email": {"status": "not_started"},
            "warm_intro": {"status": "not_started"},
            "blurbs": {"status": "not_started", "b14_exists": False}
        }
    
    # Initialize specific system if not present
    if system_name not in manifest["system_states"]:
        manifest["system_states"][system_name] = {}
    
    # Update system state
    manifest["system_states"][system_name]["status"] = status
    manifest["system_states"][system_name]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    if output_file:
        manifest["system_states"][system_name]["output_file"] = output_file
    
    if task_name:
        manifest["system_states"][system_name]["last_updated_by"] = task_name
    
    # Special handling for intelligence_blocks
    if system_name == "intelligence_blocks" and status == "complete":
        manifest["system_states"][system_name]["required_blocks_generated"] = True
        manifest["system_states"][system_name]["total_blocks"] = manifest.get("total_blocks", 0)
    
    # Special handling for blurbs - check B14 status
    if system_name == "blurbs":
        b14_path = Path(meeting_folder) / "B14_BLURBS_REQUESTED.jsonl"
        blurbs_state = manifest["system_states"]["blurbs"]
        
        if b14_path.exists():
            blurbs_state["b14_exists"] = True
            
            # Count blurb statuses
            total = 0
            pending = 0
            complete = 0
            
            with open(b14_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        total += 1
                        if entry.get("status") == "pending":
                            pending += 1
                        elif entry.get("status") == "complete":
                            complete += 1
            
            blurbs_state["total_blurbs"] = total
            blurbs_state["pending_blurbs"] = pending
            blurbs_state["complete_blurbs"] = complete
            
            # Auto-determine status based on counts
            if pending == 0 and complete == total:
                blurbs_state["status"] = "complete"
            elif pending > 0:
                blurbs_state["status"] = "in_progress"
        else:
            blurbs_state["b14_exists"] = False
            blurbs_state["status"] = "not_applicable"
    
    # Evaluate state transition readiness
    blocking = []
    states = manifest["system_states"]
    
    if states["intelligence_blocks"]["status"] != "complete":
        blocking.append("intelligence_blocks")
    
    if states["follow_up_email"]["status"] != "complete":
        blocking.append("follow_up_email")
    
    if states["warm_intro"]["status"] not in ["complete", "not_applicable"]:
        blocking.append("warm_intro")
    
    # Check blurbs only if B14 exists
    if states["blurbs"].get("b14_exists", False):
        if states["blurbs"].get("pending_blurbs", 1) > 0:
            blocking.append("blurbs")
    
    # Update ready_for_state_transition
    manifest["system_states"]["ready_for_state_transition"] = {
        "status": len(blocking) == 0,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "can_transition_to": "P" if len(blocking) == 0 else "M",
        "blocking_systems": blocking
    }
    
    # Write back to manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Output status
    print(f"✓ Updated '{system_name}' state to '{status}'")
    print(f"  Meeting: {Path(meeting_folder).name}")
    print(f"  Ready for [P]: {manifest['system_states']['ready_for_state_transition']['status']}")
    
    if blocking:
        print(f"  ⚠ Blocking: {', '.join(blocking)}")
    else:
        print(f"  🎯 All systems complete - ready for [M] → [P] transition")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update manifest.json system states",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update after follow-up email generation
  python3 manifest_state_updater.py /path/to/meeting follow_up_email complete \\
    --output-file FOLLOW_UP_EMAIL.md --task-name MG-3

  # Update after warm intro generation
  python3 manifest_state_updater.py /path/to/meeting warm_intro complete \\
    --output-file B07_WARM_INTRO_BIDIRECTIONAL.md --task-name MG-4

  # Update after blurb generation (auto-detects B14 status)
  python3 manifest_state_updater.py /path/to/meeting blurbs complete \\
    --task-name blurb_workflow
        """
    )
    
    parser.add_argument("meeting_folder", help="Path to meeting folder containing manifest.json")
    parser.add_argument("system_name", choices=VALID_SYSTEMS, 
                       help="System name to update")
    parser.add_argument("status", choices=VALID_STATUSES,
                       help="New status value")
    parser.add_argument("--output-file", help="Output file path (relative to meeting folder)")
    parser.add_argument("--task-name", help="Name of scheduled task updating this state")
    
    args = parser.parse_args()
    
    success = update_manifest_state(
        args.meeting_folder, 
        args.system_name, 
        args.status,
        args.output_file,
        args.task_name
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


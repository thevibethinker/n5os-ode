#!/usr/bin/env python3
"""
Migrate manifest.json files to include system_states tracking

Backs up originals as: manifest.json.pre-system-states.backup
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

def analyze_meeting_folder(meeting_path):
    """
    Analyze meeting folder to determine initial system states
    Returns dict of system_name -> status
    """
    meeting_path = Path(meeting_path)
    states = {}
    
    # 1. Intelligence blocks - check if blocks are generated in manifest
    manifest_path = meeting_path / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        # Check blocks section
        blocks = manifest.get("blocks", [])
        if blocks:
            # Check if all blocks are generated
            all_generated = all(
                block.get("status") == "generated" 
                for block in blocks
            )
            states["intelligence_blocks"] = "complete" if all_generated else "in_progress"
        else:
            states["intelligence_blocks"] = "not_started"
    else:
        states["intelligence_blocks"] = "not_started"
    
    # 2. Follow-up email
    follow_up_path = meeting_path / "FOLLOW_UP_EMAIL.md"
    if follow_up_path.exists():
        states["follow_up_email"] = "complete"
    else:
        states["follow_up_email"] = "not_started"
    
    # 3. Warm intro
    warm_intro_path = meeting_path / "B07_WARM_INTRO_BIDIRECTIONAL.md"
    if warm_intro_path.exists():
        states["warm_intro"] = "complete"
    else:
        states["warm_intro"] = "not_started"
    
    # 4. Blurbs
    b14_path = meeting_path / "B14_BLURBS_REQUESTED.jsonl"
    if b14_path.exists():
        # Check if all blurbs are complete
        try:
            with open(b14_path, 'r') as f:
                blurbs = [json.loads(line.strip()) for line in f if line.strip()]
            
            total = len(blurbs)
            complete = sum(1 for b in blurbs if b.get("status") == "complete")
            pending = sum(1 for b in blurbs if b.get("status") == "pending")
            
            if complete == total:
                states["blurbs"] = "complete"
            elif complete > 0:
                states["blurbs"] = "in_progress"
            else:
                states["blurbs"] = "pending"
        except:
            states["blurbs"] = "not_started"
    else:
        states["blurbs"] = "not_applicable"
    
    return states

def evaluate_ready_for_transition(system_states):
    """
    Evaluate if meeting is ready for [M] → [P] transition
    """
    intelligence = system_states["intelligence_blocks"]["status"]
    follow_up = system_states["follow_up_email"]["status"]
    warm_intro = system_states["warm_intro"]["status"]
    blurbs = system_states["blurbs"]["status"]
    
    # Blurbs are optional (not_applicable is okay)
    blurbs_ok = blurbs in ["complete", "not_applicable"]
    
    ready = (
        intelligence == "complete" and
        follow_up == "complete" and
        warm_intro == "complete" and
        blurbs_ok
    )
    
    blocking = []
    if intelligence != "complete":
        blocking.append("intelligence_blocks")
    if follow_up != "complete":
        blocking.append("follow_up_email")
    if warm_intro != "complete":
        blocking.append("warm_intro")
    if not blurbs_ok:
        blocking.append("blurbs")
    
    return ready, blocking

def migrate_manifest(meeting_path, dry_run=False):
    """
    Migrate a single manifest.json to include system_states
    Returns (success, message)
    """
    meeting_path = Path(meeting_path)
    manifest_path = meeting_path / "manifest.json"
    backup_path = meeting_path / "manifest.json.pre-system-states.backup"
    
    if not manifest_path.exists():
        return False, "manifest.json not found"
    
    if backup_path.exists():
        return False, "Already migrated (backup exists)"
    
    # Read original manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Check if already has system_states
    if "system_states" in manifest:
        return False, "Already has system_states"
    
    # Analyze folder to determine initial states
    initial_states = analyze_meeting_folder(meeting_path)
    
    # Build system_states section
    system_states = {
        "intelligence_blocks": {
            "status": initial_states["intelligence_blocks"]
        },
        "follow_up_email": {
            "status": initial_states["follow_up_email"]
        },
        "warm_intro": {
            "status": initial_states["warm_intro"]
        },
        "blurbs": {
            "status": initial_states["blurbs"],
            "b14_exists": initial_states["blurbs"] != "not_applicable"
        }
    }
    
    # Add completion timestamps for complete items
    now = datetime.now(timezone.utc).isoformat()
    for system_name, system_data in system_states.items():
        if system_data["status"] == "complete":
            system_data["completed_at"] = now
            system_data["last_updated_by"] = "migration_script"
    
    # Evaluate readiness
    ready, blocking = evaluate_ready_for_transition(system_states)
    
    system_states["ready_for_state_transition"] = {
        "status": ready,
        "evaluated_at": now,
        "can_transition_to": "P" if ready else "M",
        "blocking_systems": blocking
    }
    
    # Add system_states to manifest
    manifest["system_states"] = system_states
    
    if dry_run:
        return True, f"Would migrate (ready={ready}, blocking={blocking})"
    
    # Backup original
    with open(backup_path, 'w') as f:
        json.dump(json.load(open(manifest_path)), f, indent=2)
    
    # Write migrated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return True, f"✓ Migrated (ready={ready}, blocking={blocking})"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate manifests to include system_states")
    parser.add_argument("--meeting", help="Single meeting folder to migrate")
    parser.add_argument("--all", action="store_true", help="Migrate all meetings in Inbox")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.meeting:
        # Single meeting
        success, msg = migrate_manifest(args.meeting, args.dry_run)
        print(f"{'[DRY RUN] ' if args.dry_run else ''}{args.meeting}: {msg}")
        return 0 if success else 1
    
    elif args.all:
        # All meetings in Inbox
        inbox = Path("/home/workspace/Personal/Meetings/Inbox")
        meetings = [d for d in inbox.iterdir() if d.is_dir()]
        
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Migrating {len(meetings)} meetings...\n")
        
        results = {"success": 0, "skipped": 0, "failed": 0}
        
        for meeting in sorted(meetings):
            success, msg = migrate_manifest(meeting, args.dry_run)
            
            if success:
                if "Already" in msg or "Would migrate" in msg:
                    results["skipped"] += 1
                else:
                    results["success"] += 1
                    print(f"✓ {meeting.name}")
                    print(f"  {msg}")
            else:
                results["failed"] += 1
                print(f"✗ {meeting.name}: {msg}")
        
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Results:")
        print(f"  Migrated: {results['success']}")
        print(f"  Skipped: {results['skipped']}")
        print(f"  Failed: {results['failed']}")
        
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())


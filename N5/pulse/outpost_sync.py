#!/usr/bin/env python3
"""
Google Drive sync executor for Pulse v2 outpost.
This script is called by Zo to execute the actual Drive operations.

Usage (called by Zo):
    python3 N5/pulse/outpost_sync.py sync <slug>

This script handles the actual Drive operations and updates meta.json.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE_ROOT = Path("/home/workspace")
CONFIG_PATH = WORKSPACE_ROOT / "Skills/pulse/config/pulse_v2_config.json"
BUILDS_DIR = WORKSPACE_ROOT / "N5/builds"

def load_config() -> dict:
    """Load Pulse v2 configuration."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "google_drive": {
            "outpost_folder": "Zo/Pulse Builds",
            "email": "attawar.v@gmail.com"
        }
    }

def update_meta_sync_status(slug: str, sync_result: dict):
    """Update meta.json with Drive sync status."""
    meta_path = BUILDS_DIR / slug / "meta.json"
    
    if not meta_path.exists():
        return
    
    meta = json.loads(meta_path.read_text())
    
    # Add or update drive_sync section
    meta["drive_sync"] = {
        "synced_at": datetime.utcnow().isoformat() + "Z",
        "folder_path": sync_result.get("folder_path"),
        "file_id": sync_result.get("file_id"),
        "shareable_link": sync_result.get("shareable_link"),
        "sync_failed": not sync_result.get("success", False),
        "error": sync_result.get("error")
    }
    
    meta_path.write_text(json.dumps(meta, indent=2))

def get_sync_instructions(slug: str) -> dict:
    """
    Generate instructions for Zo to execute Google Drive sync.
    Returns instructions that Zo should follow.
    """
    build_dir = BUILDS_DIR / slug
    
    if not build_dir.exists():
        return {
            "success": False,
            "error": f"Build not found: {slug}"
        }
    
    plan_path = build_dir / "PLAN.md"
    
    if not plan_path.exists():
        return {
            "success": False,
            "error": f"No PLAN.md found at {plan_path}"
        }
    
    plan_content = plan_path.read_text()
    config = load_config()
    outpost_folder = config.get("google_drive", {}).get("outpost_folder", "Zo/Pulse Builds")
    email = config.get("google_drive", {}).get("email")
    
    return {
        "success": True,
        "slug": slug,
        "email": email,
        "base_folder": outpost_folder,
        "target_folder": f"{outpost_folder}/{slug}",
        "file_name": f"PLAN - {slug}",
        "plan_content": plan_content,
        "instructions": [
            f"1. Get or create folder path: {outpost_folder}/{slug}",
            f"2. Upload PLAN.md as Google Doc named 'PLAN - {slug}'",
            "3. Set sharing to 'anyone with link can view'",
            "4. Get shareable link",
            "5. Update meta.json with sync status"
        ]
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: outpost_sync.py <command> <slug>", "success": False}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sync":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing slug argument", "success": False}))
            sys.exit(1)
        
        slug = sys.argv[2]
        instructions = get_sync_instructions(slug)
        print(json.dumps(instructions, indent=2))
        
        # Return error code if failed
        if not instructions.get("success", False):
            sys.exit(1)
            
    elif command == "update_meta":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing slug argument", "success": False}))
            sys.exit(1)
        
        slug = sys.argv[2]
        # Read sync result from stdin
        sync_result = json.loads(sys.stdin.read())
        update_meta_sync_status(slug, sync_result)
        print(json.dumps({"success": True, "slug": slug}))
        
    else:
        print(json.dumps({"error": f"Unknown command: {command}", "success": False}))
        sys.exit(1)

if __name__ == "__main__":
    main()

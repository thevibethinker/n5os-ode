#!/usr/bin/env python3
"""
Google Drive outpost manager for Pulse v2.
Mirrors build plans to Drive for shareable review.

Usage:
    python3 N5/pulse/outpost_manager.py sync <slug>
    python3 N5/pulse/outpost_manager.py link <slug>
    python3 N5/pulse/outpost_manager.py list
"""

import json
import argparse
import subprocess
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

def ensure_folder_structure(slug: str, email: str) -> dict:
    """
    Ensure folder structure exists in Drive: Zo/Pulse Builds/<slug>/
    Returns the folder ID.
    
    This function generates instructions for Zo to execute.
    """
    config = load_config()
    outpost_folder = config.get("google_drive", {}).get("outpost_folder", "Zo/Pulse Builds")
    
    # Split path into components
    parts = outpost_folder.split("/") + [slug]
    
    # For now, we'll use the root folder and create subfolders
    # In production, Zo would create each folder level
    # We'll use the built-in folder finding for the outpost folder
    
    return {
        "action": "ensure_folders",
        "base_path": outpost_folder,
        "build_slug": slug,
        "email": email
    }

def upload_plan_as_doc(slug: str, email: str) -> dict:
    """
    Upload PLAN.md content as a Google Doc.
    Returns shareable link information.
    """
    build_dir = BUILDS_DIR / slug
    plan_path = build_dir / "PLAN.md"
    
    if not plan_path.exists():
        return {
            "success": False,
            "error": f"No PLAN.md found at {plan_path}"
        }
    
    plan_content = plan_path.read_text()
    config = load_config()
    outpost_folder = config.get("google_drive", {}).get("outpost_folder", "Zo/Pulse Builds")
    
    # Prepare folder path for the build
    folder_path = f"{outpost_folder}/{slug}"
    
    return {
        "action": "upload_plan",
        "slug": slug,
        "folder_path": folder_path,
        "file_name": f"PLAN - {slug}",
        "content": plan_content,
        "email": email,
        "mime_type": "text/markdown"  # Will be converted to Google Doc
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

def get_shareable_link(slug: str) -> dict:
    """Get the shareable link for a build's plan."""
    meta_path = BUILDS_DIR / slug / "meta.json"
    
    if not meta_path.exists():
        return {
            "success": False,
            "error": "Build not found"
        }
    
    meta = json.loads(meta_path.read_text())
    drive_sync = meta.get("drive_sync", {})
    
    return {
        "slug": slug,
        "link": drive_sync.get("shareable_link"),
        "synced_at": drive_sync.get("synced_at"),
        "sync_failed": drive_sync.get("sync_failed", False)
    }

def list_synced_builds() -> dict:
    """List all builds that have been synced to Drive."""
    builds = []
    
    if not BUILDS_DIR.exists():
        return {"builds": [], "count": 0}
    
    for build_dir in BUILDS_DIR.iterdir():
        if build_dir.is_dir():
            meta_path = build_dir / "meta.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                drive_sync = meta.get("drive_sync", {})
                
                if drive_sync or "slug" in meta:
                    synced_at = drive_sync.get("synced_at") or ""
                    builds.append({
                        "slug": meta.get("slug"),
                        "title": meta.get("title"),
                        "link": drive_sync.get("shareable_link"),
                        "synced_at": synced_at,
                        "sync_failed": drive_sync.get("sync_failed", False)
                    })
    
    return {
        "builds": sorted(builds, key=lambda x: x.get("synced_at", ""), reverse=True),
        "count": len(builds)
    }

def sync_build_to_drive(slug: str) -> dict:
    """
    Sync entire build folder to Drive outpost.
    This generates instructions that Zo should execute.
    """
    build_dir = BUILDS_DIR / slug
    
    if not build_dir.exists():
        return {
            "success": False,
            "error": f"Build not found: {slug}"
        }
    
    config = load_config()
    email = config.get("google_drive", {}).get("email")
    
    # Generate upload instructions
    upload_instructions = upload_plan_as_doc(slug, email)
    
    if not upload_instructions.get("success", True):  # Default to True unless explicit error
        return upload_instructions
    
    # Return full sync instructions
    return {
        "success": True,
        "slug": slug,
        "email": email,
        "folder_instructions": ensure_folder_structure(slug, email),
        "upload_instructions": upload_instructions,
        "message": "Use these instructions with Zo's Google Drive integration"
    }

def main():
    parser = argparse.ArgumentParser(description="Google Drive Outpost Manager for Pulse v2")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync build plan to Drive")
    sync_parser.add_argument("slug", help="Build slug")
    
    # link command
    link_parser = subparsers.add_parser("link", help="Get shareable link")
    link_parser.add_argument("slug", help="Build slug")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List synced builds")
    
    args = parser.parse_args()
    
    if args.command == "sync":
        result = sync_build_to_drive(args.slug)
        print(json.dumps(result, indent=2))
        
        # Return error code if failed
        if not result.get("success", True):
            sys.exit(1)
            
    elif args.command == "link":
        result = get_shareable_link(args.slug)
        print(json.dumps(result, indent=2))
        
        if not result.get("link"):
            sys.exit(1)
            
    elif args.command == "list":
        result = list_synced_builds()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

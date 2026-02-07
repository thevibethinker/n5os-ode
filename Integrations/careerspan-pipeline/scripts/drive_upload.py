#!/usr/bin/env python3
"""
Google Drive Upload Handler for Careerspan Pipeline

Handles uploading Hiring POVs to the shared folder structure:
    <Shared Root>/
        <Employer Name>/
            Hiring_POV_v1.md
            Hiring_POV_v2.md (after employer responses)
            <Candidate Name>/
                ... (future candidate outputs)

Usage:
    python3 drive_upload.py --file /path/to/hiring_pov.md --employer "Company Name"
    python3 drive_upload.py --setup  # Create shared folder structure
"""

import argparse
import json
import os
import sys
from pathlib import Path

# This script outputs commands for Zo to execute via Google Drive tools
# It doesn't call the API directly - Zo handles that

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR.parent / "config.yaml"


def get_config():
    """Load config to get Drive folder ID."""
    import yaml
    with open(CONFIG_PATH) as f:
        content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        return yaml.safe_load(content)


def generate_upload_instructions(file_path: str, employer_name: str, version: str = "v1") -> dict:
    """
    Generate instructions for Zo to upload a file to Drive.
    
    Returns a dict with:
        - action: 'upload'
        - steps: List of steps for Zo to execute
        - employer_folder_name: Folder name to create/use
        - file_name: Target filename
    """
    config = get_config()
    root_folder_id = config.get("google_drive", {}).get("shared_folder_id")
    
    # Sanitize employer name for folder
    safe_employer = "".join(c if c.isalnum() or c in " -_" else "_" for c in employer_name)
    
    file_name = f"Hiring_POV_{version}.md"
    
    return {
        "action": "upload",
        "root_folder_id": root_folder_id,
        "employer_folder_name": safe_employer,
        "file_path": file_path,
        "target_filename": file_name,
        "steps": [
            f"1. Check if folder '{safe_employer}' exists under root folder {root_folder_id}",
            f"2. If not, create folder '{safe_employer}' under root",
            f"3. Upload {file_path} as '{file_name}' to the employer folder",
            "4. Return the file's web view link"
        ],
        "zo_commands": {
            "list_folder": {
                "tool": "google_drive-find-file",
                "props": {
                    "search": safe_employer,
                    "type": "folder"
                }
            },
            "create_folder": {
                "tool": "google_drive-create-folder", 
                "props": {
                    "name": safe_employer,
                    "parent": root_folder_id
                }
            },
            "upload_file": {
                "tool": "google_drive-upload-file",
                "props": {
                    "filePath": file_path,
                    "parent": "<employer_folder_id>",
                    "name": file_name
                }
            }
        }
    }


def generate_setup_instructions() -> dict:
    """
    Generate instructions for setting up the shared folder structure.
    """
    config = get_config()
    
    return {
        "action": "setup",
        "steps": [
            "1. Create a new folder called 'Careerspan Pipeline - Shared'",
            "2. Share it with shivam@corridorx.io (Viewer access)",
            "3. Get the folder ID and update config.yaml with it",
            "4. Create subfolders for each geography (optional)"
        ],
        "folder_structure": {
            "Careerspan Pipeline - Shared": {
                "description": "Root folder shared with Shivam",
                "sharing": ["shivam@corridorx.io (Viewer)"],
                "subfolders": [
                    "# Employers will be auto-created as subfolders",
                    "# e.g., 'Acme Corp/', 'TechStartup Inc/'"
                ]
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Google Drive upload handler")
    parser.add_argument("--file", help="File path to upload")
    parser.add_argument("--employer", help="Employer name for folder organization")
    parser.add_argument("--version", default="v1", help="POV version (v1, v2, etc.)")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.setup:
        result = generate_setup_instructions()
    elif args.file and args.employer:
        result = generate_upload_instructions(args.file, args.employer, args.version)
    else:
        parser.print_help()
        return
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Action: {result['action'].upper()}")
        print(f"{'='*60}\n")
        
        if "steps" in result:
            print("Steps:")
            for step in result["steps"]:
                print(f"  {step}")
        
        if "zo_commands" in result:
            print("\nZo Commands Reference:")
            for name, cmd in result["zo_commands"].items():
                print(f"\n  {name}:")
                print(f"    Tool: {cmd['tool']}")
                print(f"    Props: {json.dumps(cmd['props'], indent=6)}")


if __name__ == "__main__":
    main()

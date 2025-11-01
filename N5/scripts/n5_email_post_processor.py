#!/usr/bin/env python3
"""
N5 Email Post-Processor
Generates follow-up emails for external meetings after processing completes.

Called by Zo after meeting-process command completes.
Returns structured JSON for SMS notification.

Version: 1.0.0
Date: 2025-10-13
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
EMAIL_GENERATOR = WORKSPACE / "N5/scripts/n5_follow_up_email_generator.py"


def is_external_meeting(meeting_dir: Path) -> bool:
    """Check if meeting is external stakeholder meeting"""
    # Check folder name first
    if "_external-" in meeting_dir.name:
        return True
    
    # Fallback: check metadata file
    metadata_file = meeting_dir / "_metadata.json"
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text())
            stakeholder_type = metadata.get("stakeholder_type", "").upper()
            # Internal = team meetings, 1:1s with employees
            # External = everyone else
            return stakeholder_type not in ["INTERNAL", "TEAM", "EMPLOYEE"]
        except Exception:
            pass
    
    # Default: assume external if unclear
    return True


def email_exists(meeting_dir: Path) -> bool:
    """Check if email draft already exists"""
    deliverables = meeting_dir / "DELIVERABLES"
    if not deliverables.exists():
        return False
    
    email_files = [
        "follow_up_email_draft.md",
        "follow_up_email_copy_paste.txt"
    ]
    
    return any((deliverables / f).exists() for f in email_files)


def generate_email(meeting_dir: Path, dry_run: bool = False) -> Dict:
    """Generate email for meeting"""
    result = {
        "status": "unknown",
        "meeting": meeting_dir.name,
        "output_files": [],
        "errors": []
    }
    
    # Check if external
    if not is_external_meeting(meeting_dir):
        result["status"] = "skipped"
        result["message"] = "Internal meeting (no follow-up needed)"
        return result
    
    # Check if already exists
    if email_exists(meeting_dir):
        result["status"] = "exists"
        result["message"] = "Email draft already exists"
        
        # Find existing files
        deliverables = meeting_dir / "DELIVERABLES"
        result["output_files"] = [
            str(f.relative_to(WORKSPACE))
            for f in deliverables.glob("follow_up_email*")
            if f.is_file()
        ]
        return result
    
    try:
        # Generate email
        logger.info(f"Generating email for: {meeting_dir.name}")
        
        cmd = [
            "python3",
            str(EMAIL_GENERATOR),
            "--meeting-folder", str(meeting_dir)
        ]
        
        if dry_run:
            cmd.append("--dry-run")
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if proc.returncode == 0:
            result["status"] = "success"
            result["message"] = "Email draft generated successfully"
            
            # Find generated files
            deliverables = meeting_dir / "DELIVERABLES"
            if deliverables.exists():
                result["output_files"] = [
                    str(f.relative_to(WORKSPACE))
                    for f in deliverables.glob("follow_up_email*")
                    if f.is_file()
                ]
        else:
            result["status"] = "error"
            error_msg = proc.stderr or proc.stdout or "Unknown error"
            result["errors"].append(f"Generator failed: {error_msg}")
            logger.error(f"Generator failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        result["status"] = "error"
        result["errors"].append("Generation timeout (>120s)")
        logger.error("Generation timeout")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Exception: {str(e)}")
        logger.error(f"Exception: {e}")
    
    return result


def process_meeting(meeting_path: str, dry_run: bool = False) -> Dict:
    """Process a single meeting"""
    meeting_dir = Path(meeting_path)
    
    # Handle relative paths
    if not meeting_dir.is_absolute():
        meeting_dir = MEETINGS_DIR / meeting_path
    
    # Fuzzy match if exact path doesn't exist
    if not meeting_dir.exists():
        matches = [
            d for d in MEETINGS_DIR.glob("*")
            if d.is_dir() and meeting_path.lower() in d.name.lower()
        ]
        if matches:
            meeting_dir = sorted(matches)[-1]  # Use most recent
        else:
            return {
                "status": "error",
                "meeting": meeting_path,
                "errors": [f"Meeting folder not found: {meeting_path}"]
            }
    
    if not meeting_dir.is_dir():
        return {
            "status": "error",
            "meeting": meeting_path,
            "errors": ["Path is not a directory"]
        }
    
    return generate_email(meeting_dir, dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate follow-up email for processed meeting"
    )
    parser.add_argument(
        "meeting",
        help="Meeting folder name or path"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without generating"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only (no human text)"
    )
    
    args = parser.parse_args()
    
    result = process_meeting(args.meeting, dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        status = result["status"]
        meeting = result.get("meeting", "unknown")
        
        if status == "success":
            print(f"\n✅ Email generated: {meeting}")
            for f in result.get("output_files", []):
                print(f"   📄 {f}")
        elif status == "exists":
            print(f"\n✓ Email already exists: {meeting}")
            for f in result.get("output_files", []):
                print(f"   📄 {f}")
        elif status == "skipped":
            print(f"\n⏭️  Skipped: {meeting}")
            print(f"   {result.get('message', 'No reason provided')}")
        else:  # error
            print(f"\n❌ Failed: {meeting}")
            for err in result.get("errors", []):
                print(f"   {err}")
    
    # Return appropriate exit code
    return 0 if result["status"] in ["success", "exists", "skipped"] else 1


if __name__ == "__main__":
    sys.exit(main())

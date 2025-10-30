#!/usr/bin/env python3
"""
Validate Meeting Folder Names

Ensures all folders in N5/records/meetings follow the correct naming convention:
  YYYY-MM-DD-name-organization/

Detects and reports violations like:
  - YYYY-MM-DD/name/ (incorrect separator, missing org)
  - Other non-standard formats

Usage:
  python3 validate_meeting_folder_names.py         # Scan and report
  python3 validate_meeting_folder_names.py --fix   # Auto-fix violations
"""

import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import re
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

# Expected pattern: YYYY-MM-DD-name-organization
# Examples: 2025-10-28-jake-fohe, 2025-10-27_external-company
VALID_PATTERNS = [
    re.compile(r"^\d{4}-\d{2}-\d{2}[-_][a-z0-9-]+$"),  # Basic format
    re.compile(r"^📭\s+\d{4}-\d{2}-\d{2}[-_].*$"),      # Inbox marker
]

# Invalid patterns to detect
# Pattern: date folders with subfolders (2025-10-28/name/)
INVALID_DATE_FOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def scan_meetings_directory() -> Tuple[List[Path], List[Path]]:
    """
    Scan meetings directory for valid and invalid folders.
    
    Returns:
        (valid_folders, invalid_folders)
    """
    if not MEETINGS_DIR.exists():
        logger.error(f"Meetings directory not found: {MEETINGS_DIR}")
        return [], []
    
    valid = []
    invalid = []
    
    for item in MEETINGS_DIR.iterdir():
        if not item.is_dir():
            continue
        
        folder_name = item.name
        
        # Check if it matches any valid pattern
        is_valid = any(pattern.match(folder_name) for pattern in VALID_PATTERNS)
        
        # Check if it's an invalid date folder
        if INVALID_DATE_FOLDER.match(folder_name):
            # This is a date-only folder, which should not exist
            # Check if it has subfolders (the actual profiles)
            subfolders = list(item.iterdir())
            if subfolders:
                logger.warning(f"Found invalid date folder with subfolders: {folder_name}")
                invalid.append(item)
            else:
                # Empty date folder
                logger.warning(f"Found empty date folder: {folder_name}")
                invalid.append(item)
            continue
        
        if is_valid:
            valid.append(item)
        else:
            # Could be a special folder or non-standard format
            logger.info(f"Non-standard folder (may be OK): {folder_name}")
    
    return valid, invalid


def analyze_invalid_folder(folder: Path) -> Dict:
    """
    Analyze an invalid folder structure to determine how to fix it.
    
    Returns dict with fix strategy.
    """
    folder_name = folder.name
    
    # Check if it's a date-only folder
    if INVALID_DATE_FOLDER.match(folder_name):
        # List subfolders (profile directories)
        subfolders = [sf for sf in folder.iterdir() if sf.is_dir()]
        
        fixes = []
        for subfolder in subfolders:
            name_part = subfolder.name
            
            # Try to find profile.md to extract email
            profile_md = subfolder / "profile.md"
            email = None
            org_part = "unknown"
            
            if profile_md.exists():
                content = profile_md.read_text()
                # Extract email from first line: # Stakeholder Profile: email@domain.com
                match = re.search(r"Stakeholder Profile: ([^\s]+@[^\s]+)", content)
                if match:
                    email = match.group(1)
                    # Extract org from email domain
                    domain = email.split('@')[1]
                    org_part = domain.split('.')[0]
            
            # Construct correct path
            correct_name = f"{folder_name}-{name_part}-{org_part}"
            correct_path = MEETINGS_DIR / correct_name
            
            fixes.append({
                "wrong_path": subfolder,
                "correct_path": correct_path,
                "email": email,
                "name": name_part,
                "org": org_part
            })
        
        return {
            "type": "date_folder_with_subfolders",
            "folder": folder,
            "fixes": fixes,
            "can_auto_fix": True
        }
    
    return {
        "type": "unknown",
        "folder": folder,
        "can_auto_fix": False
    }


def fix_invalid_folders(invalid_folders: List[Path], dry_run: bool = False) -> int:
    """
    Attempt to fix invalid folder structures.
    
    Returns:
        Number of fixes applied
    """
    fixes_applied = 0
    
    for folder in invalid_folders:
        analysis = analyze_invalid_folder(folder)
        
        if not analysis["can_auto_fix"]:
            logger.warning(f"Cannot auto-fix: {folder.name}")
            continue
        
        if analysis["type"] == "date_folder_with_subfolders":
            logger.info(f"Fixing date folder: {folder.name}")
            
            for fix in analysis["fixes"]:
                logger.info(
                    f"  Moving: {fix['wrong_path'].relative_to(MEETINGS_DIR)} "
                    f"→ {fix['correct_path'].name}"
                )
                
                if not dry_run:
                    shutil.move(str(fix["wrong_path"]), str(fix["correct_path"]))
                    fixes_applied += 1
                else:
                    logger.info(f"  [DRY RUN] Would move to: {fix['correct_path']}")
            
            # Try to remove empty date folder
            if not dry_run:
                try:
                    folder.rmdir()
                    logger.info(f"  Removed empty date folder: {folder.name}")
                except OSError:
                    logger.warning(f"  Could not remove date folder (not empty): {folder.name}")
    
    return fixes_applied


def main(fix: bool = False, dry_run: bool = False) -> int:
    """
    Main validation entry point.
    
    Returns:
        0 if all folders valid, 1 if violations found
    """
    logger.info("=== Meeting Folder Name Validation ===")
    logger.info(f"Scanning: {MEETINGS_DIR}")
    
    if not MEETINGS_DIR.exists():
        logger.error(f"Meetings directory not found")
        return 1
    
    valid, invalid = scan_meetings_directory()
    
    logger.info(f"\n✓ Valid folders: {len(valid)}")
    logger.info(f"✗ Invalid folders: {len(invalid)}")
    
    if invalid:
        logger.info("\nInvalid folders found:")
        for folder in invalid:
            logger.info(f"  - {folder.name}")
            analysis = analyze_invalid_folder(folder)
            if analysis["can_auto_fix"] and analysis["type"] == "date_folder_with_subfolders":
                logger.info(f"    Type: Date folder with {len(analysis['fixes'])} subfolders")
                for f in analysis["fixes"]:
                    logger.info(f"      → Should be: {f['correct_path'].name}")
        
        if fix:
            logger.info("\n" + "=" * 60)
            if dry_run:
                logger.info("DRY RUN MODE - No changes will be made")
            
            fixes_applied = fix_invalid_folders(invalid, dry_run=dry_run)
            
            if dry_run:
                logger.info(f"\nWould apply {fixes_applied} fixes")
            else:
                logger.info(f"\n✅ Applied {fixes_applied} fixes")
        else:
            logger.info("\nRun with --fix to automatically correct these issues")
            return 1
    else:
        logger.info("\n✅ All meeting folders follow correct naming convention")
    
    return 0 if not invalid else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate meeting folder names")
    parser.add_argument("--fix", action="store_true", help="Auto-fix violations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without applying")
    args = parser.parse_args()
    
    exit(main(fix=args.fix, dry_run=args.dry_run))

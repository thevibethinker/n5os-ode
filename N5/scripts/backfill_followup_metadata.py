#!/usr/bin/env python3
"""
Backfill generated_deliverables metadata for meetings with follow-up emails in B25 blocks.

One-time migration script to populate missing metadata fields.
"""

import argparse
import json
import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")


def detect_followup_section(b25_path: Path) -> bool:
    """
    Check if B25_DELIVERABLE_CONTENT_MAP.md contains a follow-up email section.
    
    Args:
        b25_path: Path to B25 file
        
    Returns:
        True if follow-up email detected, False otherwise
    """
    try:
        content = b25_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.warning(f"Could not read {b25_path}: {e}")
        return False
    
    # Detection patterns for follow-up email sections
    patterns = [
        r'###\s*Section\s+2:\s*Follow-Up Email',
        r'##\s*Follow-Up Email\s*Draft',
        r'\*\*Subject:\*\*\s*.+?—.+?\[',  # Email subject format
    ]
    
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            logger.debug(f"Detected follow-up in {b25_path.name} via pattern: {pattern}")
            return True
    
    return False


def detect_followup_in_b25(meeting_folder: Path) -> Optional[Dict]:
    """Detect follow-up email in B25_DELIVERABLE_CONTENT_MAP."""
    b25_path = meeting_folder / "B25_DELIVERABLE_CONTENT_MAP.md"
    
    if not b25_path.exists():
        return None
    
    try:
        content = b25_path.read_text()
        
        # Check for follow-up email sections
        patterns = [
            r'###\s*Section 2:\s*Follow-Up Email',
            r'##\s*Follow-Up Email\s*Draft',
            r'##\s*Section 2.*Follow.*Up'
        ]
        
        if any(re.search(p, content, re.IGNORECASE) for p in patterns):
            # Extract subject line
            subject_match = re.search(r'\*\*Subject\*\*:?\s*(.+?)(?:\n|$)', content)
            subject = subject_match.group(1).strip() if subject_match else "Unknown Subject"
            
            # Extract email (look for email patterns)
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
            email = email_match.group(0) if email_match else ""
            
            # Extract stakeholder name from B08 if available
            b08_path = meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md"
            stakeholder_name = ""
            if b08_path.exists():
                b08_content = b08_path.read_text()
                # Try to get name from title or first heading
                name_match = re.search(r'^#\s*(.+?)(?:\n|$)', b08_content, re.MULTILINE)
                if name_match:
                    stakeholder_name = name_match.group(1).strip()
            
            relative_path = str(b25_path.relative_to(Path('/home/workspace')))
            
            return {
                "type": "follow_up_email",
                "path": relative_path,
                "section": "Section 2",
                "status": "pending",
                "subject": subject,
                "email": email,
                "stakeholder_name": stakeholder_name,
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "backfilled": True
            }
    
    except Exception as e:
        logger.debug(f"Error detecting follow-up in B25: {e}")
    
    return None


def load_metadata(meeting_folder: Path) -> Optional[Dict]:
    """Load _metadata.json from meeting folder."""
    metadata_path = meeting_folder / "_metadata.json"
    
    if not metadata_path.exists():
        logger.warning(f"No metadata file in {meeting_folder.name}")
        return None
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Corrupt JSON in {metadata_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Could not read {metadata_path}: {e}")
        return None


def backup_metadata(metadata_path: Path, dry_run: bool = False) -> bool:
    """Create timestamped backup of metadata file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = metadata_path.with_suffix(f".json.backup-{timestamp}")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would backup: {metadata_path.name} → {backup_path.name}")
        return True
    
    try:
        shutil.copy2(metadata_path, backup_path)
        logger.info(f"✓ Backed up: {backup_path.name}")
        return True
    except Exception as e:
        logger.error(f"Backup failed for {metadata_path}: {e}")
        return False


def write_metadata(metadata: Dict, meeting_folder: Path, dry_run: bool = False) -> bool:
    """Write metadata to file atomically."""
    metadata_path = meeting_folder / "_metadata.json"
    temp_path = metadata_path.with_suffix(".json.tmp")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would write: {metadata_path}")
        logger.debug(f"[DRY RUN] New content: {json.dumps(metadata.get('generated_deliverables', []), indent=2)}")
        return True
    
    try:
        # Write to temp file
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        temp_path.replace(metadata_path)
        logger.info(f"✓ Updated: {metadata_path}")
        return True
    except Exception as e:
        logger.error(f"Write failed for {metadata_path}: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def verify_metadata(meeting_folder: Path) -> bool:
    """Verify metadata file is valid JSON and contains expected fields."""
    metadata_path = meeting_folder / "_metadata.json"
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check required fields
        if 'generated_deliverables' not in metadata:
            logger.error(f"Verification failed: missing generated_deliverables in {metadata_path}")
            return False
        
        # Check structure
        if not isinstance(metadata['generated_deliverables'], list):
            logger.error(f"Verification failed: generated_deliverables not a list in {metadata_path}")
            return False
        
        logger.debug(f"✓ Verified: {metadata_path}")
        return True
    except Exception as e:
        logger.error(f"Verification failed for {metadata_path}: {e}")
        return False


def process_meeting(meeting_folder: Path, dry_run: bool = False) -> Dict[str, any]:
    """
    Process a single meeting folder.
    
    Returns:
        Dict with status: 'skipped', 'updated', or 'failed'
    """
    result = {
        'meeting_id': meeting_folder.name,
        'status': 'skipped',
        'reason': None,
        'error': None
    }
    
    # Load metadata
    metadata = load_metadata(meeting_folder)
    if metadata is None:
        result['reason'] = 'no_metadata'
        return result
    
    # Skip if already has generated_deliverables
    if 'generated_deliverables' in metadata:
        result['reason'] = 'already_has_field'
        logger.debug(f"Skip {meeting_folder.name}: already has generated_deliverables")
        return result
    
    # Check for B25 file
    b25_path = meeting_folder / "B25_DELIVERABLE_CONTENT_MAP.md"
    if not b25_path.exists():
        result['reason'] = 'no_b25'
        logger.debug(f"Skip {meeting_folder.name}: no B25 file")
        return result
    
    # Detect follow-up email
    has_followup = detect_followup_section(b25_path)
    if not has_followup:
        result['reason'] = 'no_followup_in_b25'
        logger.debug(f"Skip {meeting_folder.name}: no follow-up detected in B25")
        return result
    
    # Found follow-up! Prepare to update metadata
    logger.info(f"→ Processing: {meeting_folder.name}")
    
    # Backup metadata
    metadata_path = meeting_folder / "_metadata.json"
    if not backup_metadata(metadata_path, dry_run=dry_run):
        result['status'] = 'failed'
        result['error'] = 'backup_failed'
        return result
    
    # Add generated_deliverables field
    metadata['generated_deliverables'] = [
        {
            'type': 'follow_up_email',
            'path': f"N5/records/meetings/{meeting_folder.name}/B25_DELIVERABLE_CONTENT_MAP.md",
            'section': 'Section 2',
            'status': 'pending',
            'detected_at': datetime.now(timezone.utc).isoformat(),
            'backfilled': True
        }
    ]
    
    # Write metadata
    if not write_metadata(metadata, meeting_folder, dry_run=dry_run):
        result['status'] = 'failed'
        result['error'] = 'write_failed'
        return result
    
    # Verify (only in production mode)
    if not dry_run:
        if not verify_metadata(meeting_folder):
            result['status'] = 'failed'
            result['error'] = 'verification_failed'
            return result
    
    result['status'] = 'updated'
    logger.info(f"✓ Updated: {meeting_folder.name}")
    return result


def main(dry_run: bool = False, debug: bool = False) -> int:
    """Main execution."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if dry_run:
        logger.info("=== DRY RUN MODE - NO CHANGES WILL BE MADE ===")
    
    if not MEETINGS_DIR.exists():
        logger.error(f"Meetings directory not found: {MEETINGS_DIR}")
        return 1
    
    # Scan all meeting folders
    meeting_folders = sorted([
        d for d in MEETINGS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])
    
    logger.info(f"Scanning {len(meeting_folders)} meeting folders...")
    
    results = {
        'total': len(meeting_folders),
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'details': []
    }
    
    for meeting_folder in meeting_folders:
        try:
            result = process_meeting(meeting_folder, dry_run=dry_run)
            results['details'].append(result)
            
            if result['status'] == 'updated':
                results['updated'] += 1
            elif result['status'] == 'failed':
                results['failed'] += 1
            else:
                results['skipped'] += 1
        except Exception as e:
            logger.error(f"Unexpected error processing {meeting_folder.name}: {e}", exc_info=True)
            results['failed'] += 1
            results['details'].append({
                'meeting_id': meeting_folder.name,
                'status': 'failed',
                'error': str(e)
            })
    
    # Summary
    logger.info("")
    logger.info("=== SUMMARY ===")
    logger.info(f"Total meetings scanned: {results['total']}")
    logger.info(f"Updated: {results['updated']}")
    logger.info(f"Skipped: {results['skipped']}")
    logger.info(f"Failed: {results['failed']}")
    
    if results['updated'] > 0:
        logger.info("")
        logger.info("Updated meetings:")
        for detail in results['details']:
            if detail['status'] == 'updated':
                logger.info(f"  - {detail['meeting_id']}")
    
    if results['failed'] > 0:
        logger.warning("")
        logger.warning("Failed meetings:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                logger.warning(f"  - {detail['meeting_id']}: {detail.get('error', 'unknown')}")
        return 1
    
    if dry_run:
        logger.info("")
        logger.info("Dry run complete. Run without --dry-run to apply changes.")
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill generated_deliverables metadata for meetings with follow-up emails"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run, debug=args.debug))

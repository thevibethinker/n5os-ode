#!/usr/bin/env python3
"""
MG-6: Meeting State Transition (manifest_generated → processed)

Purpose: Transition meetings from early processing states to 'processed' status
after block generation is complete. This makes them ready for the Weekly Organizer.

v3.0 (2026-01-03): Added artifact validation and atomic writes
- Integrates with manifest_validator.py for pre-transition validation
- Uses atomic temp file + rename for safe writes
- Validates required block files exist before transition
- Detailed validation reporting

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
from tempfile import NamedTemporaryFile

# Import validator
try:
    from manifest_validator import validate_meeting, ManifestValidationReport
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

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

# Required block files that must exist for transition
REQUIRED_BLOCK_FILES = [
    "B01_DETAILED_RECAP.md",
    "B02_COMMITMENTS_CONTEXTUAL.md",
    "B25_DELIVERABLE_CONTENT_MAP.md",
    "B26_MEETING_METADATA_SUMMARY.md",
]


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


def check_blocks_complete(manifest: dict, folder_path: Path) -> tuple[bool, str, list]:
    """Check if required blocks have been generated AND files exist on disk.

    Returns:
        Tuple of (is_complete: bool, reason: str, missing_files: list)
    """
    blocks = manifest.get("blocks_generated", {})
    missing_files = []

    # v3.0: Validate actual files exist on disk
    for required_file in REQUIRED_BLOCK_FILES:
        file_path = folder_path / required_file
        if not file_path.exists():
            missing_files.append(required_file)
        elif file_path.stat().st_size == 0:
            missing_files.append(f"{required_file} (empty)")

    if missing_files:
        return False, f"missing required files: {', '.join(missing_files)}", missing_files

    # Also check manifest flags for consistency
    if blocks.get("transcript_processed"):
        return True, "transcript processed, all required files present", []

    # Check for any block generation flag
    if blocks.get("all_blocks") or blocks.get("brief") or blocks.get("stakeholder_intelligence"):
        return True, "blocks generated, all required files present", []

    # Files exist even if manifest flags not set - still valid
    return True, "required files present (manifest flags may need update)", []


def validate_artifacts(folder_path: Path) -> tuple[bool, str, dict]:
    """Run full artifact validation using manifest_validator.

    Returns:
        Tuple of (is_valid: bool, reason: str, validation_details: dict)
    """
    if not VALIDATOR_AVAILABLE:
        # Fallback to basic file check if validator not importable
        missing = []
        for required_file in REQUIRED_BLOCK_FILES:
            if not (folder_path / required_file).exists():
                missing.append(required_file)
        if missing:
            return False, f"missing: {', '.join(missing)}", {"missing": missing}
        return True, "basic file check passed (full validator unavailable)", {}

    # Use full validator
    report = validate_meeting(folder_path)

    details = {
        "error_count": report.error_count,
        "warning_count": report.warning_count,
        "can_transition": report.can_transition,
        "failed_checks": [c.check_name for c in report.checks if not c.passed and c.severity == "error"]
    }

    if report.can_transition:
        return True, "all validation checks passed", details
    else:
        return False, f"{report.error_count} errors: {', '.join(details['failed_checks'])}", details


def update_manifest_status(folder_path: Path, new_status: str, validation_details: dict = None) -> bool:
    """Update the status field in manifest.json using atomic write.

    v3.0: Uses temp file + rename for atomic writes to prevent corruption.

    Returns:
        True if successful, False otherwise
    """
    manifest_path = folder_path / "manifest.json"

    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        old_status = manifest.get('status', 'unknown')
        manifest['status'] = new_status
        manifest['last_updated_by'] = 'MG-6_Transition_v3'
        manifest['last_updated_at'] = datetime.now(timezone.utc).isoformat()

        # Add transition history entry
        manifest['transition_history'] = manifest.get('transition_history', [])
        transition_entry = {
            'from': old_status,
            'to': new_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent': 'MG-6',
            'version': '3.0'
        }

        # Include validation details if provided
        if validation_details:
            transition_entry['validation'] = {
                'passed': True,
                'error_count': validation_details.get('error_count', 0),
                'warning_count': validation_details.get('warning_count', 0)
            }

        manifest['transition_history'].append(transition_entry)

        # v3.0: Atomic write using temp file + rename
        temp_path = manifest_path.with_suffix('.json.tmp')
        try:
            with open(temp_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            # Atomic rename (works on POSIX systems)
            temp_path.replace(manifest_path)
            return True

        except Exception as write_error:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise write_error

    except Exception as e:
        logger.error(f"Failed to update manifest for {folder_path.name}: {e}")
        return False


def run_transition(validate_only: bool = False, verbose: bool = False):
    """Main transition logic.

    Args:
        validate_only: If True, only validate without transitioning
        verbose: If True, show detailed validation output
    """
    print(f"\n{'='*60}")
    print(f"[M] → [P] State Transition (v3.0)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    if validate_only:
        print(f"Mode: VALIDATE ONLY (no changes)")
    if VALIDATOR_AVAILABLE:
        print(f"Validator: Available")
    else:
        print(f"Validator: Not available (using basic checks)")
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
        "validation_failed": 0,
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
            # v3.0: Check blocks AND file existence
            blocks_ok, blocks_reason, missing = check_blocks_complete(manifest, folder)
            if blocks_ok:
                candidates.append((folder, manifest, status, blocks_reason))
            else:
                stats["not_ready"] += 1
                stats["details"].append(f"⏳ {folder.name}: {blocks_reason}")

        elif status in EARLY_STATUSES:
            stats["not_ready"] += 1
            stats["details"].append(f"⏳ {folder.name}: {status} (awaiting block generation)")

    if not candidates:
        print("✓ No meetings ready for [M] → [P] transition")
        if stats["already_processed"] > 0:
            print(f"  ({stats['already_processed']} already processed)")
        if stats["not_ready"] > 0:
            print(f"  ({stats['not_ready']} not ready yet)")
        return 0

    print(f"\nFound {len(candidates)} meetings ready for transition:\n")

    for folder, manifest, old_status, reason in candidates:
        print(f"  📁 {folder.name}")
        print(f"     Status: {old_status} → processed")
        print(f"     Block check: {reason}")

        # v3.0: Run full artifact validation
        valid, validation_reason, validation_details = validate_artifacts(folder)

        if not valid:
            stats["validation_failed"] += 1
            print(f"     ❌ Validation FAILED: {validation_reason}")
            if verbose and validation_details.get('failed_checks'):
                for check in validation_details['failed_checks']:
                    print(f"        - {check}")
            stats["details"].append(f"❌ {folder.name}: validation failed - {validation_reason}")
            print()
            continue

        print(f"     ✓ Validation passed")
        if validation_details.get('warning_count', 0) > 0:
            print(f"       ({validation_details['warning_count']} warnings)")

        # Perform transition (unless validate_only mode)
        if validate_only:
            print(f"     ⏸ Would transition (validate-only mode)")
            stats["transitioned"] += 1  # Count as would-transition
        else:
            if update_manifest_status(folder, 'processed', validation_details):
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
    print(f"  Not ready (blocks): {stats['not_ready']}")
    print(f"  Validation failed: {stats['validation_failed']}")
    if stats['errors'] > 0:
        print(f"  Errors: {stats['errors']}")

    if stats["details"]:
        print(f"\nDetails:")
        for detail in stats["details"]:
            print(f"  {detail}")

    return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="MG-6: Meeting State Transition ([M] → [P])",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
v3.0 Features:
  - Artifact validation: Verifies required files exist before transition
  - Atomic writes: Uses temp file + rename for safe manifest updates
  - Detailed reporting: Shows validation status for each meeting

Examples:
  # Run normal transition
  python3 m_to_p_transition.py

  # Validate only (no changes)
  python3 m_to_p_transition.py --validate-only

  # Verbose output with validation details
  python3 m_to_p_transition.py --verbose
        """
    )

    parser.add_argument("--validate-only", "-n", action="store_true",
                       help="Validate without making changes (dry run)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed validation output")

    args = parser.parse_args()

    return run_transition(
        validate_only=args.validate_only,
        verbose=args.verbose
    )


if __name__ == "__main__":
    sys.exit(main())


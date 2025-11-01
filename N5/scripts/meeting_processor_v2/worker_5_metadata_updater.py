#!/usr/bin/env python3
"""
Worker 5: Metadata Updater
Updates metadata after successful processing.
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)

PROCESSOR_VERSION = "meeting-processor-v2"


def create_metadata(meeting_dir: Path, meeting_id: str, gdrive_id: str) -> dict:
    """
    Create metadata dictionary for meeting.
    
    Args:
        meeting_dir: Production meeting directory
        meeting_id: Meeting identifier
        gdrive_id: Google Drive file ID
        
    Returns:
        dict: Metadata structure
    """
    # Scan for generated blocks
    intel_dir = meeting_dir / "INTELLIGENCE"
    blocks_generated = []
    
    if intel_dir.exists():
        for file in intel_dir.iterdir():
            if file.is_file() and file.suffix == ".md":
                blocks_generated.append(file.name)
    
    # Get transcript size
    transcript_path = meeting_dir / f"{meeting_dir.name}.transcript.jsonl"
    transcript_size = transcript_path.stat().st_size if transcript_path.exists() else 0
    
    # Determine classification from directory structure
    classification = "external"  # Default
    parts = meeting_dir.name.split("_")
    if len(parts) >= 3:
        classification = parts[2]  # e.g., 2025-11-01_0000_external_mujgan
    
    metadata = {
        "meeting_id": meeting_id,
        "classification": classification,
        "gdrive_id": gdrive_id,
        "status": "processed",
        "blocks_generated": sorted(blocks_generated),
        "transcript_size_bytes": transcript_size,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "processor_version": PROCESSOR_VERSION
    }
    
    return metadata


def write_metadata_file(meeting_dir: Path, metadata: dict, dry_run: bool = False) -> bool:
    """
    Write _metadata.json to meeting folder.
    
    Args:
        meeting_dir: Meeting directory
        metadata: Metadata dict
        dry_run: If True, don't write
        
    Returns:
        bool: Success
    """
    metadata_path = meeting_dir / "_metadata.json"
    
    if dry_run:
        logging.info(f"[DRY-RUN] Would write metadata to: {metadata_path}")
        logging.info(f"[DRY-RUN] Content: {json.dumps(metadata, indent=2)}")
        return True
    
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logging.info(f"✓ Metadata written: {metadata_path}")
        return True
    except Exception as e:
        logging.warning(f"⚠ Failed to write metadata: {e}")
        return False


def append_to_registry(registry_path: Path, metadata: dict, dry_run: bool = False) -> bool:
    """
    Append entry to global meeting registry.
    
    Args:
        registry_path: Path to meeting_gdrive_registry.jsonl
        metadata: Metadata dict
        dry_run: If True, don't write
        
    Returns:
        bool: Success
    """
    registry_entry = {
        "meeting_id": metadata["meeting_id"],
        "gdrive_id": metadata["gdrive_id"],
        "classification": metadata["classification"],
        "processed_at": metadata["processed_at"],
        "blocks_count": len(metadata["blocks_generated"])
    }
    
    if dry_run:
        logging.info(f"[DRY-RUN] Would append to registry: {registry_path}")
        logging.info(f"[DRY-RUN] Entry: {json.dumps(registry_entry)}")
        return True
    
    try:
        # Ensure parent directory exists
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_path, "a") as f:
            f.write(json.dumps(registry_entry) + "\n")
        logging.info(f"✓ Registry updated: {registry_path}")
        return True
    except Exception as e:
        logging.warning(f"⚠ Failed to update registry: {e}")
        return False


def generate_report(metadata_success: bool, registry_success: bool, warnings: list) -> dict:
    """
    Generate W5 update report.
    
    Args:
        metadata_success: Whether metadata was written
        registry_success: Whether registry was updated
        warnings: List of warning messages
        
    Returns:
        dict: Report structure
    """
    report = {
        "worker": "W5_metadata_updater",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata_created": metadata_success,
        "registry_updated": registry_success,
        "warnings": warnings
    }
    return report


def validate_inputs(meeting_dir: Path, meeting_id: str, gdrive_id: str) -> bool:
    """
    Validate required inputs.
    
    Args:
        meeting_dir: Meeting directory path
        meeting_id: Meeting identifier
        gdrive_id: Google Drive file ID
        
    Returns:
        bool: Validation passed
    """
    if not meeting_dir.exists():
        logging.error(f"Meeting directory not found: {meeting_dir}")
        return False
    
    if not meeting_id:
        logging.error("Meeting ID is required")
        return False
    
    if not gdrive_id:
        logging.error("Google Drive ID is required")
        return False
    
    return True


def main(meeting_dir: str, meeting_id: str, gdrive_id: str, dry_run: bool = False) -> int:
    """
    Main execution: Update metadata and registry.
    
    Args:
        meeting_dir: Production meeting directory
        meeting_id: Meeting identifier
        gdrive_id: Google Drive file ID
        dry_run: If True, preview only
        
    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    try:
        meeting_path = Path(meeting_dir)
        warnings = []
        
        # Validate inputs
        if not validate_inputs(meeting_path, meeting_id, gdrive_id):
            return 1
        
        logging.info(f"Worker 5: Metadata Updater starting")
        logging.info(f"Meeting: {meeting_path.name}")
        logging.info(f"Meeting ID: {meeting_id}")
        logging.info(f"GDrive ID: {gdrive_id}")
        
        if dry_run:
            logging.info("=== DRY-RUN MODE ===")
        
        # Create metadata
        metadata = create_metadata(meeting_path, meeting_id, gdrive_id)
        logging.info(f"Metadata created: {len(metadata['blocks_generated'])} blocks")
        
        # Write metadata file
        metadata_success = write_metadata_file(meeting_path, metadata, dry_run)
        if not metadata_success:
            warnings.append("Metadata file write failed")
        
        # Update registry
        registry_path = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
        registry_success = append_to_registry(registry_path, metadata, dry_run)
        if not registry_success:
            warnings.append("Registry append failed")
        
        # Generate report
        report = generate_report(metadata_success, registry_success, warnings)
        report_path = meeting_path / "W5_update_report.json"
        
        if not dry_run:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            logging.info(f"✓ Report written: {report_path}")
        else:
            logging.info(f"[DRY-RUN] Would write report to: {report_path}")
            logging.info(f"[DRY-RUN] Report: {json.dumps(report, indent=2)}")
        
        # Summary
        if warnings:
            logging.warning(f"⚠ Completed with warnings: {warnings}")
        else:
            logging.info("✓ Worker 5 completed successfully")
        
        # Non-critical worker: Always return success
        return 0
        
    except Exception as e:
        logging.error(f"Worker 5 error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Worker 5: Update meeting metadata and registry"
    )
    parser.add_argument(
        "--meeting-dir",
        required=True,
        help="Production meeting directory path"
    )
    parser.add_argument(
        "--meeting-id",
        required=True,
        help="Meeting identifier"
    )
    parser.add_argument(
        "--gdrive-id",
        required=True,
        help="Google Drive file ID"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing"
    )
    
    args = parser.parse_args()
    exit(main(args.meeting_dir, args.meeting_id, args.gdrive_id, args.dry_run))

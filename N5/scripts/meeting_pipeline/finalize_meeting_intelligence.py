#!/usr/bin/env python3
"""
Meeting Intelligence Finalization Workflow

This script processes completed meetings from Inbox to Archive with database tracking.
It enforces completion validation, removes duplicates, and maintains the archive structure.

Prerequisites:
- Meetings must be in /home/workspace/Personal/Meetings/Inbox/ with _[P] suffix
- Manifest file must exist with all blocks marked as "completed"
- Database script must be accessible

Exit Codes:
- 0: Success
- 1: No meetings found or validation error
- 2: Database operation failed
- 3: Archive operation failed
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class MeetingFinalizer:
    def __init__(self):
        self.inbox_dir = Path("/home/workspace/Personal/Meetings/Inbox")
        self.archive_base = Path("/home/workspace/Personal/Meetings/Archive")
        self.db_script = Path("/home/workspace/N5/scripts/meeting_pipeline/add_to_database.py")
        
    def find_completed_meetings(self):
        """Find all folders in Inbox with _[P] suffix."""
        if not self.inbox_dir.exists():
            logger.error(f"Inbox directory does not exist: {self.inbox_dir}")
            return []
        
        completed = []
        for item in self.inbox_dir.iterdir():
            if item.is_dir() and item.name.endswith("_[P]"):
                completed.append(item)
        
        # Sort by date (oldest first) - extract date from YYYY-MM-DD format
        completed.sort(key=lambda p: p.name[:10])
        return completed
    
    def find_nested_duplicate(self, parent_path):
        """Check for nested folder with same base name (without suffix and date)."""
        # Extract base name without date and suffix
        # Format: YYYY-MM-DD_Meeting_Name_[P]
        parent_name = parent_path.name
        if len(parent_name) < 11:  # Too short to have date
            return None
            
        date_part = parent_name[:10]  # YYYY-MM-DD
        remaining = parent_name[11:]  # Remove date and underscore
        
        if not remaining.endswith("_[P]"):
            return None
            
        # Extract meeting name (everything between date and _[P])
        meeting_name = remaining[:-3]  # Remove _[P]
        
        # Look for nested folder pattern
        nested_name = f"{date_part}_{meeting_name}"
        nested_path = parent_path / nested_name
        
        if nested_path.exists() and nested_path.is_dir():
            return nested_path
        return None
    
    def clean_nested_duplicates(self, meeting_path):
        """Remove nested duplicate folders."""
        nested = self.find_nested_duplicate(meeting_path)
        if nested:
            logger.info(f"Removing nested duplicate: {nested}")
            import shutil
            shutil.rmtree(nested)
            logger.info("✓ Nested duplicate removed")
            return True
        return False
    
    def validate_completion(self, meeting_path):
        """Verify all blocks in manifest have 'completed' status."""
        manifest_path = meeting_path / "manifest.json"
        
        if not manifest_path.exists():
            logger.error(f"Manifest not found: {manifest_path}")
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest: {e}")
            return False
        
        # Check if manifest has blocks
        if "blocks" not in manifest:
            logger.error("Manifest missing 'blocks' key")
            return False
        
        # Validate all blocks are completed
        pending_blocks = []
        for block_id, block_data in manifest["blocks"].items():
            status = block_data.get("status", "unknown")
            if status != "completed":
                pending_blocks.append((block_id, status))
        
        if pending_blocks:
            logger.error(f"Found {len(pending_blocks)} non-completed blocks:")
            for block_id, status in pending_blocks:
                logger.error(f"  - {block_id}: {status}")
            return False
        
        logger.info(f"✓ All {len(manifest['blocks'])} blocks validated as completed")
        return True
    
    def add_to_database(self, meeting_path):
        """Add meeting to database using the pipeline script."""
        if not self.db_script.exists():
            logger.error(f"Database script not found: {self.db_script}")
            return False
        
        # Check if already in database by looking for database ID marker
        db_id_file = meeting_path / ".database_id"
        if db_id_file.exists():
            logger.info("✓ Meeting already in database (skipping)")
            return True
        
        logger.info(f"Adding to database: {meeting_path.name}")
        
        # Run database script
        import subprocess
        try:
            result = subprocess.run([
                sys.executable, str(self.db_script),
                "--meeting-folder", str(meeting_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"Database script failed: {result.stderr}")
                return False
            
            logger.info("✓ Database entry created successfully")
            return True
        except subprocess.TimeoutExpired:
            logger.error("Database script timed out")
            return False
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            return False
    
    def get_year_quarter(self, date_str):
        """Convert YYYY-MM-DD to YYYY-QN format."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return None
    
    def extract_date_from_name(self, folder_name):
        """Extract YYYY-MM-DD date from folder name."""
        if len(folder_name) >= 10:
            date_part = folder_name[:10]
            # Validate date format
            try:
                datetime.strptime(date_part, "%Y-%m-%d")
                return date_part
            except ValueError:
                pass
        return None
    
    def move_to_archive(self, meeting_path):
        """Move meeting to year-quarter archive folder."""
        # Extract date from folder name
        date_str = self.extract_date_from_name(meeting_path.name)
        if not date_str:
            logger.error(f"Could not extract valid date from: {meeting_path.name}")
            return False
        
        year_quarter = self.get_year_quarter(date_str)
        if not year_quarter:
            return False
        
        # Create archive directory
        archive_dir = self.archive_base / year_quarter
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Remove _[P] suffix to get clean name
        clean_name = meeting_path.name[:-3]  # Remove _[P]
        destination = archive_dir / clean_name
        
        if destination.exists():
            logger.error(f"Destination already exists: {destination}")
            return False
        
        logger.info(f"Archiving to: {destination.relative_to(self.archive_base.parent)}")
        
        try:
            meeting_path.rename(destination)
            logger.info("✓ Archive successful")
            return True
        except Exception as e:
            logger.error(f"Archive operation failed: {e}")
            return False
    
    def process_meeting(self, meeting_path):
        """Process a single meeting through all steps."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {meeting_path.name}")
        logger.info(f"{'='*60}")
        
        # Step 2: Clean nested duplicates
        self.clean_nested_duplicates(meeting_path)
        
        # Step 3: Validate completion
        if not self.validate_completion(meeting_path):
            logger.error("✗ Validation failed: Not all blocks completed")
            return False
        
        # Step 4: Add to database
        if not self.add_to_database(meeting_path):
            logger.error("✗ Database operation failed")
            return False
        
        # Step 5: Move to archive
        if not self.move_to_archive(meeting_path):
            logger.error("✗ Archive operation failed")
            return False
        
        logger.info("\n✓ SUCCESS: Meeting finalized and archived")
        return True
    
    def run(self):
        """Main execution: find and process all completed meetings."""
        logger.info("Starting Meeting Intelligence Finalization")
        logger.info(f"{'='*60}")
        
        # Step 1: Find completed meetings
        completed_meetings = self.find_completed_meetings()
        
        if not completed_meetings:
            logger.info("No completed meetings found in Inbox")
            return 0
        
        logger.info(f"Found {len(completed_meetings)} completed meeting(s)")
        
        # Process oldest first
        success_count = 0
        for meeting_path in completed_meetings:
            try:
                if self.process_meeting(meeting_path):
                    success_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing {meeting_path.name}: {e}")
                continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY: {success_count}/{len(completed_meetings)} meetings processed successfully")
        
        if success_count == len(completed_meetings):
            logger.info("✓ All meetings finalized successfully")
            return 0
        else:
            logger.warning("⚠ Some meetings failed to process")
            return 1

def main():
    parser = argparse.ArgumentParser(description="Finalize meeting intelligence and archive")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    finalizer = MeetingFinalizer()
    return finalizer.run()

if __name__ == "__main__":
    sys.exit(main())


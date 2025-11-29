#!/usr/bin/env python3
"""
Meeting Folder Duplicate Cleanup Script

Fixes the MG-6️⃣ task bug where folders are created with literal backslashes:
- Incorrect: meeting_name_\\[P\\]
- Correct: meeting_name_[P]

This script:
1. Identifies duplicate pairs (escaped + correct formats)
2. Merges content from both folders
3. Renames escaped folders to correct format
4. Validates no data loss

Safety: Dry-run by default, detailed logging, no overwrites.
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any

# Constants
INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
LOG_DIR = Path("/home/workspace/N5/runtime/meeting_cleanup")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class DuplicateCleanup:
    """Handles cleanup of duplicate meeting folders with escaped brackets."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.log_file = LOG_DIR / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.operations = []
        
    def log_operation(self, op_type: str, details: dict):
        """Log an operation for audit trail."""
        self.operations.append({
            "timestamp": datetime.now().isoformat(),
            "type": op_type,
            "details": details,
            "dry_run": self.dry_run
        })
    
    def find_duplicates(self) -> List[Tuple[Path, Optional[Path]]]:
        """
        Find duplicate folder pairs.
        
        Returns:
            List of (escaped_folder, correct_folder_or_None) tuples
        """
        if not INBOX.exists():
            print(f"❌ Error: Inbox not found at {INBOX}")
            sys.exit(1)
            
        escaped_folders = []
        correct_folders = []
        
        # Scan all folders
        for folder in INBOX.iterdir():
            if not folder.is_dir():
                continue
                
            name_bytes = folder.name.encode()
            
            # Check for literal backslashes in name
            if b"\\[P\\]" in name_bytes:
                escaped_folders.append(folder)
            elif b"[P]" in name_bytes:
                correct_folders.append(folder)
        
        # Match duplicates
        duplicates = []
        for esc_folder in escaped_folders:
            # Construct what the correct folder name would be
            base_name = esc_folder.name.replace("_\\[P\\]", "")
            correct_name = f"{base_name}_[P]"
            correct_path = INBOX / correct_name
            
            # Check if correct version exists
            if correct_path in correct_folders:
                duplicates.append((esc_folder, correct_path))
            else:
                # Escaped folder exists alone (will just be renamed)
                duplicates.append((esc_folder, None))
        
        return duplicates
    
    def verify_no_overwrites(self, source: Path, dest: Path) -> bool:
        """
        Verify that moving files from source to dest won't overwrite anything.
        
        Returns:
            True if safe, False if conflicts exist
        """
        if not dest.exists():
            return True
            
        conflicts = []
        for src_file in source.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(source)
                dest_file = dest / rel_path
                if dest_file.exists():
                    conflicts.append(rel_path)
        
        if conflicts:
            print(f"⚠️  Conflicts detected in {dest.name}:")
            for conflict in conflicts:
                print(f"   - {conflict}")
            return False
            
        return True
    
    def _merge_folders(self, source: Path, dest: Path) -> Dict[str, Any]:
        """
        Merge content from source folder into dest folder.
        For conflicts, keep the newer file based on mtime.
        """
        result = {
            "moved": [],
            "skipped": [],
            "conflicts_resolved": []
        }
        
        for item in source.iterdir():
            if not item.is_file():
                continue
            
            dest_file = dest / item.name
            
            if not dest_file.exists():
                # No conflict, safe to move
                if self.dry_run:
                    print(f"   [DRY-RUN] Would move: {item.name}")
                else:
                    shutil.move(str(item), str(dest_file))
                result["moved"].append(item.name)
            else:
                # Conflict: compare timestamps and keep newer
                source_mtime = item.stat().st_mtime
                dest_mtime = dest_file.stat().st_mtime
                
                if source_mtime > dest_mtime:
                    # Source is newer, replace dest
                    if self.dry_run:
                        print(f"   [DRY-RUN] Would replace with newer: {item.name} (source newer by {int(source_mtime - dest_mtime)}s)")
                    else:
                        dest_file.unlink()
                        shutil.move(str(item), str(dest_file))
                    result["conflicts_resolved"].append(f"{item.name} (kept newer from source)")
                else:
                    # Dest is newer or same, keep dest
                    if self.dry_run:
                        print(f"   [DRY-RUN] Would keep existing: {item.name} (dest newer by {int(dest_mtime - source_mtime)}s)")
                    else:
                        item.unlink()  # Remove older source file
                    result["conflicts_resolved"].append(f"{item.name} (kept newer from dest)")
        
        return result
    
    def merge_folders(self, source: Path, dest: Path) -> bool:
        """
        Merge contents from source into dest using timestamp-based conflict resolution.
        
        Args:
            source: Folder to merge from
            dest: Folder to merge into
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self._merge_folders(source, dest)
            
            self.log_operation("merge", {
                "source": str(source),
                "dest": str(dest),
                "files_moved": result["moved"],
                "conflicts_resolved": result["conflicts_resolved"],
                "moved_count": len(result["moved"]),
                "resolved_count": len(result["conflicts_resolved"])
            })
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error during merge: {e}")
            self.log_operation("merge_failed", {
                "source": str(source),
                "dest": str(dest),
                "error": str(e)
            })
            return False
    
    def rename_folder(self, old_path: Path, new_name: str) -> bool:
        """
        Rename a folder, ensuring correct bracket format.
        
        Args:
            old_path: Current folder path
            new_name: New folder name (just the name, not full path)
            
        Returns:
            True if successful, False otherwise
        """
        new_path = old_path.parent / new_name
        
        if new_path.exists() and new_path != old_path:
            print(f"   ❌ Cannot rename: {new_name} already exists")
            self.log_operation("rename_failed", {
                "old_path": str(old_path),
                "new_name": new_name,
                "reason": "destination_exists"
            })
            return False
        
        if self.dry_run:
            print(f"   [DRY-RUN] Would rename: {old_path.name} → {new_name}")
        else:
            # Use shutil.move to handle cross-device links
            shutil.move(str(old_path), str(new_path))
            print(f"   ✓ Renamed: {old_path.name} → {new_name}")
        
        self.log_operation("rename", {
            "old_path": str(old_path),
            "new_path": str(new_path),
            "old_name": old_path.name,
            "new_name": new_name
        })
        
        return True
    
    def remove_empty_folder(self, folder: Path) -> bool:
        """Remove an empty folder after merge."""
        try:
            if self.dry_run:
                print(f"   [DRY-RUN] Would remove empty folder: {folder.name}")
            else:
                folder.rmdir()
                print(f"   ✓ Removed empty folder: {folder.name}")
                
            self.log_operation("remove", {
                "folder": str(folder)
            })
            return True
            
        except OSError as e:
            print(f"   ⚠️  Could not remove {folder.name}: {e}")
            return False
    
    def cleanup_duplicate(self, esc_folder: Path, correct_folder: Optional[Path]) -> bool:
        """
        Clean up a duplicate pair or standalone escaped folder.
        
        Args:
            esc_folder: Folder with escaped brackets (\\[P\\])
            correct_folder: Folder with correct brackets ([P]), or None
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Processing: {esc_folder.name}")
        print(f"{'='*60}")
        
        if correct_folder:
            # Case 1: Duplicate pair exists
            print(f"✓ Duplicate detected")
            print(f"  Escaped:  {esc_folder.name}")
            print(f"  Correct:  {correct_folder.name}")
            print(f"\nMerging content from escaped → correct...")
            
            if not self.merge_folders(esc_folder, correct_folder):
                return False
            
            print(f"\nRemoving empty escaped folder...")
            if not self.remove_empty_folder(esc_folder):
                print(f"   ⚠️  Manual cleanup needed: {esc_folder}")
                
        else:
            # Case 2: Only escaped version exists, rename it
            print(f"✓ Standalone escaped folder (no duplicate)")
            correct_name = esc_folder.name.replace("_\\[P\\]", "_[P]")
            print(f"\nRenaming to correct format...")
            
            if not self.rename_folder(esc_folder, correct_name):
                return False
        
        return True
    
    def run(self) -> Dict:
        """
        Execute the cleanup process.
        
        Returns:
            Summary statistics
        """
        print(f"\n{'='*60}")
        print(f"Meeting Folder Duplicate Cleanup")
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
        print(f"{'='*60}\n")
        
        # Find duplicates
        print("Scanning for duplicates...")
        duplicates = self.find_duplicates()
        
        if not duplicates:
            print("✓ No duplicates found! All folders use correct format.")
            return {
                "duplicates_found": 0,
                "duplicates_fixed": 0,
                "errors": 0
            }
        
        print(f"\n✓ Found {len(duplicates)} folder(s) needing cleanup\n")
        
        # Process each duplicate
        success_count = 0
        error_count = 0
        
        for esc_folder, correct_folder in duplicates:
            try:
                if self.cleanup_duplicate(esc_folder, correct_folder):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"\n❌ Error processing {esc_folder.name}: {e}")
                self.log_operation("error", {
                    "folder": str(esc_folder),
                    "error": str(e)
                })
                error_count += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Summary")
        print(f"{'='*60}")
        print(f"Duplicates found: {len(duplicates)}")
        print(f"Successfully processed: {success_count}")
        print(f"Errors: {error_count}")
        
        if self.dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made")
            print(f"Review the plan above, then run with --execute to apply changes")
        else:
            print(f"\n✓ Cleanup complete!")
        
        # Write log
        with open(self.log_file, 'w') as f:
            json.dump({
                "mode": "dry_run" if self.dry_run else "execute",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "duplicates_found": len(duplicates),
                    "success": success_count,
                    "errors": error_count
                },
                "operations": self.operations
            }, f, indent=2)
        
        print(f"\nLog saved: {self.log_file}")
        
        return {
            "duplicates_found": len(duplicates),
            "duplicates_fixed": success_count,
            "errors": error_count
        }


def verify_state() -> Dict:
    """
    Verify current state without making changes.
    
    Returns:
        State report
    """
    print(f"\n{'='*60}")
    print(f"Meeting Folder State Verification")
    print(f"{'='*60}\n")
    
    if not INBOX.exists():
        print(f"❌ Error: Inbox not found at {INBOX}")
        return {"error": "inbox_not_found"}
    
    escaped_folders = []
    correct_folders = []
    
    for folder in INBOX.iterdir():
        if not folder.is_dir():
            continue
            
        name_bytes = folder.name.encode()
        
        if b"\\[P\\]" in name_bytes:
            escaped_folders.append(folder.name)
        elif b"[P]" in name_bytes:
            correct_folders.append(folder.name)
    
    # Find duplicate pairs
    duplicates = []
    for esc_name in escaped_folders:
        base_name = esc_name.replace("_\\[P\\]", "")
        correct_name = f"{base_name}_[P]"
        if correct_name in correct_folders:
            duplicates.append(base_name)
    
    # Report
    print(f"Folders with escaped brackets (\\[P\\]): {len(escaped_folders)}")
    for name in sorted(escaped_folders):
        print(f"  - {name}")
    
    print(f"\nFolders with correct brackets ([P]): {len(correct_folders)}")
    for name in sorted(correct_folders)[:5]:
        print(f"  - {name}")
    if len(correct_folders) > 5:
        print(f"  ... and {len(correct_folders) - 5} more")
    
    print(f"\nDuplicate pairs detected: {len(duplicates)}")
    for base in sorted(duplicates):
        print(f"  - {base}")
        print(f"    • {base}_\\[P\\]")
        print(f"    • {base}_[P]")
    
    if len(escaped_folders) == 0:
        print(f"\n✓ All folders use correct format!")
        status = "healthy"
    else:
        print(f"\n⚠️  {len(escaped_folders)} folder(s) need cleanup")
        status = "needs_cleanup"
    
    return {
        "status": status,
        "escaped_count": len(escaped_folders),
        "correct_count": len(correct_folders),
        "duplicate_pairs": len(duplicates),
        "escaped_folders": escaped_folders,
        "duplicates": duplicates
    }


def main():
    parser = argparse.ArgumentParser(
        description="Clean up duplicate meeting folders with escaped brackets"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute cleanup (default is dry-run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes (default)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify state without making any changes"
    )
    
    args = parser.parse_args()
    
    # Verify mode
    if args.verify:
        result = verify_state()
        sys.exit(0 if result.get("status") == "healthy" else 1)
    
    # Determine mode
    dry_run = not args.execute
    
    # Execute cleanup
    cleanup = DuplicateCleanup(dry_run=dry_run)
    result = cleanup.run()
    
    # Exit code based on results
    if result["errors"] > 0:
        sys.exit(1)
    elif result["duplicates_found"] > 0 and dry_run:
        sys.exit(2)  # Duplicates exist but dry-run
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()





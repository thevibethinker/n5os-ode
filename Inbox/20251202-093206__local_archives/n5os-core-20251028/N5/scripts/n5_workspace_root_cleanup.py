#!/usr/bin/env python3
"""
N5 Workspace Root Cleanup
Part of conversation-end: Review and cleanup files in workspace root.

Most files in root are conversation artifacts and should be deleted unless
explicitly needed. This script identifies and removes transient files.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import hashlib
import json

WORKSPACE_ROOT = Path("/home/workspace")

# Directories that should exist
PERMANENT_DIRS = {
    "Articles", "Backups", "Careerspan", "Documents", "Exports", 
    "Images", "Knowledge", "Lists", "N5", "Personal", "Records",
    "Trash", "projects"
}

# File patterns that should be DELETED (conversation artifacts)
DELETE_PATTERNS = [
    # Function templates (AI prompts - transient)
    r"^Function \[\d+\] - .+\.(txt|pdf|md)$",
    
    # Companion files (references - transient)
    r"^Companion \[\d+\] - .+\.(txt|xml)$",
    
    # Temporary completion docs
    r"^(AUTOMATED|COMPLETE|DOCUMENTATION|FINAL|SYSTEM|QUICK|README).+\.(md|txt)$",
    r"^.*COMPLETE.*\.md$",
    
    # System prompts (should be in proper location)
    r"^Real-Time_Thought_Partner.+\.txt$",
    r"^careerspan_meeting_automation.+\.txt$",
    
    # Temporary meeting docs (should be processed and moved)
    r"^.*meeting.*(process|summary|setup).*\.(md|txt)$",
    r"^meeting-(process|complete|summary)\.md$",
    r"^automated-meeting-processing-setup\.md$",
    
    # Duplicate files (with numeric suffixes)
    r"^.+ \(\d+\)\.(txt|pdf|md|jpg|xml)$",
]

# File patterns to KEEP (exceptions)
KEEP_PATTERNS = [
    # None currently - be aggressive about cleanup
]

# File patterns to ASK about (ambiguous)
ASK_PATTERNS = [
    # Meeting transcripts/docs without "process" in name
    r"^[a-z_]+_meeting_\d{4}-\d{2}-\d{2}\.(docx|txt)$",
    
    # Screenshots
    r"^Xnip\d{4}-\d{2}-\d{2}.+\.jpg$",
    
    # Project refactor summaries
    r"^PREFS_REFACTOR_SUMMARY\.md$",
]


def should_delete(filename: str) -> bool:
    """Check if file should be deleted."""
    for pattern in DELETE_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    return False


def should_keep(filename: str) -> bool:
    """Check if file should definitely be kept."""
    for pattern in KEEP_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    return False


def should_ask(filename: str) -> bool:
    """Check if file needs user decision."""
    for pattern in ASK_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    return False


def is_duplicate(filename: str, all_files: List[str]) -> Tuple[bool, str]:
    """
    Check if file is a duplicate (has numeric suffix).
    Returns: (is_dup, original_name)
    """
    match = re.match(r'^(.+) \((\d+)\)(\..+)$', filename)
    if match:
        base_name = match.group(1)
        ext = match.group(3)
        original = f"{base_name}{ext}"
        # Check if original exists
        if original in all_files or original == filename:
            return (True, original)
    return (False, None)


def scan_workspace_root() -> Dict[str, List[Path]]:
    """
    Scan workspace root and categorize files for cleanup.
    
    Returns:
        {
            'delete': [(file, reason), ...],
            'keep': [file, ...],
            'ask': [(file, reason), ...],
            'protected': [file, ...],
        }
    """
    results = {
        'delete': [],
        'keep': [],
        'ask': [],
        'protected': [],
    }
    
    # Get all root files
    all_files = [f for f in WORKSPACE_ROOT.iterdir() if f.is_file()]
    all_filenames = [f.name for f in all_files]
    
    for filepath in all_files:
        filename = filepath.name
        
        # Skip hidden files and git
        if filename.startswith('.'):
            results['protected'].append(filepath)
            continue
        
        # Check for duplicates first
        is_dup, original = is_duplicate(filename, all_filenames)
        if is_dup:
            results['delete'].append((filepath, f"Duplicate of {original}"))
            continue
        
        # Check if should keep
        if should_keep(filename):
            results['keep'].append(filepath)
            continue
        
        # Check if should delete
        if should_delete(filename):
            # Categorize reason
            if re.match(r"^Function \[\d+\]", filename):
                reason = "Function template (conversation artifact)"
            elif re.match(r"^Companion \[\d+\]", filename):
                reason = "Companion file (conversation artifact)"
            elif "COMPLETE" in filename.upper():
                reason = "Temporary completion doc"
            elif "meeting" in filename.lower():
                reason = "Temporary meeting processing doc"
            else:
                reason = "Conversation artifact"
            
            results['delete'].append((filepath, reason))
            continue
        
        # Check if should ask
        if should_ask(filename):
            if "meeting" in filename.lower():
                reason = "Meeting transcript - keep or delete?"
            elif "Xnip" in filename:
                reason = "Screenshot - keep or delete?"
            elif "REFACTOR" in filename:
                reason = "Refactor summary - archive?"
            else:
                reason = "Ambiguous file"
            
            results['ask'].append((filepath, reason))
            continue
        
        # Default: Flag as needing review (unknown)
        results['ask'].append((filepath, "Unknown file - manual review needed"))
    
    return results


def generate_cleanup_report(scan_results: Dict) -> str:
    """Generate human-readable cleanup report."""
    lines = []
    lines.append("=" * 80)
    lines.append("WORKSPACE ROOT CLEANUP REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Files to delete
    lines.append(f"## FILES TO DELETE ({len(scan_results['delete'])})")
    lines.append("")
    if scan_results['delete']:
        lines.append("These files will be moved to Trash:")
        lines.append("")
        for filepath, reason in sorted(scan_results['delete'], key=lambda x: x[0].name):
            lines.append(f"  ✗ {filepath.name}")
            lines.append(f"     → {reason}")
        lines.append("")
    else:
        lines.append("  ✓ No files to delete")
        lines.append("")
    
    # Files needing decision
    lines.append(f"## FILES NEEDING DECISION ({len(scan_results['ask'])})")
    lines.append("")
    if scan_results['ask']:
        lines.append("These files need your review:")
        lines.append("")
        for filepath, reason in sorted(scan_results['ask'], key=lambda x: x[0].name):
            size = filepath.stat().st_size
            modified = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')
            lines.append(f"  ? {filepath.name}")
            lines.append(f"     → {reason}")
            lines.append(f"     → Size: {size:,} bytes, Modified: {modified}")
        lines.append("")
    else:
        lines.append("  ✓ All files classified")
        lines.append("")
    
    # Summary
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"  Files to delete:       {len(scan_results['delete'])}")
    lines.append(f"  Files needing review:  {len(scan_results['ask'])}")
    lines.append(f"  Protected files:       {len(scan_results['protected'])}")
    lines.append("")
    
    return "\n".join(lines)


def execute_cleanup(scan_results: Dict, dry_run: bool = True):
    """Execute cleanup operations."""
    trash_dir = WORKSPACE_ROOT / "Trash"
    trash_dir.mkdir(exist_ok=True)
    
    actions_log = []
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be moved\n")
    else:
        print("\n🧹 EXECUTING CLEANUP\n")
    
    # Delete files (move to trash)
    for filepath, reason in scan_results['delete']:
        target = trash_dir / filepath.name
        
        # Handle name collisions
        counter = 1
        while target.exists():
            target = trash_dir / f"{filepath.stem}_{counter}{filepath.suffix}"
            counter += 1
        
        action = f"DELETE: {filepath.name} → Trash/ ({reason})"
        if not dry_run:
            shutil.move(str(filepath), str(target))
            action += " ✓"
        
        actions_log.append(action)
        print(f"  {action}")
    
    # Save log
    if not dry_run:
        log_path = WORKSPACE_ROOT / "N5" / "runtime" / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'actions': actions_log,
                'summary': {
                    'deleted': len(scan_results['delete']),
                    'pending_review': len(scan_results['ask']),
                }
            }, f, indent=2)
        print(f"\n📝 Log saved to: {log_path.relative_to(WORKSPACE_ROOT)}")
    
    return len(actions_log)


def main():
    """Main entry point."""
    import sys
    
    dry_run = "--execute" not in sys.argv
    
    print("\n🧹 N5 Workspace Root Cleanup\n")
    print("Purpose: Remove conversation artifacts from workspace root")
    print("")
    
    # Scan
    print("📊 Scanning workspace root...")
    scan_results = scan_workspace_root()
    print("✓ Scan complete\n")
    
    # Report
    report = generate_cleanup_report(scan_results)
    
    # Save report
    report_path = WORKSPACE_ROOT / "N5" / "runtime" / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"📄 Full report saved to: {report_path.relative_to(WORKSPACE_ROOT)}\n")
    
    # Execute
    if scan_results['delete'] or scan_results['ask']:
        if dry_run:
            print("=" * 80)
            print("To execute cleanup, run: python3 <script> --execute")
            print("=" * 80)
        else:
            # Execute deletions
            deleted_count = execute_cleanup(scan_results, dry_run=False)
            print(f"\n✅ Cleanup complete: {deleted_count} files moved to Trash")
            
            # Remind about files needing review
            if scan_results['ask']:
                print(f"\n⚠️  {len(scan_results['ask'])} files still need manual review")
    else:
        print("✅ Workspace root is clean!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
N5 Workspace Maintenance Script
Automatically categorizes, archives, and deduplicates files in workspace root.
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
DRY_RUN = True  # Safety first - always preview changes

# Target directories
DIRS = {
    "templates": WORKSPACE_ROOT / "Documents" / "Templates",
    "prompts": WORKSPACE_ROOT / "Documents" / "Prompts",
    "companions": WORKSPACE_ROOT / "Documents" / "Companions",
    "system_prompts": WORKSPACE_ROOT / "Careerspan" / "System-Prompts",
    "project_docs": WORKSPACE_ROOT / "Documents" / "Projects",
    "meeting_docs": WORKSPACE_ROOT / "Documents" / "Meetings",
    "temp_docs": WORKSPACE_ROOT / "Documents" / "Archive" / "Temp",
    "imported": WORKSPACE_ROOT / "Documents" / "Imported",
    "trash": WORKSPACE_ROOT / "Trash",
}

# File categorization rules
RULES = {
    # Functions are prompt templates
    r"^Function \[\d+\] - .+\.(txt|pdf|md)$": "prompts",
    
    # Companions are reference files
    r"^Companion \[\d+\] - .+\.(txt|xml)$": "companions",
    
    # System prompts for Careerspan
    r"^Real-Time_Thought_Partner_Careerspan.+\.txt$": "system_prompts",
    r"^careerspan_meeting_automation_suite.+\.txt$": "system_prompts",
    
    # Temporary project completion docs
    r"^(AUTOMATED|COMPLETE|DOCUMENTATION|FINAL|SYSTEM|QUICK|README).+\.(md|txt)$": "temp_docs",
    r"^.*COMPLETE.*\.md$": "temp_docs",
    
    # Meeting-related files
    r"^.*meeting.*(process|summary|analysis|setup).*\.(md|txt)$": "meeting_docs",
    r"^alex_meeting.+\.(docx|txt)$": "meeting_docs",
    
    # Project-specific docs
    r"^PREFS_REFACTOR_SUMMARY\.md$": "project_docs",
    
    # Screenshots and images
    r"^Xnip\d{4}-\d{2}-\d{2}.+\.jpg$": "imported",
}


def ensure_dirs():
    """Ensure all target directories exist."""
    for name, path in DIRS.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory: {path.relative_to(WORKSPACE_ROOT)}")


def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def find_duplicates(files: List[Path]) -> Dict[str, List[Path]]:
    """Find duplicate files by content hash, grouped by base name."""
    duplicates = {}
    base_name_groups = {}
    
    # Group by base name pattern (without duplicate suffixes)
    for f in files:
        base_name = re.sub(r'\s*\(\d+\)', '', f.stem)
        if base_name not in base_name_groups:
            base_name_groups[base_name] = []
        base_name_groups[base_name].append(f)
    
    # For each group, check if they're true duplicates
    for base_name, file_list in base_name_groups.items():
        if len(file_list) > 1:
            # Calculate hashes
            hash_map = {}
            for f in file_list:
                file_hash = get_file_hash(f)
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(f)
            
            # Keep only groups with actual duplicates
            for file_hash, dup_files in hash_map.items():
                if len(dup_files) > 1:
                    # Sort to keep the one without suffix
                    dup_files.sort(key=lambda x: (
                        '(' in x.name,  # Files without () come first
                        x.stat().st_mtime  # Then by modification time
                    ))
                    duplicates[base_name] = dup_files
    
    return duplicates


def categorize_file(filename: str) -> str:
    """Determine target directory for a file based on rules."""
    for pattern, target in RULES.items():
        if re.match(pattern, filename, re.IGNORECASE):
            return target
    return None


def scan_root() -> Dict[str, List[Path]]:
    """Scan workspace root and categorize files."""
    results = {
        "duplicates": [],
        "categorizable": [],
        "unknown": [],
        "protected": [],
    }
    
    # Protected files that should never be moved
    protected_patterns = [
        r"^\.git",
        r"^\.n5_backups",
        r"^\..*",  # Hidden files
    ]
    
    root_files = [f for f in WORKSPACE_ROOT.iterdir() if f.is_file()]
    
    # Find duplicates
    duplicates = find_duplicates(root_files)
    for base_name, dup_list in duplicates.items():
        # Keep first, mark rest as duplicates
        for dup_file in dup_list[1:]:
            results["duplicates"].append((dup_file, dup_list[0]))
    
    # Categorize files
    for f in root_files:
        # Check if protected
        if any(re.match(p, f.name) for p in protected_patterns):
            results["protected"].append(f)
            continue
        
        # Check if already marked as duplicate
        if any(f == dup[0] for dup in results["duplicates"]):
            continue
        
        # Try to categorize
        target = categorize_file(f.name)
        if target:
            results["categorizable"].append((f, target))
        else:
            # Only flag non-directory files as unknown
            if f.is_file():
                results["unknown"].append(f)
    
    return results


def generate_report(scan_results: Dict) -> str:
    """Generate a human-readable report of proposed actions."""
    report = []
    report.append("=" * 80)
    report.append("WORKSPACE MAINTENANCE REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    # Duplicates
    report.append(f"## DUPLICATES TO REMOVE ({len(scan_results['duplicates'])})")
    report.append("")
    if scan_results['duplicates']:
        for dup_file, original in scan_results['duplicates']:
            report.append(f"  REMOVE: {dup_file.name}")
            report.append(f"    ↳ Duplicate of: {original.name}")
            report.append("")
    else:
        report.append("  ✓ No duplicates found")
        report.append("")
    
    # Categorizable files
    report.append(f"## FILES TO ORGANIZE ({len(scan_results['categorizable'])})")
    report.append("")
    if scan_results['categorizable']:
        by_target = {}
        for f, target in scan_results['categorizable']:
            if target not in by_target:
                by_target[target] = []
            by_target[target].append(f)
        
        for target, files in sorted(by_target.items()):
            report.append(f"  → {DIRS[target].relative_to(WORKSPACE_ROOT)}/")
            for f in files:
                report.append(f"    - {f.name}")
            report.append("")
    else:
        report.append("  ✓ No files to organize")
        report.append("")
    
    # Unknown files
    report.append(f"## UNCLASSIFIED FILES ({len(scan_results['unknown'])})")
    report.append("")
    if scan_results['unknown']:
        report.append("  These files need manual review:")
        for f in scan_results['unknown']:
            size = f.stat().st_size
            modified = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d')
            report.append(f"    - {f.name} ({size:,} bytes, modified {modified})")
        report.append("")
        report.append("  Consider adding rules to categorize these files.")
        report.append("")
    else:
        report.append("  ✓ All files classified")
        report.append("")
    
    # Summary
    report.append("=" * 80)
    report.append("SUMMARY")
    report.append("=" * 80)
    report.append(f"  Duplicates to remove:  {len(scan_results['duplicates'])}")
    report.append(f"  Files to organize:     {len(scan_results['categorizable'])}")
    report.append(f"  Files needing review:  {len(scan_results['unknown'])}")
    report.append(f"  Protected files:       {len(scan_results['protected'])}")
    report.append("")
    
    return "\n".join(report)


def execute_maintenance(scan_results: Dict, dry_run: bool = True):
    """Execute the maintenance operations."""
    actions_log = []
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be moved or deleted\n")
    else:
        print("\n🚀 EXECUTING MAINTENANCE OPERATIONS\n")
    
    # Remove duplicates
    for dup_file, original in scan_results['duplicates']:
        action = f"DELETE: {dup_file.name} (duplicate of {original.name})"
        if not dry_run:
            target = DIRS['trash'] / dup_file.name
            shutil.move(str(dup_file), str(target))
            action += " ✓"
        actions_log.append(action)
        print(f"  {action}")
    
    # Move categorizable files
    for f, target_key in scan_results['categorizable']:
        target_dir = DIRS[target_key]
        target_path = target_dir / f.name
        
        # Handle name collisions
        counter = 1
        while target_path.exists():
            target_path = target_dir / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        
        action = f"MOVE: {f.name} → {target_path.relative_to(WORKSPACE_ROOT)}"
        if not dry_run:
            shutil.move(str(f), str(target_path))
            action += " ✓"
        actions_log.append(action)
        print(f"  {action}")
    
    # Save log
    if not dry_run:
        log_path = WORKSPACE_ROOT / "N5" / "runtime" / f"maintenance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'actions': actions_log,
                'summary': {
                    'duplicates_removed': len(scan_results['duplicates']),
                    'files_organized': len(scan_results['categorizable']),
                    'files_pending_review': len(scan_results['unknown']),
                }
            }, f, indent=2)
        print(f"\n📝 Log saved to: {log_path.relative_to(WORKSPACE_ROOT)}")
    
    return actions_log


def main():
    """Main entry point."""
    print("\n🔧 N5 Workspace Maintenance\n")
    
    # Ensure directories exist
    ensure_dirs()
    print()
    
    # Scan workspace
    print("📊 Scanning workspace root...")
    scan_results = scan_root()
    print("✓ Scan complete\n")
    
    # Generate report
    report = generate_report(scan_results)
    
    # Save report
    report_path = WORKSPACE_ROOT / "N5" / "runtime" / f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n📄 Full report saved to: {report_path.relative_to(WORKSPACE_ROOT)}")
    
    # Execute (dry run by default)
    if DRY_RUN:
        print("\n" + "=" * 80)
        print("To execute these changes, run with --execute flag")
        print("=" * 80)
    else:
        execute_maintenance(scan_results, dry_run=False)


if __name__ == "__main__":
    import sys
    if "--execute" in sys.argv:
        DRY_RUN = False
    main()

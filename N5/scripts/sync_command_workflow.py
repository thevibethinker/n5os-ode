#!/usr/bin/env python3
"""
Command workflow to sync N5_mirror to N5 with conflict resolution via Socratic questioning
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict

SYNC_SCRIPT = Path("/home/workspace/N5_mirror/scripts/sync_to_main.py")


def run_sync_script(dry_run: bool = True) -> Dict:
    """Run the sync script, returns parsed JSON report or None on failure"""
    args = [str(SYNC_SCRIPT)]
    if dry_run:
        args.append("--dry-run")
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Sync script failed: {result.stderr}")
        return None
    # The sync script logs but does not output JSON, so assuming log file is final report
    # We'll read the latest report file from N5
    report_dir = Path("/home/workspace/Knowledge/sync_reports")
    if not report_dir.exists():
        print("No sync report directory found")
        return None
    # Find latest report
    reports = sorted(report_dir.glob("sync_report_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not reports:
        print("No sync report file found")
        return None
    with open(reports[0], 'r') as f:
        report = json.load(f)
    return report


def find_conflicts(report: Dict) -> List[str]:
    """Find scripts that synced with failures or are potentially conflicting"""
    conflicts = []
    for item in report["manifest"]:
        if item["status"] == "failed":
            conflicts.append(item["file"] if "file" in item else item["path"])
        # Here we could add logic to detect soft conflicts, like differing hashes.
    return conflicts


def socratic_clarification(conflicts: List[str]):
    """Engage USER in Q&A to resolve conflicts, preferring additive merges"""
    print("Conflict resolution required for the following files:")
    for c in conflicts:
        print(f" - {c}")
    print("For each, answer the following:")
    for c in conflicts:
        print(f"\nFile: {c}")
        print("Do you want to:")
        print("  1 - Keep existing N5 version as is (preserve info, no overwrite)")
        print("  2 - Overwrite N5 version with N5_mirror (replace with tested)")
        print("  3 - Manually review and merge later")
        choice = None
        while choice not in {"1", "2", "3"}:
            choice = input(f"Choose option for '{c}' (1/2/3): ")
        # Store decision for now as a dict (could be saved for later merging tool)
        yield (c, int(choice))


def apply_decisions(decisions: Dict[str, int]):
    """Apply USER decisions to resolve conflicts"""
    for file_name, decision in decisions.items():
        source = Path("/home/workspace/N5_mirror/scripts") / file_name
        target = Path("/home/workspace/N5/scripts") / file_name
        if decision == 1:
            print(f"Keeping existing N5 version of {file_name}")
            # Do nothing
        elif decision == 2:
            print(f"Overwriting {file_name} with N5_mirror version")
            # Overwrite file
            target.write_text(source.read_text())
        else:
            print(f"Please manually review and merge {file_name} later")


if __name__ == '__main__':
    dry_run = True
    print("Starting dry run sync...")
    report = run_sync_script(dry_run)
    if not report:
        print("Sync failed or no report found.")
        sys.exit(1)
    conflicts = find_conflicts(report)
    if conflicts:
        print("Conflicts detected.")
        decisions = {}
        for conflict_file, decision in socratic_clarification(conflicts):
            decisions[conflict_file] = decision
        apply_decisions(decisions)
    else:
        print("No conflicts, proceeding with real sync...")
        # Run real sync
        subprocess.run([sys.executable, str(SYNC_SCRIPT)])
    print("Synchronization complete.")

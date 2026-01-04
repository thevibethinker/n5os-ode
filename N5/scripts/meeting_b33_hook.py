#!/usr/bin/env python3
"""
Meeting B33 Hook: Integration point for B33 edge generation in meeting pipeline.

This module provides functions that can be imported by meeting processing scripts
to trigger B33 edge generation at the appropriate pipeline stage.

Usage:
    from meeting_b33_hook import generate_b33_for_meeting, should_generate_b33
    
    if should_generate_b33(meeting_folder):
        result = generate_b33_for_meeting(meeting_folder)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE = Path("/home/workspace")
B33_SCRIPT = WORKSPACE / "N5/scripts/generate_b33_edges.py"


def should_generate_b33(meeting_folder: Path) -> bool:
    """
    Check if a meeting folder is ready for B33 generation.
    
    Requirements:
    - Has B01_DETAILED_RECAP.md (core intelligence complete)
    - Does NOT have B33_DECISION_EDGES.jsonl yet
    - Has manifest.json indicating MG-2 complete
    """
    folder = Path(meeting_folder)
    
    # Check for prerequisite blocks
    b01_exists = (folder / "B01_DETAILED_RECAP.md").exists()
    if not b01_exists:
        return False
    
    # Check if B33 already exists
    b33_exists = (folder / "B33_DECISION_EDGES.jsonl").exists()
    if b33_exists:
        return False
    
    # Optional: check manifest for MG-2 completion
    manifest_path = folder / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            blocks = manifest.get("blocks_generated", {})
            # At minimum, stakeholder intelligence should be done
            if not blocks.get("stakeholder_intelligence", False):
                return False
        except:
            pass
    
    return True


def generate_b33_for_meeting(
    meeting_folder: Path,
    auto_commit: bool = False,
    timeout: int = 180
) -> Dict[str, Any]:
    """
    Generate B33 edges for a meeting folder.
    
    Args:
        meeting_folder: Path to meeting folder
        auto_commit: If True, commit edges directly to edges.db
        timeout: Max seconds to wait for generation
        
    Returns:
        Dict with status, edges_extracted, errors
    """
    folder = Path(meeting_folder)
    
    if not folder.exists():
        return {
            "status": "error",
            "meeting_folder": str(folder),
            "errors": ["Folder not found"]
        }
    
    cmd = [
        sys.executable,
        str(B33_SCRIPT),
        "--meeting", str(folder)
    ]
    
    if auto_commit:
        cmd.append("--auto-commit")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "meeting_folder": str(folder),
                    "output": result.stdout
                }
        else:
            return {
                "status": "error",
                "meeting_folder": str(folder),
                "errors": [result.stderr or "Unknown error"],
                "returncode": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "meeting_folder": str(folder),
            "errors": [f"Timeout after {timeout}s"]
        }
    except Exception as e:
        return {
            "status": "error",
            "meeting_folder": str(folder),
            "errors": [str(e)]
        }


def batch_generate_b33(
    meetings_root: Path = WORKSPACE / "Personal/Meetings",
    limit: Optional[int] = None,
    auto_commit: bool = False
) -> Dict[str, Any]:
    """
    Generate B33 for all eligible meetings.
    
    Args:
        meetings_root: Root folder to scan for meetings
        limit: Max meetings to process (None = all)
        auto_commit: If True, commit edges directly
        
    Returns:
        Summary dict with processed/skipped/errors counts
    """
    results = {
        "processed": [],
        "skipped": [],
        "errors": [],
        "total_edges": 0
    }
    
    # Find all [P] and [M] state meetings by walking directory tree
    candidates = []
    for folder in meetings_root.rglob("*"):
        if folder.is_dir() and ("_[P]" in folder.name or "_[M]" in folder.name):
            candidates.append(folder)
    
    # Sort by date (most recent first) for predictable processing order
    candidates.sort(key=lambda x: x.name, reverse=True)
    
    # Apply limit
    if limit:
        candidates = candidates[:limit]
    
    for folder in candidates:
        if should_generate_b33(folder):
            result = generate_b33_for_meeting(folder, auto_commit=auto_commit)
            
            if result.get("status") == "success":
                results["processed"].append(str(folder))
                results["total_edges"] += result.get("edges_extracted", 0)
            elif result.get("status") == "exists":
                results["skipped"].append(str(folder))
            else:
                results["errors"].append({
                    "folder": str(folder),
                    "errors": result.get("errors", [])
                })
        else:
            results["skipped"].append(str(folder))
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="B33 pipeline integration")
    parser.add_argument("--check", help="Check if meeting is ready for B33")
    parser.add_argument("--batch", action="store_true", help="Process all eligible meetings")
    parser.add_argument("--limit", type=int, help="Max meetings to process in batch")
    parser.add_argument("--auto-commit", action="store_true", help="Auto-commit edges")
    
    args = parser.parse_args()
    
    if args.check:
        folder = Path(args.check)
        ready = should_generate_b33(folder)
        print(f"Ready for B33: {ready}")
        
    elif args.batch:
        results = batch_generate_b33(limit=args.limit, auto_commit=args.auto_commit)
        print(json.dumps(results, indent=2))
        
    else:
        parser.print_help()



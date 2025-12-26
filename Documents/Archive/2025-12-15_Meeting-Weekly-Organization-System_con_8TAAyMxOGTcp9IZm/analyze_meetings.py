#!/usr/bin/env python3
"""Analyze meeting folder structure and identify issues."""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS = Path("/home/workspace/Personal/Meetings")

def get_week_folder_name(date_str: str) -> str:
    """Get week folder name like 'Week-of-2025-12-09' (Monday of that week)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        # Get Monday of the week
        monday = date - timedelta(days=date.weekday())
        return f"Week-of-{monday.strftime('%Y-%m-%d')}"
    except:
        return "Unknown-Week"

def clean_meeting_name(folder_name: str) -> str:
    """Extract cleaner name from folder name."""
    # Remove date prefix and [P]/[M]/[C] suffix
    name = folder_name
    if name.startswith("2025-"):
        parts = name.split("_", 1)
        if len(parts) > 1:
            name = parts[1]
    
    # Remove state suffix
    for suffix in ["_[P]", "_[M]", "_[C]"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    return name

def analyze():
    issues = {
        "nested_duplicates": [],
        "long_names": [],
        "meetings_by_week": defaultdict(list),
        "total_meetings": 0,
        "has_manifest": 0,
        "has_transcript": 0,
    }
    
    for item in INBOX.iterdir():
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue
        
        issues["total_meetings"] += 1
        
        # Extract date
        date_str = item.name[:10] if item.name[:4] == "2025" else "unknown"
        week = get_week_folder_name(date_str)
        
        # Check for nested duplicates
        nested_dirs = [d for d in item.iterdir() if d.is_dir() and not d.name.startswith(".")]
        for nested in nested_dirs:
            if nested.name.startswith("2025-"):
                issues["nested_duplicates"].append(str(item))
                break
        
        # Check name length
        clean_name = clean_meeting_name(item.name)
        if len(clean_name) > 60:
            issues["long_names"].append({
                "path": item.name,
                "clean_name": clean_name,
                "length": len(clean_name)
            })
        
        # Check for manifest/transcript
        if (item / "manifest.json").exists():
            issues["has_manifest"] += 1
        if (item / "transcript.jsonl").exists():
            issues["has_transcript"] += 1
        
        # Add to week bucket
        issues["meetings_by_week"][week].append({
            "folder": item.name,
            "date": date_str,
            "clean_name": clean_name[:50] + "..." if len(clean_name) > 50 else clean_name
        })
    
    return issues

if __name__ == "__main__":
    results = analyze()
    print(f"\n=== MEETING INBOX ANALYSIS ===")
    print(f"Total meetings: {results['total_meetings']}")
    print(f"With manifest: {results['has_manifest']}")
    print(f"With transcript: {results['has_transcript']}")
    print(f"\n--- NESTED DUPLICATES ({len(results['nested_duplicates'])}) ---")
    for p in results["nested_duplicates"][:10]:
        print(f"  {p}")
    print(f"\n--- OVERLY LONG NAMES ({len(results['long_names'])}) ---")
    for item in results["long_names"][:5]:
        print(f"  {item['length']} chars: {item['clean_name'][:60]}...")
    print(f"\n--- MEETINGS BY WEEK ---")
    for week in sorted(results["meetings_by_week"].keys()):
        meetings = results["meetings_by_week"][week]
        print(f"  {week}: {len(meetings)} meetings")
        for m in meetings[:3]:
            print(f"    - {m['date']}: {m['clean_name']}")
        if len(meetings) > 3:
            print(f"    ... and {len(meetings)-3} more")

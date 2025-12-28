#!/usr/bin/env python3
"""
Acquisition Deal Scanner - Scan for unprocessed meetings matching watched entities.

This script:
1. Scans recent meeting folders
2. Identifies meetings related to watched acquisition targets
3. Reports which meetings need syncing to Airtable

Usage:
    python3 acquisition_deal_scanner.py                    # Scan last 2 weeks
    python3 acquisition_deal_scanner.py --weeks 4          # Scan last 4 weeks
    python3 acquisition_deal_scanner.py --all              # Scan all meetings
    python3 acquisition_deal_scanner.py --entity "Ribbon"  # Filter by entity
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))
from airtable_config import (
    WATCHED_ENTITIES,
    ACQUISITION_KEYWORDS,
    MEETINGS_DIR,
)


def get_week_folders(weeks_back: int = 2, scan_all: bool = False) -> List[Path]:
    """Get week folders to scan."""
    meetings_root = Path(MEETINGS_DIR)
    week_folders = sorted(meetings_root.glob("Week-of-*"))
    
    if scan_all:
        return week_folders
    
    # Calculate cutoff date
    cutoff = datetime.now() - timedelta(weeks=weeks_back)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    
    recent_folders = []
    for folder in week_folders:
        # Extract date from folder name
        match = re.search(r"Week-of-(\d{4}-\d{2}-\d{2})", folder.name)
        if match:
            week_date = match.group(1)
            if week_date >= cutoff_str:
                recent_folders.append(folder)
    
    return recent_folders


def read_b01_content(meeting_path: Path) -> Optional[str]:
    """Read B01 content for entity detection."""
    for file in meeting_path.glob("B01*.md"):
        try:
            return file.read_text(encoding="utf-8")
        except Exception:
            pass
    return None


def check_entity_match(content: str, entity_filter: Optional[str] = None) -> List[Dict]:
    """Check if content mentions any watched entities."""
    matches = []
    content_lower = content.lower()
    
    for entity in WATCHED_ENTITIES:
        if entity_filter and entity_filter.lower() not in entity["name"].lower():
            continue
        
        for alias in entity["aliases"]:
            if alias in content_lower:
                matches.append(entity)
                break
    
    return matches


def check_acquisition_signals(content: str) -> List[str]:
    """Check for acquisition-related keywords."""
    content_lower = content.lower()
    found = []
    
    for keyword in ACQUISITION_KEYWORDS:
        if keyword.lower() in content_lower:
            found.append(keyword)
    
    return found


def scan_meeting_folder(meeting_path: Path, entity_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Scan a single meeting folder for acquisition signals."""
    folder_name = meeting_path.name
    
    # Extract date
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", folder_name)
    meeting_date = date_match.group(1) if date_match else None
    
    # Read B01 content
    b01_content = read_b01_content(meeting_path)
    if not b01_content:
        return None
    
    # Check for entity matches
    matched_entities = check_entity_match(b01_content, entity_filter)
    
    # Check for acquisition signals
    signals = check_acquisition_signals(b01_content)
    
    # Calculate relevance score
    if matched_entities and len(signals) >= 2:
        relevance = "HIGH"
    elif matched_entities:
        relevance = "MEDIUM"
    elif len(signals) >= 3:
        relevance = "LOW"
    else:
        return None
    
    # Check manifest for state
    manifest_path = meeting_path / "manifest.json"
    state = "unknown"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            state = manifest.get("status", "unknown")
        except Exception:
            pass
    
    return {
        "folder_name": folder_name,
        "path": str(meeting_path),
        "date": meeting_date,
        "matched_entities": [e["name"] for e in matched_entities],
        "signals": signals[:5],  # Limit to top 5 signals
        "relevance": relevance,
        "state": state,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan for acquisition-related meetings")
    parser.add_argument("--weeks", type=int, default=2, help="Weeks to look back (default: 2)")
    parser.add_argument("--all", action="store_true", help="Scan all meetings")
    parser.add_argument("--entity", help="Filter by entity name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    logger.info(f"Scanning meetings (weeks={args.weeks}, all={args.all})")
    
    week_folders = get_week_folders(weeks_back=args.weeks, scan_all=args.all)
    logger.info(f"Found {len(week_folders)} week folders to scan")
    
    results = []
    total_meetings = 0
    
    for week_folder in week_folders:
        for meeting_path in week_folder.iterdir():
            if not meeting_path.is_dir():
                continue
            total_meetings += 1
            
            result = scan_meeting_folder(meeting_path, args.entity)
            if result:
                results.append(result)
    
    # Also scan _quarantine
    quarantine = Path(MEETINGS_DIR) / "_quarantine"
    if quarantine.exists():
        for meeting_path in quarantine.iterdir():
            if not meeting_path.is_dir():
                continue
            total_meetings += 1
            result = scan_meeting_folder(meeting_path, args.entity)
            if result:
                results.append(result)
    
    logger.info(f"Scanned {total_meetings} meetings, found {len(results)} with acquisition signals")
    
    # Sort by relevance and date
    relevance_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    results.sort(key=lambda x: (relevance_order.get(x["relevance"], 3), x.get("date", "") or ""))
    results.reverse()  # Most recent first within each relevance tier
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n=== ACQUISITION DEAL CANDIDATES ===\n")
        
        high = [r for r in results if r["relevance"] == "HIGH"]
        medium = [r for r in results if r["relevance"] == "MEDIUM"]
        low = [r for r in results if r["relevance"] == "LOW"]
        
        if high:
            print("🔴 HIGH RELEVANCE (Entity + Signals)")
            print("-" * 60)
            for r in high:
                print(f"  [{r['date']}] {r['folder_name']}")
                print(f"      Entities: {', '.join(r['matched_entities'])}")
                print(f"      Signals: {', '.join(r['signals'][:3])}")
                print()
        
        if medium:
            print("🟡 MEDIUM RELEVANCE (Entity Match)")
            print("-" * 60)
            for r in medium:
                print(f"  [{r['date']}] {r['folder_name']}")
                print(f"      Entities: {', '.join(r['matched_entities'])}")
                print()
        
        if low:
            print("⚪ LOW RELEVANCE (Signals Only)")
            print("-" * 60)
            for r in low[:5]:  # Limit low relevance to top 5
                print(f"  [{r['date']}] {r['folder_name']}")
                print(f"      Signals: {', '.join(r['signals'][:3])}")
                print()
        
        print(f"\nTotal: {len(results)} meetings with acquisition signals out of {total_meetings} scanned")
        
        # Provide next steps
        if high or medium:
            print("\n=== NEXT STEPS ===")
            print("To sync a meeting to Airtable, run:")
            if high:
                example = high[0]["folder_name"]
            else:
                example = medium[0]["folder_name"]
            print(f'  python3 N5/scripts/airtable_deal_sync.py --meeting-folder "{example}"')


if __name__ == "__main__":
    main()


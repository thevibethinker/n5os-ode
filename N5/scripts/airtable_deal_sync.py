#!/usr/bin/env python3
"""
Airtable Deal Sync - Process a single meeting folder and sync to Airtable.

This script:
1. Reads B-blocks from a meeting folder
2. Extracts acquisition-relevant intelligence
3. Appends to the deal's Intelligence Summary field
4. Logs the meeting in the Audit Trail

Usage:
    python3 airtable_deal_sync.py --meeting-folder "2025-12-22_Christine-Song-Ribbon-Partnership-Sync"
    python3 airtable_deal_sync.py --meeting-path "/home/workspace/Personal/Meetings/Week-of-2025-12-22/2025-12-22_Christine-Song-Ribbon-Partnership-Sync"
    python3 airtable_deal_sync.py --meeting-folder "..." --deal "Ribbon"  # Explicit deal association
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Import config
sys.path.insert(0, str(Path(__file__).parent))
from airtable_config import (
    WATCHED_ENTITIES,
    ACQUISITION_KEYWORDS,
    BLOCK_MAPPING,
    MEETINGS_DIR,
    AIRTABLE_BASE_ID,
    TABLES,
    DEAL_FIELDS,
    AUDIT_FIELDS,
)


def find_meeting_folder(meeting_ref: str) -> Optional[Path]:
    """Find a meeting folder by name or path."""
    if Path(meeting_ref).is_absolute() and Path(meeting_ref).exists():
        return Path(meeting_ref)
    
    meetings_root = Path(MEETINGS_DIR)
    
    # Search in week folders
    for week_dir in meetings_root.glob("Week-of-*"):
        candidate = week_dir / meeting_ref
        if candidate.exists():
            return candidate
        # Try partial match
        for folder in week_dir.iterdir():
            if meeting_ref in folder.name:
                return folder
    
    # Search in Inbox
    inbox = meetings_root / "Inbox"
    if inbox.exists():
        candidate = inbox / meeting_ref
        if candidate.exists():
            return candidate
    
    # Search in _quarantine
    quarantine = meetings_root / "_quarantine"
    if quarantine.exists():
        candidate = quarantine / meeting_ref
        if candidate.exists():
            return candidate
    
    return None


def read_block(meeting_path: Path, block_prefix: str) -> Optional[str]:
    """Read a B-block file from the meeting folder."""
    for file in meeting_path.glob(f"{block_prefix}*.md"):
        try:
            content = file.read_text(encoding="utf-8")
            # Strip YAML frontmatter if present (may have multiple --- blocks)
            while content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
                else:
                    break
            return content
        except Exception as e:
            logger.warning(f"Failed to read {file}: {e}")
    return None


def detect_entity_match(content: str) -> List[Dict]:
    """Detect which watched entities are mentioned in the content."""
    matches = []
    content_lower = content.lower()
    
    for entity in WATCHED_ENTITIES:
        for alias in entity["aliases"]:
            if alias in content_lower:
                matches.append(entity)
                break
    
    return matches


def detect_acquisition_signals(content: str) -> Tuple[bool, List[str]]:
    """Detect acquisition-related keywords in content."""
    content_lower = content.lower()
    found_keywords = []
    
    for keyword in ACQUISITION_KEYWORDS:
        if keyword.lower() in content_lower:
            found_keywords.append(keyword)
    
    return len(found_keywords) >= 2, found_keywords


def extract_meeting_intelligence(meeting_path: Path) -> Dict[str, Any]:
    """Extract intelligence from B-blocks in the meeting folder."""
    intelligence = {
        "date": None,
        "title": None,
        "strategic_recap": None,
        "stakeholder_map": None,
        "risks_opportunities": None,
        "key_moments": None,
        "deliverables": None,
        "raw_content": "",
    }
    
    # Try to get date and title from folder name
    folder_name = meeting_path.name
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", folder_name)
    if date_match:
        intelligence["date"] = date_match.group(1)
    
    # Parse title from folder name (after date)
    title_part = re.sub(r"^\d{4}-\d{2}-\d{2}_?", "", folder_name)
    title_part = re.sub(r"_\[[MP]\]$", "", title_part)  # Remove state suffix
    intelligence["title"] = title_part.replace("-", " ").replace("_", " ").strip()
    
    # Read manifest for more accurate title
    manifest_path = meeting_path / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if "meeting_title" in manifest:
                intelligence["title"] = manifest["meeting_title"]
        except Exception as e:
            logger.warning(f"Failed to read manifest: {e}")
    
    # Read B-blocks
    b01 = read_block(meeting_path, "B01")
    if b01:
        intelligence["strategic_recap"] = b01
        intelligence["raw_content"] += b01 + "\n"
    
    b08 = read_block(meeting_path, "B08")
    if b08:
        intelligence["stakeholder_map"] = b08
        intelligence["raw_content"] += b08 + "\n"
    
    b13 = read_block(meeting_path, "B13")
    if b13:
        intelligence["risks_opportunities"] = b13
        intelligence["raw_content"] += b13 + "\n"
    
    b21 = read_block(meeting_path, "B21")
    if b21:
        intelligence["key_moments"] = b21
        intelligence["raw_content"] += b21 + "\n"
    
    b25 = read_block(meeting_path, "B25")
    if b25:
        intelligence["deliverables"] = b25
        intelligence["raw_content"] += b25 + "\n"
    
    return intelligence


def format_append_entry(intel: Dict[str, Any]) -> str:
    """Format intelligence as an append-only entry."""
    date = intel.get("date", datetime.now().strftime("%Y-%m-%d"))
    title = intel.get("title", "Unknown Meeting")
    
    entry = f"\n\n---\n## [{date}] {title}\n\n"
    
    if intel.get("strategic_recap"):
        # Extract just the key points from B01
        recap = intel["strategic_recap"]
        # Take first 500 chars or first section
        if len(recap) > 800:
            # Try to find a natural break point
            break_points = ["\n##", "\n###", "\n\n"]
            for bp in break_points:
                idx = recap.find(bp, 300)
                if idx > 0 and idx < 800:
                    recap = recap[:idx] + "\n..."
                    break
            else:
                recap = recap[:800] + "..."
        entry += f"### Strategic Insights\n{recap}\n\n"
    
    if intel.get("key_moments"):
        moments = intel["key_moments"]
        # Take first 400 chars
        if len(moments) > 400:
            moments = moments[:400] + "..."
        entry += f"### Key Moments\n{moments}\n\n"
    
    if intel.get("deliverables"):
        deliverables = intel["deliverables"]
        if len(deliverables) > 300:
            deliverables = deliverables[:300] + "..."
        entry += f"### Next Steps\n{deliverables}\n"
    
    return entry.strip()


def main():
    parser = argparse.ArgumentParser(description="Sync meeting intelligence to Airtable deal")
    parser.add_argument("--meeting-folder", help="Meeting folder name")
    parser.add_argument("--meeting-path", help="Full path to meeting folder")
    parser.add_argument("--deal", help="Explicit deal name (Ribbon, Teamwork Online, FutureFit)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without actually syncing")
    args = parser.parse_args()
    
    # Find meeting folder
    meeting_ref = args.meeting_path or args.meeting_folder
    if not meeting_ref:
        logger.error("Must provide --meeting-folder or --meeting-path")
        sys.exit(1)
    
    meeting_path = find_meeting_folder(meeting_ref)
    if not meeting_path:
        logger.error(f"Could not find meeting folder: {meeting_ref}")
        sys.exit(1)
    
    logger.info(f"Processing meeting: {meeting_path}")
    
    # Extract intelligence
    intel = extract_meeting_intelligence(meeting_path)
    logger.info(f"Extracted intelligence from {meeting_path.name}")
    logger.info(f"  Date: {intel['date']}")
    logger.info(f"  Title: {intel['title']}")
    logger.info(f"  B01 (recap): {'✓' if intel['strategic_recap'] else '✗'}")
    logger.info(f"  B08 (stakeholders): {'✓' if intel['stakeholder_map'] else '✗'}")
    logger.info(f"  B13 (risks/opps): {'✓' if intel['risks_opportunities'] else '✗'}")
    logger.info(f"  B21 (key moments): {'✓' if intel['key_moments'] else '✗'}")
    logger.info(f"  B25 (deliverables): {'✓' if intel['deliverables'] else '✗'}")
    
    # Detect which deal this belongs to
    if args.deal:
        # Explicit deal specified
        target_entity = None
        for entity in WATCHED_ENTITIES:
            if args.deal.lower() in entity["name"].lower():
                target_entity = entity
                break
        if not target_entity:
            logger.error(f"Unknown deal: {args.deal}")
            sys.exit(1)
        matched_entities = [target_entity]
        logger.info(f"Explicit deal specified: {target_entity['name']}")
    else:
        # Auto-detect from content
        matched_entities = detect_entity_match(intel["raw_content"])
        if matched_entities:
            logger.info(f"Detected entities: {[e['name'] for e in matched_entities]}")
        else:
            logger.warning("No watched entities detected in meeting content")
    
    # Check for acquisition signals
    has_signals, keywords = detect_acquisition_signals(intel["raw_content"])
    if keywords:
        logger.info(f"Acquisition signals found: {keywords[:5]}")
    
    # Determine confidence
    if matched_entities and has_signals:
        confidence = "HIGH"
    elif matched_entities:
        confidence = "MEDIUM"
    elif has_signals:
        confidence = "LOW"
    else:
        confidence = "NONE"
    
    logger.info(f"Confidence level: {confidence}")
    
    if confidence == "NONE":
        logger.info("No acquisition signals detected. Skipping sync.")
        return
    
    if confidence == "LOW":
        logger.warning("Low confidence - acquisition signals found but no entity match.")
        logger.warning("Consider running with --deal to specify the target deal.")
        if not args.deal:
            return
    
    # Format the append entry
    append_entry = format_append_entry(intel)
    
    if args.dry_run:
        logger.info("=== DRY RUN - Would append to deal ===")
        logger.info(f"Target deal(s): {[e['name'] for e in matched_entities]}")
        logger.info(f"Meeting ID: {meeting_path.name}")
        logger.info("Append content:")
        print(append_entry)
        return
    
    # Output the sync data for the calling process (Zo) to execute via use_app_airtable
    sync_data = {
        "meeting_id": meeting_path.name,
        "meeting_title": intel["title"],
        "meeting_date": intel["date"],
        "matched_entities": [e["name"] for e in matched_entities],
        "deal_record_ids": [e["deal_record_id"] for e in matched_entities],
        "confidence": confidence,
        "append_content": append_entry,
        "blocks_found": {
            "B01": bool(intel["strategic_recap"]),
            "B08": bool(intel["stakeholder_map"]),
            "B13": bool(intel["risks_opportunities"]),
            "B21": bool(intel["key_moments"]),
            "B25": bool(intel["deliverables"]),
        }
    }
    
    # Write sync data to stdout as JSON for Zo to process
    print("=== SYNC_DATA_START ===")
    print(json.dumps(sync_data, indent=2))
    print("=== SYNC_DATA_END ===")
    
    logger.info("Sync data prepared. Zo will execute Airtable update.")


if __name__ == "__main__":
    main()



#!/usr/bin/env python3
"""
Airtable Deal Sync v2 - Context-Aware Progression Tracking

This script:
1. Reads current deal state from Airtable BEFORE updating
2. Extracts intelligence from meeting B-blocks
3. Compares new meeting to previous state
4. Calculates momentum and deal health
5. Outputs structured sync data for Zo to execute

Key difference from v1: Context-aware. Knows what happened before.
"""

import argparse
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

# B-blocks to extract and their target fields
BLOCK_MAPPING = {
    "B01": {"field": "intelligence", "label": "Strategic Insights"},
    "B05": {"field": "action_items", "label": "Action Items"},
    "B08": {"field": "stakeholders", "label": "Stakeholders"},
    "B13": {"field": "risks_opps", "label": "Risks & Opportunities"},
    "B21": {"field": "key_moments", "label": "Key Moments"},
    "B25": {"field": "deliverables", "label": "Deliverables & Next Steps"},
}


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return content


def read_block(meeting_path: Path, block_prefix: str) -> Optional[str]:
    """Read a B-block file and return its content (without frontmatter)."""
    block_files = list(meeting_path.glob(f"{block_prefix}*.md"))
    if not block_files:
        return None
    
    content = block_files[0].read_text(encoding="utf-8", errors="ignore")
    return strip_frontmatter(content)


def extract_action_items(content: str) -> Tuple[List[str], List[str]]:
    """Extract open and completed action items from B05 content."""
    open_items = []
    completed_items = []
    
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- [ ]"):
            open_items.append(line[5:].strip())
        elif line.startswith("- [x]") or line.startswith("- [X]"):
            completed_items.append(line[5:].strip())
    
    return open_items, completed_items


def extract_meeting_date(folder_name: str) -> str:
    """Extract date from meeting folder name."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", folder_name)
    return match.group(1) if match else datetime.now().strftime("%Y-%m-%d")


def extract_meeting_title(folder_name: str) -> str:
    """Extract human-readable title from folder name."""
    # Remove date prefix and state suffix
    title = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", folder_name)
    title = re.sub(r"_\[[A-Z]\]$", "", title)
    # Replace hyphens with spaces, capitalize
    title = title.replace("-", " ").replace("_", " ")
    return title.title()


def calculate_momentum(
    last_meeting_date: Optional[str],
    current_meeting_date: str,
    previous_open_items: int,
    current_open_items: int,
    meetings_in_last_2_weeks: int
) -> str:
    """Calculate deal momentum based on activity patterns."""
    
    if not last_meeting_date:
        return "Steady"  # First meeting, can't calculate yet
    
    # Parse dates
    try:
        last_date = datetime.strptime(last_meeting_date, "%Y-%m-%d")
        current_date = datetime.strptime(current_meeting_date, "%Y-%m-%d")
        days_gap = (current_date - last_date).days
    except ValueError:
        return "Steady"
    
    # Momentum logic
    if days_gap <= 7 and meetings_in_last_2_weeks >= 2:
        return "Accelerating"
    elif days_gap <= 14:
        return "Steady"
    elif days_gap <= 21:
        return "Stalling"
    else:
        return "Stalled"


def calculate_deal_health(
    momentum: str,
    open_items_count: int,
    has_blockers: bool
) -> str:
    """Calculate overall deal health."""
    
    if momentum in ["Accelerating", "Steady"] and not has_blockers:
        return "🟢 Healthy"
    elif momentum == "Stalling" or (has_blockers and open_items_count > 3):
        return "🟡 Needs Attention"
    elif momentum == "Stalled" or (has_blockers and open_items_count > 5):
        return "🔴 At Risk"
    else:
        return "🟢 Healthy"


def process_meeting(
    meeting_path: Path,
    previous_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a meeting folder and generate sync data with context awareness."""
    
    folder_name = meeting_path.name
    meeting_date = extract_meeting_date(folder_name)
    meeting_title = extract_meeting_title(folder_name)
    
    # Extract all B-blocks
    extracted = {}
    blocks_found = {}
    
    for block_prefix, config in BLOCK_MAPPING.items():
        content = read_block(meeting_path, block_prefix)
        if content:
            extracted[config["field"]] = content
            blocks_found[block_prefix] = True
        else:
            blocks_found[block_prefix] = False
    
    # Extract action items specifically
    open_items = []
    completed_items = []
    if "action_items" in extracted:
        open_items, completed_items = extract_action_items(extracted["action_items"])
    
    # Check for blockers in risks content
    has_blockers = False
    blockers_text = ""
    if "risks_opps" in extracted:
        risks_content = extracted["risks_opps"].lower()
        if any(word in risks_content for word in ["blocker", "risk", "concern", "obstacle", "delay"]):
            has_blockers = True
            # Extract blocker lines
            for line in extracted["risks_opps"].split("\n"):
                if any(word in line.lower() for word in ["blocker", "risk", "concern"]):
                    blockers_text += line + "\n"
    
    # Context-aware calculations
    previous_date = previous_state.get("last_meeting_date") if previous_state else None
    previous_open_count = previous_state.get("open_items_count", 0) if previous_state else 0
    meeting_count = (previous_state.get("meeting_count", 0) if previous_state else 0) + 1
    
    # For now, assume this is the only meeting in last 2 weeks (agent will track properly)
    meetings_in_2_weeks = 1
    
    momentum = calculate_momentum(
        previous_date,
        meeting_date,
        previous_open_count,
        len(open_items),
        meetings_in_2_weeks
    )
    
    deal_health = calculate_deal_health(momentum, len(open_items), has_blockers)
    
    # Build append content for Intelligence Summary
    append_content = f"\n---\n## [{meeting_date}] {meeting_title}\n\n"
    
    if "intelligence" in extracted:
        # Extract key insights (first 500 chars or first section)
        intel_preview = extracted["intelligence"][:800]
        append_content += f"### Strategic Insights\n{intel_preview}\n\n"
    
    if "key_moments" in extracted:
        append_content += f"### Key Moments\n{extracted['key_moments'][:500]}\n\n"
    
    if "deliverables" in extracted:
        append_content += f"### Next Steps\n{extracted['deliverables'][:400]}\n\n"
    
    if open_items:
        append_content += "### Open Action Items\n"
        for item in open_items[:5]:
            append_content += f"- [ ] {item}\n"
        append_content += "\n"
    
    if blockers_text:
        append_content += f"### Blockers\n{blockers_text}\n"
    
    return {
        "meeting_id": folder_name,
        "meeting_title": meeting_title,
        "meeting_date": meeting_date,
        "meeting_path": str(meeting_path),
        
        # Append content for Intelligence Summary
        "append_content": append_content.strip(),
        
        # Progression fields
        "last_meeting_date": meeting_date,
        "meeting_count": meeting_count,
        "momentum": momentum,
        "deal_health": deal_health,
        
        # Structured data
        "open_action_items": open_items,
        "completed_action_items": completed_items,
        "has_blockers": has_blockers,
        "blockers": blockers_text.strip() if blockers_text else None,
        
        # Next steps from B25
        "next_steps": extracted.get("deliverables", "")[:500] if "deliverables" in extracted else None,
        
        # Metadata
        "blocks_found": blocks_found,
        "context_aware": previous_state is not None,
    }


def main():
    parser = argparse.ArgumentParser(description="Context-aware deal sync")
    parser.add_argument("--meeting-folder", required=True, help="Meeting folder name")
    parser.add_argument("--meeting-path", help="Full path to meeting (overrides folder search)")
    parser.add_argument("--previous-state", help="JSON string of previous deal state")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")
    args = parser.parse_args()
    
    # Find meeting path
    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
    else:
        # Search in recent weeks
        meeting_path = None
        for week_folder in sorted(MEETINGS_DIR.glob("Week-of-*"), reverse=True)[:8]:
            for folder in week_folder.iterdir():
                if args.meeting_folder in folder.name:
                    meeting_path = folder
                    break
            if meeting_path:
                break
        
        # Also check quarantine
        if not meeting_path:
            quarantine = MEETINGS_DIR / "_quarantine"
            if quarantine.exists():
                for folder in quarantine.iterdir():
                    if args.meeting_folder in folder.name:
                        meeting_path = folder
                        break
    
    if not meeting_path or not meeting_path.exists():
        logger.error(f"Meeting not found: {args.meeting_folder}")
        return
    
    logger.info(f"Processing meeting: {meeting_path}")
    
    # Parse previous state if provided
    previous_state = None
    if args.previous_state:
        try:
            previous_state = json.loads(args.previous_state)
            logger.info("Using previous deal state for context-aware analysis")
        except json.JSONDecodeError:
            logger.warning("Could not parse previous state, proceeding without context")
    
    # Process meeting
    sync_data = process_meeting(meeting_path, previous_state)
    
    if args.dry_run:
        logger.info("=== DRY RUN - Would sync the following ===")
        print(f"\nMeeting: {sync_data['meeting_title']} ({sync_data['meeting_date']})")
        print(f"Momentum: {sync_data['momentum']}")
        print(f"Deal Health: {sync_data['deal_health']}")
        print(f"Open Items: {len(sync_data['open_action_items'])}")
        print(f"Has Blockers: {sync_data['has_blockers']}")
        print(f"\n--- Append Content Preview ---")
        print(sync_data['append_content'][:1000])
        return
    
    # Output structured JSON for Zo to process
    print("=== SYNC_DATA_START ===")
    print(json.dumps(sync_data, indent=2))
    print("=== SYNC_DATA_END ===")
    
    logger.info("Context-aware sync data prepared. Zo will execute Airtable update.")


if __name__ == "__main__":
    main()


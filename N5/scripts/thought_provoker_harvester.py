#!/usr/bin/env python3
"""
Thought Provoker Harvester

Scans Personal/Meetings/ for B32_THOUGHT_PROVOKING_IDEAS.md blocks
and aggregates them into a central collection file.

Usage:
    python3 thought_provoker_harvester.py [--output path/to/collection.md]
"""

import os
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
DEFAULT_OUTPUT = Path("/home/workspace/Knowledge/reflections/thought_provoker_collection.md")

class ThoughtProvokerHarvester:
    def __init__(self, output_path: Path = DEFAULT_OUTPUT):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def find_b32_blocks(self) -> List[Path]:
        """Find all B32 blocks in the meetings root."""
        return list(MEETINGS_ROOT.rglob("B32_THOUGHT_PROVOKING_IDEAS.md"))

    def parse_block(self, path: Path) -> Dict[str, Any]:
        """Parse the B32 block content."""
        content = path.read_text()
        meeting_folder = path.parent.name
        
        # Extract meeting date from folder name (YYYY-MM-DD)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", meeting_folder)
        date = date_match.group(1) if date_match else "Unknown Date"
        
        # Extract meeting title (everything after the date)
        title = meeting_folder
        if date_match:
            title = meeting_folder[date_match.end():].strip("_ ")
            title = title.replace("_", " ").title()

        return {
            "date": date,
            "meeting_id": meeting_folder,
            "meeting_title": title,
            "content": content,
            "path": str(path)
        }

    def load_existing_ids(self) -> set:
        """Load IDs of meetings already in the collection."""
        if not self.output_path.exists():
            return set()
        
        content = self.output_path.read_text()
        # Look for meeting IDs in comments or specific headers
        # We'll use a hidden marker in the collection file
        ids = set(re.findall(r"<!-- ID: (.*?) -->", content))
        return ids

    def harvest(self):
        """Perform the harvesting and update the collection."""
        blocks = self.find_b32_blocks()
        existing_ids = self.load_existing_ids()
        
        new_entries = []
        for block_path in blocks:
            meeting_id = block_path.parent.name
            if meeting_id not in existing_ids:
                logger.info(f"New B32 found: {meeting_id}")
                new_entries.append(self.parse_block(block_path))
        
        if not new_entries:
            logger.info("No new B32 entries to harvest.")
            return

        # Sort by date
        new_entries.sort(key=lambda x: x["date"], reverse=True)
        
        self.update_collection(new_entries)

    def update_collection(self, new_entries: List[Dict]):
        """Update the central collection file with new entries."""
        if not self.output_path.exists():
            header = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
last_edited: {datetime.now().strftime("%Y-%m-%d")}
version: 1.0
type: collection
provenance: thought-provoker-harvester
---

# Collection of Thought-Provoking Ideas

This is a living repository of "spark moments," strategic weirdness, and provocative challenges extracted from V's meetings.

---
"""
        else:
            header = "" # Header already exists
            
        new_content = []
        for entry in new_entries:
            entry_md = f"""
## {entry['date']} — {entry['meeting_title']}
<!-- ID: {entry['meeting_id']} -->
{entry['content']}

---
"""
            new_content.append(entry_md)

        if not self.output_path.exists():
            final_content = header + "\n".join(new_content)
        else:
            # Insert after the header (after the second ---)
            existing_content = self.output_path.read_text()
            parts = existing_content.split("---", 2)
            if len(parts) >= 3:
                # Reconstruct with new entries at the top of the list (after the descriptive intro)
                # Find the end of the intro
                intro_end = existing_content.find("---", existing_content.find("# Collection"))
                if intro_end != -1:
                    pre_content = existing_content[:intro_end + 3]
                    post_content = existing_content[intro_end + 3:]
                    final_content = pre_content + "\n" + "\n".join(new_content) + post_content
                else:
                    final_content = existing_content + "\n" + "\n".join(new_content)
            else:
                final_content = existing_content + "\n" + "\n".join(new_content)

        # Update last_edited date
        final_content = re.sub(r"last_edited: \d{4}-\d{2}-\d{2}", f'last_edited: {datetime.now().strftime("%Y-%m-%d")}', final_content)

        self.output_path.write_text(final_content)
        logger.info(f"Harvested {len(new_entries)} entries into {self.output_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Thought Provoker Harvester")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to collection file")
    args = parser.parse_args()

    harvester = ThoughtProvokerHarvester(output_path=args.output)
    harvester.harvest()

if __name__ == "__main__":
    main()


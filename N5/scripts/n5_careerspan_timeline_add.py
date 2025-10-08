#!/usr/bin/env python3
"""
N5 Careerspan Timeline Add - Add new entry to Careerspan company and personal timeline
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Optional


class CareerspanTimelineAdder:
    def __init__(self, timeline_path: str = "/home/workspace/N5/knowledge/careerspan-timeline.md"):
        self.timeline_path = Path(timeline_path)
        # Ensure file exists
        if not self.timeline_path.exists():
            self._create_initial_file()
    
    def _create_initial_file(self):
        """Create initial timeline file with frontmatter"""
        from datetime import datetime
        initial_content = f"""---
date: '{datetime.utcnow().isoformat()}Z'
last-tested: '{datetime.utcnow().isoformat()}Z'
generated_date: '{datetime.utcnow().isoformat()}Z'
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/knowledge/careerspan-timeline.md
---
# Careerspan Timeline

"""
        self.timeline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.timeline_path, 'w') as f:
            f.write(initial_content)
    
    def add_entry(self, year: str, title: str, description: str, 
                  category: Optional[str] = None, tags: Optional[str] = None) -> bool:
        """Add entry to timeline file"""
        try:
            # Read existing content
            with open(self.timeline_path, 'r') as f:
                content = f.read()
            
            # Create new entry
            entry_lines = []
            entry_lines.append(f"## {year}: {title}")
            if category:
                entry_lines.append(f"**Category:** {category}")
            entry_lines.append(description)
            if tags:
                entry_lines.append(f"\n**Tags:** {tags}")
            entry_lines.append("")  # Blank line
            
            entry_text = "\n".join(entry_lines)
            
            # Append to file
            with open(self.timeline_path, 'a') as f:
                f.write("\n" + entry_text)
            
            return True
        except Exception as e:
            print(f"Error writing to timeline: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(description="Add entry to Careerspan company and personal timeline")
    parser.add_argument("--year", required=True, help="Year or date of the event")
    parser.add_argument("--title", required=True, help="Brief title of the event/milestone")
    parser.add_argument("--description", required=True, help="Detailed description")
    parser.add_argument("--category", choices=["company", "personal", "milestone"], help="Type of event")
    parser.add_argument("--tags", help="Additional tags (comma-separated)")
    
    args = parser.parse_args()
    
    adder = CareerspanTimelineAdder()
    
    # Add entry
    success = adder.add_entry(
        year=args.year,
        title=args.title,
        description=args.description,
        category=args.category,
        tags=args.tags
    )
    
    if success:
        print(f"✓ Added timeline entry: {args.title}")
        print(f"  Year: {args.year}")
        if args.category:
            print(f"  Category: {args.category}")
        
        # Output metadata for N5 integration
        print(f"\n--N5-OUTPUT--")
        print(json.dumps({
            "success": True,
            "path": str(adder.timeline_path),
            "title": args.title,
            "year": args.year
        }))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

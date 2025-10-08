#!/usr/bin/env python3
"""
N5 Careerspan Timeline - View and search Careerspan company and personal timeline
"""

import json
import argparse
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional


class CareerspanTimelineViewer:
    def __init__(self, timeline_path: str = "/home/workspace/Knowledge/careerspan-timeline.md"):
        self.timeline_path = Path(timeline_path)
        self.entries = []
        self.load_entries()
    
    def load_entries(self):
        """Load all timeline entries from markdown file"""
        if not self.timeline_path.exists():
            return
        
        try:
            with open(self.timeline_path, 'r') as f:
                content = f.read()
            
            # Skip frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2]
            
            # Parse markdown sections (## Year: Title format)
            pattern = r'##\s+([^:\n]+):\s+([^\n]+)\n(.+?)(?=##\s+|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for year, title, description in matches:
                self.entries.append({
                    "year": year.strip(),
                    "title": title.strip(),
                    "description": description.strip(),
                    "category": self._infer_category(title, description)
                })
        
        except Exception as e:
            print(f"Error loading timeline: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _infer_category(self, title: str, description: str) -> str:
        """Infer category from title and description"""
        text = (title + " " + description).lower()
        if any(word in text for word in ["funding", "launch", "rebrand", "pivot", "partnership", "pilot"]):
            return "company"
        elif any(word in text for word in ["personal", "life", "achievement"]):
            return "personal"
        return "milestone"
    
    def filter_entries(self, year: Optional[str] = None, 
                      category: Optional[str] = None,
                      limit: Optional[int] = None) -> List[Dict]:
        """Filter timeline entries based on criteria"""
        filtered = self.entries
        
        # Filter by year
        if year:
            filtered = [e for e in filtered if year in e.get('year', '')]
        
        # Filter by category
        if category:
            filtered = [e for e in filtered if e.get('category') == category]
        
        # Apply limit
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def format_markdown(self, entries: List[Dict]) -> str:
        """Format entries as Markdown"""
        if not entries:
            return "No timeline entries found."
        
        output = []
        output.append("# Careerspan Company & Life Timeline")
        output.append("")
        
        for entry in entries:
            year = entry.get('year', 'Unknown')
            title = entry.get('title', 'Untitled')
            description = entry.get('description', '')
            category = entry.get('category', 'milestone')
            
            output.append(f"## {year}: {title}")
            output.append("")
            output.append(f"**Category:** {category}")
            output.append("")
            output.append(description)
            output.append("")
        
        return "\n".join(output)
    
    def format_json(self, entries: List[Dict]) -> str:
        """Format entries as JSON"""
        return json.dumps(entries, indent=2)


def main():
    parser = argparse.ArgumentParser(description="View Careerspan company and personal timeline")
    parser.add_argument("--year", help="Filter by year")
    parser.add_argument("--category", choices=["company", "personal", "milestone"], help="Filter by category")
    parser.add_argument("--limit", type=int, help="Number of entries to show")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    viewer = CareerspanTimelineViewer()
    filtered = viewer.filter_entries(
        year=args.year,
        category=args.category,
        limit=args.limit
    )
    
    if args.format == "json":
        print(viewer.format_json(filtered))
    else:
        print(viewer.format_markdown(filtered))
    
    # Output metadata for N5 integration
    print(f"\n--N5-OUTPUT--")
    print(json.dumps({
        "entries": filtered,
        "count": len(filtered)
    }))


if __name__ == "__main__":
    main()

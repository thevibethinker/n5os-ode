#!/usr/bin/env python3
"""
N5 System Timeline Management - View and search N5 OS development timeline entries
"""

import json
import argparse
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional


class TimelineViewer:
    def __init__(self, timeline_path: str = "/home/workspace/N5/timeline/system-timeline.jsonl"):
        self.timeline_path = Path(timeline_path)
        self.entries = []
        self.load_entries()
    
    def load_entries(self):
        """Load all timeline entries from JSONL file"""
        if not self.timeline_path.exists():
            return
        
        try:
            with open(self.timeline_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            self.entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error loading timeline: {e}", file=sys.stderr)
            sys.exit(1)
    
    def filter_entries(self, category: Optional[str] = None, 
                      from_date: Optional[str] = None,
                      to_date: Optional[str] = None,
                      limit: int = 20) -> List[Dict]:
        """Filter timeline entries based on criteria"""
        filtered = self.entries
        
        # Filter by category
        if category:
            filtered = [e for e in filtered if e.get('category') == category]
        
        # Filter by date range
        if from_date:
            try:
                from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                filtered = [e for e in filtered if datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) >= from_dt]
            except (ValueError, AttributeError):
                pass
        
        if to_date:
            try:
                to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                filtered = [e for e in filtered if datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) <= to_dt]
            except (ValueError, AttributeError):
                pass
        
        # Sort by timestamp (newest first) and limit
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return filtered[:limit]
    
    def format_table(self, entries: List[Dict]) -> str:
        """Format entries as a table"""
        if not entries:
            return "No timeline entries found."
        
        output = []
        output.append("N5 OS System Development Timeline")
        output.append("=" * 80)
        output.append("")
        
        for entry in entries:
            timestamp = entry.get('timestamp', 'N/A')[:10]  # Just date
            category = entry.get('category', 'unknown')
            version = entry.get('version', 'N/A')
            title = entry.get('title', 'Untitled')
            impact = entry.get('impact', 'medium')
            status = entry.get('status', 'completed')
            
            # Color coding for impact (using ANSI codes)
            impact_color = {"low": "\033[32m", "medium": "\033[33m", "high": "\033[31m"}.get(impact, "")
            reset_color = "\033[0m"
            
            output.append(f"{timestamp} | {category:12} | v{version:8} | {impact_color}{impact:6}{reset_color} | {status:10} | {title}")
            
            # Show description if available
            description = entry.get('description', '')
            if description:
                # Wrap description to 60 chars
                words = description.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 60:
                        current_line += (" " + word if current_line else word)
                    else:
                        lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                for line in lines:
                    output.append(f"{' '*60} | {line}")
            
            output.append("")
        
        return "\n".join(output)
    
    def format_json(self, entries: List[Dict]) -> str:
        """Format entries as JSON"""
        return json.dumps(entries, indent=2)
    
    def format_markdown(self, entries: List[Dict]) -> str:
        """Format entries as Markdown"""
        if not entries:
            return "No timeline entries found."
        
        output = []
        output.append("# N5 OS System Development Timeline")
        output.append("")
        
        for entry in entries:
            timestamp = entry.get('timestamp', 'N/A')
            category = entry.get('category', 'unknown')
            version = entry.get('version', 'N/A')
            title = entry.get('title', 'Untitled')
            description = entry.get('description', '')
            impact = entry.get('impact', 'medium')
            status = entry.get('status', 'completed')
            components = entry.get('components', [])
            tags = entry.get('tags', [])
            
            output.append(f"## {title}")
            output.append("")
            output.append(f"**Date:** {timestamp} | **Version:** {version} | **Category:** {category}")
            output.append(f"**Impact:** {impact} | **Status:** {status}")
            
            if components:
                output.append(f"**Components:** {', '.join(components)}")
            
            if tags:
                output.append(f"**Tags:** {', '.join(tags)}")
            
            output.append("")
            output.append(description)
            output.append("")
            output.append("---")
            output.append("")
        
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="View N5 OS system development timeline")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--from", dest="from_date", help="Start date (ISO format)")
    parser.add_argument("--to", dest="to_date", help="End date (ISO format)")
    parser.add_argument("--limit", type=int, default=20, help="Number of entries to show")
    parser.add_argument("--format", choices=["table", "json", "markdown"], default="table", help="Output format")
    
    args = parser.parse_args()
    
    viewer = TimelineViewer()
    filtered = viewer.filter_entries(
        category=args.category,
        from_date=args.from_date,
        to_date=args.to_date,
        limit=args.limit
    )
    
    if args.format == "json":
        print(viewer.format_json(filtered))
    elif args.format == "markdown":
        print(viewer.format_markdown(filtered))
    else:
        print(viewer.format_table(filtered))
    
    # Output metadata for N5 integration
    print(f"\n--N5-OUTPUT--")
    print(json.dumps({
        "entries": filtered,
        "count": len(filtered)
    }))


if __name__ == "__main__":
    main()
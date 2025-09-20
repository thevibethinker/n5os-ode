#!/usr/bin/env python3
"""
N5 Timeline Add - Add new entry to development timeline
"""

import json
import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TimelineAdder:
    def __init__(self, timeline_path: str = "/home/workspace/N5/timeline/timeline.jsonl"):
        self.timeline_path = Path(timeline_path)
        # Ensure directory exists
        self.timeline_path.parent.mkdir(parents=True, exist_ok=True)
    
    def create_entry(self, title: str, description: str, category: str,
                    version: Optional[str] = None, components: Optional[List[str]] = None,
                    impact: str = "medium", status: str = "completed",
                    tags: Optional[List[str]] = None) -> Dict:
        """Create a new timeline entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry_id": str(uuid.uuid4()),
            "type": "manual" if not version else "versioned",
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "status": status
        }
        
        if version:
            entry["version"] = version
        
        if components:
            entry["components"] = components
        
        if tags:
            entry["tags"] = tags
        
        # Add author if available (would need to integrate with n5 user system)
        entry["author"] = "system"  # Could be enhanced with actual user detection
        
        return entry
    
    def add_entry(self, entry: Dict) -> bool:
        """Add entry to timeline file"""
        try:
            with open(self.timeline_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            return True
        except Exception as e:
            print(f"Error writing to timeline: {e}", file=sys.stderr)
            return False
    
    def parse_json_list(self, json_str: str) -> List[str]:
        """Parse JSON array string to list"""
        if not json_str:
            return []
        try:
            result = json.loads(json_str)
            if isinstance(result, list):
                return result
            return []
        except json.JSONDecodeError:
            # Try parsing as comma-separated string
            return [item.strip() for item in json_str.split(',') if item.strip()]


def main():
    parser = argparse.ArgumentParser(description="Add entry to n5.os development timeline")
    parser.add_argument("--title", required=True, help="Brief title of the change/feature")
    parser.add_argument("--description", required=True, help="Detailed description")
    parser.add_argument("--category", required=True, 
                       choices=["infrastructure", "feature", "command", "workflow", "ui", "integration", "fix"],
                       help="Type of change")
    parser.add_argument("--version", help="Version number (optional)")
    parser.add_argument("--components", help="Components affected (JSON array or comma-separated)")
    parser.add_argument("--impact", default="medium", 
                       choices=["low", "medium", "high"], help="Impact level")
    parser.add_argument("--status", default="completed",
                       choices=["planned", "in-progress", "completed"], help="Status")
    parser.add_argument("--tags", help="Additional tags (JSON array or comma-separated)")
    
    args = parser.parse_args()
    
    adder = TimelineAdder()
    
    # Parse components and tags
    components = adder.parse_json_list(args.components) if args.components else None
    tags = adder.parse_json_list(args.tags) if args.tags else None
    
    # Create entry
    entry = adder.create_entry(
        title=args.title,
        description=args.description,
        category=args.category,
        version=args.version,
        components=components,
        impact=args.impact,
        status=args.status,
        tags=tags
    )
    
    # Add to timeline
    success = adder.add_entry(entry)
    
    if success:
        print(f"✓ Added timeline entry: {entry['title']}")
        print(f"  Category: {entry['category']} | Impact: {entry['impact']} | Status: {entry['status']}")
        print(f"  Entry ID: {entry['entry_id']}")
        
        # Output metadata for N5 integration
        print(f"\n--N5-OUTPUT--")
        print(json.dumps({
            "entry_id": entry["entry_id"],
            "path": str(adder.timeline_path),
            "title": entry["title"],
            "timestamp": entry["timestamp"]
        }))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
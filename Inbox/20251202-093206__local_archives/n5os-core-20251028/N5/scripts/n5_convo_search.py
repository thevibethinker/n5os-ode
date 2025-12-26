#!/usr/bin/env python3
"""
Search conversations by text query

Usage:
    n5_convo_search.py "authentication" [--type build] [--limit 20]
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from conversation_registry import ConversationRegistry

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def format_timestamp(ts_str):
    """Format ISO timestamp to readable date"""
    if not ts_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return ts_str[:16]


def main():
    parser = argparse.ArgumentParser(description="Search conversations")
    parser.add_argument("query", help="Search query (searches focus/objective/tags)")
    parser.add_argument("--type", choices=["build", "research", "discussion", "planning", "content"])
    parser.add_argument("--status", choices=["active", "complete", "archived", "blocked"])
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    registry = ConversationRegistry()
    
    # Build filters
    filters = {}
    if args.type:
        filters["type"] = args.type
    if args.status:
        filters["status"] = args.status
    
    # Search
    conversations = registry.search(query=args.query, filters=filters, limit=args.limit)
    
    if not conversations:
        print(f"No conversations found matching '{args.query}'")
        return 0
    
    # Output
    if args.json:
        import json
        print(json.dumps(conversations, indent=2))
    else:
        # Table format
        print(f"\nFound {len(conversations)} conversation(s) matching '{args.query}':\n")
        print(f"{'ID':<20} {'Type':<12} {'Status':<10} {'Focus':<40} {'Updated':<17}")
        print("-" * 100)
        
        for convo in conversations:
            convo_id = convo["id"]
            type_str = convo.get("type", "?")
            status = convo.get("status", "?")
            focus = convo.get("focus", "N/A")[:38]
            updated = format_timestamp(convo.get("updated_at"))
            
            starred = "⭐" if convo.get("starred") else "  "
            
            print(f"{starred} {convo_id:<18} {type_str:<12} {status:<10} {focus:<40} {updated}")
        
        print()
    
    return 0


if __name__ == "__main__":
    exit(main())

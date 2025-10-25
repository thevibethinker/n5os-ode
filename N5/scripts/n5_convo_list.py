#!/usr/bin/env python3
"""
List conversations from registry with filtering

Usage:
    n5_convo_list.py [--type build|research] [--status active] [--starred] [--limit 20]
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
    parser = argparse.ArgumentParser(description="List conversations")
    parser.add_argument("--type", choices=["build", "research", "discussion", "planning", "content"])
    parser.add_argument("--status", choices=["active", "complete", "archived", "blocked"])
    parser.add_argument("--mode", choices=["standalone", "orchestrator", "worker"])
    parser.add_argument("--starred", action="store_true", help="Show only starred")
    parser.add_argument("--parent", help="Show workers for orchestrator ID")
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
    if args.mode:
        filters["mode"] = args.mode
    if args.starred:
        filters["starred"] = 1
    if args.parent:
        filters["parent_id"] = args.parent
    
    # Search
    conversations = registry.search(filters=filters, limit=args.limit)
    
    if not conversations:
        print("No conversations found")
        return 0
    
    # Output
    if args.json:
        import json
        print(json.dumps(conversations, indent=2))
    else:
        # Table format
        print(f"\nFound {len(conversations)} conversation(s):\n")
        print(f"ID                   Type         Status     Title                                    Updated          ")
        print("-" * 100)
        
        for convo in conversations:
            convo_id = convo["id"]
            type_str = convo["type"][:12]
            status = convo.get("status", "")[:10]
            title = convo.get("title", convo.get("focus", ""))[:40]
            updated = convo.get("updated_at", "")[:16]
            starred = "⭐" if convo.get("starred") else "  "
            
            print(f"{starred} {convo_id:<18} {type_str:<12} {status:<10} {title:<40} {updated}")
        
        print()
    
    return 0


if __name__ == "__main__":
    exit(main())

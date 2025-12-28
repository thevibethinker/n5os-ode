#!/usr/bin/env python3
"""
Get Allowlist Query
Generates a Gmail query for a specific allowlist type.

Usage:
  python3 get_allowlist_query.py events      # Event sources
  python3 get_allowlist_query.py newsletters # Newsletter sources
  python3 get_allowlist_query.py jobs        # Job sources
"""
import json
import sys
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "allowlists.json"

def main():
    allowlist_type = sys.argv[1] if len(sys.argv) > 1 else "events"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    if not CONFIG_FILE.exists():
        print(f"from:noreply@example.invalid newer_than:{days}d")
        return
    
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    
    allowlists = config.get("allowlists", {})
    
    if allowlist_type not in allowlists:
        print(f"from:noreply@example.invalid newer_than:{days}d")
        return
    
    al = allowlists[allowlist_type]
    senders = al.get("senders", [])
    domains = al.get("domains", [])
    
    if not senders and not domains:
        print(f"from:noreply@example.invalid newer_than:{days}d")
        return
    
    query_parts = []
    
    for sender in senders:
        query_parts.append(f"from:{sender}")
    
    for domain in domains:
        query_parts.append(f"from:@{domain}")
    
    combined = " OR ".join(query_parts)
    final_query = f"({combined}) newer_than:{days}d"
    print(final_query)


if __name__ == "__main__":
    main()


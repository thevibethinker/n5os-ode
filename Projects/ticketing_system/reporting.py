#!/usr/bin/env python3
"""Generate simple aggregate stats on tickets."""
import json, collections, pathlib, sys
STORE = pathlib.Path("/home/workspace/ticketing_system/tickets_store.json")

def main():
    tickets = json.loads(STORE.read_text()) if STORE.exists() else []
    counts = collections.Counter(t["status"] for t in tickets)
    cat_counts = collections.Counter(cat for t in tickets for cat in t.get("categories", []))
    print("Total tickets:", len(tickets))
    print("Status counts:", dict(counts))
    print("Category counts:", dict(cat_counts))

if __name__ == "__main__":
    main()

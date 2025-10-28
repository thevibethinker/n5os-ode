#!/usr/bin/env python3
"""Minimal interactive manager for demo purposes."""
import json, pathlib, sys
STORE = pathlib.Path("/home/workspace/ticketing_system/tickets_store.json")

def load():
    return json.loads(STORE.read_text()) if STORE.exists() else []

def save(lst):
    STORE.write_text(json.dumps(lst, indent=2))

def list_tickets():
    for t in load():
        print(t["id"], t["title"], t.get("status"))

def main():
    while True:
        cmd = input("list/quit> ").strip()
        if cmd == "list":
            list_tickets()
        elif cmd == "quit":
            break

if __name__ == "__main__":
    main()

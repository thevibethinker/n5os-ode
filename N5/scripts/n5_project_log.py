#!/usr/bin/env python3
"""
N5 Project Log - Wisdom Aggregation

Purpose: Centralize "Lessons Learned" and "Execution Wisdom" from all threads
into a single chronological log.

Usage:
    python3 n5_project_log.py add --type "architecture|process|tooling" --lesson "text"
    python3 n5_project_log.py list --last 10
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("/home/workspace/N5/data/project_log.jsonl")

def init_log():
    if not LOG_FILE.parent.exists():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()

def add_entry(lesson_type, text, source=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": lesson_type,
        "lesson": text,
        "source": source or "manual"
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Logged lesson ({lesson_type})")

def list_entries(limit=10):
    if not LOG_FILE.exists():
        print("No log entries found.")
        return

    entries = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    print(f"\n--- Project Log (Last {limit}) ---\n")
    for e in entries[-limit:]:
        print(f"[{e['timestamp'][:10]}] [{e['type'].upper()}] {e['lesson']}")

def main():
    init_log()
    parser = argparse.ArgumentParser(description="N5 Project Log")
    subparsers = parser.add_subparsers(dest="command")
    
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--type", required=True, choices=["architecture", "process", "tooling", "strategy", "other"])
    add_parser.add_argument("--lesson", required=True)
    add_parser.add_argument("--source", help="Source conversation or context")
    
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--last", type=int, default=10)
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_entry(args.type, args.lesson, args.source)
    elif args.command == "list":
        list_entries(args.last)
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"

def read_jsonl(p: Path):
    items = []
    if not p.exists():
        return items
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            ln = line.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSON on line {i} of {p}: {e}")
    return items

def matches_filters(item, filters):
    for key, value in filters.items():
        if key not in item:
            if value is not None:
                return False
            continue
        if isinstance(value, list):
            if not isinstance(item[key], list):
                return False
            if not set(value).issubset(set(item[key])):
                return False
        else:
            if item[key] != value:
                return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Find items in an N5 list.")
    parser.add_argument("list", help="List slug")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--priority", help="Filter by priority")
    parser.add_argument("--tags", nargs='*', help="Filter by tags (any match)")
    parser.add_argument("--project", help="Filter by project")
    parser.add_argument("--title-contains", help="Filter title containing substring")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--count", action="store_true", help="Just count results")
    args = parser.parse_args()

    slug = args.list.strip()
    if not slug:
        raise SystemExit("List cannot be empty")

    registry = read_jsonl(INDEX_FILE)
    reg_item = next((r for r in registry if r.get("slug") == slug), None)
    if not reg_item:
        raise SystemExit(f"List '{slug}' not found in registry")

    jsonl_file = LISTS_DIR / f"{slug}.jsonl"
    items = read_jsonl(jsonl_file)

    filters = {}
    if args.status:
        filters["status"] = args.status
    if args.priority:
        filters["priority"] = args.priority
    if args.tags:
        filters["tags"] = args.tags  # list, so subset
    if args.project:
        filters["project"] = args.project
    if args.title_contains:
        # Special filter
        pass

    matches = []
    for item in items:
        if matches_filters(item, filters):
            if args.title_contains:
                if args.title_contains.lower() not in item.get("title", "").lower():
                    continue
            matches.append(item)

    if args.count:
        print(len(matches))
    elif args.json:
        print(json.dumps(matches, indent=2))
    else:
        for item in matches:
            print(f"ID: {item['id']}")
            print(f"Title: {item['title']}")
            print(f"Status: {item['status']}")
            if item.get("priority"):
                print(f"Priority: {item['priority']}")
            if item.get("tags"):
                print(f"Tags: {', '.join(item['tags'])}")
            if item.get("body"):
                print(f"Body: {item['body'][:100]}{'...' if len(item['body']) > 100 else ''}")
            print("---")

if __name__ == "__main__":
    main()
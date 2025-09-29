#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"

def load_schema(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

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

def write_jsonl(p: Path, items):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, separators=(',', ':')) + '\n')

def validate_item(item, schema):
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(item), key=lambda e: e.path)
    if errors:
        msgs = [f"- {'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
        raise SystemExit("Schema validation failed:\n" + "\n".join(msgs))

def main():
    parser = argparse.ArgumentParser(description="Update an item in an N5 list.")
    parser.add_argument("list", help="List slug")
    parser.add_argument("item_id", help="Item ID")
    parser.add_argument("--title", help="New title")
    parser.add_argument("--body", help="New body")
    parser.add_argument("--tags", nargs='*', help="New tags (replace)")
    parser.add_argument("--priority", choices=["L", "M", "H"], help="New priority")
    parser.add_argument("--status", choices=["open", "pinned", "done", "archived"], help="New status")
    parser.add_argument("--project", help="New project")
    parser.add_argument("--due", help="New due date (ISO format)")
    parser.add_argument("--notes", help="New notes")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    slug = args.list.strip()
    item_id = args.item_id.strip()

    registry = read_jsonl(INDEX_FILE)
    reg_item = next((r for r in registry if r.get("slug") == slug), None)
    if not reg_item:
        raise SystemExit(f"List '{slug}' not found in registry")

    jsonl_file = LISTS_DIR / f"{slug}.jsonl"
    items = read_jsonl(jsonl_file)

    item = next((i for i in items if i.get("id") == item_id), None)
    if not item:
        raise SystemExit(f"Item '{item_id}' not found in list '{slug}'")

    now = datetime.now(timezone.utc).isoformat()
    updated = False

    if args.title is not None:
        item["title"] = args.title
        updated = True
    if args.body is not None:
        item["body"] = args.body
        updated = True
    if args.tags is not None:
        item["tags"] = args.tags
        updated = True
    if args.priority is not None:
        item["priority"] = args.priority
        updated = True
    if args.status is not None:
        item["status"] = args.status
        updated = True
    if args.project is not None:
        item["project"] = args.project
        updated = True
    if args.due is not None:
        item["due"] = args.due
        updated = True
    if args.notes is not None:
        item["notes"] = args.notes
        updated = True

    if updated:
        item["updated_at"] = now

    schema = load_schema(SCHEMAS / "lists.item.schema.json")
    validate_item(item, schema)

    if not args.dry_run:
        write_jsonl(jsonl_file, items)
        print(f"Updated item '{item_id}' in list '{slug}'")
        print(f"File: {jsonl_file}")
    else:
        print("Dry run: would update item")
        print(json.dumps(item, indent=2))

if __name__ == "__main__":
    main()
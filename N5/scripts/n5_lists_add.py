#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Import safety layer
from n5_safety import execute_with_safety, load_command_spec

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
    parser = argparse.ArgumentParser(description="Add an item to an N5 list.")
    parser.add_argument("list", help="List slug")
    parser.add_argument("title", help="Item title")
    parser.add_argument("--body", help="Item body")
    parser.add_argument("--tags", nargs='*', default=[], help="Tags")
    parser.add_argument("--priority", choices=["L", "M", "H"], help="Priority")
    parser.add_argument("--status", choices=["open", "pinned", "done", "archived"], default="open", help="Status")
    parser.add_argument("--project", help="Project")
    parser.add_argument("--due", help="Due date (ISO format)")
    parser.add_argument("--notes", help="Notes")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    # Load command spec for safety checks
    command_spec = load_command_spec("lists-add")

    def execute_lists_add(args):
        slug = args.list.strip()
        if not slug:
            raise SystemExit("List cannot be empty")

        registry = read_jsonl(INDEX_FILE)
        reg_item = next((r for r in registry if r.get("slug") == slug), None)
        if not reg_item:
            raise SystemExit(f"List '{slug}' not found in registry")

        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        items = read_jsonl(jsonl_file)

        title = args.title.strip()
        if not title:
            raise SystemExit("Title cannot be empty")

        now = datetime.now(timezone.utc).isoformat()
        item_id = str(uuid.uuid4())

        item = {
            "id": item_id,
            "created_at": now,
            "updated_at": now,
            "title": title,
            "status": args.status
        }

        if args.body:
            item["body"] = args.body
        if args.tags:
            item["tags"] = args.tags
        if args.priority:
            item["priority"] = args.priority
        if args.project:
            item["project"] = args.project
        if args.due:
            item["due"] = args.due
        if args.notes:
            item["notes"] = args.notes

        schema = load_schema(SCHEMAS / "lists.item.schema.json")
        validate_item(item, schema)

        items.append(item)

        if not args.dry_run:
            write_jsonl(jsonl_file, items)
            print(f"Added item '{title}' to list '{slug}'")
            print(f"Item ID: {item_id}")
            print(f"File: {jsonl_file}")
        else:
            print("Dry run: would add item")
            print(json.dumps(item, indent=2))

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_lists_add)
    return result

if __name__ == "__main__":
    main()
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
    temp_file = p.with_suffix('.tmp')
    try:
        with temp_file.open("w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, separators=(',', ':')) + '\n')
        temp_file.replace(p)  # Atomic move
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise SystemExit(f"Failed to write JSONL: {e}")


def validate_item(item, schema):
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(item), key=lambda e: e.path)
    if errors:
        msgs = [f"- {'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
        raise SystemExit("Schema validation failed:\n" + "\n".join(msgs))


def main():
    parser = argparse.ArgumentParser(description="Move an item from one N5 list to another.")
    parser.add_argument("source_list", help="Source list slug")
    parser.add_argument("item_id", help="Item ID to move")
    parser.add_argument("dest_list", help="Destination list slug")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    # Load command spec for safety checks
    command_spec = load_command_spec("lists-move")

    def execute_lists_move(args):
        # Load registry
        registry = read_jsonl(INDEX_FILE)
        available_slugs = [r.get("slug") for r in registry if r.get("slug")]
        if not registry:
            raise SystemExit("No lists defined in registry")

        source_slug = args.source_list.strip()
        dest_slug = args.dest_list.strip()
        item_id = args.item_id.strip()

        if not source_slug or not dest_slug or not item_id:
            raise SystemExit("Source list, destination list, and item ID cannot be empty")

        # Validate source and dest lists
        source_reg = next((r for r in registry if r.get("slug") == source_slug), None)
        if not source_reg:
            raise SystemExit(f"Source list '{source_slug}' not found in registry")

        dest_reg = next((r for r in registry if r.get("slug") == dest_slug), None)
        if not dest_reg:
            raise SystemExit(f"Destination list '{dest_slug}' not found in registry")

        if source_slug == dest_slug:
            raise SystemExit("Source and destination lists must be different")

        source_file = (LISTS_DIR / f"{source_slug}.jsonl").resolve()
        dest_file = (LISTS_DIR / f"{dest_slug}.jsonl").resolve()

        source_items = read_jsonl(source_file)
        dest_items = read_jsonl(dest_file)

        # Find and remove item from source
        item_to_move = None
        for i, item in enumerate(source_items):
            if item.get("id") == item_id:
                item_to_move = source_items.pop(i)
                break

        if not item_to_move:
            raise SystemExit(f"Item '{item_id}' not found in source list '{source_slug}'")

        # Update metadata
        now = datetime.now(timezone.utc).isoformat()
        item_to_move["updated_at"] = now
        # Optionally add move note
        if "notes" not in item_to_move:
            item_to_move["notes"] = ""
        item_to_move["notes"] += f" Moved from {source_slug} to {dest_slug} at {now}."

        # Validate updated item
        schema = load_schema(SCHEMAS / "lists.item.schema.json")
        validate_item(item_to_move, schema)

        # Add to dest
        dest_items.append(item_to_move)

        if not args.dry_run:
            write_jsonl(source_file, source_items)
            write_jsonl(dest_file, dest_items)
            print(f"Moved item '{item_to_move.get('title', 'Untitled')}' from '{source_slug}' to '{dest_slug}'")
            print(f"Item ID: {item_id}")
            print(f"Source: {source_file}")
            print(f"Destination: {dest_file}")
        else:
            print("Dry run: would move item")
            print(f"From {source_slug} to {dest_slug}")
            print(json.dumps(item_to_move, indent=2))

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_lists_move)
    return result

if __name__ == "__main__":
    main()
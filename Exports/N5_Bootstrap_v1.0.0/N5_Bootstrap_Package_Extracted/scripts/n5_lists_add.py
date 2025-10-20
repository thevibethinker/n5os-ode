#!/usr/bin/env python3
import json, sys, argparse
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timezone
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

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
    parser = argparse.ArgumentParser(description="Add an item to an N5 list.")
    parser.add_argument("list", nargs='?', help="List slug (optional; auto-assigned if omitted)")
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
        # Load registry
        registry = read_jsonl(INDEX_FILE)
        available_slugs = [r.get("slug") for r in registry if r.get("slug")]
        if not registry:
            raise SystemExit("No lists defined in registry")

        # Determine slug via argument or classifier
        slug_arg = (args.list or '').strip() if hasattr(args, 'list') else ''
        slug = None
        rationale = None
        if not slug_arg:
            try:
                from listclassifier import classify_list as classify
                cls = classify(args.title, available_slugs)
                slug = cls[0]
                rationale = cls[1]
            except Exception:
                slug = 'ideas' if 'ideas' in available_slugs else (available_slugs[0] if available_slugs else 'ideas')
                rationale = 'classifier unavailable; defaulted'
        else:
            slug = slug_arg
            rationale = 'explicit list provided'

        if not slug:
            raise SystemExit("Unable to determine target list")

        reg_item = next((r for r in registry if r.get("slug") == slug), None)
        if not reg_item:
            raise SystemExit(f"List '{slug}' not found in registry")

        jsonl_file = (LISTS_DIR / f"{slug}.jsonl").resolve()
        items = read_jsonl(jsonl_file)

        title = args.title.strip()
        if not title:
            raise SystemExit("Corrupt input: Title cannot be empty")

        now = datetime.now(timezone.utc).isoformat()
        item_id = str(uuid.uuid4())

        item = {
            "id": item_id,
            "created_at": now,
            "updated_at": now,
            "title": title,
            "status": args.status
        }

        # Validate and parse optional fields for corrupt inputs
        if args.body:
            try:
                # If body is meant to be JSON, validate; else treat as string
                json.loads(args.body)
                item["body"] = args.body
            except json.JSONDecodeError:
                item["body"] = args.body  # Treat as plain text if not JSON
        if args.tags:
            if not isinstance(args.tags, list) or any(not isinstance(t, str) for t in args.tags):
                raise SystemExit("Corrupt input: Tags must be list of strings")
            item["tags"] = args.tags
        elif not slug_arg:  # Extract tags only if auto-assigning and no tags provided
            try:
                from listclassifier import extract_tags
                content_for_tags = args.title
                if args.body:
                    content_for_tags += " " + args.body
                extracted = extract_tags(content_for_tags)
                if extracted:
                    item["tags"] = extracted
            except Exception:
                pass  # Ignore if extraction fails
        if args.priority:
            item["priority"] = args.priority
        if args.project:
            item["project"] = args.project
        if args.due:
            item["due"] = args.due
        if args.notes:
            try:
                # If notes is meant to be JSON, validate; else treat as string
                json.loads(args.notes)
                item["notes"] = args.notes
            except json.JSONDecodeError:
                item["notes"] = args.notes  # Treat as plain text

        schema = load_schema(SCHEMAS / "lists.item.schema.json")
        validate_item(item, schema)

        items.insert(0, item)  # Insert at beginning for reverse chronological order

        # Output assignment info without prompts
        print(f"Assigned list: {slug}")
        print(f"Rationale: {rationale}")

        if not args.dry_run:
            write_jsonl(jsonl_file, items)
            print(f"Added item '{title}' to list '{slug}'")
            print(f"Item ID: {item_id}")
            print(f"File: {jsonl_file}")
            
            # Dual-write: Update markdown view
            logger.info("Updating markdown view...")
            docgen_script = Path(__file__).parent / "n5_lists_docgen.py"
            result = subprocess.run(
                [sys.executable, str(docgen_script), "--list", slug],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.warning(f"MD generation failed: {result.stderr}")
            else:
                logger.info("✓ MD view updated")
        else:
            print("Dry run: would add item")
            print(json.dumps(item, indent=2))

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_lists_add)
    return result

if __name__ == "__main__":
    main()
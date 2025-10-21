#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid
import re

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"

def generate_slug(title: str) -> str:
    # Basic cleanup: lowercase, replace spaces with hyphens, remove special chars
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    if not slug:
        return "list"
    if len(slug) > 30:
        words = slug.split('-')[:4]
        slug = '-'.join(words)
    return slug

def find_similar_lists(registry, title, slug):
    similar = []
    title_lower = title.lower()
    for item in registry:
        existing_title = item.get('title', '').lower()
        existing_slug = item.get('slug', '')
        if existing_title == title_lower or existing_slug == slug:
            similar.append(('exact', item))
        elif existing_title in title_lower or title_lower in existing_title:
            similar.append(('partial_title', item))
        elif existing_slug in slug or slug in existing_slug:
            similar.append(('partial_slug', item))
    return similar

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
    with p.open("a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, separators=(',', ':')) + '\n')

def validate_registry_item(item, schema):
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(item), key=lambda e: e.path)
    if errors:
        msgs = [f"- {'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
        raise SystemExit("Schema validation failed:\n" + "\n".join(msgs))

def main():
    parser = argparse.ArgumentParser(description="Create a new N5 list.")
    parser.add_argument("slug", help="List slug (lowercase, hyphens allowed)")
    parser.add_argument("title", help="List title")
    parser.add_argument("--tags", nargs='*', default=[], help="Tags")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    slug = args.slug.lower().strip()
    if not slug:
        raise SystemExit("Slug cannot be empty")
    # Validate slug pattern
    import re
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise SystemExit("Slug must match pattern: ^[a-z0-9]+(?:-[a-z0-9]+)*$")

    title = args.title.strip()
    if not title:
        raise SystemExit("Title cannot be empty")

    schema = load_schema(SCHEMAS / "lists.registry.schema.json")
    registry = read_jsonl(INDEX_FILE)

    # Check if slug exists
    if any(r.get("slug") == slug for r in registry):
        raise SystemExit(f"List '{slug}' already exists")

    now = datetime.now(timezone.utc).isoformat()

    item = {
        "slug": slug,
        "title": title,
        "path_jsonl": f"Lists/{slug}.jsonl",
        "path_md": f"Lists/{slug}.md",
        "created_at": now,
        "updated_at": now
    }
    if args.tags:
        item["tags"] = args.tags

    validate_registry_item(item, schema)

    if not args.dry_run:
        write_jsonl(INDEX_FILE, [item])
        # Create empty files
        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        md_file = LISTS_DIR / f"{slug}.md"
        jsonl_file.touch()
        md_file.write_text(f"# {title}\n\n<!-- Generated MD view of {slug}.jsonl -->\n\n", encoding="utf-8")
        print(f"Created list '{slug}'")
        print(f"Registry: {INDEX_FILE}")
        print(f"JSONL: {jsonl_file}")
        print(f"MD: {md_file}")
    else:
        print("Dry run: would create list")
        print(json.dumps(item, indent=2))

if __name__ == "__main__":
    main()
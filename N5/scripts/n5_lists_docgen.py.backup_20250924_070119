#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime

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

def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").replace("\r", "")

def render_md(title, items):
    lines = [f"# {title}\n\n<!-- Generated MD view of JSONL -->\n\n"]
    if not items:
        lines.append("No items.\n\n")
        return "".join(lines)

    # Group by status
    groups = {}
    for item in items:
        status = item.get("status", "open")
        groups.setdefault(status, []).append(item)

    for status in ["open", "pinned", "done", "archived"]:
        if status not in groups:
            continue
        lines.append(f"## {status.title()}\n\n")
        for item in sorted(groups[status], key=lambda x: x.get("created_at", "")):
            lines.append(f"### {md_escape(item['title'])}\n\n")
            lines.append(f"**ID:** {item['id']}\n\n")
            lines.append(f"**Created:** {item.get('created_at', 'N/A')}\n\n")
            if item.get("updated_at") and item["updated_at"] != item.get("created_at"):
                lines.append(f"**Updated:** {item['updated_at']}\n\n")
            if item.get("priority"):
                lines.append(f"**Priority:** {item['priority']}\n\n")
            if item.get("tags"):
                lines.append(f"**Tags:** {', '.join(item['tags'])}\n\n")
            if item.get("project"):
                lines.append(f"**Project:** {item['project']}\n\n")
            if item.get("due"):
                lines.append(f"**Due:** {item['due']}\n\n")
            if item.get("body"):
                lines.append(f"**Body:**\n\n{item['body']}\n\n")
            if item.get("notes"):
                lines.append(f"**Notes:** {item['notes']}\n\n")
            lines.append("---\n\n")
        lines.append("\n")

    return "".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Regenerate MD views for N5 lists.")
    parser.add_argument("--list", help="Specific list slug, else all")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    registry = read_jsonl(INDEX_FILE)
    if not registry:
        print("No lists in registry.")
        return

    lists_to_process = registry
    if args.list:
        lists_to_process = [r for r in registry if r.get("slug") == args.list]
        if not lists_to_process:
            raise SystemExit(f"List '{args.list}' not found")

    for reg in lists_to_process:
        slug = reg["slug"]
        title = reg["title"]
        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        md_file = LISTS_DIR / f"{slug}.md"

        items = read_jsonl(jsonl_file)
        md_content = render_md(title, items)

        if not args.dry_run:
            md_file.parent.mkdir(parents=True, exist_ok=True)
            md_file.write_text(md_content, encoding="utf-8")
            print(f"Generated MD for '{slug}': {md_file}")
        else:
            print(f"Dry run: would generate MD for '{slug}'")
            print(md_content[:500] + ("..." if len(md_content) > 500 else ""))

if __name__ == "__main__":
    main()
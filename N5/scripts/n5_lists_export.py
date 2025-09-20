#!/usr/bin/env python3
import json, sys, argparse, csv
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

def export_md(title, items, output_file):
    md_content = render_md(title, items)
    with output_file.open("w", encoding="utf-8") as f:
        f.write(md_content)

def export_csv(items, output_file):
    if not items:
        return
    fieldnames = ["id", "title", "status", "priority", "tags", "project", "due", "body", "notes", "created_at", "updated_at"]
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            row = {k: item.get(k, "") for k in fieldnames}
            if isinstance(row["tags"], list):
                row["tags"] = ", ".join(row["tags"])
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Export an N5 list to MD or CSV.")
    parser.add_argument("list", help="List slug")
    parser.add_argument("format", choices=["md", "csv"], help="Export format")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    slug = args.list.strip()

    registry = read_jsonl(INDEX_FILE)
    reg_item = next((r for r in registry if r.get("slug") == slug), None)
    if not reg_item:
        raise SystemExit(f"List '{slug}' not found in registry")

    jsonl_file = LISTS_DIR / f"{slug}.jsonl"
    items = read_jsonl(jsonl_file)

    if not args.output:
        output_file = LISTS_DIR / f"{slug}.{args.format}"
    else:
        output_file = Path(args.output)

    if args.format == "md":
        export_md(reg_item["title"], items, output_file)
    elif args.format == "csv":
        export_csv(items, output_file)

    if not args.dry_run:
        print(f"Exported '{slug}' to {output_file}")
    else:
        print(f"Dry run: would export to {output_file}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Frontmatter Manager — Add, validate, and query YAML frontmatter on markdown files.

Enforces provenance metadata (P39: Audit Everything) by ensuring every document
has structured frontmatter with type, category, version, and timestamps.

Usage:
    python3 frontmatter_manager.py add --file doc.md --type note --category ops
    python3 frontmatter_manager.py validate --file doc.md
    python3 frontmatter_manager.py validate --dir ./docs
    python3 frontmatter_manager.py query --type note --dir ./docs
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TAXONOMY = {
    "types": [
        "note", "protocol", "guide", "script", "config", "report",
        "meeting", "decision", "plan", "reference", "template", "log"
    ],
    "categories": [
        "ops", "build", "research", "personal", "system", "content",
        "automation", "integration", "documentation", "planning"
    ]
}


def load_taxonomy(taxonomy_path=None):
    if taxonomy_path and Path(taxonomy_path).exists():
        return json.loads(Path(taxonomy_path).read_text())
    config_path = SCRIPT_DIR.parent / "config" / "frontmatter_taxonomy.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return DEFAULT_TAXONOMY


class FrontmatterManager:
    def __init__(self, taxonomy_path=None):
        self.taxonomy = load_taxonomy(taxonomy_path)

    def parse_frontmatter(self, content):
        if not content.startswith('---\n'):
            return None, content
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return None, content
        fm = {}
        for line in parts[1].strip().split('\n'):
            if ':' not in line:
                continue
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"\'')
        return fm, parts[2]

    def serialize_frontmatter(self, fm):
        lines = ['---']
        for k, v in fm.items():
            lines.append(f'{k}: "{v}"')
        lines.append('---\n')
        return '\n'.join(lines)

    def validate(self, file_path, verbose=True):
        content = file_path.read_text()
        fm, _ = self.parse_frontmatter(content)
        if not fm:
            return False, ["No frontmatter"]
        errors = []
        for field in ['type', 'category', 'version', 'created', 'modified', 'status', 'owner']:
            if field not in fm:
                errors.append(f"Missing: {field}")
        if not errors:
            if fm['type'] not in self.taxonomy['types']:
                errors.append(f"Invalid type: {fm['type']}")
            if fm['category'] not in self.taxonomy['categories']:
                errors.append(f"Invalid category: {fm['category']}")
            if not re.match(r'^\d+\.\d+\.\d+$', fm['version']):
                errors.append(f"Invalid version: {fm['version']}")
        if verbose and not errors:
            print(f"  Valid: {file_path}")
        return len(errors) == 0, errors

    def add(self, file_path, fm_data, force=False):
        content = file_path.read_text()
        existing, body = self.parse_frontmatter(content)
        if existing and not force:
            raise ValueError("Frontmatter exists. Use --force")
        today = datetime.now().strftime("%Y-%m-%d")
        fm_data.setdefault('version', '1.0.0')
        fm_data.setdefault('created', today)
        fm_data.setdefault('modified', today)
        fm_data.setdefault('status', 'draft')
        fm_data.setdefault('owner', 'user')
        file_path.write_text(self.serialize_frontmatter(fm_data) + body)
        print(f"  Added frontmatter: {file_path}")

    def query(self, filters, search_dir=None):
        if search_dir is None:
            search_dir = Path.cwd()
        matches = []
        for f in search_dir.rglob("*.md"):
            try:
                content = f.read_text()
                fm, _ = self.parse_frontmatter(content)
                if fm and all(fm.get(k) == v for k, v in filters.items()):
                    matches.append(f)
            except Exception:
                pass
        return sorted(matches)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Manage YAML frontmatter on markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --file docs/plan.md --type plan --category build
  %(prog)s validate --dir ./docs
  %(prog)s query --type note --category ops --dir ./Knowledge
        """
    )
    parser.add_argument('--taxonomy', type=Path, help="Path to taxonomy JSON file")
    sub = parser.add_subparsers(dest='cmd', required=True)

    add_p = sub.add_parser('add', help="Add frontmatter to a markdown file")
    add_p.add_argument('--file', required=True, type=Path)
    add_p.add_argument('--type', required=True)
    add_p.add_argument('--category', required=True)
    add_p.add_argument('--force', action='store_true', help="Overwrite existing frontmatter")

    val_p = sub.add_parser('validate', help="Validate frontmatter on files")
    val_p.add_argument('--file', type=Path, help="Single file to validate")
    val_p.add_argument('--dir', type=Path, help="Directory to validate recursively")

    query_p = sub.add_parser('query', help="Query files by frontmatter fields")
    query_p.add_argument('--type')
    query_p.add_argument('--category')
    query_p.add_argument('--dir', type=Path, default=Path.cwd())

    args = parser.parse_args()
    manager = FrontmatterManager(taxonomy_path=args.taxonomy)

    try:
        if args.cmd == 'add':
            manager.add(args.file, {'type': args.type, 'category': args.category}, args.force)
        elif args.cmd == 'validate':
            if args.file:
                ok, errs = manager.validate(args.file)
                if not ok:
                    print(f"  Failed: {args.file}: {', '.join(errs)}")
                    sys.exit(1)
            elif args.dir:
                files = list(args.dir.rglob("*.md"))
                failed = []
                for f in files:
                    ok, errs = manager.validate(f, verbose=False)
                    if not ok:
                        failed.append((f, errs))
                if failed:
                    print(f"  {len(failed)}/{len(files)} failed validation")
                    for f, errs in failed[:5]:
                        print(f"    {f}: {errs[0]}")
                    sys.exit(1)
                print(f"  All {len(files)} files valid")
            else:
                print("Provide --file or --dir", file=sys.stderr)
                sys.exit(1)
        elif args.cmd == 'query':
            filters = {k: v for k, v in [('type', args.type), ('category', args.category)] if v}
            matches = manager.query(filters, args.dir)
            print(f"Found {len(matches)}:")
            for m in matches:
                print(f"  {m}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""N5 Frontmatter Manager"""
import argparse, json, re, sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/workspace")
TAXONOMY_FILE = WORKSPACE / "N5/config/frontmatter_taxonomy.json"

class FrontmatterManager:
    def __init__(self):
        self.taxonomy = json.loads(TAXONOMY_FILE.read_text())
    
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
            print(f"✓ Valid: {file_path.relative_to(WORKSPACE)}")
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
        fm_data.setdefault('owner', 'zo')
        file_path.write_text(self.serialize_frontmatter(fm_data) + body)
        print(f"✓ Added: {file_path.relative_to(WORKSPACE)}")
    
    def query(self, filters, search_dir=WORKSPACE):
        matches = []
        for f in search_dir.rglob("*.md"):
            if "/.z/workspaces/" in str(f):
                continue
            try:
                content = f.read_text()
                fm, _ = self.parse_frontmatter(content)
                if fm and all(fm.get(k) == v for k, v in filters.items()):
                    matches.append(f)
            except:
                pass
        return sorted(matches)

manager = FrontmatterManager()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd', required=True)
    
    add_p = sub.add_parser('add')
    add_p.add_argument('--file', required=True, type=Path)
    add_p.add_argument('--type', required=True)
    add_p.add_argument('--category', required=True)
    add_p.add_argument('--force', action='store_true')
    
    val_p = sub.add_parser('validate')
    val_p.add_argument('--file', type=Path)
    val_p.add_argument('--dir', type=Path)
    
    query_p = sub.add_parser('query')
    query_p.add_argument('--type')
    query_p.add_argument('--category')
    query_p.add_argument('--dir', type=Path, default=WORKSPACE)
    
    args = parser.parse_args()
    
    try:
        if args.cmd == 'add':
            manager.add(args.file, {'type': args.type, 'category': args.category}, args.force)
        elif args.cmd == 'validate':
            if args.file:
                ok, errs = manager.validate(args.file)
                if not ok:
                    print(f"✗ {args.file}: {', '.join(errs)}")
                    sys.exit(1)
            elif args.dir:
                files = list(args.dir.rglob("*.md"))
                failed = [(f, e) for f in files if not (ok := manager.validate(f, False))[0] for e in [ok[1]]]
                if failed:
                    print(f"✗ {len(failed)}/{len(files)} failed")
                    for f, errs in failed[:5]:
                        print(f"  {f.relative_to(WORKSPACE)}: {errs[0]}")
                    sys.exit(1)
                print(f"✓ All {len(files)} valid")
        elif args.cmd == 'query':
            filters = {k: v for k, v in [('type', args.type), ('category', args.category)] if v}
            matches = manager.query(filters, args.dir)
            print(f"Found {len(matches)}:\n" + '\n'.join(f"  {m.relative_to(WORKSPACE)}" for m in matches))
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

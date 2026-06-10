#!/usr/bin/env python3
"""
Load the visual skill catalog by reading chain_metadata frontmatter
from every Skills/*/SKILL.md that has it.

Returns a dict: {skill_slug: chain_metadata + name + description}

NOTE: Reconstructed from compiled bytecode (original source was lost);
behavior matches the original CLI surface.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: pip install pyyaml\n")
    sys.exit(2)


def load_catalog(skills_root="/home/workspace/Skills"):
    catalog = {}
    root = Path(skills_root)
    for skill_md in sorted(root.glob("*/SKILL.md")):
        slug = skill_md.parent.name
        try:
            text = skill_md.read_text(errors="ignore")
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1])
            if not isinstance(fm, dict):
                continue
            chain_meta = fm.get("chain_metadata")
            if not chain_meta:
                continue
            entry = dict(chain_meta)
            entry["name"] = fm.get("name", slug)
            desc = fm.get("description", "")
            if isinstance(desc, str):
                entry["description"] = desc.strip()
            else:
                entry["description"] = ""
            catalog[slug] = entry
        except Exception as e:
            sys.stderr.write(f"WARN: skipping {slug}: {e}\n")
            continue
    return catalog


def main():
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Load visual skill catalog from SKILL.md frontmatter")
    ap.add_argument("--skills-root", default="/home/workspace/Skills")
    ap.add_argument("--format", choices=["json", "summary"], default="summary")
    args = ap.parse_args()

    catalog = load_catalog(args.skills_root)

    if args.format == "json":
        print(json.dumps(catalog, indent=2))
        return 0

    print(f"Catalog: {len(catalog)} skills with chain_metadata")
    for slug, entry in catalog.items():
        stage = entry.get("stage", "unknown")
        print(f"  [{stage}] {slug}: {entry.get('description', '')[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

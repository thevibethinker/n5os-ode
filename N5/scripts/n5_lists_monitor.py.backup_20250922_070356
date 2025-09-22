#!/usr/bin/env python3
"""
N5 Lists Monitor: Check integrity of lists system for edge cases.
"""

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"
SCHEMAS = ROOT / "schemas"

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
                print(f"❌ {p.name}: Invalid JSON on line {i}: {e}")
                return None
    return items

def validate_item(item, schema):
    try:
        from jsonschema import Draft202012Validator
        v = Draft202012Validator(schema)
        errors = list(v.iter_errors(item))
        return errors
    except ImportError:
        return ["jsonschema not available"]

def main():
    issues = []

    # Load registry
    registry = read_jsonl(INDEX_FILE)
    if registry is None:
        issues.append("❌ index.jsonl: Corrupt")
        return issues

    schema = load_schema(SCHEMAS / "lists.item.schema.json")

    for reg in registry:
        slug = reg.get("slug")
        if not slug:
            issues.append(f"❌ Registry item missing slug: {reg}")
            continue

        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        items = read_jsonl(jsonl_file)
        if items is None:
            issues.append(f"❌ {slug}.jsonl: Corrupt")
            continue

        for item in items:
            errors = validate_item(item, schema)
            if errors:
                issues.append(f"❌ {slug}: Item {item.get('id')} schema errors: {errors}")
            # Check for missing required fields
            if not item.get("id"):
                issues.append(f"❌ {slug}: Item missing ID")
            if not item.get("title"):
                issues.append(f"❌ {slug}: Item {item.get('id')} missing title")

    if not issues:
        print("✅ No issues detected in lists system.")
    else:
        print("Issues found:")
        for issue in issues:
            print(issue)

    return issues

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
FACTS_FILE = KNOWLEDGE_DIR / "facts.jsonl"

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

def main():
    parser = argparse.ArgumentParser(description="Search facts in the knowledge base.")
    parser.add_argument("--subject", help="Subject to match")
    parser.add_argument("--predicate", help="Predicate to match")
    parser.add_argument("--object", help="Object to match")
    parser.add_argument("--source", help="Source to match")
    parser.add_argument("--tags", help="Tags as JSON string")
    parser.add_argument("--count", action="store_true", help="Just count matches")
    args = parser.parse_args()

    # Parse tags if provided
    search_tags = []
    if args.tags:
        try:
            search_tags = json.loads(args.tags)
            if not isinstance(search_tags, list):
                search_tags = [args.tags]
        except json.JSONDecodeError:
            search_tags = [args.tags]

    facts = read_jsonl(FACTS_FILE)
    matches = []

    for fact in facts:
        if args.subject and fact.get("subject") != args.subject:
            continue
        if args.predicate and fact.get("predicate") != args.predicate:
            continue
        if args.object and fact.get("object") != args.object:
            continue
        if args.source and fact.get("source") != args.source:
            continue
        if search_tags:
            fact_tags = fact.get("tags", [])
            if not any(tag in fact_tags for tag in search_tags):
                continue
        matches.append(fact)

    if args.count:
        print(len(matches))
    else:
        print(json.dumps(matches, indent=2))

if __name__ == "__main__":
    main()
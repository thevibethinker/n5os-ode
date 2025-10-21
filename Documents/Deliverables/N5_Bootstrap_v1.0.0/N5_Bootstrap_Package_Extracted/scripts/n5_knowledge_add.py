#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid

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

def write_jsonl(p: Path, items):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, separators=(',', ':')) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Add a fact to the knowledge base.")
    parser.add_argument("--subject", required=True, help="Subject of the fact")
    parser.add_argument("--predicate", required=True, help="Predicate/relationship")
    parser.add_argument("--object", required=True, help="Object of the fact")
    parser.add_argument("--source", help="Source of the fact")
    parser.add_argument("--tags", help="Tags as JSON string")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    # Parse tags if provided
    tags = []
    if args.tags:
        try:
            tags = json.loads(args.tags)
            if not isinstance(tags, list):
                tags = [args.tags]
        except json.JSONDecodeError:
            tags = [args.tags]

    facts = read_jsonl(FACTS_FILE)

    # Generate fact ID
    fact_id = str(uuid.uuid4())[:8]

    now = datetime.now(timezone.utc).isoformat()
    fact = {
        "id": fact_id,
        "subject": args.subject,
        "predicate": args.predicate,
        "object": args.object,
        "source": args.source or "manual",
        "confidence": 1.0,
        "tags": tags,
        "created_at": now,
        "updated_at": now
    }

    if not args.dry_run:
        facts.append(fact)
        write_jsonl(FACTS_FILE, facts)
        print(f"Added fact: {fact_id}")
        print(f"Facts file: {FACTS_FILE}")
    else:
        print("Dry run: would add fact")
        print(json.dumps(fact, indent=2))

if __name__ == "__main__":
    main()
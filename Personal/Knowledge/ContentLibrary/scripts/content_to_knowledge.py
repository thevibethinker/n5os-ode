#!/usr/bin/env python3
"""
Content Library to Knowledge Bridge
- Append-only promotion of key findings from Content Library entries into Knowledge base
- Avoid rewriting existing knowledge facts
- Supports flexible addition of fields and categories
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

CONTENT_LIBRARY_PATH = Path("/home/workspace/Personal/Content-Library/content-library.json")
KNOWLEDGE_FACTS_PATH = Path("/home/workspace/N5/knowledge/facts.jsonl")


def load_content_library():
    with open(CONTENT_LIBRARY_PATH, "r") as f:
        return json.load(f)


def load_knowledge_facts():
    facts = []
    if KNOWLEDGE_FACTS_PATH.exists():
        with open(KNOWLEDGE_FACTS_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    facts.append(json.loads(line))
    return facts


def fact_exists(facts, subject, predicate, obj):
    for fact in facts:
        if fact.get("subject") == subject and fact.get("predicate") == predicate and fact.get("object") == obj:
            return True
    return False


def append_fact(fact):
    with open(KNOWLEDGE_FACTS_PATH, "a") as f:
        f.write(json.dumps(fact, separators=(',', ':')) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Append Content Library findings to Knowledge base (append-only)")
    parser.add_argument("--entry-id", required=True, help="Content Library entry ID to promote")
    parser.add_argument("--finding-indices", nargs='+', type=int, help="Indices of key findings to promote")
    args = parser.parse_args()

    content_library = load_content_library()
    facts = load_knowledge_facts()

    entry = content_library["entries"].get(args.entry_id)
    if not entry:
        print(f"Error: Entry ID {args.entry_id} not found in Content Library")
        sys.exit(1)

    findings = entry.get("key_findings", [])
    if not findings:
        print(f"Error: No key findings found in entry {args.entry_id}")
        sys.exit(1)

    indices_to_promote = args.finding_indices if args.finding_indices else range(len(findings))

    promoted = 0
    for idx in indices_to_promote:
        if idx < 0 or idx >= len(findings):
            print(f"Warning: Finding index {idx} out of range")
            continue
        finding_text = findings[idx]

        # Derive subject, predicate, object from text - this is a placeholder, real NLP can be added
        subject = entry.get("title", "unknown")
        predicate = "has-key-finding"
        obj = finding_text

        if fact_exists(facts, subject, predicate, obj):
            print(f"Skipping duplicate fact: {subject} | {predicate} | {obj}")
            continue

        fact = {
            "id": f"fact_{args.entry_id}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "source_entry_id": args.entry_id,
            "date_added": datetime.now().isoformat()
        }

        append_fact(fact)
        promoted += 1
        print(f"Promoted fact {fact['id']}")

    print(f"Total promoted: {promoted}")

if __name__ == '__main__':
    main()


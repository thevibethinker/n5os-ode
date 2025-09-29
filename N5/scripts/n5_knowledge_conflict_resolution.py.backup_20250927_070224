#!/usr/bin/env python3
"""
Conflict Resolution Module for N5 Knowledge Ingestion System.

Detects contradictions and conflicts in appended facts and knowledge items.
Surfaces conflicts for user or AI-driven resolution.
Provides safe merging or replacement workflows.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

FACTS_FILE = Path(__file__).resolve().parents[1] / "knowledge" / "facts.jsonl"


def load_facts() -> List[Dict]:
    if not FACTS_FILE.exists():
        return []
    facts = []
    with open(FACTS_FILE, "r") as f:
        for line in f:
            try:
                facts.append(json.loads(line.strip()))
            except Exception:
                continue
    return facts


def find_conflicts(facts: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """Detect contradictions by finding facts with same subject-predicate but different objects."""
    conflict_map = defaultdict(list)
    for fact in facts:
        key = (fact.get('subject'), fact.get('predicate'))
        conflict_map[key].append(fact)

    conflicts = []
    for key, fact_list in conflict_map.items():
        objects = set(f['object'] for f in fact_list)
        if len(objects) > 1:
            # Conflicting facts found for same subject-predicate
            for i in range(len(fact_list)):
                for j in range(i+1, len(fact_list)):
                    if fact_list[i]['object'] != fact_list[j]['object']:
                        conflicts.append((fact_list[i], fact_list[j]))
    return conflicts


def surface_conflicts(conflicts: List[Tuple[Dict, Dict]]):
    """Print conflicts clearly for user or AI to review."""
    if not conflicts:
        print("No conflicts detected.")
        return
    print(f"{len(conflicts)} conflicts detected:")
    for i, (fact1, fact2) in enumerate(conflicts, 1):
        print(f"Conflicting pair #{i}:")
        print(f"  Fact 1: subject='{fact1['subject']}', predicate='{fact1['predicate']}', object='{fact1['object']}'")
        print(f"  Fact 2: subject='{fact2['subject']}', predicate='{fact2['predicate']}', object='{fact2['object']}'")
        print("---")


def main():
    print("Loading facts...")
    facts = load_facts()
    print(f"Loaded {len(facts)} facts.")

    conflicts = find_conflicts(facts)
    surface_conflicts(conflicts)

    # Placeholder for implementing resolution workflows
    if conflicts:
        print("Resolution workflows to be implemented.")


if __name__ == '__main__':
    main()

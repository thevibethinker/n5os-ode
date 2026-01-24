#!/usr/bin/env python3
"""
Pulse Learnings: Capture and propagate learnings at build and system level.

Two tiers:
1. Build-local learnings  → N5/builds/<slug>/BUILD_LESSONS.json
2. System-wide learnings  → N5/learnings/SYSTEM_LEARNINGS.json

Usage:
  pulse_learnings.py add <slug> "learning text" [--system]
  pulse_learnings.py list <slug>
  pulse_learnings.py list-system
  pulse_learnings.py promote <slug> <index>  # Promote build learning to system
  pulse_learnings.py inject <slug>           # Inject relevant system learnings into build briefs
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SYSTEM_LEARNINGS = WORKSPACE / "N5" / "learnings" / "SYSTEM_LEARNINGS.json"


def load_build_learnings(slug: str) -> dict:
    """Load build-specific learnings"""
    path = BUILDS_DIR / slug / "BUILD_LESSONS.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"slug": slug, "learnings": []}


def save_build_learnings(slug: str, data: dict):
    """Save build-specific learnings"""
    path = BUILDS_DIR / slug / "BUILD_LESSONS.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_system_learnings() -> dict:
    """Load system-wide learnings"""
    if SYSTEM_LEARNINGS.exists():
        with open(SYSTEM_LEARNINGS) as f:
            return json.load(f)
    return {"meta": {"description": "System-wide learnings", "version": "1.0"}, "learnings": []}


def save_system_learnings(data: dict):
    """Save system-wide learnings"""
    with open(SYSTEM_LEARNINGS, "w") as f:
        json.dump(data, f, indent=2)


def add_learning(slug: str, text: str, source: str = "manual", system: bool = False, tags: list = None):
    """Add a learning to build or system level"""
    learning = {
        "text": text,
        "source": source,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "tags": tags or []
    }
    
    if system:
        learning["origin_build"] = slug
        data = load_system_learnings()
        data["learnings"].append(learning)
        save_system_learnings(data)
        print(f"[SYSTEM] Added learning: {text[:60]}...")
    else:
        data = load_build_learnings(slug)
        data["learnings"].append(learning)
        save_build_learnings(slug, data)
        print(f"[{slug}] Added learning: {text[:60]}...")


def list_learnings(slug: str) -> list:
    """List build learnings"""
    data = load_build_learnings(slug)
    return data.get("learnings", [])


def list_system_learnings() -> list:
    """List system learnings"""
    data = load_system_learnings()
    return data.get("learnings", [])


def promote_learning(slug: str, index: int):
    """Promote a build learning to system level"""
    build_data = load_build_learnings(slug)
    learnings = build_data.get("learnings", [])
    
    if index < 0 or index >= len(learnings):
        print(f"Invalid index {index}. Build has {len(learnings)} learnings.")
        return False
    
    learning = learnings[index].copy()
    learning["origin_build"] = slug
    learning["promoted_at"] = datetime.now(timezone.utc).isoformat()
    
    system_data = load_system_learnings()
    system_data["learnings"].append(learning)
    save_system_learnings(system_data)
    
    print(f"Promoted to system: {learning['text'][:60]}...")
    return True


def get_relevant_learnings(slug: str, tags: list = None) -> list:
    """Get system learnings relevant to a build (by tags or all)"""
    system = load_system_learnings()
    learnings = system.get("learnings", [])
    
    if not tags:
        return learnings
    
    return [l for l in learnings if any(t in l.get("tags", []) for t in tags)]


def inject_learnings_into_brief(brief_path: Path, learnings: list) -> str:
    """Inject relevant learnings into a Drop brief"""
    if not learnings:
        return None
    
    with open(brief_path) as f:
        content = f.read()
    
    # Check if already has learnings section
    if "## System Learnings" in content:
        return None  # Already injected
    
    learnings_section = "\n\n## System Learnings (Auto-Injected)\n\n"
    learnings_section += "Review these before starting:\n\n"
    for i, l in enumerate(learnings[:5]):  # Max 5
        learnings_section += f"- {l['text']}\n"
    
    # Insert before "## Requirements" or at end
    if "## Requirements" in content:
        content = content.replace("## Requirements", learnings_section + "## Requirements")
    else:
        content += learnings_section
    
    with open(brief_path, "w") as f:
        f.write(content)
    
    return brief_path


def inject_all_briefs(slug: str, tags: list = None):
    """Inject relevant system learnings into all Drop briefs for a build"""
    learnings = get_relevant_learnings(slug, tags)
    if not learnings:
        print("No relevant system learnings to inject.")
        return
    
    drops_dir = BUILDS_DIR / slug / "drops"
    if not drops_dir.exists():
        print(f"No drops directory for {slug}")
        return
    
    injected = 0
    for brief_path in drops_dir.glob("*.md"):
        result = inject_learnings_into_brief(brief_path, learnings)
        if result:
            injected += 1
            print(f"Injected learnings into {brief_path.name}")
    
    print(f"Injected into {injected} briefs.")


def extract_learnings_from_deposit(slug: str, drop_id: str) -> list:
    """Extract learnings from a Drop's deposit"""
    deposit_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}.json"
    if not deposit_path.exists():
        return []
    
    with open(deposit_path) as f:
        deposit = json.load(f)
    
    # Look for learnings field
    return deposit.get("learnings", [])


def harvest_build_learnings(slug: str):
    """Harvest all learnings from completed deposits"""
    deposits_dir = BUILDS_DIR / slug / "deposits"
    if not deposits_dir.exists():
        print(f"No deposits for {slug}")
        return
    
    harvested = 0
    for deposit_path in deposits_dir.glob("*.json"):
        if "_filter" in deposit_path.name:
            continue  # Skip filter results
        
        drop_id = deposit_path.stem
        learnings = extract_learnings_from_deposit(slug, drop_id)
        
        for learning_text in learnings:
            add_learning(slug, learning_text, source=f"Drop:{drop_id}")
            harvested += 1
    
    print(f"Harvested {harvested} learnings from {slug}")


def main():
    parser = argparse.ArgumentParser(description="Pulse Learnings Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a learning")
    add_parser.add_argument("slug", help="Build slug")
    add_parser.add_argument("text", help="Learning text")
    add_parser.add_argument("--system", action="store_true", help="Add to system level")
    add_parser.add_argument("--tags", nargs="*", help="Tags for categorization")
    
    # list
    list_parser = subparsers.add_parser("list", help="List build learnings")
    list_parser.add_argument("slug", help="Build slug")
    
    # list-system
    subparsers.add_parser("list-system", help="List system learnings")
    
    # promote
    promote_parser = subparsers.add_parser("promote", help="Promote build learning to system")
    promote_parser.add_argument("slug", help="Build slug")
    promote_parser.add_argument("index", type=int, help="Learning index")
    
    # inject
    inject_parser = subparsers.add_parser("inject", help="Inject system learnings into briefs")
    inject_parser.add_argument("slug", help="Build slug")
    inject_parser.add_argument("--tags", nargs="*", help="Filter by tags")
    
    # harvest
    harvest_parser = subparsers.add_parser("harvest", help="Harvest learnings from deposits")
    harvest_parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_learning(args.slug, args.text, system=args.system, tags=args.tags)
    
    elif args.command == "list":
        learnings = list_learnings(args.slug)
        if not learnings:
            print(f"No learnings for {args.slug}")
        else:
            print(f"\n{args.slug} Learnings ({len(learnings)}):\n")
            for i, l in enumerate(learnings):
                print(f"  [{i}] {l['text'][:80]}")
                print(f"      Source: {l.get('source', 'unknown')} | {l.get('added_at', '')[:10]}")
    
    elif args.command == "list-system":
        learnings = list_system_learnings()
        if not learnings:
            print("No system learnings")
        else:
            print(f"\nSystem Learnings ({len(learnings)}):\n")
            for i, l in enumerate(learnings):
                print(f"  [{i}] {l['text'][:80]}")
                origin = l.get('origin_build', 'manual')
                print(f"      Origin: {origin} | Tags: {l.get('tags', [])}")
    
    elif args.command == "promote":
        promote_learning(args.slug, args.index)
    
    elif args.command == "inject":
        inject_all_briefs(args.slug, args.tags)
    
    elif args.command == "harvest":
        harvest_build_learnings(args.slug)


if __name__ == "__main__":
    main()

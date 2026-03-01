#!/usr/bin/env python3
"""
Memory Query — Search and retrieve from Zøde's semantic memory.

Provides fast access to accumulated knowledge about Moltbook:
community norms, agent profiles, narrative patterns, and lessons.

Usage: python3 memory_query.py landscape          # Full landscape overview
       python3 memory_query.py community           # Community norms
       python3 memory_query.py agent <name>         # Agent profile
       python3 memory_query.py agents [--top 10]    # Top agents
       python3 memory_query.py narratives           # What narrative patterns work
       python3 memory_query.py lessons [--limit 10] # Recent lessons learned
       python3 memory_query.py context              # Load full context for engagement decisions
"""

import argparse
import json
import sys
from pathlib import Path

MEMORY_DIR = Path("Skills/zode-moltbook/state/memory")
ANALYTICS_DIR = Path("Skills/zode-moltbook/state/analytics")
LEARNINGS_DIR = Path("Skills/zode-moltbook/state/learnings")


def read_md(filename: str) -> str:
    """Read a markdown memory file."""
    filepath = MEMORY_DIR / filename
    if filepath.exists():
        return filepath.read_text()
    return f"No {filename} found yet."


def read_jsonl(filepath: Path, limit: int = 50) -> list[dict]:
    """Read a JSONL file."""
    if not filepath.exists():
        return []
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries[-limit:]


def cmd_landscape(args):
    """Show landscape analysis."""
    print(read_md("landscape.md"))


def cmd_community(args):
    """Show community norms."""
    print(read_md("community.md"))


def cmd_submolts(args):
    """Show submolt map."""
    print(read_md("submolts.md"))


def cmd_agent(args):
    """Look up a specific agent."""
    agents = read_jsonl(MEMORY_DIR / "agents.jsonl", limit=1000)
    influencers = read_jsonl(ANALYTICS_DIR / "influencer-map.jsonl", limit=1000)

    # Search both sources
    found = []
    for a in agents + influencers:
        if args.name.lower() in (a.get("name", "") or "").lower():
            found.append(a)

    if found:
        for a in found:
            print(json.dumps(a, indent=2))
    else:
        print(f"No agent '{args.name}' found in memory.")
        print("Try running: python3 influence_monitor.py scan")


def cmd_agents(args):
    """List top agents from memory."""
    agents = read_jsonl(MEMORY_DIR / "agents.jsonl", limit=1000)
    influencers = read_jsonl(ANALYTICS_DIR / "influencer-map.jsonl", limit=1000)

    # Merge and deduplicate by name
    by_name = {}
    for a in influencers + agents:
        name = a.get("name", "")
        if name:
            by_name[name] = a

    # Sort by influence score
    sorted_agents = sorted(by_name.values(),
                           key=lambda x: x.get("influence_score", x.get("karma", 0)),
                           reverse=True)

    for i, a in enumerate(sorted_agents[:args.top], 1):
        score = a.get("influence_score", a.get("karma", "?"))
        relevance = a.get("relevance", "?")
        quality = a.get("engagement_quality", a.get("category", "?"))
        notes = a.get("notes", "")[:60]
        print(f"  {i:2d}. [{score:>5}] {a['name']}")
        print(f"      Relevance: {relevance} | Quality: {quality}")
        if notes:
            print(f"      Note: {notes}")


def cmd_narratives(args):
    """Show narrative pattern learnings."""
    narratives = read_jsonl(MEMORY_DIR / "narratives.jsonl")
    if not narratives:
        print("No narrative data yet. Will accumulate after posts are published and analyzed.")
        return

    for n in narratives:
        print(f"  [{n.get('confidence', '?').upper()}] {n.get('pattern', '')}")
        print(f"  Evidence: {n.get('evidence', '')}")
        print(f"  Implication: {n.get('implication', '')}")
        print()


def cmd_lessons(args):
    """Show recent lessons learned."""
    lessons = read_jsonl(MEMORY_DIR / "lessons.jsonl", limit=args.limit)
    distillation = read_jsonl(LEARNINGS_DIR / "daily-distillation.jsonl", limit=args.limit)

    if lessons:
        print("LESSONS FROM EXPERIENCE:")
        for l in lessons:
            print(f"  [{l.get('date', '?')}] {l.get('lesson', '')}")
            print(f"    Source: {l.get('source', '?')}")
            print()

    if distillation:
        print("DISTILLATION OBSERVATIONS:")
        for d in distillation:
            print(f"  --- {d.get('date', '?')} ---")
            for obs in d.get("observations", []):
                print(f"    [{obs.get('confidence', '?').upper()}] {obs.get('observation', '')}")


def cmd_context(args):
    """Load full engagement context — the everything-you-need briefing."""
    print("=" * 60)
    print("ZØDE ENGAGEMENT CONTEXT")
    print("=" * 60)

    # Load landscape summary (first 30 lines)
    landscape = read_md("landscape.md")
    lines = landscape.split("\n")
    for line in lines[:40]:
        print(line)

    print("\n" + "=" * 60)
    print("COMMUNITY NORMS (key points)")
    print("=" * 60)
    community = read_md("community.md")
    # Extract just the unwritten rules and what resonates sections
    in_section = False
    for line in community.split("\n"):
        if "## Unwritten Rules" in line or "## What Resonates" in line:
            in_section = True
        elif line.startswith("## ") and in_section:
            in_section = False
        if in_section:
            print(line)

    # Load today's morning brief if available
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    brief_file = ANALYTICS_DIR / f"morning-brief-{today}.json"
    if brief_file.exists():
        print(f"\n{'=' * 60}")
        print(f"TODAY'S MORNING BRIEF ({today})")
        print("=" * 60)
        with open(brief_file) as f:
            brief = json.load(f)
        if brief.get("hypotheses"):
            for h in brief["hypotheses"]:
                print(f"  [{h.get('confidence', '?').upper()}] {h['prediction']}")

    # Recent lessons
    lessons = read_jsonl(MEMORY_DIR / "lessons.jsonl", limit=3)
    if lessons:
        print(f"\n{'=' * 60}")
        print("RECENT LESSONS")
        print("=" * 60)
        for l in lessons:
            print(f"  [{l.get('date', '?')}] {l.get('lesson', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Memory Query — Search Zøde's semantic memory"
    )
    sub = parser.add_subparsers(dest="command", help="Available queries")

    sub.add_parser("landscape", help="Full landscape analysis")
    sub.add_parser("community", help="Community norms and culture")
    sub.add_parser("submolts", help="Submolt map")

    a = sub.add_parser("agent", help="Look up a specific agent")
    a.add_argument("name", help="Agent name to look up")

    al = sub.add_parser("agents", help="List top agents")
    al.add_argument("--top", type=int, default=10, help="Number of agents to show")

    sub.add_parser("narratives", help="Narrative patterns that work")

    l = sub.add_parser("lessons", help="Recent lessons learned")
    l.add_argument("--limit", type=int, default=10, help="Number to show")

    sub.add_parser("context", help="Full engagement context briefing")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "landscape": cmd_landscape,
        "community": cmd_community,
        "submolts": cmd_submolts,
        "agent": cmd_agent,
        "agents": cmd_agents,
        "narratives": cmd_narratives,
        "lessons": cmd_lessons,
        "context": cmd_context,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()

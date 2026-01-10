#!/usr/bin/env python3
"""
Evolution Tracker: Detect and log when V's established ideas evolve.

Compares new edges against the Resonance Index to detect:
- domain_expansion: Same idea applied to new context/domain
- refinement: Idea sharpened, nuanced, or made more specific
- challenge: Idea questioned, contradicted, or tested
- abandonment: Idea explicitly dropped or superseded

Usage:
    # Analyze a batch of new edges for evolution events
    python3 evolution_tracker.py analyze --file /path/to/edges.jsonl
    
    # Check a single idea for evolution patterns
    python3 evolution_tracker.py check --idea "meaning-level-intelligence"
    
    # View evolution history for an idea
    python3 evolution_tracker.py history --idea "meaning-level-intelligence"
    
    # Generate evolution summary report
    python3 evolution_tracker.py report
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
N5_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = N5_ROOT / "data"
RESONANCE_INDEX_PATH = DATA_DIR / "resonance_index.json"
EVOLUTION_LOG_PATH = DATA_DIR / "evolution_log.jsonl"
EDGES_DB_PATH = DATA_DIR / "edges.db"

# Evolution types
EVOLUTION_TYPES = {
    "domain_expansion": "Same idea applied to new context/domain",
    "refinement": "Idea sharpened, nuanced, or made more specific",
    "challenge": "Idea questioned, contradicted, or tested",
    "abandonment": "Idea explicitly dropped or superseded"
}


def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(str(EDGES_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_resonance_index() -> Dict:
    """Load the resonance index."""
    if not RESONANCE_INDEX_PATH.exists():
        return {"cornerstones": [], "active_theses": [], "recurring_tools": [], "sparks": []}
    return json.loads(RESONANCE_INDEX_PATH.read_text())


def get_known_contexts(idea_slug: str) -> Set[str]:
    """Get all known contexts/domains for an idea from edges.db."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all evidence/contexts for this idea
    cursor.execute("""
        SELECT DISTINCT evidence, context_meeting_id
        FROM edges
        WHERE (source_type = 'idea' AND source_id = ?)
           OR (target_type = 'idea' AND target_id = ?)
    """, (idea_slug, idea_slug))
    
    contexts = set()
    for row in cursor.fetchall():
        if row['evidence']:
            # Extract domain keywords from evidence
            evidence_lower = row['evidence'].lower()
            # Common domain markers
            for domain in ['hiring', 'recruiting', 'sales', 'marketing', 'product', 
                          'engineering', 'ai', 'startup', 'enterprise', 'consumer',
                          'b2b', 'b2c', 'healthcare', 'fintech', 'edtech',
                          'personal', 'productivity', 'relationships', 'career']:
                if domain in evidence_lower:
                    contexts.add(domain)
    
    conn.close()
    return contexts


def get_idea_level(idea_slug: str, index: Dict) -> Optional[str]:
    """Get the resonance level for an idea."""
    for level, key in [("L0", "cornerstones"), ("L1", "active_theses"), 
                       ("L2", "recurring_tools"), ("L3", "sparks")]:
        for idea in index.get(key, []):
            if idea.get("idea_slug") == idea_slug:
                return level
    return None


def detect_evolution(edge: Dict, index: Dict) -> Optional[Dict]:
    """
    Analyze a single edge for evolution patterns.
    
    Returns evolution event dict if detected, None otherwise.
    """
    # Only track ideas
    idea_slug = None
    if edge.get("source_type") == "idea":
        idea_slug = edge.get("source_id")
    elif edge.get("target_type") == "idea":
        idea_slug = edge.get("target_id")
    
    if not idea_slug:
        return None
    
    # Get idea's current level
    level = get_idea_level(idea_slug, index)
    
    # Only track evolution for established ideas (L0, L1, L2)
    if level not in ["L0", "L1", "L2"]:
        return None
    
    relation = edge.get("relation", "")
    evidence = edge.get("evidence", "")
    meeting_id = edge.get("context_meeting_id", "")
    
    # Check for explicit evolution relation
    if relation == "evolves":
        return {
            "idea_slug": idea_slug,
            "evolution_type": edge.get("evolution_type", "refinement"),
            "evidence": evidence,
            "meeting_id": meeting_id,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "level": level
        }
    
    # Check for challenge (challenged_by relation)
    if relation == "challenged_by":
        return {
            "idea_slug": idea_slug,
            "evolution_type": "challenge",
            "challenger": edge.get("target_id") if edge.get("target_type") == "person" else None,
            "evidence": evidence,
            "meeting_id": meeting_id,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "level": level
        }
    
    # Check for domain expansion by comparing contexts
    known_contexts = get_known_contexts(idea_slug)
    evidence_lower = evidence.lower() if evidence else ""
    
    new_domains = []
    for domain in ['hiring', 'recruiting', 'sales', 'marketing', 'product', 
                  'engineering', 'ai', 'startup', 'enterprise', 'consumer',
                  'personal', 'productivity', 'relationships', 'career',
                  'healthcare', 'fintech', 'edtech']:
        if domain in evidence_lower and domain not in known_contexts:
            new_domains.append(domain)
    
    if new_domains:
        return {
            "idea_slug": idea_slug,
            "evolution_type": "domain_expansion",
            "from_domains": list(known_contexts)[:5],
            "to_domains": new_domains,
            "evidence": evidence,
            "meeting_id": meeting_id,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "level": level
        }
    
    return None


def log_evolution_event(event: Dict) -> None:
    """Append an evolution event to the log."""
    with open(EVOLUTION_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def analyze_edges_file(file_path: str) -> Dict:
    """Analyze a JSONL file of edges for evolution events."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    index = load_resonance_index()
    events = []
    edges_analyzed = 0
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                edge = json.loads(line)
                # Skip meta lines
                if edge.get("_meta"):
                    continue
                edges_analyzed += 1
                
                event = detect_evolution(edge, index)
                if event:
                    events.append(event)
                    log_evolution_event(event)
            except json.JSONDecodeError:
                continue
    
    return {
        "edges_analyzed": edges_analyzed,
        "evolution_events_detected": len(events),
        "events": events
    }


def check_idea_evolution(idea_slug: str) -> Dict:
    """Check evolution patterns for a specific idea."""
    index = load_resonance_index()
    level = get_idea_level(idea_slug, index)
    
    if not level:
        return {
            "idea_slug": idea_slug,
            "status": "unknown",
            "message": "Idea not found in resonance index"
        }
    
    known_contexts = get_known_contexts(idea_slug)
    
    # Get all edges involving this idea
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT relation, evidence, context_meeting_id, evolution_type, captured_at
        FROM edges
        WHERE (source_type = 'idea' AND source_id = ?)
           OR (target_type = 'idea' AND target_id = ?)
        ORDER BY captured_at DESC
        LIMIT 20
    """, (idea_slug, idea_slug))
    
    recent_edges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Count relation types
    relation_counts = defaultdict(int)
    for edge in recent_edges:
        relation_counts[edge['relation']] += 1
    
    return {
        "idea_slug": idea_slug,
        "level": level,
        "known_contexts": list(known_contexts),
        "recent_edges": len(recent_edges),
        "relation_distribution": dict(relation_counts),
        "evolution_edges": [e for e in recent_edges if e.get('evolution_type')]
    }


def get_idea_history(idea_slug: str) -> Dict:
    """Get full evolution history for an idea."""
    history = []
    
    if EVOLUTION_LOG_PATH.exists():
        with open(EVOLUTION_LOG_PATH) as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get("idea_slug") == idea_slug:
                        history.append(event)
                except json.JSONDecodeError:
                    continue
    
    # Sort by date
    history.sort(key=lambda x: x.get("detected_at", ""), reverse=True)
    
    return {
        "idea_slug": idea_slug,
        "evolution_count": len(history),
        "history": history
    }


def generate_evolution_report() -> str:
    """Generate a summary report of all evolution events."""
    if not EVOLUTION_LOG_PATH.exists():
        return "No evolution events recorded yet."
    
    events_by_type = defaultdict(list)
    events_by_idea = defaultdict(list)
    
    with open(EVOLUTION_LOG_PATH) as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                events_by_type[event.get("evolution_type", "unknown")].append(event)
                events_by_idea[event.get("idea_slug", "unknown")].append(event)
            except json.JSONDecodeError:
                continue
    
    lines = ["# Evolution Report", f"Generated: {datetime.now(timezone.utc).isoformat()}", ""]
    
    # Summary
    total = sum(len(v) for v in events_by_type.values())
    lines.append(f"**Total Evolution Events:** {total}")
    lines.append("")
    
    # By type
    lines.append("## By Evolution Type")
    for evo_type, desc in EVOLUTION_TYPES.items():
        count = len(events_by_type.get(evo_type, []))
        lines.append(f"- **{evo_type}** ({desc}): {count}")
    lines.append("")
    
    # Most evolved ideas
    lines.append("## Most Evolved Ideas")
    sorted_ideas = sorted(events_by_idea.items(), key=lambda x: -len(x[1]))[:10]
    for idea, events in sorted_ideas:
        types = [e.get("evolution_type", "?") for e in events]
        lines.append(f"- **{idea}**: {len(events)} events — {', '.join(types)}")
    lines.append("")
    
    # Recent events
    lines.append("## Recent Events (Last 10)")
    all_events = []
    for events in events_by_type.values():
        all_events.extend(events)
    all_events.sort(key=lambda x: x.get("detected_at", ""), reverse=True)
    
    for event in all_events[:10]:
        idea = event.get("idea_slug", "?")
        evo_type = event.get("evolution_type", "?")
        meeting = event.get("meeting_id", "?")
        lines.append(f"- [{evo_type}] **{idea}** — {meeting}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track evolution of V's ideas")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze edges file for evolution")
    analyze_parser.add_argument("--file", required=True, help="Path to JSONL edges file")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check evolution patterns for an idea")
    check_parser.add_argument("--idea", required=True, help="Idea slug to check")
    
    # History command
    history_parser = subparsers.add_parser("history", help="View evolution history for an idea")
    history_parser.add_argument("--idea", required=True, help="Idea slug")
    
    # Report command
    subparsers.add_parser("report", help="Generate evolution summary report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "analyze":
        result = analyze_edges_file(args.file)
        print(json.dumps(result, indent=2))
        
    elif args.command == "check":
        result = check_idea_evolution(args.idea)
        print(json.dumps(result, indent=2))
        
    elif args.command == "history":
        result = get_idea_history(args.idea)
        print(json.dumps(result, indent=2))
        
    elif args.command == "report":
        report = generate_evolution_report()
        print(report)


if __name__ == "__main__":
    main()


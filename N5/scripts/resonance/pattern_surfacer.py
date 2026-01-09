#!/usr/bin/env python3
"""
Pattern Surfacer: Analyze edges.db to classify ideas by resonance level.

Resonance Hierarchy:
- L0 Cornerstone: 10+ meetings (foundational beliefs)
- L1 Active Thesis: 4-9 meetings (developing ideas)
- L2 Recurring Tool: 2-3 meetings (frameworks V reaches for)
- L3 Spark: 1 meeting (novel ideas)

Usage:
    python3 pattern_surfacer.py generate     # Generate resonance_index.json
    python3 pattern_surfacer.py report       # Human-readable summary
    python3 pattern_surfacer.py stats        # Quick stats
"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Paths
N5_ROOT = Path("/home/workspace/N5")
EDGES_DB = N5_ROOT / "data" / "edges.db"
RESONANCE_INDEX = N5_ROOT / "data" / "resonance_index.json"
INSIGHTS_DIR = N5_ROOT / "insights" / "resonance"

# Thresholds (configurable)
THRESHOLDS = {
    "cornerstone": 10,  # L0: 10+ meetings
    "active_thesis": 4,  # L1: 4-9 meetings
    "recurring_tool": 2,  # L2: 2-3 meetings
    # L3 Spark: 1 meeting (implicit)
}


def get_db_connection():
    """Get SQLite connection."""
    return sqlite3.connect(EDGES_DB)


def get_idea_frequencies() -> Dict[str, Dict]:
    """
    Query edges.db for idea frequencies across extraction sessions.
    Returns dict of idea_slug -> {frequency, sessions, first_seen, last_seen, label, contexts}
    
    Note: context_meeting_id stores batch/session IDs (e.g., 'backfill-2026-01-05-1230'),
    which represent distinct extraction sessions. We count unique sessions as frequency.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all edges involving ideas with their session context
    cursor.execute("""
        SELECT 
            source_type, source_id, target_type, target_id,
            relation, context_meeting_id, evidence, created_at
        FROM edges
        WHERE source_type = 'idea' OR target_type = 'idea'
    """)
    
    rows = cursor.fetchall()
    
    # Also get entity labels directly
    cursor.execute("SELECT entity_id, name, created_at FROM entities WHERE entity_type = 'idea'")
    entity_rows = cursor.fetchall()
    entity_labels = {row[0]: row[1] for row in entity_rows}
    entity_dates = {row[0]: row[2] for row in entity_rows}
    
    # Process edges to build idea -> sessions mapping
    idea_sessions = defaultdict(set)
    idea_contexts = defaultdict(set)
    idea_dates = defaultdict(list)
    
    for row in rows:
        source_type, source_id, target_type, target_id, relation, session_id, evidence, created_at = row
        
        # Get the idea slug from either source or target
        idea_slug = None
        if source_type == 'idea':
            idea_slug = source_id
        elif target_type == 'idea':
            idea_slug = target_id
        
        if idea_slug:
            # Count any non-empty session_id as a unique extraction session
            if session_id:
                idea_sessions[idea_slug].add(session_id)
            if created_at:
                idea_dates[idea_slug].append(created_at)
            
            # Extract context keywords from evidence
            if evidence:
                words = evidence.lower().split()
                for word in words:
                    if len(word) > 4 and word not in ['about', 'their', 'which', 'would', 'could', 'being', 'there', 'these', 'those']:
                        idea_contexts[idea_slug].add(word[:20])
    
    conn.close()
    
    # Build frequency data
    ideas = {}
    for idea_slug, sessions in idea_sessions.items():
        dates = sorted(idea_dates.get(idea_slug, []))
        ideas[idea_slug] = {
            "idea_slug": idea_slug,
            "label": entity_labels.get(idea_slug, idea_slug.replace("-", " ").title()),
            "frequency": len(sessions),
            "sessions": sorted(list(sessions)),
            "first_seen": dates[0][:10] if dates else None,
            "last_seen": dates[-1][:10] if dates else None,
            "sample_contexts": list(idea_contexts.get(idea_slug, set()))[:5]
        }
    
    return ideas


def classify_ideas(ideas: Dict[str, Dict]) -> Dict[str, List]:
    """Classify ideas into resonance levels."""
    classified = {
        "cornerstones": [],      # L0: 10+
        "active_theses": [],     # L1: 4-9
        "recurring_tools": [],   # L2: 2-3
        "sparks": []             # L3: 1
    }
    
    for idea_slug, data in ideas.items():
        freq = data["frequency"]
        
        if freq >= THRESHOLDS["cornerstone"]:
            classified["cornerstones"].append(data)
        elif freq >= THRESHOLDS["active_thesis"]:
            classified["active_theses"].append(data)
        elif freq >= THRESHOLDS["recurring_tool"]:
            classified["recurring_tools"].append(data)
        else:
            classified["sparks"].append(data)
    
    # Sort each category by frequency descending
    for key in classified:
        classified[key] = sorted(classified[key], key=lambda x: -x["frequency"])
    
    return classified


def generate_resonance_index() -> Dict:
    """Generate the full resonance index."""
    ideas = get_idea_frequencies()
    classified = classify_ideas(ideas)
    
    index = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "thresholds": THRESHOLDS,
        "total_ideas": len(ideas),
        "summary": {
            "cornerstones": len(classified["cornerstones"]),
            "active_theses": len(classified["active_theses"]),
            "recurring_tools": len(classified["recurring_tools"]),
            "sparks": len(classified["sparks"])
        },
        **classified
    }
    
    return index


def save_index(index: Dict) -> Path:
    """Save resonance index to JSON."""
    RESONANCE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(RESONANCE_INDEX, "w") as f:
        json.dump(index, f, indent=2)
    return RESONANCE_INDEX


def generate_report(index: Dict) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("# Resonance Report")
    lines.append(f"Generated: {index['generated_at']}")
    lines.append(f"Total Ideas Tracked: {index['total_ideas']}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append(f"- **Cornerstones (L0)**: {index['summary']['cornerstones']} ideas (10+ meetings)")
    lines.append(f"- **Active Theses (L1)**: {index['summary']['active_theses']} ideas (4-9 meetings)")
    lines.append(f"- **Recurring Tools (L2)**: {index['summary']['recurring_tools']} ideas (2-3 meetings)")
    lines.append(f"- **Sparks (L3)**: {index['summary']['sparks']} ideas (1 meeting)")
    lines.append("")
    
    # Cornerstones
    if index["cornerstones"]:
        lines.append("## 🏛️ Cornerstones (L0) — Your Foundational Beliefs")
        lines.append("These are ideas you return to repeatedly. They define your intellectual identity.")
        lines.append("")
        for idea in index["cornerstones"][:15]:
            contexts = ", ".join(idea["sample_contexts"][:3]) if idea["sample_contexts"] else "various"
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings ({idea['first_seen']} → {idea['last_seen']})")
        lines.append("")
    
    # Active Theses
    if index["active_theses"]:
        lines.append("## 🔬 Active Theses (L1) — Ideas You're Developing")
        lines.append("These are ideas gaining traction. Watch for evolution or consolidation.")
        lines.append("")
        for idea in index["active_theses"][:15]:
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings ({idea['first_seen']} → {idea['last_seen']})")
        lines.append("")
    
    # Recurring Tools
    if index["recurring_tools"]:
        lines.append("## 🔧 Recurring Tools (L2) — Frameworks You Reach For")
        lines.append("These are mental models you apply. Note when they appear in new domains.")
        lines.append("")
        for idea in index["recurring_tools"][:15]:
            lines.append(f"- **{idea['label']}** — {idea['frequency']} meetings")
        lines.append("")
    
    # Recent Sparks (only last 20)
    if index["sparks"]:
        lines.append("## ✨ Recent Sparks (L3) — Novel Ideas")
        lines.append("These appeared once. Candidates for exploration or naturally fleeting.")
        lines.append("")
        # Sort sparks by last_seen descending to show most recent
        recent_sparks = sorted(index["sparks"], key=lambda x: x["last_seen"] or "", reverse=True)[:20]
        for idea in recent_sparks:
            lines.append(f"- **{idea['label']}** — {idea['last_seen'] or 'unknown'}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pattern Surfacer for Resonance Reservoir")
    parser.add_argument("command", choices=["generate", "report", "stats", "json"],
                       help="Command to run")
    parser.add_argument("--output", "-o", help="Output file for report")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        index = generate_resonance_index()
        path = save_index(index)
        print(json.dumps({
            "status": "generated",
            "path": str(path),
            "summary": index["summary"],
            "total_ideas": index["total_ideas"]
        }, indent=2))
        
    elif args.command == "report":
        index = generate_resonance_index()
        save_index(index)  # Also save the index
        report = generate_report(index)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report)
            print(f"Report saved to: {output_path}")
        else:
            print(report)
            
    elif args.command == "stats":
        index = generate_resonance_index()
        print(json.dumps({
            "total_ideas": index["total_ideas"],
            **index["summary"]
        }, indent=2))
        
    elif args.command == "json":
        index = generate_resonance_index()
        print(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()





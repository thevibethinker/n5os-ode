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
EDGES_DB_PATH = Path("/home/workspace/N5/cognition/brain.db")

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
    """Get all known contexts/domains for an idea from brain.db."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all evidence/contexts for this idea
    cursor.execute("""
        SELECT DISTINCT evidence, context_meeting_id
        FROM meeting_edges
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
        FROM meeting_edges
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


def get_challenge_status(idea_slug: Optional[str] = None) -> Dict:
    """
    Query challenged_by edges with challenger identity, date, evidence, and resolution status.
    
    Args:
        idea_slug: Optional - filter to specific idea. If None, returns all challenges.
        
    Returns:
        Dict with challenges grouped by resolution status (pending, resolved, abandoned)
        and summary statistics including stale challenges (30+ days unresolved).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query
    if idea_slug:
        cursor.execute("""
            SELECT 
                id,
                source_type,
                source_id,
                target_id as challenger_id,
                evidence,
                context_meeting_id,
                captured_at,
                resolution_status,
                outcome_note
            FROM meeting_edges
            WHERE relation = 'challenged_by'
              AND source_id = ?
            ORDER BY captured_at DESC
        """, (idea_slug,))
    else:
        cursor.execute("""
            SELECT 
                id,
                source_type,
                source_id,
                target_id as challenger_id,
                evidence,
                context_meeting_id,
                captured_at,
                resolution_status,
                outcome_note
            FROM meeting_edges
            WHERE relation = 'challenged_by'
            ORDER BY captured_at DESC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by resolution status
    challenges = {
        "pending": [],
        "resolved": [],
        "abandoned": []
    }
    
    stale_threshold_days = 30
    now = datetime.now(timezone.utc)
    stale_challenges = []
    
    for row in rows:
        challenge = {
            "edge_id": row["id"],
            "entity_type": row["source_type"],
            "entity_id": row["source_id"],
            "challenger": row["challenger_id"],
            "evidence": row["evidence"],
            "meeting_id": row["context_meeting_id"],
            "captured_at": row["captured_at"],
            "resolution_status": row["resolution_status"] or "pending",
            "resolution_note": row["outcome_note"]
        }
        
        status = challenge["resolution_status"]
        if status in challenges:
            challenges[status].append(challenge)
        else:
            challenges["pending"].append(challenge)
        
        # Check for stale (30+ days unresolved)
        if status == "pending" and row["captured_at"]:
            try:
                captured = datetime.fromisoformat(row["captured_at"].replace("Z", "+00:00"))
                if hasattr(captured, 'tzinfo') and captured.tzinfo is None:
                    captured = captured.replace(tzinfo=timezone.utc)
                days_old = (now - captured).days
                if days_old >= stale_threshold_days:
                    challenge["days_unresolved"] = days_old
                    stale_challenges.append(challenge)
            except (ValueError, TypeError):
                pass
    
    return {
        "idea_slug": idea_slug,
        "total_challenges": len(rows),
        "by_status": {
            "pending": len(challenges["pending"]),
            "resolved": len(challenges["resolved"]),
            "abandoned": len(challenges["abandoned"])
        },
        "challenges": challenges,
        "stale_challenges": stale_challenges,
        "stale_count": len(stale_challenges)
    }


def resolve_challenge(edge_id: int, resolution: str, note: Optional[str] = None) -> Dict:
    """
    Update resolution status for a challenge.
    
    Args:
        edge_id: The edge ID of the challenge
        resolution: One of 'resolved' (idea strengthened), 'abandoned' (challenge won), 'pending'
        note: Optional note explaining the resolution
        
    Returns:
        Success/failure status
    """
    valid_resolutions = {"pending", "resolved", "abandoned"}
    if resolution not in valid_resolutions:
        return {"success": False, "error": f"Invalid resolution. Must be one of: {valid_resolutions}"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE meeting_edges
        SET resolution_status = ?,
            outcome_note = ?,
            updated_at = datetime('now')
        WHERE id = ? AND relation = 'challenged_by'
    """, (resolution, note, edge_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected == 0:
        return {"success": False, "error": "Edge not found or not a challenge"}
    
    return {"success": True, "edge_id": edge_id, "resolution": resolution}


# ============================================================================
# PHASE 4: Idea Genealogy
# ============================================================================

def build_genealogy(idea_id: str) -> Dict:
    """
    Build the genealogy tree for an idea: ancestors, descendants, and siblings.
    
    Uses the 'derives_from' edge type where:
    - derives_from: child -> parent (child derives_from parent)
    - spawned: inverse relation (parent spawned child)
    
    Returns:
        {
            'idea_id': str,
            'ancestors': [list of parent ideas, oldest first],
            'descendants': [list of child ideas],
            'siblings': [ideas sharing the same parent],
            'lineage_depth': int (how many generations back)
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get ancestors: walk up derives_from chain (transitive closure)
    ancestors = []
    current = idea_id
    visited = {idea_id}  # Prevent cycles
    
    while True:
        # Find parent: idea derives_from X means X is parent
        cursor.execute("""
            SELECT target_id, evidence, context_meeting_id
            FROM meeting_edges
            WHERE source_type = 'idea' 
              AND source_id = ?
              AND target_type = 'idea'
              AND relation = 'derives_from'
              AND status = 'active'
            LIMIT 1
        """, (current,))
        
        row = cursor.fetchone()
        if not row or row['target_id'] in visited:
            break
        
        parent_id = row['target_id']
        ancestors.append({
            'idea_id': parent_id,
            'evidence': row['evidence'],
            'meeting_id': row['context_meeting_id']
        })
        visited.add(parent_id)
        current = parent_id
    
    # Reverse so oldest ancestor is first
    ancestors = list(reversed(ancestors))
    
    # Get descendants: find all ideas that derive from this one (direct children)
    cursor.execute("""
        SELECT source_id, evidence, context_meeting_id
        FROM meeting_edges
        WHERE target_type = 'idea'
          AND target_id = ?
          AND source_type = 'idea'
          AND relation = 'derives_from'
          AND status = 'active'
    """, (idea_id,))
    
    descendants = [
        {
            'idea_id': row['source_id'],
            'evidence': row['evidence'],
            'meeting_id': row['context_meeting_id']
        }
        for row in cursor.fetchall()
    ]
    
    # Get siblings: ideas that share the same parent
    siblings = []
    
    # First, find the direct parent of this idea
    cursor.execute("""
        SELECT target_id
        FROM meeting_edges
        WHERE source_type = 'idea'
          AND source_id = ?
          AND target_type = 'idea'
          AND relation = 'derives_from'
          AND status = 'active'
        LIMIT 1
    """, (idea_id,))
    
    parent_row = cursor.fetchone()
    if parent_row:
        parent_id = parent_row['target_id']
        
        # Find all other children of this parent
        cursor.execute("""
            SELECT source_id, evidence
            FROM meeting_edges
            WHERE target_type = 'idea'
              AND target_id = ?
              AND source_type = 'idea'
              AND relation = 'derives_from'
              AND source_id != ?
              AND status = 'active'
        """, (parent_id, idea_id))
        
        siblings = [
            {
                'idea_id': row['source_id'],
                'shared_parent': parent_id
            }
            for row in cursor.fetchall()
        ]
    
    conn.close()
    
    return {
        'idea_id': idea_id,
        'ancestors': ancestors,
        'descendants': descendants,
        'siblings': siblings,
        'lineage_depth': len(ancestors)
    }


def detect_potential_duplicates(co_occurrence_threshold: float = 0.70) -> List[Dict]:
    """
    Detect potential duplicate ideas based on high co-occurrence + similar edge patterns.
    
    Two ideas are flagged as potential duplicates if:
    1. They co-occur in >70% of their combined meetings
    2. They have similar edge patterns (same people supporting/challenging, similar evidence)
    
    Returns:
        List of potential duplicate pairs with confidence scores
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all ideas and their meeting counts
    cursor.execute("""
        SELECT DISTINCT 
            CASE WHEN source_type='idea' THEN source_id 
                 WHEN target_type='idea' THEN target_id 
            END as idea_id,
            context_meeting_id
        FROM meeting_edges
        WHERE (source_type = 'idea' OR target_type = 'idea')
          AND context_meeting_id IS NOT NULL
    """)
    
    # Build idea -> meetings mapping
    idea_meetings = defaultdict(set)
    for row in cursor.fetchall():
        if row['idea_id'] and row['context_meeting_id']:
            idea_meetings[row['idea_id']].add(row['context_meeting_id'])
    
    # Get edge patterns for each idea (who supports/challenges, what relations)
    cursor.execute("""
        SELECT 
            CASE WHEN source_type='idea' THEN source_id ELSE target_id END as idea_id,
            relation,
            CASE WHEN source_type='person' THEN source_id 
                 WHEN target_type='person' THEN target_id 
                 ELSE NULL END as person_id
        FROM meeting_edges
        WHERE source_type = 'idea' OR target_type = 'idea'
    """)
    
    idea_patterns = defaultdict(lambda: {'relations': defaultdict(int), 'people': set()})
    for row in cursor.fetchall():
        idea_id = row['idea_id']
        if idea_id:
            idea_patterns[idea_id]['relations'][row['relation']] += 1
            if row['person_id']:
                idea_patterns[idea_id]['people'].add(row['person_id'])
    
    conn.close()
    
    # Find potential duplicates
    duplicates = []
    ideas = list(idea_meetings.keys())
    
    for i, idea_a in enumerate(ideas):
        for idea_b in ideas[i+1:]:
            meetings_a = idea_meetings[idea_a]
            meetings_b = idea_meetings[idea_b]
            
            # Skip if either has too few meetings
            if len(meetings_a) < 2 or len(meetings_b) < 2:
                continue
            
            # Calculate co-occurrence rate
            shared = meetings_a & meetings_b
            union = meetings_a | meetings_b
            co_occurrence_rate = len(shared) / len(union) if union else 0
            
            if co_occurrence_rate >= co_occurrence_threshold:
                # Check edge pattern similarity
                pattern_a = idea_patterns[idea_a]
                pattern_b = idea_patterns[idea_b]
                
                # People overlap
                people_a = pattern_a['people']
                people_b = pattern_b['people']
                people_overlap = len(people_a & people_b) / len(people_a | people_b) if (people_a | people_b) else 0
                
                # Relation type overlap
                rels_a = set(pattern_a['relations'].keys())
                rels_b = set(pattern_b['relations'].keys())
                rel_overlap = len(rels_a & rels_b) / len(rels_a | rels_b) if (rels_a | rels_b) else 0
                
                # Combined score
                edge_similarity = (people_overlap + rel_overlap) / 2
                confidence = (co_occurrence_rate + edge_similarity) / 2
                
                if edge_similarity > 0.3:  # Some edge pattern similarity required
                    duplicates.append({
                        'idea_a': idea_a,
                        'idea_b': idea_b,
                        'co_occurrence_rate': round(co_occurrence_rate, 3),
                        'edge_similarity': round(edge_similarity, 3),
                        'confidence': round(confidence, 3),
                        'shared_meetings': len(shared),
                        'shared_people': list(people_a & people_b)[:5]  # Limit for readability
                    })
    
    # Sort by confidence descending
    duplicates.sort(key=lambda x: -x['confidence'])
    
    return duplicates


def get_ideas_with_lineage() -> List[Dict]:
    """
    Get all ideas that have derives_from relationships (for reporting).
    
    Returns list of ideas with their genealogy summary.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find all ideas involved in derives_from relationships
    cursor.execute("""
        SELECT DISTINCT source_id as idea_id FROM edges 
        WHERE relation = 'derives_from' AND source_type = 'idea'
        UNION
        SELECT DISTINCT target_id as idea_id FROM edges 
        WHERE relation = 'derives_from' AND target_type = 'idea'
    """)
    
    ideas_with_lineage = [row['idea_id'] for row in cursor.fetchall()]
    conn.close()
    
    # Build genealogy for each
    results = []
    for idea_id in ideas_with_lineage:
        genealogy = build_genealogy(idea_id)
        results.append({
            'idea_id': idea_id,
            'ancestor_count': len(genealogy['ancestors']),
            'descendant_count': len(genealogy['descendants']),
            'sibling_count': len(genealogy['siblings']),
            'lineage_depth': genealogy['lineage_depth'],
            'is_root': len(genealogy['ancestors']) == 0 and len(genealogy['descendants']) > 0,
            'is_leaf': len(genealogy['descendants']) == 0 and len(genealogy['ancestors']) > 0
        })
    
    return results


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
    
    # === UNDER CHALLENGE SECTION ===
    challenge_status = get_challenge_status()
    lines.append("## Under Challenge")
    lines.append(f"**Total Challenges:** {challenge_status['total_challenges']}")
    lines.append(f"- Pending: {challenge_status['by_status']['pending']}")
    lines.append(f"- Resolved (idea strengthened): {challenge_status['by_status']['resolved']}")
    lines.append(f"- Abandoned (challenge won): {challenge_status['by_status']['abandoned']}")
    lines.append("")
    
    # Stale challenges (30+ days unresolved)
    if challenge_status['stale_challenges']:
        lines.append("### ⚠️ Needs Attention (30+ days unresolved)")
        for c in challenge_status['stale_challenges']:
            lines.append(f"- **{c['entity_id']}** challenged by **{c['challenger']}** ({c['days_unresolved']} days)")
            if c['evidence']:
                evidence_preview = c['evidence'][:100] + "..." if len(c['evidence']) > 100 else c['evidence']
                lines.append(f"  - _{evidence_preview}_")
        lines.append("")
    
    # Active pending challenges
    pending = challenge_status['challenges']['pending']
    if pending:
        lines.append("### Pending Challenges")
        for c in pending[:10]:  # Show top 10
            lines.append(f"- **{c['entity_id']}** ← challenged by **{c['challenger']}**")
            if c['evidence']:
                evidence_preview = c['evidence'][:80] + "..." if len(c['evidence']) > 80 else c['evidence']
                lines.append(f"  - _{evidence_preview}_")
            if c['meeting_id']:
                lines.append(f"  - Meeting: {c['meeting_id']}")
        if len(pending) > 10:
            lines.append(f"  - _...and {len(pending) - 10} more_")
        lines.append("")
    
    # Recently resolved
    resolved = challenge_status['challenges']['resolved']
    if resolved:
        lines.append("### Recently Resolved (Idea Strengthened)")
        for c in resolved[:5]:
            lines.append(f"- **{c['entity_id']}** - challenge from {c['challenger']} resolved")
            if c['resolution_note']:
                lines.append(f"  - Note: {c['resolution_note']}")
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
    
    # Challenges command
    challenges_parser = subparsers.add_parser("challenges", help="View challenge status")
    challenges_parser.add_argument("--idea", required=False, help="Filter to specific idea slug")
    challenges_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a challenge")
    resolve_parser.add_argument("--edge-id", type=int, required=True, help="Edge ID of the challenge")
    resolve_parser.add_argument("--status", required=True, choices=["resolved", "abandoned", "pending"],
                               help="Resolution status: resolved (idea strengthened), abandoned (challenge won), pending")
    resolve_parser.add_argument("--note", required=False, help="Resolution note")
    
    # Genealogy command
    genealogy_parser = subparsers.add_parser("genealogy", help="View idea genealogy")
    genealogy_parser.add_argument("--idea", required=True, help="Idea slug")
    genealogy_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    # Duplicates command
    duplicates_parser = subparsers.add_parser("duplicates", help="Detect potential duplicate ideas")
    duplicates_parser.add_argument("--threshold", type=float, default=0.70, help="Co-occurrence threshold (default 0.70)")
    duplicates_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    # Lineage command - show all ideas with genealogy relationships
    subparsers.add_parser("lineage", help="Show all ideas with genealogy relationships")
    
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
    
    elif args.command == "challenges":
        result = get_challenge_status(args.idea)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            # Text format
            print(f"Challenge Status {'for ' + args.idea if args.idea else '(all ideas)'}")
            print(f"Total: {result['total_challenges']}")
            print(f"  Pending: {result['by_status']['pending']}")
            print(f"  Resolved: {result['by_status']['resolved']}")
            print(f"  Abandoned: {result['by_status']['abandoned']}")
            if result['stale_challenges']:
                print(f"\n⚠️  Stale ({result['stale_count']} need attention):")
                for c in result['stale_challenges']:
                    print(f"  - {c['entity_id']} ← {c['challenger']} ({c['days_unresolved']}d)")
    
    elif args.command == "resolve":
        result = resolve_challenge(args.edge_id, args.status, args.note)
        if result['success']:
            print(f"✓ Challenge {args.edge_id} marked as {args.status}")
        else:
            print(f"✗ Error: {result['error']}")
    
    elif args.command == "genealogy":
        result = build_genealogy(args.idea)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            # Text format with lineage visualization
            print(f"Genealogy for: {args.idea}")
            print(f"Lineage depth: {result['lineage_depth']}")
            print()
            
            if result['ancestors']:
                print("📜 Ancestors (oldest → recent):")
                for i, a in enumerate(result['ancestors']):
                    indent = "  " * i
                    print(f"{indent}↳ {a['idea_id']}")
                    if a.get('evidence'):
                        evidence_preview = a['evidence'][:60] + "..." if len(a['evidence']) > 60 else a['evidence']
                        print(f"{indent}  _{evidence_preview}_")
            else:
                print("📜 No ancestors (this is a root idea)")
            
            print()
            print(f"→ **{args.idea}** ← (target idea)")
            print()
            
            if result['descendants']:
                print("🌱 Descendants (direct children):")
                for d in result['descendants']:
                    print(f"  ↳ {d['idea_id']}")
                    if d.get('evidence'):
                        evidence_preview = d['evidence'][:60] + "..." if len(d['evidence']) > 60 else d['evidence']
                        print(f"    _{evidence_preview}_")
            else:
                print("🌱 No descendants")
            
            if result['siblings']:
                print()
                print("👥 Siblings (same parent):")
                for s in result['siblings']:
                    print(f"  - {s['idea_id']} (from {s['shared_parent']})")
    
    elif args.command == "duplicates":
        result = detect_potential_duplicates(args.threshold)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if not result:
                print("No potential duplicates detected.")
            else:
                print(f"⚠️  Potential Duplicates Detected ({len(result)} pairs)")
                print(f"Threshold: {args.threshold * 100:.0f}% co-occurrence\n")
                for dup in result:
                    print(f"🔍 {dup['idea_a']} ↔ {dup['idea_b']}")
                    print(f"   Co-occurrence: {dup['co_occurrence_rate']*100:.1f}% ({dup['shared_meetings']} meetings)")
                    print(f"   Edge similarity: {dup['edge_similarity']*100:.1f}%")
                    print(f"   Confidence: {dup['confidence']*100:.1f}%")
                    if dup['shared_people']:
                        print(f"   Shared people: {', '.join(dup['shared_people'][:3])}")
                    print()
    
    elif args.command == "lineage":
        result = get_ideas_with_lineage()
        if not result:
            print("No ideas with genealogy relationships found.")
        else:
            print(f"Ideas with Lineage ({len(result)} total)\n")
            
            # Group by type
            roots = [r for r in result if r['is_root']]
            leaves = [r for r in result if r['is_leaf']]
            middle = [r for r in result if not r['is_root'] and not r['is_leaf']]
            
            if roots:
                print("🌳 Root Ideas (originated new lineages):")
                for r in roots:
                    print(f"  - {r['idea_id']} → {r['descendant_count']} descendants")
                print()
            
            if middle:
                print("🔗 Bridge Ideas (have both ancestors and descendants):")
                for r in middle:
                    print(f"  - {r['idea_id']} (depth {r['lineage_depth']}, {r['descendant_count']} children)")
                print()
            
            if leaves:
                print("🍃 Leaf Ideas (most evolved, no children yet):")
                for r in leaves:
                    print(f"  - {r['idea_id']} (depth {r['lineage_depth']})")


if __name__ == "__main__":
    main()








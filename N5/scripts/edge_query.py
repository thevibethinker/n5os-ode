#!/usr/bin/env python3
"""
Edge Query: Query the context graph for provenance, relationships, and traces.

Usage:
    # Where did this idea come from?
    python3 edge_query.py trace --entity "idea:context-graph"
    
    # Who has influenced my thinking?
    python3 edge_query.py find --relation "influenced_by" --target-type "person"
    
    # What edges came from this meeting?
    python3 edge_query.py meeting --id "mtg_2026-01-04"
    
    # All edges involving a person
    python3 edge_query.py person --id "animesh-koratana"
    
    # Find edges by entity
    python3 edge_query.py find --source "idea:context-graph"
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from edge_types import get_inverse, EdgeCategory, EDGE_TYPES

DB_PATH = Path("/home/workspace/N5/cognition/brain.db")


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite Row to dict."""
    return dict(row)


def find_edges(
    source: Optional[str] = None,
    target: Optional[str] = None,
    relation: Optional[str] = None,
    source_type: Optional[str] = None,
    target_type: Optional[str] = None,
    status: str = "active",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find edges matching criteria.
    
    Args:
        source: Full source reference (type:id)
        target: Full target reference (type:id)
        relation: Relation type to filter
        source_type: Filter by source entity type
        target_type: Filter by target entity type
        status: Edge status (default: active)
        limit: Max results
    
    Returns:
        List of matching edges
    """
    conn = get_connection()
    try:
        query = "SELECT * FROM edges_resolved WHERE 1=1"
        params = []
        
        if source:
            s_type, s_id = source.split(':', 1)
            query += " AND source_type = ? AND source_id = ?"
            params.extend([s_type, s_id])
        
        if target:
            t_type, t_id = target.split(':', 1)
            query += " AND target_type = ? AND target_id = ?"
            params.extend([t_type, t_id])
        
        if relation:
            query += " AND relation = ?"
            params.append(relation)
        
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        
        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def trace_provenance(entity: str, depth: int = 5) -> Dict[str, Any]:
    """
    Trace the provenance chain of an entity.
    
    Follows: originated_by, influenced_by, preceded_by
    
    Args:
        entity: Entity reference (type:id)
        depth: Max trace depth
    
    Returns:
        Dict with chain and all edges found
    """
    provenance_relations = ["originated_by", "influenced_by", "preceded_by"]
    
    conn = get_connection()
    try:
        visited = set()
        chain = []
        all_edges = []
        
        def trace(current: str, current_depth: int):
            if current_depth > depth or current in visited:
                return
            
            visited.add(current)
            c_type, c_id = current.split(':', 1)
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM edges_resolved 
                WHERE source_type = ? AND source_id = ? 
                AND relation IN (?, ?, ?)
                AND status = 'active'
            """, (c_type, c_id, *provenance_relations))
            
            for row in cursor.fetchall():
                edge = row_to_dict(row)
                all_edges.append(edge)
                
                target_ref = f"{edge['target_type']}:{edge['target_id']}"
                chain.append({
                    "from": current,
                    "relation": edge['relation'],
                    "to": target_ref,
                    "evidence": edge.get('evidence')
                })
                
                # Continue tracing from target
                trace(target_ref, current_depth + 1)
        
        trace(entity, 0)
        
        return {
            "query": f"trace {entity}",
            "entity": entity,
            "depth_searched": depth,
            "chain": chain,
            "edges_found": len(all_edges),
            "edges": all_edges
        }
    finally:
        conn.close()


def trace_outcomes(entity: str) -> Dict[str, Any]:
    """
    Find expectations (hoped_for, concerned_about) and their validation status.
    
    Args:
        entity: Entity reference (type:id) - typically a decision or idea
    
    Returns:
        Dict with expectations and their outcomes
    """
    conn = get_connection()
    try:
        e_type, e_id = entity.split(':', 1)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM edges 
            WHERE source_type = ? AND source_id = ? 
            AND relation IN ('hoped_for', 'concerned_about')
        """, (e_type, e_id))
        
        expectations = []
        for row in cursor.fetchall():
            edge = row_to_dict(row)
            expectations.append({
                "expectation_type": edge['relation'],
                "description": edge['evidence'],
                "target": f"{edge['target_type']}:{edge['target_id']}",
                "outcome_status": edge.get('outcome_status', 'pending'),
                "outcome_note": edge.get('outcome_note'),
                "created_at": edge['created_at']
            })
        
        return {
            "query": f"outcomes {entity}",
            "entity": entity,
            "expectations": expectations,
            "summary": {
                "total": len(expectations),
                "validated": sum(1 for e in expectations if e['outcome_status'] == 'validated'),
                "invalidated": sum(1 for e in expectations if e['outcome_status'] == 'invalidated'),
                "pending": sum(1 for e in expectations if e['outcome_status'] == 'pending')
            }
        }
    finally:
        conn.close()


def find_by_person(person_id: str, relation: Optional[str] = None) -> Dict[str, Any]:
    """
    Find all edges involving a person (as source or target).
    
    Args:
        person_id: Person slug (without 'person:' prefix)
        relation: Optional relation filter
    
    Returns:
        Edges grouped by direction (from_person, to_person)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Edges FROM this person
        from_query = """
            SELECT * FROM edges_resolved 
            WHERE source_type = 'person' AND source_id = ?
            AND status = 'active'
        """
        from_params = [person_id]
        
        if relation:
            from_query += " AND relation = ?"
            from_params.append(relation)
        
        cursor.execute(from_query, from_params)
        from_edges = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Edges TO this person
        to_query = """
            SELECT * FROM edges_resolved 
            WHERE target_type = 'person' AND target_id = ?
            AND status = 'active'
        """
        to_params = [person_id]
        
        if relation:
            to_query += " AND relation = ?"
            to_params.append(relation)
        
        cursor.execute(to_query, to_params)
        to_edges = [row_to_dict(row) for row in cursor.fetchall()]
        
        return {
            "query": f"person {person_id}" + (f" relation={relation}" if relation else ""),
            "person": f"person:{person_id}",
            "from_person": from_edges,
            "to_person": to_edges,
            "summary": {
                "total_edges": len(from_edges) + len(to_edges),
                "as_source": len(from_edges),
                "as_target": len(to_edges)
            }
        }
    finally:
        conn.close()


def find_by_meeting(meeting_id: str) -> Dict[str, Any]:
    """
    Find all edges captured in a specific meeting.
    
    Args:
        meeting_id: Meeting identifier
    
    Returns:
        All edges from that meeting
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM edges_resolved 
            WHERE context_meeting_id = ?
            ORDER BY created_at
        """, (meeting_id,))
        
        edges = [row_to_dict(row) for row in cursor.fetchall()]
        
        # Group by relation type
        by_relation = defaultdict(list)
        for edge in edges:
            by_relation[edge['relation']].append(edge)
        
        return {
            "query": f"meeting {meeting_id}",
            "meeting_id": meeting_id,
            "edges": edges,
            "by_relation": dict(by_relation),
            "summary": {
                "total_edges": len(edges),
                "relation_counts": {k: len(v) for k, v in by_relation.items()}
            }
        }
    finally:
        conn.close()


def get_influence_map(target_type: str = "person", target_id: str = "vrijen") -> Dict[str, Any]:
    """
    Build influence map showing who/what has shaped thinking.
    
    Args:
        target_type: Usually 'person'
        target_id: Usually 'vrijen'
    
    Returns:
        Ranked list of influences
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Find all things V has been influenced by
        cursor.execute("""
            SELECT 
                target_type,
                target_id,
                COUNT(*) as influence_count,
                GROUP_CONCAT(DISTINCT source_id) as influenced_items
            FROM edges 
            WHERE relation = 'influenced_by'
            AND status = 'active'
            GROUP BY target_type, target_id
            ORDER BY influence_count DESC
        """)
        
        influences = []
        for row in cursor.fetchall():
            influences.append({
                "influencer": f"{row['target_type']}:{row['target_id']}",
                "influence_count": row['influence_count'],
                "influenced_items": row['influenced_items'].split(',') if row['influenced_items'] else []
            })
        
        return {
            "query": "influence_map",
            "influences": influences,
            "top_influencer": influences[0] if influences else None
        }
    finally:
        conn.close()


def get_stats() -> Dict[str, Any]:
    """Get summary statistics of the graph."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Edge counts by relation
        cursor.execute("""
            SELECT relation, COUNT(*) as count 
            FROM edges WHERE status = 'active'
            GROUP BY relation
        """)
        by_relation = {row['relation']: row['count'] for row in cursor.fetchall()}
        
        # Entity counts by type
        cursor.execute("""
            SELECT entity_type, COUNT(*) as count 
            FROM entities 
            GROUP BY entity_type
        """)
        by_entity = {row['entity_type']: row['count'] for row in cursor.fetchall()}
        
        # Total active edges
        cursor.execute("SELECT COUNT(*) FROM edges WHERE status = 'active'")
        total_edges = cursor.fetchone()[0]
        
        # Edges with outcomes
        cursor.execute("SELECT COUNT(*) FROM edges WHERE outcome_status IS NOT NULL")
        with_outcomes = cursor.fetchone()[0]
        
        return {
            "total_active_edges": total_edges,
            "total_entities": sum(by_entity.values()),
            "edges_by_relation": by_relation,
            "entities_by_type": by_entity,
            "edges_with_outcomes": with_outcomes
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Edge Query: Query context graph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Find edges
    find_parser = subparsers.add_parser("find", help="Find edges by criteria")
    find_parser.add_argument("--source", help="Source entity (type:id)")
    find_parser.add_argument("--target", help="Target entity (type:id)")
    find_parser.add_argument("--relation", help="Relation type")
    find_parser.add_argument("--source-type", help="Filter by source type")
    find_parser.add_argument("--target-type", help="Filter by target type")
    find_parser.add_argument("--status", default="active", help="Edge status")
    find_parser.add_argument("--limit", type=int, default=100, help="Max results")
    
    # Trace provenance
    trace_parser = subparsers.add_parser("trace", help="Trace provenance chain")
    trace_parser.add_argument("--entity", required=True, help="Entity to trace (type:id)")
    trace_parser.add_argument("--depth", type=int, default=5, help="Max trace depth")
    
    # Trace outcomes
    outcomes_parser = subparsers.add_parser("outcomes", help="Find expectations and outcomes")
    outcomes_parser.add_argument("--entity", required=True, help="Entity (type:id)")
    
    # Person lookup
    person_parser = subparsers.add_parser("person", help="Edges involving a person")
    person_parser.add_argument("--id", required=True, help="Person slug")
    person_parser.add_argument("--relation", help="Filter by relation")
    
    # Meeting lookup
    meeting_parser = subparsers.add_parser("meeting", help="Edges from a meeting")
    meeting_parser.add_argument("--id", required=True, help="Meeting ID")
    
    # Influence map
    influence_parser = subparsers.add_parser("influence", help="Build influence map")
    
    # Stats
    stats_parser = subparsers.add_parser("stats", help="Graph statistics")
    
    args = parser.parse_args()
    
    try:
        if args.command == "find":
            result = find_edges(
                source=args.source,
                target=args.target,
                relation=args.relation,
                source_type=args.source_type,
                target_type=args.target_type,
                status=args.status,
                limit=args.limit
            )
        elif args.command == "trace":
            result = trace_provenance(args.entity, args.depth)
        elif args.command == "outcomes":
            result = trace_outcomes(args.entity)
        elif args.command == "person":
            result = find_by_person(args.id, args.relation)
        elif args.command == "meeting":
            result = find_by_meeting(args.id)
        elif args.command == "influence":
            result = get_influence_map()
        elif args.command == "stats":
            result = get_stats()
        else:
            result = {"error": f"Unknown command: {args.command}"}
        
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


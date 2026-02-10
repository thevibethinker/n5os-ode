#!/usr/bin/env python3
"""
Edge Analysis: Extract insights from the context graph.

Usage:
    # Who generates ideas vs adopts them?
    python3 edge_analysis.py originated
    
    # What ideas have I supported vs challenged?
    python3 edge_analysis.py stance
    
    # Which hoped_for/concerned_about edges need outcome review?
    python3 edge_analysis.py outcomes
    
    # Find idea clusters (ideas that share originators or supporters)
    python3 edge_analysis.py clusters
    
    # Influence map: who influences my thinking?
    python3 edge_analysis.py influence
    
    # Decision chain: trace an idea back to its roots
    python3 edge_analysis.py chain --entity idea:context-graph-system
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DB_PATH = Path("/home/workspace/N5/cognition/brain.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def originated_vs_adopted():
    """Analyze who originates ideas vs who adopts/supports them."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all originated_by edges
    cursor.execute("""
        SELECT target_id, source_type, source_id, e.name as entity_name
        FROM meeting_edges
        JOIN entities e ON e.entity_type = 'person' AND e.entity_id = edges.target_id
        WHERE relation = 'originated_by' AND status = 'active'
    """)
    originated = cursor.fetchall()
    
    # Get all supported_by edges
    cursor.execute("""
        SELECT target_id, source_type, source_id, e.name as entity_name
        FROM meeting_edges
        JOIN entities e ON e.entity_type = 'person' AND e.entity_id = edges.target_id
        WHERE relation = 'supported_by' AND status = 'active'
    """)
    supported = cursor.fetchall()
    
    # Aggregate by person
    originators = defaultdict(list)
    supporters = defaultdict(list)
    
    for person_id, source_type, source_id, name in originated:
        originators[name or person_id].append(f"{source_type}:{source_id}")
    
    for person_id, source_type, source_id, name in supported:
        supporters[name or person_id].append(f"{source_type}:{source_id}")
    
    # Build report
    all_people = set(originators.keys()) | set(supporters.keys())
    report = {
        "analysis": "originated_vs_adopted",
        "people": []
    }
    
    for person in sorted(all_people):
        orig_count = len(originators.get(person, []))
        supp_count = len(supporters.get(person, []))
        total = orig_count + supp_count
        
        if total > 0:
            originator_ratio = orig_count / total
            role = "originator" if originator_ratio > 0.6 else "adopter" if originator_ratio < 0.4 else "balanced"
        else:
            role = "unknown"
            originator_ratio = 0
        
        report["people"].append({
            "person": person,
            "originated": orig_count,
            "supported": supp_count,
            "originator_ratio": round(originator_ratio, 2),
            "role": role,
            "originated_items": originators.get(person, [])[:5],
            "supported_items": supporters.get(person, [])[:5]
        })
    
    # Sort by total activity
    report["people"].sort(key=lambda x: x["originated"] + x["supported"], reverse=True)
    
    conn.close()
    return report


def stance_analysis():
    """Analyze V's stance: what have I supported vs challenged?"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get V's supported edges
    cursor.execute("""
        SELECT source_type, source_id, evidence, context_meeting_id
        FROM meeting_edges
        WHERE relation = 'supported_by' AND target_id = 'vrijen' AND status = 'active'
    """)
    supported = cursor.fetchall()
    
    # Get V's challenged edges
    cursor.execute("""
        SELECT source_type, source_id, evidence, context_meeting_id
        FROM meeting_edges
        WHERE relation = 'challenged_by' AND target_id = 'vrijen' AND status = 'active'
    """)
    challenged = cursor.fetchall()
    
    report = {
        "analysis": "v_stance",
        "supported": [
            {
                "entity": f"{s[0]}:{s[1]}",
                "evidence": s[2],
                "meeting": s[3]
            } for s in supported
        ],
        "challenged": [
            {
                "entity": f"{c[0]}:{c[1]}",
                "evidence": c[2],
                "meeting": c[3]
            } for c in challenged
        ],
        "summary": {
            "total_supported": len(supported),
            "total_challenged": len(challenged),
            "support_ratio": round(len(supported) / max(len(supported) + len(challenged), 1), 2)
        }
    }
    
    conn.close()
    return report


def outcome_review():
    """Find hoped_for/concerned_about edges that need outcome validation."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, source_type, source_id, relation, target_type, target_id,
               evidence, context_meeting_id, outcome_status, created_at
        FROM meeting_edges
        WHERE relation IN ('hoped_for', 'concerned_about') AND status = 'active'
        ORDER BY created_at ASC
    """)
    edges = cursor.fetchall()
    
    pending = []
    validated = []
    invalidated = []
    
    for edge in edges:
        edge_data = {
            "id": edge[0],
            "source": f"{edge[1]}:{edge[2]}",
            "relation": edge[3],
            "target": f"{edge[4]}:{edge[5]}",
            "evidence": edge[6],
            "meeting": edge[7],
            "outcome_status": edge[8],
            "created_at": edge[9]
        }
        
        if edge[8] == "validated":
            validated.append(edge_data)
        elif edge[8] == "invalidated":
            invalidated.append(edge_data)
        else:
            pending.append(edge_data)
    
    report = {
        "analysis": "outcome_review",
        "needs_review": pending,
        "validated": validated,
        "invalidated": invalidated,
        "summary": {
            "total": len(edges),
            "pending": len(pending),
            "validated": len(validated),
            "invalidated": len(invalidated)
        }
    }
    
    conn.close()
    return report


def idea_clusters():
    """Find clusters of related ideas based on shared originators/supporters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all idea -> person edges
    cursor.execute("""
        SELECT source_id, target_id, relation
        FROM meeting_edges
        WHERE source_type = 'idea' 
          AND target_type = 'person'
          AND relation IN ('originated_by', 'supported_by')
          AND status = 'active'
    """)
    edges = cursor.fetchall()
    
    # Build person -> ideas map
    person_ideas = defaultdict(set)
    idea_people = defaultdict(set)
    
    for idea_id, person_id, relation in edges:
        person_ideas[person_id].add(idea_id)
        idea_people[idea_id].add(person_id)
    
    # Find ideas that share people
    clusters = []
    processed = set()
    
    for idea in idea_people:
        if idea in processed:
            continue
            
        # Find all ideas connected through shared people
        cluster = {idea}
        to_check = [idea]
        
        while to_check:
            current = to_check.pop()
            for person in idea_people.get(current, []):
                for related_idea in person_ideas.get(person, []):
                    if related_idea not in cluster:
                        cluster.add(related_idea)
                        to_check.append(related_idea)
        
        if len(cluster) > 1:
            clusters.append({
                "ideas": list(cluster),
                "shared_people": list(set.union(*[idea_people[i] for i in cluster])),
                "size": len(cluster)
            })
        
        processed.update(cluster)
    
    # Sort by cluster size
    clusters.sort(key=lambda x: x["size"], reverse=True)
    
    report = {
        "analysis": "idea_clusters",
        "clusters": clusters[:10],
        "summary": {
            "total_clusters": len(clusters),
            "largest_cluster": clusters[0]["size"] if clusters else 0,
            "isolated_ideas": len(idea_people) - sum(c["size"] for c in clusters)
        }
    }
    
    conn.close()
    return report


def influence_map():
    """Map who influences V's thinking based on idea origins and support patterns."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ideas originated by others that V supported
    cursor.execute("""
        SELECT DISTINCT e1.source_id as idea, e1.target_id as originator
        FROM edges e1
        JOIN edges e2 ON e1.source_type = e2.source_type AND e1.source_id = e2.source_id
        WHERE e1.relation = 'originated_by'
          AND e2.relation = 'supported_by'
          AND e2.target_id = 'vrijen'
          AND e1.target_id != 'vrijen'
          AND e1.status = 'active'
          AND e2.status = 'active'
    """)
    influenced_by = cursor.fetchall()
    
    # Count by originator
    influence_count = defaultdict(list)
    for idea, originator in influenced_by:
        influence_count[originator].append(idea)
    
    # Ideas V originated that others supported
    cursor.execute("""
        SELECT DISTINCT e1.source_id as idea, e2.target_id as supporter
        FROM edges e1
        JOIN edges e2 ON e1.source_type = e2.source_type AND e1.source_id = e2.source_id
        WHERE e1.relation = 'originated_by'
          AND e1.target_id = 'vrijen'
          AND e2.relation = 'supported_by'
          AND e2.target_id != 'vrijen'
          AND e1.status = 'active'
          AND e2.status = 'active'
    """)
    influenced_others = cursor.fetchall()
    
    influenced_count = defaultdict(list)
    for idea, supporter in influenced_others:
        influenced_count[supporter].append(idea)
    
    report = {
        "analysis": "influence_map",
        "v_influenced_by": [
            {
                "person": person,
                "ideas_adopted": len(ideas),
                "examples": ideas[:3]
            }
            for person, ideas in sorted(influence_count.items(), key=lambda x: len(x[1]), reverse=True)
        ],
        "v_influenced": [
            {
                "person": person,
                "ideas_they_adopted": len(ideas),
                "examples": ideas[:3]
            }
            for person, ideas in sorted(influenced_count.items(), key=lambda x: len(x[1]), reverse=True)
        ],
        "summary": {
            "total_influencers": len(influence_count),
            "total_influenced": len(influenced_count),
            "top_influencer": max(influence_count.items(), key=lambda x: len(x[1]))[0] if influence_count else None
        }
    }
    
    conn.close()
    return report


def trace_chain(entity: str):
    """Trace an entity back through its dependency and origin chain."""
    conn = get_connection()
    cursor = conn.cursor()
    
    entity_type, entity_id = entity.split(":", 1)
    
    chain = []
    visited = set()
    to_visit = [(entity_type, entity_id, 0)]
    
    while to_visit:
        etype, eid, depth = to_visit.pop(0)
        
        if (etype, eid) in visited:
            continue
        visited.add((etype, eid))
        
        # Get entity name
        cursor.execute("""
            SELECT name FROM entities WHERE entity_type = ? AND entity_id = ?
        """, (etype, eid))
        name_row = cursor.fetchone()
        name = name_row[0] if name_row else eid
        
        # Get edges from this entity
        cursor.execute("""
            SELECT relation, target_type, target_id, evidence, context_meeting_id
            FROM meeting_edges
            WHERE source_type = ? AND source_id = ? AND status = 'active'
        """, (etype, eid))
        outgoing = cursor.fetchall()
        
        node = {
            "entity": f"{etype}:{eid}",
            "name": name,
            "depth": depth,
            "edges": []
        }
        
        for relation, ttype, tid, evidence, meeting in outgoing:
            node["edges"].append({
                "relation": relation,
                "target": f"{ttype}:{tid}",
                "evidence": evidence,
                "meeting": meeting
            })
            
            # Follow provenance chains
            if relation in ("originated_by", "depends_on", "preceded_by"):
                to_visit.append((ttype, tid, depth + 1))
        
        chain.append(node)
    
    report = {
        "analysis": "trace_chain",
        "root": entity,
        "chain": chain,
        "depth": max(n["depth"] for n in chain) if chain else 0
    }
    
    conn.close()
    return report


def main():
    parser = argparse.ArgumentParser(description="Edge Analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("originated", help="Who originates vs adopts ideas?")
    subparsers.add_parser("stance", help="V's support vs challenge patterns")
    subparsers.add_parser("outcomes", help="Outcome validation queue")
    subparsers.add_parser("clusters", help="Find idea clusters")
    subparsers.add_parser("influence", help="Influence map")
    
    chain_parser = subparsers.add_parser("chain", help="Trace entity chain")
    chain_parser.add_argument("--entity", required=True, help="Entity to trace (e.g., idea:context-graph-system)")
    
    args = parser.parse_args()
    
    try:
        if args.command == "originated":
            result = originated_vs_adopted()
        elif args.command == "stance":
            result = stance_analysis()
        elif args.command == "outcomes":
            result = outcome_review()
        elif args.command == "clusters":
            result = idea_clusters()
        elif args.command == "influence":
            result = influence_map()
        elif args.command == "chain":
            result = trace_chain(args.entity)
        else:
            print(json.dumps({"error": f"Unknown command: {args.command}"}), file=sys.stderr)
            sys.exit(1)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


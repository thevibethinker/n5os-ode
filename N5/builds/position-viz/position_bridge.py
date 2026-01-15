#!/usr/bin/env python3
"""
Position System → Knowledge Graph Bridge
Extracts positions and their connections from N5's positions.db
and generates triples for visualization.
"""
import sqlite3
import json
import argparse
from pathlib import Path

DB_PATH = "/home/workspace/N5/data/positions.db"

def get_positions():
    """Load all positions from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, domain, insight, connections, stability, confidence FROM positions")
    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions

def build_id_to_title_map(positions):
    """Create lookup from position ID to title."""
    return {p["id"]: p["title"] for p in positions}

def extract_triples(positions, id_map):
    """Convert position connections to Subject-Predicate-Object triples."""
    triples = []
    
    for pos in positions:
        if not pos.get("connections"):
            continue
        
        try:
            connections = json.loads(pos["connections"])
        except (json.JSONDecodeError, TypeError):
            continue
        
        # Handle case where connections is not a list
        if not isinstance(connections, list):
            continue
        
        source_title = pos["title"]
        source_domain = pos.get("domain", "unknown")
        
        for conn in connections:
            # Skip if conn is not a dict
            if not isinstance(conn, dict):
                continue
                
            target_id = conn.get("target_id")
            relationship = conn.get("relationship", "related_to")
            
            if not target_id:
                continue
            
            target_title = id_map.get(target_id, target_id)
            
            triples.append({
                "subject": source_title,
                "predicate": relationship,
                "object": target_title,
                "source_domain": source_domain
            })
    
    return triples

def generate_domain_triples(positions):
    """Create domain membership triples (Position -> belongs_to -> Domain)."""
    triples = []
    for pos in positions:
        if pos.get("domain"):
            triples.append({
                "subject": pos["title"],
                "predicate": "belongs_to",
                "object": f"[{pos['domain'].upper()}]"
            })
    return triples

def main():
    parser = argparse.ArgumentParser(description="Position System → Knowledge Graph Bridge")
    parser.add_argument("--dry-run", action="store_true", help="Print sample output without writing files")
    parser.add_argument("--output", type=str, default="positions_triples.json", help="Output JSON file")
    parser.add_argument("--include-domains", action="store_true", help="Include domain membership edges")
    parser.add_argument("--domain-filter", type=str, help="Filter to specific domain (e.g., 'epistemology')")
    args = parser.parse_args()
    
    positions = get_positions()
    print(f"Loaded {len(positions)} positions from database")
    
    if args.domain_filter:
        positions = [p for p in positions if p.get("domain") == args.domain_filter]
        print(f"Filtered to {len(positions)} positions in domain '{args.domain_filter}'")
    
    id_map = build_id_to_title_map(positions)
    
    triples = extract_triples(positions, id_map)
    print(f"Extracted {len(triples)} relationship triples")
    
    if args.include_domains:
        domain_triples = generate_domain_triples(positions)
        triples.extend(domain_triples)
        print(f"Added {len(domain_triples)} domain membership triples")
    
    if args.dry_run:
        print("\n--- Sample Triples (first 10) ---")
        for t in triples[:10]:
            print(f"  {t['subject']} --[{t['predicate']}]--> {t['object']}")
        return
    
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(triples, f, indent=2)
    print(f"\nWrote {len(triples)} triples to {output_path}")

if __name__ == "__main__":
    main()



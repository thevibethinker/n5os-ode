#!/usr/bin/env python3
"""
Semantic Linker for Position Mind Map

Uses sentence-transformers to compute semantic similarity between all positions
and automatically discover missing connections based on embedding cosine similarity.

Two modes:
1. discover - Find semantically similar positions that aren't currently connected
2. enrich - Add connections with thematic descriptions

Usage:
    python semantic_linker.py discover --threshold 0.6
    python semantic_linker.py enrich --top-k 5
"""

import argparse
import json
import sqlite3
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = "/home/workspace/N5/data/positions.db"

# Relationship strength based on similarity score
def similarity_to_relationship(score: float) -> str:
    if score >= 0.85:
        return "strongly_related"
    elif score >= 0.70:
        return "related"
    elif score >= 0.55:
        return "tangentially_related"
    else:
        return "weakly_related"


def load_positions():
    """Load all positions from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, title, insight, domain, stability, confidence, connections
        FROM positions
    """)
    
    positions = [dict(row) for row in cur.fetchall()]
    conn.close()
    return positions


def get_existing_connections(positions):
    """Build set of existing connection pairs."""
    existing = set()
    for pos in positions:
        if pos['connections']:
            try:
                conns = json.loads(pos['connections'])
                for c in conns:
                    if isinstance(c, dict):
                        target = c.get('target_id')
                    else:
                        target = c
                    if target:
                        # Store both directions
                        existing.add((pos['id'], target))
                        existing.add((target, pos['id']))
            except:
                pass
    return existing


def compute_embeddings(positions, model):
    """Compute embeddings for all positions."""
    print(f"Computing embeddings for {len(positions)} positions...")
    
    # Combine title and insight for richer embedding
    texts = [
        f"{p['title']}. {p['insight'][:500] if p['insight'] else ''}"
        for p in positions
    ]
    
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings


def discover_missing_connections(positions, embeddings, existing_connections, threshold=0.55, top_k=10):
    """Find pairs of positions that are semantically similar but not connected."""
    print(f"\nDiscovering missing connections (threshold={threshold})...")
    
    # Compute pairwise similarities
    similarities = cosine_similarity(embeddings)
    
    # Find missing connections
    missing = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            score = similarities[i][j]
            if score >= threshold:
                pair = (positions[i]['id'], positions[j]['id'])
                reverse_pair = (positions[j]['id'], positions[i]['id'])
                
                # Check if connection already exists
                if pair not in existing_connections and reverse_pair not in existing_connections:
                    missing.append({
                        'source_id': positions[i]['id'],
                        'source_title': positions[i]['title'],
                        'target_id': positions[j]['id'],
                        'target_title': positions[j]['title'],
                        'similarity': float(score),
                        'relationship': similarity_to_relationship(score),
                        'source_domain': positions[i]['domain'],
                        'target_domain': positions[j]['domain'],
                        'cross_domain': positions[i]['domain'] != positions[j]['domain']
                    })
    
    # Sort by similarity (highest first)
    missing.sort(key=lambda x: x['similarity'], reverse=True)
    
    return missing[:top_k * 10] if top_k else missing


def generate_thematic_description(source_title, target_title, source_insight, target_insight, relationship):
    """Generate a brief thematic description of the connection."""
    # Simple heuristic-based description (can be enhanced with LLM)
    source_keywords = set(source_title.lower().split())
    target_keywords = set(target_title.lower().split())
    common = source_keywords & target_keywords - {'the', 'a', 'an', 'of', 'in', 'to', 'and', 'is', 'are', 'for'}
    
    if common:
        return f"shared focus on {', '.join(list(common)[:3])}"
    elif relationship == "strongly_related":
        return "deeply interconnected concepts"
    elif relationship == "related":
        return "complementary perspectives"
    else:
        return "thematic resonance"


def add_connections(positions, new_connections, dry_run=True):
    """Add new connections to the database."""
    if dry_run:
        print("\n[DRY RUN] Would add the following connections:")
        for conn in new_connections:
            print(f"  {conn['source_title'][:50]}...")
            print(f"    → {conn['target_title'][:50]}...")
            print(f"    Score: {conn['similarity']:.3f} | {conn['relationship']}")
            if conn['cross_domain']:
                print(f"    🌉 Cross-domain: {conn['source_domain']} ↔ {conn['target_domain']}")
            print()
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    added = 0
    for new_conn in new_connections:
        # Get current connections for source
        cur.execute("SELECT connections FROM positions WHERE id = ?", (new_conn['source_id'],))
        row = cur.fetchone()
        
        if row:
            try:
                current = json.loads(row[0]) if row[0] else []
            except:
                current = []
            
            # Check if already exists
            existing_targets = {c.get('target_id') if isinstance(c, dict) else c for c in current}
            if new_conn['target_id'] not in existing_targets:
                # Add new connection
                current.append({
                    'target_id': new_conn['target_id'],
                    'relationship': new_conn['relationship'],
                    'thematic_description': generate_thematic_description(
                        new_conn['source_title'],
                        new_conn['target_title'],
                        '', '',  # insights not needed for simple heuristic
                        new_conn['relationship']
                    ),
                    'similarity_score': new_conn['similarity'],
                    'auto_discovered': True
                })
                
                cur.execute(
                    "UPDATE positions SET connections = ? WHERE id = ?",
                    (json.dumps(current), new_conn['source_id'])
                )
                added += 1
                print(f"✓ Added: {new_conn['source_title'][:40]}... → {new_conn['target_title'][:40]}...")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Added {added} new connections")


def main():
    parser = argparse.ArgumentParser(description="Semantic linker for position mind map")
    parser.add_argument('mode', choices=['discover', 'enrich', 'stats'],
                       help="discover=find missing links, enrich=add connections, stats=show statistics")
    parser.add_argument('--threshold', type=float, default=0.55,
                       help="Similarity threshold for discovering connections (default: 0.55)")
    parser.add_argument('--top-k', type=int, default=20,
                       help="Number of top connections to show/add (default: 20)")
    parser.add_argument('--apply', action='store_true',
                       help="Actually add the connections (default is dry-run)")
    parser.add_argument('--cross-domain-only', action='store_true',
                       help="Only show cross-domain connections")
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                       help="Sentence transformer model to use")
    
    args = parser.parse_args()
    
    # Load data
    positions = load_positions()
    existing = get_existing_connections(positions)
    
    print(f"Loaded {len(positions)} positions with {len(existing)//2} existing connections")
    
    if args.mode == 'stats':
        # Show statistics
        orphans = [p for p in positions if not p['connections'] or p['connections'] == '[]']
        print(f"\nStatistics:")
        print(f"  Total positions: {len(positions)}")
        print(f"  Existing connections: {len(existing)//2}")
        print(f"  Orphan positions (no connections): {len(orphans)}")
        
        # Domain breakdown
        domains = {}
        for p in positions:
            domains[p['domain']] = domains.get(p['domain'], 0) + 1
        print(f"\nBy domain:")
        for d, count in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {d}: {count}")
        return
    
    # Load model and compute embeddings
    print(f"\nLoading model: {args.model}")
    model = SentenceTransformer(args.model)
    embeddings = compute_embeddings(positions, model)
    
    if args.mode == 'discover':
        # Find missing connections
        missing = discover_missing_connections(
            positions, embeddings, existing,
            threshold=args.threshold,
            top_k=args.top_k
        )
        
        if args.cross_domain_only:
            missing = [m for m in missing if m['cross_domain']]
        
        print(f"\nFound {len(missing)} potential missing connections:\n")
        
        for i, conn in enumerate(missing[:args.top_k], 1):
            cross = "🌉" if conn['cross_domain'] else "  "
            print(f"{i:2}. {cross} [{conn['similarity']:.3f}] {conn['relationship']}")
            print(f"    {conn['source_title'][:60]}...")
            print(f"    → {conn['target_title'][:60]}...")
            if conn['cross_domain']:
                print(f"    ({conn['source_domain']} ↔ {conn['target_domain']})")
            print()
    
    elif args.mode == 'enrich':
        # Discover and optionally add connections
        missing = discover_missing_connections(
            positions, embeddings, existing,
            threshold=args.threshold,
            top_k=args.top_k
        )
        
        if args.cross_domain_only:
            missing = [m for m in missing if m['cross_domain']]
        
        add_connections(positions, missing[:args.top_k], dry_run=not args.apply)


if __name__ == "__main__":
    main()

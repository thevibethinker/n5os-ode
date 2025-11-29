#!/usr/bin/env python3
"""
Query GTM Intelligence Database
"""
import sqlite3
import argparse
from pathlib import Path
import sys
import yaml

WORKSPACE = Path("/home/workspace")
PATHS_YAML = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"


def load_db_path() -> Path:
    try:
        with PATHS_YAML.open() as f:
            cfg = yaml.safe_load(f) or {}
        db_rel = (
            cfg.get("personal_knowledge", {})
            .get("market_intelligence", {})
            .get("db")
        )
        if not db_rel:
            raise KeyError("personal_knowledge.market_intelligence.db missing")
        return WORKSPACE / db_rel
    except Exception as exc:
        print(
            f"Error: Unable to resolve GTM DB path from {PATHS_YAML}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


DB_PATH = load_db_path()

def query(args):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    where_clauses = []
    params = []
    
    if args.stakeholder_type:
        where_clauses.append("stakeholder_type = ?")
        params.append(args.stakeholder_type)
    
    if args.category:
        where_clauses.append("category LIKE ?")
        params.append(f"%{args.category}%")
    
    if args.min_signal:
        where_clauses.append("signal_strength >= ?")
        params.append(args.min_signal)
    
    if args.search:
        where_clauses.append("(title LIKE ? OR insight LIKE ?)")
        params.extend([f"%{args.search}%", f"%{args.search}%"])
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query_sql = f"""
        SELECT stakeholder_name, meeting_date, signal_strength, category, title, 
               SUBSTR(insight, 1, 200) as insight_preview
        FROM gtm_insights
        WHERE {where_sql}
        ORDER BY meeting_date DESC, signal_strength DESC
        LIMIT {args.limit}
    """
    
    cursor.execute(query_sql, params)
    results = cursor.fetchall()
    
    print(f"\n{'='*100}")
    print(f"Found {len(results)} insights")
    print(f"{'='*100}\n")
    
    for row in results:
        print(f"{'●' * row['signal_strength']}{'○' * (5 - row['signal_strength'])} | {row['stakeholder_name']} | {row['meeting_date']}")
        print(f"📁 {row['category']}")
        print(f"💡 {row['title']}")
        print(f"   {row['insight_preview']}...")
        print()
    
    conn.close()

def stats(args):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n=== GTM Intelligence Database Stats ===\n")
    
    # Total counts
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT meeting_id) as meetings FROM gtm_insights")
    row = cursor.fetchone()
    print(f"Total Insights: {row[0]}")
    print(f"Total Meetings: {row[1]}")
    
    # By category
    print("\n--- By Category ---")
    cursor.execute("SELECT category, COUNT(*) as count FROM gtm_insights GROUP BY category ORDER BY count DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"  {row[1]:>3}  {row[0]}")
    
    # By signal strength
    print("\n--- By Signal Strength ---")
    cursor.execute("SELECT signal_strength, COUNT(*) as count FROM gtm_insights GROUP BY signal_strength ORDER BY signal_strength DESC")
    for row in cursor.fetchall():
        print(f"  {'●' * row[0]}{'○' * (5 - row[0])}  {row[1]} insights")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Query GTM Intelligence Database")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query insights')
    query_parser.add_argument('--stakeholder-type', help='Filter by stakeholder type (recruiter, founder, etc.)')
    query_parser.add_argument('--category', help='Filter by category (partial match)')
    query_parser.add_argument('--min-signal', type=int, help='Minimum signal strength (1-5)')
    query_parser.add_argument('--search', help='Search in title or insight text')
    query_parser.add_argument('--limit', type=int, default=20, help='Max results (default: 20)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if args.command == 'query':
        query(args)
    elif args.command == 'stats':
        stats(args)

if __name__ == "__main__":
    main()


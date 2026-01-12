#!/usr/bin/env python3
"""
Retrieve relevant voice primitives for content generation.

Part of Voice Library V2 (Phase 3: Vibe Writer Integration).

Usage:
  python3 retrieve_primitives.py --topic "talent optionality" --count 10
  python3 retrieve_primitives.py --domains career,incentives --min-distinctiveness 0.6
  python3 retrieve_primitives.py --type metaphor --count 5
  python3 retrieve_primitives.py --random --count 3
  python3 retrieve_primitives.py --stats

Process:
1. Filter by domains and/or primitive type (if specified)
2. Filter by distinctiveness_score >= threshold (default 0.6)
3. Exclude recently used (last_used_at within throttle window)
4. Optionally search by topic using keyword matching
5. Return top N primitives
6. Update last_used_at and use_count for returned primitives

Retrieval Contract:
- Default: 5-10 primitives per 1,000-2,000 word piece
- Distinctiveness threshold: ≥ 0.6 (only distinctive primitives)
- Throttle: Same primitive not reused within 500 words / 2 generations
- Diversity: Prefer primitives from different domain tags
"""

import argparse
import json
import logging
import random
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
VOICE_DB = ROOT / "data" / "voice_library.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
LOG = logging.getLogger("retrieve_primitives")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_COUNT = 5
DEFAULT_MIN_DISTINCTIVENESS = 0.6
THROTTLE_HOURS = 24  # Same primitive can't be reused within this window
MAX_SAME_DOMAIN = 3  # Max primitives from same domain in one retrieval


# ─────────────────────────────────────────────────────────────────────────────
# Database Operations
# ─────────────────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    if not VOICE_DB.exists():
        LOG.error(f"Voice library database not found at {VOICE_DB}")
        sys.exit(1)
    conn = sqlite3.connect(str(VOICE_DB))
    conn.row_factory = sqlite3.Row
    return conn


def get_primitives(
    conn: sqlite3.Connection,
    count: int = DEFAULT_COUNT,
    min_distinctiveness: float = DEFAULT_MIN_DISTINCTIVENESS,
    domains: Optional[List[str]] = None,
    primitive_type: Optional[str] = None,
    topic: Optional[str] = None,
    exclude_recently_used: bool = True,
    random_order: bool = False,
) -> List[Dict[str, Any]]:
    """
    Retrieve primitives matching criteria.
    
    Args:
        count: Number of primitives to return
        min_distinctiveness: Minimum distinctiveness score
        domains: Filter to these domains (any match)
        primitive_type: Filter to this type (signature_phrase, metaphor, etc)
        topic: Keyword to search in exact_text
        exclude_recently_used: Exclude primitives used within throttle window
        random_order: If True, randomize order (useful for variety)
    
    Returns:
        List of primitive dicts with all fields
    """
    cursor = conn.cursor()
    
    # Build WHERE clauses
    conditions = ["status = 'approved'"]
    params = []
    
    # Distinctiveness filter
    if min_distinctiveness > 0:
        conditions.append("(distinctiveness_score IS NULL OR distinctiveness_score >= ?)")
        params.append(min_distinctiveness)
    
    # Type filter
    if primitive_type:
        conditions.append("primitive_type = ?")
        params.append(primitive_type)
    
    # Throttle filter
    if exclude_recently_used:
        throttle_cutoff = (datetime.now(timezone.utc) - timedelta(hours=THROTTLE_HOURS)).isoformat()
        conditions.append("(last_used_at IS NULL OR last_used_at < ?)")
        params.append(throttle_cutoff)
    
    # Topic filter (simple keyword search)
    if topic:
        # Search in exact_text and domains_json
        topic_words = topic.lower().split()
        topic_conditions = []
        for word in topic_words:
            topic_conditions.append("(LOWER(exact_text) LIKE ? OR LOWER(domains_json) LIKE ?)")
            params.extend([f"%{word}%", f"%{word}%"])
        if topic_conditions:
            conditions.append(f"({' OR '.join(topic_conditions)})")
    
    # Domain filter (any match)
    if domains:
        domain_conditions = []
        for domain in domains:
            domain_conditions.append("LOWER(domains_json) LIKE ?")
            params.append(f'%"{domain.lower()}"%')
        conditions.append(f"({' OR '.join(domain_conditions)})")
    
    # Build query
    where_clause = " AND ".join(conditions)

    if random_order:
        order_clause = "RANDOM()"
    else:
        order_clause = "(COALESCE(distinctiveness_score,0) - CASE WHEN LENGTH(TRIM(exact_text)) < 25 THEN 0.25 WHEN LENGTH(TRIM(exact_text)) < 50 THEN 0.10 ELSE 0 END) DESC, use_count ASC"
    
    query = f"""
        SELECT 
            id, exact_text, primitive_type, domains_json,
            distinctiveness_score, novelty_flagged, use_count, last_used_at,
            status, notes
        FROM primitives
        WHERE {where_clause}
        ORDER BY {order_clause}
        LIMIT ?
    """
    params.append(count * 2)  # Fetch extra for diversity filtering
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Apply diversity filter (limit same-domain primitives)
    results = []
    domain_counts = {}
    
    for row in rows:
        if len(results) >= count:
            break
            
        row_dict = dict(row)
        
        # Parse domains
        try:
            row_domains = json.loads(row_dict.get("domains_json") or "[]")
        except json.JSONDecodeError:
            row_domains = []
        row_dict["domains"] = row_domains
        
        # Check domain diversity
        skip = False
        for d in row_domains:
            if domain_counts.get(d, 0) >= MAX_SAME_DOMAIN:
                skip = True
                break
        
        if skip:
            continue
        
        # Update domain counts
        for d in row_domains:
            domain_counts[d] = domain_counts.get(d, 0) + 1
        
        results.append(row_dict)
    
    return results


def mark_as_used(conn: sqlite3.Connection, primitive_ids: List[str]) -> int:
    """
    Update last_used_at and increment use_count for retrieved primitives.
    
    Returns number of rows updated.
    """
    if not primitive_ids:
        return 0
    
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    placeholders = ",".join(["?" for _ in primitive_ids])
    cursor.execute(f"""
        UPDATE primitives
        SET last_used_at = ?, use_count = use_count + 1, updated_at = ?
        WHERE id IN ({placeholders})
    """, [now, now] + primitive_ids)
    
    conn.commit()
    return cursor.rowcount


def get_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get voice library statistics."""
    cursor = conn.cursor()
    
    # Total counts by status
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM primitives
        GROUP BY status
    """)
    status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
    
    # Counts by type
    cursor.execute("""
        SELECT primitive_type, COUNT(*) as count
        FROM primitives
        WHERE status = 'approved'
        GROUP BY primitive_type
        ORDER BY count DESC
    """)
    type_counts = {row["primitive_type"]: row["count"] for row in cursor.fetchall()}
    
    # Distinctiveness distribution
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN distinctiveness_score >= 0.9 THEN 1 END) as high,
            COUNT(CASE WHEN distinctiveness_score >= 0.6 AND distinctiveness_score < 0.9 THEN 1 END) as medium,
            COUNT(CASE WHEN distinctiveness_score < 0.6 THEN 1 END) as low,
            COUNT(CASE WHEN distinctiveness_score IS NULL THEN 1 END) as unscored
        FROM primitives
        WHERE status = 'approved'
    """)
    dist_row = cursor.fetchone()
    distinctiveness = {
        "high (≥0.9)": dist_row["high"],
        "medium (0.6-0.9)": dist_row["medium"],
        "low (<0.6)": dist_row["low"],
        "unscored": dist_row["unscored"],
    }
    
    # Usage stats
    cursor.execute("""
        SELECT 
            SUM(use_count) as total_uses,
            COUNT(CASE WHEN use_count > 0 THEN 1 END) as ever_used,
            COUNT(CASE WHEN last_used_at > datetime('now', '-24 hours') THEN 1 END) as used_today
        FROM primitives
        WHERE status = 'approved'
    """)
    usage_row = cursor.fetchone()
    usage = {
        "total_uses": usage_row["total_uses"] or 0,
        "primitives_ever_used": usage_row["ever_used"],
        "used_last_24h": usage_row["used_today"],
    }
    
    # Domain frequency (top 10)
    cursor.execute("SELECT domains_json FROM primitives WHERE status = 'approved'")
    domain_freq = {}
    for row in cursor.fetchall():
        try:
            domains = json.loads(row["domains_json"] or "[]")
            for d in domains:
                domain_freq[d] = domain_freq.get(d, 0) + 1
        except json.JSONDecodeError:
            pass
    top_domains = sorted(domain_freq.items(), key=lambda x: -x[1])[:10]
    
    return {
        "status_counts": status_counts,
        "type_counts": type_counts,
        "distinctiveness": distinctiveness,
        "usage": usage,
        "top_domains": top_domains,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Retrieve voice primitives for content generation"
    )
    
    # Retrieval options
    parser.add_argument("--count", "-n", type=int, default=DEFAULT_COUNT,
                        help=f"Number of primitives to retrieve (default: {DEFAULT_COUNT})")
    parser.add_argument("--topic", "-t", type=str,
                        help="Topic to search for (keywords)")
    parser.add_argument("--domains", "-d", type=str,
                        help="Comma-separated domains to filter (e.g., career,hiring)")
    parser.add_argument("--type", type=str,
                        choices=["signature_phrase", "metaphor", "analogy", 
                                 "syntactic_pattern", "conceptual_frame", "rhetorical_device"],
                        help="Filter by primitive type")
    parser.add_argument("--min-distinctiveness", type=float, default=DEFAULT_MIN_DISTINCTIVENESS,
                        help=f"Minimum distinctiveness score (default: {DEFAULT_MIN_DISTINCTIVENESS})")
    
    # Behavior flags
    parser.add_argument("--random", action="store_true",
                        help="Randomize order (for variety)")
    parser.add_argument("--no-throttle", action="store_true",
                        help="Ignore throttle window (include recently used)")
    parser.add_argument("--no-update", action="store_true",
                        help="Don't update usage tracking")
    
    # Output options
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--stats", action="store_true",
                        help="Show library statistics instead of retrieving")
    
    args = parser.parse_args()
    
    conn = get_connection()
    
    # Stats mode
    if args.stats:
        stats = get_stats(conn)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n=== Voice Library Statistics ===\n")
            
            print("Status Counts:")
            for status, count in stats["status_counts"].items():
                print(f"  {status}: {count}")
            
            print("\nBy Type (approved):")
            for ptype, count in stats["type_counts"].items():
                print(f"  {ptype}: {count}")
            
            print("\nDistinctiveness Distribution:")
            for level, count in stats["distinctiveness"].items():
                print(f"  {level}: {count}")
            
            print("\nUsage:")
            for metric, value in stats["usage"].items():
                print(f"  {metric}: {value}")
            
            print("\nTop Domains:")
            for domain, count in stats["top_domains"]:
                print(f"  {domain}: {count}")
        
        conn.close()
        return
    
    # Parse domains
    domains = None
    if args.domains:
        domains = [d.strip() for d in args.domains.split(",")]
    
    # Retrieve primitives
    primitives = get_primitives(
        conn,
        count=args.count,
        min_distinctiveness=args.min_distinctiveness,
        domains=domains,
        primitive_type=args.type,
        topic=args.topic,
        exclude_recently_used=not args.no_throttle,
        random_order=args.random,
    )
    
    if not primitives:
        LOG.warning("No primitives found matching criteria")
        conn.close()
        sys.exit(0)
    
    # Update usage tracking
    if not args.no_update:
        ids = [p["id"] for p in primitives]
        updated = mark_as_used(conn, ids)
        LOG.info(f"Updated usage for {updated} primitives")
    
    # Output
    if args.json:
        # Clean output for JSON
        output = []
        for p in primitives:
            output.append({
                "id": p["id"],
                "exact_text": p["exact_text"],
                "primitive_type": p["primitive_type"],
                "domains": p["domains"],
                "distinctiveness_score": p["distinctiveness_score"],
                "use_count": p["use_count"],
            })
        print(json.dumps(output, indent=2))
    else:
        print(f"\n=== Retrieved {len(primitives)} Primitives ===\n")
        for i, p in enumerate(primitives, 1):
            print(f"{i}. [{p['primitive_type']}] {p['exact_text']}")
            print(f"   Domains: {', '.join(p['domains'])}")
            print(f"   Distinctiveness: {p['distinctiveness_score']:.2f} | Uses: {p['use_count']}")
            print()
    
    conn.close()


if __name__ == "__main__":
    main()




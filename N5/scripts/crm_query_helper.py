#!/usr/bin/env python3
"""
CRM Query Helper - Fast database queries for CRM profiles

Quick access to CRM data with markdown fallback
"""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path("/home/workspace")
CRM_DB = WORKSPACE / "Knowledge/crm/crm.db"


def query_db(query: str, params: tuple = ()) -> List[Dict]:
    """Execute query and return results as list of dicts"""
    try:
        conn = sqlite3.connect(CRM_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        print(f"Query error: {e}")
        return []


def find_by_name(name: str) -> List[Dict]:
    """Find profiles by name (partial match)"""
    query = """
        SELECT full_name, company, title, category, email,
               last_contact_date, priority, markdown_path
        FROM individuals
        WHERE full_name LIKE ?
        ORDER BY last_contact_date DESC
    """
    return query_db(query, (f"%{name}%",))


def find_by_company(company: str) -> List[Dict]:
    """Find all contacts at a company"""
    query = """
        SELECT full_name, title, email, last_contact_date, markdown_path
        FROM individuals
        WHERE company LIKE ?
        ORDER BY full_name
    """
    return query_db(query, (f"%{company}%",))


def find_by_category(category: str, priority: Optional[str] = None) -> List[Dict]:
    """Find contacts by category and optional priority"""
    if priority:
        query = """
            SELECT full_name, company, title, last_contact_date, markdown_path
            FROM individuals
            WHERE category = ? AND priority = ?
            ORDER BY last_contact_date DESC
        """
        return query_db(query, (category.upper(), priority.lower()))
    else:
        query = """
            SELECT full_name, company, title, last_contact_date, markdown_path
            FROM individuals
            WHERE category = ?
            ORDER BY last_contact_date DESC
        """
        return query_db(query, (category.upper(),))


def get_touchpoints(name: str) -> Dict:
    """Get individual and their interaction history"""
    # Get individual
    person_query = """
        SELECT id, full_name, company, title, email, linkedin_url,
               category, status, priority, first_contact_date,
               last_contact_date, markdown_path
        FROM individuals
        WHERE full_name LIKE ?
        LIMIT 1
    """
    person = query_db(person_query, (f"%{name}%",))
    
    if not person:
        return {"error": f"No profile found for '{name}'"}
    
    person = person[0]
    
    # Get interactions
    interactions_query = """
        SELECT interaction_type, interaction_date, context
        FROM interactions
        WHERE individual_id = ?
        ORDER BY interaction_date DESC
    """
    interactions = query_db(interactions_query, (person["id"],))
    
    return {
        "profile": person,
        "interactions": interactions,
        "interaction_count": len(interactions)
    }


def get_priority_followups() -> List[Dict]:
    """Get high-priority contacts needing follow-up"""
    query = "SELECT * FROM priority_follow_ups LIMIT 20"
    return query_db(query)


def get_network_by_org() -> List[Dict]:
    """Get network grouped by organization"""
    query = "SELECT * FROM network_by_organization"
    return query_db(query)


def get_recent_activity(days: int = 30) -> List[Dict]:
    """Get recent interactions"""
    query = """
        SELECT full_name, company, interaction_type, interaction_date,
               context, markdown_path
        FROM recent_activity
        LIMIT 50
    """
    return query_db(query)


def get_stats() -> Dict:
    """Get CRM database statistics"""
    stats = {}
    
    # Total counts
    stats["total_profiles"] = query_db("SELECT COUNT(*) as count FROM individuals")[0]["count"]
    stats["total_interactions"] = query_db("SELECT COUNT(*) as count FROM interactions")[0]["count"]
    stats["total_organizations"] = query_db("SELECT COUNT(*) as count FROM organizations")[0]["count"]
    
    # By category
    category_query = """
        SELECT category, COUNT(*) as count
        FROM individuals
        GROUP BY category
        ORDER BY count DESC
    """
    stats["by_category"] = query_db(category_query)
    
    # By priority
    priority_query = """
        SELECT priority, COUNT(*) as count
        FROM individuals
        GROUP BY priority
        ORDER BY
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END
    """
    stats["by_priority"] = query_db(priority_query)
    
    # Recent contacts (last 30 days)
    recent_query = """
        SELECT COUNT(*) as count
        FROM individuals
        WHERE julianday('now') - julianday(last_contact_date) <= 30
    """
    stats["contacted_last_30_days"] = query_db(recent_query)[0]["count"]
    
    return stats


def format_results(results: List[Dict], limit: int = None) -> str:
    """Format query results for display"""
    if not results:
        return "No results found."
    
    if limit:
        results = results[:limit]
    
    output = []
    for r in results:
        output.append(json.dumps(r, indent=2))
    
    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="CRM Query Helper")
    parser.add_argument("--name", help="Find by name (partial match)")
    parser.add_argument("--company", help="Find by company")
    parser.add_argument("--category", help="Find by category (INVESTOR, FOUNDER, etc.)")
    parser.add_argument("--priority", help="Filter by priority (high, medium, low)")
    parser.add_argument("--touchpoints", help="Get touchpoint history for person")
    parser.add_argument("--priority-followups", action="store_true", help="Show priority follow-ups")
    parser.add_argument("--network", action="store_true", help="Show network by organization")
    parser.add_argument("--recent", action="store_true", help="Show recent activity")
    parser.add_argument("--stats", action="store_true", help="Show CRM statistics")
    parser.add_argument("--limit", type=int, default=20, help="Limit results (default: 20)")
    
    args = parser.parse_args()
    
    # Execute query based on arguments
    if args.name:
        results = find_by_name(args.name)
        print(format_results(results, args.limit))
    
    elif args.company:
        results = find_by_company(args.company)
        print(format_results(results, args.limit))
    
    elif args.category:
        results = find_by_category(args.category, args.priority)
        print(format_results(results, args.limit))
    
    elif args.touchpoints:
        result = get_touchpoints(args.touchpoints)
        print(json.dumps(result, indent=2))
    
    elif args.priority_followups:
        results = get_priority_followups()
        print(format_results(results, args.limit))
    
    elif args.network:
        results = get_network_by_org()
        print(format_results(results, args.limit))
    
    elif args.recent:
        results = get_recent_activity()
        print(format_results(results, args.limit))
    
    elif args.stats:
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

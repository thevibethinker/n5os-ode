#!/usr/bin/env python3
"""
CRM Query Helper - Fast database queries for CRM data

Provides quick access to CRM data from the unified n5_core.db database.

Updated 2026-01-19: Migrated from crm.db/individuals to n5_core.db/people table.

Usage:
    python3 crm_query_helper.py --name "John"
    python3 crm_query_helper.py --company "Acme"
    python3 crm_query_helper.py --stats
"""

import argparse
import json
import sys
from typing import List, Dict, Optional

# Add workspace to path
sys.path.insert(0, '/home/workspace')

# Import unified database paths
from N5.scripts.db_paths import (
    get_db_connection,
    PEOPLE_TABLE,
    ORGANIZATIONS_TABLE,
    INTERACTIONS_TABLE,
    DEALS_TABLE,
    DEAL_ROLES_TABLE
)


def query_db(query: str, params: tuple = ()) -> List[Dict]:
    """Execute query and return results as list of dicts"""
    try:
        conn = get_db_connection(readonly=True)
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        print(f"Query error: {e}")
        return []


def find_by_name(name: str) -> List[Dict]:
    """Find people by name (partial match)"""
    query = f"""
        SELECT full_name, company, title, category, email,
               last_contact_date, priority, markdown_path
        FROM {PEOPLE_TABLE}
        WHERE full_name LIKE ?
        ORDER BY last_contact_date DESC NULLS LAST
    """
    return query_db(query, (f"%{name}%",))


def find_by_company(company: str) -> List[Dict]:
    """Find all contacts at a company"""
    query = f"""
        SELECT full_name, title, email, last_contact_date, markdown_path
        FROM {PEOPLE_TABLE}
        WHERE company LIKE ?
        ORDER BY full_name
    """
    return query_db(query, (f"%{company}%",))


def find_by_category(category: str, priority: Optional[str] = None) -> List[Dict]:
    """Find contacts by category and optional priority"""
    if priority:
        query = f"""
            SELECT full_name, company, title, last_contact_date, markdown_path
            FROM {PEOPLE_TABLE}
            WHERE category = ? AND priority = ?
            ORDER BY last_contact_date DESC NULLS LAST
        """
        return query_db(query, (category.upper(), priority.lower()))
    else:
        query = f"""
            SELECT full_name, company, title, last_contact_date, markdown_path
            FROM {PEOPLE_TABLE}
            WHERE category = ?
            ORDER BY last_contact_date DESC NULLS LAST
        """
        return query_db(query, (category.upper(),))


def get_touchpoints(name: str) -> Dict:
    """Get person and their interaction history"""
    # Get person
    person_query = f"""
        SELECT id, full_name, company, title, email, linkedin_url,
               category, status, priority, first_contact_date,
               last_contact_date, markdown_path
        FROM {PEOPLE_TABLE}
        WHERE full_name LIKE ?
        LIMIT 1
    """
    person = query_db(person_query, (f"%{name}%",))
    
    if not person:
        return {"error": f"No person found for '{name}'"}
    
    person = person[0]
    person_id = person["id"]
    
    # Get interactions
    interactions_query = f"""
        SELECT type, created_at, notes
        FROM {INTERACTIONS_TABLE}
        WHERE person_id = ?
        ORDER BY created_at DESC
    """
    interactions = query_db(interactions_query, (person_id,))
    
    return {
        "profile": person,
        "interactions": interactions,
        "interaction_count": len(interactions)
    }


def get_person_deals(name: str) -> Dict:
    """Get deals associated with a person"""
    # Find person first
    person_query = f"""
        SELECT id, full_name
        FROM {PEOPLE_TABLE}
        WHERE full_name LIKE ?
        LIMIT 1
    """
    person = query_db(person_query, (f"%{name}%",))
    
    if not person:
        return {"error": f"No person found for '{name}'"}
    
    person_id = person[0]["id"]
    person_name = person[0]["full_name"]
    
    # Get deals via deal_roles junction table
    deals_query = f"""
        SELECT d.id, d.company, d.deal_type, d.pipeline, d.stage, 
               d.temperature, dr.role, d.notes
        FROM {DEAL_ROLES_TABLE} dr
        JOIN {DEALS_TABLE} d ON dr.deal_id = d.id
        WHERE dr.person_id = ?
        ORDER BY d.updated_at DESC
    """
    deals = query_db(deals_query, (person_id,))
    
    return {
        "person": person_name,
        "person_id": person_id,
        "deals": deals,
        "deal_count": len(deals)
    }


def get_priority_followups() -> List[Dict]:
    """Get high-priority contacts needing follow-up"""
    query = f"""
        SELECT id, full_name, company, email, category, priority,
               last_contact_date, markdown_path
        FROM {PEOPLE_TABLE}
        WHERE priority = 'high'
          AND (last_contact_date IS NULL 
               OR julianday('now') - julianday(last_contact_date) > 14)
        ORDER BY last_contact_date ASC NULLS FIRST
        LIMIT 20
    """
    return query_db(query)


def get_network_by_org() -> List[Dict]:
    """Get network grouped by organization"""
    query = f"""
        SELECT company, COUNT(*) as contact_count,
               GROUP_CONCAT(full_name, ', ') as contacts
        FROM {PEOPLE_TABLE}
        WHERE company IS NOT NULL AND company != ''
        GROUP BY company
        ORDER BY contact_count DESC
        LIMIT 30
    """
    return query_db(query)


def get_recent_activity(days: int = 30) -> List[Dict]:
    """Get people with recent interactions"""
    query = f"""
        SELECT p.full_name, p.company, i.type, i.created_at, i.notes
        FROM {INTERACTIONS_TABLE} i
        JOIN {PEOPLE_TABLE} p ON i.person_id = p.id
        WHERE i.created_at >= date('now', '-{days} days')
        ORDER BY i.created_at DESC
        LIMIT 50
    """
    return query_db(query)


def get_stats() -> Dict:
    """Get CRM database statistics"""
    stats = {}
    
    # Total counts
    stats["total_people"] = query_db(f"SELECT COUNT(*) as count FROM {PEOPLE_TABLE}")[0]["count"]
    stats["total_interactions"] = query_db(f"SELECT COUNT(*) as count FROM {INTERACTIONS_TABLE}")[0]["count"]
    stats["total_organizations"] = query_db(f"SELECT COUNT(*) as count FROM {ORGANIZATIONS_TABLE}")[0]["count"]
    stats["total_deals"] = query_db(f"SELECT COUNT(*) as count FROM {DEALS_TABLE}")[0]["count"]
    
    # By category
    category_query = f"""
        SELECT category, COUNT(*) as count
        FROM {PEOPLE_TABLE}
        GROUP BY category
        ORDER BY count DESC
    """
    stats["by_category"] = query_db(category_query)
    
    # By priority
    priority_query = f"""
        SELECT priority, COUNT(*) as count
        FROM {PEOPLE_TABLE}
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
    recent_query = f"""
        SELECT COUNT(*) as count
        FROM {PEOPLE_TABLE}
        WHERE last_contact_date >= date('now', '-30 days')
    """
    stats["contacted_last_30_days"] = query_db(recent_query)[0]["count"]
    
    # Deal pipeline summary
    deals_query = f"""
        SELECT pipeline, stage, COUNT(*) as count
        FROM {DEALS_TABLE}
        GROUP BY pipeline, stage
        ORDER BY pipeline, stage
    """
    stats["deals_by_pipeline"] = query_db(deals_query)
    
    return stats


def format_results(results: List[Dict], limit: int = None) -> str:
    """Format query results for display"""
    if not results:
        return "No results found."
    
    if limit:
        results = results[:limit]
    
    output = []
    for r in results:
        output.append(json.dumps(r, indent=2, default=str))
    
    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="CRM Query Helper (n5_core.db)")
    parser.add_argument("--name", help="Find by name (partial match)")
    parser.add_argument("--company", help="Find by company")
    parser.add_argument("--category", help="Find by category (INVESTOR, FOUNDER, etc.)")
    parser.add_argument("--priority", help="Filter by priority (high, medium, low)")
    parser.add_argument("--touchpoints", help="Get touchpoint history for person")
    parser.add_argument("--deals", help="Get deals for person")
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
        print(json.dumps(result, indent=2, default=str))
    
    elif args.deals:
        result = get_person_deals(args.deals)
        print(json.dumps(result, indent=2, default=str))
    
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
        print(json.dumps(stats, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

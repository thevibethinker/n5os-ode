#!/usr/bin/env python3
"""
Quick Deal Query - Search across deals and contacts

Uses unified n5_core.db database with people table and deal_roles junction.

Usage:
  python3 deal_query.py search "darwinbox"
  python3 deal_query.py contacts --role broker
  python3 deal_query.py deals --pipeline careerspan --temp hot
  python3 deal_query.py summary
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection


def get_db():
    """Get database connection using unified db_paths."""
    return get_db_connection()


def search(query: str):
    """Search across deals and people (via deal_roles)"""
    conn = get_db()
    c = conn.cursor()
    q = f"%{query}%"
    
    print(f"\n🔍 Searching for: {query}\n")
    
    # Search deals
    c.execute("""
        SELECT id, pipeline, company, temperature, stage 
        FROM deals 
        WHERE company LIKE ? OR notes LIKE ? OR id LIKE ?
    """, (q, q, q))
    deals = c.fetchall()
    
    if deals:
        print("DEALS:")
        for d in deals:
            temp = f"[{d['temperature']}]" if d['temperature'] else ""
            pipeline = d['pipeline'] or "-"
            print(f"  {pipeline:10} {d['company'][:30]:30} {temp} ({d['stage']})")
    
    # Search people linked to deals via deal_roles
    c.execute("""
        SELECT DISTINCT p.id, p.full_name, p.company, p.email, dr.deal_id, dr.role
        FROM people p
        LEFT JOIN deal_roles dr ON p.id = dr.person_id
        WHERE p.full_name LIKE ? OR p.company LIKE ? OR p.email LIKE ?
    """, (q, q, q))
    contacts = c.fetchall()
    
    if contacts:
        print("\nPEOPLE:")
        for c in contacts:
            assoc = f"→ {c['deal_id']} ({c['role']})" if c['deal_id'] else "(no deal linked)"
            company = c['company'] or ''
            print(f"  {c['full_name'][:25]:25} @ {company[:20]:20} {assoc}")
    
    if not deals and not contacts:
        print("No results found.")
    
    conn.close()


def list_contacts(role: str = None):
    """List people with deal_roles, optionally filtered by role"""
    conn = get_db()
    c = conn.cursor()
    
    if role:
        c.execute("""
            SELECT p.*, dr.role, dr.deal_id
            FROM people p
            JOIN deal_roles dr ON p.id = dr.person_id
            WHERE dr.role = ?
            ORDER BY p.full_name
        """, (role,))
    else:
        c.execute("""
            SELECT p.*, dr.role, dr.deal_id
            FROM people p
            JOIN deal_roles dr ON p.id = dr.person_id
            ORDER BY dr.role, p.full_name
        """)
    
    contacts = c.fetchall()
    
    print(f"\n{'Role':<15} {'Name':<25} {'Company':<20} {'Deal':<15} {'LinkedIn'}")
    print("-" * 90)
    for contact in contacts:
        li = "✓" if contact['linkedin_url'] else ""
        company = (contact['company'] or '-')[:19]
        deal_id = contact['deal_id'] or '-'
        print(f"{contact['role']:<15} {contact['full_name'][:24]:<25} {company:<20} {deal_id:<15} {li}")
    
    print(f"\nTotal: {len(contacts)}")
    conn.close()


def list_deals(pipeline: str = None, temp: str = None):
    """List deals, optionally filtered"""
    conn = get_db()
    c = conn.cursor()
    
    query = "SELECT * FROM deals WHERE 1=1"
    params = []
    
    if pipeline:
        query += " AND pipeline = ?"
        params.append(pipeline)
    if temp:
        query += " AND temperature = ?"
        params.append(temp)
    
    query += " ORDER BY pipeline, temperature, company"
    c.execute(query, params)
    deals = c.fetchall()
    
    print(f"\n{'Pipeline':<12} {'Company':<28} {'Temp':<8} {'Stage':<12}")
    print("-" * 70)
    for d in deals:
        pipeline_val = d['pipeline'] or '-'
        temp_val = d['temperature'] or '-'
        stage_val = d['stage'] or '-'
        print(f"{pipeline_val:<12} {d['company'][:27]:<28} {temp_val:<8} {stage_val:<12}")
    
    print(f"\nTotal: {len(deals)}")
    conn.close()


def summary():
    """Show pipeline summary"""
    conn = get_db()
    c = conn.cursor()
    
    print("\n" + "=" * 60)
    print("DEAL PIPELINE SUMMARY")
    print("=" * 60)
    
    # Deals by pipeline
    print("\n📊 DEALS (Business Opportunities)")
    c.execute("""
        SELECT pipeline, 
               COUNT(*) as total,
               SUM(CASE WHEN temperature = 'hot' THEN 1 ELSE 0 END) as hot,
               SUM(CASE WHEN temperature = 'warm' THEN 1 ELSE 0 END) as warm
        FROM deals GROUP BY pipeline
    """)
    for row in c.fetchall():
        pipeline = row['pipeline'] or 'unassigned'
        print(f"  {pipeline:12} {row['total']:3} total  ({row['hot'] or 0} hot, {row['warm'] or 0} warm)")
    
    # People by role (via deal_roles)
    print("\n👥 CONTACTS (People linked to deals)")
    c.execute("""
        SELECT dr.role, COUNT(*) as total,
               COUNT(DISTINCT dr.deal_id) as deals_linked
        FROM deal_roles dr
        GROUP BY dr.role
    """)
    for row in c.fetchall():
        role = row['role'] or 'unspecified'
        print(f"  {role:15} {row['total']:3} total  ({row['deals_linked'] or 0} deals)")
    
    # Total unique people with deal associations
    c.execute("""
        SELECT COUNT(DISTINCT person_id) as linked_people,
               (SELECT COUNT(*) FROM people) as total_people
        FROM deal_roles
    """)
    stats = c.fetchone()
    print(f"\n  Total people in CRM: {stats['total_people']}")
    print(f"  People linked to deals: {stats['linked_people']}")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Deal Query Tool')
    subparsers = parser.add_subparsers(dest='command')
    
    # search
    search_p = subparsers.add_parser('search', help='Search deals and contacts')
    search_p.add_argument('query', help='Search term')
    
    # contacts
    contacts_p = subparsers.add_parser('contacts', help='List contacts with deal roles')
    contacts_p.add_argument('--role', help='Filter by role (broker, primary_contact, champion, etc.)')
    
    # deals
    deals_p = subparsers.add_parser('deals', help='List deals')
    deals_p.add_argument('--pipeline', help='Filter by pipeline (zo, careerspan)')
    deals_p.add_argument('--temp', help='Filter by temperature')
    
    # summary
    subparsers.add_parser('summary', help='Pipeline summary')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        search(args.query)
    elif args.command == 'contacts':
        list_contacts(args.role)
    elif args.command == 'deals':
        list_deals(args.pipeline, args.temp)
    elif args.command == 'summary':
        summary()
    else:
        summary()

if __name__ == '__main__':
    main()

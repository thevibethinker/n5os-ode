#!/usr/bin/env python3
"""
Quick Deal Query - Search across deals and contacts

Usage:
  python3 deal_query.py search "darwinbox"
  python3 deal_query.py contacts --type broker
  python3 deal_query.py deals --pipeline careerspan --temp hot
  python3 deal_query.py summary
"""

import argparse
import sqlite3
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/deals.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def search(query: str):
    """Search across deals and contacts"""
    conn = get_db()
    c = conn.cursor()
    q = f"%{query}%"
    
    print(f"\n🔍 Searching for: {query}\n")
    
    # Search deals
    c.execute("""
        SELECT id, pipeline, company, temperature, primary_contact 
        FROM deals 
        WHERE company LIKE ? OR primary_contact LIKE ? OR notes LIKE ?
    """, (q, q, q))
    deals = c.fetchall()
    
    if deals:
        print("DEALS:")
        for d in deals:
            temp = f"[{d['temperature']}]" if d['temperature'] else ""
            print(f"  {d['pipeline']:10} {d['company'][:30]:30} {temp}")
    
    # Search contacts
    c.execute("""
        SELECT id, contact_type, full_name, company, associated_deal_id
        FROM deal_contacts
        WHERE full_name LIKE ? OR company LIKE ? OR notes LIKE ?
    """, (q, q, q))
    contacts = c.fetchall()
    
    if contacts:
        print("\nCONTACTS:")
        for c in contacts:
            assoc = f"→ {c['associated_deal_id']}" if c['associated_deal_id'] else ""
            print(f"  {c['contact_type']:10} {c['full_name'][:25]:25} @ {(c['company'] or '')[:20]:20} {assoc}")
    
    if not deals and not contacts:
        print("No results found.")
    
    conn.close()

def list_contacts(contact_type: str = None):
    """List contacts, optionally filtered by type"""
    conn = get_db()
    c = conn.cursor()
    
    if contact_type:
        c.execute("SELECT * FROM deal_contacts WHERE contact_type = ? ORDER BY full_name", (contact_type,))
    else:
        c.execute("SELECT * FROM deal_contacts ORDER BY contact_type, full_name")
    
    contacts = c.fetchall()
    
    print(f"\n{'Type':<12} {'Name':<25} {'Company':<20} {'LinkedIn'}")
    print("-" * 80)
    for c in contacts:
        li = "✓" if c['linkedin_url'] else ""
        print(f"{c['contact_type']:<12} {c['full_name'][:24]:<25} {(c['company'] or '-')[:19]:<20} {li}")
    
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
        print(f"{d['pipeline']:<12} {d['company'][:27]:<28} {(d['temperature'] or '-'):<8} {(d['stage'] or '-'):<12}")
    
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
        print(f"  {row['pipeline']:12} {row['total']:3} total  ({row['hot'] or 0} hot, {row['warm'] or 0} warm)")
    
    # Contacts by type
    print("\n👥 CONTACTS (People)")
    c.execute("""
        SELECT contact_type, COUNT(*) as total,
               SUM(CASE WHEN associated_deal_id IS NOT NULL THEN 1 ELSE 0 END) as linked
        FROM deal_contacts GROUP BY contact_type
    """)
    for row in c.fetchall():
        print(f"  {row['contact_type']:12} {row['total']:3} total  ({row['linked'] or 0} linked to deals)")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Deal Query Tool')
    subparsers = parser.add_subparsers(dest='command')
    
    # search
    search_p = subparsers.add_parser('search', help='Search deals and contacts')
    search_p.add_argument('query', help='Search term')
    
    # contacts
    contacts_p = subparsers.add_parser('contacts', help='List contacts')
    contacts_p.add_argument('--type', help='Filter by type (broker, leadership)')
    
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
        list_contacts(args.type)
    elif args.command == 'deals':
        list_deals(args.pipeline, args.temp)
    elif args.command == 'summary':
        summary()
    else:
        summary()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
CRM CLI - Unified Database Interface

Command-line interface for CRM operations using the unified n5_core.db database.

Updated 2026-01-19: Migrated from n5_core.db/people to n5_core.db/people table.

Commands:
- create: Manually create a person
- search: Search for people
- intel: Get intelligence synthesis
- list: List people
- stats: Show CRM statistics
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')

# Use unified database paths
from N5.scripts.db_paths import (
    get_db_connection,
    N5_CORE_DB,
    PEOPLE_TABLE,
    ORGANIZATIONS_TABLE,
    INTERACTIONS_TABLE,
    DEALS_TABLE,
    DEAL_ROLES_TABLE
)

# Profile directory for markdown files
CRM_INDIVIDUALS = Path("/home/workspace/Personal/Knowledge/CRM/individuals")


def create_person(email: str, name: str, category: str = 'NETWORKING', 
                  company: str = None, title: str = None, notes: str = None):
    """
    Manually create a person in the CRM.
    
    Args:
        email: Contact email
        name: Full name
        category: NETWORKING | INVESTOR | ADVISOR | COMMUNITY | FOUNDER | CUSTOMER | PARTNER | OTHER
        company: Optional company name
        title: Optional job title
        notes: Optional notes (appended to markdown profile)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if person already exists
        cursor.execute(f"SELECT id, full_name, markdown_path FROM {PEOPLE_TABLE} WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠ Person already exists: {existing['full_name']} (ID: {existing['id']})")
            if existing['markdown_path']:
                print(f"  Path: {existing['markdown_path']}")
            conn.close()
            return
        
        # Create person
        cursor.execute(f"""
            INSERT INTO {PEOPLE_TABLE} (full_name, email, category, company, title, first_contact_date, source_db)
            VALUES (?, ?, ?, ?, ?, datetime('now'), 'manual_cli')
        """, (name, email, category.upper(), company, title))
        
        person_id = cursor.lastrowid
        conn.commit()
        
        # Create markdown profile if it doesn't exist
        slug = email.split('@')[0].lower().replace('.', '-')
        md_path = CRM_INDIVIDUALS / f"{slug}.md"
        
        if not md_path.exists():
            CRM_INDIVIDUALS.mkdir(parents=True, exist_ok=True)
            with open(md_path, 'w') as f:
                f.write(f"---\nname: {name}\nemail: {email}\ncategory: {category}\n")
                if company:
                    f.write(f"company: {company}\n")
                if title:
                    f.write(f"title: {title}\n")
                f.write(f"created: {datetime.now().strftime('%Y-%m-%d')}\n---\n\n")
                f.write(f"# {name}\n\n")
                if notes:
                    f.write(f"## Notes\n\n{notes}\n")
            
            # Update markdown_path in database
            cursor.execute(f"UPDATE {PEOPLE_TABLE} SET markdown_path = ? WHERE id = ?", 
                          (str(md_path), person_id))
            conn.commit()
        
        conn.close()
        
        print(f"✓ Person created: {name} (ID: {person_id})")
        print(f"  Email: {email}")
        print(f"  Category: {category}")
        if md_path.exists():
            print(f"  Path: {md_path}")
        
    except Exception as e:
        print(f"✗ Error creating person: {e}", file=sys.stderr)
        sys.exit(1)


def search_people(email: str = None, name: str = None, company: str = None):
    """
    Search for people.
    
    Args:
        email: Exact email match
        name: Fuzzy name match
        company: Company name match
    """
    try:
        conn = get_db_connection(readonly=True)
        cursor = conn.cursor()
        
        if email:
            cursor.execute(f"""
                SELECT id, full_name, email, company, title, category, last_contact_date
                FROM {PEOPLE_TABLE}
                WHERE email = ?
            """, (email,))
        elif name:
            cursor.execute(f"""
                SELECT id, full_name, email, company, title, category, last_contact_date
                FROM {PEOPLE_TABLE}
                WHERE full_name LIKE ?
                ORDER BY last_contact_date DESC
                LIMIT 20
            """, (f"%{name}%",))
        elif company:
            cursor.execute(f"""
                SELECT id, full_name, email, company, title, category, last_contact_date
                FROM {PEOPLE_TABLE}
                WHERE company LIKE ?
                ORDER BY full_name
                LIMIT 20
            """, (f"%{company}%",))
        else:
            print("✗ Specify --email, --name, or --company", file=sys.stderr)
            conn.close()
            return
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No results found.")
            return
        
        print(f"\n{'ID':<5} {'Name':<30} {'Company':<20} {'Category':<12} {'Last Contact'}")
        print("-" * 90)
        
        for row in results:
            last_contact = row['last_contact_date'][:10] if row['last_contact_date'] else 'Never'
            company_str = (row['company'] or '')[:18]
            category_str = row['category'] or 'None'
            print(f"{row['id']:<5} {row['full_name'][:28]:<30} {company_str:<20} {category_str:<12} {last_contact}")
        
        print()
        
    except Exception as e:
        print(f"✗ Error searching: {e}", file=sys.stderr)
        sys.exit(1)


def get_intelligence(email: str = None, person_id: int = None):
    """
    Get intelligence synthesis for a person.
    
    Args:
        email: Person's email
        person_id: Person's ID
    """
    try:
        conn = get_db_connection(readonly=True)
        cursor = conn.cursor()
        
        # Find person
        if email:
            cursor.execute(f"""
                SELECT id, full_name, email, company, title, category, status, priority,
                       first_contact_date, last_contact_date, markdown_path, linkedin_url
                FROM {PEOPLE_TABLE}
                WHERE email = ?
            """, (email,))
        elif person_id:
            cursor.execute(f"""
                SELECT id, full_name, email, company, title, category, status, priority,
                       first_contact_date, last_contact_date, markdown_path, linkedin_url
                FROM {PEOPLE_TABLE}
                WHERE id = ?
            """, (person_id,))
        else:
            print("✗ Specify --email or --id", file=sys.stderr)
            conn.close()
            return
        
        person = cursor.fetchone()
        
        if not person:
            print("✗ Person not found", file=sys.stderr)
            conn.close()
            return
        
        pid = person['id']
        
        # Get interactions
        cursor.execute(f"""
            SELECT type, created_at, notes
            FROM {INTERACTIONS_TABLE}
            WHERE person_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (pid,))
        interactions = cursor.fetchall()
        
        # Get deal associations
        cursor.execute(f"""
            SELECT d.company, d.stage, d.temperature, dr.role
            FROM {DEAL_ROLES_TABLE} dr
            JOIN {DEALS_TABLE} d ON dr.deal_id = d.id
            WHERE dr.person_id = ?
        """, (pid,))
        deals = cursor.fetchall()
        
        conn.close()
        
        # Display synthesis
        print(f"\n{'='*70}")
        print(f"Intelligence Synthesis: {person['full_name']}")
        print(f"{'='*70}\n")
        
        print("Profile:")
        print(f"  Email: {person['email'] or 'N/A'}")
        print(f"  Company: {person['company'] or 'N/A'}")
        print(f"  Title: {person['title'] or 'N/A'}")
        print(f"  Category: {person['category'] or 'Uncategorized'}")
        print(f"  Status: {person['status'] or 'active'}")
        print(f"  Priority: {person['priority'] or 'medium'}")
        print()
        
        print("Tracking:")
        print(f"  First Contact: {person['first_contact_date'] or 'Unknown'}")
        print(f"  Last Contact: {person['last_contact_date'] or 'Never'}")
        if person['linkedin_url']:
            print(f"  LinkedIn: {person['linkedin_url']}")
        print()
        
        if interactions:
            print(f"Recent Interactions ({len(interactions)}):")
            for i in interactions[:5]:
                date_str = i['created_at'][:10] if i['created_at'] else 'N/A'
                print(f"  - [{i['type']}] {date_str}: {(i['notes'] or '')[:50]}")
            print()
        
        if deals:
            print(f"Deal Associations ({len(deals)}):")
            for d in deals:
                print(f"  - {d['company']} ({d['role']}): {d['stage']} / {d['temperature']}")
            print()
        
        if person['markdown_path']:
            print(f"Profile: {person['markdown_path']}")
        
        print()
        
    except Exception as e:
        print(f"✗ Error getting intelligence: {e}", file=sys.stderr)
        sys.exit(1)


def list_people(category: str = None, limit: int = 20):
    """
    List people in the CRM.
    
    Args:
        category: Filter by category
        limit: Maximum number to show
    """
    try:
        conn = get_db_connection(readonly=True)
        cursor = conn.cursor()
        
        if category:
            cursor.execute(f"""
                SELECT id, full_name, email, company, category, last_contact_date
                FROM {PEOPLE_TABLE}
                WHERE category = ?
                ORDER BY last_contact_date DESC NULLS LAST
                LIMIT ?
            """, (category.upper(), limit))
        else:
            cursor.execute(f"""
                SELECT id, full_name, email, company, category, last_contact_date
                FROM {PEOPLE_TABLE}
                ORDER BY last_contact_date DESC NULLS LAST
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No people found.")
            return
        
        print(f"\n{'ID':<5} {'Name':<30} {'Category':<12} {'Company':<20} {'Last Contact'}")
        print("-" * 85)
        
        for row in results:
            last_contact = row['last_contact_date'][:10] if row['last_contact_date'] else 'Never'
            category_str = row['category'] or 'None'
            company_str = (row['company'] or '')[:18]
            print(f"{row['id']:<5} {row['full_name'][:28]:<30} {category_str:<12} {company_str:<20} {last_contact}")
        
        print(f"\nShowing {len(results)} people\n")
        
    except Exception as e:
        print(f"✗ Error listing people: {e}", file=sys.stderr)
        sys.exit(1)


def show_stats():
    """Display CRM statistics."""
    try:
        conn = get_db_connection(readonly=True)
        cursor = conn.cursor()
        
        # Total people
        cursor.execute(f"SELECT COUNT(*) as count FROM {PEOPLE_TABLE}")
        total_people = cursor.fetchone()['count']
        
        # By category
        cursor.execute(f"""
            SELECT category, COUNT(*) as count
            FROM {PEOPLE_TABLE}
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = cursor.fetchall()
        
        # By status
        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM {PEOPLE_TABLE}
            GROUP BY status
        """)
        by_status = cursor.fetchall()
        
        # Total organizations
        cursor.execute(f"SELECT COUNT(*) as count FROM {ORGANIZATIONS_TABLE}")
        total_orgs = cursor.fetchone()['count']
        
        # Total deals
        cursor.execute(f"SELECT COUNT(*) as count FROM {DEALS_TABLE}")
        total_deals = cursor.fetchone()['count']
        
        # Total interactions
        cursor.execute(f"SELECT COUNT(*) as count FROM {INTERACTIONS_TABLE}")
        total_interactions = cursor.fetchone()['count']
        
        # Recent activity (last 30 days)
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM {PEOPLE_TABLE}
            WHERE last_contact_date >= date('now', '-30 days')
        """)
        recent_contacts = cursor.fetchone()['count']
        
        conn.close()
        
        # Display
        print("\n" + "=" * 50)
        print("CRM Statistics (n5_core.db)")
        print("=" * 50 + "\n")
        
        print(f"People: {total_people} total")
        for row in by_category:
            cat_name = row['category'] if row['category'] else "Uncategorized"
            print(f"  ├─ {cat_name}: {row['count']}")
        print()
        
        print("Status:")
        for row in by_status:
            status_name = row['status'] if row['status'] else "None"
            print(f"  ├─ {status_name}: {row['count']}")
        print()
        
        print(f"Organizations: {total_orgs}")
        print(f"Deals: {total_deals}")
        print(f"Interactions: {total_interactions}")
        print()
        
        print("Activity:")
        print(f"  └─ {recent_contacts} people contacted in last 30 days")
        print()
        
    except Exception as e:
        print(f"✗ Error generating stats: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CRM CLI - Unified Database Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --email john@example.com --name "John Doe" --category INVESTOR
  %(prog)s search --name "John"
  %(prog)s search --company "Acme"
  %(prog)s intel --email john@example.com
  %(prog)s list --category INVESTOR --limit 10
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to execute')
    
    # create
    create_parser = subparsers.add_parser('create', help='Create person manually')
    create_parser.add_argument('--email', required=True, help='Contact email')
    create_parser.add_argument('--name', required=True, help='Full name')
    create_parser.add_argument('--category', default='NETWORKING',
                               choices=['NETWORKING', 'INVESTOR', 'ADVISOR', 'COMMUNITY', 
                                       'FOUNDER', 'CUSTOMER', 'PARTNER', 'OTHER'],
                               help='Person category')
    create_parser.add_argument('--company', help='Company name')
    create_parser.add_argument('--title', help='Job title')
    create_parser.add_argument('--notes', help='Optional notes')
    
    # search
    search_parser = subparsers.add_parser('search', help='Search people')
    search_parser.add_argument('--email', help='Search by email (exact match)')
    search_parser.add_argument('--name', help='Search by name (fuzzy match)')
    search_parser.add_argument('--company', help='Search by company')
    
    # intel
    intel_parser = subparsers.add_parser('intel', help='Get intelligence synthesis')
    intel_parser.add_argument('--email', help='Person email')
    intel_parser.add_argument('--id', type=int, help='Person ID')
    
    # list
    list_parser = subparsers.add_parser('list', help='List people')
    list_parser.add_argument('--category',
                             choices=['NETWORKING', 'INVESTOR', 'ADVISOR', 'COMMUNITY',
                                     'FOUNDER', 'CUSTOMER', 'PARTNER', 'OTHER'],
                             help='Filter by category')
    list_parser.add_argument('--limit', type=int, default=20, help='Max people to show')
    
    # stats
    subparsers.add_parser('stats', help='Show CRM statistics')
    
    args = parser.parse_args()
    
    # Route to appropriate function
    if args.command == 'create':
        create_person(args.email, args.name, args.category, 
                     args.company, args.title, args.notes)
    elif args.command == 'search':
        search_people(args.email, args.name, args.company)
    elif args.command == 'intel':
        get_intelligence(args.email, args.id)
    elif args.command == 'list':
        list_people(args.category, args.limit)
    elif args.command == 'stats':
        show_stats()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

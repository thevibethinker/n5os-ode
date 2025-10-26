#!/usr/bin/env python3
"""
CRM Query Helper - Quick CLI for querying the CRM database

Usage:
    python crm_query.py list [--category=prospect] [--status=active]
    python crm_query.py search <name>
    python crm_query.py add <name> --company=<company> --title=<title> ...
    python crm_query.py update <id> --status=active
    python crm_query.py stale [--days=90]
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
import sys

DB_PATH = Path('/home/workspace/Knowledge/crm/crm.db')


def get_connection():
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run migrate_crm_to_sqlite.py first")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def list_individuals(args):
    """List individuals with optional filters"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, full_name, title, company, category, status, tags FROM individuals WHERE 1=1"
    params = []
    
    if args.category:
        query += " AND category = ?"
        params.append(args.category)
    
    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    
    query += " ORDER BY updated_at DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    if not results:
        print("No individuals found.")
        return
    
    print(f"\n{'ID':<5} {'Name':<25} {'Title':<20} {'Company':<20} {'Category':<15} {'Status':<10}")
    print("-" * 100)
    for row in results:
        print(f"{row[0]:<5} {row[1]:<25} {(row[2] or ''):<20} {(row[3] or ''):<20} {row[4]:<15} {row[5]:<10}")
    
    print(f"\nTotal: {len(results)} individuals")


def search_individuals(args):
    """Search individuals by name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, full_name, title, company, email, primary_category, status, tags
        FROM individuals
        WHERE full_name LIKE ? OR company LIKE ?
        ORDER BY full_name
    """, (f"%{args.query}%", f"%{args.query}%"))
    
    results = cursor.fetchall()
    
    if not results:
        print(f"No results for '{args.query}'")
        return
    
    for row in results:
        print(f"\n{'='*60}")
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Title: {row[2] or 'N/A'}")
        print(f"Company: {row[3] or 'N/A'}")
        print(f"Email: {row[4] or 'N/A'}")
        print(f"Category: {row[5]}")
        print(f"Status: {row[6]}")
        print(f"Tags: {row[7] or 'N/A'}")


def show_stale(args):
    """Show contacts with no recent interaction"""
    conn = get_connection()
    cursor = conn.cursor()
    
    days = args.days if args.days else 90
    
    cursor.execute(f"""
        SELECT full_name, company, days_since_contact
        FROM stale_contacts
        WHERE days_since_contact > {days} OR days_since_contact IS NULL
        ORDER BY days_since_contact DESC
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print(f"No stale contacts (>{days} days)")
        return
    
    print(f"\nStale Contacts (>{days} days since contact):")
    print("-" * 60)
    for row in results:
        days_str = f"{int(row[2])} days" if row[2] else "Never contacted"
        print(f"  {row[0]:<30} {(row[1] or 'N/A'):<20} {days_str}")
    
    print(f"\nTotal: {len(results)} stale contacts")


def add_individual(args):
    """Add new individual to database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate markdown file path from name
    md_filename = args.name.lower().replace(' ', '-') + '.md'
    md_path = f'Knowledge/crm/individuals/{md_filename}'
    
    cursor.execute("""
        INSERT INTO individuals (
            full_name, title, company, email, linkedin_url, twitter_handle,
            primary_category, status, tags, source_type, notes, markdown_file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args.name,
        args.title,
        args.company,
        args.email,
        args.linkedin,
        args.twitter,
        args.category or 'other',
        args.status or 'prospect',
        args.tags,
        args.source,
        args.notes,
        md_path
    ))
    
    conn.commit()
    new_id = cursor.lastrowid
    
    print(f"✓ Added: {args.name} (ID: {new_id})")
    print(f"  Markdown file: {md_path}")
    
    # Optionally create markdown file
    if args.create_markdown:
        create_markdown_file(new_id, args)


def create_markdown_file(individual_id, args):
    """Create markdown file for individual"""
    md_path = Path('/home/workspace') / f'Knowledge/crm/individuals/{args.name.lower().replace(" ", "-")}.md'
    md_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
name: {args.name}
title: {args.title or ''}
company: {args.company or ''}
email: {args.email or ''}
linkedin: {args.linkedin or ''}
category: {args.category or 'other'}
status: {args.status or 'prospect'}
tags: {args.tags or ''}
source: {args.source or ''}
---

# {args.name}

## Overview
{args.notes or 'Add notes here...'}

## Interactions
- [Date]: Initial contact

## Next Steps
- 

## References
- Markdown file linked to DB ID: {individual_id}
"""
    
    md_path.write_text(content)
    print(f"  ✓ Created markdown: {md_path}")


def main():
    parser = argparse.ArgumentParser(description='CRM Query Helper')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List individuals')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search by name/company')
    search_parser.add_argument('query', help='Search query')
    
    # Stale command
    stale_parser = subparsers.add_parser('stale', help='Show stale contacts')
    stale_parser.add_argument('--days', type=int, default=90, help='Days threshold (default: 90)')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new individual')
    add_parser.add_argument('name', help='Full name')
    add_parser.add_argument('--title', help='Job title')
    add_parser.add_argument('--company', help='Company name')
    add_parser.add_argument('--email', help='Email address')
    add_parser.add_argument('--linkedin', help='LinkedIn URL')
    add_parser.add_argument('--twitter', help='Twitter handle')
    add_parser.add_argument('--category', help='Primary category')
    add_parser.add_argument('--status', default='prospect', help='Status (default: prospect)')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--source', help='Source type')
    add_parser.add_argument('--notes', help='Brief notes')
    add_parser.add_argument('--create-markdown', action='store_true', help='Create markdown file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_individuals(args)
    elif args.command == 'search':
        search_individuals(args)
    elif args.command == 'stale':
        show_stale(args)
    elif args.command == 'add':
        add_individual(args)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Deal Management CLI for N5

Uses unified n5_core.db database.

Commands:
  list [--type TYPE] [--stage STAGE] [--temp TEMP]  - List deals
  show <deal_id>                                     - Show deal details
  add <company> --type TYPE [options]               - Add new deal
  update <deal_id> [options]                        - Update deal
  log <deal_id> <activity_type> [--desc DESC]       - Log activity
  stages                                            - Show stage definitions
  summary                                           - Dashboard view
  contacts <deal_id>                                - Show deal contacts

Examples:
  python3 deal_cli.py list --type zo_partnership
  python3 deal_cli.py show zo-dp-001
  python3 deal_cli.py update zo-dp-003 --stage outreach --next-action "Email Tope"
  python3 deal_cli.py log zo-dp-001 meeting_held --desc "Partnership review call"
  python3 deal_cli.py contacts zo-dp-001
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection, N5_CORE_DB

STAGES = [
    ('identified', 'Target recognized, not yet researched'),
    ('researched', 'Intel gathered, warm intro path found'),
    ('outreach', 'First touch sent'),
    ('engaged', 'Response received, conversation open'),
    ('qualified', 'Confirmed mutual interest + fit'),
    ('negotiating', 'Terms being discussed'),
    ('closed_won', 'Deal completed successfully'),
    ('closed_lost', 'Deal dead or declined'),
]

ACTIVITY_TYPES = ['email_sent', 'email_received', 'meeting_held', 'call', 'linkedin_message', 
                  'x_interaction', 'stage_change', 'note', 'intro_made']


def get_db():
    """Get database connection using unified db_paths."""
    return get_db_connection()


def list_deals(args):
    conn = get_db()
    c = conn.cursor()
    
    query = "SELECT * FROM deals WHERE 1=1"
    params = []
    
    if args.type:
        query += " AND deal_type = ?"
        params.append(args.type)
    if args.stage:
        query += " AND stage = ?"
        params.append(args.stage)
    if args.temp:
        query += " AND temperature = ?"
        params.append(args.temp)
    
    query += " ORDER BY temperature DESC, stage, company"
    
    c.execute(query, params)
    deals = c.fetchall()
    
    if not deals:
        print("No deals found matching criteria.")
        return
    
    print(f"\n{'ID':<15} {'Company':<25} {'Type':<18} {'Temp':<8} {'Stage':<12} {'Pipeline':<10}")
    print("-" * 95)
    
    for d in deals:
        temp = d['temperature'] or '-'
        pipeline = d['pipeline'] or '-'
        print(f"{d['id']:<15} {d['company'][:24]:<25} {d['deal_type']:<18} {temp:<8} {d['stage']:<12} {pipeline:<10}")
    
    print(f"\nTotal: {len(deals)} deals")
    conn.close()


def show_deal(args):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM deals WHERE id = ?", (args.deal_id,))
    deal = c.fetchone()
    
    if not deal:
        print(f"Deal not found: {args.deal_id}")
        return
    
    print(f"\n{'='*60}")
    print(f"Deal: {deal['id']}")
    print(f"{'='*60}")
    print(f"Company:        {deal['company']}")
    print(f"Type:           {deal['deal_type']}")
    print(f"Category:       {deal['category'] or '-'}")
    print(f"Pipeline:       {deal['pipeline'] or '-'}")
    print()
    print(f"Temperature:    {deal['temperature'] or '-'}")
    print(f"Stage:          {deal['stage']}")
    print()
    if deal['notes']:
        print(f"Notes:\n  {deal['notes']}")
    print()
    print(f"Created:  {deal['created_at']}")
    print(f"Updated:  {deal['updated_at']}")
    
    # Show contacts via deal_roles junction table
    c.execute("""
        SELECT p.full_name, p.email, p.title, p.company as person_company, dr.role
        FROM deal_roles dr
        JOIN people p ON dr.person_id = p.id
        WHERE dr.deal_id = ?
        ORDER BY 
            CASE dr.role 
                WHEN 'primary_contact' THEN 1 
                WHEN 'decision_maker' THEN 2
                WHEN 'champion' THEN 3
                WHEN 'broker' THEN 4
                ELSE 5 
            END
    """, (args.deal_id,))
    contacts = c.fetchall()
    
    if contacts:
        print(f"\n{'Contacts':}")
        print("-" * 40)
        for contact in contacts:
            role = contact['role'] or 'contact'
            email = f" ({contact['email']})" if contact['email'] else ""
            title = f" - {contact['title']}" if contact['title'] else ""
            print(f"  [{role}] {contact['full_name']}{title}{email}")
    
    # Show recent activities
    c.execute("""
        SELECT * FROM deal_activities 
        WHERE deal_id = ? 
        ORDER BY timestamp DESC LIMIT 5
    """, (args.deal_id,))
    activities = c.fetchall()
    
    if activities:
        print(f"\n{'Recent Activities':}")
        print("-" * 40)
        for a in activities:
            ts = a['timestamp'][:10] if a['timestamp'] else '-'
            print(f"  [{ts}] {a['activity_type']}: {a['description'] or '-'}")
    
    conn.close()


def show_contacts(args):
    """Show all contacts associated with a deal."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT company FROM deals WHERE id = ?", (args.deal_id,))
    deal = c.fetchone()
    if not deal:
        print(f"Deal not found: {args.deal_id}")
        return
    
    c.execute("""
        SELECT p.id, p.full_name, p.email, p.linkedin_url, p.title, p.company, dr.role, dr.notes
        FROM deal_roles dr
        JOIN people p ON dr.person_id = p.id
        WHERE dr.deal_id = ?
        ORDER BY dr.role, p.full_name
    """, (args.deal_id,))
    contacts = c.fetchall()
    
    print(f"\n{'='*60}")
    print(f"Contacts for: {args.deal_id} ({deal['company']})")
    print(f"{'='*60}")
    
    if not contacts:
        print("No contacts linked to this deal.")
    else:
        for contact in contacts:
            print(f"\n  {contact['full_name']}")
            print(f"    Role:     {contact['role'] or '-'}")
            if contact['title']:
                print(f"    Title:    {contact['title']}")
            if contact['email']:
                print(f"    Email:    {contact['email']}")
            if contact['linkedin_url']:
                print(f"    LinkedIn: {contact['linkedin_url']}")
            if contact['notes']:
                print(f"    Notes:    {contact['notes']}")
    
    print(f"\nTotal: {len(contacts)} contacts")
    conn.close()


def add_deal(args):
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    deal_id = args.id or f"{args.type[:2]}-{datetime.now().strftime('%y%m%d%H%M%S')}"
    
    c.execute("""
        INSERT INTO deals (id, deal_type, company, category, pipeline,
                          temperature, stage, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        deal_id, args.type, args.company, args.category, args.pipeline,
        args.temp, args.stage or 'identified', args.notes, now, now
    ))
    
    # If contact provided, create person + deal_role
    if args.contact:
        # Check if person exists
        c.execute("SELECT id FROM people WHERE full_name = ?", (args.contact,))
        person = c.fetchone()
        
        if person:
            person_id = person['id']
        else:
            # Create new person
            c.execute("""
                INSERT INTO people (full_name, company, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (args.contact, args.company, now, now))
            person_id = c.lastrowid
        
        # Create deal_role
        c.execute("""
            INSERT INTO deal_roles (deal_id, person_id, role, created_at)
            VALUES (?, ?, 'primary_contact', ?)
        """, (deal_id, person_id, now))
    
    conn.commit()
    print(f"✓ Created deal: {deal_id}")
    conn.close()


def update_deal(args):
    conn = get_db()
    c = conn.cursor()
    
    updates = []
    params = []
    
    if args.stage:
        updates.append("stage = ?")
        params.append(args.stage)
    if args.temp:
        updates.append("temperature = ?")
        params.append(args.temp)
    if args.pipeline:
        updates.append("pipeline = ?")
        params.append(args.pipeline)
    if args.notes:
        updates.append("notes = ?")
        params.append(args.notes)
    if args.category:
        updates.append("category = ?")
        params.append(args.category)
    
    if not updates:
        print("No updates specified.")
        return
    
    updates.append("updated_at = ?")
    now = datetime.now().isoformat()
    params.extend([now, args.deal_id])
    
    query = f"UPDATE deals SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    
    if c.rowcount == 0:
        print(f"Deal not found: {args.deal_id}")
    else:
        print(f"✓ Updated deal: {args.deal_id}")
        
        # Log stage change if applicable
        if args.stage:
            c.execute("""
                INSERT INTO deal_activities (deal_id, activity_type, description, timestamp)
                VALUES (?, 'stage_change', ?, ?)
            """, (args.deal_id, f"Stage changed to: {args.stage}", now))
    
    conn.commit()
    conn.close()


def log_activity(args):
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute("""
        INSERT INTO deal_activities (deal_id, activity_type, description, performed_by, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (args.deal_id, args.activity_type, args.desc, args.by, now))
    
    # Update deal's updated_at
    c.execute("UPDATE deals SET updated_at = ? WHERE id = ?", (now, args.deal_id))
    
    conn.commit()
    print(f"✓ Logged {args.activity_type} for {args.deal_id}")
    conn.close()


def show_stages(args):
    print("\nDeal Stages:")
    print("-" * 60)
    for stage, desc in STAGES:
        print(f"  {stage:<15} {desc}")


def summary(args):
    conn = get_db()
    c = conn.cursor()
    
    print("\n" + "=" * 60)
    print("DEAL PIPELINE SUMMARY")
    print("=" * 60)
    
    # By deal type
    c.execute("""
        SELECT deal_type, COUNT(*) as count 
        FROM deals 
        GROUP BY deal_type
    """)
    print("\nBy Type:")
    for row in c.fetchall():
        print(f"  {row['deal_type']}: {row['count']}")
    
    # By pipeline
    c.execute("""
        SELECT pipeline, COUNT(*) as count 
        FROM deals 
        WHERE pipeline IS NOT NULL
        GROUP BY pipeline
    """)
    print("\nBy Pipeline:")
    for row in c.fetchall():
        print(f"  {row['pipeline'] or 'unassigned'}: {row['count']}")
    
    # By stage
    c.execute("""
        SELECT stage, COUNT(*) as count 
        FROM deals 
        GROUP BY stage
        ORDER BY 
            CASE stage 
                WHEN 'identified' THEN 1
                WHEN 'researched' THEN 2
                WHEN 'outreach' THEN 3
                WHEN 'engaged' THEN 4
                WHEN 'qualified' THEN 5
                WHEN 'negotiating' THEN 6
                WHEN 'closed_won' THEN 7
                WHEN 'closed_lost' THEN 8
            END
    """)
    print("\nBy Stage:")
    for row in c.fetchall():
        print(f"  {row['stage']}: {row['count']}")
    
    # Hot deals
    c.execute("""
        SELECT id, company, stage 
        FROM deals 
        WHERE temperature = 'hot' AND stage NOT IN ('closed_won', 'closed_lost')
        ORDER BY updated_at DESC
    """)
    hot = c.fetchall()
    if hot:
        print("\n🔥 Hot Deals:")
        for d in hot:
            print(f"  [{d['id']}] {d['company']} ({d['stage']})")
    
    # Stale deals (not updated in 7+ days)
    c.execute("""
        SELECT id, company, stage, updated_at 
        FROM deals 
        WHERE date(updated_at) < date('now', '-7 days')
          AND stage NOT IN ('closed_won', 'closed_lost', 'identified')
        ORDER BY updated_at
        LIMIT 5
    """)
    stale = c.fetchall()
    if stale:
        print("\n⚠️  Stale (7+ days):")
        for d in stale:
            print(f"  [{d['id']}] {d['company']} - last: {d['updated_at'][:10]}")
    
    # Contact stats
    c.execute("""
        SELECT COUNT(DISTINCT dr.person_id) as linked_people,
               COUNT(DISTINCT dr.deal_id) as deals_with_contacts
        FROM deal_roles dr
    """)
    stats = c.fetchone()
    print(f"\n👥 Contacts: {stats['linked_people']} people linked to {stats['deals_with_contacts']} deals")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Deal Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list
    list_p = subparsers.add_parser('list', help='List deals')
    list_p.add_argument('--type', help='Filter by deal type')
    list_p.add_argument('--stage', help='Filter by stage')
    list_p.add_argument('--temp', help='Filter by temperature')
    list_p.set_defaults(func=list_deals)
    
    # show
    show_p = subparsers.add_parser('show', help='Show deal details')
    show_p.add_argument('deal_id', help='Deal ID')
    show_p.set_defaults(func=show_deal)
    
    # contacts
    contacts_p = subparsers.add_parser('contacts', help='Show deal contacts')
    contacts_p.add_argument('deal_id', help='Deal ID')
    contacts_p.set_defaults(func=show_contacts)
    
    # add
    add_p = subparsers.add_parser('add', help='Add new deal')
    add_p.add_argument('company', help='Company name')
    add_p.add_argument('--type', required=True, help='Deal type')
    add_p.add_argument('--id', help='Custom deal ID')
    add_p.add_argument('--category', help='Category')
    add_p.add_argument('--contact', help='Primary contact name (creates person + deal_role)')
    add_p.add_argument('--temp', help='Temperature (hot/warm/cold)')
    add_p.add_argument('--stage', help='Initial stage')
    add_p.add_argument('--pipeline', help='Pipeline (zo/careerspan)')
    add_p.add_argument('--notes', help='Deal notes')
    add_p.set_defaults(func=add_deal)
    
    # update
    update_p = subparsers.add_parser('update', help='Update deal')
    update_p.add_argument('deal_id', help='Deal ID')
    update_p.add_argument('--stage', help='New stage')
    update_p.add_argument('--temp', help='New temperature')
    update_p.add_argument('--pipeline', help='Pipeline')
    update_p.add_argument('--category', help='Category')
    update_p.add_argument('--notes', help='Notes')
    update_p.set_defaults(func=update_deal)
    
    # log
    log_p = subparsers.add_parser('log', help='Log activity')
    log_p.add_argument('deal_id', help='Deal ID')
    log_p.add_argument('activity_type', choices=ACTIVITY_TYPES, help='Activity type')
    log_p.add_argument('--desc', help='Description')
    log_p.add_argument('--by', help='Performed by')
    log_p.set_defaults(func=log_activity)
    
    # stages
    stages_p = subparsers.add_parser('stages', help='Show stage definitions')
    stages_p.set_defaults(func=show_stages)
    
    # summary
    summary_p = subparsers.add_parser('summary', help='Dashboard summary')
    summary_p.set_defaults(func=summary)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Deal Management CLI for N5

Commands:
  list [--type TYPE] [--stage STAGE] [--temp TEMP]  - List deals
  show <deal_id>                                     - Show deal details
  add <company> --type TYPE [options]               - Add new deal
  update <deal_id> [options]                        - Update deal
  log <deal_id> <activity_type> [--desc DESC]       - Log activity
  stages                                            - Show stage definitions
  summary                                           - Dashboard view

Examples:
  python3 deal_cli.py list --type zo_partnership
  python3 deal_cli.py show zo-dp-001
  python3 deal_cli.py update zo-dp-003 --stage outreach --next-action "Email Tope"
  python3 deal_cli.py log zo-dp-001 meeting_held --desc "Partnership review call"
"""

import argparse
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/home/workspace/N5/data/deals.db')

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
    return sqlite3.connect(DB_PATH)

def list_deals(args):
    conn = get_db()
    conn.row_factory = sqlite3.Row
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
    
    # Print table
    print(f"\n{'ID':<12} {'Company':<25} {'Type':<20} {'Temp':<8} {'Stage':<12} {'Owner':<6}")
    print("-" * 90)
    
    for d in deals:
        temp = d['temperature'] or '-'
        owner = d['owner'] or '-'
        print(f"{d['id']:<12} {d['company'][:24]:<25} {d['deal_type']:<20} {temp:<8} {d['stage']:<12} {owner:<6}")
    
    print(f"\nTotal: {len(deals)} deals")
    conn.close()

def show_deal(args):
    conn = get_db()
    conn.row_factory = sqlite3.Row
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
    print(f"Primary Contact: {deal['primary_contact'] or '-'}")
    print()
    print(f"Temperature:    {deal['temperature'] or '-'}")
    print(f"Proximity:      {deal['proximity'] or '-'}")
    print(f"Stage:          {deal['stage']}")
    print(f"Confidence:     {deal['confidence']}/10")
    print()
    print(f"Owner:          {deal['owner'] or '-'}")
    print(f"Liaison:        {deal['liaison'] or '-'}")
    print(f"Warm Intro Path: {deal['warm_intro_path'] or '-'}")
    print()
    if deal['thesis']:
        print(f"Thesis:\n  {deal['thesis']}")
    if deal['implementation']:
        print(f"Implementation:\n  {deal['implementation']}")
    if deal['blockers']:
        print(f"Blockers:\n  {deal['blockers']}")
    if deal['next_action']:
        print(f"Next Action:\n  {deal['next_action']}")
        if deal['next_action_date']:
            print(f"  Due: {deal['next_action_date']}")
    print()
    print(f"First Identified: {deal['first_identified']}")
    print(f"Last Touched:     {deal['last_touched']}")
    
    # Show recent activities
    c.execute("""
        SELECT * FROM deal_activities 
        WHERE deal_id = ? 
        ORDER BY created_at DESC LIMIT 5
    """, (args.deal_id,))
    activities = c.fetchall()
    
    if activities:
        print(f"\n{'Recent Activities':}")
        print("-" * 40)
        for a in activities:
            print(f"  [{a['created_at'][:10]}] {a['activity_type']}: {a['description'] or '-'}")
    
    conn.close()

def add_deal(args):
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    deal_id = args.id or f"{args.type[:2]}-{datetime.now().strftime('%y%m%d%H%M%S')}"
    
    c.execute("""
        INSERT INTO deals (id, deal_type, company, category, primary_contact, 
                          temperature, stage, thesis, owner, first_identified, 
                          last_touched, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        deal_id, args.type, args.company, args.category, args.contact,
        args.temp, args.stage or 'identified', args.thesis, args.owner,
        now, now, now, now
    ))
    
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
    if args.next_action:
        updates.append("next_action = ?")
        params.append(args.next_action)
    if args.next_action_date:
        updates.append("next_action_date = ?")
        params.append(args.next_action_date)
    if args.owner:
        updates.append("owner = ?")
        params.append(args.owner)
    if args.confidence:
        updates.append("confidence = ?")
        params.append(args.confidence)
    if args.blockers:
        updates.append("blockers = ?")
        params.append(args.blockers)
    if args.thesis:
        updates.append("thesis = ?")
        params.append(args.thesis)
    
    if not updates:
        print("No updates specified.")
        return
    
    updates.append("updated_at = ?")
    updates.append("last_touched = ?")
    now = datetime.now().isoformat()
    params.extend([now, now, args.deal_id])
    
    query = f"UPDATE deals SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    
    if c.rowcount == 0:
        print(f"Deal not found: {args.deal_id}")
    else:
        print(f"✓ Updated deal: {args.deal_id}")
        
        # Log stage change if applicable
        if args.stage:
            c.execute("""
                INSERT INTO deal_activities (deal_id, activity_type, description, created_at)
                VALUES (?, 'stage_change', ?, ?)
            """, (args.deal_id, f"Stage changed to: {args.stage}", now))
    
    conn.commit()
    conn.close()

def log_activity(args):
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute("""
        INSERT INTO deal_activities (deal_id, activity_type, description, channel, outcome, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (args.deal_id, args.activity_type, args.desc, args.channel, args.outcome, now))
    
    # Update last_touched
    c.execute("UPDATE deals SET last_touched = ? WHERE id = ?", (now, args.deal_id))
    
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
    conn.row_factory = sqlite3.Row
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
    
    # Hot deals (action needed)
    c.execute("""
        SELECT id, company, stage, next_action 
        FROM deals 
        WHERE temperature = 'hot' AND stage NOT IN ('closed_won', 'closed_lost')
        ORDER BY last_touched
    """)
    hot = c.fetchall()
    if hot:
        print("\n🔥 Hot Deals:")
        for d in hot:
            action = d['next_action'] or 'No action set'
            print(f"  [{d['id']}] {d['company']} ({d['stage']}) → {action[:40]}")
    
    # Stale deals (not touched in 7+ days)
    c.execute("""
        SELECT id, company, stage, last_touched 
        FROM deals 
        WHERE date(last_touched) < date('now', '-7 days')
          AND stage NOT IN ('closed_won', 'closed_lost', 'identified')
        ORDER BY last_touched
        LIMIT 5
    """)
    stale = c.fetchall()
    if stale:
        print("\n⚠️  Stale (7+ days):")
        for d in stale:
            print(f"  [{d['id']}] {d['company']} - last: {d['last_touched'][:10]}")
    
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
    
    # add
    add_p = subparsers.add_parser('add', help='Add new deal')
    add_p.add_argument('company', help='Company name')
    add_p.add_argument('--type', required=True, help='Deal type')
    add_p.add_argument('--id', help='Custom deal ID')
    add_p.add_argument('--category', help='Category')
    add_p.add_argument('--contact', help='Primary contact')
    add_p.add_argument('--temp', help='Temperature (hot/warm/cold)')
    add_p.add_argument('--stage', help='Initial stage')
    add_p.add_argument('--thesis', help='Why this deal makes sense')
    add_p.add_argument('--owner', help='Deal owner')
    add_p.set_defaults(func=add_deal)
    
    # update
    update_p = subparsers.add_parser('update', help='Update deal')
    update_p.add_argument('deal_id', help='Deal ID')
    update_p.add_argument('--stage', help='New stage')
    update_p.add_argument('--temp', help='New temperature')
    update_p.add_argument('--next-action', help='Next action')
    update_p.add_argument('--next-action-date', help='Next action due date')
    update_p.add_argument('--owner', help='Deal owner')
    update_p.add_argument('--confidence', type=int, help='Confidence (1-10)')
    update_p.add_argument('--blockers', help='Blockers')
    update_p.add_argument('--thesis', help='Deal thesis')
    update_p.set_defaults(func=update_deal)
    
    # log
    log_p = subparsers.add_parser('log', help='Log activity')
    log_p.add_argument('deal_id', help='Deal ID')
    log_p.add_argument('activity_type', choices=ACTIVITY_TYPES, help='Activity type')
    log_p.add_argument('--desc', help='Description')
    log_p.add_argument('--channel', help='Channel used')
    log_p.add_argument('--outcome', help='Outcome')
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

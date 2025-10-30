#!/usr/bin/env python3
"""
LinkedIn Conversation Query Tool

Query LinkedIn conversations, commitments, and pending responses from Kondo webhook data.

Usage:
    linkedin_query.py pending [--threshold-hours=48]
    linkedin_query.py commitments [--mine|--theirs] [--status=PENDING]
    linkedin_query.py conversation <id>
    linkedin_query.py search <name>
    linkedin_query.py stats

Version: 1.0.0
Created: 2025-10-30
"""

import sqlite3
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = Path('/home/workspace/Knowledge/linkedin/linkedin.db')

def get_connection() -> sqlite3.Connection:
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Run the webhook service first to create the database.")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_elapsed_time(ms: int) -> str:
    """Format elapsed time in milliseconds to human-readable"""
    hours = ms / 3600000
    if hours < 1:
        return f"{int(ms / 60000)} min"
    elif hours < 24:
        return f"{hours:.1f} hrs"
    else:
        return f"{hours / 24:.1f} days"

def format_timestamp(ms: int) -> str:
    """Format Unix timestamp (milliseconds) to readable date"""
    return datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M')

def query_pending_responses(threshold_hours: int = 48):
    """Show conversations with pending responses"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id,
            c.participant_name,
            c.linkedin_profile_url,
            c.crm_profile_slug,
            c.last_message_at,
            ((strftime('%s', 'now') * 1000) - c.last_message_at) AS elapsed_ms,
            m.content AS last_message_content
        FROM conversations c
        LEFT JOIN messages m ON m.id = (
            SELECT id FROM messages 
            WHERE conversation_id = c.id 
            ORDER BY sent_at DESC 
            LIMIT 1
        )
        WHERE c.status = 'PENDING_RESPONSE'
            AND c.last_message_from = 'them'
            AND ((strftime('%s', 'now') * 1000) - c.last_message_at) > (? * 3600000)
        ORDER BY c.last_message_at ASC
    """, (threshold_hours,))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"✅ No pending responses (threshold: {threshold_hours} hours)")
        return
    
    print(f"📥 {len(results)} LinkedIn conversation(s) awaiting response:\n")
    
    for row in results:
        print(f"👤 {row['participant_name']}")
        print(f"   Conversation: {row['id']}")
        if row['crm_profile_slug']:
            print(f"   CRM Profile: Knowledge/crm/individuals/{row['crm_profile_slug']}.md")
        print(f"   Last message: {format_timestamp(row['last_message_at'])} ({format_elapsed_time(row['elapsed_ms'])} ago)")
        print(f"   Preview: {row['last_message_content'][:100]}...")
        if row['linkedin_profile_url']:
            print(f"   LinkedIn: {row['linkedin_profile_url']}")
        print()

def query_commitments(commitment_type: str = 'all', status: str = 'PENDING'):
    """Show commitments (what I owe or what they owe)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if commitment_type == 'mine':
        where_clauses.append("cm.commitment_type = 'I_OWE_THEM'")
    elif commitment_type == 'theirs':
        where_clauses.append("cm.commitment_type = 'THEY_OWE_ME'")
    
    if status:
        where_clauses.append("cm.status = ?")
        params.append(status)
    
    where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'
    
    cursor.execute(f"""
        SELECT
            cm.id,
            cm.what,
            cm.deadline,
            cm.status,
            cm.confidence,
            cm.commitment_type,
            c.participant_name,
            c.linkedin_profile_url,
            c.crm_profile_slug,
            m.content AS message_context,
            m.sent_at AS message_timestamp,
            cm.created_at
        FROM commitments cm
        JOIN conversations c ON cm.conversation_id = c.id
        JOIN messages m ON cm.message_id = m.id
        WHERE {where_clause}
        ORDER BY 
            CASE WHEN cm.deadline_timestamp IS NOT NULL THEN 0 ELSE 1 END,
            cm.deadline_timestamp ASC,
            cm.created_at DESC
    """, params)
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"✅ No {commitment_type} commitments with status {status}")
        return
    
    type_label = "My" if commitment_type == 'mine' else ("Their" if commitment_type == 'theirs' else "All")
    print(f"📌 {len(results)} {type_label} commitment(s):\n")
    
    for row in results:
        type_icon = "💼" if row['commitment_type'] == 'I_OWE_THEM' else "🎯"
        print(f"{type_icon} {row['what']}")
        print(f"   To/From: {row['participant_name']}")
        if row['deadline']:
            print(f"   Deadline: {row['deadline']}")
        print(f"   Status: {row['status']} (confidence: {row['confidence']:.0%})")
        if row['crm_profile_slug']:
            print(f"   CRM: Knowledge/crm/individuals/{row['crm_profile_slug']}.md")
        print(f"   Context: {row['message_context'][:100]}...")
        print()

def query_conversation(conversation_id: str):
    """Show full conversation by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get conversation metadata
    cursor.execute("""
        SELECT * FROM conversations WHERE id = ?
    """, (conversation_id,))
    
    conv = cursor.fetchone()
    if not conv:
        print(f"❌ Conversation not found: {conversation_id}")
        conn.close()
        return
    
    print(f"💬 Conversation with {conv['participant_name']}")
    print(f"   ID: {conv['id']}")
    print(f"   Status: {conv['status']}")
    print(f"   Messages: {conv['message_count']}")
    print(f"   First message: {format_timestamp(conv['first_message_at'])}")
    print(f"   Last message: {format_timestamp(conv['last_message_at'])} (from {conv['last_message_from']})")
    if conv['crm_profile_slug']:
        print(f"   CRM Profile: Knowledge/crm/individuals/{conv['crm_profile_slug']}.md")
    if conv['linkedin_profile_url']:
        print(f"   LinkedIn: {conv['linkedin_profile_url']}")
    print()
    
    # Get messages
    cursor.execute("""
        SELECT * FROM messages 
        WHERE conversation_id = ?
        ORDER BY sent_at ASC
    """, (conversation_id,))
    
    messages = cursor.fetchall()
    print(f"📜 {len(messages)} message(s):\n")
    
    for msg in messages:
        print(f"[{format_timestamp(msg['sent_at'])}] {msg['sender']}:")
        print(f"  {msg['content']}\n")
    
    # Get commitments
    cursor.execute("""
        SELECT * FROM commitments
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    """, (conversation_id,))
    
    commitments = cursor.fetchall()
    if commitments:
        print(f"📌 {len(commitments)} commitment(s) extracted:\n")
        for cm in commitments:
            type_icon = "💼" if cm['commitment_type'] == 'I_OWE_THEM' else "🎯"
            print(f"{type_icon} {cm['what']}")
            print(f"   Type: {cm['commitment_type']} | Status: {cm['status']}")
            if cm['deadline']:
                print(f"   Deadline: {cm['deadline']}")
            print()
    
    conn.close()

def search_conversations(query: str):
    """Search conversations by participant name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id,
            c.participant_name,
            c.participant_email,
            c.linkedin_profile_url,
            c.crm_profile_slug,
            c.message_count,
            c.status,
            c.last_message_at,
            c.last_message_from
        FROM conversations c
        WHERE c.participant_name LIKE ?
           OR c.participant_email LIKE ?
        ORDER BY c.last_message_at DESC
    """, (f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"❌ No conversations found matching: {query}")
        return
    
    print(f"🔍 Found {len(results)} conversation(s) matching '{query}':\n")
    
    for row in results:
        print(f"👤 {row['participant_name']}")
        print(f"   ID: {row['id']}")
        print(f"   Status: {row['status']}")
        print(f"   Messages: {row['message_count']}")
        print(f"   Last: {format_timestamp(row['last_message_at'])} (from {row['last_message_from']})")
        if row['crm_profile_slug']:
            print(f"   CRM: Knowledge/crm/individuals/{row['crm_profile_slug']}.md")
        print()

def show_stats():
    """Show database statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Conversations
    cursor.execute("SELECT COUNT(*) as count, status FROM conversations GROUP BY status")
    conv_stats = cursor.fetchall()
    
    # Messages
    cursor.execute("SELECT COUNT(*) as count FROM messages")
    msg_count = cursor.fetchone()['count']
    
    # Commitments
    cursor.execute("SELECT COUNT(*) as count, status, commitment_type FROM commitments GROUP BY status, commitment_type")
    commit_stats = cursor.fetchall()
    
    # Pending responses
    cursor.execute("""
        SELECT COUNT(*) as count FROM conversations 
        WHERE status = 'PENDING_RESPONSE' AND last_message_from = 'them'
    """)
    pending_count = cursor.fetchone()['count']
    
    conn.close()
    
    print("📊 LinkedIn Intelligence System Stats\n")
    
    print("💬 Conversations:")
    for row in conv_stats:
        print(f"   {row['status']}: {row['count']}")
    
    print(f"\n📨 Total Messages: {msg_count}")
    
    print(f"\n⏳ Pending Responses: {pending_count}")
    
    if commit_stats:
        print("\n📌 Commitments:")
        for row in commit_stats:
            print(f"   {row['commitment_type']} ({row['status']}): {row['count']}")

def main():
    parser = argparse.ArgumentParser(
        description='Query LinkedIn conversation data from Kondo webhooks',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Pending responses command
    pending_parser = subparsers.add_parser('pending', help='Show pending responses')
    pending_parser.add_argument('--threshold-hours', type=int, default=48,
                               help='Threshold in hours (default: 48)')
    
    # Commitments command
    commit_parser = subparsers.add_parser('commitments', help='Show commitments')
    commit_parser.add_argument('--mine', action='store_true', help='Show only my commitments')
    commit_parser.add_argument('--theirs', action='store_true', help='Show only their commitments')
    commit_parser.add_argument('--status', default='PENDING',
                              help='Filter by status (default: PENDING)')
    
    # Conversation command
    conv_parser = subparsers.add_parser('conversation', help='Show full conversation')
    conv_parser.add_argument('id', help='Conversation ID')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search conversations by name')
    search_parser.add_argument('query', help='Search query')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'pending':
            query_pending_responses(args.threshold_hours)
        elif args.command == 'commitments':
            commitment_type = 'mine' if args.mine else ('theirs' if args.theirs else 'all')
            query_commitments(commitment_type, args.status)
        elif args.command == 'conversation':
            query_conversation(args.id)
        elif args.command == 'search':
            search_conversations(args.query)
        elif args.command == 'stats':
            show_stats()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Journal CLI - Quick journaling with typed entries and SQLite storage.

Usage:
    journal.py new [TYPE]           Start a new journal entry (default: journal)
    journal.py list [--type TYPE] [--days N] [--limit N]   List recent entries
    journal.py view ID              View a specific entry
    journal.py types                List available entry types
    journal.py edit ID              Edit an existing entry
    journal.py search QUERY         Search entries by content

Entry Types:
    - journal          General journaling
    - morning_pages    Morning stream-of-consciousness
    - evening          Evening reflection
    - gratitude        Gratitude practice
    - weekly_review    Weekly reflection
    - idea             Idea capture
    - custom           Any custom type you specify

Examples:
    python3 journal.py new morning_pages
    python3 journal.py new evening
    python3 journal.py list --type morning_pages --days 7
    python3 journal.py view 42
"""

import argparse
import sqlite3
import subprocess
import tempfile
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent

DB_PATH = Path("/home/workspace/N5/data/journal.db")
EDITOR = os.environ.get("EDITOR", "nano")

ENTRY_TYPES = {
    "journal": "General journaling",
    "morning_pages": "Morning stream-of-consciousness writing",
    "evening": "Evening reflection on the day",
    "gratitude": "Gratitude practice - what you're thankful for",
    "weekly_review": "Weekly reflection and planning",
    "idea": "Idea capture and exploration",
    "temptation": "Urge awareness and temptation check-in",
}

PROMPTS = {
    "journal": "Write freely about whatever is on your mind...\n\n",
    "morning_pages": dedent("""
        Morning Pages - Stream of consciousness writing
        ===============================================
        Write whatever comes to mind. Don't edit, don't judge.
        Just let the thoughts flow onto the page.
        
        ---
        
    """).strip() + "\n\n",
    "evening": dedent("""
        Evening Reflection
        ==================
        
        What went well today?
        
        
        What could have gone better?
        
        
        What did I learn?
        
        
        What am I grateful for?
        
    """).strip() + "\n",
    "gratitude": dedent("""
        Gratitude Practice
        ==================
        
        Three things I'm grateful for today:
        
        1. 
        
        2. 
        
        3. 
        
        Why these matter to me:
        
    """).strip() + "\n",
    "weekly_review": dedent("""
        Weekly Review
        =============
        
        ## Wins this week
        
        
        ## Challenges faced
        
        
        ## Lessons learned
        
        
        ## Focus for next week
        
        
        ## Energy/mood reflection
        
    """).strip() + "\n",
    "idea": dedent("""
        Idea Capture
        ============
        
        The idea:
        
        
        Why it matters:
        
        
        Next steps to explore:
        
    """).strip() + "\n",
}


def init_db():
    """Initialize the database schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            entry_type TEXT NOT NULL DEFAULT 'journal',
            content TEXT NOT NULL,
            mood TEXT,
            tags TEXT,
            word_count INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entry_type ON journal_entries(entry_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at ON journal_entries(created_at)
    """)
    
    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def new_entry(entry_type: str, mood: str = None, tags: str = None):
    """Create a new journal entry using the default editor."""
    if entry_type not in ENTRY_TYPES and entry_type != "custom":
        print(f"Unknown entry type: {entry_type}")
        print(f"Available types: {', '.join(ENTRY_TYPES.keys())}")
        print("Or use any custom type name.")
        # Allow custom types anyway
    
    # Get the prompt template
    prompt = PROMPTS.get(entry_type, f"# {entry_type.replace('_', ' ').title()}\n\n")
    
    # Create temp file with prompt
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        temp_path = f.name
    
    # Open editor
    try:
        subprocess.run([EDITOR, temp_path], check=True)
    except subprocess.CalledProcessError:
        print("Editor exited with error.")
        os.unlink(temp_path)
        return None
    except FileNotFoundError:
        print(f"Editor not found: {EDITOR}")
        print("Set EDITOR environment variable or install nano.")
        os.unlink(temp_path)
        return None
    
    # Read content
    with open(temp_path, 'r') as f:
        content = f.read()
    
    os.unlink(temp_path)
    
    # Check if content was actually written (beyond the prompt)
    if content.strip() == prompt.strip():
        print("No content added. Entry not saved.")
        return None
    
    # Save to database
    word_count = len(content.split())
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO journal_entries (entry_type, content, mood, tags, word_count)
        VALUES (?, ?, ?, ?, ?)
    """, (entry_type, content, mood, tags, word_count))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Entry #{entry_id} saved ({word_count} words)")
    return entry_id


def list_entries(entry_type: str = None, days: int = None, limit: int = 20):
    """List recent journal entries."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT id, created_at, entry_type, word_count, substr(content, 1, 80) as preview FROM journal_entries"
    params = []
    conditions = []
    
    if entry_type:
        conditions.append("entry_type = ?")
        params.append(entry_type)
    
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        conditions.append("created_at >= ?")
        params.append(cutoff.isoformat())
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No entries found.")
        return
    
    print(f"\n{'ID':>5} | {'Date':^19} | {'Type':^15} | {'Words':>5} | Preview")
    print("-" * 90)
    
    for row in rows:
        created = row['created_at'][:16] if row['created_at'] else 'Unknown'
        preview = row['preview'].replace('\n', ' ')[:40] + '...' if len(row['preview']) > 40 else row['preview'].replace('\n', ' ')
        print(f"{row['id']:>5} | {created:^19} | {row['entry_type']:^15} | {row['word_count']:>5} | {preview}")
    
    print(f"\n{len(rows)} entries shown")


def view_entry(entry_id: int):
    """View a specific journal entry."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"Entry #{entry_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print(f"Entry #{row['id']} - {row['entry_type']}")
    print(f"Created: {row['created_at']}")
    if row['updated_at'] != row['created_at']:
        print(f"Updated: {row['updated_at']}")
    if row['mood']:
        print(f"Mood: {row['mood']}")
    if row['tags']:
        print(f"Tags: {row['tags']}")
    print(f"Words: {row['word_count']}")
    print(f"{'='*60}\n")
    print(row['content'])
    print(f"\n{'='*60}")


def edit_entry(entry_id: int):
    """Edit an existing journal entry."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"Entry #{entry_id} not found.")
        conn.close()
        return
    
    # Create temp file with existing content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(row['content'])
        temp_path = f.name
    
    # Open editor
    try:
        subprocess.run([EDITOR, temp_path], check=True)
    except subprocess.CalledProcessError:
        print("Editor exited with error.")
        os.unlink(temp_path)
        conn.close()
        return
    
    # Read updated content
    with open(temp_path, 'r') as f:
        content = f.read()
    
    os.unlink(temp_path)
    
    # Update database
    word_count = len(content.split())
    cursor.execute("""
        UPDATE journal_entries 
        SET content = ?, word_count = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (content, word_count, entry_id))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Entry #{entry_id} updated ({word_count} words)")


def search_entries(query: str, limit: int = 20):
    """Search entries by content."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, entry_type, word_count, substr(content, 1, 80) as preview 
        FROM journal_entries 
        WHERE content LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No entries matching '{query}'")
        return
    
    print(f"\nSearch results for '{query}':")
    print(f"\n{'ID':>5} | {'Date':^19} | {'Type':^15} | {'Words':>5} | Preview")
    print("-" * 90)
    
    for row in rows:
        created = row['created_at'][:16] if row['created_at'] else 'Unknown'
        preview = row['preview'].replace('\n', ' ')[:40] + '...'
        print(f"{row['id']:>5} | {created:^19} | {row['entry_type']:^15} | {row['word_count']:>5} | {preview}")


def add_entry(entry_type: str, content: str, mood: str = None, tags: str = None):
    """Add a journal entry programmatically (used by Zo after conversational reflection)."""
    if not content or not content.strip():
        print("Error: Content cannot be empty.")
        return None
    
    word_count = len(content.split())
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO journal_entries (entry_type, content, mood, tags, word_count)
        VALUES (?, ?, ?, ?, ?)
    """, (entry_type, content, mood, tags, word_count))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Entry #{entry_id} saved ({word_count} words) - {entry_type}")
    return entry_id


def list_types():
    """List available entry types with descriptions."""
    print("\nAvailable entry types:\n")
    for name, desc in ENTRY_TYPES.items():
        print(f"  {name:15} - {desc}")
    print("\nYou can also use any custom type name.")
    
    # Show stats for types in use
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entry_type, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY entry_type 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        print("\nYour entries by type:")
        for row in rows:
            print(f"  {row['entry_type']:15} - {row['count']} entries")


def main():
    parser = argparse.ArgumentParser(
        description="Journal CLI - Quick journaling with typed entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # new command
    new_parser = subparsers.add_parser('new', help='Create a new entry')
    new_parser.add_argument('type', nargs='?', default='journal', help='Entry type')
    new_parser.add_argument('--mood', help='Current mood')
    new_parser.add_argument('--tags', help='Comma-separated tags')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List recent entries')
    list_parser.add_argument('--type', '-t', help='Filter by entry type')
    list_parser.add_argument('--days', '-d', type=int, help='Entries from last N days')
    list_parser.add_argument('--limit', '-n', type=int, default=20, help='Max entries to show')
    
    # view command
    view_parser = subparsers.add_parser('view', help='View a specific entry')
    view_parser.add_argument('id', type=int, help='Entry ID')
    
    # edit command
    edit_parser = subparsers.add_parser('edit', help='Edit an existing entry')
    edit_parser.add_argument('id', type=int, help='Entry ID')
    
    # search command
    search_parser = subparsers.add_parser('search', help='Search entries')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-n', type=int, default=20, help='Max results')
    
    # types command
    subparsers.add_parser('types', help='List available entry types')
    
    # add command (programmatic)
    add_parser = subparsers.add_parser('add', help='Add entry programmatically')
    add_parser.add_argument('type', help='Entry type')
    add_parser.add_argument('content', help='Entry content')
    add_parser.add_argument('--mood', help='Current mood')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    
    args = parser.parse_args()
    
    if args.command == 'new':
        new_entry(args.type, args.mood, args.tags)
    elif args.command == 'list':
        list_entries(args.type, args.days, args.limit)
    elif args.command == 'view':
        view_entry(args.id)
    elif args.command == 'edit':
        edit_entry(args.id)
    elif args.command == 'search':
        search_entries(args.query, args.limit)
    elif args.command == 'types':
        list_types()
    elif args.command == 'add':
        add_entry(args.type, args.content, args.mood, args.tags)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()



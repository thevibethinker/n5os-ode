#!/usr/bin/env python3
"""
Voice Feedback Capture - Store before/after pairs for learning.

Usage:
  python3 N5/scripts/voice_feedback_capture.py capture \
    --original "Zo's version" \
    --improved "V's version" \
    --content-type "cold_email" \
    [--context "Partnership outreach to Julien"] \
    [--conversation-id "con_xxx"]

  python3 N5/scripts/voice_feedback_capture.py list \
    [--content-type "cold_email"] \
    [--unanalyzed-only]

  python3 N5/scripts/voice_feedback_capture.py mark-analyzed --id 5
"""

import argparse
import hashlib
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "voice_library.db"


def compute_hash(original: str, improved: str) -> str:
    combined = f"{original}||{improved}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def capture(args):
    content_hash = compute_hash(args.original, args.improved)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM feedback_pairs WHERE content_hash = ?", (content_hash,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⏭ Duplicate detected - existing pair #{existing[0]} ({args.content_type})")
        conn.close()
        return existing[0]
    
    cursor.execute("""
        INSERT INTO feedback_pairs (original_text, improved_text, content_type, context, conversation_id, content_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (args.original, args.improved, args.content_type, args.context, args.conversation_id, content_hash))
    
    pair_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Captured feedback pair #{pair_id} ({args.content_type})")
    return pair_id


def list_pairs(args):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT id, content_type, context, created_at, analyzed, original_text, improved_text FROM feedback_pairs WHERE 1=1"
    params = []
    
    if args.content_type:
        query += " AND content_type = ?"
        params.append(args.content_type)
    
    if args.unanalyzed_only:
        query += " AND analyzed = 0"
    
    query += " ORDER BY created_at DESC LIMIT 20"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No feedback pairs found.")
        return
    
    print(f"{'ID':<5} {'Type':<15} {'Analyzed':<10} {'Created':<20} {'Context':<30}")
    print("-" * 80)
    
    for row in rows:
        analyzed = "✓" if row["analyzed"] else "○"
        context = (row["context"] or "—")[:28]
        created = row["created_at"][:16] if row["created_at"] else "—"
        print(f"{row['id']:<5} {row['content_type']:<15} {analyzed:<10} {created:<20} {context:<30}")
    
    print(f"\n{len(rows)} pair(s) shown")
    
    if args.verbose and rows:
        print("\n--- Preview of most recent pair ---")
        row = rows[0]
        print(f"Original (truncated): {row['original_text'][:100]}...")
        print(f"Improved (truncated): {row['improved_text'][:100]}...")


def mark_analyzed(args):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE feedback_pairs SET analyzed = 1 WHERE id = ?", (args.id,))
    
    if cursor.rowcount == 0:
        print(f"✗ No pair found with ID #{args.id}")
        conn.close()
        return False
    
    conn.commit()
    conn.close()
    print(f"✓ Marked pair #{args.id} as analyzed")
    return True


def main():
    parser = argparse.ArgumentParser(description="Voice Feedback Capture")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    capture_parser = subparsers.add_parser("capture", help="Capture a feedback pair")
    capture_parser.add_argument("--original", required=True, help="Zo's original version")
    capture_parser.add_argument("--improved", required=True, help="V's improved version")
    capture_parser.add_argument("--content-type", required=True, help="Type of content (cold_email, linkedin_post, memo, etc.)")
    capture_parser.add_argument("--context", help="Optional context (the ask, audience, etc.)")
    capture_parser.add_argument("--conversation-id", help="Conversation ID for provenance")
    
    list_parser = subparsers.add_parser("list", help="List feedback pairs")
    list_parser.add_argument("--content-type", help="Filter by content type")
    list_parser.add_argument("--unanalyzed-only", action="store_true", help="Show only unanalyzed pairs")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show preview of content")
    
    mark_parser = subparsers.add_parser("mark-analyzed", help="Mark a pair as analyzed")
    mark_parser.add_argument("--id", type=int, required=True, help="Pair ID to mark")
    
    args = parser.parse_args()
    
    if args.command == "capture":
        capture(args)
    elif args.command == "list":
        list_pairs(args)
    elif args.command == "mark-analyzed":
        mark_analyzed(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

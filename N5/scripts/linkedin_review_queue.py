#!/usr/bin/env python3
"""
LinkedIn → CRM Review Queue Manager

Manages the queue of LinkedIn contacts who don't have CRM profiles yet.
V reviews and approves/rejects before they get added to CRM.

Usage:
  python3 linkedin_review_queue.py scan          # Find new contacts to review
  python3 linkedin_review_queue.py pending       # List pending reviews
  python3 linkedin_review_queue.py approve <name> [--notes "reason"]
  python3 linkedin_review_queue.py reject <name> [--notes "reason"]
  python3 linkedin_review_queue.py ignore <name>  # Won't show again
  python3 linkedin_review_queue.py digest        # Generate review digest for V
"""

import argparse
import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

LINKEDIN_DB = Path("/home/workspace/Knowledge/linkedin/linkedin.db")
CRM_PROFILES_DIR = Path("/home/workspace/N5/crm_v3/profiles")

def slugify(name: str) -> str:
    """Convert name to slug format."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '_', slug)
    return slug.strip('_')

def find_matching_profile(name: str) -> Optional[Path]:
    """Find CRM profile matching the name."""
    if not name or name == 'Unknown':
        return None
    
    clean_name = re.sub(r'[^\w\s]', '', name).strip()
    name_parts = clean_name.lower().split()
    
    if len(name_parts) < 2:
        return None
    
    first_name = name_parts[0]
    last_name = name_parts[-1]
    
    for profile in CRM_PROFILES_DIR.glob("*.yaml"):
        stem_lower = profile.stem.lower()
        if first_name in stem_lower and last_name in stem_lower:
            return profile
    
    full_slug = slugify(clean_name)
    for profile in CRM_PROFILES_DIR.glob("*.yaml"):
        if full_slug == profile.stem.lower().replace('_', ''):
            return profile
    
    return None

def scan_for_new_contacts(conn: sqlite3.Connection) -> int:
    """Scan LinkedIn conversations and add unmatched contacts to review queue."""
    cursor = conn.execute("""
        SELECT 
            c.id,
            c.participant_name,
            c.linkedin_profile_url,
            c.contact_headline,
            c.contact_location,
            c.message_count,
            c.last_message_at
        FROM conversations c
        LEFT JOIN crm_review_queue q ON c.id = q.conversation_id
        WHERE c.participant_name IS NOT NULL
          AND c.participant_name != 'Unknown'
          AND q.id IS NULL
    """)
    
    added = 0
    for row in cursor.fetchall():
        conv_id, name, url, headline, location, msg_count, last_msg = row
        
        # Check if they already have a CRM profile
        if find_matching_profile(name):
            continue
        
        # Add to review queue (UPSERT)
        try:
            conn.execute("""
                INSERT INTO crm_review_queue 
                (conversation_id, participant_name, linkedin_url, headline, location, message_count, last_message_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conv_id, name, url, headline, location, msg_count or 1, last_msg))
            added += 1
            print(f"  + {name}")
        except Exception as e:
            print(f"  ! Error adding {name}: {e}")
    
    conn.commit()
    return added

def list_pending(conn: sqlite3.Connection) -> list[dict]:
    """List all pending reviews."""
    cursor = conn.execute("""
        SELECT 
            q.participant_name,
            q.headline,
            q.location,
            q.message_count,
            datetime(q.first_seen_at/1000, 'unixepoch') as first_seen,
            datetime(q.last_message_at/1000, 'unixepoch') as last_message,
            c.status as conv_status
        FROM crm_review_queue q
        JOIN conversations c ON q.conversation_id = c.id
        WHERE q.status = 'PENDING'
        ORDER BY q.message_count DESC, q.last_message_at DESC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def update_status(conn: sqlite3.Connection, name: str, status: str, notes: Optional[str] = None) -> bool:
    """Update a contact's review status."""
    cursor = conn.execute("""
        UPDATE crm_review_queue
        SET status = ?, reviewed_at = strftime('%s', 'now') * 1000, notes = ?
        WHERE participant_name LIKE ? AND status = 'PENDING'
    """, (status, notes, f"%{name}%"))
    conn.commit()
    return cursor.rowcount > 0

def generate_digest(conn: sqlite3.Connection) -> str:
    """Generate a markdown digest of pending reviews for V."""
    pending = list_pending(conn)
    
    if not pending:
        return "## LinkedIn Review Queue\n\n✅ No pending contacts to review!"
    
    # Group by engagement level
    high_engagement = [p for p in pending if (p['message_count'] or 0) >= 3]
    medium_engagement = [p for p in pending if 1 < (p['message_count'] or 0) < 3]
    low_engagement = [p for p in pending if (p['message_count'] or 0) <= 1]
    
    digest = "## LinkedIn Review Queue\n\n"
    digest += f"**{len(pending)} contacts** awaiting review\n\n"
    
    if high_engagement:
        digest += "### 🔥 High Engagement (3+ messages)\n"
        digest += "*These folks have had real conversations with you*\n\n"
        for p in high_engagement:
            digest += f"**{p['participant_name']}**\n"
            if p['headline']:
                digest += f"  - {p['headline'][:80]}{'...' if len(p['headline'] or '') > 80 else ''}\n"
            if p['location']:
                digest += f"  - 📍 {p['location']}\n"
            digest += f"  - 💬 {p['message_count']} messages | Last: {p['last_message'] or 'Unknown'}\n"
            if p['conv_status'] == 'PENDING_RESPONSE':
                digest += f"  - ⏳ Awaiting your reply\n"
            digest += "\n"
    
    if medium_engagement:
        digest += "### 💬 Medium Engagement (2 messages)\n"
        for p in medium_engagement:
            digest += f"- **{p['participant_name']}**"
            if p['headline']:
                digest += f" — {p['headline'][:50]}..."
            digest += "\n"
        digest += "\n"
    
    if low_engagement:
        digest += f"### 📩 Low Engagement ({len(low_engagement)} contacts with 1 message)\n"
        digest += "*Likely cold outreach or initial connections*\n\n"
        # Just show names in compact format
        names = [p['participant_name'] for p in low_engagement[:10]]
        digest += ", ".join(names)
        if len(low_engagement) > 10:
            digest += f", ... and {len(low_engagement) - 10} more"
        digest += "\n"
    
    digest += "\n---\n"
    digest += "**Commands:**\n"
    digest += "- `python3 N5/scripts/linkedin_review_queue.py approve \"Name\"` — Add to CRM\n"
    digest += "- `python3 N5/scripts/linkedin_review_queue.py reject \"Name\"` — Not interested\n"
    digest += "- `python3 N5/scripts/linkedin_review_queue.py ignore \"Name\"` — Hide from queue\n"
    
    return digest

def get_approved_for_enrichment(conn: sqlite3.Connection) -> list[dict]:
    """Get approved contacts ready for CRM creation and Aviato enrichment."""
    cursor = conn.execute("""
        SELECT 
            q.conversation_id,
            q.participant_name,
            q.linkedin_url,
            q.headline,
            q.location,
            c.contact_picture_url,
            c.connected_at,
            c.participant_email,
            c.message_count,
            c.first_message_at,
            c.last_message_at
        FROM crm_review_queue q
        JOIN conversations c ON q.conversation_id = c.id
        WHERE q.status = 'APPROVED'
    """)
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def approve_contact(conn, name: str, notes: str = None):
    """Mark a contact as approved and trigger CRM creation + Aviato enrichment."""
    cursor = conn.execute("""
        UPDATE crm_review_queue 
        SET status = 'APPROVED', 
            reviewed_at = ?,
            notes = ?
        WHERE participant_name LIKE ? AND status = 'PENDING'
    """, (int(datetime.now().timestamp() * 1000), notes, f"%{name}%"))
    
    if cursor.rowcount == 0:
        print(f"❌ No pending contact found matching '{name}'")
        return False
    
    conn.commit()
    print(f"✅ Approved: {name}")
    
    # Trigger enrichment pipeline
    import subprocess
    result = subprocess.run([
        'python3', '/home/workspace/N5/scripts/linkedin_approve_and_enrich.py',
        'approve', name
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"⚠️  Enrichment output: {result.stderr or result.stdout}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="LinkedIn CRM Review Queue Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # scan
    subparsers.add_parser("scan", help="Scan for new contacts to review")
    
    # pending
    subparsers.add_parser("pending", help="List pending reviews")
    
    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve a contact for CRM")
    approve_parser.add_argument("name", help="Contact name (partial match)")
    approve_parser.add_argument("--notes", help="Reason for approval")
    
    # reject
    reject_parser = subparsers.add_parser("reject", help="Reject a contact")
    reject_parser.add_argument("name", help="Contact name (partial match)")
    reject_parser.add_argument("--notes", help="Reason for rejection")
    
    # ignore
    ignore_parser = subparsers.add_parser("ignore", help="Ignore a contact (won't show again)")
    ignore_parser.add_argument("name", help="Contact name (partial match)")
    
    # digest
    subparsers.add_parser("digest", help="Generate review digest")
    
    # approved (list approved for processing)
    subparsers.add_parser("approved", help="List approved contacts for enrichment")
    
    args = parser.parse_args()
    
    conn = sqlite3.connect(LINKEDIN_DB)
    
    try:
        if args.command == "scan":
            print("🔍 Scanning for new LinkedIn contacts...")
            added = scan_for_new_contacts(conn)
            print(f"\n✅ Added {added} contacts to review queue")
            
        elif args.command == "pending":
            pending = list_pending(conn)
            print(f"📋 {len(pending)} pending reviews:\n")
            for p in pending:
                print(f"  {p['participant_name']}")
                if p['headline']:
                    print(f"    └─ {p['headline'][:60]}...")
                print(f"    └─ {p['message_count']} msgs, last: {p['last_message']}")
                
        elif args.command == "approve":
            if approve_contact(conn, args.name, args.notes):
                print("   Run `linkedin_review_queue.py approved` to see contacts ready for CRM creation")
            else:
                print(f"❌ No pending contact matching '{args.name}'")
                
        elif args.command == "reject":
            if update_status(conn, args.name, "REJECTED", args.notes):
                print(f"❌ Rejected: {args.name}")
            else:
                print(f"❌ No pending contact matching '{args.name}'")
                
        elif args.command == "ignore":
            if update_status(conn, args.name, "IGNORED"):
                print(f"🙈 Ignored: {args.name}")
            else:
                print(f"❌ No pending contact matching '{args.name}'")
                
        elif args.command == "digest":
            digest = generate_digest(conn)
            print(digest)
            
        elif args.command == "approved":
            approved = get_approved_for_enrichment(conn)
            print(f"✅ {len(approved)} approved contacts ready for CRM creation:\n")
            for a in approved:
                print(f"  {a['participant_name']}")
                if a['headline']:
                    print(f"    └─ {a['headline'][:60]}...")
                if a['linkedin_url']:
                    print(f"    └─ {a['linkedin_url']}")
                    
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())




#!/usr/bin/env python3
"""Stakeholder Intel Viewer

Given either:
- a CRM person_id slug (matching Personal/Knowledge/CRM/individuals/<slug>.md), OR
- a calendar meeting ID (as recorded in the "**Meeting IDs:**" metadata field),
- a database person ID (integer)

assemble a consolidated intelligence view from:
- Unified n5_core.db (people, deals, interactions)
- CRM individual markdown
- Kondo/LinkedIn DB (Knowledge/linkedin/linkedin.db)
- Aviato usage log (N5/logs/aviato_usage.jsonl)

UPDATED 2026-01-19: Now uses unified n5_core.db for primary lookups.
Includes deal involvement in stakeholder intelligence.

Usage examples:
    stakeholder_intel.py --person-id lauren-salitan
    stakeholder_intel.py --db-id 42
    stakeholder_intel.py --meeting-id 4f1si317tp728hmnjcrtc82hc7

This is read-only: it prints intel, does not modify any files.
"""

import argparse
import json
import logging
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from db_paths import get_db_connection, PEOPLE_TABLE, INTERACTIONS_TABLE, DEAL_ROLES_TABLE, DEALS_TABLE
from crm_paths import CRM_INDIVIDUALS

WORKSPACE = Path("/home/workspace")
CRM_DIR = CRM_INDIVIDUALS
LINKEDIN_DB = WORKSPACE / "Knowledge/linkedin/linkedin.db"
AVIATO_LOG = WORKSPACE / "N5/logs/aviato_usage.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _fmt_ms(ts_ms: Optional[int]) -> str:
    """Format a millisecond unix timestamp into a human-readable ET string."""
    if ts_ms is None:
        return "unknown time"
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        return str(ts_ms)


def get_person_from_db(slug: str = None, db_id: int = None, email: str = None) -> Optional[Dict]:
    """Get person from unified database.
    
    Returns dict with all person fields or None.
    """
    conn = get_db_connection(readonly=True)
    try:
        if db_id:
            row = conn.execute(f"SELECT * FROM {PEOPLE_TABLE} WHERE id = ?", (db_id,)).fetchone()
        elif email:
            row = conn.execute(f"SELECT * FROM {PEOPLE_TABLE} WHERE email = ?", (email,)).fetchone()
        elif slug:
            # Try to find by markdown_path ending with slug
            row = conn.execute(
                f"SELECT * FROM {PEOPLE_TABLE} WHERE markdown_path LIKE ?",
                (f"%/{slug}.md",)
            ).fetchone()
            if not row:
                # Try name match
                row = conn.execute(
                    f"SELECT * FROM {PEOPLE_TABLE} WHERE LOWER(REPLACE(full_name, ' ', '-')) = LOWER(?)",
                    (slug,)
                ).fetchone()
        else:
            return None
        
        return dict(row) if row else None
    finally:
        conn.close()


def get_person_deals(person_id: int) -> List[Dict]:
    """Get all deals involving this person."""
    conn = get_db_connection(readonly=True)
    try:
        rows = conn.execute(
            f"""
            SELECT 
                d.id as deal_id,
                d.company,
                d.deal_type,
                d.pipeline,
                d.stage,
                d.temperature,
                dr.role,
                dr.context
            FROM {DEAL_ROLES_TABLE} dr
            JOIN {DEALS_TABLE} d ON dr.deal_id = d.id
            WHERE dr.person_id = ?
            ORDER BY d.updated_at DESC
            """,
            (person_id,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_person_interactions(person_id: int, limit: int = 10) -> List[Dict]:
    """Get recent interactions for a person."""
    conn = get_db_connection(readonly=True)
    try:
        rows = conn.execute(
            f"""
            SELECT 
                type, direction, summary, source_ref, occurred_at
            FROM {INTERACTIONS_TABLE}
            WHERE person_id = ?
            ORDER BY occurred_at DESC
            LIMIT ?
            """,
            (person_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def load_crm_profile(slug: str) -> Optional[str]:
    """Load CRM markdown profile by slug."""
    path = CRM_DIR / f"{slug}.md"
    if not path.exists():
        logger.warning(f"CRM profile not found: {path}")
        return None
    return path.read_text(encoding="utf-8")


def extract_linkedin_metadata(md: str) -> Dict[str, Any]:
    """Extract LinkedIn URL and conversation ID from markdown."""
    linkedin_url = None
    convo_id = None

    url_match = re.search(r"\*\*LinkedIn URL:?\*\*\s*(https?://\S+)", md)
    if url_match:
        linkedin_url = url_match.group(1).strip()

    convo_match = re.search(r"\*\*LinkedIn Conversation ID \(Kondo\):\*\*\s*([\w-]+)", md)
    if not convo_match:
        convo_match = re.search(r"\*\*LinkedIn conversation IDs?:\*\*\s*([\w-]+)", md)
    if convo_match:
        convo_id = convo_match.group(1).strip()

    return {"linkedin_url": linkedin_url, "linkedin_conversation_id": convo_id}


def query_linkedin_conversation(conversation_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Query Kondo LinkedIn DB for conversation details."""
    if not conversation_id:
        return None
    if not LINKEDIN_DB.exists():
        logger.warning("LinkedIn DB not found; skipping LinkedIn intel")
        return None

    conn = sqlite3.connect(LINKEDIN_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, participant_name, participant_email, linkedin_profile_url, status,
               first_message_at, last_message_at, last_message_from, message_count
        FROM conversations
        WHERE id = ?
        """,
        (conversation_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    conv = dict(row)

    cur.execute(
        """
        SELECT sender, content, sent_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY sent_at DESC
        LIMIT 10
        """,
        (conversation_id,),
    )
    messages = [dict(r) for r in cur.fetchall()]
    conn.close()

    return {"conversation": conv, "messages": messages}


def lookup_aviato_events(email: Optional[str]) -> Dict[str, Any]:
    """Look up Aviato enrichment events for an email."""
    info = {"exists": AVIATO_LOG.exists(), "events": []}
    if not email or not info["exists"]:
        return info

    events: List[Dict[str, Any]] = []
    with AVIATO_LOG.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("email") == email:
                events.append(data)
    info["events"] = events
    return info


def extract_primary_email(md: str) -> Optional[str]:
    """Extract primary email from markdown profile."""
    m = re.search(r"\*\*Email:?\*\*\s*([^\s]+)", md)
    if m:
        return m.group(1).strip()
    return None


def _extract_header_block(md: str) -> List[str]:
    """Extract the human header from a CRM markdown file."""
    header_lines: List[str] = []
    in_frontmatter = False
    frontmatter_count = 0
    
    for line in md.splitlines():
        if line.strip() == "---":
            frontmatter_count += 1
            if frontmatter_count <= 2:
                continue  # Skip YAML frontmatter
        if frontmatter_count < 2:
            continue  # Still in frontmatter
            
        if line.startswith("# "):
            header_lines.append(line)
            continue
        if any(line.startswith(f"**{field}") for field in 
               ["Organization:", "Role:", "Email:", "Status:", "LinkedIn URL:", 
                "LinkedIn Conversation ID", "Company:", "Title:"]):
            header_lines.append(line)
        elif line.startswith("## "):
            break  # Stop at first section header
    return header_lines


def summarize_intel(slug: str = None, db_id: int = None) -> None:
    """Print consolidated stakeholder intelligence."""
    
    # First try database lookup
    db_person = get_person_from_db(slug=slug, db_id=db_id)
    
    print("=" * 60)
    print("STAKEHOLDER INTELLIGENCE REPORT")
    print("=" * 60)
    
    if db_person:
        print("\n## Database Record (n5_core.db)")
        print(f"- **ID:** {db_person['id']}")
        print(f"- **Name:** {db_person['full_name']}")
        print(f"- **Email:** {db_person.get('email') or 'Not recorded'}")
        print(f"- **Company:** {db_person.get('company') or 'Not recorded'}")
        print(f"- **Title:** {db_person.get('title') or 'Not recorded'}")
        print(f"- **Category:** {db_person.get('category') or 'Not categorized'}")
        print(f"- **Status:** {db_person.get('status') or 'unknown'}")
        print(f"- **LinkedIn:** {db_person.get('linkedin_url') or 'Not recorded'}")
        print(f"- **First Contact:** {db_person.get('first_contact_date') or 'Unknown'}")
        print(f"- **Last Contact:** {db_person.get('last_contact_date') or 'Unknown'}")
        
        # Deal involvement
        print("\n## Deal Involvement")
        deals = get_person_deals(db_person['id'])
        if deals:
            for deal in deals:
                temp_emoji = {"hot": "🔥", "warm": "☀️", "cold": "❄️"}.get(deal.get('temperature'), "")
                print(f"- **{deal['company']}** ({deal['deal_type']}) - Role: {deal['role']}")
                print(f"  Pipeline: {deal['pipeline']} | Stage: {deal['stage']} | Temp: {temp_emoji} {deal.get('temperature', 'unknown')}")
                if deal.get('context'):
                    print(f"  Context: {deal['context']}")
        else:
            print("- No deal involvement recorded.")
        
        # Recent interactions from DB
        print("\n## Recent Interactions (Database)")
        interactions = get_person_interactions(db_person['id'])
        if interactions:
            for i in interactions:
                print(f"- [{i['occurred_at']}] {i['type']}: {i.get('summary', 'No summary')}")
        else:
            print("- No interactions recorded in database.")
        
        # Get slug for markdown lookup
        if db_person.get('markdown_path'):
            slug = Path(db_person['markdown_path']).stem
        email = db_person.get('email')
    else:
        email = None
        print("\n- No database record found.")
    
    # Load markdown profile
    md = load_crm_profile(slug) if slug else None
    
    if md:
        print("\n## CRM Markdown Profile")
        header = _extract_header_block(md)
        for line in header:
            print(line)
        
        if not email:
            email = extract_primary_email(md)
    else:
        print("\n- No markdown profile found.")
    
    # LinkedIn intelligence
    print("\n## LinkedIn Intelligence (Kondo)")
    linkedin_meta = extract_linkedin_metadata(md) if md else {}
    linkedin_url = linkedin_meta.get("linkedin_url") or (db_person.get('linkedin_url') if db_person else None)
    linkedin_convo_id = linkedin_meta.get("linkedin_conversation_id")
    
    li_conv = query_linkedin_conversation(linkedin_convo_id)
    
    if not linkedin_url and not linkedin_convo_id:
        print("- No LinkedIn metadata recorded.")
    elif linkedin_url and not linkedin_convo_id:
        print(f"- LinkedIn URL: {linkedin_url}")
        print("- No conversation ID linked yet (Kondo data unavailable).")
    elif linkedin_convo_id and not li_conv:
        print(f"- LinkedIn conversation ID: {linkedin_convo_id}")
        print("- No matching conversation found in Kondo DB.")
    elif li_conv:
        conv = li_conv["conversation"]
        print(f"- Name: {conv['participant_name']}")
        print(f"- Email (from LinkedIn): {conv['participant_email']}")
        print(f"- Profile URL: {conv['linkedin_profile_url']}")
        print(f"- Status: {conv['status']}")
        print(f"- First message: {_fmt_ms(conv['first_message_at'])}")
        print(f"- Last message: {_fmt_ms(conv['last_message_at'])} (from: {conv['last_message_from']})")
        print(f"- Messages: {conv['message_count']}")
        print()
        print("### Sample Messages")
        for msg in li_conv["messages"][:5]:
            print(f"- [{_fmt_ms(msg['sent_at'])}] {msg['sender']}: {msg['content'][:100]}...")

    # Aviato enrichment
    print("\n## Aviato Enrichment Events")
    aviato_info = lookup_aviato_events(email)
    if not aviato_info["exists"]:
        print("- Aviato usage log not found.")
    elif not aviato_info["events"]:
        print(f"- No events found for {email!r}.")
    else:
        for ev in aviato_info["events"]:
            status = "found" if ev.get("person_found") else "not_found"
            ts = ev.get("timestamp")
            print(f"- {ts}: {status} (success={ev.get('success')})")


def find_people_for_meeting(meeting_id: str) -> List[str]:
    """Return CRM slugs whose markdown lists the given meeting_id in '**Meeting IDs:**'."""
    slugs: List[str] = []
    pattern = re.compile(r"\*\*Meeting IDs:\*\*\s*(.+)")

    for path in sorted(CRM_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = pattern.search(text)
        if not m:
            continue
        if meeting_id in m.group(1):
            slugs.append(path.stem)
    return slugs


def find_people_for_meeting_db(meeting_id: str) -> List[int]:
    """Return person IDs from database via interactions."""
    conn = get_db_connection(readonly=True)
    try:
        rows = conn.execute(
            f"""
            SELECT DISTINCT person_id FROM {INTERACTIONS_TABLE}
            WHERE source_ref LIKE ?
            """,
            (f"%{meeting_id}%",)
        ).fetchall()
        return [row['person_id'] for row in rows]
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="View consolidated stakeholder intelligence")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--person-id", help="CRM person_id / slug (e.g., lauren-salitan)")
    group.add_argument("--db-id", type=int, help="Database person ID (integer)")
    group.add_argument("--meeting-id", help="Calendar meeting ID as stored in CRM metadata")
    args = parser.parse_args()

    if args.person_id:
        summarize_intel(slug=args.person_id)
    elif args.db_id:
        summarize_intel(db_id=args.db_id)
    elif args.meeting_id:
        # Try database first
        db_ids = find_people_for_meeting_db(args.meeting_id)
        if db_ids:
            for person_id in db_ids:
                summarize_intel(db_id=person_id)
                print("\n" + "=" * 60 + "\n")
        else:
            # Fallback to markdown
            slugs = find_people_for_meeting(args.meeting_id)
            if not slugs:
                print(f"No profiles found for meeting ID {args.meeting_id!r}.")
                return
            for slug in slugs:
                summarize_intel(slug=slug)
                print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stakeholder Intel Viewer

Given either:
- a CRM person_id slug (matching Personal/Knowledge/CRM/individuals/<slug>.md), OR
- a calendar meeting ID (as recorded in the "**Meeting IDs:**" metadata field),

assemble a consolidated intelligence view from:
- CRM individual markdown
- Kondo/LinkedIn DB (Knowledge/linkedin/linkedin.db)
- Aviato usage log (N5/logs/aviato_usage.jsonl)

Usage examples:
    stakeholder_intel.py --person-id lauren-salitan
    stakeholder_intel.py --meeting-id 4f1si317tp728hmnjcrtc82hc7

This is read-only: it prints intel, does not modify any files.
"""

import argparse
import json
import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

WORKSPACE = Path("/home/workspace")
CRM_DIR = WORKSPACE / "Personal/Knowledge/CRM/individuals"
LINKEDIN_DB = WORKSPACE / "Knowledge/linkedin/linkedin.db"
AVIATO_LOG = WORKSPACE / "N5/logs/aviato_usage.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _fmt_ms(ts_ms: Optional[int]) -> str:
    """Format a millisecond unix timestamp into a human-readable ET string.

    Falls back gracefully if ts_ms is None or not an int.
    """
    if ts_ms is None:
        return "unknown time"
    try:
        # ts_ms is milliseconds since epoch
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
        # Render in ET-equivalent offset while keeping things simple
        # (The exact offset isn't critical for intel; readability is.)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        return str(ts_ms)


def load_crm_profile(slug: str) -> Optional[str]:
    path = CRM_DIR / f"{slug}.md"
    if not path.exists():
        logger.error(f"CRM profile not found: {path}")
        return None
    return path.read_text(encoding="utf-8")


def extract_linkedin_metadata(md: str) -> Dict[str, Any]:
    linkedin_url = None
    convo_id = None

    # Allow for minor label variations around LinkedIn URL
    url_match = re.search(r"\*\*LinkedIn URL:?\*\*\s*(https?://\S+)", md)
    if url_match:
        linkedin_url = url_match.group(1).strip()

    # Support both the header "**LinkedIn Conversation ID (Kondo):**" and a
    # metadata footer "**LinkedIn conversation IDs:**"
    convo_match = re.search(r"\*\*LinkedIn Conversation ID \(Kondo\):\*\*\s*([\w-]+)", md)
    if not convo_match:
        convo_match = re.search(r"\*\*LinkedIn conversation IDs?:\*\*\s*([\w-]+)", md)
    if convo_match:
        convo_id = convo_match.group(1).strip()

    return {"linkedin_url": linkedin_url, "linkedin_conversation_id": convo_id}


def query_linkedin_conversation(conversation_id: Optional[str]) -> Optional[Dict[str, Any]]:
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
        SELECT id, participant_name, participant_email, linkedin_profile_url,
               status, first_message_at, last_message_at, last_message_from,
               message_count, crm_profile_slug
        FROM conversations
        WHERE id = ?
        """,
        (conversation_id,),
    )
    conv = cur.fetchone()
    if not conv:
        conn.close()
        return None

    cur.execute(
        """
        SELECT sender, content, sent_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY sent_at ASC
        """,
        (conversation_id,),
    )
    messages = [dict(row) for row in cur.fetchall()]
    conn.close()

    return {
        "conversation": dict(conv),
        "messages": messages,
    }


def load_aviato_events(email: Optional[str]) -> Dict[str, Any]:
    """Load Aviato events for an email.

    Returns a dict with keys:
    - exists: whether the log file exists at all
    - events: list of matching events (may be empty)
    """
    info: Dict[str, Any] = {"exists": AVIATO_LOG.exists(), "events": []}
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
    # Slightly more forgiving: allow optional space before the colon
    m = re.search(r"\*\*Email:?\*\*\s*([^\s]+)", md)
    if m:
        return m.group(1).strip()
    return None


def _extract_header_block(md: str) -> List[str]:
    """Extract the human header we want to show from a CRM markdown file.

    This is intentionally conservative: it only pulls the top name line and key
    bold metadata lines, and stops once we hit the first horizontal rule.
    """
    header_lines: List[str] = []
    for line in md.splitlines():
        if line.strip() == "---":
            # Skip YAML frontmatter separators but stop once we pass the second one
            continue
        if line.startswith("# "):
            header_lines.append(line)
            continue
        if line.startswith("**Organization:") or line.startswith("**Role:") or line.startswith("**Email:") or line.startswith("**Status:") or line.startswith("**LinkedIn URL:") or line.startswith("**LinkedIn Conversation ID (Kondo):"):
            header_lines.append(line)
            continue
        if line.strip() == "---":
            break
    return header_lines


def summarize_intel(slug: str) -> None:
    md = load_crm_profile(slug)
    if md is None:
        return

    linkedin_meta = extract_linkedin_metadata(md)
    email = extract_primary_email(md)
    aviato_info = load_aviato_events(email)
    li_conv = query_linkedin_conversation(linkedin_meta.get("linkedin_conversation_id"))

    print("# Stakeholder Intelligence")
    print(f"Person ID: {slug}")
    print()

    print("## Sources")
    print("- CRM: Personal/Knowledge/CRM/individuals")
    print("- LinkedIn: Knowledge/linkedin/linkedin.db")
    print("- Aviato: N5/logs/aviato_usage.jsonl")
    print()

    print("## CRM Snapshot (header)")
    header_lines = _extract_header_block(md)
    print("\n".join(header_lines))
    print()

    print("## LinkedIn Intelligence (Kondo)")
    linkedin_url = linkedin_meta.get("linkedin_url")
    linkedin_convo_id = linkedin_meta.get("linkedin_conversation_id")

    if not linkedin_url and not linkedin_convo_id:
        print("- No LinkedIn metadata recorded in CRM profile.")
    elif linkedin_url and not linkedin_convo_id:
        print(f"- LinkedIn URL recorded, but no conversation ID yet: {linkedin_url}")
        print("- Kondo data will appear once a conversation ID is linked in CRM.")
    elif linkedin_convo_id and not li_conv:
        print(f"- LinkedIn conversation ID in CRM: {linkedin_convo_id}")
        print("- No matching conversation found in Kondo DB yet.")
    else:
        conv = li_conv["conversation"]
        print(f"- Name: {conv['participant_name']}")
        print(f"- Email (from LinkedIn/Kondo): {conv['participant_email']}")
        print(f"- Profile URL: {conv['linkedin_profile_url']}")
        print(f"- Status: {conv['status']}")
        print(f"- First message: {_fmt_ms(conv['first_message_at'])}")
        print(f"- Last message:  {_fmt_ms(conv['last_message_at'])} (last_from={conv['last_message_from']})")
        print(f"- Messages: {conv['message_count']}")
        print()
        print("### Sample Messages")
        for msg in li_conv["messages"][:5]:
            print(f"- [{_fmt_ms(msg['sent_at'])}] {msg['sender']}: {msg['content']}")

    print()
    print("## Aviato Enrichment Events")
    if not aviato_info["exists"]:
        print("- Aviato usage log not found yet; enrichment jobs may not have run.")
    elif not aviato_info["events"]:
        print(f"- Aviato log present, but no events found for {email!r}.")
    else:
        for ev in aviato_info["events"]:
            status = "found" if ev.get("person_found") else "not_found"
            ts = ev.get("timestamp")
            print(f"- {ts}: {status} (success={ev.get('success')})")


def find_people_for_meeting(meeting_id: str) -> List[str]:
    """Return CRM slugs whose markdown lists the given meeting_id in "**Meeting IDs:**"."""
    slugs: List[str] = []
    pattern = re.compile(r"\*\*Meeting IDs:\*\*\s*(.+)")

    for path in sorted(CRM_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = pattern.search(text)
        if not m:
            continue
        # Simple substring match within the Meeting IDs line
        if meeting_id in m.group(1):
            slugs.append(path.stem)
    return slugs


def main() -> None:
    parser = argparse.ArgumentParser(description="View consolidated stakeholder intelligence")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--person-id", help="CRM person_id / slug (e.g., lauren-salitan)")
    group.add_argument("--meeting-id", help="Calendar meeting ID as stored in CRM metadata")
    args = parser.parse_args()

    if args.person_id:
        summarize_intel(args.person_id)
    elif args.meeting_id:
        slugs = find_people_for_meeting(args.meeting_id)
        if not slugs:
            print(f"No CRM profiles found for meeting ID {args.meeting_id!r}.")
            return
        for slug in slugs:
            summarize_intel(slug)
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()








#!/usr/bin/env python3
"""
CC Outreach Processor
---------------------
Scans Gmail for CC'd emails with V-OS tags and updates CRM/lists accordingly.

Actions supported:
- [CRM]: Update last_contact_at in CRM
- [DONE]: Mark must-contact item as done
- [F-X]: Schedule follow-up in X days

Usage:
    python3 cc_outreach_processor.py [--dry-run] [--since HOURS]
"""

import argparse
import json
import logging
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from vos_tag_parser import parse_vos_tags, VOSParseResult

import sys
sys.path.insert(0, "/home/workspace")

from N5.lib.paths import N5_DATA_DIR

# Unified database connection
try:
    from N5.scripts.db_paths import get_db_connection, N5_CORE_DB
except ImportError:
    N5_CORE_DB = N5_DATA_DIR / "n5_core.db"
    def get_db_connection(readonly=False):
        import sqlite3
        conn = sqlite3.connect(N5_CORE_DB)
        conn.row_factory = sqlite3.Row
        return conn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths - use centralized paths
STATE_FILE = N5_DATA_DIR / "cc_processor_state.json"


@dataclass
class OutreachEmail:
    """Parsed outreach email with V-OS tags."""
    message_id: str
    date: datetime
    sender: str
    recipients: list[str]
    subject: str
    vos_result: VOSParseResult
    raw_body: str = ""


def load_state() -> dict:
    """Load processor state (last run timestamp)."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_processed_at": None, "processed_ids": []}


def save_state(state: dict):
    """Save processor state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def fetch_cc_emails(since_hours: int = 24) -> list[dict]:
    """
    Fetch emails where V CC'd va@zo.computer.
    
    Uses zo CLI to query Gmail.
    """
    since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%Y/%m/%d")
    query = f"from:me cc:va@zo.computer after:{since_date}"
    
    logger.info(f"Searching Gmail: {query}")
    
    # Use zo CLI for Gmail access
    try:
        result = subprocess.run(
            ["zo", "gmail", "search", "--query", query, "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    
    # Fallback: return empty (agent will use use_app_gmail directly)
    logger.warning("zo CLI not available, returning empty - agent should use Gmail tool directly")
    return []


def extract_recipients(email_data: dict) -> list[str]:
    """Extract TO recipients from email."""
    to_field = email_data.get("recipient", email_data.get("to", ""))
    if isinstance(to_field, list):
        return [e.strip() for e in to_field]
    return [e.strip() for e in to_field.split(",") if e.strip()]


def find_crm_profile_by_email(email: str) -> Optional[dict]:
    """Look up CRM profile by email address in unified database."""
    if not N5_CORE_DB.exists():
        return None
    
    conn = get_db_connection(readonly=True)
    cursor = conn.cursor()
    
    # Search in email field
    cursor.execute("""
        SELECT id, full_name as name, email, category, last_contact_date as last_contact_at
        FROM people
        WHERE email LIKE ? OR email LIKE ?
    """, (f"%{email}%", f"%{email.lower()}%"))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def update_crm_last_contact(profile_id: str, contact_date: datetime, dry_run: bool = False) -> bool:
    """Update last_contact_date in unified database."""
    if dry_run:
        logger.info(f"[DRY RUN] Would update CRM profile {profile_id} last_contact_date = {contact_date}")
        return True
    
    conn = get_db_connection(readonly=False)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE people 
        SET last_contact_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (contact_date.strftime("%Y-%m-%d"), profile_id))
    conn.commit()
    conn.close()
    
    logger.info(f"Updated CRM profile {profile_id} last_contact_date = {contact_date}")
    return True


def mark_must_contact_done(email: str, dry_run: bool = False) -> bool:
    """Mark must-contact item as done if it matches the recipient email."""
    if not MUST_CONTACT_LIST.exists():
        return False
    
    items = []
    updated = False
    
    with open(MUST_CONTACT_LIST) as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                # Check if this item mentions the email
                title = item.get("title", "").lower()
                body = item.get("body", "").lower()
                if email.lower() in title or email.lower() in body:
                    if item.get("status") != "done":
                        if dry_run:
                            logger.info(f"[DRY RUN] Would mark must-contact '{item.get('title')}' as done")
                        else:
                            item["status"] = "done"
                            item["completed_at"] = datetime.now().isoformat()
                            logger.info(f"Marked must-contact '{item.get('title')}' as done")
                        updated = True
                items.append(item)
    
    if updated and not dry_run:
        with open(MUST_CONTACT_LIST, "w") as f:
            for item in items:
                f.write(json.dumps(item) + "\n")
    
    return updated


def process_outreach_email(email_data: dict, dry_run: bool = False) -> dict:
    """
    Process a single CC'd email.
    
    Returns dict with actions taken.
    """
    actions = {"crm_updates": [], "list_updates": [], "follow_ups": []}
    
    body = email_data.get("payload", email_data.get("body", ""))
    vos_result = parse_vos_tags(body)
    
    if not vos_result.zo_triggered():
        logger.debug(f"No Zo trigger in email: {email_data.get('subject', 'Unknown')}")
        return actions
    
    recipients = extract_recipients(email_data)
    email_date = datetime.fromisoformat(email_data.get("date", "").replace("Z", "+00:00"))
    
    logger.info(f"Processing: {email_data.get('subject')} -> {recipients}")
    logger.info(f"  Zo tags: {vos_result.zo.tags}")
    
    for recipient_email in recipients:
        # Skip self and zo
        if "zo.computer" in recipient_email or "attawar" in recipient_email:
            continue
        
        # [CRM] - Update CRM contact
        if vos_result.has_tag("CRM"):
            profile = find_crm_profile_by_email(recipient_email)
            if profile:
                update_crm_last_contact(profile["id"], email_date, dry_run)
                actions["crm_updates"].append({
                    "profile_id": profile["id"],
                    "name": profile["name"],
                    "email": recipient_email,
                    "date": email_date.isoformat()
                })
        
        # [DONE] - Mark list item done
        if vos_result.has_tag("DONE"):
            if mark_must_contact_done(recipient_email, dry_run):
                actions["list_updates"].append({
                    "email": recipient_email,
                    "action": "marked_done"
                })
        
        # [F-X] - Log follow-up (actual scheduling handled separately)
        follow_up_days = vos_result.get_follow_up_days()
        if follow_up_days:
            follow_up_date = email_date + timedelta(days=follow_up_days)
            actions["follow_ups"].append({
                "email": recipient_email,
                "days": follow_up_days,
                "due_date": follow_up_date.isoformat()
            })
            logger.info(f"  Follow-up scheduled: {recipient_email} in {follow_up_days} days")
    
    return actions


def run_processor(since_hours: int = 24, dry_run: bool = False) -> dict:
    """
    Main processor entry point.
    
    Returns summary of actions taken.
    """
    state = load_state()
    summary = {
        "processed": 0,
        "crm_updates": 0,
        "list_updates": 0,
        "follow_ups": 0,
        "errors": []
    }
    
    emails = fetch_cc_emails(since_hours)
    
    if not emails:
        logger.info("No CC'd emails found (or using agent mode)")
        return summary
    
    processed_ids = set(state.get("processed_ids", []))
    
    for email_data in emails:
        msg_id = email_data.get("id", email_data.get("message_id"))
        
        if msg_id in processed_ids:
            logger.debug(f"Skipping already processed: {msg_id}")
            continue
        
        try:
            actions = process_outreach_email(email_data, dry_run)
            summary["processed"] += 1
            summary["crm_updates"] += len(actions["crm_updates"])
            summary["list_updates"] += len(actions["list_updates"])
            summary["follow_ups"] += len(actions["follow_ups"])
            
            if not dry_run:
                processed_ids.add(msg_id)
        except Exception as e:
            logger.error(f"Error processing {msg_id}: {e}")
            summary["errors"].append(str(e))
    
    # Save state
    if not dry_run:
        state["last_processed_at"] = datetime.now().isoformat()
        state["processed_ids"] = list(processed_ids)[-1000:]  # Keep last 1000
        save_state(state)
    
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CC'd outreach emails")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes")
    parser.add_argument("--since", type=int, default=24, help="Hours to look back")
    args = parser.parse_args()
    
    summary = run_processor(since_hours=args.since, dry_run=args.dry_run)
    
    print(f"\n{'='*50}")
    print("CC Outreach Processor Summary")
    print(f"{'='*50}")
    print(f"Emails processed: {summary['processed']}")
    print(f"CRM updates: {summary['crm_updates']}")
    print(f"List items marked done: {summary['list_updates']}")
    print(f"Follow-ups logged: {summary['follow_ups']}")
    if summary['errors']:
        print(f"Errors: {len(summary['errors'])}")



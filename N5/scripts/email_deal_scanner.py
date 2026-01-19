#!/usr/bin/env python3
"""
Email Deal Scanner — Worker 5

Scans Gmail for deal-related emails and extracts intelligence.
Designed to be called by Zo (agentic execution) - prepares queries
and processes results through DealSignalRouter.

Usage (CLI for testing):
  python3 email_deal_scanner.py --days 7 --dry-run
  python3 email_deal_scanner.py --scan-contacts --dry-run
  python3 email_deal_scanner.py --query "from:specific@email.com" --dry-run
  
Backfill Usage:
  python3 email_deal_scanner.py --days 30 --offset 0    # Last 30 days
  python3 email_deal_scanner.py --days 30 --offset 30   # 30-60 days ago
  python3 email_deal_scanner.py --days 30 --offset 60   # 60-90 days ago
  python3 email_deal_scanner.py backfill --check        # Check backfill progress
  python3 email_deal_scanner.py backfill --advance      # Advance backfill window

Agentic Usage:
  1. Zo calls get_search_queries() to build Gmail queries
  2. Zo executes Gmail searches via use_app_gmail
  3. Zo calls process_email_results() with search results
  4. Results fed through DealSignalRouter
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure we can import from same directory
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from deal_signal_router import DealSignalRouter

DB_PATH = "/home/workspace/N5/data/deals.db"
BACKFILL_STATE_FILE = "/home/workspace/N5/data/backfill_state.json"
BACKFILL_DEFAULT_MAX_OFFSET = 60  # 2 months


@dataclass
class SearchQuery:
    """A Gmail search query with context."""
    query: str
    context_type: str  # 'contact', 'deal', 'company'
    context_id: Optional[str]
    context_name: str
    pipeline: Optional[str]


@dataclass
class EmailResult:
    """Parsed email result from Gmail API."""
    message_id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    date: str
    body_preview: Optional[str] = None


@dataclass
class ScanResult:
    """Result of processing a single email."""
    email: EmailResult
    matched: bool
    deal_id: Optional[str]
    contact_id: Optional[str]
    signal_extracted: bool
    extraction_summary: Optional[str]


def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_deal_contacts() -> Tuple[List[dict], List[dict]]:
    """Get all contacts and deals from database for matching."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get contacts with emails
    c.execute("""
        SELECT id, full_name, company, contact_type, pipeline, email,
               associated_deal_id, temperature
        FROM deal_contacts
        WHERE full_name IS NOT NULL
    """)
    contacts = [dict(r) for r in c.fetchall()]
    
    # Get deals
    c.execute("""
        SELECT id, company, primary_contact, pipeline, temperature, stage
        FROM deals
        WHERE company IS NOT NULL
    """)
    deals = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return contacts, deals


# =============================================================================
# Broad Query + Pre-filter Functions (W1.1)
# =============================================================================

EXCLUDE_SENDER_PATTERNS = [
    r'@linkedin\.com', r'@facebookmail\.com', r'notify\.', 
    r'noreply@', r'no-reply@', r'mailer-daemon', r'postmaster@',
    r'@github\.com', r'@notifications\.', r'digest@', r'newsletter@',
    r'@mail\.asana\.com', r'@slack\.com'
]

EXCLUDE_SUBJECT_PATTERNS = [
    r'weekly digest', r'daily digest', r'unsubscribe', 
    r'reset password', r'verify your email', r'your .* receipt',
    r'invitation to edit', r'shared .* with you', r'commented on',
    r'assigned to you', r'mentioned you'
]


def get_broad_email_queries(days: int, offset: int = 0) -> List[dict]:
    """Generate broad Gmail queries for semantic analysis.
    
    Args:
        days: Number of days in the search window
        offset: Days to skip from today (for backfill)
    
    Returns:
        List of query dicts with 'query' and 'description' keys.
    """
    end_date = datetime.now() - timedelta(days=offset)
    start_date = end_date - timedelta(days=days)
    
    date_filter = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
    
    return [
        {
            "query": f"-category:promotions -category:social -category:updates {date_filter}",
            "description": f"All non-promotional emails from {start_date.date()} to {end_date.date()}"
        }
    ]


def should_analyze_email(email: dict) -> Tuple[bool, str]:
    """Pre-filter to exclude obvious noise.
    
    Args:
        email: Dict with 'from' and 'subject' keys
    
    Returns:
        Tuple of (should_analyze, skip_reason)
    """
    sender = email.get('from', '').lower()
    subject = email.get('subject', '').lower()
    
    for pattern in EXCLUDE_SENDER_PATTERNS:
        if re.search(pattern, sender, re.IGNORECASE):
            return False, f"Excluded sender pattern: {pattern}"
    
    for pattern in EXCLUDE_SUBJECT_PATTERNS:
        if re.search(pattern, subject, re.IGNORECASE):
            return False, f"Excluded subject pattern: {pattern}"
    
    return True, ""


def build_llm_context() -> str:
    """Build deal/contact context string for LLM prompt.
    
    Returns:
        Formatted string with known contacts and active deals.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get contacts (limit to avoid context overflow)
    c.execute("""
        SELECT id, full_name, email, company, pipeline 
        FROM deal_contacts 
        WHERE full_name IS NOT NULL
        ORDER BY 
            CASE WHEN email IS NOT NULL AND email != '' THEN 0 ELSE 1 END,
            updated_at DESC
        LIMIT 50
    """)
    contacts = [dict(r) for r in c.fetchall()]
    
    # Get deals
    c.execute("""
        SELECT id, company, primary_contact, pipeline, stage 
        FROM deals 
        WHERE company IS NOT NULL
        ORDER BY last_touched DESC
        LIMIT 30
    """)
    deals = [dict(r) for r in c.fetchall()]
    
    conn.close()
    
    context = "## Known Contacts:\n"
    for contact in contacts:
        email_str = f" <{contact['email']}>" if contact.get('email') else " (no email)"
        company_str = f" @ {contact['company']}" if contact.get('company') else ""
        context += f"- {contact['full_name']}{email_str}{company_str} [id: {contact['id']}]\n"
    
    context += "\n## Active Deals:\n"
    for deal in deals:
        contact_str = f" (contact: {deal['primary_contact']})" if deal.get('primary_contact') else ""
        context += f"- {deal['company']} [{deal['pipeline']}/{deal['stage']}]{contact_str} [id: {deal['id']}]\n"
    
    return context


def update_contact_email(contact_id: str, email: str, dry_run: bool = False) -> dict:
    """Update a contact's email if currently empty.
    
    Returns dict with status and details.
    """
    if not contact_id or not email:
        return {"updated": False, "reason": "Missing contact_id or email"}
    
    if dry_run:
        return {"updated": True, "dry_run": True, "contact_id": contact_id, "email": email}
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check current state
    c.execute("SELECT email FROM deal_contacts WHERE id = ?", (contact_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return {"updated": False, "reason": f"Contact {contact_id} not found"}
    
    current_email = row['email']
    if current_email and current_email.strip():
        conn.close()
        return {"updated": False, "reason": f"Contact already has email: {current_email}"}
    
    # Update
    c.execute("""
        UPDATE deal_contacts 
        SET email = ?, updated_at = ?
        WHERE id = ?
    """, (email, datetime.now().isoformat(), contact_id))
    
    conn.commit()
    conn.close()
    
    return {"updated": True, "contact_id": contact_id, "email": email}


def format_email_for_llm(email: dict, context: str) -> str:
    """Format an email + context into the analysis prompt.
    
    Args:
        email: Gmail email dict with 'from', 'subject', 'date', 'snippet'
        context: Pre-built context string from build_llm_context()
    
    Returns:
        Formatted prompt string ready for LLM
    """
    # Import here to avoid circular imports at module load
    from deal_llm_prompts import EMAIL_ANALYSIS_PROMPT
    
    return EMAIL_ANALYSIS_PROMPT.format(
        sender=email.get('from', 'Unknown sender'),
        subject=email.get('subject', '(no subject)'),
        date=email.get('date', 'Unknown date'),
        snippet=email.get('snippet', ''),
        context=context
    )


def process_email_with_llm_analysis(
    email: dict,
    analysis: dict,
    dry_run: bool = False
) -> dict:
    """Process an email using LLM analysis results.
    
    This function takes pre-computed LLM analysis (since Zo IS the LLM)
    and performs the appropriate actions:
    - Enriches contact email if discovered
    - Routes signals through DealSignalRouter
    - Marks email as processed
    
    Args:
        email: Gmail email dict (id, from, subject, snippet, date)
        analysis: LLM analysis result dict with:
            - matched_contact_id
            - matched_deal_id
            - discovered_email
            - signal_strength (none/weak/medium/strong)
            - intel (dict with stage_signal, key_facts, etc.)
            - match_reasoning
        dry_run: If True, don't write to database
    
    Returns:
        dict with processing results and actions taken
    """
    result = {
        "message_id": email.get('id'),
        "sender": email.get('from'),
        "subject": email.get('subject'),
        "signal_strength": analysis.get('signal_strength', 'none'),
        "matched_contact_id": analysis.get('matched_contact_id'),
        "matched_deal_id": analysis.get('matched_deal_id'),
        "actions_taken": [],
        "dry_run": dry_run
    }
    
    # Contact email enrichment
    discovered_email = analysis.get('discovered_email')
    contact_id = analysis.get('matched_contact_id')
    
    if discovered_email and contact_id:
        enrich_result = update_contact_email(contact_id, discovered_email, dry_run=dry_run)
        if enrich_result.get('updated'):
            result['actions_taken'].append(f"Enriched contact {contact_id} with email: {discovered_email}")
    
    # Signal routing
    signal_strength = analysis.get('signal_strength', 'none')
    intel = analysis.get('intel')
    
    if signal_strength in ('medium', 'strong') and intel:
        deal_id = analysis.get('matched_deal_id')
        
        if deal_id and not dry_run:
            # Route through existing DealSignalRouter
            router = DealSignalRouter()
            
            # Build content summary for router
            content = f"Email from {email.get('from')}\nSubject: {email.get('subject')}\n\n{email.get('snippet')}"
            
            route_result = router.process_signal(
                source="email_scan",
                content=content,
                metadata={
                    "message_id": email.get('id'),
                    "sender": email.get('from'),
                    "subject": email.get('subject'),
                    "llm_intel": intel
                },
                context=deal_id,
                dry_run=dry_run
            )
            
            result['actions_taken'].append(f"Routed to deal {deal_id}: {route_result.action_taken}")
    
    # Mark as processed (skip if dry_run)
    if not dry_run:
        mark_email_processed(
            message_id=email.get('id', ''),
            thread_id=email.get('threadId', ''),
            deal_id=analysis.get('matched_deal_id'),
            contact_id=analysis.get('matched_contact_id'),
            subject=email.get('subject', ''),
            sender=email.get('from', ''),
            signal_extracted=signal_strength in ('medium', 'strong'),
            extraction_summary=analysis.get('match_reasoning')
        )
        result['actions_taken'].append("Marked as processed")
    
    return result


def build_search_queries(
    days: int = 7,
    max_queries: int = 30,
    priority: str = "hot",
    offset: int = 0
) -> List[SearchQuery]:
    """
    Build Gmail search queries based on known contacts and deals.
    
    Args:
        days: Number of days in the search window
        max_queries: Maximum number of queries to generate
        priority: Filter by temperature ('hot', 'warm', 'all')
        offset: Days to skip from today (for backfill)
    
    Returns:
        List of SearchQuery objects ready for Gmail API
    """
    contacts, deals = get_deal_contacts()
    
    # Calculate date range with offset
    end_date = datetime.now() - timedelta(days=offset)
    start_date = end_date - timedelta(days=days)
    after_date = start_date.strftime("%Y/%m/%d")
    before_date = end_date.strftime("%Y/%m/%d")
    
    date_filter = f"after:{after_date}"
    if offset > 0:
        date_filter += f" before:{before_date}"
    
    queries: List[SearchQuery] = []
    
    # Priority 1: Contacts with known emails
    contacts_with_email = [c for c in contacts if c.get("email")]
    if priority == "hot":
        contacts_with_email = [c for c in contacts_with_email if c.get("temperature") == "hot"]
    elif priority == "warm":
        contacts_with_email = [c for c in contacts_with_email if c.get("temperature") in ("hot", "warm")]
    
    for c in contacts_with_email[:max_queries // 3]:
        email = c["email"]
        queries.append(SearchQuery(
            query=f"(from:{email} OR to:{email}) {date_filter}",
            context_type="contact",
            context_id=c["id"],
            context_name=c["full_name"],
            pipeline=c.get("pipeline")
        ))
    
    # Priority 2: Hot deals by company name
    hot_deals = [d for d in deals if d.get("temperature") == "hot"]
    for d in hot_deals[:max_queries // 3]:
        company = d["company"]
        company_query = f'"{company}"' if " " in company else company
        queries.append(SearchQuery(
            query=f"{company_query} {date_filter}",
            context_type="deal",
            context_id=d["id"],
            context_name=company,
            pipeline=d.get("pipeline")
        ))
    
    # Priority 3: Contacts by name (fuzzy)
    remaining_slots = max_queries - len(queries)
    contacts_by_name = [c for c in contacts if not c.get("email") and c.get("full_name")]
    for c in contacts_by_name[:remaining_slots]:
        name = c["full_name"]
        if len(name.split()) >= 2:
            queries.append(SearchQuery(
                query=f'"{name}" {date_filter}',
                context_type="contact",
                context_id=c["id"],
                context_name=name,
                pipeline=c.get("pipeline")
            ))
    
    return queries[:max_queries]


def is_email_processed(message_id: str) -> bool:
    """Check if an email has already been processed."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed_emails WHERE message_id = ?", (message_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


def mark_email_processed(
    message_id: str,
    thread_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    subject: Optional[str] = None,
    sender: Optional[str] = None,
    signal_extracted: bool = False,
    extraction_summary: Optional[str] = None
) -> None:
    """Mark an email as processed in the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO processed_emails 
        (message_id, thread_id, deal_id, contact_id, subject, sender, 
         processed_at, signal_extracted, extraction_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message_id, thread_id, deal_id, contact_id, subject, sender,
        datetime.now().isoformat(), signal_extracted, extraction_summary
    ))
    conn.commit()
    conn.close()


def process_email(
    email: EmailResult,
    search_context: Optional[SearchQuery] = None,
    dry_run: bool = False
) -> ScanResult:
    """
    Process a single email through the signal router.
    
    Args:
        email: Parsed email result
        search_context: Original search query context (helps with matching)
        dry_run: If True, don't write to database
    
    Returns:
        ScanResult with processing outcome
    """
    # Check if already processed
    if is_email_processed(email.message_id):
        return ScanResult(
            email=email,
            matched=False,
            deal_id=None,
            contact_id=None,
            signal_extracted=False,
            extraction_summary="Already processed"
        )
    
    # Build content for signal router
    content = f"Email from {email.sender}\nSubject: {email.subject}\n\n{email.snippet}"
    if email.body_preview:
        content += f"\n\n{email.body_preview}"
    
    # Determine context for matching
    context = ""
    if search_context:
        context = search_context.pipeline or ""
    
    # Route through signal router
    router = DealSignalRouter()
    result = router.process_signal(
        source="email",
        content=content,
        metadata={
            "message_id": email.message_id,
            "thread_id": email.thread_id,
            "sender": email.sender,
            "subject": email.subject,
            "date": email.date
        },
        context=context,
        dry_run=dry_run
    )
    
    # Build extraction summary
    extraction_summary = None
    if result.extraction:
        ext = result.extraction
        parts = []
        if ext.stage_signal != "none":
            parts.append(f"Stage: {ext.stage_signal}")
        if ext.inferred_stage:
            parts.append(f"→ {ext.inferred_stage}")
        if ext.key_facts:
            parts.append(f"Facts: {len(ext.key_facts)}")
        if ext.next_action:
            parts.append(f"Action: {ext.next_action[:50]}")
        extraction_summary = " | ".join(parts) if parts else None
    
    # Mark as processed
    if not dry_run:
        mark_email_processed(
            message_id=email.message_id,
            thread_id=email.thread_id,
            deal_id=result.deal_id,
            contact_id=None,  # Could extract from search_context
            subject=email.subject,
            sender=email.sender,
            signal_extracted=result.matched,
            extraction_summary=extraction_summary
        )
    
    return ScanResult(
        email=email,
        matched=result.matched,
        deal_id=result.deal_id,
        contact_id=search_context.context_id if search_context and search_context.context_type == "contact" else None,
        signal_extracted=result.extraction is not None,
        extraction_summary=extraction_summary
    )


def parse_gmail_response(gmail_response: dict) -> List[EmailResult]:
    """
    Parse Gmail API response into EmailResult objects.
    
    The Gmail API returns messages in a specific format. This function
    normalizes that into our EmailResult dataclass.
    """
    results: List[EmailResult] = []
    
    messages = gmail_response.get("messages", [])
    if not messages:
        return results
    
    for msg in messages:
        # Handle both full message format and metadata-only format
        headers = {}
        for header in msg.get("payload", {}).get("headers", []):
            headers[header["name"].lower()] = header["value"]
        
        results.append(EmailResult(
            message_id=msg.get("id", ""),
            thread_id=msg.get("threadId", ""),
            subject=headers.get("subject", "(no subject)"),
            sender=headers.get("from", "unknown"),
            snippet=msg.get("snippet", ""),
            date=headers.get("date", ""),
            body_preview=msg.get("textPayload")  # If withTextPayload=true
        ))
    
    return results


def get_scan_stats() -> dict:
    """Get statistics about processed emails."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM processed_emails")
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM processed_emails WHERE signal_extracted = 1")
    with_signals = c.fetchone()[0]
    
    c.execute("""
        SELECT COUNT(DISTINCT deal_id) FROM processed_emails 
        WHERE deal_id IS NOT NULL
    """)
    unique_deals = c.fetchone()[0]
    
    c.execute("""
        SELECT date(processed_at) as day, COUNT(*) as count
        FROM processed_emails
        GROUP BY date(processed_at)
        ORDER BY day DESC
        LIMIT 7
    """)
    daily = [{"date": r[0], "count": r[1]} for r in c.fetchall()]
    
    conn.close()
    
    return {
        "total_processed": total,
        "with_signals": with_signals,
        "unique_deals": unique_deals,
        "daily_counts": daily
    }


def get_backfill_state() -> dict:
    """Get current backfill state from file."""
    if not Path(BACKFILL_STATE_FILE).exists():
        return {
            "status": "not_started",
            "current_offset": 0,
            "max_offset": BACKFILL_DEFAULT_MAX_OFFSET,
            "window_days": 30,
            "runs_completed": 0,
            "total_runs_needed": 2,
            "emails_processed": 0,
            "signals_found": 0,
            "started_at": None,
            "last_run_at": None,
            "completed_at": None
        }
    return json.loads(Path(BACKFILL_STATE_FILE).read_text())


def save_backfill_state(state: dict) -> None:
    """Save backfill state to file."""
    Path(BACKFILL_STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(BACKFILL_STATE_FILE).write_text(json.dumps(state, indent=2))


def advance_backfill(emails_processed: int = 0, signals_found: int = 0) -> dict:
    """Advance backfill to next window, return updated state."""
    state = get_backfill_state()
    
    if state["status"] == "not_started":
        state["status"] = "in_progress"
        state["started_at"] = datetime.now().isoformat()
    
    state["current_offset"] += state["window_days"]
    state["runs_completed"] += 1
    state["emails_processed"] += emails_processed
    state["signals_found"] += signals_found
    state["last_run_at"] = datetime.now().isoformat()
    
    # Check if complete
    if state["current_offset"] >= state["max_offset"]:
        state["status"] = "complete"
        state["completed_at"] = datetime.now().isoformat()
    
    save_backfill_state(state)
    return state


def reset_backfill(max_offset: int = BACKFILL_DEFAULT_MAX_OFFSET) -> dict:
    """Reset backfill state for a new run."""
    state = {
        "status": "not_started",
        "current_offset": 0,
        "max_offset": max_offset,
        "window_days": 30,
        "runs_completed": 0,
        "total_runs_needed": (max_offset + 29) // 30,  # Ceiling division
        "emails_processed": 0,
        "signals_found": 0,
        "started_at": None,
        "last_run_at": None,
        "completed_at": None
    }
    save_backfill_state(state)
    return state


def cmd_backfill(args):
    """Handle backfill subcommand."""
    state = get_backfill_state()
    
    if args.reset:
        max_off = args.max_offset if args.max_offset else BACKFILL_DEFAULT_MAX_OFFSET
        state = reset_backfill(max_offset=max_off)
        print(f"✓ Backfill reset. Target: {max_off} days ({state['total_runs_needed']} runs)")
        return
    
    if args.complete:
        # Exit code 0 if complete, 1 if not - for agent self-destruct check
        if state["status"] == "complete":
            print("✓ Backfill complete")
            sys.exit(0)
        else:
            pct = (state["runs_completed"] / max(state["total_runs_needed"], 1)) * 100
            print(f"⏳ Backfill in progress: {pct:.0f}% ({state['runs_completed']}/{state['total_runs_needed']} runs)")
            sys.exit(1)
    
    if args.check:
        # Human-readable status
        if state["status"] == "not_started":
            print(f"Backfill Status: not_started")
            print(f"Target: {state['max_offset']} days ({state['total_runs_needed']} runs needed)")
        elif state["status"] == "complete":
            print(f"✅ Backfill COMPLETE")
            print(f"Runs: {state['runs_completed']}")
            print(f"Emails processed: {state['emails_processed']}")
            print(f"Signals found: {state['signals_found']}")
            print(f"Completed: {state['completed_at']}")
        else:
            pct = (state["runs_completed"] / max(state["total_runs_needed"], 1)) * 100
            window_start = state["current_offset"]
            window_end = window_start + state["window_days"]
            print(f"Backfill Status: {state['status']}")
            print(f"Progress: {pct:.0f}% ({state['runs_completed']}/{state['total_runs_needed']} runs)")
            print(f"Next window: {window_start}-{window_end} days ago")
            print(f"Emails processed: {state['emails_processed']}")
            print(f"Signals found: {state['signals_found']}")
        
        if args.json:
            print(json.dumps(state, indent=2))
        return
    
    if args.advance:
        # Used by agent after successful scan
        emails = args.emails_processed if args.emails_processed else 0
        signals = args.signals_found if args.signals_found else 0
        state = advance_backfill(emails_processed=emails, signals_found=signals)
        
        if state["status"] == "complete":
            print(f"🎉 BACKFILL COMPLETE!")
            print(f"Total runs: {state['runs_completed']}")
            print(f"Total emails: {state['emails_processed']}")
            print(f"Total signals: {state['signals_found']}")
        else:
            pct = (state["runs_completed"] / max(state["total_runs_needed"], 1)) * 100
            print(f"✓ Advanced to next window")
            print(f"Progress: {pct:.0f}% ({state['runs_completed']}/{state['total_runs_needed']})")
            print(f"Next offset: {state['current_offset']} days")
        return
    
    # Default: show status
    cmd_backfill_check(state, args.json if hasattr(args, 'json') else False)


def cmd_backfill_check(state: dict, as_json: bool = False):
    """Display backfill status."""
    if as_json:
        print(json.dumps(state, indent=2))
    else:
        if state["status"] == "not_started":
            print(f"Backfill: not started (target: {state['max_offset']} days)")
        elif state["status"] == "complete":
            print(f"✅ Backfill complete ({state['runs_completed']} runs, {state['emails_processed']} emails)")
        else:
            pct = (state["runs_completed"] / max(state["total_runs_needed"], 1)) * 100
            print(f"Backfill: {pct:.0f}% ({state['runs_completed']}/{state['total_runs_needed']})")


# ============================================================
# CLI Interface
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Email Deal Scanner - Scan Gmail for deal signals"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Backfill subcommand
    bp = subparsers.add_parser("backfill", help="Manage email backfill state")
    bp.add_argument("--check", action="store_true", help="Show backfill status")
    bp.add_argument("--complete", action="store_true", help="Check if complete (exit 0 if done, 1 if not)")
    bp.add_argument("--advance", action="store_true", help="Advance to next window after scan")
    bp.add_argument("--reset", action="store_true", help="Reset backfill state")
    bp.add_argument("--max-offset", type=int, help=f"Max days to backfill (default: {BACKFILL_DEFAULT_MAX_OFFSET})")
    bp.add_argument("--emails-processed", type=int, help="Emails processed in last run (for --advance)")
    bp.add_argument("--signals-found", type=int, help="Signals found in last run (for --advance)")
    bp.add_argument("--json", action="store_true", help="Output as JSON")
    bp.set_defaults(func=cmd_backfill)
    
    # Main scan arguments
    parser.add_argument(
        "--days", type=int, default=7,
        help="Number of days in search window (default: 7)"
    )
    parser.add_argument(
        "--offset", type=int, default=0,
        help="Days to skip from today for backfill (default: 0)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Max emails to process per run (default: 50)"
    )
    parser.add_argument(
        "--max-queries", type=int, default=20,
        help="Maximum number of search queries to generate (default: 20)"
    )
    parser.add_argument(
        "--priority", choices=["hot", "warm", "all"], default="hot",
        help="Filter contacts/deals by temperature (default: hot)"
    )
    parser.add_argument(
        "--scan-contacts", action="store_true",
        help="Generate queries for contacts (default mode)"
    )
    parser.add_argument(
        "--query", type=str,
        help="Custom Gmail search query"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Show scan statistics"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Don't write to database"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    if args.command == "backfill":
        args.func(args)
        return
    
    if args.stats:
        stats = get_scan_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Total processed: {stats['total_processed']}")
            print(f"With signals: {stats['with_signals']}")
            print(f"Unique deals: {stats['unique_deals']}")
            print("\nDaily counts (last 7 days):")
            for day in stats['daily_counts']:
                print(f"  {day['date']}: {day['count']}")
        return
    
    # Generate search queries
    queries = build_search_queries(
        days=args.days,
        max_queries=args.max_queries,
        priority=args.priority,
        offset=args.offset
    )
    
    if args.query:
        queries.insert(0, SearchQuery(
            query=args.query,
            context_type="custom",
            context_id=None,
            context_name="Custom query",
            pipeline=None
        ))
    
    # Calculate date range for display
    end_date = datetime.now() - timedelta(days=args.offset)
    start_date = end_date - timedelta(days=args.days)
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    output = {
        "mode": "query_generation",
        "dry_run": args.dry_run,
        "days": args.days,
        "offset": args.offset,
        "date_range": date_range,
        "batch_size": args.batch_size,
        "queries": [asdict(q) for q in queries],
        "instructions": f"""
To execute these queries, Zo should:
1. For each query, call: use_app_gmail(
     tool_name="gmail-find-email",
     configured_props={{"q": query["query"], "maxResults": {args.batch_size // len(queries) if queries else 10}}}
   )
2. Parse results using email_deal_scanner.parse_gmail_response()
3. Process each email using email_deal_scanner.process_email()
4. Report summary of signals found
5. Total batch limit: {args.batch_size} emails
        """
    }
    
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Generated {len(queries)} search queries for Gmail")
        print(f"Date range: {date_range} (offset: {args.offset} days)")
        print(f"Batch size: {args.batch_size}")
        print("\nQueries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. [{q.context_type}] {q.context_name}")
            print(f"     Query: {q.query}")
        print("\n" + output["instructions"])


if __name__ == "__main__":
    main()

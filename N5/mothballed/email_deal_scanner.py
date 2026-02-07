#!/usr/bin/env python3
"""
Email Deal Scanner — Worker 5

Updated 2026-01-19: Now uses unified n5_core.db database with people table.

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
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure we can import from same directory
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection, N5_CORE_DB
from deal_signal_router import DealSignalRouter

BACKFILL_STATE_FILE = "/home/workspace/N5/data/backfill_state.json"
BACKFILL_DEFAULT_MAX_OFFSET = 60  # 2 months


@dataclass
class SearchQuery:
    """A Gmail search query with context."""
    query: str
    context_type: str  # 'person', 'deal', 'company'
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
    person_id: Optional[int]
    signal_extracted: bool
    extraction_summary: Optional[str]


def get_people_and_deals() -> Tuple[List[dict], List[dict]]:
    """Get all people and deals from database for matching.
    
    Uses unified n5_core.db with people table and deal_roles junction.
    """
    conn = get_db_connection(readonly=True)
    c = conn.cursor()
    
    # Get people with emails - include deal association via deal_roles
    c.execute("""
        SELECT DISTINCT
            p.id, p.full_name, p.company, p.category, p.email,
            dr.deal_id as associated_deal_id,
            d.pipeline, d.temperature
        FROM people p
        LEFT JOIN deal_roles dr ON dr.person_id = p.id
        LEFT JOIN deals d ON d.id = dr.deal_id
        WHERE p.full_name IS NOT NULL
    """)
    people = [dict(r) for r in c.fetchall()]
    
    # Get deals with primary contacts
    c.execute("""
        SELECT 
            d.id, d.company, d.pipeline, d.temperature, d.stage,
            p.full_name as primary_contact_name
        FROM deals d
        LEFT JOIN people p ON p.id = d.primary_contact_id
        WHERE d.company IS NOT NULL
    """)
    deals = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return people, deals


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
            'query': f'in:inbox is:unread {date_filter}',
            'description': 'Unread inbox emails',
        },
        {
            'query': f'in:inbox (subject:meeting OR subject:call OR subject:intro OR subject:connect) {date_filter}',
            'description': 'Meeting/connection related',
        },
        {
            'query': f'in:inbox (subject:follow OR subject:checking) {date_filter}',
            'description': 'Follow-ups and check-ins',
        },
    ]


def is_likely_signal_email(email: dict) -> bool:
    """Pre-filter emails to exclude obvious non-signals.
    
    Args:
        email: Dict with 'from', 'subject', 'snippet' keys
    
    Returns:
        True if email should be analyzed further
    """
    sender = email.get('from', '').lower()
    subject = email.get('subject', '').lower()
    
    # Check sender patterns
    for pattern in EXCLUDE_SENDER_PATTERNS:
        if re.search(pattern, sender):
            return False
    
    # Check subject patterns
    for pattern in EXCLUDE_SUBJECT_PATTERNS:
        if re.search(pattern, subject):
            return False
    
    return True


def get_search_queries(
    days: int = 7,
    max_queries: int = 20,
    priority: str = "all",
    offset: int = 0
) -> List[SearchQuery]:
    """Build Gmail search queries based on people and deals.
    
    Args:
        days: Number of days to search
        max_queries: Maximum number of queries to return
        priority: Filter by temperature ("hot", "warm", "all")
        offset: Days offset for backfill (0 = today, 30 = 30-60 days ago)
    
    Returns:
        List of SearchQuery objects ready for Gmail API
    """
    people, deals = get_people_and_deals()
    
    # Calculate date range with offset
    end_date = datetime.now() - timedelta(days=offset)
    start_date = end_date - timedelta(days=days)
    after_date = start_date.strftime("%Y/%m/%d")
    before_date = end_date.strftime("%Y/%m/%d")
    
    date_filter = f"after:{after_date}"
    if offset > 0:
        date_filter += f" before:{before_date}"
    
    queries: List[SearchQuery] = []
    
    # Priority 1: People with known emails
    people_with_email = [p for p in people if p.get("email")]
    if priority == "hot":
        people_with_email = [p for p in people_with_email if p.get("temperature") == "hot"]
    elif priority == "warm":
        people_with_email = [p for p in people_with_email if p.get("temperature") in ("hot", "warm")]
    
    for p in people_with_email[:max_queries // 3]:
        email = p["email"]
        queries.append(SearchQuery(
            query=f"(from:{email} OR to:{email}) {date_filter}",
            context_type="person",
            context_id=str(p["id"]),
            context_name=p["full_name"],
            pipeline=p.get("pipeline")
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
    
    # Priority 3: People by name (fuzzy)
    remaining_slots = max_queries - len(queries)
    people_by_name = [p for p in people if not p.get("email") and p.get("full_name")]
    for p in people_by_name[:remaining_slots]:
        name = p["full_name"]
        if len(name.split()) >= 2:
            queries.append(SearchQuery(
                query=f'"{name}" {date_filter}',
                context_type="person",
                context_id=str(p["id"]),
                context_name=name,
                pipeline=p.get("pipeline")
            ))
    
    return queries[:max_queries]


def is_email_processed(message_id: str) -> bool:
    """Check if an email has already been processed.
    
    Uses interactions table in unified DB.
    """
    conn = get_db_connection(readonly=True)
    c = conn.cursor()
    c.execute("SELECT 1 FROM interactions WHERE source_ref = ?", (f"email:{message_id}",))
    result = c.fetchone()
    conn.close()
    return result is not None


def mark_email_processed(
    message_id: str,
    thread_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    person_id: Optional[int] = None,
    subject: Optional[str] = None,
    sender: Optional[str] = None,
    signal_extracted: bool = False,
    extraction_summary: Optional[str] = None
) -> None:
    """Mark an email as processed by creating an interaction entry."""
    conn = get_db_connection()
    c = conn.cursor()
    
    summary = f"Email from {sender}: {subject}" if sender and subject else extraction_summary
    
    c.execute("""
        INSERT INTO interactions 
        (person_id, deal_id, type, direction, summary, source_ref, occurred_at, created_at)
        VALUES (?, ?, 'email', 'inbound', ?, ?, datetime('now'), datetime('now'))
    """, (person_id, deal_id, summary, f"email:{message_id}"))
    
    conn.commit()
    conn.close()


def ensure_person_exists(name: str, email: str = None, company: str = None) -> int:
    """Get or create person, return person_id."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Try to find by email first
    if email:
        c.execute("SELECT id FROM people WHERE email = ?", (email.lower(),))
        row = c.fetchone()
        if row:
            conn.close()
            return row['id']
    
    # Try by name + company
    c.execute("""
        SELECT id FROM people 
        WHERE full_name = ? AND (company = ? OR company IS NULL)
    """, (name, company))
    row = c.fetchone()
    if row:
        conn.close()
        return row['id']
    
    # Create new
    c.execute("""
        INSERT INTO people (full_name, email, company, source_db, created_at)
        VALUES (?, ?, ?, 'email_scanner', datetime('now'))
    """, (name, email.lower() if email else None, company))
    person_id = c.lastrowid
    conn.commit()
    conn.close()
    return person_id


def update_person_email(person_id: int, email: str, dry_run: bool = False) -> dict:
    """Update a person's email if they don't have one."""
    if dry_run:
        return {"updated": False, "dry_run": True, "person_id": person_id, "email": email}
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check current state
    c.execute("SELECT email FROM people WHERE id = ?", (person_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return {"updated": False, "reason": f"Person {person_id} not found"}
    
    current_email = row['email']
    if current_email and current_email.strip():
        conn.close()
        return {"updated": False, "reason": f"Person already has email: {current_email}"}
    
    # Update
    c.execute("""
        UPDATE people 
        SET email = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (email, person_id))
    
    conn.commit()
    conn.close()
    
    return {"updated": True, "person_id": person_id, "email": email}


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
            person_id=None,
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
    
    # Get person_id from search context if available
    person_id = None
    if search_context and search_context.context_type == "person":
        try:
            person_id = int(search_context.context_id)
        except (ValueError, TypeError):
            pass
    
    # Mark as processed (creates interaction entry)
    if not dry_run:
        mark_email_processed(
            message_id=email.message_id,
            thread_id=email.thread_id,
            deal_id=result.deal_id,
            person_id=person_id,
            subject=email.subject,
            sender=email.sender,
            signal_extracted=result.matched,
            extraction_summary=extraction_summary
        )
    
    return ScanResult(
        email=email,
        matched=result.matched,
        deal_id=result.deal_id,
        person_id=person_id,
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
        # Handle both full message format and list format
        if "payload" in msg:
            # Full message format
            headers = msg.get("payload", {}).get("headers", [])
            header_dict = {h["name"].lower(): h["value"] for h in headers}
            
            results.append(EmailResult(
                message_id=msg.get("id", ""),
                thread_id=msg.get("threadId", ""),
                subject=header_dict.get("subject", "(no subject)"),
                sender=header_dict.get("from", "Unknown"),
                snippet=msg.get("snippet", ""),
                date=header_dict.get("date", ""),
                body_preview=None  # Could extract from payload
            ))
        else:
            # List format (minimal)
            results.append(EmailResult(
                message_id=msg.get("id", ""),
                thread_id=msg.get("threadId", ""),
                subject=msg.get("subject", "(no subject)"),
                sender=msg.get("from", "Unknown"),
                snippet=msg.get("snippet", ""),
                date=msg.get("date", ""),
                body_preview=None
            ))
    
    return results


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


# =============================================================================
# Backfill Management
# =============================================================================

def get_backfill_state() -> dict:
    """Load backfill progress state."""
    try:
        with open(BACKFILL_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'current_offset': 0,
            'max_offset': BACKFILL_DEFAULT_MAX_OFFSET,
            'last_run': None,
            'emails_processed': 0
        }


def save_backfill_state(state: dict) -> None:
    """Save backfill progress state."""
    Path(BACKFILL_STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(BACKFILL_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def advance_backfill(days: int = 7) -> dict:
    """Advance backfill window by specified days."""
    state = get_backfill_state()
    
    old_offset = state['current_offset']
    new_offset = old_offset + days
    
    if new_offset >= state['max_offset']:
        return {
            'status': 'complete',
            'message': f'Backfill complete (reached {state["max_offset"]} days)'
        }
    
    state['current_offset'] = new_offset
    state['last_run'] = datetime.now().isoformat()
    save_backfill_state(state)
    
    return {
        'status': 'advanced',
        'old_offset': old_offset,
        'new_offset': new_offset,
        'remaining': state['max_offset'] - new_offset
    }


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Email Deal Scanner - scan Gmail for deal intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 email_deal_scanner.py --days 7 --dry-run
  python3 email_deal_scanner.py --scan-contacts --dry-run
  python3 email_deal_scanner.py backfill --check
"""
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Default scan command
    parser.add_argument('--days', type=int, default=7, help='Days to search')
    parser.add_argument('--offset', type=int, default=0, help='Days offset for backfill')
    parser.add_argument('--max-queries', type=int, default=20, help='Max queries to generate')
    parser.add_argument('--priority', choices=['hot', 'warm', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true', help='Preview without processing')
    parser.add_argument('--scan-contacts', action='store_true', help='Scan by contacts only')
    parser.add_argument('--query', help='Custom Gmail query')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Backfill subcommand
    backfill_parser = subparsers.add_parser('backfill', help='Manage backfill progress')
    backfill_parser.add_argument('--check', action='store_true', help='Check backfill status')
    backfill_parser.add_argument('--advance', action='store_true', help='Advance backfill window')
    backfill_parser.add_argument('--reset', action='store_true', help='Reset backfill progress')
    
    args = parser.parse_args()
    
    # Handle backfill subcommand
    if args.command == 'backfill':
        if args.check:
            state = get_backfill_state()
            print(json.dumps(state, indent=2))
        elif args.advance:
            result = advance_backfill()
            print(json.dumps(result, indent=2))
        elif args.reset:
            save_backfill_state({
                'current_offset': 0,
                'max_offset': BACKFILL_DEFAULT_MAX_OFFSET,
                'last_run': None,
                'emails_processed': 0
            })
            print("Backfill state reset")
        return
    
    # Generate queries
    queries = get_search_queries(
        days=args.days,
        max_queries=args.max_queries,
        priority=args.priority,
        offset=args.offset
    )
    
    if args.json:
        print(json.dumps([asdict(q) for q in queries], indent=2))
    else:
        print(f"Generated {len(queries)} search queries:")
        for i, q in enumerate(queries[:5], 1):
            print(f"  {i}. [{q.context_type}] {q.context_name}: {q.query[:60]}...")
        if len(queries) > 5:
            print(f"  ... and {len(queries) - 5} more")


if __name__ == "__main__":
    main()

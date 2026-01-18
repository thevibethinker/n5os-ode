#!/usr/bin/env python3
"""
SMS Deal Handler — Worker 4 (SMS Interface)

Purpose:
- Parse "n5 deal <query> <update>" commands from SMS
- Route through DealSignalRouter for matching + extraction
- Queue Notion sync via notion_deal_sync.py
- Return human-friendly SMS response

CLI:
  python3 sms_deal_handler.py --message "n5 deal darwinbox Ready to proceed"
  python3 sms_deal_handler.py --message "n5 deal ribbon Christine confirmed budget" --dry-run
  python3 sms_deal_handler.py --help
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Ensure we can import from the same directory
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from deal_signal_router import DealSignalRouter, ProcessResult

DB_PATH_DEFAULT = "/home/workspace/N5/data/deals.db"
CONFIG_PATH_DEFAULT = "/home/workspace/N5/config/deal_signal_config.json"


@dataclass
class ParsedCommand:
    """Result of parsing an SMS deal command."""
    valid: bool
    query: Optional[str] = None
    update: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SMSHandlerResult:
    """Result of processing an SMS deal command."""
    success: bool
    matched: bool
    deal_id: Optional[str]
    deal_company: Optional[str]
    response: str
    dry_run: bool
    notion_queued: bool
    process_result: Optional[ProcessResult] = None


def parse_sms_deal_command(message: str) -> ParsedCommand:
    """
    Parse 'n5 deal <query> <update>' format.
    
    Handles various formats:
    - n5 deal darwinbox Ready to proceed
    - n5 deal "ribbon health" Christine confirmed budget
    - N5 Deal GLOAT Meeting scheduled for Tuesday
    
    Returns ParsedCommand with valid=True if parseable.
    """
    message = message.strip()
    
    # Check for n5 deal prefix with content after (case-insensitive)
    # Must have whitespace and content after "deal"
    if not re.match(r'^n5\s+deal\s+\S', message, re.IGNORECASE):
        # Check if it's "n5 deal" with nothing after
        if re.match(r'^n5\s+deal\s*$', message, re.IGNORECASE):
            return ParsedCommand(
                valid=False,
                error="Missing company and update. Use: n5 deal <company> <update>"
            )
        return ParsedCommand(
            valid=False, 
            error="Not a deal command. Use: n5 deal <company> <update>"
        )
    
    # Remove the prefix
    remainder = re.sub(r'^n5\s+deal\s+', '', message, flags=re.IGNORECASE).strip()
    
    if not remainder:
        return ParsedCommand(
            valid=False,
            error="Missing company and update. Use: n5 deal <company> <update>"
        )
    
    # Handle quoted company names: "ribbon health" update text
    quoted_match = re.match(r'^["\']([^"\']+)["\']\s+(.+)$', remainder)
    if quoted_match:
        return ParsedCommand(
            valid=True,
            query=quoted_match.group(1).strip(),
            update=quoted_match.group(2).strip()
        )
    
    # Handle unquoted: first word is query, rest is update
    parts = remainder.split(None, 1)
    if len(parts) < 2:
        return ParsedCommand(
            valid=False,
            error="Missing update text. Use: n5 deal <company> <update>"
        )
    
    return ParsedCommand(
        valid=True,
        query=parts[0].strip(),
        update=parts[1].strip()
    )


def get_similar_deals(db_path: str, query: str, limit: int = 3) -> List[Tuple[str, str, int]]:
    """
    Get similar deal suggestions for "did you mean" responses.
    Returns list of (deal_id, company, similarity_score).
    """
    from difflib import SequenceMatcher
    
    query_lower = query.lower()
    results = []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, company FROM deals")
        
        for row in c.fetchall():
            deal_id = row['id']
            company = row['company'] or ''
            
            # Score based on company name similarity
            ratio = SequenceMatcher(None, query_lower, company.lower()).ratio()
            score = int(ratio * 100)
            
            # Also check if query is substring
            if query_lower in company.lower():
                score = max(score, 75)
            
            if score >= 50:
                results.append((deal_id, company, score))
        
        conn.close()
    except Exception:
        pass
    
    # Sort by score descending
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:limit]


def queue_notion_sync(
    db_path: str,
    deal_id: str,
    source_title: str,
    source_type: str,
    key_facts: List[str],
    next_action: Optional[str] = None,
    dry_run: bool = False
) -> bool:
    """
    Queue Notion intelligence update via notion_deal_sync.py enqueue-intel.
    
    Returns True if successfully queued (or dry_run).
    """
    if dry_run:
        return True
    
    try:
        from notion_deal_sync import DealDB
        
        deal_db = DealDB(db_path)
        deal_db.ensure_schema()
        
        # Get notion_page_id from entity state
        entity_state = deal_db.get_entity_state('deal', deal_id)
        if not entity_state or not entity_state.get('notion_page_id'):
            # No Notion page linked yet - skip silently
            return False
        
        notion_page_id = entity_state['notion_page_id']
        
        # Build payload for intel append
        payload = {
            'source_title': source_title,
            'source_type': source_type,
            'key_facts': key_facts,
        }
        if next_action:
            payload['next_action'] = next_action
        
        # Enqueue to outbox
        outbox_id = deal_db.enqueue_outbox(
            entity_type='deal',
            entity_id=deal_id,
            notion_page_id=notion_page_id,
            action_type='append_intel',
            payload=payload,
            dry_run=dry_run
        )
        
        return outbox_id is not None
    except Exception as e:
        # Log but don't fail the main operation
        print(f"[sms_deal_handler] Notion queue error: {e}", file=sys.stderr)
        return False


def format_response(result: SMSHandlerResult) -> str:
    """Format the SMS response message."""
    return result.response


def handle_deal_sms(
    message: str,
    db_path: str = DB_PATH_DEFAULT,
    config_path: str = CONFIG_PATH_DEFAULT,
    dry_run: bool = False
) -> SMSHandlerResult:
    """
    Process an SMS deal update.
    
    1. Parse the command
    2. Match to deal via DealSignalRouter
    3. Extract signal intelligence
    4. Update local DB
    5. Queue Notion sync
    6. Return formatted response
    """
    # Parse command
    parsed = parse_sms_deal_command(message)
    if not parsed.valid:
        return SMSHandlerResult(
            success=False,
            matched=False,
            deal_id=None,
            deal_company=None,
            response=f"❌ {parsed.error}",
            dry_run=dry_run,
            notion_queued=False
        )
    
    # Initialize router
    router = DealSignalRouter(db_path=db_path, config_path=config_path)
    
    # Match deal
    match = router.match_deal(query=parsed.query, context="")
    
    min_confidence = int(router.config.get("matching", {}).get("min_confidence_threshold", 70))
    
    if not match.deal_id or match.confidence < min_confidence:
        # Try to suggest similar deals
        suggestions = get_similar_deals(db_path, parsed.query)
        
        if suggestions:
            suggest_text = ", ".join([f"{s[1]} ({s[2]}%)" for s in suggestions[:3]])
            response = f"⚠️ No deal found for '{parsed.query}'. Did you mean: {suggest_text}?"
        else:
            response = f"⚠️ No deal match found for '{parsed.query}'"
        
        return SMSHandlerResult(
            success=True,
            matched=False,
            deal_id=None,
            deal_company=None,
            response=response,
            dry_run=dry_run,
            notion_queued=False
        )
    
    # Get deal details
    deal = router.get_deal(match.deal_id)
    if not deal:
        return SMSHandlerResult(
            success=False,
            matched=True,
            deal_id=match.deal_id,
            deal_company=None,
            response=f"❌ Deal '{match.deal_id}' not found in database",
            dry_run=dry_run,
            notion_queued=False
        )
    
    company = deal.get('company', match.deal_id)
    
    # Process signal through router (this updates the DB)
    # Reconstruct full message for signal extraction
    full_content = f"n5 deal {parsed.query} {parsed.update}"
    
    process_result = router.process_signal(
        source='sms',
        content=full_content,
        metadata={'query': parsed.query, 'update': parsed.update},
        context='',
        dry_run=dry_run
    )
    
    if not process_result.success:
        return SMSHandlerResult(
            success=False,
            matched=True,
            deal_id=match.deal_id,
            deal_company=company,
            response=f"❌ Error processing update: {process_result.notes}",
            dry_run=dry_run,
            notion_queued=False,
            process_result=process_result
        )
    
    # Build response
    action_parts = []
    
    if process_result.extraction:
        ext = process_result.extraction
        
        if ext.inferred_stage and ext.stage_signal == 'stage_change':
            action_parts.append(f"Stage → {ext.inferred_stage}")
        
        if ext.next_action:
            action_parts.append(f"Next: {ext.next_action[:50]}")
        
        if ext.sentiment and ext.sentiment != 'neutral':
            action_parts.append(f"({ext.sentiment})")
    
    if not action_parts:
        action_parts.append("activity logged")
    
    action_text = ", ".join(action_parts)
    
    # Queue Notion sync
    notion_queued = False
    if process_result.extraction and not dry_run:
        ext = process_result.extraction
        notion_queued = queue_notion_sync(
            db_path=db_path,
            deal_id=match.deal_id,
            source_title=f"SMS Update: {datetime.now().strftime('%Y-%m-%d')}",
            source_type='sms',
            key_facts=ext.key_facts if ext.key_facts else [parsed.update[:200]],
            next_action=ext.next_action,
            dry_run=dry_run
        )
    
    # Format final response
    if dry_run:
        response = f"🔍 [DRY RUN] Would update {company}: {action_text}"
    else:
        notion_suffix = " (Notion queued)" if notion_queued else ""
        response = f"✓ Updated {company}: {action_text}{notion_suffix}"
    
    return SMSHandlerResult(
        success=True,
        matched=True,
        deal_id=match.deal_id,
        deal_company=company,
        response=response,
        dry_run=dry_run,
        notion_queued=notion_queued,
        process_result=process_result
    )


def main():
    parser = argparse.ArgumentParser(
        description="Process SMS deal commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sms_deal_handler.py --message "n5 deal darwinbox Ready to proceed with pilot"
  python3 sms_deal_handler.py --message "n5 deal ribbon Christine confirmed budget" --dry-run
  python3 sms_deal_handler.py --message 'n5 deal "gloat hr" Meeting scheduled for Tuesday'
        """
    )
    parser.add_argument(
        "--message", "-m",
        required=True,
        help="The SMS message to process"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't make any changes, just show what would happen"
    )
    parser.add_argument(
        "--db-path",
        default=DB_PATH_DEFAULT,
        help=f"Path to deals database (default: {DB_PATH_DEFAULT})"
    )
    parser.add_argument(
        "--config-path",
        default=CONFIG_PATH_DEFAULT,
        help=f"Path to signal config (default: {CONFIG_PATH_DEFAULT})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    result = handle_deal_sms(
        message=args.message,
        db_path=args.db_path,
        config_path=args.config_path,
        dry_run=args.dry_run
    )
    
    if args.json:
        output = {
            'success': result.success,
            'matched': result.matched,
            'deal_id': result.deal_id,
            'deal_company': result.deal_company,
            'response': result.response,
            'dry_run': result.dry_run,
            'notion_queued': result.notion_queued,
        }
        if result.process_result and result.process_result.extraction:
            ext = result.process_result.extraction
            output['extraction'] = {
                'stage_signal': ext.stage_signal,
                'inferred_stage': ext.inferred_stage,
                'key_facts': ext.key_facts,
                'next_action': ext.next_action,
                'sentiment': ext.sentiment,
            }
        print(json.dumps(output, indent=2))
    else:
        print(result.response)
    
    # Exit code: 0 for success, 1 for error
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

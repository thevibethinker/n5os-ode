#!/usr/bin/env python3
"""
SMS Deal Handler — Worker 4 (SMS Interface)

Purpose:
- Parse "n5 deal <command>" messages from SMS
- Support commands: update, add, status, list
- Route through DealSignalRouter for matching + extraction
- Queue Notion sync via notion_deal_sync.py
- Return human-friendly SMS response

CLI:
  python3 sms_deal_handler.py --message "n5 deal darwinbox Ready to proceed"
  python3 sms_deal_handler.py --message "n5 deal status calendly"
  python3 sms_deal_handler.py --message "n5 deal list hot"
  python3 sms_deal_handler.py --message "n5 deal add Acme careerspan Met at conference"
  python3 sms_deal_handler.py --help

Commands:
  n5 deal <company> <update>              Update a deal with new information
  n5 deal status <company>                Get deal status
  n5 deal list [hot|warm|cold|all]        List deals by temperature
  n5 deal add <company> <pipeline> [note] Add new deal (pipeline: careerspan|zo)
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

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
    command_type: str = "update"
    pipeline: Optional[str] = None
    filter_temp: Optional[str] = None
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
    Parse 'n5 deal <command>' format.
    
    Supported commands:
    - n5 deal <company> <update>           → update (default)
    - n5 deal add <company> <pipeline> [notes]
    - n5 deal status <company>
    - n5 deal list [hot|warm|cold|all]
    """
    message = message.strip()
    
    if not re.match(r'^n5\s+deal\b', message, re.IGNORECASE):
        return ParsedCommand(
            valid=False, 
            error="Not a deal command. Use: n5 deal <company> <update>"
        )
    
    remainder = re.sub(r'^n5\s+deal\s*', '', message, flags=re.IGNORECASE).strip()
    
    if not remainder:
        return ParsedCommand(
            valid=False,
            error="Missing command. Try: n5 deal status <company>, n5 deal list, or n5 deal <company> <update>"
        )
    
    # ADD command
    add_match = re.match(r'^add\s+(.+)$', remainder, re.IGNORECASE)
    if add_match:
        add_remainder = add_match.group(1).strip()
        quoted = re.match(r'^["\']([^"\']+)["\']\s+(\w+)\s*(.*)$', add_remainder)
        if quoted:
            return ParsedCommand(
                valid=True,
                command_type="add",
                query=quoted.group(1).strip(),
                pipeline=quoted.group(2).strip().lower(),
                update=quoted.group(3).strip() if quoted.group(3) else None
            )
        parts = add_remainder.split(None, 2)
        if len(parts) >= 2:
            return ParsedCommand(
                valid=True,
                command_type="add",
                query=parts[0],
                pipeline=parts[1].lower(),
                update=parts[2] if len(parts) > 2 else None
            )
        return ParsedCommand(
            valid=False,
            error="Usage: n5 deal add <company> <pipeline> [notes]. Pipelines: careerspan, zo"
        )
    
    # STATUS command
    status_match = re.match(r'^status\s+(.+)$', remainder, re.IGNORECASE)
    if status_match:
        company = status_match.group(1).strip().strip("\"'")
        return ParsedCommand(valid=True, command_type="status", query=company)
    
    # LIST command
    list_match = re.match(r'^list(?:\s+(.+))?$', remainder, re.IGNORECASE)
    if list_match:
        temp_filter = (list_match.group(1) or "hot").strip().lower()
        if temp_filter not in ("hot", "warm", "cold", "all"):
            temp_filter = "hot"
        return ParsedCommand(valid=True, command_type="list", filter_temp=temp_filter)
    
    # DEFAULT: update command
    quoted_match = re.match(r'^["\']([^"\']+)["\']\s+(.+)$', remainder)
    if quoted_match:
        return ParsedCommand(
            valid=True,
            command_type="update",
            query=quoted_match.group(1).strip(),
            update=quoted_match.group(2).strip()
        )
    
    parts = remainder.split(None, 1)
    if len(parts) < 2:
        return ParsedCommand(valid=True, command_type="status", query=parts[0])
    
    return ParsedCommand(valid=True, command_type="update", query=parts[0], update=parts[1])


def get_similar_deals(db_path: str, query: str, limit: int = 3) -> List[Tuple[str, str, int]]:
    """Find deals with similar company names."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query_lower = query.lower()
    c.execute("SELECT id, company FROM deals WHERE company IS NOT NULL")
    
    results = []
    for row in c.fetchall():
        deal_id, company = row
        if not company:
            continue
        company_lower = company.lower()
        if query_lower in company_lower or company_lower in query_lower:
            score = 80
        elif any(w in company_lower for w in query_lower.split()):
            score = 60
        else:
            continue
        results.append((deal_id, company, score))
    
    conn.close()
    results.sort(key=lambda x: -x[2])
    return results[:limit]


def queue_notion_sync(
    db_path: str,
    deal_id: str,
    source_title: str,
    source_type: str,
    key_facts: List[str],
    next_action: Optional[str],
    dry_run: bool
) -> bool:
    """Queue intel for Notion sync."""
    try:
        from notion_deal_sync import DealDB, format_intel_entry
        
        db = DealDB(db_path)
        db.ensure_schema()
        
        conn = db.connect()
        c = conn.cursor()
        c.execute("SELECT external_id FROM deals WHERE id = ?", (deal_id,))
        row = c.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return False
        
        notion_page_id = row[0]
        
        entry = format_intel_entry(
            date=datetime.now().date().isoformat(),
            source_title=source_title,
            source_type=source_type,
            key_facts=key_facts,
            next_action=next_action,
        )
        
        payload = {'entry': entry, 'next_action': next_action}
        
        db.enqueue_outbox(
            entity_type='deal',
            entity_id=deal_id,
            notion_page_id=notion_page_id,
            action_type='append_intel',
            payload=payload,
            dry_run=dry_run
        )
        
        return True
    except Exception as e:
        print(f"[sms_deal_handler] Notion queue error: {e}", file=sys.stderr)
        return False


def handle_deal_add(company: str, pipeline: str, notes: Optional[str], db_path: str, dry_run: bool) -> SMSHandlerResult:
    """Handle 'n5 deal add <company> <pipeline> [notes]' command."""
    valid_pipelines = ["careerspan", "zo"]
    if pipeline not in valid_pipelines:
        return SMSHandlerResult(
            success=False, matched=False, deal_id=None, deal_company=company,
            response=f"❌ Invalid pipeline '{pipeline}'. Use: careerspan or zo",
            dry_run=dry_run, notion_queued=False
        )
    
    slug = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')[:30]
    prefix = "cs-acq" if pipeline == "careerspan" else "zo-dp"
    deal_id = f"{prefix}-{slug}"
    deal_type = "careerspan_acquirer" if pipeline == "careerspan" else "zo_partnership"
    
    if dry_run:
        return SMSHandlerResult(
            success=True, matched=False, deal_id=deal_id, deal_company=company,
            response=f"🔍 [DRY RUN] Would add {company} to {pipeline} pipeline as {deal_id}",
            dry_run=True, notion_queued=False
        )
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    try:
        c.execute("""
            INSERT INTO deals (id, deal_type, company, pipeline, stage, temperature, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'identified', 'cold', ?, ?, ?)
        """, (deal_id, deal_type, company, pipeline, notes or "", now, now))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return SMSHandlerResult(
            success=False, matched=True, deal_id=deal_id, deal_company=company,
            response=f"❌ Deal '{company}' already exists in {pipeline}",
            dry_run=False, notion_queued=False
        )
    finally:
        conn.close()
    
    return SMSHandlerResult(
        success=True, matched=False, deal_id=deal_id, deal_company=company,
        response=f"✓ Added {company} to {pipeline} pipeline ({deal_id})",
        dry_run=False, notion_queued=False
    )


def handle_deal_status(query: str, db_path: str, config_path: str) -> SMSHandlerResult:
    """Handle 'n5 deal status <company>' command."""
    router = DealSignalRouter(db_path=db_path, config_path=config_path)
    match = router.match_deal(query=query, context="")
    
    if not match.deal_id:
        return SMSHandlerResult(
            success=True, matched=False, deal_id=None, deal_company=query,
            response=f"❓ No deal found matching '{query}'",
            dry_run=False, notion_queued=False
        )
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT company, stage, temperature, next_action, next_action_date, last_touched, pipeline
        FROM deals WHERE id = ?
    """, (match.deal_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return SMSHandlerResult(
            success=True, matched=False, deal_id=match.deal_id, deal_company=query,
            response=f"❓ Deal {match.deal_id} not found in DB",
            dry_run=False, notion_queued=False
        )
    
    d = dict(row)
    company = d['company']
    stage = d['stage'] or 'unknown'
    temp = d['temperature'] or ''
    next_action = d['next_action'] or ''
    last_touched = d['last_touched'] or ''
    
    if last_touched:
        try:
            lt = datetime.fromisoformat(last_touched.replace('Z', '+00:00').replace('+00:00', ''))
            days_ago = (datetime.now() - lt).days
            last_str = "today" if days_ago == 0 else "yesterday" if days_ago == 1 else f"{days_ago}d ago"
        except:
            last_str = last_touched[:10]
    else:
        last_str = "never"
    
    temp_emoji = {"hot": "🔥", "warm": "🌡️", "cold": "❄️"}.get(temp, "")
    response = f"{company}: {stage} ({temp}{temp_emoji}). Last: {last_str}."
    if next_action:
        response += f" Next: {next_action}"
    
    return SMSHandlerResult(
        success=True, matched=True, deal_id=match.deal_id, deal_company=company,
        response=response, dry_run=False, notion_queued=False
    )


def handle_deal_list(temp_filter: str, db_path: str) -> SMSHandlerResult:
    """Handle 'n5 deal list [hot|warm|cold|all]' command."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if temp_filter == "all":
        c.execute("""
            SELECT company, stage, temperature, pipeline FROM deals
            WHERE stage NOT IN ('closed_won', 'closed_lost', 'churned')
            ORDER BY CASE temperature WHEN 'hot' THEN 1 WHEN 'warm' THEN 2 WHEN 'cold' THEN 3 ELSE 4 END, company
            LIMIT 15
        """)
    else:
        c.execute("""
            SELECT company, stage, temperature, pipeline FROM deals
            WHERE temperature = ? AND stage NOT IN ('closed_won', 'closed_lost', 'churned')
            ORDER BY company LIMIT 10
        """, (temp_filter,))
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return SMSHandlerResult(
            success=True, matched=False, deal_id=None, deal_company=None,
            response=f"No {temp_filter} deals found.",
            dry_run=False, notion_queued=False
        )
    
    temp_emoji = {"hot": "🔥", "warm": "🌡️", "cold": "❄️"}
    lines = []
    for r in rows:
        emoji = temp_emoji.get(r['temperature'], "")
        tag = "[CS]" if r['pipeline'] == "careerspan" else "[ZO]" if r['pipeline'] == "zo" else ""
        lines.append(f"{emoji}{r['company']} ({r['stage']}) {tag}")
    
    header = f"{temp_filter.title()} deals:" if temp_filter != "all" else "Active deals:"
    response = f"{header}\n" + "\n".join(lines)
    
    return SMSHandlerResult(
        success=True, matched=True, deal_id=None, deal_company=None,
        response=response, dry_run=False, notion_queued=False
    )


def handle_deal_sms(
    message: str,
    db_path: str = DB_PATH_DEFAULT,
    config_path: str = CONFIG_PATH_DEFAULT,
    dry_run: bool = False
) -> SMSHandlerResult:
    """Process an SMS deal command."""
    parsed = parse_sms_deal_command(message)
    
    if not parsed.valid:
        return SMSHandlerResult(
            success=False, matched=False, deal_id=None, deal_company=None,
            response=f"❌ {parsed.error}", dry_run=dry_run, notion_queued=False
        )
    
    if parsed.command_type == "add":
        return handle_deal_add(parsed.query, parsed.pipeline, parsed.update, db_path, dry_run)
    
    if parsed.command_type == "status":
        return handle_deal_status(parsed.query, db_path, config_path)
    
    if parsed.command_type == "list":
        return handle_deal_list(parsed.filter_temp or "hot", db_path)
    
    # DEFAULT: update command
    router = DealSignalRouter(db_path=db_path, config_path=config_path)
    match = router.match_deal(query=parsed.query, context="")
    
    min_confidence = int(router.config.get("matching", {}).get("min_confidence_threshold", 70))
    
    if not match.deal_id or match.confidence < min_confidence:
        suggestions = get_similar_deals(db_path, parsed.query)
        if suggestions:
            suggest_text = ", ".join([f"{s[1]} ({s[2]}%)" for s in suggestions[:3]])
            response = f"⚠️ No deal found for '{parsed.query}'. Did you mean: {suggest_text}?"
        else:
            response = f"⚠️ No deal match found for '{parsed.query}'"
        return SMSHandlerResult(
            success=True, matched=False, deal_id=None, deal_company=None,
            response=response, dry_run=dry_run, notion_queued=False
        )
    
    deal = router.get_deal(match.deal_id)
    if not deal:
        return SMSHandlerResult(
            success=False, matched=True, deal_id=match.deal_id, deal_company=None,
            response=f"❌ Deal '{match.deal_id}' not found in database",
            dry_run=dry_run, notion_queued=False
        )
    
    company = deal.get('company', match.deal_id)
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
            success=False, matched=True, deal_id=match.deal_id, deal_company=company,
            response=f"❌ Error processing update: {process_result.notes}",
            dry_run=dry_run, notion_queued=False, process_result=process_result
        )
    
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
    
    if dry_run:
        response = f"🔍 [DRY RUN] Would update {company}: {action_text}"
    else:
        notion_suffix = " (Notion queued)" if notion_queued else ""
        response = f"✓ Updated {company}: {action_text}{notion_suffix}"
    
    return SMSHandlerResult(
        success=True, matched=True, deal_id=match.deal_id, deal_company=company,
        response=response, dry_run=dry_run, notion_queued=notion_queued, process_result=process_result
    )


def main():
    parser = argparse.ArgumentParser(
        description="Process SMS deal commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sms_deal_handler.py -m "n5 deal darwinbox Ready to proceed"
  python3 sms_deal_handler.py -m "n5 deal status calendly"
  python3 sms_deal_handler.py -m "n5 deal list hot"
  python3 sms_deal_handler.py -m "n5 deal add Acme careerspan Met at conference" --dry-run
        """
    )
    parser.add_argument("--message", "-m", required=True, help="The SMS message to process")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Don't make changes")
    parser.add_argument("--db-path", default=DB_PATH_DEFAULT)
    parser.add_argument("--config-path", default=CONFIG_PATH_DEFAULT)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
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
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

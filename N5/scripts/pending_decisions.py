#!/usr/bin/env python3
"""
Pending Decisions Store - Cross-conversation decision management
Created by D3.1 Drop for zoputer-autonomy-v2
"""

import sqlite3
import json
import uuid
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

# Database path
DB_PATH = "/home/workspace/N5/data/pending_decisions.db"
SCHEMA_PATH = "/home/workspace/N5/config/pending_decisions_schema.sql"

def init_db() -> None:
    """Initialize the database with schema if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        # Read and execute schema
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()

def create_decision(
    origin: str,
    origin_conversation: str,
    summary: str,
    full_context: Dict[str, Any],
    options: Optional[List[Dict[str, Any]]] = None,
    priority: str = "normal",
    expires_in_hours: int = 24
) -> str:
    """Create a new pending decision. Returns decision_id."""
    if len(summary) > 160:
        raise ValueError("Summary must be <= 160 characters for SMS compatibility")
    
    if priority not in ['low', 'normal', 'high', 'critical']:
        raise ValueError("Priority must be one of: low, normal, high, critical")
    
    if origin not in ['va', 'zoputer']:
        raise ValueError("Origin must be 'va' or 'zoputer'")
    
    decision_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    expires_at = (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat() + "Z"
    
    # Ensure full_context has required structure
    context = {
        "question": full_context.get("question", ""),
        "background": full_context.get("background", ""),
        "options": options or full_context.get("options", []),
        "recommendation": full_context.get("recommendation"),
        "recommendation_confidence": full_context.get("recommendation_confidence"),
        "deadline": full_context.get("deadline"),
        "related_files": full_context.get("related_files", []),
        "escalation_chain": full_context.get("escalation_chain", [])
    }
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO pending_decisions 
            (id, created_at, expires_at, priority, origin, origin_conversation, 
             summary, full_context, options)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision_id, created_at, expires_at, priority, origin, 
            origin_conversation, summary, json.dumps(context), 
            json.dumps(options) if options else None
        ))
        conn.commit()
    
    return decision_id

def get_decision(decision_id: str) -> Optional[Dict[str, Any]]:
    """Get a single decision by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM pending_decisions WHERE id = ?", (decision_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        result = dict(row)
        # Parse JSON fields
        if result['full_context']:
            result['full_context'] = json.loads(result['full_context'])
        if result['options']:
            result['options'] = json.loads(result['options'])
        
        return result

def list_pending(priority: Optional[str] = None, origin: Optional[str] = None, status: str = "pending") -> List[Dict[str, Any]]:
    """List all pending decisions, optionally filtered."""
    query = "SELECT * FROM pending_decisions WHERE status = ?"
    params = [status]
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    if origin:
        query += " AND origin = ?"
        params.append(origin)
    
    query += " ORDER BY priority DESC, created_at DESC"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            if result['full_context']:
                result['full_context'] = json.loads(result['full_context'])
            if result['options']:
                result['options'] = json.loads(result['options'])
            results.append(result)
        
        return results

def resolve_decision(
    decision_id: str,
    resolution: str,
    resolved_by: str,
    notes: Optional[str] = None
) -> bool:
    """Mark a decision as resolved."""
    resolved_at = datetime.utcnow().isoformat() + "Z"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            UPDATE pending_decisions 
            SET status = 'resolved', resolved_at = ?, resolved_by = ?, 
                resolution = ?, resolution_notes = ?
            WHERE id = ? AND status = 'pending'
        """, (resolved_at, resolved_by, resolution, notes, decision_id))
        
        return cursor.rowcount > 0

def get_context_for_sms(decision_id: str) -> Optional[Dict[str, Any]]:
    """Get minimal context for SMS notification."""
    decision = get_decision(decision_id)
    if not decision:
        return None
    
    return {
        "id": decision_id,
        "summary": decision["summary"],
        "priority": decision["priority"],
        "created_at": decision["created_at"],
        "expires_at": decision["expires_at"],
        "origin": decision["origin"],
        "options_count": len(decision.get("options", [])) if decision.get("options") else 0
    }

def expire_old_decisions() -> int:
    """Mark expired decisions. Returns count expired."""
    now = datetime.utcnow().isoformat() + "Z"
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            UPDATE pending_decisions 
            SET status = 'expired'
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        
        return cursor.rowcount

def cancel_decision(decision_id: str, cancelled_by: str) -> bool:
    """Cancel a pending decision."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            UPDATE pending_decisions 
            SET status = 'cancelled', resolved_at = ?, resolved_by = ?
            WHERE id = ? AND status = 'pending'
        """, (datetime.utcnow().isoformat() + "Z", cancelled_by, decision_id))
        
        return cursor.rowcount > 0

def main():
    """CLI interface for pending decisions."""
    parser = argparse.ArgumentParser(description="Manage pending decisions across conversations")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new pending decision")
    create_parser.add_argument("--origin", required=True, choices=["va", "zoputer"])
    create_parser.add_argument("--conversation", required=True, help="Origin conversation ID")
    create_parser.add_argument("--summary", required=True, help="Brief summary (<=160 chars)")
    create_parser.add_argument("--context", required=True, help="Full context as JSON string")
    create_parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "critical"])
    create_parser.add_argument("--expires-in", type=int, default=24, help="Hours until expiration")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List decisions")
    list_parser.add_argument("--pending", action="store_true", help="Only show pending decisions")
    list_parser.add_argument("--priority", choices=["low", "normal", "high", "critical"])
    list_parser.add_argument("--origin", choices=["va", "zoputer"])
    list_parser.add_argument("--status", default="pending", help="Status filter")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get decision by ID")
    get_parser.add_argument("decision_id", help="Decision ID")
    get_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a pending decision")
    resolve_parser.add_argument("decision_id", help="Decision ID")
    resolve_parser.add_argument("--resolution", required=True, help="The decision made")
    resolve_parser.add_argument("--by", required=True, help="Conversation ID resolving this")
    resolve_parser.add_argument("--notes", help="Additional notes")
    
    # Expire command
    expire_parser = subparsers.add_parser("expire", help="Expire old decisions")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a pending decision")
    cancel_parser.add_argument("decision_id", help="Decision ID")
    cancel_parser.add_argument("--by", required=True, help="Conversation ID cancelling this")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    init_db()
    
    try:
        if args.command == "create":
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print("Error: Context must be valid JSON")
                return
            
            decision_id = create_decision(
                origin=args.origin,
                origin_conversation=args.conversation,
                summary=args.summary,
                full_context=context,
                priority=args.priority,
                expires_in_hours=args.expires_in
            )
            print(f"Created decision: {decision_id}")
        
        elif args.command == "list":
            decisions = list_pending(
                priority=args.priority,
                origin=args.origin,
                status=args.status
            )
            
            if args.json:
                print(json.dumps(decisions, indent=2))
            else:
                if not decisions:
                    print(f"No {args.status} decisions found.")
                else:
                    print(f"\n{len(decisions)} {args.status} decision(s):")
                    for d in decisions:
                        print(f"  {d['id'][:8]}... | {d['priority']:8} | {d['origin']:7} | {d['summary']}")
        
        elif args.command == "get":
            decision = get_decision(args.decision_id)
            if not decision:
                print(f"Decision {args.decision_id} not found.")
                return
            
            if args.json:
                print(json.dumps(decision, indent=2))
            else:
                print(f"Decision: {decision['id']}")
                print(f"Status: {decision['status']}")
                print(f"Priority: {decision['priority']}")
                print(f"Origin: {decision['origin']} (conversation: {decision['origin_conversation']})")
                print(f"Created: {decision['created_at']}")
                print(f"Expires: {decision['expires_at']}")
                print(f"Summary: {decision['summary']}")
                
                if decision['full_context']:
                    print("\nFull Context:")
                    context = decision['full_context']
                    print(f"  Question: {context.get('question', 'N/A')}")
                    print(f"  Background: {context.get('background', 'N/A')}")
                    if context.get('options'):
                        print("  Options:")
                        for i, opt in enumerate(context['options']):
                            print(f"    {i+1}. {opt.get('description', opt)}")
                
                if decision['status'] == 'resolved':
                    print(f"\nResolved: {decision['resolved_at']}")
                    print(f"Resolved by: {decision['resolved_by']}")
                    print(f"Resolution: {decision['resolution']}")
                    if decision['resolution_notes']:
                        print(f"Notes: {decision['resolution_notes']}")
        
        elif args.command == "resolve":
            success = resolve_decision(
                decision_id=args.decision_id,
                resolution=args.resolution,
                resolved_by=args.by,
                notes=args.notes
            )
            if success:
                print(f"Decision {args.decision_id} resolved.")
            else:
                print(f"Decision {args.decision_id} not found or already resolved.")
        
        elif args.command == "expire":
            count = expire_old_decisions()
            print(f"Expired {count} old decision(s).")
        
        elif args.command == "cancel":
            success = cancel_decision(args.decision_id, args.by)
            if success:
                print(f"Decision {args.decision_id} cancelled.")
            else:
                print(f"Decision {args.decision_id} not found or already resolved.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Edge Lifecycle: Manage edge status transitions and outcome tracking.

Usage:
    # Mark edge as superseded by a newer decision
    python3 edge_lifecycle.py supersede --old-id 5 --new-id 12
    
    # Mark edge as reversed
    python3 edge_lifecycle.py reverse --id 5 --reason "Changed direction after user feedback"
    
    # Mark edge as decayed (stale)
    python3 edge_lifecycle.py decay --id 5
    
    # Link outcome to a hoped_for/concerned_about edge
    python3 edge_lifecycle.py outcome --id 5 --status validated --note "This worked out"
    
    # Reactivate a decayed edge
    python3 edge_lifecycle.py reactivate --id 5
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).parent.parent / "data" / "edges.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_edge(conn: sqlite3.Connection, edge_id: int) -> Optional[Dict]:
    """Get edge by ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM edges WHERE id = ?", (edge_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def supersede(old_id: int, new_id: int) -> Dict[str, Any]:
    """
    Mark an edge as superseded by a newer one.
    
    Args:
        old_id: ID of edge being superseded
        new_id: ID of replacement edge
    
    Returns:
        Status dict
    """
    conn = get_connection()
    try:
        # Verify both edges exist
        old_edge = get_edge(conn, old_id)
        new_edge = get_edge(conn, new_id)
        
        if not old_edge:
            return {"error": f"Edge {old_id} not found"}
        if not new_edge:
            return {"error": f"Edge {new_id} not found"}
        if old_edge['status'] != 'active':
            return {"error": f"Edge {old_id} is not active (status: {old_edge['status']})"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE edges 
            SET status = 'superseded', 
                superseded_by = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (new_id, old_id))
        conn.commit()
        
        return {
            "status": "success",
            "action": "superseded",
            "old_edge_id": old_id,
            "new_edge_id": new_id,
            "message": f"Edge {old_id} superseded by {new_id}"
        }
    finally:
        conn.close()


def reverse(edge_id: int, reason: str) -> Dict[str, Any]:
    """
    Mark an edge as reversed (decision was walked back).
    
    Args:
        edge_id: ID of edge to reverse
        reason: Why it was reversed
    
    Returns:
        Status dict
    """
    conn = get_connection()
    try:
        edge = get_edge(conn, edge_id)
        if not edge:
            return {"error": f"Edge {edge_id} not found"}
        if edge['status'] != 'active':
            return {"error": f"Edge {edge_id} is not active (status: {edge['status']})"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE edges 
            SET status = 'reversed', 
                reversed_at = datetime('now'),
                reversal_reason = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (reason, edge_id))
        conn.commit()
        
        return {
            "status": "success",
            "action": "reversed",
            "edge_id": edge_id,
            "reason": reason,
            "message": f"Edge {edge_id} marked as reversed"
        }
    finally:
        conn.close()


def decay(edge_id: int) -> Dict[str, Any]:
    """
    Mark an edge as decayed (stale, no longer relevant).
    
    Args:
        edge_id: ID of edge to decay
    
    Returns:
        Status dict
    """
    conn = get_connection()
    try:
        edge = get_edge(conn, edge_id)
        if not edge:
            return {"error": f"Edge {edge_id} not found"}
        if edge['status'] != 'active':
            return {"error": f"Edge {edge_id} is not active (status: {edge['status']})"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE edges 
            SET status = 'decayed', 
                updated_at = datetime('now')
            WHERE id = ?
        """, (edge_id,))
        conn.commit()
        
        return {
            "status": "success",
            "action": "decayed",
            "edge_id": edge_id,
            "message": f"Edge {edge_id} marked as decayed"
        }
    finally:
        conn.close()


def reactivate(edge_id: int) -> Dict[str, Any]:
    """
    Reactivate a decayed edge.
    
    Args:
        edge_id: ID of edge to reactivate
    
    Returns:
        Status dict
    """
    conn = get_connection()
    try:
        edge = get_edge(conn, edge_id)
        if not edge:
            return {"error": f"Edge {edge_id} not found"}
        if edge['status'] != 'decayed':
            return {"error": f"Edge {edge_id} is not decayed (status: {edge['status']})"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE edges 
            SET status = 'active', 
                updated_at = datetime('now')
            WHERE id = ?
        """, (edge_id,))
        conn.commit()
        
        return {
            "status": "success",
            "action": "reactivated",
            "edge_id": edge_id,
            "message": f"Edge {edge_id} reactivated"
        }
    finally:
        conn.close()


def link_outcome(
    edge_id: int, 
    outcome_status: str, 
    note: Optional[str] = None,
    outcome_edge_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Link outcome to a hoped_for or concerned_about edge.
    
    Args:
        edge_id: ID of expectation edge
        outcome_status: 'validated' or 'invalidated'
        note: Optional note about outcome
        outcome_edge_id: Optional ID of edge that proved/disproved expectation
    
    Returns:
        Status dict
    """
    if outcome_status not in ('validated', 'invalidated', 'pending'):
        return {"error": f"Invalid outcome_status: {outcome_status}. Must be: validated, invalidated, pending"}
    
    conn = get_connection()
    try:
        edge = get_edge(conn, edge_id)
        if not edge:
            return {"error": f"Edge {edge_id} not found"}
        if edge['relation'] not in ('hoped_for', 'concerned_about'):
            return {"error": f"Edge {edge_id} is not an expectation (relation: {edge['relation']})"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE edges 
            SET outcome_status = ?,
                outcome_note = ?,
                outcome_edge_id = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (outcome_status, note, outcome_edge_id, edge_id))
        conn.commit()
        
        return {
            "status": "success",
            "action": "outcome_linked",
            "edge_id": edge_id,
            "outcome_status": outcome_status,
            "message": f"Outcome '{outcome_status}' linked to edge {edge_id}"
        }
    finally:
        conn.close()


def find_stale_edges(days: int = 90) -> Dict[str, Any]:
    """
    Find edges that haven't been reviewed/updated in N days.
    
    Args:
        days: Threshold for staleness
    
    Returns:
        List of potentially stale edges
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM edges 
            WHERE status = 'active'
            AND updated_at < datetime('now', ? || ' days')
            ORDER BY updated_at ASC
        """, (f"-{days}",))
        
        stale = [dict(row) for row in cursor.fetchall()]
        
        return {
            "query": f"stale edges (>{days} days)",
            "count": len(stale),
            "edges": stale
        }
    finally:
        conn.close()


def find_pending_outcomes() -> Dict[str, Any]:
    """
    Find expectation edges without outcome validation.
    
    Returns:
        List of edges needing outcome review
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM edges 
            WHERE relation IN ('hoped_for', 'concerned_about')
            AND (outcome_status IS NULL OR outcome_status = 'pending')
            AND status = 'active'
            ORDER BY created_at ASC
        """)
        
        pending = [dict(row) for row in cursor.fetchall()]
        
        return {
            "query": "pending outcomes",
            "count": len(pending),
            "edges": pending
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Edge Lifecycle: Manage edge status")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Supersede
    sup_parser = subparsers.add_parser("supersede", help="Mark edge as superseded")
    sup_parser.add_argument("--old-id", type=int, required=True, help="Edge being superseded")
    sup_parser.add_argument("--new-id", type=int, required=True, help="Replacement edge")
    
    # Reverse
    rev_parser = subparsers.add_parser("reverse", help="Mark edge as reversed")
    rev_parser.add_argument("--id", type=int, required=True, help="Edge ID")
    rev_parser.add_argument("--reason", required=True, help="Reason for reversal")
    
    # Decay
    decay_parser = subparsers.add_parser("decay", help="Mark edge as decayed")
    decay_parser.add_argument("--id", type=int, required=True, help="Edge ID")
    
    # Reactivate
    react_parser = subparsers.add_parser("reactivate", help="Reactivate decayed edge")
    react_parser.add_argument("--id", type=int, required=True, help="Edge ID")
    
    # Link outcome
    outcome_parser = subparsers.add_parser("outcome", help="Link outcome to expectation")
    outcome_parser.add_argument("--id", type=int, required=True, help="Edge ID")
    outcome_parser.add_argument("--status", required=True, choices=['validated', 'invalidated', 'pending'])
    outcome_parser.add_argument("--note", help="Outcome note")
    outcome_parser.add_argument("--outcome-edge-id", type=int, help="Edge that proved/disproved")
    
    # Find stale
    stale_parser = subparsers.add_parser("stale", help="Find stale edges")
    stale_parser.add_argument("--days", type=int, default=90, help="Days threshold")
    
    # Find pending outcomes
    pending_parser = subparsers.add_parser("pending", help="Find pending outcomes")
    
    args = parser.parse_args()
    
    try:
        if args.command == "supersede":
            result = supersede(args.old_id, args.new_id)
        elif args.command == "reverse":
            result = reverse(args.id, args.reason)
        elif args.command == "decay":
            result = decay(args.id)
        elif args.command == "reactivate":
            result = reactivate(args.id)
        elif args.command == "outcome":
            result = link_outcome(args.id, args.status, args.note, getattr(args, 'outcome_edge_id', None))
        elif args.command == "stale":
            result = find_stale_edges(args.days)
        elif args.command == "pending":
            result = find_pending_outcomes()
        else:
            result = {"error": f"Unknown command: {args.command}"}
        
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


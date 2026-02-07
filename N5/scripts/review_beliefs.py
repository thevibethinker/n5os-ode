#!/usr/bin/env python3
"""
HITL Review CLI for low-confidence beliefs.

Usage:
  python3 review_beliefs.py list          # Show pending reviews
  python3 review_beliefs.py approve <id>  # Approve a belief
  python3 review_beliefs.py reject <id>   # Reject a belief
  python3 review_beliefs.py export        # Export snapshot
"""

import argparse
import sys
import json
import sqlite3
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="HITL Belief Review")
    parser.add_argument("command", choices=["list", "approve", "reject", "export"])
    parser.add_argument("belief_id", nargs="?")
    parser.add_argument("--notes", help="Reviewer notes")
    args = parser.parse_args()
    
    # Direct DB access
    db_path = "N5/cognition/reasoning.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if args.command == "list":
        cursor.execute("""
            SELECT rq.*, b.content, b.confidence
            FROM review_queue rq
            LEFT JOIN beliefs b ON rq.belief_id = b.id
            WHERE rq.status = 'pending'
            ORDER BY rq.created_at DESC
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print("No pending reviews.")
            conn.close()
            return
        
        for item in rows:
            item_dict = dict(item)
            print(f"\n[{item_dict['id']}] Belief: {item_dict['belief_id']}")
            print(f"  Content: {item_dict.get('content', 'N/A')[:100]}...")
            print(f"  Confidence: {item_dict.get('confidence', 0):.2f}")
            print(f"  Reason: {item_dict['reason']}")
    
    elif args.command == "approve":
        if not args.belief_id:
            print("Error: belief_id required")
            conn.close()
            return
        
        # Get current confidence
        cursor.execute("SELECT confidence FROM beliefs WHERE id = ?", (args.belief_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: Belief {args.belief_id} not found")
            conn.close()
            return
        
        # Boost confidence by 0.2
        new_confidence = min(1.0, row['confidence'] + 0.2)
        updated_at = datetime.utcnow().isoformat()
        
        cursor.execute("""
            UPDATE beliefs
            SET confidence = ?, updated_at = ?
            WHERE id = ?
        """, (new_confidence, updated_at, args.belief_id))
        
        # Mark review as approved
        cursor.execute("""
            UPDATE review_queue
            SET status = 'approved', reviewer_notes = ?, reviewed_at = ?
            WHERE belief_id = ?
        """, (args.notes, updated_at, args.belief_id))
        
        conn.commit()
        print(f"Approved: {args.belief_id} (confidence: {new_confidence:.2f})")
    
    elif args.command == "reject":
        if not args.belief_id:
            print("Error: belief_id required")
            conn.close()
            return
        
        cursor = conn.cursor()
        updated_at = datetime.utcnow().isoformat()
        
        # Archive belief
        cursor.execute("""
            UPDATE beliefs
            SET status = 'archived', updated_at = ?
            WHERE id = ?
        """, (updated_at, args.belief_id))
        
        # Mark review as rejected
        cursor.execute("""
            UPDATE review_queue
            SET status = 'rejected', reviewer_notes = ?, reviewed_at = ?
            WHERE belief_id = ?
        """, (args.notes, updated_at, args.belief_id))
        
        conn.commit()
        print(f"Rejected: {args.belief_id}")
    
    elif args.command == "export":
        cursor.execute("SELECT * FROM beliefs WHERE status = 'active'")
        rows = cursor.fetchall()
        
        beliefs = []
        for row in rows:
            belief = dict(row)
            if belief.get('evidence_json'):
                try:
                    belief['evidence'] = json.loads(belief['evidence_json'])
                except:
                    belief['evidence'] = []
            else:
                belief['evidence'] = []
            beliefs.append(belief)
        
        snapshot = {
            "exported_at": datetime.utcnow().isoformat(),
            "count": len(beliefs),
            "beliefs": beliefs
        }
        
        path = "N5/cognition/beliefs_snapshot.json"
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"Exported to: {path}")
    
    conn.close()

if __name__ == "__main__":
    main()

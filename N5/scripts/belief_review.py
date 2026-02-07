#!/usr/bin/env python3
"""
HITL Belief Review CLI

Process low-confidence beliefs that need human review.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/workspace')
from N5.cognition.belief_store import N5BeliefStore, HITL_QUEUE

def list_pending():
    """List all pending belief reviews."""
    if not HITL_QUEUE.exists():
        print("No HITL queue found")
        return []
    
    pending = list(HITL_QUEUE.glob("*.md"))
    print(f"Pending reviews: {len(pending)}")
    
    for p in pending:
        content = p.read_text()
        # Extract belief_id from frontmatter
        for line in content.split('\n'):
            if line.startswith('belief_id:'):
                belief_id = line.split(':')[1].strip()
                print(f"  - {p.stem}: {belief_id}")
                break
    
    return pending

def review(belief_id: str, action: str, notes: str = ""):
    """
    Process a belief review.
    
    Actions:
    - approve: Boost confidence to 0.7
    - reject: Remove belief
    - adjust:<float>: Set specific confidence
    """
    store = N5BeliefStore()
    belief = store.get_belief(belief_id)
    
    if not belief:
        print(f"Belief not found: {belief_id}")
        return False
    
    print(f"Reviewing: {belief.content[:80]}...")
    print(f"  Current confidence: {belief.confidence}")
    
    if action == "approve":
        delta = 0.7 - belief.confidence
        store.update_confidence(belief_id, delta)
        print(f"  ✓ Approved (confidence → 0.7)")
        
    elif action == "reject":
        store.update_confidence(belief_id, -1.0)  # Will trigger prune
        print(f"  ✗ Rejected (belief removed)")
        
    elif action.startswith("adjust:"):
        new_conf = float(action.split(":")[1])
        delta = new_conf - belief.confidence
        store.update_confidence(belief_id, delta)
        print(f"  ~ Adjusted (confidence → {new_conf})")
    
    else:
        print(f"Unknown action: {action}")
        return False
    
    # Remove from queue
    queue_files = list(HITL_QUEUE.glob(f"*_{belief_id}.md"))
    for qf in queue_files:
        qf.unlink()
        print(f"  Removed from queue: {qf.name}")
    
    return True

def batch_review(action: str):
    """Apply action to all pending reviews."""
    pending = list(HITL_QUEUE.glob("*.md")) if HITL_QUEUE.exists() else []
    
    if not pending:
        print("No pending reviews")
        return
    
    print(f"Batch {action} for {len(pending)} beliefs")
    
    for p in pending:
        content = p.read_text()
        for line in content.split('\n'):
            if line.startswith('belief_id:'):
                belief_id = line.split(':')[1].strip()
                review(belief_id, action)
                break

def main():
    if len(sys.argv) < 2:
        print("Usage: belief_review.py <command> [args]")
        print("Commands:")
        print("  list              - Show pending reviews")
        print("  review <id> <action> - Process a review")
        print("    Actions: approve, reject, adjust:<confidence>")
        print("  batch <action>    - Apply action to all pending")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_pending()
    
    elif cmd == "review":
        if len(sys.argv) < 4:
            print("Usage: belief_review.py review <belief_id> <action>")
            sys.exit(1)
        review(sys.argv[2], sys.argv[3])
    
    elif cmd == "batch":
        if len(sys.argv) < 3:
            print("Usage: belief_review.py batch <action>")
            sys.exit(1)
        batch_review(sys.argv[2])
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()

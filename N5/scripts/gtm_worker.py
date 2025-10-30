#!/usr/bin/env python3
"""
GTM Database Worker - Process batch of meetings
Run in dedicated conversation with fresh token budget
"""
import sys
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("/home/workspace/Knowledge/market_intelligence/gtm_intelligence.db")
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

def get_batch_assignments():
    """Get list of unprocessed meetings, split into batches"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    processed = {row[0] for row in cursor.execute("SELECT meeting_id FROM gtm_processing_registry")}
    conn.close()
    
    unprocessed = []
    for meeting_dir in sorted(MEETINGS_DIR.iterdir()):
        if meeting_dir.is_dir() and "external" in meeting_dir.name:
            b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
            if b31.exists() and meeting_dir.name not in processed:
                unprocessed.append(meeting_dir.name)
    
    # Split into batches of 10
    batches = []
    for i in range(0, len(unprocessed), 10):
        batches.append(unprocessed[i:i+10])
    
    return batches

def main():
    if len(sys.argv) < 2:
        # No batch specified, show batches
        batches = get_batch_assignments()
        print(f"\n=== GTM Database Backfill Batches ===\n")
        print(f"Total unprocessed meetings: {sum(len(b) for b in batches)}")
        print(f"Total batches: {len(batches)}\n")
        
        for i, batch in enumerate(batches, 1):
            print(f"Batch {i}: {len(batch)} meetings")
            for meeting in batch[:3]:
                print(f"  - {meeting}")
            if len(batch) > 3:
                print(f"  ... and {len(batch) - 3} more")
            print()
        
        print(f"\nUsage: python3 gtm_worker.py <batch_number>")
        print(f"   or: python3 gtm_worker.py --list-batch <batch_number>")
        return 0
    
    if sys.argv[1] == "--list-batch" and len(sys.argv) > 2:
        batch_num = int(sys.argv[2])
        batches = get_batch_assignments()
        
        if batch_num < 1 or batch_num > len(batches):
            print(f"Error: Batch {batch_num} doesn't exist (1-{len(batches)})")
            return 1
        
        batch = batches[batch_num - 1]
        print(json.dumps(batch, indent=2))
        return 0
    
    # Process specific batch
    batch_num = int(sys.argv[1])
    batches = get_batch_assignments()
    
    if batch_num < 1 or batch_num > len(batches):
        print(f"Error: Batch {batch_num} doesn't exist (1-{len(batches)})")
        return 1
    
    batch = batches[batch_num - 1]
    
    print(f"\n=== Processing Batch {batch_num} ===")
    print(f"Meetings: {len(batch)}\n")
    
    for meeting_id in batch:
        print(f"\nMeeting: {meeting_id}")
        b31_path = MEETINGS_DIR / meeting_id / "B31_STAKEHOLDER_RESEARCH.md"
        
        if not b31_path.exists():
            print("  ❌ B31 file not found")
            continue
        
        print(f"  📄 B31 file: {b31_path}")
        print(f"  📊 Ready for LLM extraction")
        print(f"  🔗 file '{b31_path.relative_to(Path('/home/workspace'))}'")
    
    print(f"\n✅ Batch {batch_num} assignments ready")
    print(f"\nNEXT: In NEW conversation, process each meeting:")
    print(f"  1. Read B31 file")
    print(f"  2. Extract insights (title, category, signal, evidence, why_it_matters, etc)")
    print(f"  3. INSERT into database: {DB_PATH}")
    
    return 0

if __name__ == "__main__":
    exit(main())

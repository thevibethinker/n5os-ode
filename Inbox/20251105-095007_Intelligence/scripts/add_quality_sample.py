#!/usr/bin/env python3
"""
Add Quality Sample to Database

Usage:
    python3 add_quality_sample.py --block-id B01 --type baseline --input-file input.json --output-file expected.md
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/home/workspace/Intelligence/blocks.db")

def add_quality_sample(
    block_id: str,
    meeting_id: str,
    sample_type: str,
    input_snapshot: dict,
    output_snapshot: str,
    notes: str = None,
    validation_score: float = None
) -> int:
    """Add a quality sample to the database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verify block exists
    cursor.execute("SELECT block_id FROM blocks WHERE block_id = ?", (block_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError(f"Block {block_id} not found in database")
    
    # Insert sample
    cursor.execute("""
        INSERT INTO quality_samples 
        (block_id, meeting_id, sample_type, input_snapshot, output_snapshot, 
         validation_score, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        block_id,
        meeting_id,
        sample_type,
        json.dumps(input_snapshot),
        output_snapshot,
        validation_score,
        notes,
        datetime.now().isoformat()
    ))
    
    sample_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return sample_id

def main():
    parser = argparse.ArgumentParser(description="Add quality sample to database")
    parser.add_argument("--block-id", required=True, help="Block ID (e.g., B01)")
    parser.add_argument("--meeting-id", required=True, help="Meeting ID or synthetic ID")
    parser.add_argument("--type", required=True, choices=["baseline", "edge_case", "regression"],
                       help="Sample type")
    parser.add_argument("--input-file", required=True, help="Path to input JSON file")
    parser.add_argument("--output-file", required=True, help="Path to expected output file")
    parser.add_argument("--score", type=float, help="Initial validation score (0.0-1.0)")
    parser.add_argument("--notes", help="Notes about this sample")
    
    args = parser.parse_args()
    
    # Load input
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    with open(input_path) as f:
        input_snapshot = json.load(f)
    
    # Load expected output
    output_path = Path(args.output_file)
    if not output_path.exists():
        print(f"Error: Output file not found: {output_path}")
        return 1
    
    with open(output_path) as f:
        output_snapshot = f.read()
    
    # Add sample
    try:
        sample_id = add_quality_sample(
            block_id=args.block_id,
            meeting_id=args.meeting_id,
            sample_type=args.type,
            input_snapshot=input_snapshot,
            output_snapshot=output_snapshot,
            notes=args.notes,
            validation_score=args.score
        )
        print(f"✅ Added quality sample #{sample_id} for {args.block_id}")
        print(f"   Type: {args.type}")
        print(f"   Meeting: {args.meeting_id}")
        if args.score:
            print(f"   Score: {args.score}")
        return 0
        
    except Exception as e:
        print(f"❌ Error adding sample: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

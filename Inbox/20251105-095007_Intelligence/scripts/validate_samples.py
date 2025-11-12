#!/usr/bin/env python3
"""
Quick Sample Validator

Validates that quality samples exist and are accessible.
Lighter weight than full regression tests.

Usage:
    python3 validate_samples.py
"""

import sqlite3
import json
import sys
from pathlib import Path

DB_PATH = "/home/workspace/Intelligence/blocks.db"

def validate_samples():
    """Validate all quality samples exist and are loadable."""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 70)
    print("QUALITY SAMPLE VALIDATION")
    print("=" * 70)
    print()
    
    # Get all samples
    cursor.execute("""
        SELECT sample_id, block_id, sample_type, meeting_id, 
               input_snapshot, output_snapshot, validation_score, notes
        FROM quality_samples
        ORDER BY sample_id
    """)
    
    samples = cursor.fetchall()
    total = len(samples)
    passed = 0
    failed = 0
    
    print(f"Found {total} quality samples\n")
    
    for sample in samples:
        sample_id = sample['sample_id']
        block_id = sample['block_id']
        sample_type = sample['sample_type']
        meeting_id = sample['meeting_id']
        
        # Validate input data
        try:
            input_data = json.loads(sample['input_snapshot']) if sample['input_snapshot'] else None
            input_valid = input_data is not None and 'transcript' in input_data
        except:
            input_valid = False
        
        # Validate expected output
        expected_output = sample['output_snapshot']
        output_valid = expected_output and len(expected_output) > 100
        
        # Validate score
        score = sample['validation_score']
        score_valid = score and 0 <= score <= 1
        
        # Overall validation
        is_valid = input_valid and output_valid and score_valid
        
        if is_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
            
        print(f"{status} Sample #{sample_id} - {block_id} ({sample_type})")
        print(f"   Meeting: {meeting_id}")
        print(f"   Score: {score}")
        
        if not is_valid:
            issues = []
            if not input_valid:
                issues.append("Invalid input data")
            if not output_valid:
                issues.append("Invalid expected output")
            if not score_valid:
                issues.append("Invalid score")
            print(f"   Issues: {', '.join(issues)}")
        
        print()
    
    conn.close()
    
    # Summary
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Samples:  {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Pass Rate:      {(passed/total*100) if total > 0 else 0:.1f}%")
    print()
    
    # Coverage analysis
    print("=" * 70)
    print("COVERAGE ANALYSIS")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Blocks with samples
    cursor.execute("""
        SELECT b.block_id, b.name, COUNT(qs.sample_id) as sample_count
        FROM blocks b
        LEFT JOIN quality_samples qs ON b.block_id = qs.block_id
        WHERE b.block_id != 'B99'
        GROUP BY b.block_id, b.name
        HAVING sample_count > 0
        ORDER BY b.block_number
    """)
    
    covered = cursor.fetchall()
    print(f"\nBlocks with samples: {len(covered)}")
    for row in covered:
        print(f"  {row[0]} - {row[1]}: {row[2]} samples")
    
    # Blocks without samples
    cursor.execute("""
        SELECT b.block_id, b.name
        FROM blocks b
        LEFT JOIN quality_samples qs ON b.block_id = qs.block_id
        WHERE qs.sample_id IS NULL AND b.block_id != 'B99'
        ORDER BY b.block_number
        LIMIT 10
    """)
    
    uncovered = cursor.fetchall()
    if uncovered:
        print(f"\nBlocks without samples (showing first 10):")
        for row in uncovered:
            print(f"  {row[0]} - {row[1]}")
    
    conn.close()
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(validate_samples())

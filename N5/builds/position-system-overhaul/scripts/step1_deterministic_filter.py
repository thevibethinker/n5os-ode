#!/usr/bin/env python3
"""
Step 1: Deterministic Pre-Filter
Identifies verbatim dupes and same-source dupes without LLM calls.
"""
import json
import sqlite3
import re
from pathlib import Path
from collections import defaultdict

CAND_PATH = Path('/home/workspace/N5/data/position_candidates.jsonl')
DB_PATH = Path('/home/workspace/N5/data/positions.db')
OUTPUT_DIR = Path('/home/workspace/N5/builds/position-system-overhaul')

def normalize(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_source_meeting(candidate: dict) -> str:
    """Extract source meeting identifier from candidate."""
    # Try various fields where source might be stored
    source = candidate.get('source_meeting') or candidate.get('source_conversation') or ''
    if not source:
        # Try to extract from ID
        cid = candidate.get('id', '')
        # Format: cand_20251228_2025-12-23_rochelmycareerspancom_001
        parts = cid.split('_')
        if len(parts) >= 4:
            source = '_'.join(parts[2:-1])  # e.g., "2025-12-23_rochelmycareerspancom"
    return source

def main():
    # Load approved candidates
    candidates = []
    with open(CAND_PATH) as f:
        for line in f:
            obj = json.loads(line)
            if obj.get('status') == 'approved':
                candidates.append(obj)
    
    print(f"Loaded {len(candidates)} approved candidates")
    
    # Load existing positions
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    positions = [dict(r) for r in conn.execute("SELECT * FROM positions").fetchall()]
    conn.close()
    
    print(f"Loaded {len(positions)} existing positions")
    
    # Build lookup indexes
    # 1. Normalized insight → position IDs
    insight_to_positions = defaultdict(list)
    for p in positions:
        norm_insight = normalize(p.get('insight', ''))
        if norm_insight:
            insight_to_positions[norm_insight].append(p['id'])
    
    # 2. Source meeting → position IDs (from source_conversations field)
    source_to_positions = defaultdict(list)
    for p in positions:
        sources = p.get('source_conversations') or ''
        # Could be JSON array or comma-separated
        try:
            source_list = json.loads(sources) if sources.startswith('[') else [s.strip() for s in sources.split(',') if s.strip()]
        except:
            source_list = [sources] if sources else []
        for src in source_list:
            if src:
                source_to_positions[src].append(p['id'])
    
    # Categorize candidates
    verbatim_dupes = []  # Same text exactly
    source_dupes = []     # Same source meeting already promoted
    ambiguous = []        # Need LLM review
    
    for cand in candidates:
        cand_id = cand.get('id', 'unknown')
        cand_insight = normalize(cand.get('insight', ''))
        cand_source = extract_source_meeting(cand)
        
        # Check 1: Verbatim text match
        if cand_insight and cand_insight in insight_to_positions:
            matched_pos_ids = insight_to_positions[cand_insight]
            verbatim_dupes.append({
                'candidate_id': cand_id,
                'candidate_insight': cand.get('insight', '')[:200],
                'matched_position_ids': matched_pos_ids,
                'reason': 'verbatim_text_match'
            })
            continue
        
        # Check 2: Same source meeting already has positions
        # (This is informational - still needs semantic check)
        source_match = False
        if cand_source and cand_source in source_to_positions:
            source_match = True
            # Don't auto-dupe, but flag it
        
        # If not verbatim, goes to ambiguous pile
        ambiguous.append({
            'candidate_id': cand_id,
            'candidate': cand,
            'source_meeting': cand_source,
            'has_source_overlap': source_match,
            'overlapping_position_ids': source_to_positions.get(cand_source, []) if source_match else []
        })
    
    # Output results
    results = {
        'verbatim_dupes': verbatim_dupes,
        'ambiguous': ambiguous,
        'summary': {
            'total_approved': len(candidates),
            'verbatim_dupes': len(verbatim_dupes),
            'ambiguous': len(ambiguous),
            'ambiguous_with_source_overlap': sum(1 for a in ambiguous if a['has_source_overlap'])
        }
    }
    
    output_path = OUTPUT_DIR / 'step1_filter_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== STEP 1 RESULTS ===")
    print(f"Verbatim dupes (auto-mark): {len(verbatim_dupes)}")
    print(f"Ambiguous (need LLM review): {len(ambiguous)}")
    print(f"  - With source overlap: {results['summary']['ambiguous_with_source_overlap']}")
    print(f"\nSaved to {output_path}")
    
    # Also output ambiguous queue for Step 2
    queue_path = OUTPUT_DIR / 'step2_merge_queue.json'
    with open(queue_path, 'w') as f:
        json.dump(ambiguous, f, indent=2)
    print(f"Merge queue saved to {queue_path}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Decay Detector: "What have I abandoned without deciding to?"

Identifies active edges not touched in 90+ days to find:
- Ideas/decisions that may have been implicitly abandoned
- Candidates for revival vs. formal closure
- Patterns in what V tends to abandon

Usage:
    python3 decay_detector.py [--days 90] [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report, format_edges_table


ANALYSIS_PROMPT = """You are identifying abandoned ideas/decisions that were never explicitly closed.

V's context graph has many ideas, decisions, and commitments. Some remain marked "active" even though they may have been implicitly dropped. This analysis identifies stale items that deserve attention.

**Active edges not touched in {days}+ days:**

{edges_table}

**Note:** These edges are still marked "active" but haven't been referenced or updated recently. They may represent:
- Forgotten commitments
- Ideas that fizzled out naturally
- Decisions that were superseded in practice but not in the graph
- Things that are still relevant but dormant

**Analysis Tasks:**

1. **Categorize Each Stale Edge:**
   - **Revival candidate**: Still relevant, worth revisiting
   - **Closure candidate**: Implicitly dead, should be formally archived
   - **Legitimately dormant**: Fine to remain active, just not urgent

2. **Identify Abandonment Patterns:**
   - What types of things does V tend to let decay? (Ideas? Commitments? Relationships?)
   - Are there domains with higher abandonment rates?
   - Is there a pattern in timing (e.g., things from busy periods)?

3. **Assess Impact:**
   - Are any of these abandoned items linked to active goals?
   - Are there orphaned dependencies (things depending on decayed items)?

4. **Prioritize Revival/Closure:**
   - Which items are highest priority to address?
   - What's the cost of leaving them in limbo?

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview: How much decay is there? Is it concerning?]

## Candidates for Revival
[Ideas/decisions worth bringing back to active consideration]

| Item | Type | Last Touched | Why Revive |
|------|------|--------------|------------|
[Table of revival candidates]

## Candidates for Closure
[Things that should be formally marked superseded/reversed]

| Item | Type | Last Touched | Why Close |
|------|------|--------------|-----------|
[Table of closure candidates]

## Abandonment Patterns
[Analysis of what V tends to let decay and why]

## Recommendations
[Specific actions V should take]

---
Analysis Date: {date}
Stale Edge Count: {edge_count}
Days Threshold: {days}
"""


def main():
    parser = argparse.ArgumentParser(description="Decay Detector: Find abandoned ideas")
    parser.add_argument("--days", type=int, default=90, 
                       help="Consider edges older than N days as stale (default: 90)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be analyzed without calling LLM")
    args = parser.parse_args()
    
    print(f"Decay Detector: Finding edges not updated in {args.days}+ days")
    
    # Calculate cutoff date
    cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    # Query stale active edges
    edges = query_edges(f"""
        SELECT 
            id, source_type, source_id, relation, 
            target_type, target_id, evidence,
            context_meeting_id, captured_at, updated_at,
            status
        FROM edges 
        WHERE status = 'active'
        AND date(captured_at) < date('{cutoff}')
        AND (updated_at IS NULL OR date(updated_at) < date('{cutoff}'))
        ORDER BY captured_at ASC
    """)
    
    if not edges:
        print(f"No stale edges found (all active edges updated within {args.days} days).")
        print("This suggests either good graph hygiene or a young graph.")
        
        if args.dry_run:
            return
            
        content = f"""# Decay Detector

## Summary

No edges have decayed beyond the {args.days}-day threshold.

This indicates:
1. **Active graph maintenance**: Edges are being regularly reviewed/updated
2. **Young graph**: Most edges are recent enough not to trigger decay detection
3. **Different threshold needed**: Consider running with `--days 60` or `--days 30`

## Recommendation

Run decay detection again in 30 days, or lower the threshold to catch earlier decay signals.
"""
        report_path = write_report("decay_detector", content)
        print(f"\n✓ Report written: {report_path}")
        return
    
    print(f"Found {len(edges)} stale edges (not touched since {cutoff})")
    
    # Format edges table
    edges_table = format_edges_table(edges, [
        "id", "source_type", "source_id", "relation", "target_id", 
        "evidence", "captured_at"
    ])
    
    if args.dry_run:
        print("\n--- DRY RUN: Would analyze these edges ---")
        print(edges_table)
        print("\n--- End dry run ---")
        return
    
    # Build prompt
    prompt = ANALYSIS_PROMPT.format(
        edges_table=edges_table,
        date=datetime.now().strftime("%Y-%m-%d"),
        edge_count=len(edges),
        days=args.days
    )
    
    print("Sending to LLM for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        content = f"# Decay Detector\n\n{analysis}"
        
        report_path = write_report("decay_detector", content)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


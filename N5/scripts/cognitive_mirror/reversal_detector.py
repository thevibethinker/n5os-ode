#!/usr/bin/env python3
"""
Reversal Detector: "Where am I inconsistent, and is that good or bad?"

Analyzes edges marked 'superseded' or 'reversed' to identify:
- Healthy evolution vs. concerning flip-flops
- Domains where thinking is most/least stable
- Patterns in what triggers reversals

Usage:
    python3 reversal_detector.py [--include-active] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report, format_edges_table


ANALYSIS_PROMPT = """You are analyzing V's intellectual consistency to help him understand his thinking evolution.

V's context graph tracks when ideas or decisions are superseded or reversed. This data shows where his thinking has changed over time.

**Edges that were superseded or reversed:**

{edges_table}

**Edge Status Meanings:**
- `superseded`: Replaced by a newer/better idea (evolution)
- `reversed`: Explicitly contradicted or walked back (reversal)
- `reversal_reason`: V's stated reason for the change (if recorded)

**Analysis Tasks:**

1. **Cluster by Semantic Topic:**
   - Group these changes by what domain they relate to (product, GTM, technical, personal, etc.)
   - Identify if there are areas with high churn

2. **Classify Each Change:**
   - **Healthy evolution**: New information arrived, thinking matured, context changed appropriately
   - **Concerning pattern**: Same ground being re-litigated, indecision, flip-flopping without resolution

3. **Look for Triggers:**
   - What seems to precipitate changes? External feedback? New data? Pressure?
   - Are reversals happening quickly (within days) or over longer periods?

4. **Domain Stability Analysis:**
   - Where is V's thinking most stable (few changes)?
   - Where is it most volatile (many changes)?
   - Is volatility in any domain a red flag or appropriate given uncertainty?

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview: How consistent is V's thinking? Is the change rate concerning?]

## Healthy Pivots
[List changes that represent genuine growth or appropriate adaptation]

## Concerning Patterns  
[List any flip-flops, repeated reversals on same topics, or signs of indecision]

## Domain Stability Analysis
| Domain | Stability | Notes |
|--------|-----------|-------|
[Table of domains with stability assessment]

## Recommendations
[How V might improve decision quality or reduce unnecessary churn]

---
Analysis Date: {date}
Total Changes Analyzed: {edge_count}
"""


def main():
    parser = argparse.ArgumentParser(description="Reversal Detector: Analyze thinking consistency")
    parser.add_argument("--include-active", action="store_true", 
                       help="Also include active edges to provide context")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be analyzed without calling LLM")
    args = parser.parse_args()
    
    print("Reversal Detector: Analyzing superseded and reversed edges")
    
    # Query superseded/reversed edges
    changed_edges = query_edges("""
        SELECT 
            id, source_type, source_id, relation, 
            target_type, target_id, evidence,
            context_meeting_id, captured_at,
            status, superseded_by, reversed_at, reversal_reason
        FROM edges 
        WHERE status IN ('superseded', 'reversed')
        ORDER BY captured_at DESC
    """)
    
    if not changed_edges:
        # Even with no reversals, that's a finding
        print("No superseded or reversed edges found.")
        print("This suggests high consistency—or that reversals haven't been tracked yet.")
        
        if args.dry_run:
            return
            
        # Generate a brief report noting the finding
        content = """# Reversal Detector

## Summary

No edges have been marked as `superseded` or `reversed` in the context graph.

This could indicate:
1. **High consistency**: V's positions and decisions have remained stable
2. **Incomplete tracking**: Reversals may have occurred but not been recorded
3. **Early stage**: Not enough time has passed for significant changes

## Recommendation

As the context graph matures, consider:
- Actively marking edges as superseded when thinking evolves
- Recording reversal reasons to track what triggers changes
- Running this analysis again after 30+ days of edge accumulation
"""
        report_path = write_report("reversal_detector", content)
        print(f"\n✓ Report written: {report_path}")
        return
    
    print(f"Found {len(changed_edges)} changed edges")
    
    # Format edges
    edges_table = format_edges_table(changed_edges, [
        "id", "source_id", "relation", "target_id",
        "evidence", "status", "reversal_reason", "captured_at"
    ])
    
    # Optionally include some active edges for context
    context_section = ""
    if args.include_active:
        active_edges = query_edges("""
            SELECT id, source_id, relation, target_id, evidence, status
            FROM edges WHERE status = 'active'
            LIMIT 20
        """)
        if active_edges:
            context_section = f"\n\n**Sample of currently active edges for context:**\n\n{format_edges_table(active_edges)}"
    
    if args.dry_run:
        print("\n--- DRY RUN: Would analyze these edges ---")
        print(edges_table)
        if context_section:
            print(context_section)
        print("\n--- End dry run ---")
        return
    
    # Build prompt
    from datetime import datetime
    prompt = ANALYSIS_PROMPT.format(
        edges_table=edges_table + context_section,
        date=datetime.now().strftime("%Y-%m-%d"),
        edge_count=len(changed_edges)
    )
    
    print("Sending to LLM for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        content = f"# Reversal Detector\n\n{analysis}"
        
        report_path = write_report("reversal_detector", content)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


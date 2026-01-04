#!/usr/bin/env python3
"""
Decision Retrospective: "Did what I hoped/feared actually happen?"

Analyzes predictions (hoped_for, concerned_about edges) to identify:
- Predictions needing closure (no outcome linked)
- Patterns in prediction accuracy
- Domains where V is over/under-optimistic

Usage:
    python3 decision_retrospective.py [--days 90] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report, format_edges_table, get_edge_summary


ANALYSIS_PROMPT = """You are analyzing V's past predictions to identify patterns in his forecasting accuracy.

V makes predictions in meetings, captured as "hoped_for" (optimistic expectations) and "concerned_about" (risks/worries) edges in his context graph.

Given these edges representing V's hopes and concerns from meetings:

{edges_table}

**Analysis Tasks:**

1. **Categorize Each Prediction:**
   - For each edge, assess: Is this still an open prediction, or has time passed enough that we can evaluate it?
   - Note that "outcome_status" field shows if V explicitly recorded a result (validated/invalidated)
   - Many predictions won't have explicit outcomes—use your judgment on implicit resolution

2. **Identify Predictions Needing Closure:**
   - Which predictions are old enough that V should explicitly close the loop?
   - Which are still reasonably open/pending?

3. **Pattern Analysis:**
   - What types of predictions does V make? (Timeline, outcome, relationship, technical, etc.)
   - For any with known outcomes, is there a pattern in accuracy?
   - Are there domains where V tends toward optimism vs. pessimism?

4. **Recommendations:**
   - Specific predictions V should revisit and formally close
   - Suggestions for improving prediction quality

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview of findings]

## Predictions Needing Closure
[List predictions that are old and should be formally resolved]

## Patterns Observed
[Analysis of prediction types and any accuracy patterns]

## Recommendations
[Actionable suggestions]

---
Analysis Date: {date}
Edge Count: {edge_count}
"""


def main():
    parser = argparse.ArgumentParser(description="Decision Retrospective: Analyze prediction accuracy")
    parser.add_argument("--days", type=int, default=90, help="Look back N days (default: 90)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be analyzed without calling LLM")
    args = parser.parse_args()
    
    print(f"Decision Retrospective: Analyzing predictions from last {args.days}+ days")
    
    # Query predictions (hoped_for, concerned_about)
    edges = query_edges(f"""
        SELECT 
            id, source_type, source_id, relation, 
            target_type, target_id, evidence,
            context_meeting_id, captured_at,
            status, outcome_status, outcome_note
        FROM edges 
        WHERE relation IN ('hoped_for', 'concerned_about')
        AND status = 'active'
        ORDER BY captured_at ASC
    """)
    
    if not edges:
        print("No prediction edges (hoped_for, concerned_about) found.")
        print("This analysis requires edges with these relations.")
        return
    
    print(f"Found {len(edges)} prediction edges")
    
    # Format for display
    edges_table = format_edges_table(edges, [
        "id", "relation", "source_id", "target_id", 
        "evidence", "outcome_status", "captured_at"
    ])
    
    if args.dry_run:
        print("\n--- DRY RUN: Would analyze these edges ---")
        print(edges_table)
        print("\n--- End dry run ---")
        return
    
    # Build prompt
    from datetime import datetime
    prompt = ANALYSIS_PROMPT.format(
        edges_table=edges_table,
        date=datetime.now().strftime("%Y-%m-%d"),
        edge_count=len(edges)
    )
    
    print("Sending to LLM for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        # Prepend title
        content = f"# Decision Retrospective\n\n{analysis}"
        
        # Write report
        report_path = write_report("decision_retrospective", content)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


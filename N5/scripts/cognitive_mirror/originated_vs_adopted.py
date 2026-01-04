#!/usr/bin/env python3
"""
Originated vs Adopted: "Do my ideas stick better than others'?"

Compares ideas V originated vs ideas he adopted from others:
- Survival rates (still active vs superseded/reversed)
- Domain differences
- Quality signals

Usage:
    python3 originated_vs_adopted.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report, format_edges_table


ANALYSIS_PROMPT = """You are comparing V's originated ideas versus ideas he adopted from others.

This analysis helps V understand whether he's better at generating ideas or curating ideas from others.

**Ideas V originated (has "originated_by: person:vrijen" or similar):**

{originated_table}

**Ideas originated by others (adopted by V):**

{adopted_table}

**Status Summary:**
- V-originated ideas: {v_total} total, {v_active} active, {v_changed} superseded/reversed
- Others-originated ideas: {other_total} total, {other_active} active, {other_changed} superseded/reversed

**Analysis Tasks:**

1. **Calculate Survival Rates:**
   - What % of V's originated ideas remain active vs. were changed?
   - What % of adopted ideas remain active vs. were changed?
   - Which source has better "stickiness"?

2. **Domain Analysis:**
   - Are there domains where V's ideas dominate (product? strategy?)?
   - Are there domains where others' ideas dominate (technical? market?)?

3. **Quality Signals:**
   - Do adopted ideas tend to have more supporting evidence?
   - Do V's ideas tend to be more or less validated by outcomes?

4. **Strategic Implications:**
   - Should V lean more into ideation or curation?
   - What does this say about his cognitive strengths?

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview: Is V better at generating or curating ideas?]

## Origination Breakdown

| Source | Total | Active | Changed | Survival Rate |
|--------|-------|--------|---------|---------------|
| V-originated | {v_total} | {v_active} | {v_changed} | [calc]% |
| Others-originated | {other_total} | {other_active} | {other_changed} | [calc]% |

## Survival Analysis
[Deeper analysis of what survives and why]

## Domain Comparison
[Where V's vs others' ideas dominate]

## Strategic Implications
[What this means for V's approach]

## Recommendations
[How V might optimize his ideation vs. curation balance]

---
Analysis Date: {date}
"""


def main():
    parser = argparse.ArgumentParser(description="Originated vs Adopted: Compare idea sources")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be analyzed without calling LLM")
    args = parser.parse_args()
    
    print("Originated vs Adopted: Analyzing idea origination patterns")
    
    # Get all edges with origination info
    all_originated = query_edges("""
        SELECT 
            e1.id, e1.source_type, e1.source_id, e1.status,
            e1.evidence, e1.captured_at,
            e2.target_id as originator
        FROM edges e1
        LEFT JOIN edges e2 ON e1.source_type = e2.source_type 
                          AND e1.source_id = e2.source_id 
                          AND e2.relation = 'originated_by'
        WHERE e1.source_type IN ('idea', 'decision', 'position')
        AND e1.relation != 'originated_by'
        ORDER BY e1.source_type, e1.source_id
    """)
    
    # Also get direct originated_by edges
    originated_edges = query_edges("""
        SELECT 
            id, source_type, source_id, target_id as originator,
            evidence, status, captured_at
        FROM edges 
        WHERE relation = 'originated_by'
        AND status = 'active'
    """)
    
    if not originated_edges:
        print("No originated_by edges found.")
        print("This analysis requires edges tracking who originated ideas.")
        return
    
    print(f"Found {len(originated_edges)} originated_by edges")
    
    # Categorize by originator
    v_originated = []
    other_originated = []
    
    v_names = {"vrijen", "v", "vrijen-attawar"}  # Common V identifiers
    
    for edge in originated_edges:
        originator = edge.get("originator", "").lower()
        if any(v in originator for v in v_names):
            v_originated.append(edge)
        else:
            other_originated.append(edge)
    
    # Count statuses
    def count_statuses(edges):
        active = sum(1 for e in edges if e.get("status") == "active")
        changed = len(edges) - active
        return len(edges), active, changed
    
    v_total, v_active, v_changed = count_statuses(v_originated)
    other_total, other_active, other_changed = count_statuses(other_originated)
    
    print(f"  V-originated: {v_total} ({v_active} active)")
    print(f"  Others-originated: {other_total} ({other_active} active)")
    
    # Format tables
    originated_table = format_edges_table(v_originated, [
        "source_type", "source_id", "evidence", "status", "captured_at"
    ]) if v_originated else "*No V-originated ideas tracked*"
    
    adopted_table = format_edges_table(other_originated, [
        "source_type", "source_id", "originator", "evidence", "status", "captured_at"
    ]) if other_originated else "*No others-originated ideas tracked*"
    
    if args.dry_run:
        print("\n--- DRY RUN: Would analyze these edges ---")
        print("\nV-originated:")
        print(originated_table)
        print("\nOthers-originated:")
        print(adopted_table)
        print("\n--- End dry run ---")
        return
    
    # Build prompt
    from datetime import datetime
    prompt = ANALYSIS_PROMPT.format(
        originated_table=originated_table,
        adopted_table=adopted_table,
        v_total=v_total, v_active=v_active, v_changed=v_changed,
        other_total=other_total, other_active=other_active, other_changed=other_changed,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    print("Sending to LLM for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        content = f"# Originated vs Adopted\n\n{analysis}"
        
        report_path = write_report("originated_vs_adopted", content)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Influence Map: "Who shapes my thinking, and in what domains?"

Analyzes originated_by and influenced_by edges to identify:
- Top intellectual influences (by ideas adopted)
- Who challenges V effectively
- Echo chamber risks
- Underutilized perspectives

Usage:
    python3 influence_map.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report, format_edges_table


ANALYSIS_PROMPT = """You are mapping who shapes V's thinking across different domains.

V's context graph tracks idea origination and influence through these edge types:
- `originated_by`: Who came up with an idea first
- `influenced_by`: Who shaped V's thinking on something
- `challenged_by`: Who pushed back or offered a counterpoint
- `supported_by`: Who validated or reinforced an idea

**Edges showing idea origination and influence:**

{edges_table}

**Person Summary:**
{person_summary}

**Analysis Tasks:**

1. **Identify Top Influencers:**
   - Who has originated or influenced the most ideas that V holds?
   - Rank by frequency and note their apparent domains of influence

2. **Map Effective Challengers:**
   - Who has challenged V's ideas (challenged_by edges)?
   - Are challenges from diverse perspectives or same voices?

3. **Echo Chamber Assessment:**
   - Is V getting ideas from a narrow set of people?
   - Are challengers well-represented or underrepresented?
   - Are there domains with only one influence source?

4. **Identify Gaps:**
   - What perspectives might be underrepresented?
   - Are there domains where V might benefit from more diverse input?

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview of V's intellectual influence landscape]

## Top Influencers

| Person | Ideas Originated/Influenced | Primary Domains |
|--------|----------------------------|-----------------|
[Ranked table of top 5-10 influencers]

## Effective Challengers
[Who pushes back? On what topics?]

## Echo Chamber Risk Assessment
[Analysis of diversity/concentration of influences]

## Underutilized Perspectives
[Suggestions for where V might seek broader input]

## Recommendations
[Actionable suggestions for diversifying intellectual inputs]

---
Analysis Date: {date}
Total Influence Edges: {edge_count}
Unique People Referenced: {person_count}
"""


def main():
    parser = argparse.ArgumentParser(description="Influence Map: Who shapes V's thinking?")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be analyzed without calling LLM")
    args = parser.parse_args()
    
    print("Influence Map: Analyzing intellectual influences")
    
    # Query influence-related edges
    edges = query_edges("""
        SELECT 
            id, source_type, source_id, relation, 
            target_type, target_id, evidence,
            context_meeting_id, captured_at
        FROM edges 
        WHERE relation IN ('originated_by', 'influenced_by', 'challenged_by', 'supported_by')
        AND status = 'active'
        ORDER BY relation, target_id
    """)
    
    if not edges:
        print("No influence-related edges found (originated_by, influenced_by, challenged_by, supported_by).")
        print("This analysis requires edges with these relations.")
        return
    
    print(f"Found {len(edges)} influence-related edges")
    
    # Build person summary (aggregate stats)
    person_stats: dict[str, dict] = defaultdict(lambda: {
        "originated": 0, "influenced": 0, "challenged": 0, "supported": 0, "domains": set()
    })
    
    for edge in edges:
        # Person is usually the target for these relations
        if edge["target_type"] == "person":
            person = edge["target_id"]
            if edge["relation"] == "originated_by":
                person_stats[person]["originated"] += 1
            elif edge["relation"] == "influenced_by":
                person_stats[person]["influenced"] += 1
            elif edge["relation"] == "challenged_by":
                person_stats[person]["challenged"] += 1
            elif edge["relation"] == "supported_by":
                person_stats[person]["supported"] += 1
            
            # Track domain from source type
            person_stats[person]["domains"].add(edge["source_type"])
    
    # Format person summary
    person_lines = []
    for person, stats in sorted(person_stats.items(), 
                                key=lambda x: -(x[1]["originated"] + x[1]["influenced"])):
        total = stats["originated"] + stats["influenced"]
        domains = ", ".join(stats["domains"]) if stats["domains"] else "unknown"
        person_lines.append(
            f"- **{person}**: {stats['originated']} originated, {stats['influenced']} influenced, "
            f"{stats['challenged']} challenged, {stats['supported']} supported (domains: {domains})"
        )
    
    person_summary = "\n".join(person_lines) if person_lines else "*No person-targeted edges found*"
    
    # Format edges table
    edges_table = format_edges_table(edges, [
        "relation", "source_type", "source_id", "target_id", "evidence", "captured_at"
    ])
    
    if args.dry_run:
        print("\n--- DRY RUN: Would analyze these edges ---")
        print(edges_table)
        print("\n--- Person Summary ---")
        print(person_summary)
        print("\n--- End dry run ---")
        return
    
    # Build prompt
    from datetime import datetime
    prompt = ANALYSIS_PROMPT.format(
        edges_table=edges_table,
        person_summary=person_summary,
        date=datetime.now().strftime("%Y-%m-%d"),
        edge_count=len(edges),
        person_count=len(person_stats)
    )
    
    print("Sending to LLM for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        content = f"# Influence Map\n\n{analysis}"
        
        report_path = write_report("influence_map", content)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


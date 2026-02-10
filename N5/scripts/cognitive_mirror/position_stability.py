#!/usr/bin/env python3
"""
Position Stability Analysis: "Which beliefs have evidence? Which are contested?"

Analyzes positions by their edge support to identify:
- Well-supported positions (strong evidence base)
- Contested positions (both support and challenge)
- Unvalidated positions (lacking recent evidence)
- Stability recommendations (upgrade/downgrade candidates)

Usage:
    python3 position_stability.py [--days 90] [--dry-run]
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _base import query_edges, ask_zo, write_report

# Paths
POSITIONS_DB = Path(__file__).parent.parent.parent / "data" / "positions.db"
EDGES_DB = Path("/home/workspace/N5/cognition/brain.db")


ANALYSIS_PROMPT = """You are analyzing V's documented positions (beliefs, insights, worldview) by examining their evidential support in the context graph.

Positions have a "stability" level:
- **canonical**: Core beliefs, rarely change
- **stable**: Well-established, supported by evidence
- **working**: Active hypotheses, open to revision
- **emerging**: New observations, not yet validated

**Position-Edge Analysis:**

{positions_with_edges}

**Analysis Tasks:**

1. **WELL-SUPPORTED** (recommend stability upgrade):
   - Which positions have 3+ supporting edges and 0-1 challenges?
   - Which "working" or "emerging" positions have enough evidence to become "stable"?

2. **CONTESTED** (needs V's attention):
   - Which positions have both supporting AND challenging evidence?
   - What's the nature of the contestation? (Different contexts? Evolving view? Genuine conflict?)

3. **UNVALIDATED** (may be stale):
   - Which positions have <2 supporting edges total?
   - Which haven't been validated by evidence in the last {days} days?
   - Should any be demoted from "stable" to "working"?

4. **RECOMMENDATIONS**:
   - Specific stability upgrades/downgrades
   - Positions V should revisit and either reinforce or retire
   - Gaps where V has intuitions but no documented positions

**Output Format (Markdown):**

## Summary
[1-2 paragraph overview of V's belief-evidence alignment]

## Well-Supported Positions
[Positions with strong evidence, candidates for upgrade]

## Contested Positions  
[Positions with conflicting evidence, need attention]

## Unvalidated Positions
[Positions lacking recent evidence, candidates for review]

## Stability Recommendations
| Position | Current | Recommended | Reason |
|----------|---------|-------------|--------|

## Insights
[Patterns in V's belief system, blind spots, areas of growth]

---
Analysis Date: {date}
Positions Analyzed: {position_count}
Edges Examined: {edge_count}
Lookback Period: {days} days
"""


def get_positions() -> list[dict]:
    """Get all positions from positions.db"""
    conn = sqlite3.connect(str(POSITIONS_DB))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, domain, title, insight, stability, confidence, 
                   created_at, last_refined
            FROM positions
            ORDER BY domain, stability DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_position_edges(days: int = 90) -> dict[str, list[dict]]:
    """
    Get edges that reference positions (supports/challenges/crystallized_from).
    
    Returns dict: position_id -> list of edges
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    edges = query_edges(f"""
        SELECT 
            e.id,
            e.source_type,
            e.source_id,
            e.relation,
            e.target_type,
            e.target_id,
            e.evidence,
            e.context_meeting_id,
            e.created_at,
            src.name as source_name,
            tgt.name as target_name
        FROM edges e
        LEFT JOIN entities src ON e.source_type = src.entity_type AND e.source_id = src.entity_id
        LEFT JOIN entities tgt ON e.target_type = tgt.entity_type AND e.target_id = tgt.entity_id
        WHERE (e.target_type = 'position' OR e.source_type = 'position')
        AND e.status = 'active'
        ORDER BY e.created_at DESC
    """)
    
    # Group by position
    position_edges = defaultdict(list)
    for edge in edges:
        if edge['target_type'] == 'position':
            position_edges[edge['target_id']].append({
                **edge,
                'direction': 'incoming',
                'stance': 'support' if edge['relation'] == 'supports_position' else 
                          'challenge' if edge['relation'] == 'challenges_position' else 'other'
            })
        elif edge['source_type'] == 'position':
            position_edges[edge['source_id']].append({
                **edge,
                'direction': 'outgoing',
                'stance': 'crystallized' if edge['relation'] == 'crystallized_from' else 'other'
            })
    
    return dict(position_edges)


def format_positions_with_edges(positions: list[dict], position_edges: dict, days: int) -> str:
    """Format positions with their edge support for LLM analysis."""
    lines = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for pos in positions:
        pos_id = pos['id']
        edges = position_edges.get(pos_id, [])
        
        # Count support vs challenge
        support_count = len([e for e in edges if e.get('stance') == 'support'])
        challenge_count = len([e for e in edges if e.get('stance') == 'challenge'])
        recent_edges = [e for e in edges if e.get('created_at') and 
                       datetime.fromisoformat(e['created_at'].replace('Z', '+00:00').replace('+00:00', '')) > cutoff]
        
        lines.append(f"### {pos['title']}")
        lines.append(f"- **ID:** {pos_id}")
        lines.append(f"- **Domain:** {pos['domain']}")
        lines.append(f"- **Stability:** {pos['stability']}")
        lines.append(f"- **Confidence:** {pos.get('confidence', 'N/A')}")
        lines.append(f"- **Created:** {pos.get('created_at', 'unknown')[:10]}")
        lines.append(f"- **Last Refined:** {pos.get('last_refined', 'never')}")
        lines.append(f"- **Edge Support:** {support_count} supporting, {challenge_count} challenging")
        lines.append(f"- **Recent Edges ({days}d):** {len(recent_edges)}")
        
        if edges:
            lines.append(f"- **Edge Details:**")
            for edge in edges[:5]:  # Limit to 5 for context window
                stance_icon = "✓" if edge.get('stance') == 'support' else "✗" if edge.get('stance') == 'challenge' else "→"
                evidence_preview = (edge.get('evidence') or '')[:100]
                lines.append(f"  - {stance_icon} [{edge['relation']}] {evidence_preview}...")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Position Stability Analysis")
    parser.add_argument("--days", type=int, default=90, help="Lookback period in days (default: 90)")
    parser.add_argument("--dry-run", action="store_true", help="Show data without calling LLM")
    parser.add_argument("--domain", type=str, help="Filter to specific domain")
    args = parser.parse_args()
    
    print(f"Position Stability Analysis: Examining belief-evidence alignment")
    print(f"Lookback period: {args.days} days")
    
    # Get data
    positions = get_positions()
    if args.domain:
        positions = [p for p in positions if p['domain'] == args.domain]
    
    position_edges = get_position_edges(args.days)
    
    print(f"Found {len(positions)} positions, {sum(len(v) for v in position_edges.values())} position-related edges")
    
    # Format for analysis
    formatted = format_positions_with_edges(positions, position_edges, args.days)
    
    if args.dry_run:
        print("\n[DRY RUN] Would analyze:\n")
        print(formatted[:3000])
        print(f"\n... ({len(formatted)} chars total)")
        
        # Show quick stats
        print("\n--- Quick Stats ---")
        stability_counts = defaultdict(int)
        for p in positions:
            stability_counts[p['stability']] += 1
        for stability, count in sorted(stability_counts.items()):
            print(f"  {stability}: {count}")
        
        edge_positions = len([p for p in positions if position_edges.get(p['id'])])
        print(f"  Positions with edges: {edge_positions}/{len(positions)}")
        return
    
    # Run LLM analysis
    prompt = ANALYSIS_PROMPT.format(
        positions_with_edges=formatted,
        date=datetime.now().strftime("%Y-%m-%d"),
        position_count=len(positions),
        edge_count=sum(len(v) for v in position_edges.values()),
        days=args.days
    )
    
    print("Calling Zo for analysis...")
    
    try:
        analysis = ask_zo(prompt)
        
        # Write report
        report_path = write_report("position_stability", analysis)
        print(f"\n✓ Report written: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()




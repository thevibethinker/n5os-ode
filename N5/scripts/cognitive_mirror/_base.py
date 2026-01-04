#!/usr/bin/env python3
"""
Cognitive Mirror Base: Shared infrastructure for LLM-powered insight scripts.

Provides:
- query_edges(): Execute SQL against edges.db
- ask_zo(): Call /zo/ask API for semantic reasoning
- write_report(): Save dated Markdown reports
- format_edges_table(): Format edges for LLM context
"""

import os
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

# Paths
DB_PATH = Path(__file__).parent.parent.parent / "data" / "edges.db"
INSIGHTS_DIR = Path(__file__).parent.parent.parent / "insights" / "cognitive_mirror"


def query_edges(sql: str) -> list[dict]:
    """
    Execute SQL against edges.db, return list of dicts.
    
    Args:
        sql: SQL query to execute
        
    Returns:
        List of row dicts
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def ask_zo(prompt: str, context: str = "") -> str:
    """
    Call /zo/ask API for LLM reasoning.
    
    Args:
        prompt: The analysis prompt
        context: Additional context (edge data, etc.)
        
    Returns:
        LLM response text
    """
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set in environment")
    
    full_prompt = f"{prompt}\n\n---\n\n{context}" if context else prompt
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": full_prompt},
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Zo API error {response.status_code}: {response.text}")
    
    return response.json()["output"]


def write_report(script_name: str, content: str, date: Optional[datetime] = None) -> Path:
    """
    Write dated Markdown report to insights directory.
    
    Args:
        script_name: Name of the generating script (for filename)
        content: Markdown content
        date: Date for filename (defaults to today)
        
    Returns:
        Path to created report
    """
    date = date or datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    
    # Ensure directory exists
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"{date_str}_{script_name}.md"
    report_path = INSIGHTS_DIR / filename
    
    # Add frontmatter
    frontmatter = f"""---
created: {date_str}
generated_by: cognitive_mirror/{script_name}.py
version: 1.0
---

"""
    
    report_path.write_text(frontmatter + content)
    return report_path


def format_edges_table(edges: list[dict], columns: Optional[list[str]] = None) -> str:
    """
    Format edges as readable Markdown table for LLM context.
    
    Args:
        edges: List of edge dicts
        columns: Columns to include (defaults to key fields)
        
    Returns:
        Markdown table string
    """
    if not edges:
        return "*No edges to display*"
    
    # Default columns relevant for analysis
    columns = columns or [
        "id", "source_type", "source_id", "relation", 
        "target_type", "target_id", "evidence", "status", "captured_at"
    ]
    
    # Filter to columns that exist in the data
    available_cols = [c for c in columns if c in edges[0]]
    
    # Build header
    header = "| " + " | ".join(available_cols) + " |"
    separator = "| " + " | ".join(["---"] * len(available_cols)) + " |"
    
    # Build rows
    rows = []
    for edge in edges:
        values = []
        for col in available_cols:
            val = edge.get(col, "")
            # Truncate long evidence
            if col == "evidence" and val and len(str(val)) > 80:
                val = str(val)[:77] + "..."
            values.append(str(val) if val is not None else "")
        rows.append("| " + " | ".join(values) + " |")
    
    return "\n".join([header, separator] + rows)


def format_edges_grouped(edges: list[dict], group_by: str = "relation") -> str:
    """
    Format edges grouped by a field, with counts.
    
    Args:
        edges: List of edge dicts
        group_by: Field to group by
        
    Returns:
        Formatted string with groups
    """
    if not edges:
        return "*No edges to display*"
    
    groups: dict[str, list[dict]] = {}
    for edge in edges:
        key = str(edge.get(group_by, "unknown"))
        groups.setdefault(key, []).append(edge)
    
    output = []
    for key, group_edges in sorted(groups.items(), key=lambda x: -len(x[1])):
        output.append(f"\n### {key} ({len(group_edges)} edges)\n")
        output.append(format_edges_table(group_edges))
    
    return "\n".join(output)


def get_edge_summary() -> dict:
    """
    Get summary statistics for current edge database.
    
    Returns:
        Dict with counts and breakdowns
    """
    stats = {}
    
    # Total active
    result = query_edges("SELECT COUNT(*) as cnt FROM edges WHERE status = 'active'")
    stats["total_active"] = result[0]["cnt"] if result else 0
    
    # By relation
    result = query_edges("""
        SELECT relation, COUNT(*) as cnt 
        FROM edges WHERE status = 'active' 
        GROUP BY relation ORDER BY cnt DESC
    """)
    stats["by_relation"] = {r["relation"]: r["cnt"] for r in result}
    
    # By status
    result = query_edges("""
        SELECT status, COUNT(*) as cnt 
        FROM edges 
        GROUP BY status
    """)
    stats["by_status"] = {r["status"]: r["cnt"] for r in result}
    
    # With outcomes
    result = query_edges("""
        SELECT outcome_status, COUNT(*) as cnt 
        FROM edges 
        WHERE outcome_status IS NOT NULL 
        GROUP BY outcome_status
    """)
    stats["outcomes"] = {r["outcome_status"]: r["cnt"] for r in result}
    
    return stats


if __name__ == "__main__":
    # Quick test
    print("Testing _base.py functions...")
    
    stats = get_edge_summary()
    print(f"\nDatabase Stats:")
    print(f"  Total active edges: {stats['total_active']}")
    print(f"  By relation: {stats['by_relation']}")
    print(f"  By status: {stats['by_status']}")
    
    # Test edge query
    edges = query_edges("SELECT * FROM edges LIMIT 3")
    print(f"\nSample edges table:")
    print(format_edges_table(edges))
    
    print("\n✓ _base.py functions working")


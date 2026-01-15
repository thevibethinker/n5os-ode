#!/usr/bin/env python3
"""
Generate a domain review document for human validation.
Flags positions that may be mis-domained based on keyword heuristics.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = "/home/workspace/N5/data/positions.db"
OUTPUT_PATH = "/home/workspace/N5/builds/position-system-overhaul/domain-review.md"

# Domain keywords for heuristic flagging
DOMAIN_SIGNALS = {
    "hiring-market": ["hiring", "recruit", "candidate", "job", "employer", "application", "resume", "interview"],
    "careerspan": ["careerspan", "career development", "career mobility", "job search", "professional identity"],
    "ai-automation": ["ai", "automation", "llm", "model", "orchestrat", "vibe coding", "agent"],
    "epistemology": ["knowledge", "truth", "belief", "understanding", "signal", "noise", "epistem"],
    "worldview": ["systemic", "institution", "society", "culture", "paradigm"],
    "founder": ["founder", "startup", "venture", "fundrais", "investor", "moonshot"],
    "personal-foundations": ["self-aware", "integrity", "energy", "habit", "personal"],
    "education": ["education", "learning", "teaching", "student"]
}

def get_positions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, domain, title, insight FROM positions ORDER BY domain, title")
    return [dict(row) for row in cursor.fetchall()]

def suggest_domain(title: str, insight: str) -> list[str]:
    """Return list of domains that match based on keywords."""
    text = (title + " " + insight).lower()
    matches = []
    for domain, keywords in DOMAIN_SIGNALS.items():
        for kw in keywords:
            if kw in text:
                matches.append(domain)
                break
    return matches

def main():
    positions = get_positions()
    
    # Group by domain
    by_domain = {}
    for pos in positions:
        domain = pos["domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(pos)
    
    lines = [
        "---",
        "created: 2026-01-15",
        "provenance: con_AVUiANpq2GYAc3Qz",
        "type: review_queue",
        "---",
        "",
        "# Domain Review Queue",
        "",
        "Review each position's domain assignment. Mark with:",
        "- `[✓]` if correct",
        "- `[→ domain-name]` if should be moved",
        "- `[?]` if unclear",
        "",
        "Positions flagged with ⚠️ have keyword mismatches (may be mis-domained).",
        "",
    ]
    
    flagged_count = 0
    
    for domain in sorted(by_domain.keys()):
        positions_in_domain = by_domain[domain]
        lines.append(f"## {domain} ({len(positions_in_domain)} positions)")
        lines.append("")
        
        for pos in positions_in_domain:
            suggested = suggest_domain(pos["title"], pos["insight"])
            is_flagged = suggested and domain not in suggested
            
            flag = " ⚠️" if is_flagged else ""
            if is_flagged:
                flagged_count += 1
                alt_domains = ", ".join(suggested)
                flag += f" (suggests: {alt_domains})"
            
            insight_preview = pos["insight"][:120].replace("\n", " ") + "..." if len(pos["insight"]) > 120 else pos["insight"].replace("\n", " ")
            
            lines.append(f"### [ ] `{pos['id']}`{flag}")
            lines.append(f"**{pos['title']}**")
            lines.append(f"> {insight_preview}")
            lines.append("")
    
    lines.append("---")
    lines.append(f"**Summary:** {len(positions)} positions, {flagged_count} flagged for review")
    
    Path(OUTPUT_PATH).write_text("\n".join(lines))
    print(f"Generated {OUTPUT_PATH}")
    print(f"  Total: {len(positions)}")
    print(f"  Flagged: {flagged_count}")

if __name__ == "__main__":
    main()


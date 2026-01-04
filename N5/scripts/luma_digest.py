#!/usr/bin/env python3
"""
Luma Event Digest Generator - Generates actionable event digests from the events database.

Usage:
    python3 N5/scripts/luma_digest.py --days 7 --top 5 --format markdown
    python3 N5/scripts/luma_digest.py --preview --city nyc --num 5
    python3 N5/scripts/luma_digest.py --output /path/to/digest.md

Author: V's N5 System
Created: 2026-01-03
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Literal

# Calculate paths relative to this script
SCRIPTS_DIR = Path(__file__).parent
N5_ROOT = SCRIPTS_DIR.parent
N5_DATA_DIR = N5_ROOT / "data"
N5_CONFIG_DIR = N5_ROOT / "config"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = N5_DATA_DIR / "luma_events.db"
TALLY_PATH = N5_DATA_DIR / "luma_organizer_tally.json"
ALLOWLISTS_PATH = N5_CONFIG_DIR / "allowlists.json"


def load_organizer_tally() -> dict:
    """Load organizer trust scores from tally file."""
    if TALLY_PATH.exists():
        with open(TALLY_PATH) as f:
            data = json.load(f)
            data.pop("_meta", None)
            return data
    return {}


def load_priority_organizers() -> list[str]:
    """Load must-go organizers from allowlists."""
    if ALLOWLISTS_PATH.exists():
        with open(ALLOWLISTS_PATH) as f:
            config = json.load(f)
            # Extract priority organizers from the priority_note field
            note = config.get("priority_note", "")
            # Parse names like "Supermomos/Edwina, Fibe/Ben Guo..."
            priority = []
            for part in note.replace("MUST-GO organizers:", "").split(","):
                names = part.strip().split("/")
                priority.extend([n.strip() for n in names if n.strip()])
            return priority
    return []


def score_indicator(score: float) -> str:
    """Return visual indicator based on score."""
    if score >= 8:
        return "🔥"
    elif score >= 6:
        return "⭐"
    elif score >= 4:
        return "👀"
    else:
        return "📍"


def get_organizer_trust(organizers_json: str, tally: dict, priority_orgs: list[str]) -> tuple[str, bool]:
    """Get organizer display with trust indicator.
    
    Returns:
        (organizer_display, is_priority)
    """
    try:
        organizers = json.loads(organizers_json) if organizers_json else []
    except:
        organizers = []
    
    if not organizers:
        return "Unknown Organizer", False
    
    org_names = [o.get("name", "") for o in organizers if o.get("name")]
    if not org_names:
        return "Unknown Organizer", False
    
    main_org = org_names[0]
    attended_count = tally.get(main_org, 0)
    
    # Check if priority organizer
    is_priority = any(
        p.lower() in main_org.lower() or main_org.lower() in p.lower()
        for p in priority_orgs
    )
    
    # Build display string
    if is_priority:
        display = f"{main_org} (🎯 MUST-GO)"
    elif attended_count >= 3:
        display = f"{main_org} (trusted ✓ | {attended_count} attended)"
    elif attended_count > 0:
        display = f"{main_org} ({attended_count} attended)"
    else:
        display = main_org
    
    return display, is_priority


def get_events_for_digest(
    db_path: Path,
    days_ahead: int = 7,
    city: str = None,
    exclude_rejected: bool = True,
    exclude_digested: bool = False
) -> list[dict]:
    """Fetch upcoming events from database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days_ahead)
    
    query = """
        SELECT * FROM events
        WHERE event_datetime >= ?
        AND event_datetime <= ?
        AND score IS NOT NULL
    """
    params = [now.isoformat(), end_date.isoformat()]
    
    if city:
        query += " AND city = ?"
        params.append(city)
    
    if exclude_rejected:
        query += " AND rejected_at IS NULL"
    
    if exclude_digested:
        query += " AND digest_sent_at IS NULL"
    
    query += " ORDER BY score DESC, event_datetime ASC"
    
    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return events


def generate_event_reason(event: dict) -> str:
    """Generate a one-line reason why this event is recommended."""
    rationale = event.get("score_rationale", "")
    if isinstance(rationale, str):
        try:
            rationale = json.loads(rationale)
        except:
            rationale = []
    
    if not rationale:
        score = event.get("score", 0)
        if score >= 8:
            return "High-signal networking opportunity"
        elif score >= 6:
            return "Good match for your interests"
        else:
            return "Worth considering"
    
    # Extract the most meaningful rationale points
    highlights = []
    for r in rationale:
        if "Priority Organizer" in r:
            highlights.append("Priority organizer")
        elif "Organizer Loyalty" in r:
            highlights.append("Trusted organizer")
        elif "Email" in r:
            highlights.append("Email-discovered event")
        elif "Intimate" in r or "curated" in r.lower():
            highlights.append("Intimate/curated gathering")
        elif "networking" in r.lower() or "founder" in r.lower():
            highlights.append("Founder networking")
        elif "preferred_days" in r.lower() or "Weekday" in r:
            highlights.append("Good timing")
    
    if highlights:
        return "; ".join(highlights[:2])
    
    # Fall back to first rationale item
    if rationale:
        first = rationale[0]
        # Strip the score prefix like "+2.0: "
        if ":" in first:
            return first.split(":", 1)[1].strip()
    
    return "Matches your preferences"


def format_event_date(event_datetime: str) -> str:
    """Format datetime for display."""
    try:
        dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
        # Convert to ET (rough, not using pytz)
        et_offset = timedelta(hours=-5)
        dt_et = dt + et_offset
        return dt_et.strftime("%A, %b %d at %-I:%M %p")
    except:
        return event_datetime or "TBD"


def compute_stats(events: list[dict]) -> dict:
    """Compute summary statistics for the digest."""
    stats = {
        "total": len(events),
        "by_day": {},
        "by_category": {
            "networking": 0,
            "social": 0,
            "tech": 0,
            "other": 0
        },
        "high_score_count": 0,
        "priority_organizer_count": 0
    }
    
    tally = load_organizer_tally()
    priority_orgs = load_priority_organizers()
    
    for event in events:
        # Count high scores
        if (event.get("score") or 0) >= 8:
            stats["high_score_count"] += 1
        
        # Count priority organizers
        _, is_priority = get_organizer_trust(
            event.get("organizers", "[]"),
            tally,
            priority_orgs
        )
        if is_priority:
            stats["priority_organizer_count"] += 1
        
        # Categorize by keywords
        title = (event.get("title") or "").lower()
        desc = (event.get("description") or "").lower()
        text = f"{title} {desc}"
        
        if any(k in text for k in ["networking", "founder", "startup", "vc", "investor"]):
            stats["by_category"]["networking"] += 1
        elif any(k in text for k in ["party", "social", "happy hour", "drinks", "dinner"]):
            stats["by_category"]["social"] += 1
        elif any(k in text for k in ["tech", "ai", "ml", "engineering", "developer", "code"]):
            stats["by_category"]["tech"] += 1
        else:
            stats["by_category"]["other"] += 1
        
        # Count by day
        try:
            dt = datetime.fromisoformat(event.get("event_datetime", "").replace("Z", "+00:00"))
            day_name = dt.strftime("%A")
            stats["by_day"][day_name] = stats["by_day"].get(day_name, 0) + 1
        except:
            pass
    
    return stats


def generate_digest(
    db_path: str = None,
    days_ahead: int = 7,
    top_n: int = 5,
    city: str = "nyc",
    output_format: Literal["markdown", "html", "json"] = "markdown"
) -> dict:
    """
    Generate an event digest.
    
    Args:
        db_path: Path to SQLite database (defaults to N5 path)
        days_ahead: Number of days to look ahead
        top_n: Number of top events to highlight
        city: City filter (e.g., "nyc")
        output_format: Output format ("markdown", "html", or "json")
    
    Returns:
        {
            "digest_text": str,  # formatted digest
            "events": list,  # event objects used
            "stats": dict,  # summary stats
            "generated_at": str  # ISO timestamp
        }
    """
    db_path = Path(db_path) if db_path else DB_PATH
    
    # Load reference data
    tally = load_organizer_tally()
    priority_orgs = load_priority_organizers()
    
    # Fetch events
    events = get_events_for_digest(
        db_path,
        days_ahead=days_ahead,
        city=city,
        exclude_rejected=True
    )
    
    # Compute stats
    stats = compute_stats(events)
    
    # Get top events
    top_events = events[:top_n]
    
    # Generate timestamp
    now = datetime.now(timezone.utc)
    generated_at = now.isoformat()
    
    # Calculate date range
    end_date = now + timedelta(days=days_ahead)
    date_range = f"{now.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    
    if output_format == "json":
        return {
            "digest_text": json.dumps({
                "top_events": top_events,
                "stats": stats,
                "date_range": date_range
            }, indent=2),
            "events": top_events,
            "stats": stats,
            "generated_at": generated_at
        }
    
    # Build markdown digest
    lines = []
    lines.append(f"# 🎟️ V's Events Digest")
    lines.append(f"*Week of {date_range}*")
    lines.append("")
    
    if not top_events:
        lines.append("No upcoming events found matching your criteria.")
        lines.append("")
        lines.append("Check [lu.ma/nyc](https://lu.ma/nyc) for the latest events.")
    else:
        lines.append(f"## 🔥 Top {len(top_events)} Must-See Events")
        lines.append("")
        
        for i, event in enumerate(top_events, 1):
            score = event.get("score", 0)
            indicator = score_indicator(score)
            
            org_display, is_priority = get_organizer_trust(
                event.get("organizers", "[]"),
                tally,
                priority_orgs
            )
            
            reason = generate_event_reason(event)
            
            lines.append(f"### {i}. [{event.get('title', 'Untitled')}]({event.get('url', '#')})")
            lines.append(f"**When:** {format_event_date(event.get('event_datetime'))}")
            
            venue = event.get("venue_name") or "Location TBD"
            if event.get("venue_address"):
                venue += f" ({event.get('venue_address')})"
            lines.append(f"**Where:** {venue}")
            
            lines.append(f"**Score:** {indicator} {score:.1f}/10 | **Organizer:** {org_display}")
            lines.append(f"**Why:** {reason}")
            
            price = event.get("price", "Unknown")
            attendees = event.get("attendee_count", 0)
            lines.append(f"**Price:** {price} | **{attendees}** attending")
            lines.append("")
    
    # Stats section
    lines.append("---")
    lines.append("")
    lines.append("## 📊 This Week at a Glance")
    lines.append(f"- **Total Events:** {stats['total']}")
    
    cat = stats["by_category"]
    lines.append(f"- **Networking:** {cat['networking']} | **Social:** {cat['social']} | **Tech:** {cat['tech']} | **Other:** {cat['other']}")
    
    if stats["priority_organizer_count"] > 0:
        lines.append(f"- **Must-Go Organizers Active:** {stats['priority_organizer_count']}")
    
    if stats["high_score_count"] > 0:
        lines.append(f"- **High-Score Events (8+):** {stats['high_score_count']}")
    
    lines.append("")
    
    # Quick actions
    lines.append("## 🔗 Quick Actions")
    lines.append("- [View Full Calendar](https://events-calendar-va.zocomputer.io)")
    lines.append("- [Browse All Events](https://lu.ma/nyc)")
    lines.append("")
    lines.append(f"*Generated: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC*")
    
    digest_text = "\n".join(lines)
    
    # Convert to HTML if requested
    if output_format == "html":
        digest_text = markdown_to_html(digest_text)
    
    return {
        "digest_text": digest_text,
        "events": top_events,
        "stats": stats,
        "generated_at": generated_at
    }


def markdown_to_html(md_text: str) -> str:
    """Convert markdown to basic HTML for email."""
    import re
    
    html_lines = []
    html_lines.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333; }
        h1 { color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
        h2 { color: #16213e; margin-top: 30px; }
        h3 { color: #0f3460; margin-bottom: 5px; }
        a { color: #e94560; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .event { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .stats { background: #e8f4f8; padding: 15px; border-radius: 8px; }
        .actions { background: #fff3cd; padding: 15px; border-radius: 8px; }
        hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
        em { color: #666; }
    </style>
</head>
<body>
""")
    
    lines = md_text.split("\n")
    in_event = False
    
    for line in lines:
        # Headers
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            if "Top" in line:
                in_event = True
            elif "Glance" in line:
                html_lines.append('<div class="stats">')
            elif "Quick" in line:
                html_lines.append('</div>')
                html_lines.append('<div class="actions">')
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            # Event title - extract link
            match = re.match(r"### \d+\. \[(.+?)\]\((.+?)\)", line)
            if match:
                title, url = match.groups()
                html_lines.append(f'<div class="event"><h3><a href="{url}">{title}</a></h3>')
        elif line.startswith("**"):
            # Bold lines (event details)
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
            html_lines.append(f"<p>{line}</p>")
        elif line.startswith("- "):
            # List items
            content = line[2:]
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            content = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', content)
            html_lines.append(f"<p>• {content}</p>")
        elif line.startswith("---"):
            if in_event:
                html_lines.append("</div>")
                in_event = False
            html_lines.append("<hr>")
        elif line.startswith("*") and line.endswith("*"):
            html_lines.append(f"<p><em>{line[1:-1]}</em></p>")
        elif line.strip() == "":
            if in_event:
                html_lines.append("</div>")
                in_event = False
    
    html_lines.append("</div></body></html>")
    
    return "\n".join(html_lines)


def preview_digest(
    city: str = "nyc",
    num: int = 5,
    days: int = 7
) -> None:
    """Print a preview of the digest to stdout."""
    result = generate_digest(
        days_ahead=days,
        top_n=num,
        city=city,
        output_format="markdown"
    )
    
    print(result["digest_text"])
    print("\n" + "=" * 60)
    print(f"📈 Stats: {json.dumps(result['stats'], indent=2)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate event digests from Luma events database"
    )
    parser.add_argument(
        "--days", type=int, default=7,
        help="Number of days to look ahead (default: 7)"
    )
    parser.add_argument(
        "--top", "--num", type=int, default=5, dest="top",
        help="Number of top events to highlight (default: 5)"
    )
    parser.add_argument(
        "--city", default="nyc",
        help="City filter (default: nyc)"
    )
    parser.add_argument(
        "--format", choices=["markdown", "html", "json"], default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        help="Output file path (prints to stdout if not specified)"
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Preview mode: print digest with stats"
    )
    parser.add_argument(
        "--db", type=str,
        help="Custom database path"
    )
    
    args = parser.parse_args()
    
    if args.preview:
        preview_digest(city=args.city, num=args.top, days=args.days)
        return
    
    # Generate digest
    result = generate_digest(
        db_path=args.db,
        days_ahead=args.days,
        top_n=args.top,
        city=args.city,
        output_format=args.format
    )
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result["digest_text"])
        logger.info(f"Digest written to {output_path}")
        print(f"✅ Digest saved to {output_path}")
        print(f"📊 {result['stats']['total']} events found, {len(result['events'])} highlighted")
    else:
        print(result["digest_text"])


if __name__ == "__main__":
    main()




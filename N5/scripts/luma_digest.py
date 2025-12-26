#!/usr/bin/env python3
"""
Luma Daily Digest - Generates and sends event recommendations.

Usage:
    python3 N5/scripts/luma_digest.py --generate
    python3 N5/scripts/luma_digest.py --preview
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
DIGEST_DIR = N5_ROOT / "digests"


def get_top_undigest_events(city: str = "nyc", limit: int = 5) -> list[dict]:
    """Get top scored events that haven't been sent in a digest."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM events
        WHERE digest_sent_at IS NULL
        AND rejected_at IS NULL
        AND approved_at IS NULL
        AND event_datetime >= datetime('now')
        AND score IS NOT NULL
        AND city = ?
        ORDER BY score DESC, event_datetime ASC
        LIMIT ?
    """, (city, limit))
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return events


def format_digest_markdown(events: list[dict], availability: dict = None) -> str:
    """Format events as a markdown digest."""
    lines = []
    
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    
    lines.append(f"# 🎯 Luma Event Recommendations")
    lines.append(f"**{date_str}**")
    lines.append("")
    
    if availability:
        this_week = availability.get("this_week", {})
        next_week = availability.get("next_week", {})
        lines.append("## 📊 Weekly Status")
        lines.append(f"- **This week:** {this_week.get('event_count', 0)} events booked ({this_week.get('slots_available', 0)} slots available)")
        lines.append(f"- **Next week:** {next_week.get('event_count', 0)} events booked ({next_week.get('slots_available', 0)} slots available)")
        lines.append("")
    
    lines.append("## 🌟 Top Recommendations")
    lines.append("")
    
    for i, event in enumerate(events, 1):
        # Parse datetime for display
        event_dt_str = event.get("event_datetime", "")
        try:
            event_dt = datetime.fromisoformat(event_dt_str.replace("Z", "+00:00"))
            day_name = event_dt.strftime("%A")
            date_display = event_dt.strftime("%b %d")
            time_display = event_dt.strftime("%I:%M %p").lstrip("0")
        except:
            day_name = "?"
            date_display = event.get("event_date", "?")
            time_display = event.get("event_time", "?")
        
        # Parse rationale
        rationale = event.get("score_rationale", "[]")
        if isinstance(rationale, str):
            try:
                rationale = json.loads(rationale)
            except:
                rationale = []
        
        score = event.get("score", 0)
        score_bar = "⭐" * min(5, int(score / 2))
        
        lines.append(f"### {i}. {event.get('title', 'Untitled')}")
        lines.append("")
        lines.append(f"| | |")
        lines.append(f"|---|---|")
        lines.append(f"| 📅 **When** | {day_name}, {date_display} at {time_display} |")
        lines.append(f"| 📍 **Where** | {event.get('venue_name', 'TBD')} |")
        lines.append(f"| 💰 **Price** | {event.get('price', 'Unknown')} |")
        lines.append(f"| 👥 **Attending** | {event.get('attendee_count', 0)}+ people |")
        lines.append(f"| {score_bar} | Score: **{score:.1f}**/10 |")
        lines.append("")
        
        if rationale:
            lines.append(f"**Why this event:** {'; '.join(rationale[:3])}")
            lines.append("")
        
        lines.append(f"🔗 [{event.get('url', '')}]({event.get('url', '')})")
        lines.append("")
        lines.append(f"**[✅ APPROVE](approve:{event['id']})** | **[❌ SKIP](reject:{event['id']})**")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    lines.append("## 📋 Quick Actions")
    lines.append("")
    lines.append("Reply with event numbers to approve (e.g., '1, 3' or 'all')")
    lines.append("")
    
    return "\n".join(lines)


def format_digest_email_html(events: list[dict], availability: dict = None) -> str:
    """Format events as HTML for email."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %d, %Y")
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .event {{ background: #f8f9fa; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
        .event-title {{ font-size: 18px; font-weight: 600; margin-bottom: 10px; }}
        .event-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
        .score {{ background: #4CAF50; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block; }}
        .rationale {{ font-size: 13px; color: #555; background: #e8f5e9; padding: 10px; border-radius: 8px; margin: 10px 0; }}
        .actions {{ margin-top: 15px; }}
        .btn {{ display: inline-block; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 500; margin-right: 10px; }}
        .btn-approve {{ background: #4CAF50; color: white; }}
        .btn-skip {{ background: #f44336; color: white; }}
        .btn-view {{ background: #2196F3; color: white; }}
        .status {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Luma Event Recommendations</h1>
        <p>{date_str}</p>
    </div>
"""
    
    if availability:
        this_week = availability.get("this_week", {})
        next_week = availability.get("next_week", {})
        html += f"""
    <div class="status">
        <strong>📊 Weekly Status</strong><br>
        This week: {this_week.get('event_count', 0)} events ({this_week.get('slots_available', 0)} slots available)<br>
        Next week: {next_week.get('event_count', 0)} events ({next_week.get('slots_available', 0)} slots available)
    </div>
"""
    
    for i, event in enumerate(events, 1):
        event_dt_str = event.get("event_datetime", "")
        try:
            event_dt = datetime.fromisoformat(event_dt_str.replace("Z", "+00:00"))
            day_name = event_dt.strftime("%A")
            date_display = event_dt.strftime("%b %d")
            time_display = event_dt.strftime("%I:%M %p").lstrip("0")
        except:
            day_name = ""
            date_display = event.get("event_date", "?")
            time_display = event.get("event_time", "?")
        
        rationale = event.get("score_rationale", "[]")
        if isinstance(rationale, str):
            try:
                rationale = json.loads(rationale)
            except:
                rationale = []
        
        score = event.get("score", 0)
        
        html += f"""
    <div class="event">
        <div class="event-title">{i}. {event.get('title', 'Untitled')}</div>
        <div class="event-meta">📅 {day_name}, {date_display} at {time_display}</div>
        <div class="event-meta">📍 {event.get('venue_name', 'TBD')}</div>
        <div class="event-meta">💰 {event.get('price', 'Unknown')} • 👥 {event.get('attendee_count', 0)}+ attending</div>
        <span class="score">⭐ {score:.1f}/10</span>
"""
        
        if rationale:
            html += f"""
        <div class="rationale">
            <strong>Why:</strong> {'; '.join(rationale[:3])}
        </div>
"""
        
        html += f"""
        <div class="actions">
            <a href="{event.get('url', '')}" class="btn btn-view">View Event</a>
        </div>
    </div>
"""
    
    html += """
    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 13px;">
        <p>Reply to this email with event numbers to approve (e.g., "1, 3" or "all")</p>
    </div>
</body>
</html>
"""
    
    return html


def mark_digest_sent(event_ids: list[str]) -> int:
    """Mark events as having been sent in a digest."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    for event_id in event_ids:
        cursor.execute("UPDATE events SET digest_sent_at = ? WHERE id = ?", (now, event_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected


def save_digest(content: str, format: str = "md") -> str:
    """Save digest to file."""
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"luma-event-digest-{date_str}.{format}"
    filepath = DIGEST_DIR / filename
    
    with open(filepath, "w") as f:
        f.write(content)
    
    logger.info(f"Saved digest to {filepath}")
    return str(filepath)


def generate_digest(city: str = "nyc", num_events: int = 5, send_email: bool = False) -> dict:
    """Generate the daily digest."""
    from luma_scorer import score_all_pending
    from luma_calendar import get_week_availability
    
    # Rescore events
    score_all_pending(city)
    
    # Get availability
    availability = get_week_availability()
    
    # Get top events
    events = get_top_undigest_events(city, num_events)
    
    if not events:
        logger.info("No new events to recommend")
        return {"events": 0, "digest_path": None}
    
    # Generate markdown digest
    md_content = format_digest_markdown(events, availability)
    md_path = save_digest(md_content, "md")
    
    # Generate HTML for email
    html_content = format_digest_email_html(events, availability)
    html_path = save_digest(html_content, "html")
    
    # Mark events as sent (only if actually sending)
    if send_email:
        event_ids = [e["id"] for e in events]
        mark_digest_sent(event_ids)
    
    return {
        "events": len(events),
        "digest_md_path": md_path,
        "digest_html_path": html_path,
        "event_summaries": [
            {"title": e["title"], "score": e["score"], "date": e["event_date"]}
            for e in events
        ]
    }


async def main():
    parser = argparse.ArgumentParser(description="Generate Luma event digest")
    parser.add_argument("--city", default="nyc", help="City code")
    parser.add_argument("--num", type=int, default=5, help="Number of events")
    parser.add_argument("--preview", action="store_true", help="Preview without marking sent")
    parser.add_argument("--generate", action="store_true", help="Generate and save digest")
    args = parser.parse_args()
    
    if args.preview:
        events = get_top_undigest_events(args.city, args.num)
        from luma_calendar import get_week_availability
        availability = get_week_availability()
        content = format_digest_markdown(events, availability)
        print(content)
        
    elif args.generate:
        result = generate_digest(args.city, args.num, send_email=False)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


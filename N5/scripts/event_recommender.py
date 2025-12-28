#!/usr/bin/env python3
"""
Event Recommender
Scores and recommends events based on V's preferences.
Outputs must-go events for the digest.
"""
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

N5_ROOT = Path("/home/workspace/N5")
CANDIDATES_FILE = N5_ROOT / "data" / "luma_candidates.json"
PREFS_FILE = N5_ROOT / "config" / "event_preferences.json"

def load_preferences():
    if PREFS_FILE.exists():
        with open(PREFS_FILE) as f:
            return json.load(f)
    return {}

def load_events():
    if CANDIDATES_FILE.exists():
        with open(CANDIDATES_FILE) as f:
            return json.load(f)
    return []

def score_event(event: dict, prefs: dict) -> tuple[float, list[str]]:
    """Score an event and return (score, reasons)."""
    score = 0.0
    reasons = []
    
    title = event.get("title", "").lower()
    description = event.get("description", "").lower()
    
    # Handle organizers - can be string or list of objects
    organizers_raw = event.get("organizers", "")
    if isinstance(organizers_raw, list):
        organizers = " ".join([o.get("name", "") for o in organizers_raw if isinstance(o, dict)]).lower()
    elif isinstance(organizers_raw, str):
        try:
            org_list = json.loads(organizers_raw)
            organizers = " ".join([o.get("name", "") for o in org_list if isinstance(o, dict)]).lower()
        except:
            organizers = organizers_raw.lower()
    else:
        organizers = ""
    
    combined = f"{title} {description} {organizers}"
    
    # Must-go organizers (highest priority)
    for org in prefs.get("must_go_rules", {}).get("organizers", []):
        for pattern in org.get("patterns", []):
            if pattern.lower() in combined:
                score += 10.0  # Strong signal
                reasons.append(f"🌟 {org['name']}: {org['reason']}")
                break
    
    # Keyword boosts
    for kw in prefs.get("must_go_rules", {}).get("keywords_boost", []):
        if kw["keyword"].lower() in combined:
            score += kw["weight"]
            reasons.append(f"+{kw['weight']}: '{kw['keyword']}'")
    
    # Keyword penalties
    for kw in prefs.get("must_go_rules", {}).get("keywords_avoid", []):
        if kw["keyword"].lower() in combined:
            score += kw["weight"]  # negative
            reasons.append(f"{kw['weight']}: '{kw['keyword']}'")
    
    # Free events get a small boost
    price = event.get("price", "").lower()
    if price == "free" or price == "$0":
        score += 0.5
        reasons.append("+0.5: Free event")
    
    # High attendee count is social proof
    attendees = event.get("attendee_count", 0)
    if attendees > 50:
        score += 1.0
        reasons.append(f"+1.0: {attendees} attendees")
    elif attendees > 20:
        score += 0.5
        reasons.append(f"+0.5: {attendees} attendees")
    
    return score, reasons

def get_must_go_events(days_ahead: int = 30, top_n: int = 5) -> list[dict]:
    """Get top recommended events for the next N days."""
    prefs = load_preferences()
    events = load_events()
    
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)
    
    scored_events = []
    for event in events:
        # Parse date - try multiple field names
        date_str = event.get("event_datetime") or event.get("event_date") or event.get("date", "")
        try:
            # Handle various date formats
            if "T" in str(date_str):
                event_date = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            elif date_str:
                event_date = datetime.strptime(str(date_str), "%Y-%m-%d")
            else:
                continue
        except:
            continue
        
        # Skip past events
        if event_date.replace(tzinfo=None) < now:
            continue
        
        # Skip events too far out
        if event_date.replace(tzinfo=None) > cutoff:
            continue
        
        score, reasons = score_event(event, prefs)
        scored_events.append({
            **event,
            "recommendation_score": score,
            "recommendation_reasons": reasons
        })
    
    # Sort by score descending
    scored_events.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    # Return top N with score > 0
    must_go = [e for e in scored_events if e["recommendation_score"] >= 5.0][:top_n]
    
    return must_go

def format_for_digest(events: list[dict]) -> str:
    """Format events for the morning digest."""
    if not events:
        return "No must-go events this week. Check the [Events Calendar](https://events-calendar-va.zocomputer.io) for all options."
    
    lines = ["## 🎯 Must-Go Events\n"]
    for event in events:
        title = event.get("title", "Untitled")
        date = event.get("event_datetime") or event.get("event_date") or event.get("date", "TBD")
        url = event.get("url", "")
        score = event.get("recommendation_score", 0)
        reasons = event.get("recommendation_reasons", [])
        
        # Format date nicely
        try:
            if "T" in str(date):
                dt = datetime.fromisoformat(str(date).replace("Z", "+00:00"))
                date_nice = dt.strftime("%a %b %d, %I:%M %p")
            else:
                dt = datetime.strptime(str(date), "%Y-%m-%d")
                date_nice = dt.strftime("%a %b %d")
        except:
            date_nice = date
        
        lines.append(f"### [{title}]({url})")
        lines.append(f"📅 {date_nice}")
        
        # Show top reason
        if reasons:
            top_reason = [r for r in reasons if r.startswith("🌟")]
            if top_reason:
                lines.append(f"*{top_reason[0]}*")
        
        lines.append("")
    
    lines.append(f"\n[View all events →](https://events-calendar-va.zocomputer.io)")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Event Recommender")
    parser.add_argument("--days", type=int, default=30, help="Days to look ahead")
    parser.add_argument("--top", type=int, default=5, help="Top N events to return")
    parser.add_argument("--format", choices=["json", "digest"], default="json")
    args = parser.parse_args()
    
    events = get_must_go_events(days_ahead=args.days, top_n=args.top)
    
    if args.format == "digest":
        print(format_for_digest(events))
    else:
        print(json.dumps(events, indent=2, default=str))

if __name__ == "__main__":
    main()




#!/usr/bin/env python3
"""
Luma Event Scorer - Scores and ranks events based on preferences.

Usage:
    python3 N5/scripts/luma_scorer.py --city nyc
    python3 N5/scripts/luma_scorer.py --city nyc --top 10
"""

import argparse
import json
import logging
import re
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
CONFIG_PATH = N5_ROOT / "config" / "luma_scoring.json"


def load_config() -> dict:
    """Load scoring configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def score_event(event: dict, config: dict, existing_calendar_events: list = None) -> tuple[float, list[str]]:
    """
    Score a single event based on preferences.
    
    Returns:
        (score, rationale_list)
    """
    score = 5.0  # Base score
    rationale = []
    
    title = (event.get("title") or "").lower()
    description = (event.get("description") or "").lower()
    venue = (event.get("venue_name") or "").lower()
    text_content = f"{title} {description} {venue}"
    
    # === Category scoring ===
    cat_config = config.get("category_keywords", {})
    
    for priority, cfg in cat_config.items():
        keywords = cfg.get("keywords", [])
        weight = cfg.get("weight", 0)
        # Check exclusion first
        if priority == "exclude":
            for kw in keywords:
                if kw.lower() in text_content:
                    score += weight
                    rationale.append(f"{weight}: Excluded keyword '{kw}'")
            continue

        
        matched = [kw for kw in keywords if kw.lower() in text_content]
        if matched:
            score += weight
            if weight > 0:
                rationale.append(f"+{weight}: Matches {priority} keywords: {', '.join(matched[:3])}")
            else:
                rationale.append(f"{weight}: Matches exclude keywords: {', '.join(matched[:3])}")
    
    # === Time preferences ===
    time_config = config.get("time_preferences", {})
    event_datetime = event.get("event_datetime", "")
    
    if event_datetime:
        try:
            dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
            day_name = dt.strftime("%A")
            hour = dt.hour
            
            # Day preference
            preferred_days = time_config.get("preferred_days", [])
            if day_name in preferred_days:
                score += 1.0
                rationale.append(f"+1.0: Preferred day ({day_name})")
            elif day_name in ["Saturday", "Sunday"]:
                penalty = time_config.get("weekend_penalty", -1.0)
                score += penalty
                rationale.append(f"{penalty}: Weekend event")
            
            # Hour preference
            pref_hours = time_config.get("preferred_hours", {})
            if pref_hours.get("start", 0) <= hour <= pref_hours.get("end", 24):
                score += 0.5
                rationale.append(f"+0.5: Preferred time slot")
            elif hour >= 22:
                penalty = time_config.get("late_night_penalty", -1.5)
                score += penalty
                rationale.append(f"{penalty}: Late night event")
                
        except Exception as e:
            logger.warning(f"Error parsing datetime for {event.get('title')}: {e}")
    
    # === Format preferences (breakfast, dinner, fireside) ===
    format_config = config.get("format_preferences", {})
    format_keywords = format_config.get("keywords", {})
    for keyword, bonus in format_keywords.items():
        if keyword.lower() in text_content:
            score += bonus
            rationale.append(f"+{bonus}: {keyword.title()} format")
            break  # Only apply one format bonus
    
    # === Size preferences (intimate events) ===
    size_config = config.get("size_preferences", {})
    intimate_threshold = size_config.get("intimate_threshold", 50)
    large_threshold = size_config.get("large_threshold", 100)
    
    # Check for size indicators in text
    if any(x in text_content for x in ["30 founders", "40 founders", "50 people", "intimate", "curated", "select group"]):
        bonus = size_config.get("intimate_bonus", 1.5)
        score += bonus
        rationale.append(f"+{bonus}: Intimate/curated event")
    elif any(x in text_content for x in ["200+", "500+", "1000+", "conference"]):
        penalty = size_config.get("large_penalty", -1.0)
        score += penalty
        rationale.append(f"{penalty}: Large conference/event")
    
    # === Weekday bonus ===
    if event_datetime:
        try:
            dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
            if dt.weekday() < 5:  # Monday-Friday
                weekday_bonus = time_config.get("weekday_bonus", 1.0)
                score += weekday_bonus
                rationale.append(f"+{weekday_bonus}: Weekday bonus")
        except:
            pass

    # === Social proof ===
    social_config = config.get("social_proof", {})
    attendee_count = event.get("attendee_count", 0) or 0
    
    if attendee_count >= social_config.get("high_attendance_threshold", 50):
        bonus = social_config.get("high_attendance_bonus", 1.0)
        score += bonus
        rationale.append(f"+{bonus}: High attendance ({attendee_count}+ people)")
    elif attendee_count <= social_config.get("low_attendance_threshold", 5) and attendee_count > 0:
        penalty = social_config.get("low_attendance_penalty", -0.5)
        score += penalty
        rationale.append(f"{penalty}: Low attendance ({attendee_count} people)")
    
    # === Price preferences ===
    price_config = config.get("price_preferences", {})
    price = event.get("price", "").lower()
    
    if price == "free":
        bonus = price_config.get("free_bonus", 0.5)
        score += bonus
        rationale.append(f"+{bonus}: Free event")
    elif price.startswith("$"):
        try:
            price_val = float(re.sub(r"[^\d.]", "", price))
            if price_val > price_config.get("paid_max", 50):
                penalty = price_config.get("expensive_penalty", -1.0)
                score += penalty
                rationale.append(f"{penalty}: Expensive (${price_val})")
        except:
            pass
    
    # === Status adjustments ===
    status = event.get("status", "")
    if status == "waitlist":
        score -= 1.0
        rationale.append("-1.0: Waitlist only")
    elif status == "rsvp_hidden":
        score -= 0.5
        rationale.append("-0.5: RSVP hidden")    
    # === Discovery Source Boost ===
    raw_data = event.get("raw_data") or "{}"
    try:
        raw_json = json.loads(raw_data)
        if raw_json.get("_discovery_source") == "email_scan":
            score += 2.0
            rationale.append("+2.0: Discovered via Email (High Signal)")
    except:
        pass
    
    # === Booking window preference ===
    booking_config = config.get("booking_rules", {})
    if event_datetime:
        try:
            dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))            
            # Weekday/Weekend check
            is_weekend = dt.weekday() >= 5  # 5=Sat, 6=Sun
            time_prefs = config.get("time_preferences", {})
            if is_weekend:
                penalty = time_prefs.get("weekend_penalty", -0.5)
                if penalty != 0:
                    score += penalty
                    rationale.append(f"{penalty}: Weekend penalty")
            else:
                bonus = time_prefs.get("weekday_bonus", 1.0)
                if bonus != 0:
                    score += bonus
                    rationale.append(f"+{bonus}: Weekday bonus")

            # Organizer Reputation & Loyalty
            organizers_json = event.get("organizers") or "[]"
            try:
                organizers = json.loads(organizers_json)
                rep_config = config.get("organizer_reputation", {})
                priority_orgs = [o.lower() for o in rep_config.get("priority_organizers", [])]
                
                for org in organizers:
                    name = org.get("name", "").lower()
                    if not name: continue
                    
                    # 1. Priority List Check
                    for p_org in priority_orgs:
                        if p_org in name:
                            bonus = rep_config.get("priority_organizer_bonus", 5.0)
                            score += bonus
                            rationale.append(f"+{bonus}: Priority Organizer '{p_org}'")
                            break
                    # 2. Loyalty Check (Backfilled Tally)
                    tally_path = N5_ROOT / "data" / "luma_organizer_tally.json"
                    if tally_path.exists():
                        with open(tally_path) as f:
                            tally = json.load(f)
                        
                        count = tally.get(org.get("name", ""), 0)
                        if count > 0:
                            # Formula: bonus * count (capped?)
                            # Let's use config multiplier
                            multiplier = rep_config.get("attended_organizer_multiplier", 0.5)
                            loyalty_bonus = count * multiplier
                            score += loyalty_bonus
                            rationale.append(f"+{loyalty_bonus}: Organizer Loyalty ({count} attended)")

            except:
                pass

            now = datetime.now(timezone.utc)
            days_until = (dt - now).days
            
            primary_window = booking_config.get("primary_window_days", {})
            opp_window = booking_config.get("opportunistic_window_days", {})
            
            if primary_window.get("min", 14) <= days_until <= primary_window.get("max", 21):
                score += 1.0
                rationale.append(f"+1.0: In primary booking window ({days_until} days out)")
            elif opp_window.get("min", 1) <= days_until <= opp_window.get("max", 7):
                score += 0.5
                rationale.append(f"+0.5: Opportunistic window ({days_until} days out)")
        except:
            pass
    
    return max(0, score), rationale


def score_all_pending(city: str = None) -> list[dict]:
    """Score all pending (unscored) events."""
    config = load_config()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM events
        WHERE digest_sent_at IS NULL
        AND rejected_at IS NULL
        AND event_datetime >= datetime('now')
    """
    params = []
    
    if city:
        query += " AND city = ?"
        params.append(city)
    
    query += " ORDER BY event_datetime ASC"
    
    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    
    scored_events = []
    for event in events:
        score, rationale = score_event(event, config)
        
        # Update database
        cursor.execute("""
            UPDATE events 
            SET score = ?, score_rationale = ?, scored_at = ?
            WHERE id = ?
        """, (score, json.dumps(rationale), datetime.now(timezone.utc).isoformat(), event["id"]))
        
        event["score"] = score
        event["score_rationale"] = rationale
        scored_events.append(event)
    
    conn.commit()
    conn.close()
    
    # Sort by score descending
    scored_events.sort(key=lambda x: x["score"], reverse=True)
    
    logger.info(f"Scored {len(scored_events)} events")
    return scored_events


def get_top_recommendations(city: str = None, limit: int = 10) -> list[dict]:
    """Get top recommended events by score."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM events
        WHERE digest_sent_at IS NULL
        AND rejected_at IS NULL
        AND approved_at IS NULL
        AND event_datetime >= datetime('now')
        AND score IS NOT NULL
    """
    params = []
    
    if city:
        query += " AND city = ?"
        params.append(city)
    
    query += " ORDER BY score DESC, event_datetime ASC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return events


def format_event_for_display(event: dict) -> str:
    """Format an event for human-readable display."""
    lines = []
    lines.append(f"📅 **{event.get('title', 'Untitled')}**")
    lines.append(f"   🕐 {event.get('event_date', '?')} at {event.get('event_time', '?')}")
    lines.append(f"   📍 {event.get('venue_name', 'Location TBD')}")
    lines.append(f"   💰 {event.get('price', 'Unknown')}")
    lines.append(f"   👥 {event.get('attendee_count', 0)} attending")
    lines.append(f"   ⭐ Score: {event.get('score', 0):.1f}/10")
    lines.append(f"   🔗 {event.get('url', '')}")
    
    rationale = event.get("score_rationale", [])
    if isinstance(rationale, str):
        try:
            rationale = json.loads(rationale)
        except:
            rationale = []
    
    if rationale:
        lines.append(f"   📊 {'; '.join(rationale[:3])}")
    
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Score Luma events")
    parser.add_argument("--city", default="nyc", help="City code")
    parser.add_argument("--top", type=int, default=10, help="Number of top events to show")
    parser.add_argument("--rescore", action="store_true", help="Rescore all events")
    args = parser.parse_args()
    
    # Score events
    scored = score_all_pending(args.city)
    
    # Get top recommendations
    top = get_top_recommendations(args.city, args.top)
    
    print(f"\n🎯 TOP {len(top)} RECOMMENDED EVENTS IN {args.city.upper()}\n")
    print("=" * 60)
    
    for i, event in enumerate(top, 1):
        print(f"\n#{i}")
        print(format_event_for_display(event))
        print("-" * 40)
    
    # Summary stats
    print(f"\n📊 SUMMARY")
    print(f"   Total events scored: {len(scored)}")
    if scored:
        avg_score = sum(e["score"] for e in scored) / len(scored)
        print(f"   Average score: {avg_score:.1f}")
        print(f"   Highest score: {scored[0]['score']:.1f} - {scored[0]['title'][:50]}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())






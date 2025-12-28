#!/usr/bin/env python3
"""
Life Accountability - Check for missed habits and generate nudges.

Usage:
    python3 life_accountability.py check meds     # Check if meds taken today
    python3 life_accountability.py daily          # Run all daily checks
    python3 life_accountability.py status         # Show accountability status
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "wellness.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_category(slug: str, quiet: bool = False) -> dict:
    """Check if a category has been logged today."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.name, c.sentiment,
               (SELECT COUNT(*) FROM life_logs WHERE category_id = c.id AND date(timestamp) = date('now')) as today_count,
               (SELECT MAX(timestamp) FROM life_logs WHERE category_id = c.id) as last_entry
        FROM life_categories c
        WHERE c.slug = ? AND c.active = 1
    """, (slug,))
    
    cat = cursor.fetchone()
    conn.close()
    
    if not cat:
        return {"error": f"Category '{slug}' not found"}
    
    result = {
        "slug": slug,
        "name": cat['name'],
        "sentiment": cat['sentiment'],
        "logged_today": cat['today_count'] > 0,
        "today_count": cat['today_count'],
        "last_entry": cat['last_entry']
    }
    
    if not quiet:
        if result['logged_today']:
            print(f"✅ {cat['name']}: Logged today ({cat['today_count']}x)")
        else:
            if cat['last_entry']:
                last = datetime.fromisoformat(cat['last_entry'].replace('T', ' ').split('.')[0])
                days_ago = (datetime.now() - last).days
                print(f"⚠️ {cat['name']}: NOT logged today (last: {days_ago} days ago)")
            else:
                print(f"⚠️ {cat['name']}: NOT logged today (never logged)")
    
    return result


def daily_check() -> dict:
    """Run daily accountability check for good habits."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all good habits
    cursor.execute("""
        SELECT c.slug, c.name,
               (SELECT COUNT(*) FROM life_logs WHERE category_id = c.id AND date(timestamp) = date('now')) as today_count,
               (SELECT MAX(timestamp) FROM life_logs WHERE category_id = c.id) as last_entry
        FROM life_categories c
        WHERE c.sentiment = 'good' AND c.active = 1
        ORDER BY c.name
    """)
    
    categories = cursor.fetchall()
    conn.close()
    
    missed = []
    completed = []
    
    print("\n📋 Daily Accountability Check")
    print("━" * 50)
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("━" * 50)
    
    for cat in categories:
        if cat['today_count'] > 0:
            completed.append(cat['name'])
            print(f"  ✅ {cat['name']}: Done ({cat['today_count']}x)")
        else:
            missed.append({
                "name": cat['name'],
                "slug": cat['slug'],
                "last_entry": cat['last_entry']
            })
            if cat['last_entry']:
                last = datetime.fromisoformat(cat['last_entry'].replace('T', ' ').split('.')[0])
                days_ago = (datetime.now() - last).days
                urgency = "🔴" if days_ago > 2 else "🟡"
                print(f"  {urgency} {cat['name']}: Missing (last: {days_ago}d ago)")
            else:
                print(f"  🟡 {cat['name']}: Missing (never started)")
    
    print("━" * 50)
    print(f"  Done: {len(completed)}/{len(categories)} │ Missing: {len(missed)}")
    
    # Generate nudge message if there are missed items
    if missed:
        print("\n📨 Nudge Message:")
        print("-" * 40)
        nudge = generate_nudge(missed)
        print(nudge)
    
    return {
        "completed": completed,
        "missed": missed,
        "total": len(categories)
    }


def generate_nudge(missed: list) -> str:
    """Generate a nudge message for missed habits."""
    if not missed:
        return "All good habits completed today! 🎉"
    
    if len(missed) == 1:
        item = missed[0]
        return f"Hey V - you haven't logged {item['name']} today. Quick +1?"
    
    names = [m['name'] for m in missed]
    if len(names) == 2:
        items_str = f"{names[0]} and {names[1]}"
    else:
        items_str = ", ".join(names[:-1]) + f", and {names[-1]}"
    
    return f"Hey V - still need to log: {items_str}. Which one first?"


def show_status():
    """Show overall accountability status."""
    conn = get_db()
    cursor = conn.cursor()
    
    print("\n📊 Accountability Status")
    print("━" * 60)
    
    # Good habits streak status
    cursor.execute("""
        SELECT c.name, c.slug,
               (SELECT COUNT(DISTINCT date(timestamp)) FROM life_logs 
                WHERE category_id = c.id AND timestamp >= datetime('now', '-7 days')) as days_this_week
        FROM life_categories c
        WHERE c.sentiment = 'good' AND c.active = 1
        ORDER BY days_this_week DESC
    """)
    
    habits = cursor.fetchall()
    
    print("\n🟢 Good Habits (This Week)")
    print("-" * 40)
    for h in habits:
        bar = "█" * h['days_this_week'] + "░" * (7 - h['days_this_week'])
        pct = h['days_this_week'] / 7 * 100
        print(f"  {h['name']:15} │ {bar} │ {h['days_this_week']}/7 ({pct:.0f}%)")
    
    # Bad habits this week
    cursor.execute("""
        SELECT c.name, c.slug,
               COALESCE(SUM(l.value), 0) as week_total
        FROM life_categories c
        LEFT JOIN life_logs l ON c.id = l.category_id AND l.timestamp >= datetime('now', '-7 days')
        WHERE c.sentiment = 'bad' AND c.active = 1
        GROUP BY c.id
        ORDER BY week_total DESC
    """)
    
    bad_habits = cursor.fetchall()
    
    print("\n🔴 Bad Habits (This Week)")
    print("-" * 40)
    for h in bad_habits:
        if h['week_total'] > 0:
            print(f"  {h['name']:15} │ {h['week_total']:.0f}x")
        else:
            print(f"  {h['name']:15} │ Clean ✨")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Life Accountability Checker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Check single category
    check_parser = subparsers.add_parser("check", help="Check if a category was logged today")
    check_parser.add_argument("slug", help="Category slug")
    
    # Daily check
    subparsers.add_parser("daily", help="Run daily accountability check")
    
    # Status
    subparsers.add_parser("status", help="Show accountability status")
    
    args = parser.parse_args()
    
    if args.command == "check":
        check_category(args.slug)
    elif args.command == "daily":
        daily_check()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


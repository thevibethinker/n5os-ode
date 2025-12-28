#!/usr/bin/env python3
"""
Life Counter CLI - GitHub for Life
Track habits, behaviors, and life events with increment-based logging.

Usage:
    python3 life_counter.py increment <slug> [value] [--note "optional note"]
    python3 life_counter.py +1 <slug>                    # Shorthand for increment
    python3 life_counter.py list                         # Show all categories
    python3 life_counter.py history <slug> [--days N]    # Recent history
    python3 life_counter.py add-category <slug> <name> [--sentiment good|bad|neutral]
    python3 life_counter.py stats [--days N]             # Summary statistics
    python3 life_counter.py today                        # Today's activity
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent / "data" / "wellness.db"


def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def increment(slug: str, value: float = 1, note: str = None, source: str = "manual"):
    """Increment a category counter."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find category
    cursor.execute("SELECT id, name, sentiment FROM life_categories WHERE slug = ? AND active = 1", (slug,))
    cat = cursor.fetchone()
    
    if not cat:
        # Try fuzzy match
        cursor.execute("SELECT slug, name FROM life_categories WHERE active = 1")
        all_cats = cursor.fetchall()
        suggestions = [c['slug'] for c in all_cats if slug.lower() in c['slug'].lower() or slug.lower() in c['name'].lower()]
        
        if suggestions:
            print(f"Category '{slug}' not found. Did you mean: {', '.join(suggestions)}?")
        else:
            print(f"Category '{slug}' not found. Use 'list' to see available categories.")
            print(f"Or add it with: python3 life_counter.py add-category {slug} \"{slug.title()}\"")
        conn.close()
        return False
    
    # Validate value - must be positive for counter categories
    if value <= 0:
        print(f"❌ Value must be positive (got {value}). Use positive numbers only.")
        conn.close()
        return False
    
    # Insert log entry
    cursor.execute(
        "INSERT INTO life_logs (category_id, value, source, note) VALUES (?, ?, ?, ?)",
        (cat['id'], value, source, note)
    )
    conn.commit()
    
    # Get today's total
    cursor.execute("""
        SELECT SUM(value) as total 
        FROM life_logs 
        WHERE category_id = ? AND date(timestamp) = date('now')
    """, (cat['id'],))
    today_total = cursor.fetchone()['total'] or 0
    
    sentiment_emoji = {"good": "✅", "bad": "⚠️", "neutral": "📊"}.get(cat['sentiment'], "📊")
    
    print(f"{sentiment_emoji} +{value:.0f} {cat['name']} logged")
    print(f"   Today's total: {today_total:.0f}")
    
    conn.close()
    return True


def list_categories():
    """List all active categories."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.slug, c.name, c.sentiment, c.description,
               (SELECT SUM(value) FROM life_logs WHERE category_id = c.id AND date(timestamp) = date('now')) as today,
               (SELECT SUM(value) FROM life_logs WHERE category_id = c.id AND timestamp >= datetime('now', '-7 days')) as week
        FROM life_categories c
        WHERE c.active = 1
        ORDER BY c.sentiment, c.name
    """)
    
    categories = cursor.fetchall()
    
    print("\n📊 Life Categories")
    print("=" * 60)
    
    current_sentiment = None
    for cat in categories:
        if cat['sentiment'] != current_sentiment:
            current_sentiment = cat['sentiment']
            emoji = {"good": "✅ GOOD HABITS", "bad": "⚠️ BAD HABITS", "neutral": "📊 NEUTRAL"}.get(current_sentiment, "OTHER")
            print(f"\n{emoji}")
            print("-" * 40)
        
        today = int(cat['today'] or 0)
        week = int(cat['week'] or 0)
        print(f"  {cat['slug']:15} │ Today: {today:3} │ Week: {week:4} │ {cat['name']}")
    
    print("\n" + "=" * 60)
    conn.close()


def add_category(slug: str, name: str, sentiment: str = "neutral", description: str = None):
    """Add a new category."""
    # Validate slug
    if not slug or not slug.strip():
        print("❌ Slug cannot be empty.")
        return
    
    slug = slug.strip().lower()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO life_categories (slug, name, sentiment, description) VALUES (?, ?, ?, ?)",
            (slug, name, sentiment, description)
        )
        conn.commit()
        print(f"✓ Added category: {slug} ({name}) - {sentiment}")
    except sqlite3.IntegrityError:
        print(f"Category '{slug}' already exists.")
    
    conn.close()


def show_history(slug: str, days: int = 14):
    """Show recent history for a category."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM life_categories WHERE slug = ?", (slug,))
    cat = cursor.fetchone()
    
    if not cat:
        print(f"Category '{slug}' not found.")
        conn.close()
        return
    
    cursor.execute("""
        SELECT date(timestamp) as day, SUM(value) as total, COUNT(*) as entries
        FROM life_logs
        WHERE category_id = ? AND timestamp >= datetime('now', ?)
        GROUP BY date(timestamp)
        ORDER BY day DESC
    """, (cat['id'], f'-{days} days'))
    
    history = cursor.fetchall()
    
    print(f"\n📅 {cat['name']} - Last {days} Days")
    print("=" * 40)
    
    for row in history:
        bar = "█" * min(int(row['total']), 20)
        print(f"  {row['day']} │ {row['total']:5.0f} │ {bar}")
    
    if not history:
        print("  No entries in this period.")
    
    conn.close()


def show_today():
    """Show all activity for today."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.name, c.sentiment, l.value, l.timestamp, l.note
        FROM life_logs l
        JOIN life_categories c ON l.category_id = c.id
        WHERE date(l.timestamp) = date('now')
        ORDER BY l.timestamp DESC
    """)
    
    logs = cursor.fetchall()
    
    print(f"\n📅 Today's Activity ({datetime.now().strftime('%Y-%m-%d')})")
    print("=" * 50)
    
    good_count = sum(l['value'] for l in logs if l['sentiment'] == 'good')
    bad_count = sum(l['value'] for l in logs if l['sentiment'] == 'bad')
    
    for log in logs:
        emoji = {"good": "✅", "bad": "⚠️", "neutral": "📊"}.get(log['sentiment'], "📊")
        time_str = datetime.fromisoformat(log['timestamp']).strftime('%H:%M')
        note_str = f" - {log['note']}" if log['note'] else ""
        print(f"  {time_str} │ {emoji} +{log['value']:.0f} {log['name']}{note_str}")
    
    if not logs:
        print("  No activity logged today.")
    else:
        print("-" * 50)
        print(f"  ✅ Good: {good_count:.0f}  │  ⚠️ Bad: {bad_count:.0f}  │  Net: {good_count - bad_count:+.0f}")
    
    conn.close()


def show_stats(days: int = 30):
    """Show summary statistics."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.name, c.sentiment, c.slug,
               SUM(l.value) as total,
               COUNT(DISTINCT date(l.timestamp)) as days_active,
               AVG(l.value) as avg_per_entry
        FROM life_categories c
        LEFT JOIN life_logs l ON c.id = l.category_id AND l.timestamp >= datetime('now', ?)
        WHERE c.active = 1
        GROUP BY c.id
        ORDER BY c.sentiment, total DESC
    """, (f'-{days} days',))
    
    stats = cursor.fetchall()
    
    print(f"\n📊 Life Stats - Last {days} Days")
    print("=" * 60)
    
    for stat in stats:
        if stat['total']:
            emoji = {"good": "✅", "bad": "⚠️", "neutral": "📊"}.get(stat['sentiment'], "📊")
            print(f"  {emoji} {stat['name']:20} │ Total: {stat['total']:5.0f} │ Days: {stat['days_active']:3}")
    
    conn.close()


def show_ledger():
    """Show THE LEDGER - bad habits with clean streaks."""
    conn = get_db()
    cursor = conn.cursor()
    
    print("\n🔴 THE LEDGER (Bad Habits - All Time)")
    print("━" * 70)
    
    cursor.execute("""
        SELECT c.id, c.name, c.slug,
               COALESCE(SUM(l.value), 0) as lifetime_total,
               MAX(l.timestamp) as last_entry
        FROM life_categories c
        LEFT JOIN life_logs l ON c.id = l.category_id
        WHERE c.sentiment = 'bad' AND c.active = 1
        GROUP BY c.id
        ORDER BY lifetime_total DESC
    """)
    
    categories = cursor.fetchall()
    
    for cat in categories:
        # Calculate clean streak (days since last entry)
        if cat['last_entry']:
            last_date = datetime.fromisoformat(cat['last_entry'].replace('T', ' ').split('.')[0])
            clean_days = (datetime.now() - last_date).days
        else:
            clean_days = float('inf')  # Never logged
        
        # Get longest clean streak
        cursor.execute("""
            SELECT date(timestamp) as log_date FROM life_logs
            WHERE category_id = ? ORDER BY log_date
        """, (cat['id'],))
        dates = [row['log_date'] for row in cursor.fetchall()]
        
        longest_clean = 0
        if dates:
            prev = None
            for d in dates:
                curr = datetime.strptime(d, '%Y-%m-%d')
                if prev:
                    gap = (curr - prev).days - 1
                    longest_clean = max(longest_clean, gap)
                prev = curr
        
        clean_str = f"{clean_days} days" if clean_days != float('inf') else "Never logged"
        longest_str = f"{longest_clean} days" if longest_clean > 0 else "N/A"
        
        warning = " ⚠️" if clean_days == 0 else ""
        
        print(f"  {cat['name']:18} │ {cat['lifetime_total']:5.0f} total │ Clean streak: {clean_str:12} │ Best: {longest_str}{warning}")
    
    if not categories:
        print("  No bad habits tracked yet.")
    
    conn.close()


def show_scoreboard():
    """Show THE SCOREBOARD - good habits with momentum."""
    conn = get_db()
    cursor = conn.cursor()
    
    print("\n🟢 THE SCOREBOARD (Good Habits - Momentum)")
    print("━" * 70)
    
    cursor.execute("""
        SELECT c.id, c.name, c.slug,
               COALESCE(SUM(l.value), 0) as lifetime_total
        FROM life_categories c
        LEFT JOIN life_logs l ON c.id = l.category_id
        WHERE c.sentiment = 'good' AND c.active = 1
        GROUP BY c.id
        ORDER BY lifetime_total DESC
    """)
    
    categories = cursor.fetchall()
    
    for cat in categories:
        # Calculate current streak (consecutive days with at least one entry)
        cursor.execute("""
            SELECT DISTINCT date(timestamp) as log_date FROM life_logs
            WHERE category_id = ? ORDER BY log_date DESC
        """, (cat['id'],))
        dates = [row['log_date'] for row in cursor.fetchall()]
        
        current_streak = 0
        best_streak = 0
        
        if dates:
            # Current streak
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if dates[0] in [today, yesterday]:
                current_streak = 1
                for i in range(1, len(dates)):
                    prev = datetime.strptime(dates[i-1], '%Y-%m-%d')
                    curr = datetime.strptime(dates[i], '%Y-%m-%d')
                    if (prev - curr).days == 1:
                        current_streak += 1
                    else:
                        break
            
            # Best streak
            streak = 1
            for i in range(1, len(dates)):
                prev = datetime.strptime(dates[i-1], '%Y-%m-%d')
                curr = datetime.strptime(dates[i], '%Y-%m-%d')
                if (prev - curr).days == 1:
                    streak += 1
                else:
                    best_streak = max(best_streak, streak)
                    streak = 1
            best_streak = max(best_streak, streak)
        
        fire = " 🔥" if current_streak >= 3 else ""
        room = " ← room to grow" if current_streak == 0 and cat['lifetime_total'] > 0 else ""
        
        print(f"  {cat['name']:18} │ {cat['lifetime_total']:5.0f} total │ Current: {current_streak:3} days{fire} │ Best: {best_streak} days{room}")
    
    if not categories:
        print("  No good habits tracked yet.")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Life Counter - GitHub for Life")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Increment
    inc_parser = subparsers.add_parser("increment", aliases=["+1", "inc", "+"], help="Increment a counter")
    inc_parser.add_argument("slug", help="Category slug (e.g., 'weed', 'workout')")
    inc_parser.add_argument("value", nargs="?", type=float, default=1, help="Value to add (default: 1)")
    inc_parser.add_argument("--note", "-n", help="Optional note")
    inc_parser.add_argument("--source", "-s", default="manual", help="Source of entry")
    
    # List
    subparsers.add_parser("list", aliases=["ls"], help="List all categories")
    
    # Ledger (bad habits)
    subparsers.add_parser("ledger", help="Show THE LEDGER - bad habits with clean streaks")
    
    # Scoreboard (good habits)
    subparsers.add_parser("scoreboard", aliases=["score"], help="Show THE SCOREBOARD - good habits with momentum")
    
    # Add category
    add_parser = subparsers.add_parser("add-category", aliases=["add"], help="Add a new category")
    add_parser.add_argument("slug", help="URL-friendly identifier")
    add_parser.add_argument("name", help="Display name")
    add_parser.add_argument("--sentiment", choices=["good", "bad", "neutral"], default="neutral")
    add_parser.add_argument("--description", "-d", help="Description")
    
    # History
    hist_parser = subparsers.add_parser("history", aliases=["hist"], help="Show history for a category")
    hist_parser.add_argument("slug", help="Category slug")
    hist_parser.add_argument("--days", type=int, default=14, help="Number of days")
    
    # Today
    subparsers.add_parser("today", help="Show today's activity")
    
    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show summary statistics")
    stats_parser.add_argument("--days", type=int, default=30, help="Number of days")
    
    args = parser.parse_args()
    
    if args.command in ["increment", "+1", "inc", "+"]:
        increment(args.slug, args.value, args.note, args.source)
    elif args.command in ["list", "ls"]:
        list_categories()
    elif args.command == "ledger":
        show_ledger()
    elif args.command in ["scoreboard", "score"]:
        show_scoreboard()
    elif args.command in ["add-category", "add"]:
        add_category(args.slug, args.name, args.sentiment, args.description)
    elif args.command in ["history", "hist"]:
        show_history(args.slug, args.days)
    elif args.command == "today":
        show_today()
    elif args.command == "stats":
        show_stats(args.days)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()




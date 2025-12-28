#!/usr/bin/env python3
"""
Life Visualization - GitHub-style contribution graphs for life tracking.

Usage:
    python3 life_viz.py graph <slug> [--weeks N]    # Show contribution graph
    python3 life_viz.py heatmap                      # Show all categories heatmap
    python3 life_viz.py streak <slug>                # Show current streak
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "wellness.db"

# GitHub-style intensity blocks
BLOCKS = [" ", "░", "▒", "▓", "█"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def contribution_graph(slug: str, weeks: int = 26):
    """Generate a GitHub-style contribution graph."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get category info
    cursor.execute("SELECT id, name, sentiment FROM life_categories WHERE slug = ?", (slug,))
    cat = cursor.fetchone()
    
    if not cat:
        print(f"Category '{slug}' not found.")
        conn.close()
        return
    
    # Get data for the time range
    start_date = datetime.now() - timedelta(weeks=weeks)
    
    cursor.execute("""
        SELECT date(timestamp) as day, SUM(value) as total
        FROM life_logs
        WHERE category_id = ? AND timestamp >= ?
        GROUP BY date(timestamp)
    """, (cat['id'], start_date.strftime('%Y-%m-%d')))
    
    data = {row['day']: row['total'] for row in cursor.fetchall()}
    conn.close()
    
    # Calculate max for intensity scaling
    max_val = max(data.values()) if data else 1
    
    # Build the grid (7 rows x N weeks)
    today = datetime.now().date()
    
    # Find the start of the grid (should be a Sunday, `weeks` weeks ago)
    grid_start = today - timedelta(days=today.weekday() + 1 + (weeks - 1) * 7)
    if grid_start.weekday() != 6:  # Adjust to Sunday
        grid_start -= timedelta(days=(grid_start.weekday() + 1) % 7)
    
    # Generate the graph
    sentiment_color = {"good": "\033[32m", "bad": "\033[31m", "neutral": "\033[34m"}.get(cat['sentiment'], "\033[0m")
    reset = "\033[0m"
    
    print(f"\n{sentiment_color}{'█' * 3}{reset} {cat['name']} - Last {weeks} Weeks")
    print("=" * (weeks + 10))
    
    # Month labels
    month_labels = []
    current_month = None
    for w in range(weeks):
        week_start = grid_start + timedelta(weeks=w)
        month = week_start.strftime('%b')
        if month != current_month:
            month_labels.append(month[:3])
            current_month = month
        else:
            month_labels.append("   ")
    
    print("     " + "".join(m[0] if m.strip() else " " for m in month_labels))
    
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    for day_idx in range(7):
        row = f"{days[day_idx][:1]}  "
        for week in range(weeks):
            date = grid_start + timedelta(weeks=week, days=day_idx)
            date_str = date.strftime('%Y-%m-%d')
            
            if date > today:
                row += " "
            elif date_str in data:
                intensity = min(4, int((data[date_str] / max_val) * 4) + 1) if max_val > 0 else 0
                row += f"{sentiment_color}{BLOCKS[intensity]}{reset}"
            else:
                row += BLOCKS[0]
        
        print(row)
    
    # Legend
    print(f"\n     Less {BLOCKS[0]}{BLOCKS[1]}{BLOCKS[2]}{BLOCKS[3]}{BLOCKS[4]} More")
    
    # Stats
    total = sum(data.values())
    active_days = len(data)
    
    print(f"\n     Total: {total:.0f} │ Active Days: {active_days} │ Avg: {total/max(active_days,1):.1f}/day")


def streak_info(slug: str):
    """Show current streak information."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, sentiment FROM life_categories WHERE slug = ?", (slug,))
    cat = cursor.fetchone()
    
    if not cat:
        print(f"Category '{slug}' not found.")
        conn.close()
        return
    
    # Get all dates with activity
    cursor.execute("""
        SELECT DISTINCT date(timestamp) as day
        FROM life_logs
        WHERE category_id = ?
        ORDER BY day DESC
    """, (cat['id'],))
    
    dates = [datetime.strptime(row['day'], '%Y-%m-%d').date() for row in cursor.fetchall()]
    conn.close()
    
    if not dates:
        print(f"No entries for '{slug}' yet.")
        return
    
    today = datetime.now().date()
    
    # Current streak
    current_streak = 0
    check_date = today
    
    for d in dates:
        if d == check_date or d == check_date - timedelta(days=1):
            current_streak += 1
            check_date = d - timedelta(days=1)
        else:
            break
    
    # Longest streak
    longest_streak = 0
    temp_streak = 1
    
    for i in range(1, len(dates)):
        if (dates[i-1] - dates[i]).days == 1:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 1
    longest_streak = max(longest_streak, temp_streak)
    
    emoji = "🔥" if current_streak >= 3 else "📊"
    
    print(f"\n{emoji} {cat['name']} Streak Info")
    print("=" * 40)
    print(f"  Current Streak:  {current_streak} days")
    print(f"  Longest Streak:  {longest_streak} days")
    print(f"  Total Entries:   {len(dates)} days")
    
    if cat['sentiment'] == 'good':
        if current_streak >= 7:
            print("\n  🏆 Amazing! Keep the momentum going!")
        elif current_streak >= 3:
            print("\n  🔥 Great streak! You're building a habit.")
        else:
            print("\n  💪 Keep going! Consistency is key.")
    elif cat['sentiment'] == 'bad':
        # For bad habits, we want to show days WITHOUT the behavior
        cursor = get_db().cursor()
        cursor.execute("""
            SELECT MAX(date(timestamp)) as last_entry
            FROM life_logs
            WHERE category_id = ?
        """, (cat['id'],))
        last = cursor.fetchone()
        
        if last and last['last_entry']:
            last_date = datetime.strptime(last['last_entry'], '%Y-%m-%d').date()
            days_clean = (today - last_date).days
            if days_clean > 0:
                print(f"\n  🌟 {days_clean} days clean! Stay strong!")
            else:
                print(f"\n  💪 Tomorrow is a new opportunity.")


def all_heatmap(weeks: int = 12):
    """Show a compact heatmap for all categories."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.slug, c.name, c.sentiment
        FROM life_categories c
        WHERE c.active = 1
        ORDER BY c.sentiment, c.name
    """)
    
    categories = cursor.fetchall()
    
    print(f"\n📊 All Categories - Last {weeks} Weeks")
    print("=" * 60)
    
    today = datetime.now().date()
    start_date = today - timedelta(weeks=weeks)
    
    for cat in categories:
        cursor.execute("""
            SELECT date(timestamp) as day, SUM(value) as total
            FROM life_logs
            WHERE category_id = ? AND timestamp >= ?
            GROUP BY date(timestamp)
        """, (cat['id'], start_date.strftime('%Y-%m-%d')))
        
        data = {row['day']: row['total'] for row in cursor.fetchall()}
        max_val = max(data.values()) if data else 1
        
        sentiment_color = {"good": "\033[32m", "bad": "\033[31m", "neutral": "\033[34m"}.get(cat['sentiment'], "\033[0m")
        reset = "\033[0m"
        
        # Compact row: one character per day for last N weeks
        row = ""
        for i in range(weeks * 7):
            date = start_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            if date > today:
                row += " "
            elif date_str in data:
                intensity = min(4, int((data[date_str] / max_val) * 4) + 1) if max_val > 0 else 0
                row += f"{sentiment_color}{BLOCKS[intensity]}{reset}"
            else:
                row += "·"
        
        # Truncate to fit, show last portion
        display_row = row[-(weeks*7):]
        total = sum(data.values())
        print(f"  {cat['slug']:12} │ {display_row} │ {total:4.0f}")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Life Visualization - GitHub-style graphs")
    subparsers = parser.add_subparsers(dest="command")
    
    # Graph
    graph_parser = subparsers.add_parser("graph", help="Show contribution graph")
    graph_parser.add_argument("slug", help="Category slug")
    graph_parser.add_argument("--weeks", type=int, default=26, help="Number of weeks to show")
    
    # Streak
    streak_parser = subparsers.add_parser("streak", help="Show streak info")
    streak_parser.add_argument("slug", help="Category slug")
    
    # Heatmap
    heatmap_parser = subparsers.add_parser("heatmap", help="Show all categories")
    heatmap_parser.add_argument("--weeks", type=int, default=12, help="Number of weeks")
    
    args = parser.parse_args()
    
    if args.command == "graph":
        contribution_graph(args.slug, args.weeks)
    elif args.command == "streak":
        streak_info(args.slug)
    elif args.command == "heatmap":
        all_heatmap(args.weeks)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


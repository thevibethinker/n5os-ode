#!/usr/bin/env python3
"""
Life Patterns - Correlation engine for habit-outcome analysis.

Usage:
    python3 life_patterns.py correlate workout sleep     # Does working out improve sleep?
    python3 life_patterns.py correlate weed sleep        # Does weed affect sleep?
    python3 life_patterns.py weekly workout              # Weekly pattern for workout
    python3 life_patterns.py report                      # Full patterns report
"""

import argparse
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, stdev

LIFE_DB = Path(__file__).parent.parent / "data" / "wellness.db"
FITBIT_DB = Path("/home/workspace/Personal/Health/workouts.db")


def get_life_db():
    conn = sqlite3.connect(LIFE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_fitbit_db():
    if not FITBIT_DB.exists():
        return None
    conn = sqlite3.connect(FITBIT_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_sleep_data(days: int = 90) -> dict:
    """Get sleep data indexed by date."""
    conn = get_fitbit_db()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, minutes_asleep, minutes_in_bed
        FROM daily_sleep
        WHERE date >= date('now', ?)
        ORDER BY date
    """, (f'-{days} days',))
    
    sleep_data = {}
    for row in cursor.fetchall():
        if row['minutes_asleep'] and row['minutes_asleep'] > 180:  # Filter out naps (<3h)
            sleep_data[row['date']] = {
                'minutes_asleep': row['minutes_asleep'],
                'efficiency': (row['minutes_asleep'] / row['minutes_in_bed'] * 100) if row['minutes_in_bed'] else 0
            }
    
    conn.close()
    return sleep_data


def get_habit_days(slug: str, days: int = 90) -> set:
    """Get set of dates when habit was logged."""
    conn = get_life_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT date(l.timestamp) as log_date
        FROM life_logs l
        JOIN life_categories c ON l.category_id = c.id
        WHERE c.slug = ? AND l.timestamp >= datetime('now', ?)
    """, (slug, f'-{days} days'))
    
    dates = {row['log_date'] for row in cursor.fetchall()}
    conn.close()
    return dates


def correlate_habit_sleep(habit_slug: str, days: int = 90):
    """Analyze correlation between a habit and sleep quality."""
    sleep_data = get_sleep_data(days)
    habit_days = get_habit_days(habit_slug, days)
    
    if not sleep_data:
        print("❌ No sleep data available. Is Fitbit sync running?")
        return
    
    if not habit_days:
        print(f"❌ No data for habit '{habit_slug}' in the last {days} days.")
        return
    
    # Compare sleep on days AFTER habit vs days without habit
    sleep_after_habit = []
    sleep_after_no_habit = []
    
    for date_str, sleep in sleep_data.items():
        # Check if habit was done the day before
        prev_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        
        if prev_date in habit_days:
            sleep_after_habit.append(sleep['minutes_asleep'])
        else:
            sleep_after_no_habit.append(sleep['minutes_asleep'])
    
    # Get category info
    conn = get_life_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, sentiment FROM life_categories WHERE slug = ?", (habit_slug,))
    cat = cursor.fetchone()
    conn.close()
    
    cat_name = cat['name'] if cat else habit_slug
    
    print(f"\n🔬 Correlation Analysis: {cat_name} → Sleep")
    print("━" * 60)
    
    if len(sleep_after_habit) < 3 or len(sleep_after_no_habit) < 3:
        print(f"⚠️ Not enough data for reliable analysis.")
        print(f"   Nights after {cat_name}: {len(sleep_after_habit)}")
        print(f"   Nights without: {len(sleep_after_no_habit)}")
        return
    
    avg_with = mean(sleep_after_habit)
    avg_without = mean(sleep_after_no_habit)
    diff = avg_with - avg_without
    diff_pct = (diff / avg_without) * 100 if avg_without else 0
    
    print(f"\n   📊 Sleep after {cat_name}: {avg_with:.0f} min ({len(sleep_after_habit)} nights)")
    print(f"   📊 Sleep without:        {avg_without:.0f} min ({len(sleep_after_no_habit)} nights)")
    print(f"\n   Δ Difference: {diff:+.0f} min ({diff_pct:+.1f}%)")
    
    # Interpretation
    print("\n   📝 Interpretation:")
    if abs(diff) < 10:
        print(f"   → No significant correlation detected.")
    elif diff > 0:
        print(f"   → {cat_name} appears to IMPROVE sleep by ~{diff:.0f} min")
        if cat['sentiment'] == 'good':
            print(f"   ✅ Keep it up!")
        else:
            print(f"   ⚠️ Interesting - this 'bad' habit may have benefits to consider.")
    else:
        print(f"   → {cat_name} appears to REDUCE sleep by ~{abs(diff):.0f} min")
        if cat['sentiment'] == 'bad':
            print(f"   ⚠️ Another reason to reduce this habit.")
        else:
            print(f"   🤔 Consider timing - maybe do this earlier in the day?")


def weekly_pattern(slug: str, weeks: int = 8):
    """Show weekly pattern for a habit."""
    conn = get_life_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.name FROM life_categories c WHERE c.slug = ?
    """, (slug,))
    cat = cursor.fetchone()
    
    if not cat:
        print(f"Category '{slug}' not found.")
        conn.close()
        return
    
    # Get day-of-week distribution
    cursor.execute("""
        SELECT 
            CASE CAST(strftime('%w', timestamp) AS INTEGER)
                WHEN 0 THEN 'Sun'
                WHEN 1 THEN 'Mon'
                WHEN 2 THEN 'Tue'
                WHEN 3 THEN 'Wed'
                WHEN 4 THEN 'Thu'
                WHEN 5 THEN 'Fri'
                WHEN 6 THEN 'Sat'
            END as day_name,
            CAST(strftime('%w', timestamp) AS INTEGER) as day_num,
            COUNT(*) as count
        FROM life_logs l
        JOIN life_categories c ON l.category_id = c.id
        WHERE c.slug = ? AND l.timestamp >= datetime('now', ?)
        GROUP BY day_num
        ORDER BY day_num
    """, (slug, f'-{weeks * 7} days'))
    
    days = {row['day_num']: {'name': row['day_name'], 'count': row['count']} for row in cursor.fetchall()}
    
    print(f"\n📅 Weekly Pattern: {cat['name']} (last {weeks} weeks)")
    print("━" * 50)
    
    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    max_count = max((days.get(i, {}).get('count', 0) for i in range(7)), default=1)
    
    for i in range(7):
        count = days.get(i, {}).get('count', 0)
        bar_len = int((count / max_count) * 20) if max_count else 0
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {day_names[i]} │ {bar} │ {count}")
    
    # Find best/worst days
    if days:
        best_day = max(days.items(), key=lambda x: x[1]['count'])
        worst_day = min(days.items(), key=lambda x: x[1]['count'])
        print(f"\n  📈 Best day: {best_day[1]['name']} ({best_day[1]['count']}x)")
        print(f"  📉 Least active: {worst_day[1]['name']} ({worst_day[1]['count']}x)")
    
    conn.close()


def full_report():
    """Generate full patterns report."""
    conn = get_life_db()
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("   📊 LIFE PATTERNS REPORT")
    print("=" * 60)
    
    # Get all active categories with data
    cursor.execute("""
        SELECT c.slug, c.name, c.sentiment, COUNT(l.id) as total
        FROM life_categories c
        LEFT JOIN life_logs l ON c.id = l.category_id
        WHERE c.active = 1
        GROUP BY c.id
        HAVING total > 0
        ORDER BY c.sentiment, total DESC
    """)
    
    categories = cursor.fetchall()
    conn.close()
    
    # Sleep correlations
    sleep_data = get_sleep_data(90)
    if sleep_data:
        print("\n🔬 SLEEP CORRELATIONS (Last 90 Days)")
        print("-" * 50)
        
        for cat in categories:
            habit_days = get_habit_days(cat['slug'], 90)
            if len(habit_days) < 5:
                continue
            
            sleep_after = []
            sleep_without = []
            
            for date_str, sleep in sleep_data.items():
                prev_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                if prev_date in habit_days:
                    sleep_after.append(sleep['minutes_asleep'])
                else:
                    sleep_without.append(sleep['minutes_asleep'])
            
            if len(sleep_after) >= 3 and len(sleep_without) >= 3:
                diff = mean(sleep_after) - mean(sleep_without)
                emoji = "✅" if diff > 10 else ("⚠️" if diff < -10 else "➖")
                print(f"  {emoji} {cat['name']:18} → Sleep: {diff:+.0f} min")
    
    # Weekly patterns summary
    print("\n📅 WEEKLY PATTERNS")
    print("-" * 50)
    
    for cat in categories[:5]:  # Top 5 by activity
        weekly_pattern(cat['slug'], weeks=4)


def main():
    parser = argparse.ArgumentParser(description="Life Patterns - Correlation Engine")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Correlate
    corr_parser = subparsers.add_parser("correlate", help="Analyze habit-outcome correlation")
    corr_parser.add_argument("habit", help="Habit slug (e.g., 'workout', 'weed')")
    corr_parser.add_argument("outcome", choices=["sleep"], help="Outcome to analyze")
    corr_parser.add_argument("--days", type=int, default=90, help="Days to analyze")
    
    # Weekly
    week_parser = subparsers.add_parser("weekly", help="Show weekly pattern")
    week_parser.add_argument("slug", help="Category slug")
    week_parser.add_argument("--weeks", type=int, default=8, help="Weeks to analyze")
    
    # Full report
    subparsers.add_parser("report", help="Full patterns report")
    
    args = parser.parse_args()
    
    if args.command == "correlate":
        if args.outcome == "sleep":
            correlate_habit_sleep(args.habit, args.days)
    elif args.command == "weekly":
        weekly_pattern(args.slug, args.weeks)
    elif args.command == "report":
        full_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Journal Synthesis - Weekly/Monthly Digest Generator

Generates insights and patterns from journal entries over time.
Can be run on-demand or as a scheduled weekly task.
"""

import sqlite3
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import sys

DB_PATH = Path("/home/workspace/N5/data/journal.db")
DIGEST_DIR = Path("/home/workspace/N5/digests")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_entries(days: int):
    """Fetch journal entries for the specified period."""
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT id, created_at, entry_type, content, mood, tags, word_count
        FROM journal_entries 
        WHERE created_at >= ?
        ORDER BY created_at
    """, (cutoff.isoformat(),))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def analyze_mood_patterns(entries: list) -> dict:
    """Analyze mood patterns and trends."""
    mood_by_day = defaultdict(list)
    mood_counts = Counter()
    
    for entry in entries:
        if entry['mood']:
            day = entry['created_at'][:10]
            mood_by_day[day].append(entry['mood'])
            mood_counts[entry['mood']] += 1
    
    # Check for mood on days with morning pages
    morning_page_days = set()
    for entry in entries:
        if entry['entry_type'] == 'morning_pages':
            morning_page_days.add(entry['created_at'][:10])
    
    moods_on_mp_days = []
    moods_on_non_mp_days = []
    
    for day, moods in mood_by_day.items():
        if day in morning_page_days:
            moods_on_mp_days.extend(moods)
        else:
            moods_on_non_mp_days.extend(moods)
    
    return {
        'total_mood_entries': sum(mood_counts.values()),
        'mood_distribution': dict(mood_counts.most_common()),
        'days_with_morning_pages': len(morning_page_days),
        'moods_on_mp_days': len(moods_on_mp_days),
        'moods_on_non_mp_days': len(moods_on_non_mp_days),
    }

def analyze_entry_types(entries: list) -> dict:
    """Analyze entry type distribution."""
    type_counts = Counter()
    type_by_weekday = defaultdict(lambda: Counter())
    
    for entry in entries:
        entry_type = entry['entry_type']
        type_counts[entry_type] += 1
        
        # Get weekday (0=Monday, 6=Sunday)
        try:
            dt = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
            weekday = dt.strftime('%A')
            type_by_weekday[weekday][entry_type] += 1
        except:
            pass
    
    return {
        'type_distribution': dict(type_counts),
        'by_weekday': {k: dict(v) for k, v in type_by_weekday.items()},
    }

def analyze_temptation_patterns(entries: list) -> dict:
    """Deep analysis of temptation entries."""
    temptation_entries = [e for e in entries if e['entry_type'] == 'temptation']
    
    by_hour = Counter()
    by_weekday = Counter()
    
    for entry in temptation_entries:
        try:
            dt = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
            by_hour[dt.hour] += 1
            by_weekday[dt.strftime('%A')] += 1
        except:
            pass
    
    # Find cluster patterns
    clusters = []
    if by_hour:
        peak_hour = by_hour.most_common(1)[0][0]
        clusters.append(f"Peak hour: {peak_hour}:00")
    if by_weekday:
        peak_day = by_weekday.most_common(1)[0][0]
        clusters.append(f"Peak day: {peak_day}")
    
    return {
        'total': len(temptation_entries),
        'by_hour': dict(sorted(by_hour.items())),
        'by_weekday': dict(by_weekday),
        'clusters': clusters,
    }

def analyze_tags(entries: list) -> dict:
    """Analyze tag usage and patterns."""
    all_tags = Counter()
    structured_tags = defaultdict(Counter)  # mood:X, trigger:X, theme:X
    
    for entry in entries:
        if entry['tags']:
            tags = [t.strip() for t in entry['tags'].split(',') if t.strip()]
            for tag in tags:
                all_tags[tag] += 1
                # Check for structured tags
                if ':' in tag:
                    category, value = tag.split(':', 1)
                    structured_tags[category][value] += 1
    
    return {
        'top_tags': dict(all_tags.most_common(15)),
        'structured_categories': {k: dict(v.most_common(5)) for k, v in structured_tags.items()},
    }

def analyze_word_patterns(entries: list) -> dict:
    """Analyze writing patterns."""
    word_counts = [e['word_count'] for e in entries if e['word_count']]
    
    if not word_counts:
        return {'avg_words': 0, 'total_words': 0, 'entries': 0}
    
    return {
        'avg_words': round(sum(word_counts) / len(word_counts), 1),
        'total_words': sum(word_counts),
        'entries': len(word_counts),
        'min_words': min(word_counts),
        'max_words': max(word_counts),
    }

def generate_insights(analysis: dict) -> list:
    """Generate human-readable insights from analysis."""
    insights = []
    
    # Mood insights
    mood = analysis.get('mood_patterns', {})
    if mood.get('days_with_morning_pages', 0) > 0:
        mp_days = mood['days_with_morning_pages']
        insights.append(f"You did morning pages on {mp_days} days this period.")
    
    # Temptation insights
    tempt = analysis.get('temptation_patterns', {})
    if tempt.get('clusters'):
        for cluster in tempt['clusters']:
            insights.append(f"Temptation pattern: {cluster}")
    
    if tempt.get('total', 0) > 0:
        insights.append(f"You logged {tempt['total']} temptation check-ins.")
    
    # Entry type insights
    types = analysis.get('entry_types', {})
    dist = types.get('type_distribution', {})
    if dist:
        total = sum(dist.values())
        insights.append(f"Total entries: {total}")
        for entry_type, count in sorted(dist.items(), key=lambda x: -x[1])[:3]:
            pct = round(count/total*100, 1)
            insights.append(f"  - {entry_type}: {count} ({pct}%)")
    
    # Writing volume
    words = analysis.get('word_patterns', {})
    if words.get('total_words', 0) > 0:
        insights.append(f"You wrote {words['total_words']:,} words across {words['entries']} entries.")
        insights.append(f"Average entry length: {words['avg_words']} words")
    
    # Tag insights
    tags = analysis.get('tag_patterns', {})
    top_tags = tags.get('top_tags', {})
    if top_tags:
        top_3 = list(top_tags.items())[:3]
        tag_str = ', '.join([f"{t[0]} ({t[1]})" for t in top_3])
        insights.append(f"Top tags: {tag_str}")
    
    return insights

def generate_digest(period: str = 'weekly') -> dict:
    """Generate a full synthesis digest."""
    days = 7 if period == 'weekly' else 30
    
    entries = get_entries(days)
    
    if not entries:
        return {
            'period': period,
            'days': days,
            'generated_at': datetime.now().isoformat(),
            'message': 'No entries found for this period.',
            'insights': [],
        }
    
    analysis = {
        'mood_patterns': analyze_mood_patterns(entries),
        'entry_types': analyze_entry_types(entries),
        'temptation_patterns': analyze_temptation_patterns(entries),
        'tag_patterns': analyze_tags(entries),
        'word_patterns': analyze_word_patterns(entries),
    }
    
    insights = generate_insights(analysis)
    
    return {
        'period': period,
        'days': days,
        'generated_at': datetime.now().isoformat(),
        'entry_count': len(entries),
        'date_range': {
            'start': entries[0]['created_at'][:10] if entries else None,
            'end': entries[-1]['created_at'][:10] if entries else None,
        },
        'analysis': analysis,
        'insights': insights,
    }

def format_digest_markdown(digest: dict) -> str:
    """Format digest as readable markdown."""
    lines = []
    lines.append(f"# Journal Synthesis - {digest['period'].title()} Report")
    lines.append(f"*Generated: {digest['generated_at'][:16]}*")
    lines.append("")
    
    if digest.get('message'):
        lines.append(f"_{digest['message']}_")
        return '\n'.join(lines)
    
    lines.append(f"**Period:** {digest['days']} days ({digest['date_range']['start']} to {digest['date_range']['end']})")
    lines.append(f"**Total Entries:** {digest['entry_count']}")
    lines.append("")
    
    lines.append("## Key Insights")
    for insight in digest.get('insights', []):
        lines.append(f"- {insight}")
    lines.append("")
    
    # Entry types
    analysis = digest.get('analysis', {})
    entry_types = analysis.get('entry_types', {}).get('type_distribution', {})
    if entry_types:
        lines.append("## Entry Types")
        for etype, count in sorted(entry_types.items(), key=lambda x: -x[1]):
            lines.append(f"- **{etype}**: {count}")
        lines.append("")
    
    # Mood distribution
    moods = analysis.get('mood_patterns', {}).get('mood_distribution', {})
    if moods:
        lines.append("## Mood Distribution")
        for mood, count in sorted(moods.items(), key=lambda x: -x[1]):
            lines.append(f"- {mood}: {count}")
        lines.append("")
    
    # Temptation patterns
    tempt = analysis.get('temptation_patterns', {})
    if tempt.get('total', 0) > 0:
        lines.append("## Temptation Patterns")
        lines.append(f"- Total check-ins: {tempt['total']}")
        if tempt.get('by_weekday'):
            peak = max(tempt['by_weekday'].items(), key=lambda x: x[1])
            lines.append(f"- Peak day: {peak[0]} ({peak[1]} entries)")
        if tempt.get('by_hour'):
            peak = max(tempt['by_hour'].items(), key=lambda x: x[1])
            lines.append(f"- Peak hour: {peak[0]}:00 ({peak[1]} entries)")
        lines.append("")
    
    # Tags
    tags = analysis.get('tag_patterns', {})
    top_tags = tags.get('top_tags', {})
    if top_tags:
        lines.append("## Top Tags")
        for tag, count in list(top_tags.items())[:10]:
            lines.append(f"- `{tag}`: {count}")
        lines.append("")
    
    return '\n'.join(lines)

def save_digest(digest: dict, output_path: Path = None):
    """Save digest to file."""
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    
    if output_path is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_path = DIGEST_DIR / f"journal-synthesis-{digest['period']}-{date_str}.md"
    
    markdown = format_digest_markdown(digest)
    output_path.write_text(markdown)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Journal Synthesis - Generate reflection digests")
    parser.add_argument('--period', choices=['weekly', 'monthly'], default='weekly',
                       help='Analysis period (default: weekly)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    parser.add_argument('--save', action='store_true', help='Save to digest file')
    parser.add_argument('--output', type=str, help='Custom output path')
    args = parser.parse_args()
    
    digest = generate_digest(args.period)
    
    if args.json:
        print(json.dumps(digest, indent=2, default=str))
    else:
        print(format_digest_markdown(digest))
    
    if args.save or args.output:
        output_path = Path(args.output) if args.output else None
        saved_path = save_digest(digest, output_path)
        print(f"\n---\nSaved to: {saved_path}", file=sys.stderr)

if __name__ == "__main__":
    main()


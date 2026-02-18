#!/usr/bin/env python3
"""
Zo Hotline Call Analyzer

Analyzes hotline call data from DuckDB to extract patterns, statistics, and insights.
"""

import argparse
import duckdb
import json
import os
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import requests


DB_PATH = '/home/workspace/Datasets/zo-hotline-calls/data.duckdb'
ZO_API_URL = 'https://api.zo.computer/zo/ask'


def get_zo_token() -> str:
    """Get Zo API token from environment."""
    token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set in environment", file=sys.stderr)
        sys.exit(1)
    return token


def query_calls(conn: duckdb.DuckDBPyConnection, min_duration: Optional[int] = None,
                start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query calls from DuckDB with optional filters."""
    conditions = []
    if min_duration:
        conditions.append(f"duration_seconds >= {min_duration}")
    if start_date:
        conditions.append(f"started_at >= '{start_date}'")
    if end_date:
        conditions.append(f"started_at <= '{end_date}'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            id,
            started_at,
            ended_at,
            duration_seconds,
            topics_discussed,
            level_assessed,
            escalation_requested,
            raw_data
        FROM calls
        {where_clause}
        ORDER BY started_at
    """

    rows = conn.execute(query).fetchall()
    calls = []
    for row in rows:
        raw_data = json.loads(row[7]) if row[7] else {}
        calls.append({
            'id': row[0],
            'started_at': row[1],
            'ended_at': row[2],
            'duration_seconds': row[3],
            'topics_discussed': row[4],
            'level_assessed': row[5],
            'escalation_requested': row[6],
            'raw_data': raw_data
        })
    return calls


def extract_transcript(raw_data: Dict) -> Optional[str]:
    """Extract transcript from raw_data JSON."""
    try:
        return raw_data.get('message', {}).get('artifact', {}).get('transcript')
    except (KeyError, AttributeError):
        return None


def extract_summary(raw_data: Dict) -> Optional[str]:
    """Extract Vapi summary from raw_data JSON."""
    try:
        return raw_data.get('message', {}).get('analysis', {}).get('summary')
    except (KeyError, AttributeError):
        return None


def extract_ended_reason(raw_data: Dict) -> Optional[str]:
    """Extract call end reason from raw_data JSON."""
    try:
        return raw_data.get('message', {}).get('endedReason')
    except (KeyError, AttributeError):
        return None


def extract_cost(raw_data: Dict) -> Optional[float]:
    """Extract call cost from raw_data JSON."""
    try:
        return raw_data.get('message', {}).get('cost')
    except (KeyError, AttributeError):
        return None


def analyze_transcript_with_zo(transcript: str, token: str) -> Dict[str, Any]:
    """
    Use Zo API to analyze a transcript and extract patterns.

    Returns dict with: topics, caller_level, quality_score, key_questions, was_helpful
    """
    prompt = f"""Analyze this hotline call transcript and extract the following information.

Transcript:
{transcript}

Return ONLY valid JSON with these exact fields:
{{
  "topics": ["topic1", "topic2"],  // List of topics discussed (e.g., "calendar_automation", "meeting_intelligence", "email_management")
  "caller_level": "beginner|intermediate|advanced",  // Technical sophistication level
  "quality_score": 1-5,  // Overall conversation quality (1=poor, 5=excellent)
  "key_questions": ["question1", "question2"],  // Main questions the caller asked
  "was_helpful": true|false  // Whether Zoseph provided useful guidance
}}"""

    try:
        response = requests.post(
            ZO_API_URL,
            json={'prompt': prompt},
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        response.raise_for_status()

        # Parse response - extract JSON from response
        result_text = response.json().get('response', '')

        # Try to parse as JSON
        try:
            # Remove markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            analysis = json.loads(result_text)
            return analysis
        except json.JSONDecodeError:
            # If not valid JSON, return empty analysis
            print(f"Warning: Could not parse Zo response as JSON: {result_text[:200]}", file=sys.stderr)
            return {
                'topics': [],
                'caller_level': 'unknown',
                'quality_score': 0,
                'key_questions': [],
                'was_helpful': False
            }
    except Exception as e:
        print(f"Warning: Zo API call failed: {e}", file=sys.stderr)
        return {
            'topics': [],
            'caller_level': 'unknown',
            'quality_score': 0,
            'key_questions': [],
            'was_helpful': False
        }


def compute_statistics(calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate statistics from calls."""
    stats = {
        'total_calls': len(calls),
        'by_day': defaultdict(int),
        'duration_buckets': {
            '<10s': 0,
            '10-60s': 0,
            '1-2min': 0,
            '2-5min': 0,
            '5min+': 0
        },
        'durations': [],
        'topics': Counter(),
        'escalations': 0,
        'total_cost': 0.0,
        'end_reasons': Counter()
    }

    for call in calls:
        # By day
        if call['started_at']:
            day = call['started_at'].date() if hasattr(call['started_at'], 'date') else str(call['started_at'])[:10]
            stats['by_day'][str(day)] += 1

        # Duration buckets
        duration = call['duration_seconds'] or 0
        stats['durations'].append(duration)

        if duration < 10:
            stats['duration_buckets']['<10s'] += 1
        elif duration < 60:
            stats['duration_buckets']['10-60s'] += 1
        elif duration < 120:
            stats['duration_buckets']['1-2min'] += 1
        elif duration < 300:
            stats['duration_buckets']['2-5min'] += 1
        else:
            stats['duration_buckets']['5min+'] += 1

        # Topics
        if call['topics_discussed']:
            stats['topics'][call['topics_discussed']] += 1

        # Escalations
        if call['escalation_requested']:
            stats['escalations'] += 1

        # Cost
        cost = extract_cost(call['raw_data'])
        if cost:
            stats['total_cost'] += cost

        # End reason
        reason = extract_ended_reason(call['raw_data'])
        if reason:
            stats['end_reasons'][reason] += 1

    # Compute average duration
    if stats['durations']:
        stats['avg_duration'] = sum(stats['durations']) / len(stats['durations'])
    else:
        stats['avg_duration'] = 0

    return stats


def analyze_patterns(calls: List[Dict[str, Any]], token: str, min_duration: int = 120) -> List[Dict[str, Any]]:
    """
    Extract conversation patterns from substantive calls (>2min by default).
    Uses Zo API to analyze transcripts.
    """
    patterns = []

    substantive_calls = [c for c in calls if (c['duration_seconds'] or 0) >= min_duration]

    print(f"Analyzing {len(substantive_calls)} substantive calls (>={min_duration}s)...", file=sys.stderr)

    for i, call in enumerate(substantive_calls, 1):
        print(f"  [{i}/{len(substantive_calls)}] Analyzing call {call['id']}...", file=sys.stderr)

        transcript = extract_transcript(call['raw_data'])
        if not transcript:
            print(f"    Warning: No transcript found for call {call['id']}", file=sys.stderr)
            continue

        analysis = analyze_transcript_with_zo(transcript, token)

        patterns.append({
            'call_id': call['id'],
            'started_at': call['started_at'],
            'duration': call['duration_seconds'],
            'summary': extract_summary(call['raw_data']),
            'analysis': analysis
        })

    return patterns


def format_report(stats: Dict[str, Any], patterns: Optional[List[Dict[str, Any]]] = None) -> str:
    """Generate markdown report from statistics and patterns."""
    lines = [
        "# Zo Hotline Call Analysis Report",
        f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n## Overview",
        f"\n- **Total Calls:** {stats['total_calls']}",
        f"- **Average Duration:** {stats['avg_duration']:.1f}s ({stats['avg_duration']/60:.1f} min)",
        f"- **Total Cost:** ${stats['total_cost']:.4f}",
        f"- **Escalation Rate:** {stats['escalations']}/{stats['total_calls']} ({100*stats['escalations']/stats['total_calls'] if stats['total_calls'] > 0 else 0:.1f}%)",
        f"\n## Call Volume by Day",
        ""
    ]

    for day, count in sorted(stats['by_day'].items()):
        lines.append(f"- **{day}:** {count} calls")

    lines.extend([
        f"\n## Duration Distribution",
        ""
    ])

    for bucket, count in stats['duration_buckets'].items():
        pct = 100 * count / stats['total_calls'] if stats['total_calls'] > 0 else 0
        lines.append(f"- **{bucket}:** {count} calls ({pct:.1f}%)")

    if stats['topics']:
        lines.extend([
            f"\n## Topics Discussed",
            ""
        ])
        for topic, count in stats['topics'].most_common():
            pct = 100 * count / stats['total_calls'] if stats['total_calls'] > 0 else 0
            lines.append(f"- **{topic}:** {count} calls ({pct:.1f}%)")

    if stats['end_reasons']:
        lines.extend([
            f"\n## Call End Reasons",
            ""
        ])
        for reason, count in stats['end_reasons'].most_common():
            pct = 100 * count / stats['total_calls'] if stats['total_calls'] > 0 else 0
            lines.append(f"- **{reason}:** {count} calls ({pct:.1f}%)")

    if patterns:
        lines.extend([
            f"\n## Conversation Patterns (Substantive Calls)",
            f"\n**Analyzed {len(patterns)} calls >2min**",
            ""
        ])

        # Aggregate pattern insights
        all_topics = []
        level_counts = Counter()
        quality_scores = []
        helpful_count = 0

        for p in patterns:
            analysis = p['analysis']
            all_topics.extend(analysis.get('topics', []))
            level = analysis.get('caller_level', 'unknown')
            level_counts[level] += 1
            quality = analysis.get('quality_score', 0)
            if quality > 0:
                quality_scores.append(quality)
            if analysis.get('was_helpful'):
                helpful_count += 1

        topic_freq = Counter(all_topics)

        lines.extend([
            "### Topic Distribution",
            ""
        ])
        if topic_freq:
            for topic, count in topic_freq.most_common(10):
                lines.append(f"- **{topic}:** {count} mentions")
        else:
            lines.append("- No topics extracted")

        lines.extend([
            "",
            "### Caller Sophistication",
            ""
        ])
        for level, count in level_counts.most_common():
            pct = 100 * count / len(patterns) if patterns else 0
            lines.append(f"- **{level}:** {count} calls ({pct:.1f}%)")

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        helpful_pct = 100 * helpful_count / len(patterns) if patterns else 0

        lines.extend([
            "",
            "### Quality Metrics",
            "",
            f"- **Average Quality Score:** {avg_quality:.1f}/5",
            f"- **Helpful Rate:** {helpful_count}/{len(patterns)} ({helpful_pct:.1f}%)",
            "",
            "### Individual Call Details",
            ""
        ])

        for p in patterns:
            started = p['started_at']
            if hasattr(started, 'strftime'):
                started_str = started.strftime('%Y-%m-%d %H:%M')
            else:
                started_str = str(started)[:16]

            lines.append(f"#### Call {p['call_id']} — {started_str} ({p['duration']}s)")

            if p['summary']:
                lines.append(f"\n**Summary:** {p['summary']}")

            analysis = p['analysis']
            lines.extend([
                "",
                f"- **Topics:** {', '.join(analysis.get('topics', [])) or 'None'}",
                f"- **Caller Level:** {analysis.get('caller_level', 'unknown')}",
                f"- **Quality:** {analysis.get('quality_score', 0)}/5",
                f"- **Was Helpful:** {'Yes' if analysis.get('was_helpful') else 'No'}",
            ])

            if analysis.get('key_questions'):
                lines.append("\n**Key Questions:**")
                for q in analysis['key_questions']:
                    lines.append(f"  - {q}")

            lines.append("")

    return "\n".join(lines)


def cmd_analyze(args):
    """Run full analysis on all calls."""
    conn = duckdb.connect(DB_PATH)
    calls = query_calls(conn, start_date=args.start_date, end_date=args.end_date)

    if not calls:
        print("No calls found matching criteria.", file=sys.stderr)
        return

    print(f"Loaded {len(calls)} calls", file=sys.stderr)

    stats = compute_statistics(calls)

    # Optionally analyze patterns
    patterns = None
    if args.with_patterns:
        token = get_zo_token()
        patterns = analyze_patterns(calls, token, min_duration=args.min_duration)

    report = format_report(stats, patterns)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(report)


def cmd_patterns(args):
    """Extract conversation patterns from substantive calls."""
    token = get_zo_token()
    conn = duckdb.connect(DB_PATH)
    calls = query_calls(conn, min_duration=args.min_duration,
                       start_date=args.start_date, end_date=args.end_date)

    if not calls:
        print("No calls found matching criteria.", file=sys.stderr)
        return

    patterns = analyze_patterns(calls, token, min_duration=args.min_duration)

    # Output as JSON
    output = json.dumps(patterns, indent=2, default=str)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nPatterns written to {args.output}", file=sys.stderr)
    else:
        print(output)


def cmd_report(args):
    """Generate markdown summary report."""
    conn = duckdb.connect(DB_PATH)
    calls = query_calls(conn, start_date=args.start_date, end_date=args.end_date)

    if not calls:
        print("No calls found matching criteria.", file=sys.stderr)
        return

    stats = compute_statistics(calls)
    report = format_report(stats)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(report)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Zo Hotline call data from DuckDB',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run full analysis on calls')
    analyze_parser.add_argument('--start-date', help='Filter calls after this date (YYYY-MM-DD)')
    analyze_parser.add_argument('--end-date', help='Filter calls before this date (YYYY-MM-DD)')
    analyze_parser.add_argument('--with-patterns', action='store_true',
                               help='Include pattern extraction (requires Zo API)')
    analyze_parser.add_argument('--min-duration', type=int, default=120,
                               help='Minimum call duration for pattern extraction (default: 120s)')
    analyze_parser.add_argument('--output', '-o', help='Write report to file instead of stdout')

    # patterns command
    patterns_parser = subparsers.add_parser('patterns',
                                           help='Extract conversation patterns from substantive calls')
    patterns_parser.add_argument('--min-duration', type=int, default=120,
                                help='Minimum call duration in seconds (default: 120)')
    patterns_parser.add_argument('--start-date', help='Filter calls after this date (YYYY-MM-DD)')
    patterns_parser.add_argument('--end-date', help='Filter calls before this date (YYYY-MM-DD)')
    patterns_parser.add_argument('--output', '-o', help='Write patterns to file instead of stdout')

    # report command
    report_parser = subparsers.add_parser('report', help='Generate markdown summary report')
    report_parser.add_argument('--start-date', help='Filter calls after this date (YYYY-MM-DD)')
    report_parser.add_argument('--end-date', help='Filter calls before this date (YYYY-MM-DD)')
    report_parser.add_argument('--output', '-o', help='Write report to file instead of stdout')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'patterns':
        cmd_patterns(args)
    elif args.command == 'report':
        cmd_report(args)


if __name__ == '__main__':
    main()

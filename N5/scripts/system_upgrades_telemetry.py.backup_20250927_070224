#!/usr/bin/env python3
"""
N5 System Upgrades Telemetry Aggregation Script

This script aggregates telemetry events from system upgrade operations,
generating structured reports for monitoring and analysis.

Usage:
    python3 system_upgrades_telemetry.py [--date YYYY-MM-DD] [--range days] [--output-dir DIR]
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
import sys

# Constants
ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs" / "system-upgrades"
REPORTS_DIR = LOGS_DIR / "reports"

def parse_telemetry_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a telemetry log file and return list of events."""
    events = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON in {file_path}: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Warning: Telemetry file not found: {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
    
    return events

def aggregate_events(events: List[Dict[str, Any]], date_range: tuple = None) -> Dict[str, Any]:
    """Aggregate events into metrics."""
    if date_range:
        start_date, end_date = date_range
        events = [e for e in events if start_date <= datetime.fromisoformat(e['timestamp'][:-1]) <= end_date]
    
    metrics = {
        'total_events': len(events),
        'event_types': Counter(),
        'daily_counts': defaultdict(Counter),
        'hourly_counts': defaultdict(Counter),
        'data_aggregates': defaultdict(dict)
    }
    
    for event in events:
        event_type = event['event_type']
        timestamp = datetime.fromisoformat(event['timestamp'][:-1])
        date_str = timestamp.strftime('%Y-%m-%d')
        hour_str = timestamp.strftime('%Y-%m-%d %H:00')
        
        metrics['event_types'][event_type] += 1
        metrics['daily_counts'][date_str][event_type] += 1
        metrics['hourly_counts'][hour_str][event_type] += 1
        
        # Aggregate data fields
        data = event.get('data', {})
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if key not in metrics['data_aggregates'][event_type]:
                    metrics['data_aggregates'][event_type][key] = {'sum': 0, 'count': 0, 'min': float('inf'), 'max': 0}
                agg = metrics['data_aggregates'][event_type][key]
                agg['sum'] += value
                agg['count'] += 1
                agg['min'] = min(agg['min'], value)
                agg['max'] = max(agg['max'], value)
    
    # Calculate averages
    for event_type, aggregates in metrics['data_aggregates'].items():
        for key, agg in aggregates.items():
            if agg['count'] > 0:
                agg['avg'] = agg['sum'] / agg['count']
    
    return dict(metrics)

def generate_json_report(metrics: Dict[str, Any], output_path: Path) -> None:
    """Generate JSON report."""
    report = {
        'generated_at': datetime.now().isoformat(),
        'metrics': metrics
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

def generate_markdown_report(metrics: Dict[str, Any], output_path: Path) -> None:
    """Generate human-readable markdown report."""
    report_lines = [
        "# System Upgrades Telemetry Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Events:** {metrics['total_events']}",
        "",
        "## Event Types Summary",
        "",
        "| Event Type | Count |",
        "|------------|-------|"
    ]
    
    for event_type, count in sorted(metrics['event_types'].items()):
        report_lines.append(f"| {event_type} | {count} |")
    
    report_lines.extend([
        "",
        "## Data Aggregates",
        ""
    ])
    
    for event_type, aggregates in metrics['data_aggregates'].items():
        report_lines.extend([
            f"### {event_type}",
            "",
            "| Field | Sum | Count | Min | Max | Avg |",
            "|-------|-----|-------|-----|-----|-----|"
        ])
        
        for field, agg in aggregates.items():
            report_lines.append(
                f"| {field} | {agg['sum']} | {agg['count']} | {agg['min']} | {agg['max']} | {agg.get('avg', 0):.2f} |"
            )
        report_lines.append("")
    
    if metrics['daily_counts']:
        report_lines.extend([
            "## Daily Activity",
            "",
            "| Date | " + " | ".join(sorted(metrics['event_types'].keys())) + " | Total |",
            "|------|" + "|".join(["------"] * (len(metrics['event_types']) + 1)) + "|"
        ])
        
        for date in sorted(metrics['daily_counts'].keys()):
            daily = metrics['daily_counts'][date]
            total = sum(daily.values())
            row = f"| {date} | " + " | ".join(str(daily.get(et, 0)) for et in sorted(metrics['event_types'].keys())) + f" | {total} |"
            report_lines.append(row)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

def main():
    parser = argparse.ArgumentParser(description="Aggregate system upgrades telemetry")
    parser.add_argument(
        '--date',
        type=str,
        help='Specific date to process (YYYY-MM-DD), defaults to yesterday'
    )
    parser.add_argument(
        '--range',
        type=int,
        default=1,
        help='Number of days to aggregate (default: 1)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=str(REPORTS_DIR),
        help='Output directory for reports'
    )
    parser.add_argument(
        '--include-current',
        action='store_true',
        help='Include current day in aggregation'
    )
    
    args = parser.parse_args()
    
    # Determine date range
    if args.date:
        start_date = datetime.strptime(args.date, '%Y-%m-%d')
    else:
        start_date = datetime.now() - timedelta(days=1)
    
    end_date = start_date + timedelta(days=args.range - 1)
    
    if not args.include_current and end_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        end_date = datetime.now() - timedelta(days=1)
    
    print(f"Aggregating telemetry from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Collect all events in date range
    all_events = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        telemetry_file = LOGS_DIR / f"telemetry_events_{date_str}.log"
        events = parse_telemetry_file(telemetry_file)
        all_events.extend(events)
        current_date += timedelta(days=1)
    
    if not all_events:
        print("No telemetry events found for the specified date range.")
        return
    
    print(f"Found {len(all_events)} events")
    
    # Aggregate metrics
    metrics = aggregate_events(all_events)
    
    # Generate reports
    output_dir = Path(args.output_dir)
    base_name = f"telemetry_report_{start_date.strftime('%Y%m%d')}"
    if args.range > 1:
        base_name += f"_{end_date.strftime('%Y%m%d')}"
    
    json_path = output_dir / f"{base_name}.json"
    md_path = output_dir / f"{base_name}.md"
    
    generate_json_report(metrics, json_path)
    generate_markdown_report(metrics, md_path)
    
    print(f"Reports generated:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
GA4 Analytics Summary Script for vrijenattawar.com

Usage:
    python3 ga4_summary.py                    # Last 7 days summary
    python3 ga4_summary.py --days 30          # Last 30 days
    python3 ga4_summary.py --events           # Include custom events breakdown
    python3 ga4_summary.py --realtime         # Show realtime active users
"""

import os
import argparse
from datetime import datetime, timedelta

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/workspace/.secrets/ga4-service-account.json"

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, 
    RunRealtimeReportRequest,
    DateRange, 
    Metric, 
    Dimension,
    OrderBy,
    Filter,
    FilterExpression,
)

PROPERTY_ID = "520487128"

def get_client():
    return BetaAnalyticsDataClient()

def run_overview_report(client, days=7):
    """Get high-level traffic metrics."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
            Metric(name="newUsers"),
        ],
    )
    response = client.run_report(request)
    
    if response.rows:
        row = response.rows[0]
        return {
            "users": int(row.metric_values[0].value),
            "sessions": int(row.metric_values[1].value),
            "pageviews": int(row.metric_values[2].value),
            "avg_session_duration": float(row.metric_values[3].value),
            "bounce_rate": float(row.metric_values[4].value) * 100,
            "new_users": int(row.metric_values[5].value),
        }
    return None

def run_pages_report(client, days=7, limit=10):
    """Get top pages by views."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=limit,
    )
    response = client.run_report(request)
    
    pages = []
    for row in response.rows:
        pages.append({
            "path": row.dimension_values[0].value,
            "views": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
        })
    return pages

def run_traffic_sources_report(client, days=7, limit=10):
    """Get traffic sources."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="sessionSource")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=limit,
    )
    response = client.run_report(request)
    
    sources = []
    for row in response.rows:
        sources.append({
            "source": row.dimension_values[0].value or "(direct)",
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
        })
    return sources

def run_devices_report(client, days=7):
    """Get device breakdown."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="deviceCategory")],
        metrics=[Metric(name="activeUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
    )
    response = client.run_report(request)
    
    devices = {}
    for row in response.rows:
        devices[row.dimension_values[0].value] = int(row.metric_values[0].value)
    return devices

def run_events_report(client, days=7, limit=15):
    """Get custom events breakdown."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="eventName")],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=limit,
    )
    response = client.run_report(request)
    
    events = []
    for row in response.rows:
        events.append({
            "event": row.dimension_values[0].value,
            "count": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
        })
    return events

def run_mindmap_events_report(client, days=7):
    """Get mind map specific events."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.CONTAINS,
                    value="mindmap",
                ),
            )
        ),
    )
    response = client.run_report(request)
    
    events = {}
    for row in response.rows:
        events[row.dimension_values[0].value] = int(row.metric_values[0].value)
    return events

def run_badge_funnel_report(client, days=7):
    """Get badge click to mind page funnel."""
    # Badge clicks
    badge_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.EXACT,
                    value="badge_click",
                ),
            )
        ),
    )
    badge_response = client.run_report(badge_request)
    badge_clicks = int(badge_response.rows[0].metric_values[0].value) if badge_response.rows else 0
    
    # Badge unlocks  
    unlock_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.EXACT,
                    value="badge_unlock",
                ),
            )
        ),
    )
    unlock_response = client.run_report(unlock_request)
    badge_unlocks = int(unlock_response.rows[0].metric_values[0].value) if unlock_response.rows else 0
    
    return {
        "badge_clicks": badge_clicks,
        "badge_unlocks": badge_unlocks,
        "unlock_rate": (badge_unlocks / badge_clicks * 100) if badge_clicks > 0 else 0,
    }

def run_realtime_report(client):
    """Get realtime active users."""
    request = RunRealtimeReportRequest(
        property=f"properties/{PROPERTY_ID}",
        metrics=[Metric(name="activeUsers")],
    )
    response = client.run_realtime_report(request)
    
    if response.rows:
        return int(response.rows[0].metric_values[0].value)
    return 0

def format_duration(seconds):
    """Format seconds as mm:ss."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

def main():
    parser = argparse.ArgumentParser(description="GA4 Analytics Summary")
    parser.add_argument("--days", type=int, default=7, help="Number of days to report (default: 7)")
    parser.add_argument("--events", action="store_true", help="Include detailed events breakdown")
    parser.add_argument("--realtime", action="store_true", help="Show realtime active users")
    args = parser.parse_args()
    
    client = get_client()
    
    print(f"\n{'='*60}")
    print(f"  GA4 ANALYTICS SUMMARY - vrijenattawar.com")
    print(f"  Period: Last {args.days} days")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Realtime
    if args.realtime:
        realtime = run_realtime_report(client)
        print(f"🟢 REALTIME: {realtime} active users right now\n")
    
    # Overview
    overview = run_overview_report(client, args.days)
    if overview:
        print("📊 OVERVIEW")
        print(f"   Users:          {overview['users']:,} ({overview['new_users']:,} new)")
        print(f"   Sessions:       {overview['sessions']:,}")
        print(f"   Pageviews:      {overview['pageviews']:,}")
        print(f"   Avg Duration:   {format_duration(overview['avg_session_duration'])}")
        print(f"   Bounce Rate:    {overview['bounce_rate']:.1f}%")
        print()
    
    # Top Pages
    pages = run_pages_report(client, args.days)
    if pages:
        print("📄 TOP PAGES")
        for p in pages:
            print(f"   {p['path']:<30} {p['views']:>5} views  ({p['users']} users)")
        print()
    
    # Traffic Sources
    sources = run_traffic_sources_report(client, args.days)
    if sources:
        print("🔗 TRAFFIC SOURCES")
        for s in sources:
            print(f"   {s['source']:<25} {s['sessions']:>5} sessions  ({s['users']} users)")
        print()
    
    # Devices
    devices = run_devices_report(client, args.days)
    if devices:
        total = sum(devices.values())
        print("📱 DEVICES")
        for device, users in devices.items():
            pct = (users / total * 100) if total > 0 else 0
            print(f"   {device.capitalize():<15} {users:>5} users  ({pct:.0f}%)")
        print()
    
    # Badge Funnel
    try:
        funnel = run_badge_funnel_report(client, args.days)
        if funnel['badge_clicks'] > 0:
            print("🎯 BADGE FUNNEL (@thevibethinker → /mind)")
            print(f"   Badge Clicks:   {funnel['badge_clicks']}")
            print(f"   Badge Unlocks:  {funnel['badge_unlocks']}")
            print(f"   Unlock Rate:    {funnel['unlock_rate']:.1f}%")
            print()
    except Exception:
        pass  # Not enough data yet
    
    # Mind Map Events
    try:
        mm_events = run_mindmap_events_report(client, args.days)
        if mm_events:
            print("🧠 MIND MAP ENGAGEMENT")
            for event, count in sorted(mm_events.items(), key=lambda x: -x[1]):
                label = event.replace("mindmap_", "").replace("_", " ").title()
                print(f"   {label:<25} {count:>5}")
            print()
    except Exception:
        pass  # Not enough data yet
    
    # Detailed Events
    if args.events:
        events = run_events_report(client, args.days)
        if events:
            print("⚡ ALL EVENTS")
            for e in events:
                print(f"   {e['event']:<35} {e['count']:>5} ({e['users']} users)")
            print()
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

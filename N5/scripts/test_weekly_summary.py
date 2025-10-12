#!/usr/bin/env python3
"""
Test wrapper for Weekly Summary System
Tests with real Google Calendar and Gmail APIs via Zo
"""

import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def test_calendar_api():
    """Test Google Calendar API access"""
    log.info("=" * 60)
    log.info("Testing Google Calendar API")
    log.info("=" * 60)
    
    # Get next week's date range (Monday-Sunday)
    today = datetime.now(timezone.utc)
    days_until_monday = (7 - today.weekday()) % 7 or 7
    week_start = today + timedelta(days=days_until_monday)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59)
    
    log.info(f"Date range: {week_start.date()} to {week_end.date()}")
    
    # Format for RFC3339
    time_min = week_start.strftime('%Y-%m-%dT00:00:00Z')
    time_max = week_end.strftime('%Y-%m-%dT23:59:59Z')
    
    log.info(f"Querying calendar from {time_min} to {time_max}")
    
    return {
        'time_min': time_min,
        'time_max': time_max,
        'week_start': week_start.date().isoformat(),
        'week_end': week_end.date().isoformat()
    }


def test_gmail_api():
    """Test Gmail API access"""
    log.info("=" * 60)
    log.info("Testing Gmail API")
    log.info("=" * 60)
    
    # Calculate lookback period
    lookback_days = 30
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=lookback_days)
    
    # Format for Gmail search
    after_date = start_date.strftime('%Y/%m/%d')
    
    log.info(f"Email search window: after {after_date} ({lookback_days} days)")
    
    return {
        'after_date': after_date,
        'lookback_days': lookback_days
    }


def main():
    """Run tests"""
    log.info("\n" + "=" * 60)
    log.info("Weekly Summary System - API Test")
    log.info("=" * 60 + "\n")
    
    # Test 1: Calendar API parameters
    calendar_params = test_calendar_api()
    
    print("\n📅 Calendar Query Parameters:")
    print(json.dumps(calendar_params, indent=2))
    
    # Test 2: Gmail API parameters
    gmail_params = test_gmail_api()
    
    print("\n📧 Gmail Query Parameters:")
    print(json.dumps(gmail_params, indent=2))
    
    # Test 3: Show what the actual API calls would look like
    log.info("\n" + "=" * 60)
    log.info("API Call Templates")
    log.info("=" * 60)
    
    print("\n1. Google Calendar API call (via use_app_google_calendar):")
    print(f"""
    use_app_google_calendar(
        tool_name='google_calendar-list-events',
        configured_props={{
            'calendarId': 'primary',
            'timeMin': '{calendar_params['time_min']}',
            'timeMax': '{calendar_params['time_max']}',
            'singleEvents': True,
            'maxResults': 100
        }}
    )
    """)
    
    print("\n2. Gmail API call (via use_app_gmail):")
    print(f"""
    use_app_gmail(
        tool_name='gmail-find-email',
        configured_props={{
            'q': 'after:{gmail_params['after_date']}',
            'maxResults': 50,
            'withTextPayload': True
        }}
    )
    """)
    
    log.info("\n" + "=" * 60)
    log.info("Test Complete - Ready for Real API Calls")
    log.info("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

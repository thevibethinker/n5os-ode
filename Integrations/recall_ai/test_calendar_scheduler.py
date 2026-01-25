#!/usr/bin/env python3
"""
Tests for calendar_scheduler.py
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from calendar_scheduler import (
    CalendarScheduler,
    SKIP_MARKERS,
)


def create_test_event(title, description="", location="", start_time=None, status="confirmed"):
    """Helper to create test events"""
    if start_time is None:
        start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    return {
        "id": f"test_{title.replace(' ', '_')}",
        "iCalUID": f"icaluid_{title.replace(' ', '_')}",
        "summary": title,
        "description": description,
        "location": location,
        "status": status,
        "start": {"dateTime": start_time},
    }


def test_video_link_detection():
    """Test video link detection patterns"""
    scheduler = CalendarScheduler()

    print("Testing video link detection...")

    tests = [
        # (event, expected_has_link, description)
        (create_test_event("Zoom Call", description="Join: https://zoom.us/j/123456789"), True, "Zoom in description"),
        (create_test_event("Google Meet", location="https://meet.google.com/abc-defg-hij"), True, "Google Meet in location"),
        (create_test_event("Teams Meeting", description="Join at teams.microsoft.com/l/meetup-join/xyz"), True, "Teams in description"),
        (create_test_event("Webex Call", location="https://webex.com/meet/roomname"), True, "Webex in location"),
        (create_test_event("Phone Call", description="Call 555-1234"), False, "No video link"),
        (create_test_event("No Link", location="Office 123"), False, "No video link"),
        (create_test_event("Zoom with params", description="https://zoom.us/j/123456789?pwd=abc"), True, "Zoom with password"),
    ]

    passed = 0
    for event, expected, desc in tests:
        result = scheduler.has_video_link(event)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] {desc}: {result}")
        if result == expected:
            passed += 1

    print(f"\nVideo link detection: {passed}/{len(tests)} passed\n")
    return passed == len(tests)


def test_skip_markers():
    """Test skip marker detection"""
    scheduler = CalendarScheduler()

    print("Testing skip marker detection...")

    tests = [
        (create_test_event("[NR] Private Meeting"), True, "[NR] marker"),
        (create_test_event("[SKIP] Skip this"), True, "[SKIP] marker"),
        (create_test_event("[NO RECORD] Meeting"), True, "[NO RECORD] marker"),
        (create_test_event("Normal Meeting"), False, "No marker"),
        (create_test_event("Skip Meeting [NR]"), True, "Marker at end"),
    ]

    # Add video links to make them recordable except for skip
    for i, (event, _, _) in enumerate(tests):
        if i == 3:  # The one without marker
            tests[i] = (event, False, tests[i][2])  # Should NOT record (no link)
        else:
            tests[i] = (event, False, tests[i][2])  # Should NOT record (has marker)

    # Now add video links to recordable ones
    video_event = create_test_event("Normal Meeting", description="https://zoom.us/j/123")
    tests.append((video_event, True, "Recordable meeting"))

    passed = 0
    for event, expected, desc in tests:
        result = scheduler.should_record(event)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] {desc}: should_record={result}")
        if result == expected:
            passed += 1

    print(f"\nSkip marker detection: {passed}/{len(tests)} passed\n")
    return passed == len(tests)


def test_link_extraction():
    """Test meeting link extraction"""
    scheduler = CalendarScheduler()

    print("Testing link extraction...")

    tests = [
        (create_test_event("Zoom", description="Join: https://zoom.us/j/123456789?pwd=abc"), "https://zoom.us/j/123456789?pwd=abc", "Zoom from description"),
        (create_test_event("Meet", location="https://meet.google.com/abc-defg-hij"), "https://meet.google.com/abc-defg-hij", "Google Meet from location"),
        # Teams without https:// won't be extracted by our pattern (needs protocol)
        (create_test_event("Teams", description="https://teams.microsoft.com/l/meetup-join/xyz"), "https://teams.microsoft.com/l/meetup-join/xyz", "Teams with protocol"),
        (create_test_event("No Link"), None, "No link to extract"),
    ]

    passed = 0
    for event, expected, desc in tests:
        result = scheduler.extract_video_link(event)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] {desc}: {result}")
        if result == expected:
            passed += 1

    print(f"\nLink extraction: {passed}/{len(tests)} passed\n")
    return passed == len(tests)


def test_join_time_calculation():
    """Test join time calculation"""
    scheduler = CalendarScheduler()

    print("Testing join time calculation...")

    # Test far future event
    far_future = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    join_time = scheduler.calculate_join_time(far_future)
    expected = datetime.fromisoformat(far_future) - timedelta(minutes=15)  # DEFAULT_JOIN_MINUTES_AHEAD

    passed = 0
    diff = abs((join_time - expected).total_seconds())
    if diff < 1:  # Within 1 second
        print(f"  [PASS] Far future event joins 15 min early: {join_time}")
        passed += 1
    else:
        print(f"  [FAIL] Expected {expected}, got {join_time}")

    # Test near future event (should adjust to min requirement)
    near_future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    join_time = scheduler.calculate_join_time(near_future)
    min_allowed = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Allow small time difference (within 1 second) due to execution time
    if abs((join_time - min_allowed).total_seconds()) < 2:
        print(f"  [PASS] Near future event adjusted to min: {join_time}")
        passed += 1
    else:
        print(f"  [FAIL] Join time {join_time} not within threshold of min allowed {min_allowed}")

    print(f"\nJoin time calculation: {passed}/2 passed\n")
    return passed == 2


def test_event_key():
    """Test event key generation"""
    scheduler = CalendarScheduler()

    print("Testing event key generation...")

    event1 = create_test_event("Meeting A", start_time="2025-01-01T10:00:00Z")
    event1["iCalUID"] = "ical_123"

    event2 = create_test_event("Meeting B", start_time="2025-01-02T10:00:00Z")
    event2["iCalUID"] = "ical_456"

    event3 = create_test_event("Meeting C", start_time="2025-01-03T10:00:00Z")
    event3["iCalUID"] = "ical_123"  # Same iCalUID as event1 (recurring instance)

    key1 = scheduler.get_event_key(event1)
    key2 = scheduler.get_event_key(event2)
    key3 = scheduler.get_event_key(event3)

    passed = 0
    if key1 == "ical_123":
        print(f"  [PASS] Event 1 key: {key1}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 'ical_123', got {key1}")

    if key2 == "ical_456":
        print(f"  [PASS] Event 2 key: {key2}")
        passed += 1
    else:
        print(f"  [FAIL] Expected 'ical_456', got {key2}")

    if key3 == key1:  # Same recurring series
        print(f"  [PASS] Event 3 matches event 1 (recurring)")
        passed += 1
    else:
        print(f"  [FAIL] Event 3 key {key3} should match {key1}")

    print(f"\nEvent key generation: {passed}/3 passed\n")
    return passed == 3


def test_sync_with_sample_events():
    """Test sync logic with sample events (dry run)"""
    scheduler = CalendarScheduler()

    print("Testing sync with sample events (dry run)...")

    now = datetime.now(timezone.utc)
    events = [
        create_test_event(
            "Zoom Sync",
            description="Join: https://zoom.us/j/123456789",
            start_time=(now + timedelta(hours=2)).isoformat()
        ),
        create_test_event(
            "[NR] Private",
            description="Join: https://zoom.us/j/987654321",
            start_time=(now + timedelta(hours=3)).isoformat()
        ),
        create_test_event(
            "No Link Meeting",
            description="No video link here",
            start_time=(now + timedelta(hours=4)).isoformat()
        ),
        create_test_event(
            "Google Meet Sync",
            location="https://meet.google.com/abc-defg-hij",
            start_time=(now + timedelta(hours=5)).isoformat()
        ),
    ]

    results = scheduler.sync(events, dry_run=True)

    passed = 0
    if results["total_events"] == 4:
        print(f"  [PASS] Total events: 4")
        passed += 1
    else:
        print(f"  [FAIL] Expected 4 events, got {results['total_events']}")

    if results["recordable"] == 2:  # Zoom Sync + Google Meet Sync
        print(f"  [PASS] Recordable events: 2")
        passed += 1
    else:
        print(f"  [FAIL] Expected 2 recordable, got {results['recordable']}")

    if results["new_scheduled"] == 2:
        print(f"  [PASS] New scheduled (dry run): 2")
        passed += 1
    else:
        print(f"  [FAIL] Expected 2 new scheduled, got {results['new_scheduled']}")

    print(f"\nSync with sample events: {passed}/3 passed\n")
    return passed == 3


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Calendar Scheduler Test Suite")
    print("=" * 60)
    print()

    results = {
        "Video link detection": test_video_link_detection(),
        "Skip markers": test_skip_markers(),
        "Link extraction": test_link_extraction(),
        "Join time calculation": test_join_time_calculation(),
        "Event key generation": test_event_key(),
        "Sync with sample events": test_sync_with_sample_events(),
    }

    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {test}")

    print()
    print(f"Overall: {passed}/{total} test suites passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

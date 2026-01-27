#!/usr/bin/env python3
"""
Calendar-aware availability checker for Pulse v2.
Checks Google Calendar for meetings and deep work blocks.
"""

import json
import argparse
import os
from datetime import datetime, timedelta, UTC
from pathlib import Path
from zoneinfo import ZoneInfo

# Config path - relative to N5/pulse/ directory
CONFIG_PATH = Path(__file__).parent.parent / "Skills" / "pulse" / "config" / "pulse_v2_config.json"


def load_config() -> dict:
    """Load Pulse v2 configuration."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "availability": {
            "deep_work_marker": "[DW]",
            "check_calendar": True,
            "quiet_hours": {"start": "22:00", "end": "07:00"},
            "timezone": "America/New_York"
        }
    }


def get_calendar_events(hours_ahead: int = 2) -> list:
    """
    Get calendar events for the next N hours.
    Uses Google Calendar integration if available.
    """
    # Check if calendar integration is available via environment
    # For now, we return empty list to indicate "available"
    # In production, this would call use_app_google_calendar

    try:
        # Try to use the Pulse calendar integration if it exists
        calendar_script = Path(__file__).parent / "calendar_integration.py"
        if calendar_script.exists():
            import subprocess
            result = subprocess.run([
                "python3", str(calendar_script), "list", str(hours_ahead)
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("events", [])
    except Exception as e:
        # Graceful degradation - return empty list on any error
        pass

    return []


def is_quiet_hours() -> tuple[bool, dict]:
    """Check if current time is within quiet hours."""
    config = load_config()
    quiet = config.get("availability", {}).get("quiet_hours", {})
    timezone_str = config.get("availability", {}).get("timezone", "America/New_York")

    if not quiet:
        return False, {"in_quiet_hours": False, "reason": "no_quiet_hours_configured"}

    start_str = quiet.get("start", "22:00")
    end_str = quiet.get("end", "07:00")

    try:
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)

        # Parse times
        start_hour, start_min = map(int, start_str.split(":"))
        end_hour, end_min = map(int, end_str.split(":"))

        current_minutes = now.hour * 60 + now.minute
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        # Handle overnight quiet hours (e.g., 22:00 to 07:00)
        if start_minutes > end_minutes:
            # Overnight: quiet if after start OR before end
            in_quiet = current_minutes >= start_minutes or current_minutes < end_minutes
        else:
            # Same day: quiet if between start and end
            in_quiet = start_minutes <= current_minutes < end_minutes

        return in_quiet, {
            "in_quiet_hours": in_quiet,
            "timezone": timezone_str,
            "current_time": now.strftime("%H:%M"),
            "quiet_start": start_str,
            "quiet_end": end_str
        }
    except Exception as e:
        return False, {"in_quiet_hours": False, "reason": f"parse_error: {str(e)}"}


def has_deep_work_block(events: list) -> tuple[bool, str | None]:
    """Check if any event is a deep work block."""
    config = load_config()
    marker = config.get("availability", {}).get("deep_work_marker", "[DW]")

    for event in events:
        title = event.get("summary", "") or event.get("title", "")
        if marker in title:
            return True, title

    return False, None


def has_current_meeting(events: list) -> tuple[bool, str | None]:
    """Check if there's a meeting happening right now."""
    config = load_config()
    timezone_str = config.get("availability", {}).get("timezone", "America/New_York")

    try:
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)
    except:
        now = datetime.now(UTC)

    for event in events:
        start = event.get("start", {})
        end = event.get("end", {})

        # Parse datetime strings
        start_dt_str = start.get("dateTime") or start.get("date")
        end_dt_str = end.get("dateTime") or end.get("date")

        if start_dt_str and end_dt_str:
            try:
                # Simple ISO parsing - handle both full datetime and date-only
                if "T" in start_dt_str:
                    start_dt = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00"))
                    # Convert to local timezone for comparison
                    start_dt = start_dt.astimezone(tz)
                else:
                    start_dt = datetime.fromisoformat(start_dt_str)

                if "T" in end_dt_str:
                    end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00"))
                    end_dt = end_dt.astimezone(tz)
                else:
                    end_dt = datetime.fromisoformat(end_dt_str)

                if start_dt <= now <= end_dt:
                    return True, event.get("summary", "Meeting")
            except Exception:
                pass

    return False, None


def is_available() -> dict:
    """
    Check if V is currently available.

    Available = no current meeting AND no deep work block AND not quiet hours.
    """
    result = {
        "available": True,
        "reasons": [],
        "checked_at": datetime.now(UTC).isoformat().replace("+00:00", "Z")
    }

    # Check quiet hours first (no API call needed)
    is_quiet, quiet_info = is_quiet_hours()
    if is_quiet:
        result["available"] = False
        result["reasons"].append({
            "type": "quiet_hours",
            "details": quiet_info
        })

    # Check calendar
    config = load_config()
    if config.get("availability", {}).get("check_calendar", True):
        events = get_calendar_events(hours_ahead=1)

        # Check for deep work
        is_dw, dw_title = has_deep_work_block(events)
        if is_dw:
            result["available"] = False
            result["reasons"].append({
                "type": "deep_work",
                "details": {"title": dw_title}
            })

        # Check for current meeting
        in_meeting, meeting_title = has_current_meeting(events)
        if in_meeting:
            result["available"] = False
            result["reasons"].append({
                "type": "in_meeting",
                "details": {"title": meeting_title}
            })

    return result


def next_available_window() -> dict:
    """
    Find the next time V will be available.
    Returns estimated window.
    """
    current = is_available()

    if current["available"]:
        return {
            "available_now": True,
            "next_check": None
        }

    # Find end of current blocker
    # This is simplified - production would parse event end times
    now = datetime.now(UTC)
    return {
        "available_now": False,
        "reasons": current["reasons"],
        "suggested_check": (now + timedelta(minutes=30)).isoformat().replace("+00:00", "Z"),
        "message": "Try again in ~30 minutes"
    }


def main():
    parser = argparse.ArgumentParser(description="Availability Checker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("check", help="Check if available now")
    subparsers.add_parser("next", help="Find next available window")
    subparsers.add_parser("quiet", help="Check if in quiet hours")

    args = parser.parse_args()

    if args.command == "check":
        result = is_available()
    elif args.command == "next":
        result = next_available_window()
    elif args.command == "quiet":
        is_quiet, quiet_info = is_quiet_hours()
        result = {
            "in_quiet_hours": is_quiet,
            "details": quiet_info
        }
    else:
        result = is_available()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

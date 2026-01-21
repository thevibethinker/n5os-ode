#!/usr/bin/env python3
"""Founder scan system status viewer.

---
product: careerspan
created: 2026-01-20
---

Usage examples:

  # View system status (human-readable)
  export FOUNDER_AUTH_TOKEN="..."
  python3 N5/scripts/founder_scan_system_status.py

  # Get raw JSON output
  python3 N5/scripts/founder_scan_system_status.py --json

  # Use a different base URL
  python3 N5/scripts/founder_scan_system_status.py --base-url https://staging.example.com

This script uses only the Python standard library (no requests needed).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Optional


BASE_URL_DEFAULT = "https://the-apply-ai--dossier-ai-all-main-fastapi-app.modal.run"
ENDPOINT_PATH = "/etc/founder_scan_system_status"
TIMEOUT_SECONDS_DEFAULT = 300  # 5 minutes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="View founder scan system status (read-only).",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL_DEFAULT,
        help=f"Base URL for the API (default: {BASE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print raw JSON output instead of human-readable format.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=TIMEOUT_SECONDS_DEFAULT,
        help=f"Request timeout in seconds (default: {TIMEOUT_SECONDS_DEFAULT})",
    )

    return parser.parse_args()


def get_founder_token() -> str:
    token = os.getenv("FOUNDER_AUTH_TOKEN")
    if not token:
        print(
            "ERROR: FOUNDER_AUTH_TOKEN environment variable is not set.\n"
            "Set it to your founder auth token before running this script.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def fetch_system_status(base_url: str, timeout: int) -> dict[str, Any]:
    """Fetch scan system status from the API."""
    url = base_url.rstrip("/") + ENDPOINT_PATH
    token = get_founder_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        # Read error body for details
        try:
            err_body = exc.read().decode("utf-8")
            err_data = json.loads(err_body)
            detail = err_data.get("detail", str(err_data))
        except Exception:
            detail = err_body if err_body else str(exc)

        # Provide helpful context for common errors
        if exc.code == 401 or exc.code == 403:
            print(
                f"ERROR: Authentication failed (HTTP {exc.code}).\n"
                f"Detail: {detail}\n"
                f"Check that FOUNDER_AUTH_TOKEN is set correctly in Zo Settings → Developers → Secrets.",
                file=sys.stderr,
            )
        elif exc.code == 404:
            print(
                f"ERROR: Endpoint not found (HTTP 404).\n"
                f"Detail: {detail}\n"
                f"The endpoint {ENDPOINT_PATH} may not exist on this server.",
                file=sys.stderr,
            )
        else:
            print(
                f"ERROR: API returned status {exc.code}: {detail}",
                file=sys.stderr,
            )
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"ERROR: Request to {url} failed: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse JSON response: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


def format_timestamp_et(utc_now: datetime) -> str:
    """Format UTC datetime for display, approximating ET offset."""
    # Simple ET approximation: UTC-5 (EST) or UTC-4 (EDT)
    # For accuracy we'd need pytz, but we use stdlib only
    # January = EST (UTC-5)
    month = utc_now.month
    if month >= 3 and month <= 11:
        # Rough EDT period (March-November)
        offset_hours = -4
        tz_label = "ET (approx EDT)"
    else:
        offset_hours = -5
        tz_label = "ET (approx EST)"

    from datetime import timedelta
    et_time = utc_now + timedelta(hours=offset_hours)
    return f"{et_time.strftime('%Y-%m-%d %H:%M:%S')} {tz_label}"


def shorten_id(id_str: str, length: int = 8) -> str:
    """Shorten a UUID/ID string for display."""
    if not id_str:
        return "-"
    if len(id_str) <= length:
        return id_str
    return id_str[:length] + "..."


def format_seconds(seconds: Optional[float]) -> str:
    """Format seconds as human-readable duration."""
    if seconds is None:
        return "-"
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def print_human_readable(data: dict[str, Any]) -> None:
    """Print scan system status in human-readable format."""
    utc_now = datetime.now(timezone.utc)
    et_display = format_timestamp_et(utc_now)

    print(f"Scan System Status")
    print(f"Retrieved: {et_display}")
    print("=" * 60)
    print()

    # Overview block
    overall = data.get("overall", {})
    print("OVERVIEW")
    print("-" * 40)
    print(f"  Pending:                  {overall.get('pending_count', '-')}")
    print(f"  Running:                  {overall.get('running_count', '-')}")
    print(f"  Completed (30d):          {overall.get('completed_last_30_days', '-')}")
    print(f"  Errored (30d):            {overall.get('errored_last_30_days', '-')}")

    max_wait = overall.get("max_wait_seconds_last_30_days")
    avg_wait = overall.get("avg_wait_seconds_last_30_days")
    print(f"  Max wait (30d):           {format_seconds(max_wait)}")
    print(f"  Avg wait (30d):           {format_seconds(avg_wait)}")
    print()

    # Active scans table
    active_scans = data.get("active_scans", [])

    if not active_scans:
        print("No active scans.")
        return

    print(f"ACTIVE SCANS ({len(active_scans)})")
    print("-" * 100)

    # Table header
    header = (
        f"{'employer_id':<12} "
        f"{'scan_id':<12} "
        f"{'lead_id':<12} "
        f"{'status':<10} "
        f"{'created_at':<20} "
        f"{'started_at':<20} "
        f"{'since_created':<14} "
        f"{'since_started':<14}"
    )
    print(header)
    print("-" * 100)

    for scan in active_scans:
        employer_id = shorten_id(str(scan.get("employer_id", "")), 10)
        scan_id = shorten_id(str(scan.get("scan_id", "")), 10)
        lead_id = shorten_id(str(scan.get("lead_id", "")), 10)
        status = scan.get("status", "-")[:10]

        created_at = scan.get("created_at", "-")
        if created_at and len(created_at) > 19:
            created_at = created_at[:19]  # Trim microseconds/timezone

        started_at = scan.get("started_at", "-") or "-"
        if started_at and started_at != "-" and len(started_at) > 19:
            started_at = started_at[:19]

        time_created = scan.get("time_since_created_seconds")
        time_started = scan.get("time_since_started_seconds")

        row = (
            f"{employer_id:<12} "
            f"{scan_id:<12} "
            f"{lead_id:<12} "
            f"{status:<10} "
            f"{created_at:<20} "
            f"{started_at:<20} "
            f"{format_seconds(time_created):<14} "
            f"{format_seconds(time_started):<14}"
        )
        print(row)


def main() -> None:
    args = parse_args()

    data = fetch_system_status(base_url=args.base_url, timeout=args.timeout)

    if args.json_output:
        print(json.dumps(data, indent=2))
    else:
        print_human_readable(data)


if __name__ == "__main__":
    main()

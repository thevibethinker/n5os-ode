"""
Zøde Conversion Tracker — Tracks the free-help → paid-service pipeline.

Reads from:
  - conversion_log.jsonl (ACP job events)
  - Moltbook engagement data (via Skills/zode-moltbook/scripts/)

Reports:
  - Funnel metrics: engagements → replies → DMs → ACP jobs → revenue
  - Top converting topics/pain points
  - Revenue totals and projections

Usage:
    python3 conversion_tracker.py              # Print summary
    python3 conversion_tracker.py --sms        # Send summary via SMS to V
    python3 conversion_tracker.py --json       # Output as JSON
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
CONVERSION_LOG = SCRIPT_DIR / "conversion_log.jsonl"

# Pricing reference
PRICES = {
    "communicationaudit": 0.75,
    "humanreadablerewrite": 0.50,
    "trustrecoveryplan": 1.00,
}

# ACP tax: 60% to agent, 30% token buyback, 10% protocol
AGENT_REVENUE_SHARE = 0.60


def load_events(since_hours: int = 24) -> list:
    """Load conversion events from the last N hours."""
    if not CONVERSION_LOG.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    events = []

    with open(CONVERSION_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                ts = datetime.fromisoformat(event["timestamp"])
                if ts >= cutoff:
                    events.append(event)
            except (json.JSONDecodeError, KeyError):
                continue

    return events


def compute_metrics(events: list) -> dict:
    """Compute funnel metrics from conversion events."""
    received = [e for e in events if e["event"] == "job_received"]
    delivered = [e for e in events if e["event"] == "job_delivered"]
    errors = [e for e in events if e["event"] == "job_error"]

    # Revenue calculation
    gross_revenue = 0.0
    for e in delivered:
        job_type = e.get("job_type", "").lower()
        gross_revenue += PRICES.get(job_type, 0.50)

    net_revenue = gross_revenue * AGENT_REVENUE_SHARE

    # Job type breakdown
    type_counts = Counter(e.get("job_type", "unknown") for e in received)

    # Unique clients
    unique_clients = len(set(e.get("client_address", "") for e in received))

    # Repeat clients
    client_counts = Counter(e.get("client_address", "") for e in received)
    repeat_clients = sum(1 for c in client_counts.values() if c > 1)

    return {
        "period_hours": 24,
        "jobs_received": len(received),
        "jobs_delivered": len(delivered),
        "jobs_errored": len(errors),
        "delivery_rate": (
            f"{len(delivered)/len(received)*100:.0f}%"
            if received else "N/A"
        ),
        "gross_revenue_usdc": round(gross_revenue, 2),
        "net_revenue_usdc": round(net_revenue, 2),
        "unique_clients": unique_clients,
        "repeat_clients": repeat_clients,
        "job_type_breakdown": dict(type_counts),
    }


def format_summary(metrics: dict) -> str:
    """Format metrics as a readable summary."""
    lines = [
        "--- Zøde Revenue Dashboard ---",
        f"Period: Last {metrics['period_hours']}h",
        "",
        f"Jobs received:  {metrics['jobs_received']}",
        f"Jobs delivered: {metrics['jobs_delivered']}",
        f"Jobs errored:   {metrics['jobs_errored']}",
        f"Delivery rate:  {metrics['delivery_rate']}",
        "",
        f"Gross revenue:  ${metrics['gross_revenue_usdc']:.2f} USDC",
        f"Net revenue:    ${metrics['net_revenue_usdc']:.2f} USDC (60% after ACP tax)",
        "",
        f"Unique clients: {metrics['unique_clients']}",
        f"Repeat clients: {metrics['repeat_clients']}",
        "",
        "Job type breakdown:",
    ]

    for job_type, count in metrics["job_type_breakdown"].items():
        price = PRICES.get(job_type.lower(), 0.50)
        lines.append(f"  {job_type}: {count} (${price:.2f}/ea)")

    if metrics["jobs_received"] == 0:
        lines.append("")
        lines.append("No jobs yet. Moltbook engagement sprint is running — ")
        lines.append("conversions will appear here as agents discover Zøde.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Zøde Conversion Tracker")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--hours", type=int, default=24, help="Lookback period in hours")
    args = parser.parse_args()

    events = load_events(since_hours=args.hours)
    metrics = compute_metrics(events)
    metrics["period_hours"] = args.hours

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print(format_summary(metrics))


if __name__ == "__main__":
    main()

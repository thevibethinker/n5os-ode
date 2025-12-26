#!/usr/bin/env python3
"""
CLI wrapper for the Apply AI Export Employer Leads API.
Exports lead and applicant data to CSV.
"""

import os
import sys
import json
import argparse
import datetime
import requests
from pathlib import Path

# API Configuration
BASE_URL = "https://the-apply-ai--dossier-ai-all-main-fastapi-app.modal.run"
ENDPOINT = "/etc/export_employer_leads"
DEFAULT_EXPORT_DIR = Path("/home/workspace/Records/Exports/Leads")

def main():
    parser = argparse.ArgumentParser(description="Export Employer Leads from Apply AI API.")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30, max: 360)")
    parser.add_argument("--employer-email", type=str, help="Filter by specific employer email")
    parser.add_argument("--output", type=str, help="Custom output path for the CSV file")
    
    args = parser.parse_args()

    # Auth check
    auth_token = os.environ.get("FOUNDER_AUTH_TOKEN")
    if not auth_token:
        print("Error: FOUNDER_AUTH_TOKEN environment variable not set.")
        sys.exit(1)

    # Validate days
    if not (1 <= args.days <= 360):
        print(f"Error: --days must be between 1 and 360. Got: {args.days}")
        sys.exit(1)

    # Scalability warning
    if args.days > 90:
        print(f"Warning: Requesting {args.days} days of data. This may be slow or hit scalability limits.")

    # Prepare request
    url = f"{BASE_URL}{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {"days": args.days}
    if args.employer_email:
        payload["employer_email"] = args.employer_email

    # Execute request
    try:
        print(f"Requesting data for last {args.days} days...", file=sys.stderr)
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        if response is not None:
            try:
                error_detail = response.json().get("detail", "No detail provided")
                print(f"API Error Detail: {error_detail}")
            except:
                pass
        sys.exit(1)

    # Prepare output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{args.employer_email}" if args.employer_email else ""
        filename = f"leads_export_{timestamp}{suffix}.csv"
        output_path = DEFAULT_EXPORT_DIR / filename

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Successfully exported leads to: {output_path}")
    print(f"File Size: {len(response.content)} bytes")

if __name__ == "__main__":
    main()


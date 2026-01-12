#!/usr/bin/env python3
"""
Scheduled email scanner - checks Gmail for Travel emails and creates trips
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from email_scanner import scan_travel_emails

if __name__ == "__main__":
    print("Scanning emails for travel bookings...")
    result = scan_travel_emails()
    print(f"Found {result['emails_scanned']} travel emails")
    print(f"Created {result['trips_created']} new trips")
    
    if result['trips_created'] > 0:
        print("\nNew trips:")
        for trip in result['trips']:
            print(f"  - {trip['outbound']['airline']} {trip['outbound']['flight_number']}: "
                  f"{trip['outbound']['departure']['city']} → {trip['outbound']['arrival']['city']}")

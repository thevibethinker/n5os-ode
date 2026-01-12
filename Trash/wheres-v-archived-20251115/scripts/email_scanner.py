#!/usr/bin/env python3
"""
Email Scanner - Monitors Gmail for Travel emails and extracts flight details
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import anthropic
from trip_manager import create_trip, update_trip, get_active_trip

# Add new imports for Gmail integration
import base64
from typing import List, Dict

# Gmail API tool usage (via Zo's use_app_gmail)
# This will be called from the main app

def extract_flight_details_from_email(email_body: str, email_subject: str) -> dict:
    """
    Use Claude to extract flight details from email
    Returns structured trip data or None if no flights found
    """
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # If no API key, return mock data for demonstration
    if not api_key:
        print("Note: Using mock flight data (no API key configured)")
        return {
            "has_flights": True,
            "outbound": {
                "flight_number": "DL1234",
                "airline": "Delta",
                "departure": {
                    "airport": "EWR",
                    "time": "2025-11-10T08:00:00Z",
                    "city": "Newark",
                    "terminal": "C",
                    "gate": "C42"
                },
                "arrival": {
                    "airport": "SFO",
                    "time": "2025-11-10T14:00:00Z",
                    "city": "San Francisco",
                    "terminal": "1",
                    "gate": ""
                }
            },
            "return": {
                "flight_number": "DL5678",
                "airline": "Delta",
                "departure": {
                    "airport": "SFO",
                    "time": "2025-11-15T18:00:00Z",
                    "city": "San Francisco",
                    "terminal": "1",
                    "gate": ""
                },
                "arrival": {
                    "airport": "EWR",
                    "time": "2025-11-16T02:00:00Z",
                    "city": "Newark",
                    "terminal": "C",
                    "gate": ""
                }
            },
            "confirmation_number": "ABC123"
        }
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""You are extracting flight information from a travel email.

Email Subject: {email_subject}

Email Body:
{email_body}

Extract ALL flight information and return as JSON. Include BOTH outbound and return flights if present.

Required format:
{{
  "has_flights": true/false,
  "outbound": {{
    "flight_number": "AA123",
    "airline": "American Airlines",
    "departure": {{
      "airport": "EWR",
      "time": "2025-11-10T08:00:00Z",
      "city": "Newark",
      "terminal": "C",
      "gate": "C42"
    }},
    "arrival": {{
      "airport": "SFO",
      "time": "2025-11-10T14:00:00Z",
      "city": "San Francisco", 
      "terminal": "1",
      "gate": ""
    }}
  }},
  "return": {{
    "flight_number": "AA456",
    "airline": "American Airlines",
    "departure": {{
      "airport": "SFO",
      "time": "2025-11-15T18:00:00Z",
      "city": "San Francisco",
      "terminal": "1",
      "gate": ""
    }},
    "arrival": {{
      "airport": "EWR",
      "time": "2025-11-16T02:00:00Z",
      "city": "Newark",
      "terminal": "C",
      "gate": ""
    }}
  }},
  "destination_contact": {{
    "hotel": "Marriott Downtown",
    "phone": "+1-555-123-4567",
    "address": "123 Market St, SF"
  }},
  "confirmation_number": "ABC123"
}}

Rules:
- Parse times into ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- If no return flight mentioned, set "return": null
- Extract hotel/contact info if present
- If no flight info found, return {{"has_flights": false}}
- Be flexible with airline names, airport codes, date formats
- Infer missing info reasonably (e.g., city names from airport codes)

Return ONLY valid JSON, no explanation."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    result_text = response.content[0].text
    
    try:
        result = json.loads(result_text)
        return result if result.get("has_flights") else None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from Claude: {result_text}")
        return None

def process_email(email_id: str, email_subject: str, email_body: str):
    """Process a single email and create/update trip"""
    
    print(f"Processing email: {email_subject}")
    
    # Extract flight details using LLM
    flight_data = extract_flight_details_from_email(email_body, email_subject)
    
    if not flight_data:
        print("No flight information found")
        return
    
    # Check if we already have an active trip
    active_trip = get_active_trip()
    
    if active_trip:
        # Update existing trip
        trip_id = active_trip["trip_id"]
        print(f"Updating existing trip: {trip_id}")
        update_trip(trip_id, flight_data)
    else:
        # Create new trip
        trip_id = create_trip(flight_data)
        print(f"Created new trip: {trip_id}")

def scan_travel_emails() -> Dict:
    """
    Scan Gmail for Travel label emails and extract flight information
    This integrates with Zo's Gmail API via the use_app_gmail tool
    """
    from anthropic import Anthropic
    
    result = {
        "emails_scanned": 0,
        "trips_created": 0,
        "trips": [],
        "errors": []
    }
    
    try:
        # Note: In production, this would use Zo's use_app_gmail tool
        # For now, we'll return sample data to demonstrate the workflow
        # The actual implementation would:
        # 1. Call use_app_gmail with tool_name="gmail-list-messages" to get Travel label emails
        # 2. For each email, call use_app_gmail with tool_name="gmail-get-message"
        # 3. Extract the email body and subject
        # 4. Process with extract_flight_details_from_email
        # 5. Create trips for emails with flight data
        
        # For testing, use the sample email from __main__
        sample_email_body = """
Your Delta Airlines Booking Confirmation

Confirmation Number: ABC123

OUTBOUND FLIGHT
Flight: DL1234
Date: November 10, 2025
Departure: Newark (EWR) - 8:00 AM - Terminal C, Gate C42
Arrival: San Francisco (SFO) - 2:00 PM PST - Terminal 1

RETURN FLIGHT
Flight: DL5678
Date: November 15, 2025
Departure: San Francisco (SFO) - 6:00 PM PST - Terminal 1
Arrival: Newark (EWR) - 2:00 AM EST (Nov 16) - Terminal C

Hotel: Marriott Marquis San Francisco
Address: 780 Mission St, San Francisco, CA 94103
Phone: +1-415-896-1600
Check-in: Nov 10, Check-out: Nov 15
        """
        sample_subject = "Your Delta Booking Confirmation"
        
        result["emails_scanned"] = 1
        
        # Extract flight details
        flight_data = extract_flight_details_from_email(sample_email_body, sample_subject)
        
        if flight_data and flight_data.get("has_flights"):
            # Create trip
            trip_id = create_trip(flight_data)
            result["trips_created"] = 1
            result["trips"].append(flight_data)
            print(f"Successfully created trip: {trip_id}")
        else:
            print("No flight data extracted from email")
            
    except Exception as e:
        result["errors"].append(str(e))
        print(f"Error scanning emails: {e}")
    
    return result

if __name__ == "__main__":
    # Test with sample email
    sample_email = """
    Your Delta Airlines Booking Confirmation
    
    Confirmation Number: ABC123
    
    OUTBOUND FLIGHT
    Flight: DL1234
    Date: November 10, 2025
    Departure: Newark (EWR) - 8:00 AM - Terminal C, Gate C42
    Arrival: San Francisco (SFO) - 2:00 PM PST - Terminal 1
    
    RETURN FLIGHT
    Flight: DL5678
    Date: November 15, 2025
    Departure: San Francisco (SFO) - 6:00 PM PST - Terminal 1
    Arrival: Newark (EWR) - 2:00 AM EST (Nov 16) - Terminal C
    
    Hotel: Marriott Marquis San Francisco
    Address: 780 Mission St, San Francisco, CA 94103
    Phone: +1-415-896-1600
    Check-in: Nov 10, Check-out: Nov 15
    """
    
    result = extract_flight_details_from_email(sample_email, "Your Delta Booking")
    print(json.dumps(result, indent=2))

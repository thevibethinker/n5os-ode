#!/usr/bin/env python3
"""
LLM Interpreter for Where's V? Flight Tracker
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

TRIPS_FILE = Path("/home/workspace/wheresv2-data/trips.jsonl")
API_KEY = os.getenv('AVIATIONSTACK_API_KEY')

def parse_instruction(text):
    text = text.lower().strip()
    result = {
        'flight_number': None,
        'airline_code': None,
        'date': None,
        'status_update': None
    }
    
    if any(phrase in text for phrase in ['landed', 'arrived', 'touched down', 'made it']):
        result['status_update'] = 'landed'
        return result
    if any(phrase in text for phrase in ['boarding', 'at gate', 'about to board']):
        result['status_update'] = 'boarding'
        return result
    if any(phrase in text for phrase in ['took off', 'departed', 'in the air', 'wheels up']):
        result['status_update'] = 'in_air'
        return result
    
    flight_patterns = [
        r'\b([A-Z]{2})\s*(\d{1,4})\b',
        r'\bflight\s+([A-Z]{2})\s*(\d{1,4})\b',
        r'\b([A-Z]\d[A-Z0-9]?)\s*(\d{1,4})\b',
    ]
    
    for pattern in flight_patterns:
        match = re.search(pattern, text.upper())
        if match and len(match.groups()) == 2:
            result['airline_code'] = match.group(1)
            result['flight_number'] = match.group(2)
            break
    
    today = datetime.now()
    
    if 'tomorrow' in text:
        result['date'] = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'today' in text:
        result['date'] = today.strftime('%Y-%m-%d')
    elif 'yesterday' in text:
        result['date'] = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        months = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
            'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
            'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
        }
        
        for month_name, month_num in months.items():
            pattern = rf'\b{month_name}\w*\s+(\d{{1,2}})\b'
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                result['date'] = f"{today.year}-{month_num:02d}-{day:02d}"
                break
    
    return result

def create_mock_flight_data(airline_code, flight_number, flight_date):
    return {
        'airline': f"{airline_code} Airlines",
        'flight_number': f"{airline_code}{flight_number}",
        'flight_iata': f"{airline_code}{flight_number}",
        'flight_icao': f"{airline_code}{flight_number}",
        'icao24': f"MOCK{flight_number}",
        'departure': {
            'airport': 'Mock Origin Airport',
            'city': 'Origin City',
            'iata': 'XXX',
            'scheduled': f"{flight_date}T08:00:00-05:00",
        },
        'arrival': {
            'airport': 'Mock Destination Airport',
            'city': 'Destination City',
            'iata': 'YYY',
            'scheduled': f"{flight_date}T12:00:00-05:00",
        },
        'status': 'scheduled',
        'stage': 'preparing'
    }

def determine_stage(status):
    status = status.lower()
    if status in ['scheduled', 'expected']:
        return 'preparing'
    elif status in ['active', 'en-route', 'in_air']:
        return 'in_air'
    elif status in ['landed', 'arrived']:
        return 'landed'
    return 'unknown'

def parse_aviationstack_response(flight):
    return {
        'airline': flight.get('airline', {}).get('name', 'Unknown Airline'),
        'flight_number': flight.get('flight', {}).get('iata', 'UNKNOWN'),
        'flight_iata': flight.get('flight', {}).get('iata', 'UNKNOWN'),
        'flight_icao': flight.get('flight', {}).get('icao', 'UNKNOWN'),
        'icao24': flight.get('flight', {}).get('icao24'),
        'departure': {
            'airport': flight.get('departure', {}).get('airport', 'Unknown'),
            'city': flight.get('departure', {}).get('timezone', '').split('/')[0] if flight.get('departure', {}).get('timezone') else 'Unknown',
            'iata': flight.get('departure', {}).get('iata', 'XXX'),
            'scheduled': flight.get('departure', {}).get('scheduled'),
            'estimated': flight.get('departure', {}).get('estimated'),
        },
        'arrival': {
            'airport': flight.get('arrival', {}).get('airport', 'Unknown'),
            'city': flight.get('arrival', {}).get('timezone', '').split('/')[0] if flight.get('arrival', {}).get('timezone') else 'Unknown',
            'iata': flight.get('arrival', {}).get('iata', 'XXX'),
            'scheduled': flight.get('arrival', {}).get('scheduled'),
            'estimated': flight.get('arrival', {}).get('estimated'),
        },
        'status': flight.get('flight_status', 'unknown'),
        'stage': determine_stage(flight.get('flight_status', 'unknown'))
    }

def fetch_flight_data(airline_code, flight_number, flight_date):
    if not API_KEY:
        print("⚠️  AVIATIONSTACK_API_KEY not set - using mock data")
        return create_mock_flight_data(airline_code, flight_number, flight_date)
    
    try:
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            'access_key': API_KEY,
            'flight_iata': f"{airline_code}{flight_number}",
            'flight_date': flight_date
        }
        
        print(f"🔍 Fetching flight data for {airline_code}{flight_number} on {flight_date}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('data'):
            print(f"⚠️  No flight data found - using mock data")
            return create_mock_flight_data(airline_code, flight_number, flight_date)
        
        flight = data['data'][0]
        return parse_aviationstack_response(flight)
        
    except Exception as e:
        print(f"⚠️  API error: {e} - using mock data")
        return create_mock_flight_data(airline_code, flight_number, flight_date)

def load_trips():
    if not TRIPS_FILE.exists():
        return []
    
    trips = []
    with open(TRIPS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                trips.append(json.loads(line))
    return trips

def save_trips(trips):
    TRIPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRIPS_FILE, 'w') as f:
        for trip in trips:
            f.write(json.dumps(trip) + '\n')

def update_trips(flight_data=None, status_update=None):
    trips = load_trips()
    
    active_trip = None
    for trip in trips:
        if trip.get('status') == 'active':
            active_trip = trip
            break
    
    if status_update:
        if active_trip:
            active_trip['current_stage'] = status_update
            active_trip['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
            if 'outbound_flight' in active_trip:
                active_trip['outbound_flight']['stage'] = status_update
                active_trip['outbound_flight']['status'] = status_update
            
            save_trips(trips)
            print(f"✅ Updated status to: {status_update}")
            return active_trip
        else:
            print("⚠️  No active trip found to update status")
            return None
    
    if flight_data:
        now = datetime.utcnow().isoformat() + 'Z'
        
        if not active_trip:
            active_trip = {
                'trip_id': f"trip-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'status': 'active',
                'created_at': now,
                'updated_at': now,
                'current_stage': flight_data['stage'],
                'outbound_flight': flight_data,
                'manual_updates': []
            }
            trips.append(active_trip)
        else:
            if 'outbound_flight' not in active_trip or active_trip.get('current_stage') in ['landed', 'arrived']:
                active_trip['outbound_flight'] = flight_data
            else:
                active_trip['return_flight'] = flight_data
            
            active_trip['updated_at'] = now
            active_trip['current_stage'] = flight_data['stage']
        
        save_trips(trips)
        print(f"✅ Added flight {flight_data['flight_number']} to trip {active_trip['trip_id']}")
        return active_trip
    
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: llm_interpreter.py <natural language instruction>")
        sys.exit(1)
    
    instruction = ' '.join(sys.argv[1:])
    print(f"📝 Processing: {instruction}")
    
    parsed = parse_instruction(instruction)
    print(f"🧠 Parsed: {json.dumps(parsed, indent=2)}")
    
    if parsed['status_update']:
        result = update_trips(status_update=parsed['status_update'])
        if result:
            print(f"\n✈️  Trip updated successfully!")
    elif parsed['airline_code'] and parsed['flight_number'] and parsed['date']:
        flight_data = fetch_flight_data(
            parsed['airline_code'],
            parsed['flight_number'],
            parsed['date']
        )
        result = update_trips(flight_data=flight_data)
        if result:
            print(f"\n✈️  Flight tracked successfully!")
            print(f"    {flight_data['airline']} {flight_data['flight_number']}")
            print(f"    {flight_data['departure']['city']} → {flight_data['arrival']['city']}")
            print(f"    Status: {flight_data['status']}")
    else:
        print("❌ Could not parse instruction. Please provide:")
        print("   - Flight number and date (e.g., 'UA123 tomorrow')")
        print("   - Or status update (e.g., 'just landed')")
        sys.exit(1)

if __name__ == '__main__':
    main()

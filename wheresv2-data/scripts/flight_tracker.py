#!/usr/bin/env python3
"""Worker 1: AviationStack Flight Tracker"""
import json, os, sys, time, requests
from datetime import datetime

AVIATIONSTACK_API_KEY = os.getenv('AVIATIONSTACK_API_KEY', '')
TRIPS_FILE = '/home/workspace/wheresv2-data/trips.jsonl'

def fetch_flight(flight_iata, flight_date):
    if not AVIATIONSTACK_API_KEY:
        return None
    url = 'http://api.aviationstack.com/v1/flights'
    params = {'access_key': AVIATIONSTACK_API_KEY, 'flight_iata': flight_iata, 'flight_date': flight_date}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data['data'][0] if data.get('data') else None
    except:
        return None

def determine_stage(flight_data):
    status = flight_data.get('flight_status', '').lower()
    if status == 'landed': return 'landed'
    elif status == 'active': return 'in_air'
    elif status in ['scheduled', 'cancelled']: return 'preparing'
    return 'preparing'

def update_trip(trip_id, flight_type, flight_data):
    with open(TRIPS_FILE, 'r') as f:
        trips = [json.loads(l) for l in f]
    
    for trip in trips:
        if trip['trip_id'] == trip_id:
            stage = determine_stage(flight_data)
            dep = flight_data.get('departure', {})
            arr = flight_data.get('arrival', {})
            
            trip[flight_type].update({
                'status': flight_data.get('flight_status'),
                'stage': stage,
                'icao24': flight_data.get('aircraft', {}).get('icao24')
            })
            trip[flight_type]['departure'].update({
                'actual': dep.get('actual'),
                'estimated': dep.get('estimated'),
                'terminal': dep.get('terminal'),
                'gate': dep.get('gate')
            })
            trip[flight_type]['arrival'].update({
                'actual': arr.get('actual'),
                'estimated': arr.get('estimated'),
                'terminal': arr.get('terminal'),
                'gate': arr.get('gate')
            })
            trip['current_stage'] = stage
            trip['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            break
    
    with open(TRIPS_FILE, 'w') as f:
        f.write('\n'.join(json.dumps(t) for t in trips))

if __name__ == '__main__':
    # Test mode
    if len(sys.argv) == 3:
        data = fetch_flight(sys.argv[1], sys.argv[2])
        if data:
            print(json.dumps(data, indent=2))
            print(f"Stage: {determine_stage(data)}")

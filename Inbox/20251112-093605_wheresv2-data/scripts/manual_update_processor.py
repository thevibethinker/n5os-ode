#!/usr/bin/env python3
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
import re

TRIPS_FILE = Path("/home/workspace/wheresv2-data/trips.jsonl")

STAGE_KEYWORDS = {
    'preparing': ['packing', 'getting ready', 'heading to airport', 'leaving for airport', 'on way to airport', 'checking in', 'at check-in'],
    'boarding': ['at gate', 'boarding', 'about to board', 'boarding now', 'gate', 'boarding call', 'pre-boarding', 'waiting to board'],
    'in_air': ['taking off', 'took off', 'departed', 'in the air', 'wheels up', 'flying', 'on the plane', 'in flight', 'cruising'],
    'landed': ['landed', 'arrived', 'touched down', 'made it', 'wheels down', 'on the ground', 'just landed'],
    'at_destination': ['at hotel', 'checked in', 'at the hotel', 'in my room', 'made it to', 'arrived at hotel']
}

LOCATION_PATTERNS = [r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', r'\bgate\s+([A-Z]\d+)', r'\broom\s+(\d+)']

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

def get_active_trip(trips):
    for trip in trips:
        if trip.get('status') == 'active':
            return trip
    return None

def detect_stage_change(message):
    message_lower = message.lower()
    best_match = None
    best_confidence = 0
    for stage, keywords in STAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                confidence = len(keyword) / len(message_lower)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = stage
    if best_confidence > 0:
        return best_match, best_confidence
    return None, 0

def extract_location(message):
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    return None

def interpret_update(message):
    result = {
        'raw_message': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'stage_change': None,
        'confidence': 0,
        'location': None,
        'event_type': 'general_update',
        'description': message
    }
    stage, confidence = detect_stage_change(message)
    if stage:
        result['stage_change'] = stage
        result['confidence'] = confidence
    
    location = extract_location(message)
    if location:
        result['location'] = location
    
    # Check stage detection FIRST (if confidence > 0.3)
    if stage and confidence > 0.3:
        result['event_type'] = 'stage_change'
    # Only check other event types if stage detection didn't match
    elif any(word in message.lower() for word in ['delay', 'delayed']):
        result['event_type'] = 'delay'
    elif any(word in message.lower() for word in ['cancel', 'cancelled']):
        result['event_type'] = 'cancellation'
    elif any(word in message.lower() for word in ['hotel', 'room', 'checked in']):
        result['event_type'] = 'accommodation'
    
    return result

def process_manual_update(message):
    trips = load_trips()
    active_trip = get_active_trip(trips)
    if not active_trip:
        return {'success': False, 'error': 'No active trip found', 'message': 'No active trip to update'}
    interpretation = interpret_update(message)
    manual_update_entry = {'timestamp': interpretation['timestamp'], 'message': message, 'event_type': interpretation['event_type'], 'location': interpretation['location']}
    if 'manual_updates' not in active_trip:
        active_trip['manual_updates'] = []
    active_trip['manual_updates'].append(manual_update_entry)
    stage_updated = False
    old_stage = active_trip.get('current_stage', 'unknown')
    if interpretation['stage_change'] and interpretation['confidence'] > 0.02:
        active_trip['current_stage'] = interpretation['stage_change']
        active_trip['updated_at'] = interpretation['timestamp']
        stage_updated = True
        if 'outbound_flight' in active_trip:
            active_trip['outbound_flight']['stage'] = interpretation['stage_change']
            active_trip['outbound_flight']['status'] = interpretation['stage_change']
    else:
        active_trip['updated_at'] = interpretation['timestamp']
    save_trips(trips)
    response = {'success': True, 'trip_id': active_trip['trip_id'], 'update_added': True, 'stage_updated': stage_updated, 'interpretation': interpretation}
    if stage_updated:
        response['stage_change'] = {'from': old_stage, 'to': interpretation['stage_change']}
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: manual_update_processor.py <message>")
        sys.exit(1)
    message = ' '.join(sys.argv[1:])
    print(f"Processing: {message}")
    result = process_manual_update(message)
    if result['success']:
        print(f"Success! Trip: {result['trip_id']}, Event: {result['interpretation']['event_type']}")
        if result['stage_updated']:
            print(f"Stage: {result['stage_change']['from']} -> {result['stage_change']['to']}")
        else:
            print("Update logged, no stage change")
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()

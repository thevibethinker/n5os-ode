#!/usr/bin/env python3
"""Worker 2: SMS Manual Override Receiver"""
import json, os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
TRIPS_FILE = '/home/workspace/wheresv2-data/trips.jsonl'

@app.route('/sms/webhook', methods=['POST'])
def receive_sms():
    """Receive SMS from Telnyx webhook"""
    try:
        data = request.json
        from_number = data.get('from')
        message = data.get('text', '')
        
        # Add to active trip's manual_updates
        with open(TRIPS_FILE, 'r') as f:
            trips = [json.loads(l) for l in f]
        
        for trip in trips:
            if trip['status'] == 'active':
                trip['manual_updates'].append({
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'message': message,
                    'from': from_number
                })
                break
        
        with open(TRIPS_FILE, 'w') as f:
            f.write('\n'.join(json.dumps(t) for t in trips))
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manual-update', methods=['POST'])
def manual_update():
    """Direct API for manual updates (bypass SMS)"""
    try:
        data = request.json
        message = data.get('message')
        trip_id = data.get('trip_id', 'test-flight')
        
        with open(TRIPS_FILE, 'r') as f:
            trips = [json.loads(l) for l in f]
        
        for trip in trips:
            if trip['trip_id'] == trip_id:
                trip['manual_updates'].append({
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'message': message,
                    'source': 'api'
                })
                break
        
        with open(TRIPS_FILE, 'w') as f:
            f.write('\n'.join(json.dumps(t) for t in trips))
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8777))
    app.run(host='0.0.0.0', port=port)

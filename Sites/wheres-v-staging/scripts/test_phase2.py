#!/usr/bin/env python3
"""Unit tests for Phase 2: Backend API"""
import subprocess
import json
import time
import signal

def test_api_endpoint(endpoint: str, expected_keys: list = None):
    """Test if API endpoint returns valid response"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'http://localhost:54179{endpoint}'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if expected_keys:
                for key in expected_keys:
                    if key not in data:
                        print(f"  ✗ Missing key: {key}")
                        return False
            return data
        else:
            print(f"  ✗ HTTP error: {result.returncode}")
            return None
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return None

print("=== Phase 2 Unit Tests ===\n")

# Test 1: /health returns status: ok
print("Test 1: GET /health returns {status: 'ok'}")
health_data = test_api_endpoint('/health', ['status'])
if health_data and health_data.get('status') == 'ok':
    print("  ✓ Health check works")
else:
    print("  ✗ Health check failed")
    exit(1)

# Test 2: /api/status returns current_trip, next_trip, is_home
print("\nTest 2: GET /api/status returns current_trip, next_trip, is_home")
status_data = test_api_endpoint('/api/status', ['current_trip', 'next_trip', 'is_home'])
if status_data:
    print("  ✓ /api/status returns correct structure")
    print(f"    - is_home: {status_data['is_home']}")
    print(f"    - current_trip: {status_data.get('current_trip', 'None')}")
    print(f"    - next_trip: {status_data.get('next_trip', {}).get('id', 'None')}")
else:
    print("  ✗ /api/status failed")
    exit(1)

# Test 3: /api/trips returns array
print("\nTest 3: GET /api/trips returns array")
trips_data = test_api_endpoint('/api/trips')
if trips_data and isinstance(trips_data, list):
    print(f"  ✓ /api/trips returns array with {len(trips_data)} trip(s)")
else:
    print("  ✗ /api/trips failed or not an array")
    exit(1)

print("\n=== Phase 2 Tests: PASSED ===")

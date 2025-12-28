#!/usr/bin/env python3
"""Phase 3 unit tests - Frontend display"""

import subprocess
import requests
import time
import json

def test_frontend_loads():
    """Test that frontend serves HTML with React root"""
    try:
        response = requests.get('http://localhost:54179/')
        if response.status_code != 200:
            return False, f"GET / returned {response.status_code}"
        
        if '<div id="root">' not in response.text:
            return False, "React root not found in HTML"
        
        if 'main.tsx' not in response.text:
            return False, "main.tsx not referenced"
        
        return True, "Frontend loads with React app structure"
    except Exception as e:
        return False, str(e)

def test_api_via_proxy():
    """Test that API calls go through Vite proxy"""
    try:
        # These should be proxied to port 3002
        response = requests.get('http://localhost:54179/api/status')
        if response.status_code != 200:
            return False, f"GET /api/status returned {response.status_code}"
        
        data = response.json()
        if 'is_home' not in data:
            return False, "Response missing 'is_home' field"
        
        return True, f"API proxy works, is_home={data.get('is_home')}"
    except Exception as e:
        return False, str(e)

def test_health_check():
    """Test health endpoint via proxy"""
    try:
        response = requests.get('http://localhost:54179/health')
        if response.status_code != 200:
            return False, f"GET /health returned {response.status_code}"
        
        data = response.json()
        if data.get('status') != 'ok':
            return False, f"Health check returned {data}"
        
        return True, "Health check via proxy works"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("=== Phase 3 Unit Tests ===\n")
    
    tests = [
        ("Frontend loads", test_frontend_loads),
        ("API via proxy", test_api_via_proxy),
        ("Health check", test_health_check),
    ]
    
    passed = 0
    for name, test_func in tests:
        success, msg = test_func()
        status = "✓" if success else "✗"
        print(f"{status} {name}: {msg}")
        if success:
            passed += 1
    
    print(f"\n=== Phase 3 Tests: {passed}/{len(tests)} PASSED ===")
    
    exit(0 if passed == len(tests) else 1)

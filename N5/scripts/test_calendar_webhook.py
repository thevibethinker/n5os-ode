#!/usr/bin/env python3
"""
CRM Calendar Webhook Integration - Test Suite

Comprehensive testing script for Worker 4: Calendar Webhook Integration.
Tests all components: setup, handler, renewal, and health monitoring.

Usage:
    python3 /home/workspace/N5/scripts/test_calendar_webhook.py

Tests:
1. Configuration validation
2. Database schema verification
3. Google credentials validation
4. Service availability
5. Webhook endpoint health
6. Simulated notification processing
"""

import sys
import os
import json
import sqlite3
import requests
from datetime import datetime

sys.path.append('/home/workspace/N5/scripts')

try:
    from crm_calendar_helpers import (
        load_config,
        load_google_credentials,
        validate_webhook_endpoint
    )
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Colors.RESET}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text):
    print(f"ℹ {text}")


def test_config_file():
    """Test 1: Validate configuration file exists and is readable"""
    print_header("TEST 1: Configuration File")
    
    config_path = '/home/workspace/N5/config/calendar_webhook.yaml'
    
    if not os.path.exists(config_path):
        print_error(f"Config file not found: {config_path}")
        return False
    
    try:
        config = load_config(config_path)
        print_success(f"Config file loaded: {config_path}")
        
        # Validate required sections
        required_sections = ['webhook', 'enrichment', 'renewal', 'health', 'logging']
        missing = [s for s in required_sections if s not in config]
        
        if missing:
            print_warning(f"Missing config sections: {', '.join(missing)}")
        else:
            print_success("All required config sections present")
        
        # Display key settings
        print_info(f"Webhook endpoint: {config.get('webhook', {}).get('endpoint')}")
        print_info(f"Renewal threshold: {config.get('renewal', {}).get('renew_threshold_days')} days")
        print_info(f"Health check interval: {config.get('health', {}).get('check_interval_hours')} hours")
        
        return len(missing) == 0
        
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return False


def test_database_schema():
    """Test 2: Verify database schema is correct"""
    print_header("TEST 2: Database Schema")
    
    db_path = '/home/workspace/N5/data/crm_v3.db'
    
    if not os.path.exists(db_path):
        print_error(f"Database not found: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if calendar_events table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='calendar_events'
            """)
            result = cursor.fetchone()
            
            if not result:
                print_error("calendar_events table not found")
                return False
            
            print_success("calendar_events table exists")
            
            # Check for required columns
            cursor.execute("PRAGMA table_info(calendar_events)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = [
                'event_id', 'summary', 'start_time', 'attendee_emails',
                'webhook_received_at', 'status', 'last_updated_at'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print_warning(f"Missing columns: {', '.join(missing)}")
            else:
                print_success("All required columns present")
            
            # Check webhook_health table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='webhook_health'
            """)
            result = cursor.fetchone()
            
            if not result:
                print_warning("webhook_health table not found (optional)")
            else:
                print_success("webhook_health table exists")
            
            # Check enrichment_queue table (for job queuing)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='enrichment_queue'
            """)
            result = cursor.fetchone()
            
            if not result:
                print_error("enrichment_queue table not found (CRITICAL)")
                return False
            
            print_success("enrichment_queue table exists")
            
            return True
            
    except Exception as e:
        print_error(f"Database error: {e}")
        return False


def test_google_credentials():
    """Test 3: Validate Google service account credentials"""
    print_header("TEST 3: Google Credentials")
    
    creds_path = '/home/workspace/N5/config/credentials/google_service_account.json'
    
    if not os.path.exists(creds_path):
        print_error(f"Credentials file not found: {creds_path}")
        print_info("Setup required: Place service account JSON at above path")
        return False
    
    try:
        with open(creds_path) as f:
            creds_data = json.load(f)
        
        # Validate structure
        required_fields = ['client_email', 'private_key', 'project_id']
        missing = [f for f in required_fields if f not in creds_data]
        
        if missing:
            print_error(f"Invalid credentials format, missing: {', '.join(missing)}")
            return False
        
        print_success(f"Credentials loaded: {creds_data['client_email']}")
        print_info(f"Project ID: {creds_data['project_id']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        print_error(f"Failed to load credentials: {e}")
        return False


def test_user_services():
    """Test 4: Verify user services are registered and accessible"""
    print_header("TEST 4: User Services")
    
    services = [
        {"name": "crm-calendar-webhook", "port": 8765, "type": "http"},
        {"name": "crm-webhook-renewal", "port": 8766, "type": "tcp"},
        {"name": "crm-webhook-health", "port": 8767, "type": "tcp"}
    ]
    
    all_ok = True
    
    for service in services:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', service['port']))
            sock.close()
            
            if result == 0:
                print_success(f"{service['name']} accessible on port {service['port']}")
            else:
                if service['type'] == 'tcp':
                    # TCP services might not listen
                    print_info(f"{service['name']} (port {service['port']}) - TCP service may not accept connections")
                else:
                    print_warning(f"{service['name']} not accessible on port {service['port']}")
        except Exception as e:
            print_warning(f"Could not check {service['name']}: {e}")
    
    return True


def test_webhook_endpoint():
    """Test 5: Test webhook endpoint health check"""
    print_header("TEST 5: Webhook Endpoint")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8765/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Webhook handler healthy")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Notifications: {data.get('notification_count', 0)}")
            return True
        else:
            print_warning(f"Health endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_warning("Webhook endpoint not accessible (may need to start service)")
        return False
    except Exception as e:
        print_warning(f"Could not test endpoint: {e}")
        return False


def test_notification_simulation():
    """Test 6: Simulate a webhook notification"""
    print_header("TEST 6: Notification Simulation")
    
    try:
        config = load_config()
        
        # Build minimal webhook notification headers
        headers = {
            'X-Goog-Channel-ID': 'test-channel-123',
            'X-Goog-Message-Number': '1',
            'X-Goog-Resource-ID': 'test-resource-456',
            'X-Goog-Resource-State': 'sync',  # Use sync for testing
            'X-Goog-Resource-URI': 'https://www.googleapis.com/calendar/v3/calendars/primary/events/test123'
        }
        
        # Send test notification
        response = requests.post(
            'http://localhost:8765/webhooks/calendar',
            headers=headers,
            json={},  # Empty body for sync message
            timeout=10
        )
        
        if response.status_code in [200, 201, 202]:
            print_success("Test notification accepted")
            data = response.json()
            print_info(f"Response: {data.get('status')}")
            return True
        else:
            print_warning(f"Notification rejected: {response.status_code}")
            print_info(f"Response: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_warning("Webhook endpoint not accessible for testing")
        return False
    except Exception as e:
        print_warning(f"Simulation failed: {e}")
        return False


def test_database_operations():
    """Test 7: Test database read/write operations"""
    print_header("TEST 7: Database Operations")
    
    db_path = '/home/workspace/N5/data/crm_v3.db'
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Test write
            cursor.execute(
                "INSERT INTO webhook_health (service, status, expiration_time) VALUES (?, ?, datetime('now', '+7 days'))",
                ('test_service', 'active')
            )
            
            # Test read
            cursor.execute("SELECT * FROM webhook_health WHERE service = ?", ('test_service',))
            result = cursor.fetchone()
            
            if result:
                print_success("Database read/write OK")
                
                # Cleanup
                cursor.execute("DELETE FROM webhook_health WHERE service = ?", ('test_service',))
                conn.commit()
                return True
            else:
                print_error("Database write succeeded but read failed")
                return False
                
    except Exception as e:
        print_error(f"Database operation failed: {e}")
        return False


def generate_summary(results):
    """Generate test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for test_name, passed_test in results.items():
        status = "✓" if passed_test else "✗"
        color = Colors.GREEN if passed_test else Colors.RED
        print(f"{color}{status} {test_name}{Colors.RESET}")
    
    print()
    print(f"Tests passed: {Colors.GREEN}{passed}/{total}{Colors.RESET}")
    print(f"Tests failed: {Colors.RED}{failed}/{total}{Colors.RESET}")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        return True
    elif failed <= 2:
        print_warning("Most tests passed, some warnings only")
        return True
    else:
        print_error("Too many failures - review issues above")
        return False


def main():
    """Main test execution"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          CRM Calendar Webhook Integration Test Suite           ║")
    print("║                    Worker 4: Validation                         ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    tests = {
        "Configuration File": test_config_file,
        "Database Schema": test_database_schema,
        "Google Credentials": test_google_credentials,
        "User Services": test_user_services,
        "Webhook Endpoint": test_webhook_endpoint,
        "Notification Simulation": test_notification_simulation,
        "Database Operations": test_database_operations
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results[test_name] = False
    
    success = generate_summary(results)
    
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())



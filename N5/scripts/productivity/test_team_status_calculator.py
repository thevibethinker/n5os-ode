#!/usr/bin/env python3
"""
Test Suite for Team Status Calculator
Tests business logic, edge cases, and validates against requirements.
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from team_status_calculator import TeamStatusCalculator, THRESHOLDS

DB_PATH = "/home/workspace/productivity_tracker.db"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, condition: bool, message: str = ""):
        self.tests.append(name)
        if condition:
            print(f"✅ {name}")
            self.passed += 1
        else:
            print(f"❌ {name}: {message}")
            self.failed += 1
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total: {len(self.tests)}")
        print(f"{'='*60}\n")
        return self.failed == 0


def test_top5_calculation():
    """Test various scenarios of top 5 of 7 averaging"""
    runner = TestRunner()
    calc = TeamStatusCalculator(DB_PATH)
    
    print("\n=== Testing Top 5 of 7 Calculation ===\n")
    
    # Test 1: Normal 7 days
    rpi = [0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
    avg, grace = calc.calculate_top5_avg(rpi)
    expected_avg = (0.9 + 1.0 + 1.1 + 1.2 + 1.3) / 5  # 1.10
    runner.test(
        "Top 5 of 7 normal case",
        abs(avg - expected_avg) < 0.001 and grace == 2,
        f"Expected avg={expected_avg:.3f}, got {avg:.3f}"
    )
    
    # Test 2: Less than 7 days
    rpi = [1.0, 1.1]
    avg, grace = calc.calculate_top5_avg(rpi)
    runner.test(
        "Less than 7 days uses all data",
        avg == 1.05 and grace == 5,
        f"Expected avg=1.05, grace=5, got avg={avg}, grace={grace}"
    )
    
    # Test 3: Empty list
    rpi = []
    avg, grace = calc.calculate_top5_avg(rpi)
    runner.test("Empty RPI list returns (0.0, 0)", avg == 0.0 and grace == 0)
    
    # Test 4: All same values
    rpi = [1.0] * 7
    avg, grace = calc.calculate_top5_avg(rpi)
    runner.test("All same values", avg == 1.0 and grace == 2)
    
    return runner.summary()


def test_base_status_mapping():
    """Test threshold mapping to status tiers"""
    runner = TestRunner()
    calc = TeamStatusCalculator(DB_PATH)
    
    print("\n=== Testing Base Status Mapping ===\n")
    
    test_cases = [
        (0.50, 'transfer_list'),
        (0.69, 'transfer_list'),
        (0.70, 'reserves'),
        (0.89, 'reserves'),
        (0.90, 'squad_member'),
        (0.99, 'squad_member'),
        (1.00, 'first_team'),
        (1.24, 'first_team'),
        (1.25, 'invincible'),
        (1.49, 'invincible'),
        (1.50, 'legend'),
        (2.00, 'legend'),
    ]
    
    for rpi, expected in test_cases:
        result = calc.determine_base_status(rpi)
        runner.test(
            f"RPI {rpi} → {expected}",
            result == expected,
            f"Expected {expected}, got {result}"
        )
    
    return runner.summary()


def test_consecutive_poor_days():
    """Test consecutive poor days counting logic"""
    runner = TestRunner()
    calc = TeamStatusCalculator(DB_PATH)
    
    print("\n=== Testing Consecutive Poor Days ===\n")
    
    # This requires RPI data in DB - test with current data
    consecutive = calc.count_consecutive_poor_days('2025-11-02', 0.90)
    runner.test(
        "Consecutive poor days check doesn't crash",
        consecutive >= 0,
        "Function should return non-negative integer"
    )
    
    return runner.summary()


def test_real_calculation():
    """Test calculation with real DB data"""
    runner = TestRunner()
    calc = TeamStatusCalculator(DB_PATH)
    calc.verbose = False
    
    print("\n=== Testing Real Calculation ===\n")
    
    # Test with current date
    result = calc.calculate_status('2025-11-02')
    
    runner.test(
        "Calculation returns required fields",
        all(k in result for k in ['date', 'status', 'days_in_status', 'top5_avg', 'grace_days_used', 'changed', 'reason']),
        "Missing required fields"
    )
    
    runner.test(
        "Status is valid",
        result['status'] in ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend'],
        f"Invalid status: {result['status']}"
    )
    
    runner.test(
        "Days in status is positive",
        result['days_in_status'] > 0,
        f"Days in status should be positive, got {result['days_in_status']}"
    )
    
    runner.test(
        "Top5 avg is non-negative",
        result['top5_avg'] >= 0,
        f"Top5 avg should be non-negative, got {result['top5_avg']}"
    )
    
    runner.test(
        "Grace days used is valid",
        0 <= result['grace_days_used'] <= 7,
        f"Grace days should be 0-7, got {result['grace_days_used']}"
    )
    
    runner.test(
        "Changed is boolean",
        isinstance(result['changed'], bool),
        f"Changed should be bool, got {type(result['changed'])}"
    )
    
    return runner.summary()


def main():
    print("\n" + "="*60)
    print("TEAM STATUS CALCULATOR TEST SUITE")
    print("="*60)
    
    all_passed = True
    
    all_passed &= test_top5_calculation()
    all_passed &= test_base_status_mapping()
    all_passed &= test_consecutive_poor_days()
    all_passed &= test_real_calculation()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Calculator is ready for integration.\n")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Review failures above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

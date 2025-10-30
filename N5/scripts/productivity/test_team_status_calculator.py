#!/usr/bin/env python3
"""
Test Suite for Team Status Calculator

Tests all core functionality:
- Top 5 of 7 calculation
- Threshold mapping
- Promotion logic (immediate + probation)
- Demotion logic (consecutive tracking)
- Probation immunity
- Elite unlock patterns

Author: N5 System (W2)
Date: 2025-10-30
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from team_status_calculator import TeamStatusCalculator, THRESHOLDS

# Test database path
TEST_DB = "/tmp/test_productivity_tracker.db"


def setup_test_db():
    """Create test database with schema"""
    # Remove existing
    Path(TEST_DB).unlink(missing_ok=True)
    
    conn = sqlite3.connect(TEST_DB)
    
    # Create daily_stats table
    conn.execute("""
        CREATE TABLE daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            rpi REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create team_status_history table
    conn.execute("""
        CREATE TABLE team_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            days_in_status INTEGER NOT NULL DEFAULT 1,
            previous_status TEXT,
            top5_avg REAL,
            grace_days_used INTEGER DEFAULT 0,
            consecutive_poor_days INTEGER DEFAULT 0,
            probation_days_remaining INTEGER DEFAULT 0,
            reason TEXT,
            changed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Test database created: {TEST_DB}")


def insert_rpi_data(date_rpi_pairs: list):
    """Insert RPI data for testing"""
    conn = sqlite3.connect(TEST_DB)
    
    for date_str, rpi_val in date_rpi_pairs:
        conn.execute(
            "INSERT OR REPLACE INTO daily_stats (date, rpi) VALUES (?, ?)",
            (date_str, rpi_val)
        )
    
    conn.commit()
    conn.close()


def insert_status_history(status_data: dict):
    """Insert a status history record"""
    conn = sqlite3.connect(TEST_DB)
    
    conn.execute("""
        INSERT INTO team_status_history 
        (date, status, days_in_status, previous_status, top5_avg, 
         grace_days_used, consecutive_poor_days, probation_days_remaining, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        status_data['date'],
        status_data['status'],
        status_data['days_in_status'],
        status_data.get('previous_status'),
        status_data['top5_avg'],
        status_data['grace_days_used'],
        status_data['consecutive_poor_days'],
        status_data['probation_days_remaining'],
        status_data['reason']
    ))
    
    conn.commit()
    conn.close()


def test_top5_calculation():
    """Test top 5 of 7 averaging"""
    print("\n" + "="*60)
    print("TEST: Top 5 of 7 Calculation")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Test 1: Standard 7 days
    test_date = '2025-10-30'
    rpi_data = [
        ('2025-10-24', 50.0),   # Drop
        ('2025-10-25', 80.0),   # Drop
        ('2025-10-26', 90.0),   # Keep
        ('2025-10-27', 100.0),  # Keep
        ('2025-10-28', 110.0),  # Keep
        ('2025-10-29', 120.0),  # Keep
        ('2025-10-30', 130.0)   # Keep
    ]
    insert_rpi_data(rpi_data)
    
    top5_avg, grace_used = calc.calculate_top5_avg([0.50, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30])
    
    # Top 5: [1.30, 1.20, 1.10, 1.00, 0.90] = 1.10
    expected_avg = 1.10
    expected_grace = 2
    
    assert abs(top5_avg - expected_avg) < 0.01, f"Expected {expected_avg}, got {top5_avg}"
    assert grace_used == expected_grace, f"Expected {expected_grace} grace days, got {grace_used}"
    
    print(f"✓ Standard 7 days: avg={top5_avg:.2f}, grace={grace_used}")
    
    # Test 2: Less than 7 days
    top5_avg, grace_used = calc.calculate_top5_avg([1.80, 0.0])
    expected_avg = 0.90
    expected_grace = 5
    
    assert abs(top5_avg - expected_avg) < 0.01, f"Expected {expected_avg}, got {top5_avg}"
    assert grace_used == expected_grace, f"Expected {expected_grace} grace days, got {grace_used}"
    
    print(f"✓ Edge case (<7 days): avg={top5_avg:.2f}, grace={grace_used}")
    
    print("✓ All top5 calculation tests passed!")


def test_threshold_mapping():
    """Test status tier mapping"""
    print("\n" + "="*60)
    print("TEST: Threshold Mapping")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    test_cases = [
        (0.50, 'transfer_list'),
        (0.70, 'reserves'),
        (0.89, 'reserves'),
        (0.90, 'squad_member'),
    (0.99, 'squad_member'),
        (1.00, 'first_team'),
        (1.24, 'first_team'),
        (1.25, 'invincible'),
        (1.49, 'invincible'),
        (1.50, 'legend'),
        (2.00, 'legend')
    ]
    
    for rpi, expected_status in test_cases:
        result = calc.determine_base_status(rpi)
        assert result == expected_status, f"RPI {rpi} should map to {expected_status}, got {result}"
        print(f"✓ {rpi:.2f} → {expected_status}")
    
    print("✓ All threshold mapping tests passed!")


def test_first_day_initialization():
    """Test behavior with no historical data"""
    print("\n" + "="*60)
    print("TEST: First Day Initialization")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Insert RPI but no status history
    insert_rpi_data([('2025-10-29', 180.0)])
    
    result = calc.calculate_status('2025-10-29')
    
    assert result['status'] == 'first_team', "Should start at first_team"
    assert result['changed'] == True, "Should be marked as changed"
    assert result['days_in_status'] == 1, "Should be day 1"
    assert result['previous_status'] is None, "No previous status"
    
    print(f"✓ First day: {result['status']}, top5_avg={result['top5_avg']:.2f}")
    print("✓ First day initialization test passed!")


def test_immediate_promotion():
    """Test single-day promotion (not from squad_member)"""
    print("\n" + "="*60)
    print("TEST: Immediate Promotion")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Setup: currently in reserves, hit first_team threshold
    insert_rpi_data([
        ('2025-10-29', 80.0),
        ('2025-10-30', 100.0)
    ])
    
    insert_status_history({
        'date': '2025-10-29',
        'status': 'reserves',
        'days_in_status': 5,
        'previous_status': 'transfer_list',
        'top5_avg': 0.80,
        'grace_days_used': 6,
        'consecutive_poor_days': 0,
        'probation_days_remaining': 0,
        'reason': 'Test setup'
    })
    
    result = calc.calculate_status('2025-10-30')
    
    assert result['status'] == 'squad_member', f"Should promote to squad_member, got {result['status']}"
    assert result['changed'] == True, "Should be marked as changed"
    assert result['previous_status'] == 'reserves', "Should track previous status"
    assert result['probation_days_remaining'] == 7, "Should start 7-day probation"
    
    print(f"✓ Promoted from reserves to squad_member")
    print(f"  Probation: {result['probation_days_remaining']} days")
    print("✓ Immediate promotion test passed!")


def test_probation_period():
    """Test 3-day requirement from squad_member to first_team"""
    print("\n" + "="*60)
    print("TEST: Probation Period (squad_member → first_team)")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Day 1: Just promoted to squad_member
    insert_rpi_data([('2025-10-29', 95.0)])
    insert_status_history({
        'date': '2025-10-29',
        'status': 'squad_member',
        'days_in_status': 1,
        'previous_status': 'reserves',
        'top5_avg': 0.95,
        'grace_days_used': 6,
        'consecutive_poor_days': 0,
        'probation_days_remaining': 7,
        'reason': 'Promoted from reserves'
    })
    
    # Day 2: Still at 100%, but only 2 days
    insert_rpi_data([('2025-10-30', 100.0)])
    result = calc.calculate_status('2025-10-30')
    
    assert result['status'] == 'squad_member', f"Should stay in squad_member (day 2), got {result['status']}"
    assert result['days_in_status'] == 2, f"Should be day 2, got {result['days_in_status']}"
    assert result['changed'] == False, "Should not change yet"
    
    print(f"✓ Day 2: Still squad_member (need 3 days)")
    
    # Day 3: Hit first_team threshold for 3rd time
    insert_status_history({
        'date': '2025-10-30',
        'status': 'squad_member',
        'days_in_status': 2,
        'previous_status': 'reserves',
        'top5_avg': 0.95,
        'grace_days_used': 6,
        'consecutive_poor_days': 0,
        'probation_days_remaining': 6,
        'reason': 'Maintained'
    })
    insert_rpi_data([('2025-10-31', 105.0)])
    result = calc.calculate_status('2025-10-31')
    
    assert result['status'] == 'first_team', f"Should promote to first_team (day 3), got {result['status']}"
    assert result['changed'] == True, "Should be marked as changed"
    assert result['probation_days_remaining'] == 0, "Probation should end"
    
    print(f"✓ Day 3: Promoted to first_team (probation complete)")
    print("✓ Probation period test passed!")


def test_demotion_consecutive():
    """Test 3-day demotion threshold from first_team"""
    print("\n" + "="*60)
    print("TEST: Demotion (Consecutive Poor Days)")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Setup: in first_team, starting to perform poorly
    insert_rpi_data([
        ('2025-10-27', 100.0),
        ('2025-10-28', 85.0),  # Poor day 1
        ('2025-10-29', 85.0),  # Poor day 2
    ])
    
    insert_status_history({
        'date': '2025-10-29',
        'status': 'first_team',
        'days_in_status': 10,
        'previous_status': None,
        'top5_avg': 0.85,
        'grace_days_used': 6,
        'consecutive_poor_days': 2,  # 2 days below 90%
        'probation_days_remaining': 0,
        'reason': 'Maintained'
    })
    
    # Day 3 of poor performance: should demote
    insert_rpi_data([('2025-10-30', 85.0)])  # Poor day 3
    result = calc.calculate_status('2025-10-30')
    
    assert result['status'] == 'squad_member', f"Should demote to squad_member, got {result['status']}"
    assert result['changed'] == True, "Should be marked as changed"
    assert result['previous_status'] == 'first_team', "Should track previous"
    assert result['probation_days_remaining'] == 0, "No probation when demoted TO squad_member"
    
    print(f"✓ Demoted after 3 consecutive days <90%")
    print("✓ Demotion test passed!")


def test_probation_immunity():
    """Test that squad_member cannot be demoted during 7-day probation"""
    print("\n" + "="*60)
    print("TEST: Probation Immunity")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Setup: squad_member with probation active
    insert_rpi_data([
        ('2025-10-29', 95.0),
        ('2025-10-30', 50.0),  # Poor performance
        ('2025-10-31', 50.0),
        ('2025-11-01', 50.0),
        ('2025-11-02', 50.0),
        ('2025-11-03', 50.0),  # 5 poor days, normally would demote
    ])
    
    insert_status_history({
        'date': '2025-10-29',
        'status': 'squad_member',
        'days_in_status': 1,
        'previous_status': 'reserves',
        'top5_avg': 0.95,
        'grace_days_used': 6,
        'consecutive_poor_days': 0,
        'probation_days_remaining': 7,
        'reason': 'Promoted'
    })
    
    # Simulate 5 days of poor performance during probation
    current_date = datetime.strptime('2025-10-30', '%Y-%m-%d')
    for day_num in range(5):
        test_date = (current_date + timedelta(days=day_num)).strftime('%Y-%m-%d')
        result = calc.calculate_status(test_date)
        
        # Should stay in squad_member due to probation immunity
        assert result['status'] == 'squad_member', f"Should stay in squad_member during probation"
        print(f"✓ Day {day_num+1}: probation={result['probation_days_remaining']}, consecutive_poor={result['consecutive_poor_days']}")
        
        # Setup for next iteration
        if day_num < 4:
            insert_status_history(result)
    
    print("✓ Probation immunity test passed!")


def test_elite_unlock():
    """Test 2-in-7-days requirement for invincible unlock"""
    print("\n" + "="*60)
    print("TEST: Elite Unlock (Invincible)")
    print("="*60)
    
    setup_test_db()
    calc = TeamStatusCalculator(TEST_DB)
    
    # Setup: in first_team, hit 125% on 2 days within 7-day window
    insert_rpi_data([
        ('2025-10-24', 126.0),  # ✓ 126%
        ('2025-10-25', 130.0),  # ✓ 130% (first)
        ('2025-10-26', 125.0),  # ✓ 125%
        ('2025-10-27', 127.0),  # ✓ 127%
        ('2025-10-28', 128.0),  # ✓ 128% (second)
        ('2025-10-29', 126.0),  # ✓ 126%
        ('2025-10-30', 127.0),  # ✓ 127% (trigger) Top5 avg = (130+128+127+127+126)/5 = 127.6%
    ])
    
    insert_status_history({
        'date': '2025-10-29',
        'status': 'first_team',
        'days_in_status': 20,
        'previous_status': None,
        'top5_avg': 1.15,
        'grace_days_used': 2,
        'consecutive_poor_days': 0,
        'probation_days_remaining': 0,
        'reason': 'Maintained'
    })
    
    result = calc.calculate_status('2025-10-30')
    
    assert result['status'] == 'invincible', f"Should unlock invincible, got {result['status']}"
    assert result['changed'] == True, "Should be marked as changed"
    assert "unlocked" in result['reason'].lower(), "Reason should mention unlock"
    
    print(f"✓ Invincible unlocked (2 days ≥125% in 7-day window)")
    print(f"  Reason: {result['reason']}")
    print("✓ Elite unlock test passed!")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("TEAM STATUS CALCULATOR - TEST SUITE")
    print("="*70)
    
    try:
        test_top5_calculation()
        test_threshold_mapping()
        test_first_day_initialization()
        test_immediate_promotion()
        test_probation_period()
        test_demotion_consecutive()
        test_probation_immunity()
        test_elite_unlock()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*70)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        Path(TEST_DB).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(run_all_tests())

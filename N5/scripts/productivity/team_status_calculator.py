#!/usr/bin/env python3
"""
Team Status Calculator - Arsenal FC Career Simulator
Calculates V's team status based on recent productivity performance (RPI).

Usage:
    python3 team_status_calculator.py --date 2025-11-02
    python3 team_status_calculator.py --date 2025-11-02 --verbose
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sqlite3
import argparse
import sys

# Status thresholds (top5_avg determines tier)
THRESHOLDS = {
    'transfer_list': (0.0, 0.69),
    'reserves': (0.70, 0.89),
    'squad_member': (0.90, 0.99),
    'first_team': (1.00, 1.24),
    'invincible': (1.25, 1.49),
    'legend': (1.50, float('inf'))
}

# Status hierarchy for promotions/demotions
STATUS_HIERARCHY = ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend']


class TeamStatusCalculator:
    def __init__(self, db_path: str = "/home/workspace/productivity_tracker.db"):
        self.db_path = db_path
        self.verbose = False
    
    def log(self, message: str):
        """Print debug message if verbose mode enabled"""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def fetch_last_7_days_rpi(self, target_date: str) -> List[float]:
        """Fetch RPI for 7 days ending on target_date (inclusive)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        end_date = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=6)
        
        query = """
            SELECT date, rpi FROM daily_stats 
            WHERE date >= ? AND date <= ?
            ORDER BY date ASC
        """
        
        cursor = conn.execute(query, (start_date.strftime('%Y-%m-%d'), target_date))
        rows = cursor.fetchall()
        conn.close()
        
        rpi_values = [float(row['rpi']) if row['rpi'] is not None else 0.0 for row in rows]
        self.log(f"Fetched {len(rpi_values)} RPI values: {rpi_values}")
        
        return rpi_values
    
    def calculate_top5_avg(self, rpi_values: List[float]) -> Tuple[float, int]:
        """Calculate average of top 5 values, return (avg, grace_days_used)"""
        if len(rpi_values) == 0:
            return (0.0, 0)
        
        if len(rpi_values) < 7:
            # Edge case: less than 7 days of data
            grace_days_used = 7 - len(rpi_values)
            avg = sum(rpi_values) / len(rpi_values)
            self.log(f"Less than 7 days data: using all {len(rpi_values)} values, grace_days={grace_days_used}")
            return (avg, grace_days_used)
        
        # Normal case: take top 5 of 7
        sorted_vals = sorted(rpi_values, reverse=True)
        top5 = sorted_vals[:5]
        grace_days_used = 2
        avg = sum(top5) / len(top5)
        
        self.log(f"Top 5 of 7: {top5} → avg={avg:.3f}, grace_days={grace_days_used}")
        return (avg, grace_days_used)
    
    def determine_base_status(self, top5_avg: float) -> str:
        """Map top5_avg to status tier based on thresholds"""
        for status, (min_val, max_val) in THRESHOLDS.items():
            if min_val <= top5_avg <= max_val:
                return status
        return 'legend'  # Fallback for very high values
    
    def get_current_status_data(self, target_date: str) -> Optional[Dict]:
        """Fetch latest status from team_status_history before target_date"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
            SELECT * FROM team_status_history 
            WHERE date = (SELECT MAX(date) FROM team_status_history WHERE date < ?)
        """
        
        cursor = conn.execute(query, (target_date,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return dict(row)
    
    def check_elite_unlock(self, target_date: str) -> Tuple[bool, Optional[str]]:
        """
        Check if invincible or legend should be unlocked
        Returns: (unlocked, new_status or None)
        """
        conn = sqlite3.connect(self.db_path)
        end_date = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=6)
        
        # Check invincible unlock: 2 days >= 1.25 in 7-day window
        query = """
            SELECT COUNT(*) as count FROM daily_stats
            WHERE date >= ? AND date <= ? AND rpi >= 1.25
        """
        cursor = conn.execute(query, (start_date.strftime('%Y-%m-%d'), target_date))
        invincible_days = cursor.fetchone()[0]
        
        # Check legend unlock: 2 days >= 1.50 in 7-day window
        query = """
            SELECT COUNT(*) as count FROM daily_stats
            WHERE date >= ? AND date <= ? AND rpi >= 1.50
        """
        cursor = conn.execute(query, (start_date.strftime('%Y-%m-%d'), target_date))
        legend_days = cursor.fetchone()[0]
        
        conn.close()
        
        self.log(f"Elite unlock check: invincible_days={invincible_days}, legend_days={legend_days}")
        
        if legend_days >= 2:
            return (True, 'legend')
        elif invincible_days >= 2:
            return (True, 'invincible')
        
        return (False, None)
    
    def count_consecutive_poor_days(self, target_date: str, threshold: float) -> int:
        """Count consecutive days below threshold ending on target_date"""
        conn = sqlite3.connect(self.db_path)
        end_date = datetime.strptime(target_date, '%Y-%m-%d')
        
        # Check last 7 days backward from target
        consecutive = 0
        for i in range(7):
            check_date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            query = "SELECT rpi FROM daily_stats WHERE date = ?"
            cursor = conn.execute(query, (check_date,))
            row = cursor.fetchone()
            
            if row is None:
                break  # No data, stop counting
            
            rpi = float(row[0]) if row[0] is not None else 0.0
            
            if rpi < threshold:
                consecutive += 1
            else:
                break  # Streak broken
        
        conn.close()
        self.log(f"Consecutive poor days (<{threshold}): {consecutive}")
        return consecutive
    
    def calculate_status(self, target_date: str) -> Dict:
        """
        Main entry point. Calculate status for target_date.
        Returns comprehensive status data dict.
        """
        # 1. Fetch last 7 days RPI
        rpi_values = self.fetch_last_7_days_rpi(target_date)
        
        # 2. Calculate top5_avg
        top5_avg, grace_days_used = self.calculate_top5_avg(rpi_values)
        
        # 3. Get current status
        current_data = self.get_current_status_data(target_date)
        
        if current_data is None:
            # First day ever: Start at first_team
            self.log("First day ever: starting at 'first_team'")
            return {
                'date': target_date,
                'status': 'first_team',
                'days_in_status': 1,
                'previous_status': None,
                'top5_avg': top5_avg,
                'grace_days_used': grace_days_used,
                'consecutive_poor_days': 0,
                'probation_days_remaining': 0,
                'reason': 'Initial status',
                'changed': True
            }
        
        current_status = current_data['status']
        days_in_status = current_data['days_in_status']
        probation_remaining = current_data['probation_days_remaining']
        
        self.log(f"Current: status={current_status}, days={days_in_status}, probation={probation_remaining}")
        
        # 4. Determine base status from performance
        base_status = self.determine_base_status(top5_avg)
        self.log(f"Base status from performance: {base_status}")
        
        # 5. Check elite unlock
        elite_unlocked, elite_status = self.check_elite_unlock(target_date)
        if elite_unlocked and elite_status:
            self.log(f"Elite unlock triggered: {elite_status}")
            # If performance qualifies and elite is unlocked, use it
            if STATUS_HIERARCHY.index(elite_status) >= STATUS_HIERARCHY.index(base_status):
                base_status = elite_status
        
        new_status = current_status
        reason = "No change"
        changed = False
        
        # 6. Check promotion eligibility
        current_idx = STATUS_HIERARCHY.index(current_status)
        base_idx = STATUS_HIERARCHY.index(base_status)
        
        if base_idx > current_idx:
            # Performance qualifies for promotion
            if current_status == 'squad_member' and base_status in ['first_team', 'invincible', 'legend']:
                # Special case: need 3 consecutive days >= 90%
                consecutive_good = 0
                conn = sqlite3.connect(self.db_path)
                end_date = datetime.strptime(target_date, '%Y-%m-%d')
                
                for i in range(3):
                    check_date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
                    query = "SELECT rpi FROM daily_stats WHERE date = ?"
                    cursor = conn.execute(query, (check_date,))
                    row = cursor.fetchone()
                    
                    if row and row[0] and float(row[0]) >= 0.90:
                        consecutive_good += 1
                    else:
                        break
                
                conn.close()
                
                if consecutive_good >= 3:
                    new_status = base_status
                    reason = f"Promoted from probation: 3 consecutive days >= 90%"
                    changed = True
                    self.log(f"Promotion from squad_member: {consecutive_good} consecutive days >= 90%")
            else:
                # Immediate promotion
                new_status = base_status
                reason = f"Promoted: top5_avg {top5_avg:.3f} qualifies for {new_status}"
                changed = True
                self.log(f"Immediate promotion to {new_status}")
        
        elif base_idx < current_idx:
            # Performance below current tier - check demotion eligibility
            if probation_remaining > 0:
                # Immune during probation
                reason = f"Performance below tier but protected by probation ({probation_remaining} days left)"
                self.log("Demotion blocked: probation immunity")
            else:
                # Check consecutive poor days
                if current_status == 'first_team':
                    threshold = 1.00
                    required_days = 3
                elif current_status == 'squad_member':
                    threshold = 0.90
                    required_days = 5
                elif current_status == 'reserves':
                    threshold = 0.70
                    required_days = 3
                elif current_status in ['invincible', 'legend']:
                    threshold = THRESHOLDS[current_status][0]
                    required_days = 5
                else:
                    threshold = 0.70
                    required_days = 3
                
                consecutive_poor = self.count_consecutive_poor_days(target_date, threshold)
                
                if consecutive_poor >= required_days:
                    new_status = base_status
                    reason = f"Demoted: {consecutive_poor} consecutive days below threshold"
                    changed = True
                    self.log(f"Demotion to {new_status}: {consecutive_poor} consecutive poor days")
                else:
                    reason = f"Performance below tier but need {required_days} consecutive poor days (current: {consecutive_poor})"
                    self.log(f"Demotion not triggered: {consecutive_poor}/{required_days} poor days")
        
        # 7. Update counters
        if changed:
            days_in_status = 1
            # Set probation if promoted TO squad_member
            if new_status == 'squad_member' and current_status != 'squad_member':
                probation_remaining = 7
                reason += " [Probation: 7 days]"
            else:
                probation_remaining = 0
        else:
            days_in_status += 1
            probation_remaining = max(0, probation_remaining - 1)
        
        # 8. Calculate consecutive poor days (for UI/email display)
        consecutive_poor_days = self.count_consecutive_poor_days(target_date, 0.90)
        
        return {
            'date': target_date,
            'status': new_status,
            'days_in_status': days_in_status,
            'previous_status': current_status if changed else None,
            'top5_avg': top5_avg,
            'grace_days_used': grace_days_used,
            'consecutive_poor_days': consecutive_poor_days,
            'probation_days_remaining': probation_remaining,
            'reason': reason,
            'changed': changed
        }


def main():
    parser = argparse.ArgumentParser(
        description='Calculate team status based on recent productivity (RPI)'
    )
    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help='Target date (YYYY-MM-DD format)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='/home/workspace/productivity_tracker.db',
        help='Path to productivity database'
    )
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
    
    calculator = TeamStatusCalculator(args.db)
    calculator.verbose = args.verbose
    
    result = calculator.calculate_status(args.date)
    
    # Pretty print result
    print(f"\n{'='*60}")
    print(f"TEAM STATUS CALCULATION: {result['date']}")
    print(f"{'='*60}")
    print(f"Status: {result['status'].upper()}")
    if result['changed']:
        print(f"Previous: {result['previous_status']}")
        print(f"⚡ STATUS CHANGE DETECTED")
    print(f"Days in status: {result['days_in_status']}")
    print(f"Top 5/7 avg: {result['top5_avg']:.3f}")
    print(f"Grace days used: {result['grace_days_used']}")
    print(f"Consecutive poor days: {result['consecutive_poor_days']}")
    if result['probation_days_remaining'] > 0:
        print(f"Probation remaining: {result['probation_days_remaining']} days")
    print(f"\nReason: {result['reason']}")
    print(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

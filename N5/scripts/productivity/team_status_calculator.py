#!/usr/bin/env python3
"""
Team Status Calculator - W2

Calculates daily team status from RPI performance using:
- Top 5 of 7 average (grace system)
- 6-tier system with asymmetric promotion/demotion
- Probation immunity for squad_member
- Elite unlock gates (2-in-7-days pattern)

Author: N5 System (W2)
Date: 2025-10-30
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

# Status tier thresholds (top5_avg percentage)
THRESHOLDS = {
    'transfer_list': (0.0, 0.69),
    'reserves': (0.70, 0.89),
    'squad_member': (0.90, 0.99),
    'first_team': (1.00, 1.24),
    'invincible': (1.25, 1.49),
    'legend': (1.50, float('inf'))
}

# Tier ordering for promotion/demotion
TIER_ORDER = ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend']

# Demotion requirements (consecutive poor days)
DEMOTION_REQUIREMENTS = {
    'first_team': 3,      # 3 days <90%
    'squad_member': 5,    # 5 days <90% (but probation blocks)
    'reserves': 3,        # 3 days <70%
    'invincible': 5,      # 5 days <125%
    'legend': 5           # 5 days <150%
}


class TeamStatusCalculator:
    def __init__(self, db_path: str = "/home/workspace/productivity_tracker.db"):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with Row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def fetch_last_7_days_rpi(self, target_date: str) -> List[float]:
        """
        Fetch RPI for 7 days ending on target_date.
        
        Args:
            target_date: ISO format date string (YYYY-MM-DD)
            
        Returns:
            List of RPI values in decimal format (1.80 not 180), treating NULL as 0.0
        """
        conn = self._get_connection()
        try:
            end_date = datetime.strptime(target_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=6)
            
            query = """
                SELECT date, COALESCE(rpi, 0.0) as rpi 
                FROM daily_stats 
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC
            """
            
            cursor = conn.execute(query, (start_date.strftime('%Y-%m-%d'), target_date))
            rows = cursor.fetchall()
            
            # Convert from percentage (180.0) to decimal (1.80)
            return [row['rpi'] / 100.0 for row in rows]
            
        finally:
            conn.close()
    
    def calculate_top5_avg(self, rpi_values: List[float]) -> Tuple[float, int]:
        """
        Calculate average of top 5 values from last 7 days.
        
        Args:
            rpi_values: List of RPI values (may be <7 for edge cases)
            
        Returns:
            (average, grace_days_used)
        """
        if not rpi_values:
            return (0.0, 7)
        
        if len(rpi_values) < 7:
            # Edge case: use all available data
            grace_days_used = 7 - len(rpi_values)
            avg = sum(rpi_values) / len(rpi_values)
            return (avg, grace_days_used)
        
        # Standard case: top 5 of 7
        sorted_vals = sorted(rpi_values, reverse=True)
        top5 = sorted_vals[:5]
        avg = sum(top5) / 5
        grace_days_used = 2
        
        return (avg, grace_days_used)
    
    def determine_base_status(self, top5_avg: float) -> str:
        """
        Map top5_avg to status tier based on thresholds.
        Does NOT consider elite unlock gates.
        
        Args:
            top5_avg: Performance average (0.0-2.0+ range)
            
        Returns:
            Status tier string
        """
        for status, (min_val, max_val) in THRESHOLDS.items():
            if min_val <= top5_avg <= max_val:
                return status
        
        # Fallback (shouldn't reach here)
        return 'transfer_list'
    
    def get_current_status_data(self, target_date: str) -> Optional[Dict]:
        """
        Fetch most recent status before target_date.
        
        Args:
            target_date: ISO format date string
            
        Returns:
            Dict with current status data, or None if first day
        """
        conn = self._get_connection()
        try:
            query = """
                SELECT * FROM team_status_history 
                WHERE date < ?
                ORDER BY date DESC 
                LIMIT 1
            """
            
            cursor = conn.execute(query, (target_date,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        finally:
            conn.close()
    
    def check_elite_unlocked(self, status_to_check: str) -> bool:
        """
        Check if elite status has ever been unlocked.
        Once unlocked, can freely move between tiers.
        
        Args:
            status_to_check: 'invincible' or 'legend'
            
        Returns:
            True if ever achieved this status before
        """
        conn = self._get_connection()
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM team_status_history 
                WHERE status = ?
            """
            
            cursor = conn.execute(query, (status_to_check,))
            row = cursor.fetchone()
            
            return row['count'] > 0
            
        finally:
            conn.close()
    
    def check_elite_unlock_pattern(self, target_date: str, threshold: float) -> bool:
        """
        Check if 2-in-7-days pattern exists for elite unlock.
        
        Args:
            target_date: Check 7 days ending on this date
            threshold: RPI threshold in decimal (1.25 for invincible, 1.50 for legend)
            
        Returns:
            True if 2+ days meet threshold within window
        """
        conn = self._get_connection()
        try:
            end_date = datetime.strptime(target_date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=6)
            
            # Convert threshold to percentage for comparison (1.25 → 125.0)
            threshold_pct = threshold * 100.0
            
            query = """
                SELECT COUNT(*) as count 
                FROM daily_stats 
                WHERE date >= ? AND date <= ? AND rpi >= ?
            """
            
            cursor = conn.execute(query, (
                start_date.strftime('%Y-%m-%d'), 
                target_date, 
                threshold_pct
            ))
            row = cursor.fetchone()
            
            return row['count'] >= 2
            
        finally:
            conn.close()
    
    def check_promotion_eligible(
        self,
        current_status: str,
        base_status: str,
        top5_avg: float,
        days_in_status: int,
        target_date: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Check if promotion should occur.
        
        Args:
            current_status: Current tier
            base_status: Tier based on threshold
            top5_avg: Performance average
            days_in_status: How long at current tier
            target_date: Date being calculated
            
        Returns:
            (should_promote, new_status, reason)
        """
        current_idx = TIER_ORDER.index(current_status)
        base_idx = TIER_ORDER.index(base_status)
        
        # No promotion if base status not higher
        if base_idx <= current_idx:
            return (False, None, "")
        
        # Can jump multiple tiers if performance warrants it
        # But check tier-by-tier for special rules (probation, elite unlock)
        target_status = TIER_ORDER[current_idx + 1]
        
        # Special case: squad_member → first_team (3 consecutive days ≥90%)
        if current_status == 'squad_member' and base_idx >= TIER_ORDER.index('first_team'):
            # Check if THIS will be the 3rd day (days_in_status is from yesterday)
            if days_in_status >= 2 and top5_avg >= 0.90:
                # After first_team, check if we can go further
                if base_idx > TIER_ORDER.index('first_team'):
                    target_status = base_status  # Jump to actual performance level
                else:
                    target_status = 'first_team'
                return (True, target_status, f"Promoted: 3 consecutive days ≥90% (probation complete) to {target_status}")
            else:
                return (False, None, "")
        
        # Elite unlock gates
        if target_status == 'invincible':
            if not self.check_elite_unlocked('invincible'):
                # Need 2-in-7 pattern at ≥125%
                if self.check_elite_unlock_pattern(target_date, 1.25):
                    return (True, 'invincible', "Promoted: Invincible unlocked (2 days ≥125% in 7-day window)")
                else:
                    return (False, None, "")
            else:
                # Already unlocked, immediate promotion
                return (True, 'invincible', f"Promoted: Performance meets invincible tier ({top5_avg:.2f})")
        
        if target_status == 'legend':
            # Must have invincible unlocked first
            if not self.check_elite_unlocked('invincible'):
                return (False, None, "")
            
            if not self.check_elite_unlocked('legend'):
                # Need 2-in-7 pattern at ≥150%
                if self.check_elite_unlock_pattern(target_date, 1.50):
                    return (True, 'legend', "Promoted: Legend unlocked (2 days ≥150% in 7-day window)")
                else:
                    return (False, None, "")
            else:
                # Already unlocked, immediate promotion
                return (True, 'legend', f"Promoted: Performance meets legend tier ({top5_avg:.2f})")
        
        # Default: immediate promotion (1 day at threshold)
        return (True, target_status, f"Promoted: Performance meets {target_status} tier ({top5_avg:.2f})")
    
    def check_demotion_eligible(
        self,
        current_status: str,
        top5_avg: float,
        consecutive_poor_days: int,
        probation_remaining: int
    ) -> Tuple[bool, Optional[str], str]:
        """
        Check if demotion should occur.
        
        Args:
            current_status: Current tier
            top5_avg: Performance average
            consecutive_poor_days: Days below threshold in a row
            probation_remaining: Probation immunity days left
            
        Returns:
            (should_demote, new_status, reason)
        """
        # Probation immunity
        if probation_remaining > 0:
            return (False, None, "")
        
        # No demotion rule for transfer_list (bottom tier)
        if current_status == 'transfer_list':
            return (False, None, "")
        
        # Get demotion threshold for current tier
        current_idx = TIER_ORDER.index(current_status)
        
        # Determine what "poor" means for this tier
        if current_status == 'first_team' or current_status == 'squad_member':
            poor_threshold = 0.90
        elif current_status == 'reserves':
            poor_threshold = 0.70
        elif current_status == 'invincible':
            poor_threshold = 1.25
        elif current_status == 'legend':
            poor_threshold = 1.50
        else:
            return (False, None, "")
        
        # Check if currently poor
        is_poor_today = top5_avg < poor_threshold
        
        # Get required consecutive days
        required_days = DEMOTION_REQUIREMENTS.get(current_status, 999)
        
        # Check if demotion threshold met
        if consecutive_poor_days >= required_days:
            target_status = TIER_ORDER[current_idx - 1]
            return (
                True, 
                target_status, 
                f"Demoted: {consecutive_poor_days} consecutive days below {poor_threshold:.0%} threshold"
            )
        
        return (False, None, "")
    
    def calculate_status(self, target_date: str) -> Dict:
        """
        Main entry point. Calculate status for target_date.
        
        Args:
            target_date: ISO format date string (YYYY-MM-DD)
            
        Returns:
            Dict with status calculation results
        """
        # 1. Fetch last 7 days RPI
        rpi_values = self.fetch_last_7_days_rpi(target_date)
        
        # 2. Calculate top5_avg
        top5_avg, grace_days_used = self.calculate_top5_avg(rpi_values)
        
        # 3. Get current status
        current_data = self.get_current_status_data(target_date)
        
        # First day ever: start at first_team
        if current_data is None:
            return {
                'date': target_date,
                'status': 'first_team',
                'days_in_status': 1,
                'previous_status': None,
                'top5_avg': top5_avg,
                'grace_days_used': grace_days_used,
                'consecutive_poor_days': 0,
                'probation_days_remaining': 0,
                'reason': 'Initial status: Starting as first team member',
                'changed': True
            }
        
        # Extract current state
        current_status = current_data['status']
        days_in_status = current_data['days_in_status']
        consecutive_poor_days = current_data['consecutive_poor_days']
        probation_remaining = current_data['probation_days_remaining']
        
        # 4. Determine base status from threshold
        base_status = self.determine_base_status(top5_avg)
        
        # 4.5. Calculate if today is a poor day (for consecutive tracking)
        if current_status in ['first_team', 'squad_member']:
            poor_threshold = 0.90
        elif current_status == 'reserves':
            poor_threshold = 0.70
        elif current_status == 'invincible':
            poor_threshold = 1.25
        elif current_status == 'legend':
            poor_threshold = 1.50
        else:
            poor_threshold = 0.0
        
        is_poor_today = top5_avg < poor_threshold
        
        # Calculate current consecutive poor days (including today if poor)
        if is_poor_today:
            current_consecutive_poor = consecutive_poor_days + 1
        else:
            current_consecutive_poor = consecutive_poor_days
        
        # 5. Check promotion
        should_promote, promotion_target, promotion_reason = self.check_promotion_eligible(
            current_status,
            base_status,
            top5_avg,
            days_in_status,
            target_date
        )
        
        # 6. Check demotion (only if not promoting)
        should_demote = False
        demotion_target = None
        demotion_reason = ""
        
        if not should_promote:
            should_demote, demotion_target, demotion_reason = self.check_demotion_eligible(
                current_status,
                top5_avg,
                current_consecutive_poor,  # Use updated count including today
                probation_remaining
            )
        
        # 7. Apply movement
        changed = False
        new_status = current_status
        reason = f"Maintained {current_status} status (top5_avg: {top5_avg:.2f})"
        
        if should_promote:
            new_status = promotion_target
            reason = promotion_reason
            changed = True
        elif should_demote:
            new_status = demotion_target
            reason = demotion_reason
            changed = True
        
        # 8. Update counters
        if changed:
            new_days_in_status = 1
            new_consecutive_poor = 0  # Reset on status change
        else:
            new_days_in_status = days_in_status + 1
            
            # Update consecutive poor days
            if current_status in ['first_team', 'squad_member']:
                poor_threshold = 0.90
            elif current_status == 'reserves':
                poor_threshold = 0.70
            elif current_status == 'invincible':
                poor_threshold = 1.25
            elif current_status == 'legend':
                poor_threshold = 1.50
            else:
                poor_threshold = 0.0
            
            if top5_avg < poor_threshold:
                new_consecutive_poor = consecutive_poor_days + 1
            else:
                new_consecutive_poor = 0  # Reset counter
        
        # Handle probation
        if new_status == 'squad_member' and changed:
            # Probation only when PROMOTED to squad_member (from reserves/transfer_list)
            # Not when DEMOTED to squad_member (from first_team)
            if current_status in ['reserves', 'transfer_list']:
                new_probation = 7
            else:
                new_probation = 0
        elif new_status == 'squad_member' and not changed:
            # Already in squad_member: decrement probation
            new_probation = max(0, probation_remaining - 1)
        else:
            # Not in squad_member: no probation
            new_probation = 0
        
        # 9. Return structured data
        return {
            'date': target_date,
            'status': new_status,
            'days_in_status': new_days_in_status,
            'previous_status': current_status if changed else current_data.get('previous_status'),
            'top5_avg': top5_avg,
            'grace_days_used': grace_days_used,
            'consecutive_poor_days': new_consecutive_poor,
            'probation_days_remaining': new_probation,
            'reason': reason,
            'changed': changed
        }


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 team_status_calculator.py YYYY-MM-DD")
        sys.exit(1)
    
    target_date = sys.argv[1]
    
    calculator = TeamStatusCalculator()
    result = calculator.calculate_status(target_date)
    
    print(f"\nStatus Calculation for {target_date}")
    print("=" * 50)
    print(f"Status: {result['status']}")
    print(f"Changed: {'✓ YES' if result['changed'] else '✗ No'}")
    print(f"Days in Status: {result['days_in_status']}")
    print(f"Top 5 Avg: {result['top5_avg']:.2f} ({result['top5_avg']*100:.1f}%)")
    print(f"Grace Days Used: {result['grace_days_used']}")
    print(f"Consecutive Poor Days: {result['consecutive_poor_days']}")
    print(f"Probation Remaining: {result['probation_days_remaining']}")
    print(f"Reason: {result['reason']}")
    print()


if __name__ == "__main__":
    main()

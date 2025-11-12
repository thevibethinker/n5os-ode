#!/usr/bin/env python3
"""
RPI (Responsive Productivity Index) Calculator
Deterministic calculation with no LLM involvement.

Formula:
- Weekdays: expected = (free_hours × 2.5) + 5, where free_hours = 8 - meeting_hours
- Weekends: expected = 5 (fixed)
- RPI = (actual_emails / expected_emails) × 100
"""

from datetime import datetime
from typing import Tuple
import sys


class RPICalculator:
    """Deterministic RPI calculator."""
    
    # Configuration constants
    TOTAL_WORK_HOURS = 8.0
    EMAIL_RATE_PER_FREE_HOUR = 2.5
    WEEKDAY_BASE_EXPECTATION = 5.0
    WEEKEND_EXPECTATION = 5.0
    
    @staticmethod
    def is_weekend(date_str: str) -> bool:
        """
        Check if date is Saturday (5) or Sunday (6).
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            True if weekend, False if weekday
        """
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.weekday() in (5, 6)
    
    @staticmethod
    def calculate_expected_emails(date_str: str, meeting_hours: float) -> float:
        """
        Calculate expected emails for a given day.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            meeting_hours: Hours spent in meetings
            
        Returns:
            Expected number of emails
        """
        if RPICalculator.is_weekend(date_str):
            # Weekend: fixed expectation
            return RPICalculator.WEEKEND_EXPECTATION
        else:
            # Weekday: dynamic based on free time
            free_hours = RPICalculator.TOTAL_WORK_HOURS - meeting_hours
            free_hours = max(0, free_hours)  # Can't be negative
            
            expected = (free_hours * RPICalculator.EMAIL_RATE_PER_FREE_HOUR) + \
                       RPICalculator.WEEKDAY_BASE_EXPECTATION
            return expected
    
    @staticmethod
    def calculate_rpi(actual_emails: int, expected_emails: float) -> float:
        """
        Calculate RPI score.
        
        Args:
            actual_emails: Number of emails actually sent
            expected_emails: Number of emails expected
            
        Returns:
            RPI score (percentage)
        """
        if expected_emails == 0:
            return 0.0
        
        rpi = (actual_emails / expected_emails) * 100.0
        return round(rpi, 1)
    
    @staticmethod
    def calculate(date_str: str, actual_emails: int, meeting_hours: float) -> Tuple[float, float]:
        """
        Calculate RPI for a given day.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            actual_emails: Number of emails actually sent
            meeting_hours: Hours spent in meetings
            
        Returns:
            Tuple of (expected_emails, rpi_score)
        """
        expected = RPICalculator.calculate_expected_emails(date_str, meeting_hours)
        rpi = RPICalculator.calculate_rpi(actual_emails, expected)
        
        return expected, rpi


def main():
    """CLI interface for RPI calculation."""
    if len(sys.argv) != 4:
        print("Usage: calculate_rpi.py <date> <actual_emails> <meeting_hours>")
        print("Example: calculate_rpi.py 2025-11-05 15 3.5")
        sys.exit(1)
    
    date_str = sys.argv[1]
    actual_emails = int(sys.argv[2])
    meeting_hours = float(sys.argv[3])
    
    expected, rpi = RPICalculator.calculate(date_str, actual_emails, meeting_hours)
    
    day_type = "Weekend" if RPICalculator.is_weekend(date_str) else "Weekday"
    
    print(f"Date: {date_str} ({day_type})")
    print(f"Actual Emails: {actual_emails}")
    print(f"Meeting Hours: {meeting_hours}")
    print(f"Expected Emails: {expected:.1f}")
    print(f"RPI: {rpi:.1f}")


if __name__ == "__main__":
    main()

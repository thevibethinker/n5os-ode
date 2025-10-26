#!/usr/bin/env python3
"""
Arsenal XP System - Gamification Engine
Calculates XP, levels, ranks, achievements from email activity

Principles Applied:
- P2 (SSOT): Database is single source; XP derived from email data
- P7 (Dry-Run): --dry-run flag for safe testing
- P18 (Verify State): Database queries verify XP calculations
- P19 (Error Handling): Try/except around DB operations
- P21 (Document Assumptions): Formulas and thresholds documented
- P22 (Language Selection): Python for data processing + SQLite
"""

import argparse
import json
import logging
import math
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

# === XP VALUES ===

EMAIL_XP = {
    'new': 10,         # Initiating new thread
    'follow_up': 8,    # Follow-up in existing thread
    'response': 5      # Reply to incoming
}

SPEED_BONUS = 5  # Applied if response_time_hours < 24

DAILY_BONUSES = {
    'clean_sheet': {
        'xp': 50,
        'condition': lambda stats: stats.get('rpi') is not None and stats.get('rpi', 0) >= 100,
        'description': 'RPI ≥100% (Arsenal Clean Sheet)'
    },
    'hat_trick': {
        'xp': 20,
        'condition': lambda stats: stats.get('emails_new', 0) >= 3,
        'description': '3+ New Emails (Hat Trick)'
    },
    'goal_rush': {
        'xp': 50,
        'condition': lambda stats: stats.get('emails_new', 0) >= 5,
        'description': '5+ New Emails (Goal Rush)'
    }
}

# === RPI MULTIPLIERS ===

RPI_MULTIPLIERS = [
    (150, 1.5, "Invincible Form 🔥"),
    (125, 1.25, "Top Performance ⭐"),
    (100, 1.0, "Meeting Expectations ✅"),
    (75, 0.9, "Catch Up Needed ⚠️"),
    (0, 0.75, "Behind Schedule 🔻")
]

# === ARSENAL RANKS ===

ARSENAL_RANKS = [
    (1, 4, "Youth Academy ⚽", "Just getting started"),
    (5, 9, "Reserve Team 🎯", "Showing promise"),
    (10, 14, "First Team Squad 🔴", "Regular contributor"),
    (15, 19, "Regular Starter ⭐", "Key player"),
    (20, 24, "Club Captain 👑", "Leadership role"),
    (25, 999, "Arsenal Legend 🏆", "Hall of Fame")
]

# === ACHIEVEMENTS ===

ACHIEVEMENTS = [
    # Level Milestones
    ('level_5', 'Reserve Team', 'Reach Level 5', 50),
    ('level_10', 'First Team Squad', 'Reach Level 10', 100),
    ('level_15', 'Regular Starter', 'Reach Level 15', 150),
    ('level_20', 'Club Captain', 'Reach Level 20', 200),
    ('level_25', 'Arsenal Legend', 'Reach Level 25', 500),
    
    # Streak Achievements
    ('streak_3', '3-Day Streak', 'Email 3 days in a row', 20),
    ('streak_7', 'Week Warrior', 'Email 7 days in a row', 50),
    ('streak_30', 'Month Marathon', 'Email 30 days in a row', 200),
    
    # Output Achievements
    ('emails_100', 'Centurion', 'Send 100 emails', 100),
    ('emails_500', 'Goal Machine', 'Send 500 emails', 250),
    ('emails_1000', 'Legendary Striker', 'Send 1000 emails', 500),
    
    # Performance Achievements
    ('clean_sheet_10', '10 Clean Sheets', 'RPI ≥100% for 10 days', 100),
    ('invincible', 'Invincible', 'RPI ≥150% for 7 days straight', 300),
    ('hat_trick_artist', 'Hat Trick Artist', '5+ new emails in a day 10 times', 150)
]


# === CORE FUNCTIONS ===

def calculate_email_xp(email_type: str, response_time_hours: float = None) -> dict:
    """
    Calculate XP for single email with breakdown.
    
    Args:
        email_type: 'new', 'follow_up', or 'response'
        response_time_hours: Time to respond (for speed bonus)
    
    Returns:
        {
            'base_xp': 10,
            'speed_bonus': 5,  # If response <24h
            'total_xp': 15,
            'description': 'New email + Speed Bonus'
        }
    """
    base_xp = EMAIL_XP.get(email_type, 0)
    speed_bonus = 0
    
    if response_time_hours is not None and response_time_hours < 24:
        speed_bonus = SPEED_BONUS
    
    total_xp = base_xp + speed_bonus
    
    desc = email_type.replace('_', ' ').title()
    if speed_bonus > 0:
        desc += " + Speed Bonus"
    
    return {
        'base_xp': base_xp,
        'speed_bonus': speed_bonus,
        'total_xp': total_xp,
        'description': desc
    }


def calculate_daily_bonuses(date: str, stats: dict) -> list:
    """
    Calculate bonus XP for the day.
    
    Args:
        date: YYYY-MM-DD format
        stats:
            - emails_sent: int
            - emails_new: int
            - rpi: float (from RPI calculator, may be None)
            - streak_days: int
    
    Returns list of bonus transactions:
        [
            {'type': 'clean_sheet', 'xp': 50, 'description': 'RPI ≥100%'},
            {'type': 'hat_trick', 'xp': 20, 'description': '3+ new emails'},
            {'type': 'streak', 'xp': 30, 'description': '3-day streak'}
        ]
    """
    bonuses = []
    
    # Check daily bonuses
    for bonus_type, bonus_config in DAILY_BONUSES.items():
        if bonus_config['condition'](stats):
            bonuses.append({
                'type': bonus_type,
                'xp': bonus_config['xp'],
                'description': bonus_config['description']
            })
    
    # Streak bonus
    streak_days = stats.get('streak_days', 0)
    if streak_days >= 3:
        streak_xp = calculate_streak_xp(streak_days)
        bonuses.append({
            'type': 'streak',
            'xp': streak_xp,
            'description': f'{streak_days}-day streak'
        })
    
    return bonuses


def calculate_streak_xp(streak_days: int) -> int:
    """10 XP per day in streak, capped at 100 XP"""
    return min(streak_days * 10, 100)


def get_rpi_multiplier(rpi: float) -> tuple:
    """
    Get RPI-based multiplier.
    
    Returns: (multiplier, tier_name)
    """
    if rpi is None:
        return (1.0, "No RPI Data")
    
    for threshold, mult, tier in RPI_MULTIPLIERS:
        if rpi >= threshold:
            return (mult, tier)
    
    return (0.75, "Behind Schedule 🔻")


def apply_rpi_multiplier(base_xp: int, rpi: float) -> dict:
    """
    Apply RPI-based multiplier to XP.
    
    Returns:
        {
            'base_xp': 100,
            'multiplier': 1.25,
            'bonus_xp': 25,
            'final_xp': 125,
            'tier': 'Top Performance'
        }
    """
    multiplier, tier = get_rpi_multiplier(rpi)
    bonus_xp = int(base_xp * (multiplier - 1))
    final_xp = base_xp + bonus_xp
    
    return {
        'base_xp': base_xp,
        'multiplier': multiplier,
        'bonus_xp': bonus_xp,
        'final_xp': final_xp,
        'tier': tier
    }


def calculate_level(total_xp: int) -> int:
    """level = floor(sqrt(total_xp / 100))"""
    return math.floor(math.sqrt(total_xp / 100))


def xp_for_level(level: int) -> int:
    """XP required to reach this level"""
    return level * level * 100


def calculate_level_and_rank(total_xp: int) -> dict:
    """
    Calculate current level and Arsenal rank.
    
    Formula: level = floor(sqrt(total_xp / 100))
    
    Returns:
        {
            'level': 12,
            'rank': 'First Team Squad',
            'xp_current': 14400,
            'xp_next_level': 16900,
            'xp_to_next': 2500,
            'progress_pct': 85.2
        }
    """
    current_level = calculate_level(total_xp)
    next_level = current_level + 1
    
    xp_current_level = xp_for_level(current_level)
    xp_next_level = xp_for_level(next_level)
    
    xp_needed = xp_next_level - total_xp
    xp_progress = total_xp - xp_current_level
    xp_total_for_level = xp_next_level - xp_current_level
    
    progress_pct = (xp_progress / xp_total_for_level) * 100 if xp_total_for_level > 0 else 0
    
    # Get rank
    rank_info = get_rank(current_level)
    
    return {
        'level': current_level,
        'rank': rank_info['title'],
        'rank_desc': rank_info['description'],
        'xp_current': total_xp,
        'xp_next_level': xp_next_level,
        'xp_to_next': xp_needed,
        'progress_pct': round(progress_pct, 1)
    }


def get_rank(level: int) -> dict:
    """Get Arsenal rank for level"""
    for min_lvl, max_lvl, title, desc in ARSENAL_RANKS:
        if min_lvl <= level <= max_lvl:
            return {
                'title': title,
                'description': desc,
                'level_range': (min_lvl, max_lvl)
            }
    return {
        'title': 'Youth Academy ⚽',
        'description': 'Just getting started',
        'level_range': (1, 4)
    }


def populate_daily_stats_from_emails(conn, dry_run: bool = False):
    """
    Populate daily_stats table from sent_emails data.
    This is a temporary helper until Worker 3 (Email Activity Tracker) is built.
    """
    try:
        cursor = conn.cursor()
        
        # Get all unique dates from sent_emails
        cursor.execute("SELECT DISTINCT date FROM sent_emails ORDER BY date")
        dates = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Populating daily_stats for {len(dates)} dates...")
        
        for date in dates:
            # Count email types - for now, treat all as 'new' since we don't have thread tracking
            cursor.execute("""
                SELECT COUNT(*) FROM sent_emails WHERE date = ?
            """, (date,))
            emails_sent = cursor.fetchone()[0]
            
            if not dry_run:
                # Insert or update daily_stats
                cursor.execute("""
                    INSERT INTO daily_stats 
                    (date, emails_sent, emails_new, emails_followup, emails_response, rpi)
                    VALUES (?, ?, ?, 0, 0, NULL)
                    ON CONFLICT(date) DO UPDATE SET
                        emails_sent = excluded.emails_sent,
                        emails_new = excluded.emails_new
                """, (date, emails_sent, emails_sent))
            else:
                logger.info(f"[DRY RUN] Would set {date}: {emails_sent} emails")
        
        if not dry_run:
            conn.commit()
            logger.info("✓ Daily stats populated")
        
    except Exception as e:
        logger.error(f"Error populating daily_stats: {e}", exc_info=True)
        raise


def calculate_streak(conn, date: str) -> int:
    """
    Calculate consecutive days with emails sent up to this date.
    
    Returns: Number of consecutive days including current date
    """
    try:
        cursor = conn.cursor()
        
        # Get all dates with emails sent before and including this date
        cursor.execute("""
            SELECT date FROM daily_stats 
            WHERE emails_sent > 0 AND date <= ? 
            ORDER BY date DESC
        """, (date,))
        
        dates = [row[0] for row in cursor.fetchall()]
        
        if not dates:
            return 0
        
        # Count consecutive days from most recent
        streak = 1
        current_date = datetime.strptime(dates[0], "%Y-%m-%d")
        
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i], "%Y-%m-%d")
            diff = (current_date - prev_date).days
            
            if diff == 1:
                streak += 1
                current_date = prev_date
            else:
                break
        
        return streak
        
    except Exception as e:
        logger.error(f"Error calculating streak: {e}")
        return 0


def seed_achievements(conn, dry_run: bool = False):
    """Seed achievement definitions into database"""
    if dry_run:
        logger.info("[DRY RUN] Would seed achievements")
        return
    
    try:
        cursor = conn.cursor()
        
        for name, title, desc, xp in ACHIEVEMENTS:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements 
                (achievement_name, achievement_type, description, xp_reward)
                VALUES (?, 'milestone', ?, ?)
            """, (name, desc, xp))
        
        conn.commit()
        logger.info(f"✓ Seeded {len(ACHIEVEMENTS)} achievement definitions")
        
    except Exception as e:
        logger.error(f"Error seeding achievements: {e}")
        raise


def check_and_unlock_achievements(conn, total_emails: int, total_xp: int, 
                                   current_level: int, streak_days: int,
                                   clean_sheets: int, invincible_streak: int,
                                   hat_trick_days: int, dry_run: bool = False) -> list:
    """
    Check for newly unlocked achievements and update database.
    
    Returns list of newly unlocked achievements:
        [
            {'name': 'level_10', 'title': 'First Team Squad', 'xp': 100},
            {'name': 'week_streak', 'title': '7-Day Streak', 'xp': 50}
        ]
    """
    newly_unlocked = []
    
    try:
        cursor = conn.cursor()
        
        # Define achievement checks
        checks = [
            # Level milestones
            ('level_5', current_level >= 5),
            ('level_10', current_level >= 10),
            ('level_15', current_level >= 15),
            ('level_20', current_level >= 20),
            ('level_25', current_level >= 25),
            
            # Streak achievements
            ('streak_3', streak_days >= 3),
            ('streak_7', streak_days >= 7),
            ('streak_30', streak_days >= 30),
            
            # Output achievements
            ('emails_100', total_emails >= 100),
            ('emails_500', total_emails >= 500),
            ('emails_1000', total_emails >= 1000),
            
            # Performance achievements
            ('clean_sheet_10', clean_sheets >= 10),
            ('invincible', invincible_streak >= 7),
            ('hat_trick_artist', hat_trick_days >= 10)
        ]
        
        for achievement_name, condition in checks:
            if condition:
                # Check if already unlocked
                cursor.execute("""
                    SELECT unlocked_at, achievement_type, xp_reward 
                    FROM achievements 
                    WHERE achievement_name = ?
                """, (achievement_name,))
                
                result = cursor.fetchone()
                
                if result and result[0] is None:
                    # Not yet unlocked - unlock it
                    if not dry_run:
                        cursor.execute("""
                            UPDATE achievements 
                            SET unlocked_at = CURRENT_TIMESTAMP
                            WHERE achievement_name = ?
                        """, (achievement_name,))
                        
                        # Get achievement details for return
                        cursor.execute("""
                            SELECT achievement_name, achievement_type, xp_reward, description
                            FROM achievements 
                            WHERE achievement_name = ?
                        """, (achievement_name,))
                        
                        ach = cursor.fetchone()
                        newly_unlocked.append({
                            'name': ach[0],
                            'title': ach[1],
                            'xp': ach[2],
                            'description': ach[3]
                        })
                    else:
                        logger.info(f"[DRY RUN] Would unlock: {achievement_name}")
        
        if not dry_run and newly_unlocked:
            conn.commit()
        
        return newly_unlocked
        
    except Exception as e:
        logger.error(f"Error checking achievements: {e}", exc_info=True)
        return []


def recalculate_all_xp(start_date: str = None, dry_run: bool = False) -> dict:
    """
    Recalculate XP for all historical data from sent_emails table.
    
    Process:
    1. Clear xp_ledger and reset daily_stats XP columns
    2. Iterate through sent_emails by date
    3. Calculate base XP + bonuses
    4. Apply RPI multipliers (if available)
    5. Update xp_ledger with transactions
    6. Update daily_stats with aggregated XP
    7. Check achievements
    
    Returns summary stats.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Seed achievements first
        seed_achievements(conn, dry_run=dry_run)
        
        # Populate daily_stats if empty (Worker 3 not yet built)
        cursor.execute("SELECT COUNT(*) FROM daily_stats")
        if cursor.fetchone()[0] == 0:
            logger.info("Daily stats empty - populating from sent_emails...")
            populate_daily_stats_from_emails(conn, dry_run=dry_run)
        
        # Clear existing XP data
        if not dry_run:
            logger.info("Clearing existing XP data...")
            cursor.execute("DELETE FROM xp_ledger")
            cursor.execute("""
                UPDATE daily_stats 
                SET xp_earned = 0, xp_multiplier = 1.0
            """)
            # Note: Not clearing xp_cumulative field - will recalculate
            conn.commit()
        else:
            logger.info("[DRY RUN] Would clear xp_ledger and reset daily_stats XP")
        
        # Get all dates with emails
        cursor.execute("""
            SELECT DISTINCT date 
            FROM sent_emails 
            WHERE date >= COALESCE(?, '1900-01-01')
            ORDER BY date
        """, (start_date,))
        
        dates = [row[0] for row in cursor.fetchall()]
        logger.info(f"Processing {len(dates)} dates...")
        
        cumulative_xp = 0
        total_emails = 0
        clean_sheets = 0
        invincible_streak_current = 0
        invincible_streak_max = 0
        hat_trick_days = 0
        
        for idx, date in enumerate(dates):
            # Get daily stats
            cursor.execute("""
                SELECT emails_sent, emails_new, emails_followup, emails_response, rpi
                FROM daily_stats
                WHERE date = ?
            """, (date,))
            
            row = cursor.fetchone()
            if not row:
                continue
            
            emails_sent, emails_new, emails_followup, emails_response, rpi = row
            total_emails += emails_sent
            
            # Calculate streak
            streak_days = calculate_streak(conn, date)
            
            # Calculate base XP from emails
            base_xp = (
                emails_new * EMAIL_XP['new'] +
                emails_followup * EMAIL_XP['follow_up'] +
                emails_response * EMAIL_XP['response']
            )
            
            # Calculate daily bonuses
            stats = {
                'emails_sent': emails_sent,
                'emails_new': emails_new,
                'rpi': rpi,
                'streak_days': streak_days
            }
            
            bonuses = calculate_daily_bonuses(date, stats)
            bonus_xp = sum(b['xp'] for b in bonuses)
            
            total_before_multiplier = base_xp + bonus_xp
            
            # Apply RPI multiplier
            if rpi is not None and rpi > 0:
                multiplier_result = apply_rpi_multiplier(total_before_multiplier, rpi)
                final_xp = multiplier_result['final_xp']
                multiplier = multiplier_result['multiplier']
            else:
                final_xp = total_before_multiplier
                multiplier = 1.0
            
            cumulative_xp += final_xp
            
            # Track performance stats for achievements
            if rpi and rpi >= 100:
                clean_sheets += 1
            
            if rpi and rpi >= 150:
                invincible_streak_current += 1
                invincible_streak_max = max(invincible_streak_max, invincible_streak_current)
            else:
                invincible_streak_current = 0
            
            if emails_new >= 5:
                hat_trick_days += 1
            
            # Write to database
            if not dry_run:
                # Insert XP transactions
                cursor.execute("""
                    INSERT INTO xp_ledger 
                    (transaction_date, xp_amount, xp_type, description)
                    VALUES (?, ?, 'email', 'Base email XP')
                """, (date, base_xp))
                
                for bonus in bonuses:
                    cursor.execute("""
                        INSERT INTO xp_ledger 
                        (transaction_date, xp_amount, xp_type, description)
                        VALUES (?, ?, ?, ?)
                    """, (date, bonus['xp'], bonus['type'], bonus['description']))
                
                # Update daily_stats
                current_level = calculate_level(cumulative_xp)
                
                cursor.execute("""
                    UPDATE daily_stats
                    SET xp_earned = ?,
                        xp_multiplier = ?
                    WHERE date = ?
                """, (final_xp, multiplier, date))
                
                # Check achievements periodically
                if (idx + 1) % 10 == 0:
                    check_and_unlock_achievements(
                        conn, total_emails, cumulative_xp, current_level,
                        streak_days, clean_sheets, invincible_streak_max,
                        hat_trick_days, dry_run=False
                    )
            
            if (idx + 1) % 100 == 0:
                logger.info(f"  Processed {idx + 1}/{len(dates)} dates...")
        
        # Final achievement check
        final_level = calculate_level(cumulative_xp)
        final_streak = calculate_streak(conn, dates[-1]) if dates else 0
        
        newly_unlocked = check_and_unlock_achievements(
            conn, total_emails, cumulative_xp, final_level,
            final_streak, clean_sheets, invincible_streak_max,
            hat_trick_days, dry_run=dry_run
        )
        
        if not dry_run:
            conn.commit()
        
        result = {
            'days': len(dates),
            'total_emails': total_emails,
            'total_xp': cumulative_xp,
            'final_level': final_level,
            'achievements_unlocked': len(newly_unlocked),
            'new_achievements': newly_unlocked
        }
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"Error in recalculate_all_xp: {e}", exc_info=True)
        if conn:
            conn.close()
        return {'error': str(e)}


def main(recalculate: bool = False, date: str = None, dry_run: bool = False) -> int:
    """
    Main execution:
    - If recalculate=True: Rebuild all XP from scratch
    - If date provided: Calculate XP for specific date
    - Otherwise: Calculate XP for today
    """
    try:
        if recalculate:
            logger.info("=== Recalculating All XP ===")
            result = recalculate_all_xp(dry_run=dry_run)
            
            if 'error' in result:
                logger.error(f"❌ Recalculation failed: {result['error']}")
                return 1
            
            logger.info(f"✓ Processed {result['days']} days")
            logger.info(f"✓ {result['total_xp']} total XP")
            logger.info(f"✓ Level {result['final_level']}")
            
            if result.get('new_achievements'):
                logger.info(f"🏆 {result['achievements_unlocked']} achievements unlocked:")
                for ach in result['new_achievements']:
                    logger.info(f"   - {ach['name']}: {ach['description']} (+{ach['xp']} XP)")
            
            return 0
        
        # Single date calculation not implemented yet
        # (Would need similar logic but for one day)
        logger.info("Single date calculation not yet implemented")
        logger.info("Use --recalculate to process all historical data")
        return 1
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arsenal XP System")
    parser.add_argument("--recalculate", action="store_true", 
                        help="Recalculate all XP from scratch")
    parser.add_argument("--date", 
                        help="Calculate XP for specific date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Show what would be done")
    
    args = parser.parse_args()
    exit(main(recalculate=args.recalculate, date=args.date, dry_run=args.dry_run))

#!/usr/bin/env python3
"""
RPI Calculator & Daily Aggregator
Integrates email output, expected load, and XP to calculate true productivity

Principles Applied:
- P2 (SSOT): Reads from source tables, writes to daily_stats
- P7 (Dry-Run): --dry-run flag for safe testing
- P18 (Verify State): Database queries verify calculations
- P19 (Error Handling): Try/except around DB operations
- P21 (Document Assumptions): Formulas documented (3 emails/hour, baseline 5)
- P22 (Language Selection): Python for data aggregation + SQLite
"""

import argparse
import json
import logging
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

# === CONSTANTS ===

EMAILS_PER_HOUR = 3    # Meeting → follow-up email assumption
BASELINE_EMAILS = 5     # Daily minimum expectation
STREAK_RPI_THRESHOLD = 80  # RPI threshold to maintain streak

# RPI Performance Tiers (from XP System)
RPI_MULTIPLIERS = [
    (150, 1.5, "Invincible Form 🔥"),
    (125, 1.25, "Top Performance ⭐"),
    (100, 1.0, "Meeting Expectations ✅"),
    (75, 0.9, "Catch Up Needed ⚠️"),
    (0, 0.75, "Behind Schedule 🔻")
]


def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def get_performance_tier(rpi: float) -> Tuple[float, str]:
    """
    Get XP multiplier and tier name based on RPI.
    
    Returns:
        (multiplier, tier_name)
    """
    for threshold, multiplier, tier in RPI_MULTIPLIERS:
        if rpi >= threshold:
            return multiplier, tier
    return 0.75, "Behind Schedule 🔻"


def calculate_expected_load(date: str, conn: sqlite3.Connection) -> Dict:
    """
    Calculate expected email output for a date.
    
    Formula:
        expected_emails = (total_meeting_hours * 3) + baseline
        
    Where:
        - 3 emails/hour = assumption for meeting follow-up
        - baseline = 5 emails/day (minimum productivity expectation)
    
    Returns:
        {
            'expected_load_hours': 4.5,
            'expected_emails': 18.5,  # (4.5 * 3) + 5
            'load_breakdown': {
                'calendar': 4.0,
                'manual': 0.5,
                'baseline': 5.0
            }
        }
    """
    try:
        cursor = conn.cursor()
        
        # Query total hours by source
        cursor.execute("""
            SELECT source, SUM(hours) as total_hours
            FROM expected_load
            WHERE date = ?
            GROUP BY source
        """, (date,))
        
        breakdown = {}
        total_hours = 0.0
        
        for row in cursor.fetchall():
            source = row['source']
            hours = row['total_hours'] or 0
            breakdown[source] = hours
            total_hours += hours
        
        # Add baseline to breakdown
        breakdown['baseline'] = BASELINE_EMAILS
        
        # Calculate expected emails
        expected_emails = (total_hours * EMAILS_PER_HOUR) + BASELINE_EMAILS
        
        return {
            'expected_load_hours': total_hours,
            'expected_emails': expected_emails,
            'load_breakdown': breakdown
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate expected load for {date}: {e}")
        raise


def calculate_streak(date: str, emails_sent: int, rpi: float, conn: sqlite3.Connection) -> int:
    """
    Calculate current streak of productive days.
    
    Rules:
        - Streak continues if: emails_sent > 0 AND rpi >= 80%
        - Streak breaks if: emails_sent == 0 OR rpi < 80%
        - Must be consecutive calendar days
    
    Returns: int (current streak days)
    """
    try:
        if emails_sent == 0:
            return 0
        
        # Query previous day
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, emails_sent, rpi, streak_days
            FROM daily_stats
            WHERE date < ?
            ORDER BY date DESC
            LIMIT 1
        """, (date,))
        
        prev = cursor.fetchone()
        if not prev:
            return 1  # First day
        
        prev_date = prev['date']
        prev_emails = prev['emails_sent']
        prev_rpi = prev['rpi']
        prev_streak = prev['streak_days']
        
        # Check if consecutive
        current_dt = datetime.strptime(date, "%Y-%m-%d")
        prev_dt = datetime.strptime(prev_date, "%Y-%m-%d")
        
        if (current_dt - prev_dt).days != 1:
            return 1  # Gap, restart streak
        
        # Check streak rules
        if prev_emails > 0 and prev_rpi >= STREAK_RPI_THRESHOLD:
            return prev_streak + 1
        else:
            return 1  # Previous day broke streak
            
    except Exception as e:
        logger.error(f"Failed to calculate streak for {date}: {e}")
        return 0


def calculate_level_from_xp(total_xp: int) -> int:
    """
    Calculate level from cumulative XP.
    
    Formula: level = floor(sqrt(total_xp / 100)) + 1
    
    Returns: int (level)
    """
    import math
    if total_xp <= 0:
        return 1
    return math.floor(math.sqrt(total_xp / 100)) + 1


def calculate_rpi_for_date(target_date: str, dry_run: bool = False) -> Dict:
    """
    Calculate RPI and all related metrics for a specific date.
    
    Process:
    1. Count actual emails sent (from sent_emails)
    2. Calculate expected load (from expected_load + baseline)
    3. Calculate RPI = (actual / expected) * 100
    4. Aggregate XP from xp_ledger
    5. Calculate streak (consecutive days with emails)
    6. Calculate level (from cumulative XP)
    
    Returns:
        {
            'date': '2025-10-26',
            'emails_sent': 5,
            'emails_new': 0,  # Not tracked in current schema
            'emails_followup': 0,  # Not tracked in current schema
            'emails_response': 0,  # Not tracked in current schema
            'expected_load_hours': 4.5,
            'expected_emails': 13.5,  # hours * 3 emails/hour
            'rpi': 37.0,  # (5 / 13.5) * 100
            'xp_earned': 46,
            'xp_multiplier': 0.75,  # RPI <75%
            'level': 1,
            'streak_days': 0,  # RPI < 100%
            'performance_tier': 'Behind Schedule 🔻'
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Count actual emails sent
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM sent_emails
            WHERE date = ?
        """, (target_date,))
        
        emails_sent = cursor.fetchone()['count']
        
        # Note: Current schema doesn't track email_type breakdown
        # Setting to 0 for now
        emails_new = 0
        emails_followup = 0
        emails_response = 0
        
        # 2. Calculate expected load
        load_data = calculate_expected_load(target_date, conn)
        expected_emails = load_data['expected_emails']
        expected_load_hours = load_data['expected_load_hours']
        
        # 3. Calculate RPI
        if expected_emails > 0:
            rpi = (emails_sent / expected_emails) * 100
        else:
            rpi = 100.0 if emails_sent > 0 else 0.0
        
        # 4. Get performance tier and multiplier
        xp_multiplier, performance_tier = get_performance_tier(rpi)
        
        # 5. Aggregate XP for the day
        cursor.execute("""
            SELECT SUM(xp_amount) as total_xp
            FROM xp_ledger
            WHERE DATE(transaction_date) = ?
        """, (target_date,))
        
        xp_result = cursor.fetchone()
        xp_earned = xp_result['total_xp'] if xp_result['total_xp'] else 0
        
        # 6. Calculate cumulative XP and level
        cursor.execute("""
            SELECT SUM(xp_amount) as cumulative_xp
            FROM xp_ledger
            WHERE DATE(transaction_date) <= ?
        """, (target_date,))
        
        cumulative_result = cursor.fetchone()
        cumulative_xp = cumulative_result['cumulative_xp'] if cumulative_result['cumulative_xp'] else 0
        level = calculate_level_from_xp(cumulative_xp)
        
        # 7. Calculate streak (needs to be done after potential insert)
        # Will be calculated in the upsert step
        
        result = {
            'date': target_date,
            'emails_sent': emails_sent,
            'emails_new': emails_new,
            'emails_followup': emails_followup,
            'emails_response': emails_response,
            'expected_load_hours': expected_load_hours,
            'expected_emails': expected_emails,
            'rpi': round(rpi, 1),
            'xp_earned': xp_earned,
            'xp_multiplier': xp_multiplier,
            'level': level,
            'streak_days': 0,  # Placeholder, calculated after insert
            'performance_tier': performance_tier
        }
        
        if dry_run:
            logger.info(f"[DRY RUN] Would insert/update daily_stats for {target_date}")
            logger.info(f"[DRY RUN] {json.dumps(result, indent=2)}")
        else:
            # Insert/update daily_stats
            cursor.execute("""
                INSERT INTO daily_stats (
                    date, emails_sent, emails_new, emails_followup, emails_response,
                    expected_emails, rpi, xp_earned, xp_multiplier, level, streak_days
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    emails_sent = excluded.emails_sent,
                    emails_new = excluded.emails_new,
                    emails_followup = excluded.emails_followup,
                    emails_response = excluded.emails_response,
                    expected_emails = excluded.expected_emails,
                    rpi = excluded.rpi,
                    xp_earned = excluded.xp_earned,
                    xp_multiplier = excluded.xp_multiplier,
                    level = excluded.level,
                    streak_days = excluded.streak_days
            """, (
                result['date'],
                result['emails_sent'],
                result['emails_new'],
                result['emails_followup'],
                result['emails_response'],
                result['expected_emails'],
                result['rpi'],
                result['xp_earned'],
                result['xp_multiplier'],
                result['level'],
                0  # Will be updated in second pass
            ))
            
            # Now calculate streak with updated data
            streak_days = calculate_streak(target_date, emails_sent, rpi, conn)
            result['streak_days'] = streak_days
            
            # Update streak
            cursor.execute("""
                UPDATE daily_stats
                SET streak_days = ?
                WHERE date = ?
            """, (streak_days, target_date))
            
            conn.commit()
            
            # Verify write
            cursor.execute("""
                SELECT * FROM daily_stats WHERE date = ?
            """, (target_date,))
            
            verified = cursor.fetchone()
            if not verified:
                raise ValueError(f"Failed to verify daily_stats write for {target_date}")
            
            logger.info(f"✓ Updated daily_stats for {target_date}")
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"Failed to calculate RPI for {target_date}: {e}", exc_info=True)
        raise


def backfill_baseline_expectations(dry_run: bool = False) -> int:
    """
    For dates with sent emails but no expected_load, insert baseline.
    
    Baseline: 5 emails/day expected (1.67 hours at 3 emails/hour)
    
    Returns count of dates backfilled.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find dates with emails but no expected_load
        cursor.execute("""
            SELECT DISTINCT date
            FROM sent_emails
            WHERE date NOT IN (SELECT DISTINCT date FROM expected_load)
            ORDER BY date
        """)
        
        dates_to_backfill = [row['date'] for row in cursor.fetchall()]
        
        if not dates_to_backfill:
            logger.info("No dates need baseline expectations backfill")
            return 0
        
        logger.info(f"Found {len(dates_to_backfill)} dates needing baseline expectations")
        
        if dry_run:
            logger.info("[DRY RUN] Would insert baseline expectations for:")
            for date in dates_to_backfill[:10]:
                logger.info(f"  - {date}")
            if len(dates_to_backfill) > 10:
                logger.info(f"  ... and {len(dates_to_backfill) - 10} more")
            return len(dates_to_backfill)
        
        # Insert baseline expectations
        baseline_hours = BASELINE_EMAILS / EMAILS_PER_HOUR  # ~1.67 hours
        
        for date in dates_to_backfill:
            cursor.execute("""
                INSERT INTO expected_load (date, source, type, hours, title, metadata)
                VALUES (?, 'baseline', 'minimum', ?, 'Baseline expectation', '{}')
            """, (date, baseline_hours))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Backfilled baseline expectations for {len(dates_to_backfill)} dates")
        return len(dates_to_backfill)
        
    except Exception as e:
        logger.error(f"Failed to backfill baseline expectations: {e}", exc_info=True)
        raise


def aggregate_historical_rpi(start_date: str = None, end_date: str = None, dry_run: bool = False) -> Dict:
    """
    Recalculate RPI for all historical dates.
    
    Process:
    1. Query all unique dates from sent_emails and expected_load
    2. For each date, calculate RPI
    3. Update daily_stats table
    4. Log progress every 50 days
    
    Returns summary stats.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all unique dates
        cursor.execute("""
            SELECT DISTINCT date FROM sent_emails
            UNION
            SELECT DISTINCT date FROM expected_load
            ORDER BY date
        """)
        
        all_dates = [row['date'] for row in cursor.fetchall()]
        
        # Filter by date range if provided
        if start_date:
            all_dates = [d for d in all_dates if d >= start_date]
        if end_date:
            all_dates = [d for d in all_dates if d <= end_date]
        
        if not all_dates:
            logger.info("No dates found to process")
            return {'days': 0, 'avg_rpi': 0}
        
        logger.info(f"Processing {len(all_dates)} dates from {all_dates[0]} to {all_dates[-1]}")
        
        conn.close()
        
        # Process each date
        total_rpi = 0
        successful_days = 0
        
        for i, date in enumerate(all_dates):
            try:
                result = calculate_rpi_for_date(date, dry_run=dry_run)
                total_rpi += result['rpi']
                successful_days += 1
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Progress: {i + 1}/{len(all_dates)} days processed")
                    
            except Exception as e:
                logger.warning(f"Failed to process {date}: {e}")
                continue
        
        avg_rpi = total_rpi / successful_days if successful_days > 0 else 0
        
        summary = {
            'days': successful_days,
            'avg_rpi': round(avg_rpi, 1),
            'date_range': f"{all_dates[0]} to {all_dates[-1]}"
        }
        
        logger.info(f"✓ Processed {successful_days} days")
        logger.info(f"✓ Average RPI: {avg_rpi:.1f}%")
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to aggregate historical RPI: {e}", exc_info=True)
        raise


# === TEAM STATUS INTEGRATION (W3) ===

def calculate_and_update_team_status(date: str, dry_run: bool = False) -> Dict:
    """
    Calculate team status for given date and update database.
    
    Args:
        date: Date string (YYYY-MM-DD)
        dry_run: If True, calculate but don't write to DB
    
    Returns:
        Dict with status calculation results
    """
    from team_status_calculator import TeamStatusCalculator
    
    calculator = TeamStatusCalculator(str(DB_PATH))
    result = calculator.calculate_status(date)
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would update team status to: {result['status']}")
        return result
    
    # Write to database
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Insert/update team_status_history
        cursor.execute("""
            INSERT INTO team_status_history (
                date, status, days_in_status, previous_status,
                top5_avg, grace_days_used, probation_days_remaining
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                status = excluded.status,
                days_in_status = excluded.days_in_status,
                previous_status = excluded.previous_status,
                top5_avg = excluded.top5_avg,
                grace_days_used = excluded.grace_days_used,
                probation_days_remaining = excluded.probation_days_remaining
        """, (
            result['date'],
            result['status'],
            result['days_in_status'],
            result.get('previous_status'),
            result['top5_avg'],
            min(result['grace_days_used'], 2),  # Schema constraint: max 2
            result['probation_days_remaining']
        ))
        
        # If status changed, log transition
        if result['changed'] and result['previous_status']:
            # Map calculator reason to schema enum
            reason_text = result['reason'].lower()
            if 'elite' in reason_text or 'invincible' in reason_text or 'legend' in reason_text:
                reason_enum = 'unlock_elite'
            elif 'probation' in reason_text:
                reason_enum = 'probation_end'
            else:
                reason_enum = 'performance'
            
            cursor.execute("""
                INSERT INTO status_transitions (
                    date, from_status, to_status, reason, top5_avg, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                result['date'],
                result['previous_status'],
                result['status'],
                reason_enum,
                result['top5_avg'],
                result['reason']  # Store full explanation in notes
            ))
        
        # Update career_stats (single-row table, id=1)
        # First, ensure the row exists
        cursor.execute("INSERT OR IGNORE INTO career_stats (id) VALUES (1)")
        
        # Update total game days
        cursor.execute("""
            UPDATE career_stats 
            SET total_game_days = total_game_days + 1,
                last_updated = ?
            WHERE id = 1
        """, (date,))
        
        # Update days at current status
        status_col = f"days_{result['status']}"
        cursor.execute(f"""
            UPDATE career_stats 
            SET {status_col} = {status_col} + 1
            WHERE id = 1
        """)
        
        # Track promotions/demotions if status changed
        if result['changed'] and result['previous_status']:
            from_idx = ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend'].index(result['previous_status'])
            to_idx = ['transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend'].index(result['status'])
            
            if to_idx > from_idx:
                cursor.execute("UPDATE career_stats SET total_promotions = total_promotions + 1 WHERE id = 1")
                # Check for elite unlock
                if result['status'] in ['invincible', 'legend'] and result['previous_status'] not in ['invincible', 'legend']:
                    cursor.execute("UPDATE career_stats SET elite_unlocks = elite_unlocks + 1 WHERE id = 1")
            elif to_idx < from_idx:
                cursor.execute("UPDATE career_stats SET total_demotions = total_demotions + 1 WHERE id = 1")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update team status: {e}")
        raise
    finally:
        conn.close()
    
    return result




def main(recalculate: bool = False, date: str = None, backfill: bool = False, dry_run: bool = False) -> int:
    """
    Main execution:
    - If recalculate=True: Rebuild RPI for all dates
    - If backfill=True: Add baseline expectations for dates missing load
    - If date provided: Calculate RPI for specific date
    - Otherwise: Calculate RPI for today
    """
    try:
        if backfill:
            logger.info("=== Backfilling Baseline Expectations ===")
            count = backfill_baseline_expectations(dry_run=dry_run)
            logger.info(f"✓ Backfilled {count} dates")
            return 0
        
        if recalculate:
            logger.info("=== Recalculating All RPI ===")
            result = aggregate_historical_rpi(dry_run=dry_run)
            logger.info(f"✓ Processed {result['days']} days")
            logger.info(f"✓ Average RPI: {result['avg_rpi']:.1f}%")
            return 0
        
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"=== Calculating RPI for {target_date} ===")
        
        # Calculate and store RPI for date
        result = calculate_rpi_for_date(target_date, dry_run=dry_run)
        
        logger.info(f"✓ {result['emails_sent']} emails sent")
        logger.info(f"✓ {result['expected_emails']:.1f} emails expected")
        logger.info(f"✓ RPI: {result['rpi']:.1f}% ({result['performance_tier']})")
        logger.info(f"✓ XP: {result['xp_earned']} (Multiplier: {result['xp_multiplier']}×)")
        logger.info(f"✓ Level: {result['level']}")
        logger.info(f"✓ Streak: {result['streak_days']} days")

        # Calculate team status (W3 Integration)
        status_result = calculate_and_update_team_status(target_date, dry_run=dry_run)
        logger.info(f"✓ Team Status: {status_result['status'].upper()}")
        if status_result['changed']:
            logger.info(f"  ⚡ Status Change: {status_result['previous_status']} → {status_result['status']}")
            logger.info(f"  Reason: {status_result['reason']}")

        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RPI Calculator & Daily Aggregator")
    parser.add_argument("--recalculate", action="store_true", help="Recalculate RPI for all dates")
    parser.add_argument("--backfill", action="store_true", help="Backfill baseline expectations")
    parser.add_argument("--date", help="Calculate RPI for specific date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    exit(main(
        recalculate=args.recalculate,
        date=args.date,
        backfill=args.backfill,
        dry_run=args.dry_run
    ))



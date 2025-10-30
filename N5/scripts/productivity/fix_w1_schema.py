#!/usr/bin/env python3
"""
Schema Migration: Align W1 implementation with W2 handoff requirements

Fixes:
1. team_status_history - Add consecutive_poor_days, reason, changed_at
2. status_transitions - Add grace_days_used, consecutive_poor_days, probation_triggered
3. coaching_emails - Rename status → status_at_time, add trigger_context

Author: N5 System
Date: 2025-10-30
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple

DB_PATH = Path("/home/workspace/productivity_tracker.db")

def backup_database() -> Path:
    """Create timestamped backup of database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"{DB_PATH.stem}_backup_{timestamp}{DB_PATH.suffix}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def verify_current_schema(conn: sqlite3.Connection) -> bool:
    """Check that we're starting from W1's schema"""
    cursor = conn.cursor()
    
    # Check team_status_history has promotion_eligible but not consecutive_poor_days
    cursor.execute("PRAGMA table_info(team_status_history)")
    cols = {row[1] for row in cursor.fetchall()}
    
    if "consecutive_poor_days" in cols:
        print("⚠️  Schema already has consecutive_poor_days - may already be migrated")
        return False
    
    if "promotion_eligible" not in cols:
        print("⚠️  Schema missing promotion_eligible - unexpected state")
        return False
    
    print("✓ Current schema matches W1 implementation")
    return True

def migrate_team_status_history(conn: sqlite3.Connection) -> None:
    """Add missing columns to team_status_history"""
    cursor = conn.cursor()
    
    print("\n=== Migrating team_status_history ===")
    
    # Add consecutive_poor_days
    cursor.execute("""
        ALTER TABLE team_status_history 
        ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0 
        CHECK(consecutive_poor_days >= 0)
    """)
    print("✓ Added consecutive_poor_days")
    
    # Add reason
    cursor.execute("""
        ALTER TABLE team_status_history 
        ADD COLUMN reason TEXT 
        CHECK(reason IN ('performance', 'unlock_elite', 'probation_end', 'manual_override', 'initial'))
    """)
    print("✓ Added reason")
    
    # Add changed_at
    cursor.execute("""
        ALTER TABLE team_status_history 
        ADD COLUMN changed_at TIMESTAMP
    """)
    print("✓ Added changed_at")
    
    # Note: We leave promotion_eligible in place (SQLite doesn't easily drop columns)
    # W2 calculator will simply ignore it
    print("  (promotion_eligible left in place - will be ignored)")
    
    conn.commit()

def migrate_status_transitions(conn: sqlite3.Connection) -> None:
    """Add missing columns to status_transitions"""
    cursor = conn.cursor()
    
    print("\n=== Migrating status_transitions ===")
    
    # Add grace_days_used
    cursor.execute("""
        ALTER TABLE status_transitions 
        ADD COLUMN grace_days_used INTEGER DEFAULT 0 
        CHECK(grace_days_used >= 0 AND grace_days_used <= 2)
    """)
    print("✓ Added grace_days_used")
    
    # Add consecutive_poor_days
    cursor.execute("""
        ALTER TABLE status_transitions 
        ADD COLUMN consecutive_poor_days INTEGER DEFAULT 0
    """)
    print("✓ Added consecutive_poor_days")
    
    # Add probation_triggered
    cursor.execute("""
        ALTER TABLE status_transitions 
        ADD COLUMN probation_triggered INTEGER DEFAULT 0 
        CHECK(probation_triggered IN (0, 1))
    """)
    print("✓ Added probation_triggered")
    
    conn.commit()

def migrate_coaching_emails(conn: sqlite3.Connection) -> None:
    """Rebuild coaching_emails table with correct schema"""
    cursor = conn.cursor()
    
    print("\n=== Migrating coaching_emails ===")
    
    # Check if table has data
    cursor.execute("SELECT COUNT(*) FROM coaching_emails")
    row_count = cursor.fetchone()[0]
    print(f"  Found {row_count} existing rows")
    
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE coaching_emails_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            email_type TEXT NOT NULL 
                CHECK(email_type IN ('demotion', 'promotion', 'warning', 'grace_alert', 'achievement')),
            status_at_time TEXT NOT NULL 
                CHECK(status_at_time IN ('transfer_list', 'reserves', 'squad_member', 'first_team', 'invincible', 'legend')),
            trigger_context TEXT NOT NULL,
            subject TEXT,
            sent INTEGER DEFAULT 0 CHECK(sent IN (0, 1)),
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created coaching_emails_new table")
    
    # Copy data from old table (status → status_at_time, default trigger_context)
    if row_count > 0:
        cursor.execute("""
            INSERT INTO coaching_emails_new 
                (id, date, email_type, status_at_time, trigger_context, subject, sent, sent_at, created_at)
            SELECT 
                id, date, email_type, status, 
                'Migrated from W1 schema' as trigger_context,
                subject, sent, sent_at, created_at
            FROM coaching_emails
        """)
        print(f"✓ Copied {row_count} rows (status → status_at_time)")
    
    # Drop old table
    cursor.execute("DROP TABLE coaching_emails")
    print("✓ Dropped old coaching_emails table")
    
    # Rename new table
    cursor.execute("ALTER TABLE coaching_emails_new RENAME TO coaching_emails")
    print("✓ Renamed coaching_emails_new → coaching_emails")
    
    conn.commit()

def verify_final_schema(conn: sqlite3.Connection) -> Tuple[bool, list]:
    """Verify schema matches W2 handoff requirements"""
    cursor = conn.cursor()
    issues = []
    
    print("\n=== Verifying Final Schema ===")
    
    # Check team_status_history
    cursor.execute("PRAGMA table_info(team_status_history)")
    tsh_cols = {row[1] for row in cursor.fetchall()}
    required_tsh = {'consecutive_poor_days', 'reason', 'changed_at', 'days_in_status', 
                    'previous_status', 'top5_avg', 'grace_days_used', 'probation_days_remaining'}
    missing_tsh = required_tsh - tsh_cols
    if missing_tsh:
        issues.append(f"team_status_history missing: {missing_tsh}")
    else:
        print("✓ team_status_history has all required columns")
    
    # Check status_transitions
    cursor.execute("PRAGMA table_info(status_transitions)")
    st_cols = {row[1] for row in cursor.fetchall()}
    required_st = {'grace_days_used', 'consecutive_poor_days', 'probation_triggered',
                   'from_status', 'to_status', 'reason', 'top5_avg'}
    missing_st = required_st - st_cols
    if missing_st:
        issues.append(f"status_transitions missing: {missing_st}")
    else:
        print("✓ status_transitions has all required columns")
    
    # Check coaching_emails
    cursor.execute("PRAGMA table_info(coaching_emails)")
    ce_cols = {row[1] for row in cursor.fetchall()}
    required_ce = {'status_at_time', 'trigger_context', 'email_type', 'subject'}
    missing_ce = required_ce - ce_cols
    if missing_ce:
        issues.append(f"coaching_emails missing: {missing_ce}")
    
    if 'status' in ce_cols:
        issues.append("coaching_emails still has 'status' column (should be status_at_time)")
    
    if not issues:
        print("✓ coaching_emails has all required columns")
    
    return (len(issues) == 0, issues)

def main():
    """Run migration with backup and verification"""
    print("=" * 60)
    print("W1 → W2 Schema Migration")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return 1
    
    # Create backup
    backup_path = backup_database()
    
    # Connect
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Verify starting state
        if not verify_current_schema(conn):
            print("\n⚠️  Schema state unexpected. Review manually before proceeding.")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration aborted.")
                return 0
        
        # Run migrations
        migrate_team_status_history(conn)
        migrate_status_transitions(conn)
        migrate_coaching_emails(conn)
        
        # Verify final state
        success, issues = verify_final_schema(conn)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ MIGRATION SUCCESSFUL")
            print("=" * 60)
            print(f"Backup saved at: {backup_path}")
            print("\nSchema now aligned with W2 handoff requirements.")
            print("Ready to build team_status_calculator.py")
            return 0
        else:
            print("\n" + "=" * 60)
            print("⚠️  MIGRATION COMPLETED WITH ISSUES")
            print("=" * 60)
            for issue in issues:
                print(f"  - {issue}")
            print(f"\nBackup available at: {backup_path}")
            return 1
            
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print(f"\nRestore from backup: {backup_path}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Productivity Tracker Database Setup
Creates SQLite database with complete schema
"""

import sqlite3
import logging
import argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/productivity_tracker.db")

def main(dry_run: bool = False) -> int:
    """Setup database with schema and seed data"""
    try:
        if dry_run:
            logger.info("[DRY RUN] Would create database at: %s", DB_PATH)
            logger.info("[DRY RUN] Would create 6 tables with indexes")
            logger.info("[DRY RUN] Would insert seed data (3 eras, 9 achievements)")
            return 0
        
        # Create database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        logger.info("Creating tables...")
        create_tables(cursor)
        
        # Create indexes
        logger.info("Creating indexes...")
        create_indexes(cursor)
        
        # Seed data
        logger.info("Inserting seed data...")
        seed_data(cursor)
        
        conn.commit()
        conn.close()
        
        # Verify
        if not verify_database():
            logger.error("Database verification failed")
            return 1
        
        logger.info("✓ Database setup complete: %s", DB_PATH)
        return 0
        
    except Exception as e:
        logger.error("Database setup failed: %s", e, exc_info=True)
        return 1

def create_tables(cursor):
    """Create all tables"""
    # emails table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY,
            gmail_message_id TEXT UNIQUE NOT NULL,
            thread_id TEXT,
            subject TEXT,
            sent_at TIMESTAMP NOT NULL,
            email_type TEXT NOT NULL,
            subject_tag TEXT,
            word_count INTEGER,
            response_time_hours REAL,
            is_substantial BOOLEAN,
            is_incoming BOOLEAN,
            era TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # load_events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS load_events (
            id INTEGER PRIMARY KEY,
            event_date DATE NOT NULL,
            event_type TEXT NOT NULL,
            source_id TEXT,
            expected_emails REAL,
            description TEXT,
            stakeholder_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # daily_stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY,
            date DATE UNIQUE NOT NULL,
            emails_sent INTEGER DEFAULT 0,
            emails_new INTEGER DEFAULT 0,
            emails_followup INTEGER DEFAULT 0,
            emails_response INTEGER DEFAULT 0,
            expected_emails REAL DEFAULT 0,
            rpi REAL DEFAULT 100,
            xp_earned INTEGER DEFAULT 0,
            xp_multiplier REAL DEFAULT 1.0,
            level INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # xp_ledger table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS xp_ledger (
            id INTEGER PRIMARY KEY,
            transaction_date TIMESTAMP NOT NULL,
            xp_amount INTEGER NOT NULL,
            xp_type TEXT NOT NULL,
            description TEXT,
            email_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email_id) REFERENCES emails(id)
        )
    """)
    
    # achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY,
            achievement_name TEXT UNIQUE NOT NULL,
            achievement_type TEXT NOT NULL,
            xp_reward INTEGER NOT NULL,
            unlocked_at TIMESTAMP,
            description TEXT,
            icon TEXT
        )
    """)
    
    # eras table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eras (
            id INTEGER PRIMARY KEY,
            era_name TEXT UNIQUE NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            total_emails INTEGER DEFAULT 0,
            avg_emails_per_week REAL DEFAULT 0,
            avg_response_time_hours REAL DEFAULT 0,
            description TEXT
        )
    """)

def create_indexes(cursor):
    """Create all indexes"""
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_era ON emails(era)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_thread ON emails(thread_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_load_events_date ON load_events(event_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_load_events_type ON load_events(event_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_xp_ledger_date ON xp_ledger(transaction_date)")

def seed_data(cursor):
    """Insert seed data"""
    # Eras
    eras = [
        ('pre_superhuman', '2020-01-01', '2024-11-11', 'Baseline productivity before Superhuman'),
        ('post_superhuman', '2024-11-12', '2025-10-24', 'Productivity with Superhuman email client'),
        ('post_zo', '2025-10-25', None, 'Productivity with Zo AI assistance')
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO eras (era_name, start_date, end_date, description) VALUES (?, ?, ?, ?)",
        eras
    )
    
    # Achievements
    achievements = [
        ('first_email', 'milestone', 10, 'Arsenal Academy Signup', '⚽'),
        ('level_5', 'milestone', 50, 'Reserve Team Call-Up', '📋'),
        ('level_10', 'milestone', 100, 'First Team Debut', '🎽'),
        ('level_15', 'milestone', 200, 'Regular Starter', '⭐'),
        ('level_20', 'milestone', 500, 'Club Captain', '©️'),
        ('level_25', 'milestone', 1000, 'Arsenal Legend', '🏆'),
        ('clean_sheet_7', 'streak', 350, '7-Day Clean Sheet', '🔥'),
        ('hat_trick', 'performance', 20, 'Hat Trick (3+ new emails)', '⚡'),
        ('invincible', 'performance', 100, 'Invincible Week (RPI≥150% for 7 days)', '👑'),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO achievements (achievement_name, achievement_type, xp_reward, description, icon) VALUES (?, ?, ?, ?, ?)",
        achievements
    )

def verify_database() -> bool:
    """Verify database was created correctly"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        required = {'emails', 'load_events', 'daily_stats', 'xp_ledger', 'achievements', 'eras'}
        
        if not required.issubset(tables):
            logger.error("Missing tables: %s", required - tables)
            return False
        
        logger.info("✓ All 6 tables created: %s", ', '.join(sorted(required)))
        
        # Check seed data
        cursor.execute("SELECT COUNT(*) FROM eras")
        era_count = cursor.fetchone()[0]
        if era_count != 3:
            logger.error("Eras seed data incomplete: expected 3, found %d", era_count)
            return False
        
        logger.info("✓ Eras seed data: %d records", era_count)
        
        cursor.execute("SELECT COUNT(*) FROM achievements")
        achievement_count = cursor.fetchone()[0]
        if achievement_count < 9:
            logger.error("Achievements seed data incomplete: expected 9, found %d", achievement_count)
            return False
        
        logger.info("✓ Achievements seed data: %d records", achievement_count)
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        required_indexes = {
            'idx_emails_sent_at', 'idx_emails_era', 'idx_emails_thread',
            'idx_load_events_date', 'idx_load_events_type',
            'idx_daily_stats_date', 'idx_xp_ledger_date'
        }
        
        if not required_indexes.issubset(indexes):
            logger.warning("Some indexes missing: %s", required_indexes - indexes)
        else:
            logger.info("✓ All indexes created: %d indexes", len(required_indexes))
        
        conn.close()
        logger.info("✓ Database verification passed")
        return True
        
    except Exception as e:
        logger.error("Verification error: %s", e)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))

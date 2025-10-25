# Worker 1: Database Setup

**Orchestrator:** con_6NobvGrBPaGJQwZA  
**Task ID:** W1-DATABASE  
**Estimated Time:** 30 minutes  
**Dependencies:** None

---

## Mission

Create SQLite database with complete schema for productivity tracking system including emails, load events, daily stats, XP ledger, achievements, and eras tables.

---

## Context

This is the foundation (SSOT) for the entire productivity tracking system. All other components depend on this database structure. The schema must support:
- Email classification (new/follow-up/response)
- Load tracking (meetings, incoming emails, manual events)
- RPI calculation
- Arsenal FC XP system
- Historical baseline across 3 eras

**Eras:**
- Pre-Superhuman: Before Nov 12, 2024
- Post-Superhuman/Pre-Zo: Nov 12, 2024 → Oct 24, 2025
- Post-Zo: Oct 25, 2025 onwards

---

## Dependencies

None - this is the first worker.

---

## Deliverables

1. `/home/workspace/productivity_tracker.db` - SQLite database
2. `/home/workspace/N5/scripts/productivity/db_setup.py` - Setup script with dry-run support
3. Database validation output showing all tables created
4. Test results confirming schema integrity

---

## Requirements

### Database Location
- **Path:** `/home/workspace/productivity_tracker.db`
- **Type:** SQLite3
- **Permissions:** User read/write

### Schema Requirements

**Table: emails**
```sql
CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    gmail_message_id TEXT UNIQUE NOT NULL,
    thread_id TEXT,
    subject TEXT,
    sent_at TIMESTAMP NOT NULL,
    email_type TEXT NOT NULL,  -- 'new', 'follow_up', 'response'
    subject_tag TEXT,           -- Extracted [tag] from subject
    word_count INTEGER,
    response_time_hours REAL,   -- For 'response' type
    is_substantial BOOLEAN,     -- Filter out trivial emails
    is_incoming BOOLEAN,        -- Track incoming for load calculation
    era TEXT NOT NULL,          -- 'pre_superhuman', 'post_superhuman', 'post_zo'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emails_sent_at ON emails(sent_at);
CREATE INDEX idx_emails_era ON emails(era);
CREATE INDEX idx_emails_thread ON emails(thread_id);
```

**Table: load_events**
```sql
CREATE TABLE load_events (
    id INTEGER PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,  -- 'meeting', 'incoming_email', 'manual'
    source_id TEXT,             -- Calendar event ID or email ID
    expected_emails REAL,       -- Weight: meetings=1.0, incoming=0.5, manual=user-set
    description TEXT,           -- "1:1 with John", "Networking event, met 12 people"
    stakeholder_type TEXT,      -- 'customer', 'partner', 'coach', 'job_seeker', 'internal', 'other'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_load_events_date ON load_events(event_date);
CREATE INDEX idx_load_events_type ON load_events(event_type);
```

**Table: daily_stats**
```sql
CREATE TABLE daily_stats (
    id INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    emails_new INTEGER DEFAULT 0,
    emails_followup INTEGER DEFAULT 0,
    emails_response INTEGER DEFAULT 0,
    expected_emails REAL DEFAULT 0,
    rpi REAL DEFAULT 100,           -- Relative Productivity Index
    xp_earned INTEGER DEFAULT 0,
    xp_multiplier REAL DEFAULT 1.0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_daily_stats_date ON daily_stats(date);
```

**Table: xp_ledger**
```sql
CREATE TABLE xp_ledger (
    id INTEGER PRIMARY KEY,
    transaction_date TIMESTAMP NOT NULL,
    xp_amount INTEGER NOT NULL,
    xp_type TEXT NOT NULL,      -- 'email', 'bonus', 'achievement', 'streak'
    description TEXT,
    email_id INTEGER,            -- Foreign key to emails if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails(id)
);

CREATE INDEX idx_xp_ledger_date ON xp_ledger(transaction_date);
```

**Table: achievements**
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY,
    achievement_name TEXT UNIQUE NOT NULL,
    achievement_type TEXT NOT NULL,  -- 'milestone', 'streak', 'performance'
    xp_reward INTEGER NOT NULL,
    unlocked_at TIMESTAMP,
    description TEXT,
    icon TEXT                        -- Emoji or icon identifier
);
```

**Table: eras**
```sql
CREATE TABLE eras (
    id INTEGER PRIMARY KEY,
    era_name TEXT UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    total_emails INTEGER DEFAULT 0,
    avg_emails_per_week REAL DEFAULT 0,
    avg_response_time_hours REAL DEFAULT 0,
    description TEXT
);
```

### Seed Data

**Eras:**
```python
eras_data = [
    ('pre_superhuman', '2020-01-01', '2024-11-11', 'Baseline productivity before Superhuman'),
    ('post_superhuman', '2024-11-12', '2025-10-24', 'Productivity with Superhuman email client'),
    ('post_zo', '2025-10-25', None, 'Productivity with Zo AI assistance')
]
```

**Initial Achievements:**
```python
achievements_data = [
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
```

---

## Implementation Guide

### Script Template

```python
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
        
        # Check seed data
        cursor.execute("SELECT COUNT(*) FROM eras")
        if cursor.fetchone()[0] != 3:
            logger.error("Eras seed data incomplete")
            return False
        
        cursor.execute("SELECT COUNT(*) FROM achievements")
        if cursor.fetchone()[0] < 9:
            logger.error("Achievements seed data incomplete")
            return False
        
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
```

---

## Testing

### Run Setup
```bash
python3 /home/workspace/N5/scripts/productivity/db_setup.py
```

### Verify Tables
```bash
sqlite3 /home/workspace/productivity_tracker.db ".tables"
```

Expected output:
```
achievements  daily_stats   emails        eras          load_events   xp_ledger
```

### Verify Schema
```bash
sqlite3 /home/workspace/productivity_tracker.db ".schema emails"
```

### Verify Seed Data
```bash
sqlite3 /home/workspace/productivity_tracker.db "SELECT * FROM eras; SELECT COUNT(*) FROM achievements;"
```

---

## Report Back

When complete, report:
1. ✅ Database created at `/home/workspace/productivity_tracker.db`
2. ✅ Script created at `/home/workspace/N5/scripts/productivity/db_setup.py`
3. ✅ All 6 tables created with indexes
4. ✅ Seed data inserted (3 eras, 9 achievements)
5. ✅ Verification tests passed
6. ✅ Ready for dependent workers (W2, W3, W4)

---

**Orchestrator Contact:** con_6NobvGrBPaGJQwZA  
**Created:** 2025-10-24 23:50 ET

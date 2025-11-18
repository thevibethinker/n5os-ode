#!/usr/bin/env python3
"""
CRM Calendar Webhook Database Migration

Updates database schema for calendar webhook integration:
1. Adds missing columns to calendar_events table
2. Creates webhook_health table
3. Creates webhook_errors table (optional, for tracking)

Run this before setting up the webhook:
    python3 /home/workspace/N5/scripts/crm_calendar_db_migration.py
"""

import sqlite3
import sys

DB_PATH = '/home/workspace/N5/data/crm_v3.db'


def add_calendar_events_columns():
    """Add missing columns to calendar_events table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if columns already exist
    c.execute("PRAGMA table_info(calendar_events)")
    existing_columns = [row[1] for row in c.fetchall()]
    
    # Add attendee_emails column if missing
    if 'attendee_emails' not in existing_columns:
        c.execute("ALTER TABLE calendar_events ADD COLUMN attendee_emails TEXT")
        print("✓ Added attendee_emails column to calendar_events")
    else:
        print("  attendee_emails column already exists")
    
    # Add description column if missing
    if 'description' not in existing_columns:
        c.execute("ALTER TABLE calendar_events ADD COLUMN description TEXT")
        print("✓ Added description column to calendar_events")
    else:
        print("  description column already exists")
    
    # Add webhook_received_at column if missing
    if 'webhook_received_at' not in existing_columns:
        c.execute("ALTER TABLE calendar_events ADD COLUMN webhook_received_at TEXT")
        print("✓ Added webhook_received_at column to calendar_events")
    else:
        print("  webhook_received_at column already exists")
    
    # Add status column if missing
    if 'status' not in existing_columns:
        c.execute("ALTER TABLE calendar_events ADD COLUMN status TEXT DEFAULT 'confirmed'")
        print("✓ Added status column to calendar_events")
    else:
        print("  status column already exists")
    
    # Add last_updated_at column if missing
    if 'last_updated_at' not in existing_columns:
        c.execute("ALTER TABLE calendar_events ADD COLUMN last_updated_at TEXT")
        print("✓ Added last_updated_at column to calendar_events")
    else:
        print("  last_updated_at column already exists")
    
    conn.commit()
    conn.close()


def create_webhook_health_table():
    """Create webhook_health tracking table"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='webhook_health'")
    if c.fetchone():
        print("  webhook_health table already exists")
    else:
        c.execute("""
            CREATE TABLE webhook_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT UNIQUE NOT NULL,          -- 'google_calendar' | 'gmail_sent'
                channel_id TEXT,                       -- Google channel ID
                resource_id TEXT,                      -- Google resource ID
                expiration_time TEXT NOT NULL,         -- When webhook expires
                last_renewal_at TEXT,                  -- Last successful renewal
                last_received_at TEXT,                 -- Last notification received
                status TEXT DEFAULT 'ACTIVE',          -- ACTIVE | EXPIRED | FAILED
                error_count INTEGER DEFAULT 0,         -- Consecutive errors
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        print("✓ Created webhook_health table")
    
    conn.commit()
    conn.close()


def create_webhook_errors_table():
    """Create webhook_errors table for tracking failures (optional but useful)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='webhook_errors'")
    if c.fetchone():
        print("  webhook_errors table already exists")
    else:
        c.execute("""
            CREATE TABLE webhook_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,           -- 'google_calendar'
                error_type TEXT NOT NULL,        -- VALIDATION | PROCESSING | RENEWAL
                error_message TEXT NOT NULL,
                event_id TEXT,                   -- Related event ID if applicable
                
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        c.execute("CREATE INDEX idx_errors_service ON webhook_errors(service)")
        c.execute("CREATE INDEX idx_errors_created ON webhook_errors(created_at)")
        
        print("✓ Created webhook_errors table")
    
    conn.commit()
    conn.close()


def main():
    """Run all migrations"""
    print("Running CRM Calendar Webhook Database Migration...")
    print(f"Database: {DB_PATH}")
    print("=" * 60)
    
    try:
        add_calendar_events_columns()
        create_webhook_health_table()
        create_webhook_errors_table()
        
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Run: python3 /home/workspace/N5/scripts/crm_calendar_webhook_setup.py")
        print("2. Verify webhook registration")
        print("3. Deploy webhook handler as user service")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


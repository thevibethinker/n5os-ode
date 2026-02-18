#!/usr/bin/env python3
"""
N5 Core Database Schema Manager

Creates and manages the unified n5_core.db database schema.
Consolidates historical CRM/deals sources into n5_core.db

Usage:
    python3 N5/scripts/n5_core_schema.py --create
    python3 N5/scripts/n5_core_schema.py --reset
    python3 N5/scripts/n5_core_schema.py --verify
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Import centralized paths
sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_CORE_DB as DB_PATH

SCHEMA_SQL = """
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Core People Table (THE source of truth for all humans)
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identity
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    linkedin_url TEXT,
    
    -- Professional
    company TEXT,
    title TEXT,
    organization_id INTEGER REFERENCES organizations(id),
    
    -- Categorization
    category TEXT CHECK(category IN (
        'FOUNDER', 'INVESTOR', 'CUSTOMER', 'COMMUNITY',
        'NETWORKING', 'ADVISOR', 'PARTNER', 'OTHER', NULL
    )),
    status TEXT DEFAULT 'active',
    priority TEXT DEFAULT 'medium',
    tags TEXT, -- JSON array
    
    -- Tracking
    first_contact_date TEXT,
    last_contact_date TEXT,
    
    -- Profile linkage
    markdown_path TEXT,
    
    -- Source tracking for migration
    source_db TEXT, -- 'crm', 'crm_v3', 'deals'
    source_id TEXT,
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    domain TEXT,
    industry TEXT,
    size TEXT,
    description TEXT,
    linkedin_url TEXT,
    website TEXT,
    
    -- Source tracking for migration
    source_db TEXT,
    source_id TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Deals (business opportunities)
CREATE TABLE IF NOT EXISTS deals (
    id TEXT PRIMARY KEY,
    deal_type TEXT NOT NULL, -- 'zo_partnership', 'careerspan_acquirer', 'leadership'
    
    -- Entity
    company TEXT NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    category TEXT,
    
    -- Pipeline
    pipeline TEXT, -- 'careerspan', 'zo'
    stage TEXT DEFAULT 'identified',
    temperature TEXT DEFAULT 'warm',
    
    -- Key contact (now references people)
    primary_contact_id INTEGER REFERENCES people(id),
    
    -- External sync
    notion_page_id TEXT,
    google_sheet_row INTEGER,
    external_source TEXT,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Deal Roles (junction: which people are on which deals)
CREATE TABLE IF NOT EXISTS deal_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT NOT NULL REFERENCES deals(id),
    person_id INTEGER NOT NULL REFERENCES people(id),
    
    role TEXT NOT NULL, -- 'primary_contact', 'broker', 'champion', 'decision_maker', 'influencer'
    context TEXT,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(deal_id, person_id, role)
);

-- Interactions (meetings, emails, touchpoints)
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER REFERENCES people(id),
    deal_id TEXT REFERENCES deals(id),
    
    type TEXT NOT NULL, -- 'meeting', 'email', 'call', 'linkedin', 'event'
    direction TEXT, -- 'inbound', 'outbound'
    summary TEXT,
    source_ref TEXT, -- meeting folder path, email message_id, etc.
    
    occurred_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Calendar Events (migrated from crm_v3)
CREATE TABLE IF NOT EXISTS calendar_events (
    id TEXT PRIMARY KEY,
    google_event_id TEXT UNIQUE,
    title TEXT,
    start_time TEXT,
    end_time TEXT,
    location TEXT,
    description TEXT,
    meeting_folder TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Event Attendees (junction)
CREATE TABLE IF NOT EXISTS event_attendees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT REFERENCES calendar_events(id),
    person_id INTEGER REFERENCES people(id),
    email TEXT,
    response_status TEXT,
    is_organizer INTEGER DEFAULT 0,
    UNIQUE(event_id, person_id)
);

-- Pending Approvals (for proactive sensor)
CREATE TABLE IF NOT EXISTS pending_approvals (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    name TEXT,
    person_id INTEGER REFERENCES people(id),
    context TEXT,
    source_text TEXT,
    pipeline TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

-- Deal Activities Timeline
CREATE TABLE IF NOT EXISTS deal_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id TEXT REFERENCES deals(id),
    activity_type TEXT NOT NULL,
    description TEXT,
    performed_by TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Relationships (person-to-person connections)
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a_id INTEGER REFERENCES people(id),
    person_b_id INTEGER REFERENCES people(id),
    relationship_type TEXT, -- 'colleague', 'friend', 'former_colleague', 'investor', etc.
    strength TEXT, -- 'strong', 'medium', 'weak'
    notes TEXT,
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Sync State (for external sources)
CREATE TABLE IF NOT EXISTS sync_state (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    notion_page_id TEXT,
    last_pull_at TEXT,
    last_push_at TEXT,
    PRIMARY KEY (entity_type, entity_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_people_email ON people(email);
CREATE INDEX IF NOT EXISTS idx_people_company ON people(company);
CREATE INDEX IF NOT EXISTS idx_people_name ON people(full_name);
CREATE INDEX IF NOT EXISTS idx_people_category ON people(category);
CREATE INDEX IF NOT EXISTS idx_people_status ON people(status);
CREATE INDEX IF NOT EXISTS idx_deals_company ON deals(company);
CREATE INDEX IF NOT EXISTS idx_deals_type ON deals(deal_type);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_pipeline ON deals(pipeline);
CREATE INDEX IF NOT EXISTS idx_deal_roles_deal ON deal_roles(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_roles_person ON deal_roles(person_id);
CREATE INDEX IF NOT EXISTS idx_interactions_person ON interactions(person_id);
CREATE INDEX IF NOT EXISTS idx_interactions_deal ON interactions(deal_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_google ON calendar_events(google_event_id);
CREATE INDEX IF NOT EXISTS idx_event_attendees_event ON event_attendees(event_id);
CREATE INDEX IF NOT EXISTS idx_event_attendees_person ON event_attendees(person_id);
CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations(name);

-- Triggers for updated_at
CREATE TRIGGER IF NOT EXISTS update_people_timestamp 
AFTER UPDATE ON people
FOR EACH ROW
BEGIN
    UPDATE people SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_deals_timestamp 
AFTER UPDATE ON deals
FOR EACH ROW
BEGIN
    UPDATE deals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

EXPECTED_TABLES = [
    'people', 'organizations', 'deals', 'deal_roles', 'interactions',
    'calendar_events', 'event_attendees', 'pending_approvals',
    'deal_activities', 'relationships', 'sync_state'
]


def create_schema(conn: sqlite3.Connection) -> bool:
    """Create all tables and indexes."""
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        print("✓ Schema created successfully")
        return True
    except sqlite3.Error as e:
        print(f"✗ Schema creation failed: {e}")
        return False


def reset_database(db_path: Path) -> bool:
    """Delete and recreate the database."""
    if db_path.exists():
        backup_path = db_path.with_suffix('.db.bak')
        print(f"  Backing up existing database to {backup_path}")
        import shutil
        shutil.copy(db_path, backup_path)
        db_path.unlink()
        print(f"  Deleted {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    result = create_schema(conn)
    conn.close()
    return result


def verify_schema(conn: sqlite3.Connection) -> bool:
    """Verify that all expected tables exist and have correct structure."""
    issues = []
    
    # Check tables exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    for table in EXPECTED_TABLES:
        if table not in existing_tables:
            issues.append(f"Missing table: {table}")
    
    # Check foreign keys are enabled
    fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    if fk_status != 1:
        issues.append("Foreign keys are not enabled")
    
    # Check key indexes exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = {row[0] for row in cursor.fetchall()}
    
    required_indexes = [
        'idx_people_email', 'idx_people_name', 'idx_deals_company',
        'idx_deal_roles_deal', 'idx_deal_roles_person'
    ]
    for idx in required_indexes:
        if idx not in indexes:
            issues.append(f"Missing index: {idx}")
    
    # Check people table has required columns
    cursor = conn.execute("PRAGMA table_info(people)")
    people_cols = {row[1] for row in cursor.fetchall()}
    required_people_cols = {'id', 'full_name', 'email', 'source_db', 'source_id'}
    missing_cols = required_people_cols - people_cols
    if missing_cols:
        issues.append(f"People table missing columns: {missing_cols}")
    
    # Report results
    if issues:
        print("✗ Schema verification FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Schema verification PASSED")
        print(f"  Tables: {len(existing_tables)}")
        print(f"  Indexes: {len(indexes)}")
        
        # Show record counts
        print("\n  Record counts:")
        for table in EXPECTED_TABLES:
            if table in existing_tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"    {table}: {count}")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="N5 Core Database Schema Manager")
    parser.add_argument('--create', action='store_true', help='Create database schema')
    parser.add_argument('--reset', action='store_true', help='Delete and recreate database')
    parser.add_argument('--verify', action='store_true', help='Verify schema integrity')
    
    args = parser.parse_args()
    
    if not any([args.create, args.reset, args.verify]):
        parser.print_help()
        sys.exit(1)
    
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if args.reset:
        print(f"Resetting database at {DB_PATH}...")
        success = reset_database(DB_PATH)
        if not success:
            sys.exit(1)
        # Continue to verify after reset
        args.verify = True
    
    if args.create:
        print(f"Creating schema at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        success = create_schema(conn)
        conn.close()
        if not success:
            sys.exit(1)
    
    if args.verify:
        print(f"\nVerifying schema at {DB_PATH}...")
        if not DB_PATH.exists():
            print(f"✗ Database does not exist: {DB_PATH}")
            sys.exit(1)
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        success = verify_schema(conn)
        conn.close()
        if not success:
            sys.exit(1)
    
    print("\n✓ All operations completed successfully")


if __name__ == "__main__":
    main()

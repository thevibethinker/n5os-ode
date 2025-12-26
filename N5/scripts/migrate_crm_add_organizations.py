#!/usr/bin/env python3
"""
CRM V3 Migration: Add Organizations and Organization Queue
Adds support for organization entities and their enrichment workflow.
"""

import sqlite3
import sys

DB_PATH = '/home/workspace/N5/data/crm_v3.db'

def migrate():
    print(f"Migrating {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Create organizations table
    print("Creating organizations table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,  -- Maps to filename in Knowledge/crm/organizations/
            domain TEXT,
            
            -- Metadata
            source TEXT NOT NULL DEFAULT 'extraction',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            
            -- Enrichment State
            enrichment_status TEXT NOT NULL DEFAULT 'pending', -- pending, queued, enriched, failed, not_found
            last_enriched_at TEXT,
            last_enrichment_error TEXT,
            
            -- Aviato Data (Core)
            aviato_id TEXT,
            linkedin_url TEXT,
            description TEXT,
            industry TEXT,
            founded_year INTEGER,
            headcount_range TEXT,
            location TEXT
        );
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_orgs_slug ON organizations(slug);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_orgs_domain ON organizations(domain);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_orgs_status ON organizations(enrichment_status);")

    # 2. Create organization_enrichment_queue
    print("Creating organization_enrichment_queue table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS organization_enrichment_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            
            -- Scheduling
            priority INTEGER NOT NULL DEFAULT 50,
            scheduled_for TEXT NOT NULL DEFAULT (datetime('now')),
            
            -- State
            status TEXT NOT NULL DEFAULT 'queued', -- queued, processing, completed, failed
            attempt_count INTEGER DEFAULT 0,
            last_attempt_at TEXT,
            
            -- Context
            trigger_source TEXT NOT NULL,
            
            -- Results
            completed_at TEXT,
            error_message TEXT,
            
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_org_queue_status ON organization_enrichment_queue(status);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_org_queue_org ON organization_enrichment_queue(organization_id);")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()


#!/usr/bin/env python3
"""
Sync Organizations to DB
Scans Knowledge/crm/organizations/*.md and syncs them to the SQLite DB.
Queues them for enrichment if they are new or have no domain/aviato_id.
"""

import sqlite3
import os
import re
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/n5_core.db'
ORGS_DIR = '/home/workspace/Knowledge/crm/organizations'

def get_frontmatter_value(content, key):
    match = re.search(f"^{key}:\\s*\"?(.*?)\"?\\s*$", content, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def infer_domain(name):
    """
    Simple heuristic to guess domain from name if it looks like one.
    """
    name = name.lower().strip()
    if '.' in name and ' ' not in name:
        return name
    return None

def sync():
    print(f"Syncing organizations from {ORGS_DIR} to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Ensure tables exist (just in case)
    # (Assuming migration ran, but safe to fail if not)
    
    files = list(Path(ORGS_DIR).glob("*.md"))
    print(f"Found {len(files)} organization files.")
    
    synced_count = 0
    queued_count = 0
    
    for p in files:
        if p.name in ["README.md", "TEMPLATE.md"]:
            continue
            
        content = p.read_text()
        slug = p.stem
        name = get_frontmatter_value(content, "name") or slug.replace("-", " ").title()
        domain = get_frontmatter_value(content, "domain") or infer_domain(name)
        
        # Upsert into organizations
        try:
            c.execute("""
                INSERT INTO organizations (slug, name, domain, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(slug) DO UPDATE SET
                    name = excluded.name,
                    domain = COALESCE(organizations.domain, excluded.domain),
                    updated_at = datetime('now')
                RETURNING id, enrichment_status, domain
            """, (slug, name, domain))
            
            row = c.fetchone()
            org_id = row[0]
            status = row[1]
            current_domain = row[2]
            
            synced_count += 1
            
            # Queue for enrichment if:
            # 1. Status is pending/queued (retry)
            # 2. We have a domain (or can infer one) to enrich with
            # 3. Not already queued (avoid dups)
            
            should_queue = False
            if status in ['pending', 'failed'] and current_domain:
                should_queue = True
            
            if should_queue:
                # Check if already in queue
                c.execute("SELECT 1 FROM organization_enrichment_queue WHERE organization_id = ? AND status IN ('queued', 'processing')", (org_id,))
                if not c.fetchone():
                    c.execute("""
                        INSERT INTO organization_enrichment_queue (organization_id, priority, trigger_source)
                        VALUES (?, 50, 'sync_script')
                    """, (org_id,))
                    queued_count += 1
                    
        except Exception as e:
            print(f"Error syncing {slug}: {e}")

    conn.commit()
    conn.close()
    print(f"Sync complete. Synced {synced_count} orgs. Queued {queued_count} for enrichment.")

if __name__ == "__main__":
    sync()


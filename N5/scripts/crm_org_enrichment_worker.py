#!/usr/bin/env python3
"""
CRM Organization Enrichment Worker
Processes organization_enrichment_queue.
Enriches organizations using Aviato (via domain).
Updates DB and Markdown files.
"""

import sys
import sqlite3
import time
import json
from datetime import datetime
from pathlib import Path

# Add Aviato import
sys.path.insert(0, '/home/workspace/Integrations/Aviato')
from aviato_client import AviatoClient

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
ORGS_DIR = Path('/home/workspace/Knowledge/crm/organizations')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def append_intel_log(slug, source, data):
    """
    Appends an Intelligence Log entry to the organization markdown file.
    """
    path = ORGS_DIR / f"{slug}.md"
    if not path.exists():
        print(f"Warning: File {path} not found.")
        return

    content = path.read_text()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    log_entry = f"\n### {timestamp} | {source}\n\n"
    if isinstance(data, dict):
        for k, v in data.items():
            if v:
                log_entry += f"- **{k}:** {v}\n"
    else:
        log_entry += str(data) + "\n"
        
    if "## Intelligence Log" not in content:
        content += "\n\n## Intelligence Log\n"
    
    content += log_entry
    path.write_text(content)
    print(f"Updated {path.name} with intel.")

def update_markdown_frontmatter(slug, data):
    """
    Updates specific frontmatter fields if they are missing or empty.
    """
    path = ORGS_DIR / f"{slug}.md"
    if not path.exists():
        return

    content = path.read_text()
    lines = content.splitlines()
    new_lines = []
    in_frontmatter = False
    
    # Simple frontmatter update logic (robust enough for this use case)
    # We only inject fields if we have good data
    
    fields_to_update = {
        "domain": data.get("website"),
        "industry": data.get("industry"),
        "linkedin_url": data.get("linkedin_url"),
        "founded": data.get("founded_year"),
        "headcount": data.get("company_size_range")
    }
    
    # This is a bit complex to do robustly with regex replacement in one pass.
    # For now, we'll skip frontmatter rewriting to avoid corruption risk in this "dry run" phase.
    # We rely on the Intelligence Log for the data visibility.
    pass

def process_queue():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Fetch next job
    c.execute("""
        SELECT q.id, q.organization_id, o.slug, o.domain, o.name
        FROM organization_enrichment_queue q
        JOIN organizations o ON q.organization_id = o.id
        WHERE q.status = 'queued'
        ORDER BY q.priority DESC, q.scheduled_for ASC
        LIMIT 1
    """)
    
    job = c.fetchone()
    if not job:
        conn.close()
        return False
        
    job_id, org_id, slug, domain, name = job
    print(f"Processing job {job_id} for {name} ({slug})...")
    
    # Update status to processing
    c.execute("UPDATE organization_enrichment_queue SET status = 'processing', last_attempt_at = datetime('now'), attempt_count = attempt_count + 1 WHERE id = ?", (job_id,))
    conn.commit()
    
    aviato = AviatoClient()
    
    try:
        # Enrich
        result = None
        if domain:
            print(f"Enriching via domain: {domain}")
            result = aviato.enrich_company(website=domain)
        else:
            # Fallback: Try name as website? No, that's risky.
            # If no domain, we can't reliably enrich yet without search.
            print(f"No domain for {slug}. Skipping Aviato.")
            c.execute("UPDATE organization_enrichment_queue SET status = 'failed', error_message = 'No domain provided' WHERE id = ?", (job_id,))
            c.execute("UPDATE organizations SET enrichment_status = 'failed', last_enrichment_error = 'No domain' WHERE id = ?", (org_id,))
            conn.commit()
            conn.close()
            return True

        if result:
            print("Enrichment successful!")
            
            # Map fields
            aviato_data = {
                "website": result.get("website"),
                "linkedin_url": result.get("linkedinURL"),
                "industry": result.get("industry"),
                "founded_year": result.get("foundedYear"),
                "company_size_range": result.get("companySizeRange"),
                "location": result.get("location"),
                "description": result.get("description"),
                "aviato_id": result.get("id")
            }
            
            # Update DB
            c.execute("""
                UPDATE organizations SET
                    enrichment_status = 'enriched',
                    last_enriched_at = datetime('now'),
                    domain = COALESCE(domain, ?),
                    linkedin_url = ?,
                    industry = ?,
                    founded_year = ?,
                    headcount_range = ?,
                    location = ?,
                    description = ?,
                    aviato_id = ?
                WHERE id = ?
            """, (
                aviato_data["website"],
                aviato_data["linkedin_url"],
                aviato_data["industry"],
                aviato_data["founded_year"],
                aviato_data["company_size_range"],
                aviato_data["location"],
                aviato_data["description"],
                aviato_data["aviato_id"],
                org_id
            ))
            
            # Update Queue
            c.execute("UPDATE organization_enrichment_queue SET status = 'completed', completed_at = datetime('now') WHERE id = ?", (job_id,))
            
            # Update Markdown
            append_intel_log(slug, "Aviato Enrichment", aviato_data)
            
        else:
            print("Enrichment returned no data.")
            c.execute("UPDATE organization_enrichment_queue SET status = 'failed', error_message = 'Not found' WHERE id = ?", (job_id,))
            c.execute("UPDATE organizations SET enrichment_status = 'not_found' WHERE id = ?", (org_id,))
            
    except Exception as e:
        print(f"Error: {e}")
        c.execute("UPDATE organization_enrichment_queue SET status = 'failed', error_message = ? WHERE id = ?", (str(e), job_id,))
        c.execute("UPDATE organizations SET enrichment_status = 'failed', last_enrichment_error = ? WHERE id = ?", (str(e), org_id,))
    
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    # Run one job
    process_queue()



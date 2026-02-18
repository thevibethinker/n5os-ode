#!/usr/bin/env python3
"""
CRM Organization Enrichment Worker
Processes organization_enrichment_queue against canonical n5_core.db.
"""

import sys
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/workspace/Integrations/Aviato')
from aviato_client import AviatoClient

DB_PATH = '/home/workspace/N5/data/n5_core.db'
ORGS_DIR = Path('/home/workspace/Personal/Knowledge/CRM/organizations')


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def ensure_runtime_tables(conn):
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS organization_enrichment_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            scheduled_for TEXT,
            priority INTEGER NOT NULL DEFAULT 50,
            status TEXT NOT NULL DEFAULT 'queued',
            attempt_count INTEGER NOT NULL DEFAULT 0,
            last_attempt_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    c.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_org_enrich_queue_status_sched
        ON organization_enrichment_queue(status, scheduled_for)
        """
    )
    conn.commit()


def append_intel_log(slug, source, data):
    path = ORGS_DIR / f"{slug}.md"
    if not path.exists():
        return

    content = path.read_text(encoding='utf-8')
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
    path.write_text(content, encoding='utf-8')


def process_queue():
    conn = get_db_connection()
    ensure_runtime_tables(conn)
    c = conn.cursor()

    c.execute(
        """
        SELECT q.id, q.organization_id, o.name, o.domain
        FROM organization_enrichment_queue q
        JOIN organizations o ON q.organization_id = o.id
        WHERE q.status = 'queued'
        ORDER BY q.priority DESC, COALESCE(q.scheduled_for, q.created_at) ASC
        LIMIT 1
        """
    )

    job = c.fetchone()
    if not job:
        conn.close()
        return False

    job_id, org_id, name, domain = job
    slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in name).strip('-')

    c.execute(
        """
        UPDATE organization_enrichment_queue
        SET status = 'processing', last_attempt_at = datetime('now'), attempt_count = attempt_count + 1
        WHERE id = ?
        """,
        (job_id,),
    )
    conn.commit()

    aviato = AviatoClient()

    try:
        if not domain:
            c.execute(
                "UPDATE organization_enrichment_queue SET status = 'failed', error_message = 'No domain provided' WHERE id = ?",
                (job_id,),
            )
            conn.commit()
            conn.close()
            return True

        result = aviato.enrich_company(website=domain)
        if not result:
            c.execute(
                "UPDATE organization_enrichment_queue SET status = 'failed', error_message = 'Not found' WHERE id = ?",
                (job_id,),
            )
            conn.commit()
            conn.close()
            return True

        aviato_data = {
            "website": result.get("website"),
            "linkedin_url": result.get("linkedinURL"),
            "industry": result.get("industry"),
            "company_size_range": result.get("companySizeRange"),
            "location": result.get("location"),
            "description": result.get("description"),
        }

        c.execute(
            """
            UPDATE organizations SET
                domain = COALESCE(domain, ?),
                website = COALESCE(website, ?),
                linkedin_url = COALESCE(linkedin_url, ?),
                industry = COALESCE(industry, ?),
                size = COALESCE(size, ?),
                description = COALESCE(description, ?)
            WHERE id = ?
            """,
            (
                aviato_data["website"],
                aviato_data["website"],
                aviato_data["linkedin_url"],
                aviato_data["industry"],
                aviato_data["company_size_range"],
                aviato_data["description"],
                org_id,
            ),
        )

        c.execute(
            "UPDATE organization_enrichment_queue SET status = 'completed', completed_at = datetime('now') WHERE id = ?",
            (job_id,),
        )

        append_intel_log(slug, "Aviato Enrichment", aviato_data)

    except Exception as e:
        c.execute(
            "UPDATE organization_enrichment_queue SET status = 'failed', error_message = ? WHERE id = ?",
            (str(e), job_id),
        )

    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    process_queue()

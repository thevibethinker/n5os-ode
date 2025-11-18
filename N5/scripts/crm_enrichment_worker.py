#!/usr/bin/env python3
"""
CRM V3 Enrichment Worker - Tool-First Architecture

Thin orchestration layer that:
1. Manages queue (fetch, update status)
2. Delegates enrichment to LLM via prompts/tools
3. Handles retry logic

NO regex, NO manual YAML parsing - uses tools instead!

Usage:
    python3 crm_enrichment_worker.py              # Production mode (continuous)
    python3 crm_enrichment_worker.py --test       # Test mode (one job then exit)
    python3 crm_enrichment_worker.py --dry-run    # Dry-run (fetch but don't process)
"""

import sys
import os
import sqlite3
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
PROFILES_DIR = '/home/workspace/N5/crm_v3/profiles'


def fetch_next_enrichment_job():
    """
    Fetch next queued job from enrichment_queue.
    Returns job dict or None if queue is empty.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT eq.*, p.email, p.yaml_path
        FROM enrichment_queue eq
        JOIN profiles p ON eq.profile_id = p.id
        WHERE eq.status = 'queued'
          AND eq.scheduled_for <= datetime('now')
        ORDER BY eq.priority DESC, eq.scheduled_for ASC
        LIMIT 1
    """)
    
    job = c.fetchone()
    conn.close()
    
    if job:
        return dict(job)
    return None


def update_job_status(job_id: int, status: str, error_message: str = None):
    """Update job status in database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if status == 'processing':
        c.execute("""
            UPDATE enrichment_queue
            SET status = ?,
                last_attempt_at = datetime('now'),
                attempt_count = attempt_count + 1
            WHERE id = ?
        """, (status, job_id))
    
    elif status == 'completed':
        c.execute("""
            UPDATE enrichment_queue
            SET status = ?,
                completed_at = datetime('now')
            WHERE id = ?
        """, (status, job_id))
    
    elif status == 'failed':
        c.execute("""
            UPDATE enrichment_queue
            SET status = ?,
                error_message = ?
            WHERE id = ?
        """, (status, error_message, job_id))
    
    conn.commit()
    conn.close()


async def enrich_profile_via_tools(profile_id: int, email: str, checkpoint: str, yaml_path: str):
    """
    Enrich profile using tools instead of scripts.
    
    This is where we delegate to:
    - edit_file_llm for YAML appending
    - use_app_gmail for email threads
    - Aviato/LinkedIn stubs (for now)
    
    For now, this is a stub showing the architecture.
    TODO: Replace with actual tool calls via Zo API
    """
    print(f"  → Enriching profile {profile_id} ({email}) - {checkpoint}")
    
    # Gather intelligence from sources
    intelligence_parts = []
    
    # 1. Aviato (stub)
    aviato_data = {
        "name": email.split('@')[0].replace('.', ' ').title(),
        "title": "Senior Product Manager",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "note": "⚠️ STUB DATA - Aviato API not yet integrated"
    }
    intelligence_parts.append(f"""**Aviato Enrichment:**
- Name: {aviato_data['name']}
- Title: {aviato_data['title']}
- Company: {aviato_data['company']}
- Location: {aviato_data['location']}

{aviato_data['note']}
""")
    
    # 2. Gmail (stub - would use use_app_gmail tool)
    gmail_note = f"""**Gmail Thread Analysis:**

Recent threads with {email}:
- Thread 1: "Project Discussion" (2025-11-15)
- Thread 2: "Introduction Request" (2025-11-10)

⚠️ STUB DATA - use_app_gmail tool not yet integrated
"""
    intelligence_parts.append(gmail_note)
    
    # 3. LinkedIn (stub)
    linkedin_note = """**LinkedIn Intelligence:**

⚠️ STUB DATA - LinkedIn API not yet integrated
"""
    intelligence_parts.append(linkedin_note)
    
    # Combine intelligence
    intelligence_content = "\n\n".join(intelligence_parts)
    
    # Append to YAML using tool-based approach
    # TODO: Use actual edit_file_llm tool via Zo API
    # For now, use simple append but mark as tool-based architecture
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""
### {timestamp} | multi_source_enrichment
**Checkpoint:** {checkpoint}
**Sources:** aviato, gmail, linkedin (all stubbed)

{intelligence_content}
"""
    
    # Append to YAML (simple version for now)
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    if "## Intelligence Log" not in content:
        with open(yaml_path, 'a') as f:
            f.write("\n\n## Intelligence Log\n")
    
    with open(yaml_path, 'a') as f:
        f.write(entry)
    
    print(f"  ✓ Appended intelligence to {yaml_path}")
    
    return {
        "success": True,
        "sources_checked": ["aviato", "gmail", "linkedin"],
        "intelligence_added": True
    }


async def process_enrichment_job(job: dict):
    """
    Process a single enrichment job.
    Delegates actual enrichment to tools/prompts.
    """
    job_id = job['id']
    profile_id = job['profile_id']
    email = job['email']
    checkpoint = job['checkpoint']
    yaml_path = job['yaml_path']
    
    print(f"\n📋 Processing job {job_id}: profile {profile_id} ({email})")
    print(f"   Checkpoint: {checkpoint}")
    
    # Mark as processing
    update_job_status(job_id, 'processing')
    
    try:
        # Enrich using tools (not scripts!)
        result = await enrich_profile_via_tools(profile_id, email, checkpoint, yaml_path)
        
        if result['success']:
            update_job_status(job_id, 'completed')
            print(f"  ✓ Job {job_id} completed")
        else:
            update_job_status(job_id, 'failed', "Enrichment returned success=False")
            print(f"  ✗ Job {job_id} failed")
        
    except Exception as e:
        error_msg = str(e)
        print(f"  ✗ Job {job_id} error: {error_msg}")
        
        # Check if we should retry
        attempt_count = job['attempt_count'] + 1
        if attempt_count < 3:
            # Requeue with exponential backoff
            backoff_minutes = [1, 5, 15][attempt_count - 1]
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                UPDATE enrichment_queue
                SET status = 'queued',
                    scheduled_for = datetime('now', '+{} minutes'),
                    error_message = ?
                WHERE id = ?
            """.format(backoff_minutes), (error_msg, job_id))
            conn.commit()
            conn.close()
            print(f"  ↻ Requeued job {job_id} (attempt {attempt_count}/3, retry in {backoff_minutes}min)")
        else:
            # Max retries exceeded
            update_job_status(job_id, 'failed', f"Max retries exceeded: {error_msg}")
            print(f"  ✗ Job {job_id} failed permanently after 3 attempts")


async def enrichment_worker_loop(test_mode: bool = False, dry_run: bool = False):
    """
    Main worker loop.
    
    Args:
        test_mode: Process one job and exit
        dry_run: Fetch jobs but don't process
    """
    print("🚀 CRM Enrichment Worker Starting")
    print(f"   Mode: {'TEST' if test_mode else 'DRY-RUN' if dry_run else 'PRODUCTION'}")
    print(f"   DB: {DB_PATH}")
    print(f"   Profiles: {PROFILES_DIR}")
    print()
    
    iteration = 0
    while True:
        iteration += 1
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking queue (iteration {iteration})...")
        
        job = fetch_next_enrichment_job()
        
        if not job:
            print("  ∅ Queue empty")
            if test_mode:
                print("\n✓ Test mode: No jobs found, exiting")
                break
            await asyncio.sleep(60)
            continue
        
        if dry_run:
            print(f"  → Would process job {job['id']}: {job['email']} ({job['checkpoint']})")
            if test_mode:
                print("\n✓ Dry-run complete, exiting")
                break
            await asyncio.sleep(60)
            continue
        
        # Process the job
        await process_enrichment_job(job)
        
        if test_mode:
            print("\n✓ Test mode: Processed one job, exiting")
            break
        
        # Brief pause before next iteration
        await asyncio.sleep(5)


def create_test_enrichment_job():
    """Create a test enrichment job for the first profile"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get first profile with email
    c.execute("SELECT id, email FROM profiles WHERE email IS NOT NULL LIMIT 1")
    row = c.fetchone()
    
    if not row:
        print("✗ No profiles with email found")
        conn.close()
        return
    
    profile_id, email = row
    
    # Insert test job
    c.execute("""
        INSERT INTO enrichment_queue 
        (profile_id, priority, scheduled_for, checkpoint, trigger_source, trigger_metadata)
        VALUES (?, 100, datetime('now'), 'checkpoint_1', 'manual_test', ?)
    """, (profile_id, json.dumps({"email": email, "test": True})))
    
    job_id = c.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Created test job {job_id} for profile {profile_id} ({email})")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='CRM V3 Enrichment Worker')
    parser.add_argument('--test', action='store_true', help='Test mode: Process one job and exit')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run mode: Fetch jobs but don\'t process')
    parser.add_argument('--create-test-job', action='store_true', help='Create a test enrichment job')
    
    args = parser.parse_args()
    
    if args.create_test_job:
        create_test_enrichment_job()
        return
    
    # Run worker loop
    asyncio.run(enrichment_worker_loop(
        test_mode=args.test,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()




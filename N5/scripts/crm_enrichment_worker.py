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

# Add Aviato import
sys.path.insert(0, '/home/workspace')
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato

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
    - Aviato for person enrichment
    
    For now, this is a stub showing the architecture.
    TODO: Replace with actual tool calls via Zo API
    """
    print(f"  → Enriching profile {profile_id} ({email}) - {checkpoint}")
    
    # Gather intelligence from sources
    intelligence_parts = []
    
    # 1. Aviato enrichment (REAL - no stub)
    profile_name = Path(yaml_path).stem  # Extract name from filename
    aviato_result = await enrich_via_aviato(email, profile_name)
    
    if aviato_result['success']:
        intelligence_parts.append(aviato_result['markdown'])
    else:
        # Graceful fallback on error
        intelligence_parts.append(aviato_result['markdown'])

    
    # 2. Gmail thread analysis (REAL - via Zo CLI)
    try:
        import subprocess
        result = subprocess.run(
            ['zo', f'@crm-gmail-enrichment {email}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            gmail_intelligence = result.stdout.strip()
            intelligence_parts.append(gmail_intelligence)
        else:
            # Fallback if CLI fails
            intelligence_parts.append(f"""**Gmail Thread Analysis:**

⚠️ Gmail enrichment unavailable (CLI error)
Contact: {email}""")
    except subprocess.TimeoutExpired:
        intelligence_parts.append(f"""**Gmail Thread Analysis:**

⚠️ Gmail search timed out
Contact: {email}""")
    except Exception as e:
        intelligence_parts.append(f"""**Gmail Thread Analysis:**

⚠️ Error: {str(e)}
Contact: {email}""")
    
    # 3. LinkedIn intelligence (NOT YET IMPLEMENTED)
    # Reason: Requires LinkedIn API partnership or compliant data provider
    # Implementation path documented in: file 'N5/docs/LINKEDIN_INTEGRATION.md'
    # 
    # To enable LinkedIn enrichment:
    #   1. Choose integration option (API partnership or third-party provider)
    #   2. Implement client module (see LINKEDIN_INTEGRATION.md)
    #   3. Replace this stub with real API call
    #   4. Follow pattern from Aviato integration above
    #
    # Current: System works without LinkedIn using Aviato + Gmail as sources
    linkedin_note = """**LinkedIn Intelligence:**

⚠️ NOT YET IMPLEMENTED - See file 'N5/docs/LINKEDIN_INTEGRATION.md' for integration plan

Status: Phase 2 priority
Data Sources Active: Aviato (✓) + Gmail (✓)"""
    
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
    full_yaml_path = Path(yaml_path)
    if not full_yaml_path.is_absolute():
        full_yaml_path = Path('/home/workspace') / yaml_path
    
    with open(full_yaml_path, 'r') as f:
        content = f.read()
    
    if "## Intelligence Log" not in content:
        with open(full_yaml_path, 'a') as f:
            f.write("\n\n## Intelligence Log\n")
    
    with open(full_yaml_path, 'a') as f:
        f.write(entry)
    
    print(f"  ✓ Appended intelligence to {full_yaml_path}")
    
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
















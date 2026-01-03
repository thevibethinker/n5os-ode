#!/usr/bin/env python3
"""
CRM V3 Enrichment Worker - Tool-First Architecture

Under Stakeholder Intelligence Interface Contract (V1).

- Manages enrichment_queue in N5/data/crm_v3.db.
- Delegates Aviato enrichment to enrichment.aviato_enricher.
- Writes back enrichment status to crm_v3.db.
- Appends Intelligence Log entries into Personal/Knowledge/CRM/individuals/<slug>.md.

Viewer/join responsibilities remain in stakeholder_intel.py.
"""

import sys
import os
import sqlite3
import asyncio
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add Aviato import
sys.path.insert(0, '/home/workspace')
from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato
from N5.scripts.stakeholder_intel import extract_linkedin_metadata, query_linkedin_conversation

# Import canonical paths
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import CRM_INDIVIDUALS, CRM_DB

# Note: enrichment_queue lives in crm_v3.db (has queue-specific tables)
# Output goes to canonical CRM_MARKDOWN_DIR
DB_PATH = '/home/workspace/N5/data/crm_v3.db'  # Enrichment queue DB
PROFILES_DIR = '/home/workspace/N5/crm_v3/profiles'  # Legacy YAML (for queue lookups)
WORKSPACE = Path("/home/workspace")
CRM_MARKDOWN_DIR = CRM_INDIVIDUALS  # Canonical output location
STAGING_DIR = WORKSPACE / "N5" / "data" / "staging" / "aviato"


def fetch_next_enrichment_job():
    """
    Fetch next queued job from enrichment_queue.
    Returns job dict or None if queue is empty.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute(
        """
        SELECT eq.*, p.email, p.primary_email, p.yaml_path,
               p.person_type, p.enrichment_policy, p.enrichment_status
        FROM enrichment_queue eq
        JOIN profiles p ON eq.profile_id = p.id
        WHERE eq.status = 'queued'
          AND eq.scheduled_for <= datetime('now')
        ORDER BY eq.priority DESC, eq.scheduled_for ASC
        LIMIT 1
        """
    )
    
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
        c.execute(
            """
            UPDATE enrichment_queue
            SET status = ?,
                last_attempt_at = datetime('now'),
                attempt_count = attempt_count + 1
            WHERE id = ?
            """,
            (status, job_id),
        )
    elif status == 'completed':
        c.execute(
            """
            UPDATE enrichment_queue
            SET status = ?,
                completed_at = datetime('now')
            WHERE id = ?
            """,
            (status, job_id),
        )
    elif status == 'failed':
        c.execute(
            """
            UPDATE enrichment_queue
            SET status = ?,
                error_message = ?
            WHERE id = ?
            """,
            (status, error_message, job_id),
        )
    
    conn.commit()
    conn.close()


def update_profile_enrichment_status(
    profile_id: int,
    status: str,
    source: str | None = None,
    error: str | None = None,
):
    """Write enrichment status fields back to profiles table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    fields = ["enrichment_status = ?", "last_enriched_at = datetime('now')"]
    params: list[object] = [status]
    if source is not None:
        fields.append("last_enrichment_source = ?")
        params.append(source)
    if error is not None:
        fields.append("last_enrichment_error = ?")
        params.append(error)
    c.execute(
        f"UPDATE profiles SET {', '.join(fields)} WHERE id = ?",
        (*params, profile_id),
    )
    conn.commit()
    conn.close()


def _load_profile_slug(cursor, profile_id: int) -> str | None:
    """Look up YAML profile row and return the slug portion if resolvable.

    Assumes yaml_path in crm_v3 profiles table points to N5/crm_v3/profiles/<slug>.yaml.
    We map that <slug> to canonical CRM markdown path Personal/Knowledge/CRM/individuals/<slug>.md.
    """
    cursor.execute("SELECT yaml_path FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    if not row:
        return None
    yaml_path = row[0] or ""
    name = Path(yaml_path).stem
    return name or None


def _append_intel_log(slug: str, heading: str, body: str) -> None:
    """Append a timestamped Intelligence Log entry into the CRM markdown file for slug.

    Format:
    ### YYYY-MM-DD HH:MM | <heading>

    <body>

    If the file or Intelligence Log section is missing, create them.
    """
    path = CRM_MARKDOWN_DIR / f"{slug}.md"
    if not path.exists():
        # Do not create new identities here; that should be done by dedicated CRM tools.
        return

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # Ensure Intelligence Log section exists
    if "## Intelligence Log" not in text:
        lines.append("")
        lines.append("## Intelligence Log")
        lines.append("")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines.append(f"### {ts} | {heading}")
    lines.append("")
    for line in body.rstrip().splitlines():
        lines.append(line)
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def save_aviato_raw_json(slug: str, data: dict) -> Path | None:
    """Save raw Aviato response JSON to staging directory.
    
    Returns path to saved file, or None if save failed.
    """
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{slug}.json"
    path = STAGING_DIR / filename
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return path
    except Exception as e:
        print(f"  ⚠ Failed to save raw JSON: {e}")
        return None


def _append_linkedin_intel(slug: str) -> None:
    """Append a LinkedIn Intelligence snapshot for this slug, if metadata & data exist.

    Uses existing helpers from stakeholder_intel.py to read CRM markdown and query
    Knowledge/linkedin/linkedin.db. Does nothing if there is no LinkedIn metadata
    or no matching conversation.
    """
    md_path = CRM_MARKDOWN_DIR / f"{slug}.md"
    if not md_path.exists():
        return

    md = md_path.read_text(encoding="utf-8", errors="ignore")
    meta = extract_linkedin_metadata(md)
    convo_id = meta.get("linkedin_conversation_id")
    if not convo_id:
        return

    li_conv = query_linkedin_conversation(convo_id)
    if not li_conv:
        return

    conv = li_conv["conversation"]
    messages = li_conv["messages"][:5]

    lines: list[str] = []
    lines.append("**Source:** linkedin_kondo")
    lines.append("")
    lines.append("**LinkedIn Intelligence:**")
    lines.append(f"- Name: {conv['participant_name']}")
    if conv.get("participant_email"):
        lines.append(f"- Email: {conv['participant_email']}")
    if conv.get("linkedin_profile_url"):
        lines.append(f"- Profile URL: {conv['linkedin_profile_url']}")
    lines.append(f"- Status: {conv['status']}")
    lines.append(f"- Messages: {conv['message_count']}")
    lines.append("")
    if messages:
        lines.append("Recent messages:")
        for msg in messages:
            sent_at = msg.get("sent_at")
            try:
                ts = datetime.fromtimestamp(sent_at / 1000.0, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z") if isinstance(sent_at, int) else str(sent_at)
            except Exception:
                ts = str(sent_at)
            sender = msg.get("sender", "?")
            content = msg.get("content", "").replace("\n", " ")
            if len(content) > 160:
                content = content[:157] + "..."
            lines.append(f"- [{ts}] {sender}: {content}")

    body = "\n".join(lines)
    _append_intel_log(slug, "linkedin_intelligence", body)


async def enrich_profile_via_tools(profile_row: dict, cursor) -> dict:
    """Enrich a single CRM profile using Aviato and return structured result.

    profile_row is a row from the profiles table (NOT the queue join row).

    Returns dict with keys:
    - status: 'succeeded' | 'not_found' | 'failed'
    - aviato_data: mapped CRM-style dict or None
    - error: short error string if failed/not_found
    - slug: CRM slug if resolvable
    """
    profile_id = profile_row["id"]
    raw_email = profile_row["email"]
    primary_email = profile_row.get("primary_email")
    email = primary_email or raw_email

    # Resolve CRM markdown slug for this profile id
    slug = _load_profile_slug(cursor, profile_id)

    # Call Aviato - returns dict with keys: success, data, error, markdown
    try:
        result = await enrich_via_aviato(email)
    except Exception as e:
        return {"status": "failed", "aviato_data": None, "error": str(e), "slug": slug, "markdown": None}

    if not result.get('success') or result.get('error'):
        error_msg = result.get('error', 'Unknown error')
        status = "not_found" if result.get('data') is None and result.get('success') else "failed"
        return {"status": status, "aviato_data": None, "error": error_msg, "slug": slug, "markdown": result.get('markdown')}

    # Success - data may be None if person not found (success=True but data=None)
    if result.get('data') is None:
        return {"status": "not_found", "aviato_data": None, "error": None, "slug": slug, "markdown": result.get('markdown')}
    
    return {"status": "succeeded", "aviato_data": result.get('data'), "error": None, "slug": slug, "markdown": result.get('markdown')}


async def process_enrichment_job(job: dict, dry_run: bool = False) -> None:
    """Process a single enrichment_queue job and update DB + CRM markdown.

    Opens its own DB connection, loads the profile row, calls Aviato enrichment,
    writes back statuses, and appends Aviato + LinkedIn intel to CRM markdown.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    job_id = job["id"]
    profile_id = job["profile_id"]

    # Load full profile row from profiles
    cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    profile_row = {desc[0]: value for desc, value in zip(cursor.description, row)}

    person_type = (profile_row.get("person_type") or "").lower()
    policy = (profile_row.get("enrichment_policy") or "").lower()

    print(f"\n📋 Processing job {job_id}: profile {profile_id} ({profile_row.get('email')})")
    print(f"   Checkpoint: {job['checkpoint']}")

    # Policy gate: skip internal and never-policy profiles
    if person_type == "internal":
        print("  ↷ Skipping internal profile (policy: never)")
        update_profile_enrichment_status(profile_id, "skipped_internal", source=None, error=None)
        update_job_status(job_id, "completed")
        conn.close()
        return

    if policy == "never":
        print("  ↷ Skipping profile due to enrichment_policy=never")
        update_profile_enrichment_status(profile_id, "skipped_policy", source=None, error=None)
        update_job_status(job_id, "completed")
        conn.close()
        return

    # Mark as processing in the queue
    update_job_status(job_id, "processing")

    # Run Aviato enrichment
    result = await enrich_profile_via_tools(profile_row, cursor)

    slug = result.get("slug")
    if slug:
        if result["status"] == "succeeded" and result["aviato_data"]:
            # Save raw JSON to staging
            json_path = save_aviato_raw_json(slug, result["aviato_data"])
            if json_path:
                print(f"  💾 Raw JSON saved to {json_path}")
            
            body_lines = ["**Source:** aviato_api", "", "**Aviato Professional Intelligence:**"]
            for k, v in result["aviato_data"].items():
                if isinstance(v, (str, int)) and v:
                    body_lines.append(f"- {k}: {v}")
            body = "\n".join(body_lines)
            _append_intel_log(slug, "aviato_enrichment", body)
        elif result["status"] in {"failed", "not_found"} and result["error"]:
            body = f"**Source:** aviato_api\n\n- Status: {result['status']}\n- Error: {result['error']}"
            _append_intel_log(slug, "aviato_enrichment_error", body)

        # Always try to append LinkedIn intelligence if metadata exists
        _append_linkedin_intel(slug)

    # Update DB status for job/profile
    if result["status"] == "succeeded":
        update_profile_enrichment_status(profile_id, "succeeded", source="aviato_api", error=None)
        update_job_status(job_id, "completed")
    elif result["status"] in {"failed", "not_found"}:
        update_profile_enrichment_status(profile_id, result["status"], source="aviato_api", error=result.get("error"))
        update_job_status(job_id, "failed", error_message=result.get("error") or "unknown error")

    conn.close()


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
        await process_enrichment_job(job, dry_run=dry_run)
        
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


def queue_profiles_from_meeting(meeting_folder: str) -> dict:
    """
    Queue CRM profiles for enrichment based on meeting stakeholders.
    
    Reads B03 from the meeting folder, extracts stakeholder names,
    finds matching CRM profiles, and queues them for enrichment.
    
    Returns summary dict with queued, skipped, not_found counts.
    """
    import re
    from pathlib import Path
    
    meeting_path = Path(meeting_folder)
    b03_path = meeting_path / "B03_STAKEHOLDER_INTELLIGENCE.md"
    
    result = {
        "meeting": meeting_path.name,
        "queued": [],
        "skipped": [],
        "not_found": [],
        "errors": []
    }
    
    if not b03_path.exists():
        result["errors"].append(f"B03 not found: {b03_path}")
        return result
    
    # Extract stakeholder names from B03
    b03_content = b03_path.read_text()
    
    # Match ### Name or ## Name patterns (excluding common headers)
    skip_headers = {'participants', 'group dynamics', 'stakeholder intelligence', 'meeting context'}
    stakeholder_pattern = re.compile(r'^#{2,3}\s+(.+?)(?:\s*\(|$)', re.MULTILINE)
    
    names = []
    for match in stakeholder_pattern.finditer(b03_content):
        name = match.group(1).strip()
        if name.lower() not in skip_headers and not name.startswith('B0'):
            names.append(name)
    
    if not names:
        result["errors"].append("No stakeholders found in B03")
        return result
    
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    for name in names:
        # Skip V
        if name.lower() in ['vrijen', 'vrijen attawar', 'v']:
            continue
        
        # Normalize name to slug pattern
        name_slug = name.lower().replace(' ', '_').replace('-', '_')
        name_parts = name.lower().split()
        
        # Search for matching profile by name
        c.execute("""
            SELECT id, email, enrichment_status, yaml_path 
            FROM profiles 
            WHERE LOWER(yaml_path) LIKE ? 
               OR LOWER(yaml_path) LIKE ?
            LIMIT 1
        """, (f"%{name_slug}%", f"%{'_'.join(name_parts)}%"))
        
        row = c.fetchone()
        
        if not row:
            result["not_found"].append(name)
            continue
        
        profile_id = row['id']
        enrichment_status = row['enrichment_status'] or ''
        
        # Skip if already enriched successfully
        if enrichment_status in ('succeeded', 'completed'):
            result["skipped"].append(f"{name} (already enriched)")
            continue
        
        # Check if already queued
        c.execute("""
            SELECT id FROM enrichment_queue 
            WHERE profile_id = ? AND status IN ('queued', 'processing')
        """, (profile_id,))
        
        if c.fetchone():
            result["skipped"].append(f"{name} (already in queue)")
            continue
        
        # Queue for enrichment
        c.execute("""
            INSERT INTO enrichment_queue 
            (profile_id, priority, scheduled_for, checkpoint, trigger_source, trigger_metadata)
            VALUES (?, 50, datetime('now'), 'checkpoint_1', 'meeting_sync', ?)
        """, (profile_id, json.dumps({
            "meeting": meeting_path.name,
            "stakeholder_name": name
        })))
        
        result["queued"].append(name)
    
    conn.commit()
    conn.close()
    
    return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='CRM V3 Enrichment Worker')
    parser.add_argument('--test', action='store_true', help='Test mode: Process one job and exit')
    parser.add_argument('--dry-run', action='store_true', help='Dry run: Show what would be processed')
    parser.add_argument('--create-test-job', action='store_true', help='Create a test enrichment job')
    parser.add_argument('--queue-from-meeting', type=str, metavar='FOLDER',
                        help='Queue profiles from meeting stakeholders for enrichment')
    parser.add_argument('--process-next', action='store_true', help='Process next queued job and exit')
    
    args = parser.parse_args()
    
    if args.queue_from_meeting:
        result = queue_profiles_from_meeting(args.queue_from_meeting)
        print(json.dumps(result, indent=2))
        return
    
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


























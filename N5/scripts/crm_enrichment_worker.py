#!/usr/bin/env python3
"""
CRM Enrichment Worker - Unified Database Version

Manages enrichment for people in the CRM using the unified n5_core.db database.

Updated 2026-01-19: Migrated from n5_core.db/people to n5_core.db/people table.

Features:
- Reads from n5_core.db/people table
- Delegates Aviato enrichment to enrichment.aviato_enricher
- Updates enrichment status in people table
- Appends Intelligence Log entries to markdown profiles

NOTE: Nyne integration removed 2026-01-11 due to rate limiting issues.
"""

import sys
import os
import asyncio
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')

# Import unified database paths
from N5.scripts.db_paths import (
    get_db_connection, 
    N5_CORE_DB,
    PEOPLE_TABLE,
    ORGANIZATIONS_TABLE
)

# Import enrichment tools
try:
    from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato
    AVIATO_AVAILABLE = True
except ImportError:
    AVIATO_AVAILABLE = False
    print("Warning: Aviato enricher not available", file=sys.stderr)

# Import stakeholder intel (optional)
try:
    from N5.scripts.stakeholder_intel import extract_linkedin_metadata, query_linkedin_conversation
    LINKEDIN_INTEL_AVAILABLE = True
except ImportError:
    LINKEDIN_INTEL_AVAILABLE = False

# Paths
WORKSPACE = Path("/home/workspace")
CRM_MARKDOWN_DIR = WORKSPACE / "Personal/Knowledge/CRM/individuals"
STAGING_DIR = WORKSPACE / "N5/data/staging/aviato"


def get_people_needing_enrichment(limit: int = 10) -> list:
    """
    Get people who need enrichment.
    
    Returns list of people without recent enrichment data.
    """
    conn = get_db_connection(readonly=True)
    cursor = conn.cursor()
    
    # Get people with email but missing linkedin data or not recently updated
    cursor.execute(f"""
        SELECT id, full_name, email, company, title, linkedin_url, markdown_path
        FROM {PEOPLE_TABLE}
        WHERE email IS NOT NULL
          AND status = 'active'
          AND (linkedin_url IS NULL OR linkedin_url = '')
        ORDER BY 
            CASE 
                WHEN category IN ('INVESTOR', 'CUSTOMER', 'FOUNDER') THEN 1
                WHEN category = 'ADVISOR' THEN 2
                ELSE 3
            END,
            created_at DESC
        LIMIT ?
    """, (limit,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def update_person_enrichment(person_id: int, data: dict, status: str = 'succeeded'):
    """
    Update person record with enrichment data.
    
    Args:
        person_id: ID of the person
        data: Enrichment data dict (from Aviato)
        status: 'succeeded', 'failed', 'not_found'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    # Map Aviato data to people table columns
    if data:
        if data.get('linkedin_url'):
            updates.append('linkedin_url = ?')
            params.append(data['linkedin_url'])
        
        if data.get('company') and not data.get('_skip_company'):
            updates.append('company = COALESCE(company, ?)')
            params.append(data['company'])
        
        if data.get('title') and not data.get('_skip_title'):
            updates.append('title = COALESCE(title, ?)')
            params.append(data['title'])
    
    # Always update timestamp
    updates.append('updated_at = CURRENT_TIMESTAMP')
    
    if updates:
        params.append(person_id)
        cursor.execute(f"""
            UPDATE {PEOPLE_TABLE}
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        conn.commit()
    
    conn.close()


def _append_intel_log(slug: str, heading: str, body: str) -> None:
    """Append intelligence log entry to markdown profile."""
    path = CRM_MARKDOWN_DIR / f"{slug}.md"
    
    if not path.exists():
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
    """Save raw Aviato response JSON to staging directory."""
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


def get_slug_from_email(email: str) -> str:
    """Generate a slug from email address."""
    if not email:
        return "unknown"
    return email.split('@')[0].lower().replace('.', '-').replace('+', '-')


async def enrich_person(person: dict) -> dict:
    """
    Enrich a single person using Aviato.
    
    Args:
        person: Dict with id, full_name, email, linkedin_url
        
    Returns:
        Dict with status, data, error
    """
    person_id = person['id']
    email = person.get('email')
    linkedin_url = person.get('linkedin_url')
    full_name = person.get('full_name', 'Unknown')
    
    print(f"  Enriching: {full_name} ({email})")
    
    if not AVIATO_AVAILABLE:
        return {
            'status': 'failed',
            'data': None,
            'error': 'Aviato enricher not available'
        }
    
    # Call Aviato
    try:
        aviato_result = await enrich_via_aviato(email, linkedin_url=linkedin_url)
    except Exception as e:
        return {
            'status': 'failed',
            'data': None,
            'error': str(e)
        }
    
    aviato_data = aviato_result.get('data') if aviato_result else None
    aviato_success = aviato_result.get('success', False) if aviato_result else False
    
    # Determine status
    if aviato_data:
        status = 'succeeded'
        error = None
        
        # Update the person record
        update_person_enrichment(person_id, aviato_data, status)
        
        # Save raw JSON
        slug = get_slug_from_email(email)
        json_path = save_aviato_raw_json(slug, aviato_data)
        if json_path:
            print(f"  💾 Aviato raw JSON saved to {json_path}")
        
        # Append to intel log
        body_lines = ["**Source:** aviato_api", "", "**Aviato Professional Intelligence:**"]
        for k, v in aviato_data.items():
            if isinstance(v, (str, int)) and v and not k.startswith('_'):
                body_lines.append(f"- {k}: {v}")
        _append_intel_log(slug, "aviato_enrichment", "\n".join(body_lines))
        
    elif aviato_success:
        status = 'not_found'
        error = None
    else:
        status = 'failed'
        error = aviato_result.get('error') if aviato_result else 'Unknown error'
    
    return {
        'status': status,
        'data': aviato_data,
        'error': error
    }


async def enrichment_worker_loop(test_mode: bool = False, dry_run: bool = False, limit: int = 5):
    """
    Main worker loop.
    
    Args:
        test_mode: Process one person and exit
        dry_run: Show what would be processed without processing
        limit: Maximum people to process per run
    """
    print("🚀 CRM Enrichment Worker Starting")
    print(f"   Mode: {'TEST' if test_mode else 'DRY-RUN' if dry_run else 'PRODUCTION'}")
    print(f"   DB: {N5_CORE_DB}")
    print(f"   Profiles: {CRM_MARKDOWN_DIR}")
    print()
    
    # Get people needing enrichment
    people = get_people_needing_enrichment(limit=limit if not test_mode else 1)
    
    if not people:
        print("✓ No people need enrichment")
        return
    
    print(f"Found {len(people)} people needing enrichment:")
    for p in people:
        print(f"  - {p['full_name']} ({p['email']})")
    print()
    
    if dry_run:
        print("DRY RUN - would process the above people")
        return
    
    # Process each person
    results = {'succeeded': 0, 'failed': 0, 'not_found': 0}
    
    for person in people:
        result = await enrich_person(person)
        results[result['status']] = results.get(result['status'], 0) + 1
        
        if result['status'] == 'succeeded':
            print(f"  ✓ {person['full_name']}: Enriched successfully")
        elif result['status'] == 'not_found':
            print(f"  ○ {person['full_name']}: No data found")
        else:
            print(f"  ✗ {person['full_name']}: {result.get('error', 'Unknown error')}")
        
        if test_mode:
            break
    
    print()
    print("Summary:")
    print(f"  Succeeded: {results['succeeded']}")
    print(f"  Not found: {results['not_found']}")
    print(f"  Failed: {results['failed']}")


def queue_from_meeting(meeting_path_str: str) -> dict:
    """
    Queue people from a meeting for enrichment.
    
    Reads stakeholders from meeting markdown and queues them.
    
    Args:
        meeting_path_str: Path to meeting folder
        
    Returns:
        Dict with queued, skipped, not_found lists
    """
    meeting_path = Path(meeting_path_str)
    
    # Find stakeholders.md
    stakeholders_path = meeting_path / "stakeholders.md"
    if not stakeholders_path.exists():
        # Try alternate path
        stakeholders_path = meeting_path / "Stakeholders.md"
        if not stakeholders_path.exists():
            return {"error": f"No stakeholders.md found in {meeting_path}"}
    
    # Parse stakeholder names
    text = stakeholders_path.read_text()
    names = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            name = line[2:].strip()
            # Remove any markdown links
            if '[' in name and ']' in name:
                name = name.split(']')[0].replace('[', '')
            if name:
                names.append(name)
    
    if not names:
        return {"error": "No stakeholders found in file"}
    
    result = {"queued": [], "skipped": [], "not_found": []}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for name in names:
        # Skip V
        if name.lower() in ['vrijen', 'vrijen attawar', 'v']:
            continue
        
        # Search for matching person by name
        cursor.execute(f"""
            SELECT id, full_name, email, linkedin_url
            FROM {PEOPLE_TABLE}
            WHERE full_name LIKE ?
            LIMIT 1
        """, (f"%{name}%",))
        
        row = cursor.fetchone()
        
        if not row:
            result["not_found"].append(name)
            continue
        
        # Skip if already has linkedin data
        if row['linkedin_url']:
            result["skipped"].append(f"{name} (already enriched)")
            continue
        
        result["queued"].append({
            'id': row['id'],
            'name': row['full_name'],
            'email': row['email']
        })
    
    conn.close()
    
    return result


def show_enrichment_stats():
    """Show enrichment statistics."""
    conn = get_db_connection(readonly=True)
    cursor = conn.cursor()
    
    # Total people
    cursor.execute(f"SELECT COUNT(*) FROM {PEOPLE_TABLE}")
    total = cursor.fetchone()[0]
    
    # With LinkedIn
    cursor.execute(f"""
        SELECT COUNT(*) FROM {PEOPLE_TABLE}
        WHERE linkedin_url IS NOT NULL AND linkedin_url != ''
    """)
    with_linkedin = cursor.fetchone()[0]
    
    # With email but no LinkedIn
    cursor.execute(f"""
        SELECT COUNT(*) FROM {PEOPLE_TABLE}
        WHERE email IS NOT NULL 
          AND (linkedin_url IS NULL OR linkedin_url = '')
    """)
    needs_enrichment = cursor.fetchone()[0]
    
    # By category needing enrichment
    cursor.execute(f"""
        SELECT category, COUNT(*) as count
        FROM {PEOPLE_TABLE}
        WHERE email IS NOT NULL 
          AND (linkedin_url IS NULL OR linkedin_url = '')
        GROUP BY category
        ORDER BY count DESC
    """)
    by_category = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("Enrichment Statistics")
    print("=" * 50)
    print(f"\nTotal people: {total}")
    print(f"With LinkedIn: {with_linkedin} ({100*with_linkedin/total:.1f}%)" if total > 0 else "With LinkedIn: 0")
    print(f"Needs enrichment: {needs_enrichment}")
    print("\nBy category (needs enrichment):")
    for row in by_category:
        cat = row['category'] or 'Uncategorized'
        print(f"  {cat}: {row['count']}")
    print()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='CRM Enrichment Worker (n5_core.db)')
    parser.add_argument('--test', action='store_true', help='Test mode: Process one person and exit')
    parser.add_argument('--dry-run', action='store_true', help='Dry run: Show what would be processed')
    parser.add_argument('--limit', type=int, default=5, help='Max people to process (default: 5)')
    parser.add_argument('--queue-from-meeting', type=str, metavar='FOLDER',
                        help='Queue people from meeting stakeholders for enrichment')
    parser.add_argument('--stats', action='store_true', help='Show enrichment statistics')
    
    args = parser.parse_args()
    
    if args.stats:
        show_enrichment_stats()
        return
    
    if args.queue_from_meeting:
        result = queue_from_meeting(args.queue_from_meeting)
        print(json.dumps(result, indent=2))
        return
    
    # Run worker loop
    asyncio.run(enrichment_worker_loop(
        test_mode=args.test,
        dry_run=args.dry_run,
        limit=args.limit
    ))


if __name__ == "__main__":
    main()

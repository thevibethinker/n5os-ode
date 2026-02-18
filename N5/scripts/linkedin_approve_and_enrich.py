#!/usr/bin/env python3
"""
LinkedIn Approve & Enrich Pipeline

Takes approved contacts from the LinkedIn review queue and:
1. Creates a CRM profile
2. Enriches with Aviato data
3. Links the LinkedIn conversation to the CRM profile

Usage:
  python3 linkedin_approve_and_enrich.py approve "David Speigel"
  python3 linkedin_approve_and_enrich.py approve-all   # Process all approved in queue
  python3 linkedin_approve_and_enrich.py batch-approve "Name1" "Name2" "Name3"

Version: 1.0.0
Created: 2025-12-10
"""

import sys
import os
import argparse
import asyncio
import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Add workspace to path
sys.path.insert(0, '/home/workspace')

# Paths
LINKEDIN_DB = Path('/home/workspace/Knowledge/linkedin/linkedin.db')
CRM_PROFILES_DIR = Path('/home/workspace/N5/crm_v3/profiles')
CRM_DB = Path('/home/workspace/N5/data/n5_core.db')

def slugify(name: str, email: str = None) -> str:
    """Create a CRM-compatible slug from name and optional email."""
    # Clean name
    clean_name = re.sub(r'[^\w\s]', '', name).strip()
    name_parts = clean_name.split()
    
    if len(name_parts) >= 2:
        slug_name = f"{name_parts[0]}_{name_parts[-1]}"
    else:
        slug_name = clean_name.replace(' ', '_')
    
    # Add email prefix if available
    if email:
        email_prefix = email.split('@')[0].lower()
        slug = f"{slug_name}_{email_prefix}"
    else:
        slug = slug_name.lower()
    
    return slug

def get_pending_approved(conn) -> list:
    """Get all contacts marked APPROVED but not yet processed."""
    cursor = conn.execute("""
        SELECT 
            rq.id,
            rq.conversation_id,
            rq.participant_name,
            rq.linkedin_url,
            rq.headline,
            rq.location,
            c.contact_headline,
            c.contact_location,
            c.contact_picture_url,
            c.connected_at,
            c.linkedin_profile_url,
            c.message_count,
            c.first_message_at,
            c.last_message_at
        FROM crm_review_queue rq
        JOIN conversations c ON rq.conversation_id = c.id
        WHERE rq.status = 'APPROVED'
    """)
    return cursor.fetchall()

def mark_processed(conn, queue_id: int, crm_slug: str):
    """Mark a queue item as processed and link to CRM."""
    conn.execute("""
        UPDATE crm_review_queue 
        SET status = 'PROCESSED', 
            reviewed_at = ?,
            notes = ?
        WHERE id = ?
    """, (int(datetime.now().timestamp() * 1000), f"CRM: {crm_slug}", queue_id))
    conn.commit()

def link_conversation_to_crm(conn, conversation_id: str, crm_slug: str):
    """Link a LinkedIn conversation to a CRM profile."""
    conn.execute("""
        UPDATE conversations 
        SET crm_profile_slug = ?
        WHERE id = ?
    """, (crm_slug, conversation_id))
    conn.commit()

def find_existing_profile(name: str, email: str = None) -> Path | None:
    """Find an existing CRM profile with the given name and email."""
    slug = slugify(name, email)
    filename = f"{slug}.yaml"
    filepath = CRM_PROFILES_DIR / filename
    
    if filepath.exists():
        logger.info(f"Profile already exists: {filepath}")
        return filepath
    else:
        return None

def create_crm_profile(
    name: str,
    linkedin_url: str = None,
    headline: str = None,
    location: str = None,
    picture_url: str = None,
    connected_at: int = None,
    email: str = None
) -> tuple[str, Path, bool]:
    """Create a new CRM profile YAML file.
    
    Returns: (slug, filepath, is_new)
    """
    slug = slugify(name, email)
    filename = f"{slug}.yaml"
    filepath = CRM_PROFILES_DIR / filename
    
    # Check for existing profile
    existing = find_existing_profile(name, email)
    if existing:
        logger.info(f"Found existing CRM profile: {existing}")
        return existing.stem, existing, True  # True = existing
    
    # Calculate relationship age if we have connected_at
    relationship_age = None
    if connected_at:
        connected_date = datetime.fromtimestamp(connected_at / 1000)
        days = (datetime.now() - connected_date).days
        if days < 30:
            relationship_age = f"{days} days"
        elif days < 365:
            relationship_age = f"{days // 30} months"
        else:
            relationship_age = f"{days // 365} years, {(days % 365) // 30} months"
    
    # Build profile content
    today = datetime.now().strftime('%Y-%m-%d')
    
    content = f"""---
created: {today}
last_edited: {today}
version: 1.0
source: linkedin_kondo
category: NETWORKING
relationship_strength: weak
---

# {name}

## Contact Information
"""
    
    if email:
        content += f"- **Email:** {email}\n"
    if linkedin_url:
        content += f"- **LinkedIn:** [{linkedin_url}]({linkedin_url})\n"
    if location:
        content += f"- **Location:** {location}\n"
    
    content += f"""
## Professional Summary
"""
    if headline:
        content += f"- **Headline:** {headline}\n"
    
    content += f"""
## LinkedIn Intelligence

### Connection Details
- **Source:** Kondo LinkedIn Sync
- **Added to CRM:** {today}
"""
    
    if connected_at:
        connected_date = datetime.fromtimestamp(connected_at / 1000)
        content += f"- **Connected on LinkedIn:** {connected_date.strftime('%Y-%m-%d')}\n"
        if relationship_age:
            content += f"- **Relationship Age:** {relationship_age}\n"
    
    if picture_url:
        content += f"- **Profile Picture:** [View]({picture_url})\n"
    
    content += """
## Intelligence Log

*Awaiting Aviato enrichment...*
"""
    
    # Write file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
    
    logger.info(f"Created CRM profile: {filepath}")
    return slug, filepath, False  # False = new

async def enrich_profile_with_aviato(slug: str, linkedin_url: str = None, name: str = None):
    """Enrich a CRM profile using Aviato API."""
    try:
        from N5.scripts.enrichment.aviato_enricher import enrich_via_aviato
        
        result = await enrich_via_aviato(
            email=None,  # We don't have email from LinkedIn
            name=name,
            linkedin_url=linkedin_url
        )
        
        if result.get('success') and result.get('markdown'):
            # Append to profile
            filepath = CRM_PROFILES_DIR / f"{slug}.yaml"
            if filepath.exists():
                content = filepath.read_text()
                
                # Replace the "Awaiting Aviato" placeholder
                if "*Awaiting Aviato enrichment...*" in content:
                    content = content.replace(
                        "*Awaiting Aviato enrichment...*",
                        result['markdown']
                    )
                else:
                    # Append to Intelligence Log
                    content += f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')} | aviato_enrichment\n"
                    content += result['markdown']
                
                filepath.write_text(content)
                logger.info(f"Enriched {slug} with Aviato data")
                return True, None
            else:
                return False, f"Profile file not found: {filepath}"
        else:
            error = result.get('error', 'Unknown error')
            logger.warning(f"Aviato enrichment failed for {slug}: {error}")
            return False, error
            
    except Exception as e:
        logger.error(f"Aviato enrichment error for {slug}: {e}")
        return False, str(e)

async def approve_contact(name: str, conn: sqlite3.Connection) -> tuple[bool, str]:
    """Approve a contact by name and process them."""
    # Find in queue - look for APPROVED status since review_queue.py already marked it
    cursor = conn.execute("""
        SELECT 
            rq.id,
            rq.conversation_id,
            rq.participant_name,
            rq.linkedin_url,
            rq.headline,
            rq.location,
            c.contact_headline,
            c.contact_location,
            c.contact_picture_url,
            c.connected_at,
            c.linkedin_profile_url
        FROM crm_review_queue rq
        JOIN conversations c ON rq.conversation_id = c.id
        WHERE rq.participant_name LIKE ? AND rq.status IN ('PENDING', 'APPROVED')
        LIMIT 1
    """, (f"%{name}%",))
    
    row = cursor.fetchone()
    if not row:
        return {"success": False, "error": f"No pending contact found matching '{name}'"}
    
    queue_id, conv_id, full_name, linkedin_url, headline, location, c_headline, c_location, picture_url, connected_at, profile_url = row
    
    # Use conversation data if queue data is missing
    headline = headline or c_headline
    location = location or c_location
    linkedin_url = linkedin_url or profile_url
    
    # Check for existing profile first
    existing = find_existing_profile(full_name, None)
    if existing:
        logger.info(f"Found existing CRM profile: {existing}")
        slug = existing.stem
        filepath = existing
        is_existing = True
    else:
        # Create new profile
        slug, filepath, is_existing = create_crm_profile(
            name=full_name,
            linkedin_url=linkedin_url,
            headline=headline,
            location=location,
            picture_url=picture_url,
            connected_at=connected_at
        )
    
    # Link conversation to CRM
    link_conversation_to_crm(conn, conv_id, slug)
    
    # Mark as processed
    mark_processed(conn, queue_id, slug)
    
    # Enrich with Aviato
    aviato_success, aviato_error = await enrich_profile_with_aviato(
        slug=slug,
        linkedin_url=linkedin_url,
        name=full_name
    )
    
    return {
        "success": True,
        "name": full_name,
        "slug": slug,
        "profile_path": str(filepath),
        "aviato_enriched": aviato_success,
        "aviato_error": aviato_error
    }

async def process_all_approved(conn) -> list:
    """Process all contacts marked as APPROVED."""
    approved = get_pending_approved(conn)
    results = []
    
    for row in approved:
        queue_id, conv_id, full_name, linkedin_url, headline, location, c_headline, c_location, picture_url, connected_at, profile_url, msg_count, first_msg, last_msg = row
        
        # Use conversation data if queue data is missing
        headline = headline or c_headline
        location = location or c_location
        linkedin_url = linkedin_url or profile_url
        
        # Check for existing profile first
        existing = find_existing_profile(full_name, None)
        if existing:
            logger.info(f"Found existing CRM profile: {existing}")
            slug = existing.stem
            filepath = existing
            is_existing = True
        else:
            # Create new profile
            slug, filepath, is_existing = create_crm_profile(
                name=full_name,
                linkedin_url=linkedin_url,
                headline=headline,
                location=location,
                picture_url=picture_url,
                connected_at=connected_at
            )
        
        # Link conversation to CRM
        link_conversation_to_crm(conn, conv_id, slug)
        
        # Mark as processed
        mark_processed(conn, queue_id, slug)
        
        # Enrich with Aviato
        aviato_success, aviato_error = await enrich_profile_with_aviato(
            slug=slug,
            linkedin_url=linkedin_url,
            name=full_name
        )
        
        results.append({
            "name": full_name,
            "slug": slug,
            "aviato_enriched": aviato_success,
            "aviato_error": aviato_error
        })
        
        print(f"  ✅ {full_name} → {slug}" + (" (+ Aviato)" if aviato_success else ""))
    
    return results

async def main():
    parser = argparse.ArgumentParser(description='LinkedIn Approve & Enrich Pipeline')
    parser.add_argument('command', choices=['approve', 'approve-all', 'batch-approve', 'status'],
                       help='Command to run')
    parser.add_argument('names', nargs='*', help='Name(s) to approve')
    
    args = parser.parse_args()
    
    conn = sqlite3.connect(LINKEDIN_DB)
    
    try:
        if args.command == 'approve':
            if not args.names:
                print("Error: Please provide a name to approve")
                return 1
            
            name = ' '.join(args.names)
            print(f"🔄 Approving: {name}")
            result = await approve_contact(name, conn)
            
            if result['success']:
                print(f"✅ Created: {result['profile_path']}")
                if result['aviato_enriched']:
                    print(f"✨ Aviato enrichment: Success")
                else:
                    print(f"⚠️  Aviato enrichment: {result.get('aviato_error', 'Failed')}")
            else:
                print(f"❌ {result['error']}")
                return 1
                
        elif args.command == 'batch-approve':
            if not args.names:
                print("Error: Please provide names to approve")
                return 1
            
            print(f"🔄 Batch approving {len(args.names)} contacts...")
            for name in args.names:
                result = await approve_contact(name, conn)
                if result['success']:
                    status = "✅" if result['aviato_enriched'] else "⚠️"
                    print(f"  {status} {result['name']} → {result['slug']}")
                else:
                    print(f"  ❌ {name}: {result['error']}")
                    
        elif args.command == 'approve-all':
            # First mark all PENDING as APPROVED
            cursor = conn.execute("SELECT COUNT(*) FROM crm_review_queue WHERE status = 'APPROVED'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("No contacts marked as APPROVED. Use:")
                print("  python3 N5/scripts/linkedin_review_queue.py approve \"Name\"")
                return 0
            
            print(f"🔄 Processing {count} approved contacts...")
            results = await process_all_approved(conn)
            
            success = sum(1 for r in results if r.get('aviato_enriched'))
            print(f"\n📈 Summary: {len(results)} profiles created, {success} enriched with Aviato")
            
        elif args.command == 'status':
            cursor = conn.execute("""
                SELECT status, COUNT(*) 
                FROM crm_review_queue 
                GROUP BY status
            """)
            print("📊 Review Queue Status:")
            for status, count in cursor.fetchall():
                print(f"  {status}: {count}")
                
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))




#!/usr/bin/env python3
"""
LinkedIn CRM Sync

Links LinkedIn conversations to existing CRM profiles.
Updates CRM profiles with LinkedIn activity.

Usage:
    linkedin_crm_sync.py [--auto] [--dry-run]

Version: 1.0.0
Created: 2025-10-30
"""

import sqlite3
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict
import json

WORKSPACE = Path('/home/workspace')
LINKEDIN_DB = WORKSPACE / 'Knowledge/linkedin/linkedin.db'
CRM_DB = WORKSPACE / 'Knowledge/crm/crm.db'
CRM_INDIVIDUALS = WORKSPACE / 'Knowledge/crm/individuals'

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def get_crm_profile_by_linkedin(linkedin_url: str) -> Optional[str]:
    """Find CRM profile slug by LinkedIn URL"""
    if not CRM_DB.exists():
        logger.warning("CRM database not found")
        return None
    
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, full_name, email, linkedin_url
        FROM individuals
        WHERE linkedin_url = ?
    """, (linkedin_url,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Generate slug from name
        slug = result['full_name'].lower().replace(' ', '-')
        return slug
    
    return None

def get_crm_profile_by_email(email: str) -> Optional[str]:
    """Find CRM profile slug by email"""
    if not CRM_DB.exists():
        return None
    
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, full_name, email
        FROM individuals
        WHERE email = ?
    """, (email,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        slug = result['full_name'].lower().replace(' ', '-')
        return slug
    
    return None

def sync_conversation_to_crm(conversation_id: str, participant_email: Optional[str], linkedin_url: Optional[str], dry_run: bool = False) -> bool:
    """Link a LinkedIn conversation to CRM profile if match found"""
    
    # Try to find CRM profile
    crm_slug = None
    
    if linkedin_url:
        crm_slug = get_crm_profile_by_linkedin(linkedin_url)
        if crm_slug:
            logger.info(f"  ✓ Matched by LinkedIn URL: {crm_slug}")
    
    if not crm_slug and participant_email:
        crm_slug = get_crm_profile_by_email(participant_email)
        if crm_slug:
            logger.info(f"  ✓ Matched by email: {crm_slug}")
    
    if not crm_slug:
        logger.info(f"  ✗ No CRM profile found")
        return False
    
    if dry_run:
        logger.info(f"  🧪 Would link to CRM profile: {crm_slug}")
        return True
    
    # Update LinkedIn conversation with CRM link
    conn = sqlite3.connect(LINKEDIN_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE conversations
        SET crm_profile_slug = ?
        WHERE id = ?
    """, (crm_slug, conversation_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"  ✅ Linked to CRM profile: {crm_slug}")
    return True

def sync_all_conversations(dry_run: bool = False):
    """Sync all unlinked conversations to CRM"""
    
    conn = sqlite3.connect(LINKEDIN_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get conversations without CRM links
    cursor.execute("""
        SELECT id, participant_name, participant_email, linkedin_profile_url
        FROM conversations
        WHERE crm_profile_slug IS NULL
        ORDER BY last_message_at DESC
    """)
    
    conversations = cursor.fetchall()
    conn.close()
    
    if not conversations:
        logger.info("✅ All conversations already linked to CRM (or no conversations yet)")
        return
    
    logger.info(f"🔗 Attempting to link {len(conversations)} conversation(s) to CRM\n")
    
    if dry_run:
        logger.info("🧪 DRY RUN - No changes will be made\n")
    
    linked = 0
    for conv in conversations:
        logger.info(f"Conversation: {conv['participant_name']} ({conv['id'][:8]}...)")
        
        if sync_conversation_to_crm(
            conv['id'],
            conv['participant_email'],
            conv['linkedin_profile_url'],
            dry_run
        ):
            linked += 1
        
        print()
    
    logger.info(f"📊 Summary: {linked}/{len(conversations)} conversations linked to CRM")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sync LinkedIn conversations to CRM profiles'
    )
    
    parser.add_argument('--auto', action='store_true',
                       help='Automatically link all unlinked conversations')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    if not LINKEDIN_DB.exists():
        logger.error(f"❌ LinkedIn database not found: {LINKEDIN_DB}")
        sys.exit(1)
    
    try:
        if args.auto:
            sync_all_conversations(args.dry_run)
        else:
            logger.info("Use --auto to sync all unlinked conversations")
            logger.info("Use --dry-run to preview changes")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

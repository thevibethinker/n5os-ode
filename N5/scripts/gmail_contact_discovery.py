#!/usr/bin/env python3
"""
Gmail Contact Discovery for CRM Enrichment

Scans Gmail sent folder to discover new contacts and queues for CRM enrichment.
"""

import sys
import os
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DB_PATH = '/home/workspace/N5/data/n5_core.db'
HELPERS_PATH = '/home/workspace/N5/scripts/crm_calendar_helpers.py'


def get_recipient_emails_from_gmail_response(emails_data):
    """
    Extract recipient emails from Gmail API response.
    
    Args:
        emails_data: List of email objects from gmail-find-email response
        
    Returns:
        Dict mapping email address to (name, subject, snippet)
    """
    recipients = {}
    
    for email in emails_data:
        try:
            # Extract To header
            headers = email.get('payload', {}).get('headers', [])
            to_header = None
            subject = None
            
            for header in headers:
                if header.get('name') == 'To':
                    to_header = header.get('value', '')
                if header.get('name') == 'Subject':
                    subject = header.get('value', '')
            
            if not to_header:
                continue
                
            # Parse "Name <email>" format
            # Support formats: "email@domain.com" or "Name <email@domain.com>"
            to_header = to_header.strip()
            if '<' in to_header and '>' in to_header:
                # "Name <email>" format
                email_addr = to_header[to_header.index('<')+1:to_header.index('>')]
                name = to_header[:to_header.index('<')].strip()
            else:
                # Just email
                email_addr = to_header
                name = ''
            
            email_addr = email_addr.strip().lower()
            
            # Filter spam/auto-replies
            snippet = email.get('snippet', '').lower()
            subject_lower = (subject or '').lower()
            
            spam_keywords = ['out of office', 'unsubscribe', 'autoreply', 'noreply', 'auto-reply']
            if any(keyword in subject_lower or keyword in snippet for keyword in spam_keywords):
                logger.info(f"Skipping spam/autoreply: {email_addr}")
                continue
            
            # Store recipient
            if email_addr:
                recipients[email_addr] = (name, subject or '')
                logger.debug(f"Found recipient: {email_addr} ({name})")
        
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            continue
    
    return recipients


def create_or_get_profile(email, name, source='gmail_sent'):
    """
    Create a new profile or get existing profile ID.
    Uses crm_calendar_helpers.get_or_create_profile.
    
    Args:
        email: Email address
        name: Contact name
        source: Source system (default: 'gmail_sent')
        
    Returns:
        profile_id (int) or None if error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if profile exists
        c.execute("SELECT id FROM profiles WHERE email = ?", (email.lower(),))
        result = c.fetchone()
        
        if result:
            profile_id = result[0]
            logger.debug(f"Found existing profile {profile_id} for {email}")
            conn.close()
            return profile_id
        
        # Create new profile
        # Generate YAML path: FirstName_LastName_emailprefix.yaml
        name_parts = name.strip().split() if name else ['User']
        first_name = name_parts[0] if name_parts else 'User'
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        email_prefix = email.split('@')[0] if '@' in email else email[:20]
        
        # Sanitize for filename
        first_clean = ''.join(c for c in first_name if c.isalnum() or c in ' -_')
        last_clean = ''.join(c for c in last_name if c.isalnum() or c in ' -_')
        prefix_clean = ''.join(c for c in email_prefix if c.isalnum() or c in '-_')
        
        if last_clean:
            yaml_filename = f"{first_clean}_{last_clean}_{prefix_clean}.yaml"
        else:
            yaml_filename = f"{prefix_clean}.yaml"
        
        yaml_path = f"N5/crm_v3/profiles/{yaml_filename}"
        full_yaml_path = f"/home/workspace/{yaml_path}"
        
        # Create stub YAML file
        os.makedirs(os.path.dirname(full_yaml_path), exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        stub_content = f"""---
created: {today}
last_edited: {today}
version: 1.0
source: {source}
email: {email}
category: NETWORKING
relationship_strength: weak
---

# {name}

## Contact Information
- **Email:** {email}
- **Organization:** To be determined

## Metadata
- **Sources:** {source}
- **Source Count:** 1
- **Total Meetings:** 0

## Notes

*Awaiting enrichment.*
"""
        
        with open(full_yaml_path, 'w') as f:
            f.write(stub_content)
        
        logger.debug(f"Created stub profile YAML at {yaml_path}")
        
        # Insert into database
        c.execute("""
            INSERT INTO profiles 
            (email, name, yaml_path, source, enrichment_status, profile_quality, category, relationship_strength)
            VALUES (?, ?, ?, ?, 'pending', 'stub', 'NETWORKING', 'weak')
        """, (email.lower(), name or email, yaml_path, source))
        
        profile_id = c.lastrowid
        conn.commit()
        logger.info(f"Created new profile {profile_id} for {email}")
        
        conn.close()
        return profile_id
        
    except Exception as e:
        logger.error(f"Failed to create/get profile for {email}: {e}")
        return None


def schedule_enrichment(profile_id, days_out=7, priority=25):
    """
    Schedule enrichment job for profile.
    
    Args:
        profile_id: Profile database ID
        days_out: Days until enrichment (default 7)
        priority: Priority 1-100 (default 25)
        
    Returns:
        job_id (int) or None if error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Calculate scheduled_for date
        scheduled_for = (datetime.utcnow() + timedelta(days=days_out)).isoformat()
        
        # Check for duplicate job
        c.execute("""
            SELECT id FROM enrichment_queue
            WHERE profile_id = ?
              AND checkpoint = 'checkpoint_1'
              AND status = 'queued'
        """, (profile_id,))
        
        result = c.fetchone()
        if result:
            job_id = result[0]
            logger.debug(f"Duplicate job found: {job_id} for profile {profile_id}")
            conn.close()
            return job_id
        
        # Create new enrichment job
        c.execute("""
            INSERT INTO enrichment_queue
            (profile_id, scheduled_for, checkpoint, priority, trigger_source, status)
            VALUES (?, ?, 'checkpoint_1', ?, 'gmail_sent', 'queued')
        """, (profile_id, scheduled_for, priority))
        
        job_id = c.lastrowid
        conn.commit()
        logger.info(f"Scheduled enrichment job {job_id} for profile {profile_id}")
        
        conn.close()
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to schedule enrichment for profile {profile_id}: {e}")
        return None


def main():
    """Main execution function."""
    logger.info("Starting Gmail contact discovery")
    
    # Email data from the Gmail find-email response (the 3 messages we found)
    # Extracted from the earlier API call response
    emails_data = [
        {
            'snippet': 'So sorry doc...',
            'payload': {
                'headers': [
                    {'name': 'To', 'value': 'Shirin Ali <shirinali@shirinalimd.com>'},
                    {'name': 'Subject', 'value': 'Re: Fwd: Meds clarification'}
                ]
            }
        },
        {
            'snippet': "Hi Dr Ali -- I don't know what the hell happened...",
            'payload': {
                'headers': [
                    {'name': 'To', 'value': 'PreAsia Cooper <preasia@shirinalimd.com>'},
                    {'name': 'Subject', 'value': 'Re: Fwd: Meds clarification'}
                ]
            }
        },
        {
            'snippet': 'How do I stop? You stop!',
            'payload': {
                'headers': [
                    {'name': 'To', 'value': 'Zo Computer <va@zo.computer>'},
                    {'name': 'Subject', 'value': 'Re: Stop'}
                ]
            }
        }
    ]
    
    # Extract recipient emails
    recipients = get_recipient_emails_from_gmail_response(emails_data)
    logger.info(f"Found {len(recipients)} unique recipients from sent emails")
    
    # Process each recipient
    profiles_created = 0
    jobs_scheduled = 0
    
    for email, (name, subject) in recipients.items():
        logger.info(f"Processing recipient: {email} ({name})")
        
        # Skip internal/no-reply addresses
        if 'noreply' in email.lower() or 'no-reply' in email.lower():
            logger.info(f"Skipping no-reply address: {email}")
            continue
        
        # Create or get profile
        profile_id = create_or_get_profile(email, name, source='gmail_sent')
        
        if profile_id:
            # Schedule enrichment
            job_id = schedule_enrichment(profile_id, days_out=7, priority=25)
            if job_id:
                jobs_scheduled += 1
                profiles_created += 1  # This is either new or existing
        else:
            logger.error(f"Failed to create profile for {email}")
    
    # Summary
    logger.info(f"=== SUMMARY ===")
    logger.info(f"Total recipients processed: {len(recipients)}")
    logger.info(f"Profiles created/found: {profiles_created}")
    logger.info(f"Enrichment jobs scheduled: {jobs_scheduled}")
    
    return {
        'total_recipients': len(recipients),
        'profiles_created': profiles_created,
        'jobs_scheduled': jobs_scheduled,
        'success': True
    }


if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2))


#!/usr/bin/env python3
"""
Gmail Contact Discovery for CRM
Scans sent emails to discover new contacts and queue for enrichment.

Prerequisites:
- Gmail API configured (use_app_gmail already called in Zo workflow)
- Database: N5/data/n5_core.db
- Helper functions in N5/scripts/crm_calendar_helpers.py
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
import pytz
import sqlite3
import logging

# Add N5 scripts to path for imports
sys.path.insert(0, '/home/workspace/N5/scripts')

from crm_calendar_helpers import (
    get_or_create_profile,
    schedule_enrichment_job,
    get_db_connection,
    setup_logging
)

# Configure logging
log_file = '/home/workspace/N5/logs/gmail_contact_scan.log'
logger = setup_logging(log_file)

# Spam keywords to filter
SPAM_KEYWORDS = ['out of office', 'unsubscribe', 'autoreply', 'noreply']

def extract_emails_from_text(text):
    """Extract email addresses from text."""
    if not text:
        return []
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def is_spam_email(subject, snippet):
    """Check if email looks like spam/automation."""
    combined = (subject or '') + ' ' + (snippet or '')
    combined_lower = combined.lower()
    
    for keyword in SPAM_KEYWORDS:
        if keyword in combined_lower:
            return True
    return False

def extract_to_recipients(headers_dict):
    """Extract To field from email headers."""
    if not headers_dict:
        return []
    
    # Try different header names (case variations)
    to_field = (headers_dict.get('To') or 
                headers_dict.get('to') or
                headers_dict.get('To:') or
                '')
    
    if not to_field:
        return []
    
    # Split by comma and extract emails
    recipients = []
    for part in to_field.split(','):
        part = part.strip()
        emails = extract_emails_from_text(part)
        recipients.extend(emails)
    
    return recipients

def process_gmail_results(gmail_response):
    """
    Process Gmail API response to extract recipient emails.
    
    Args:
        gmail_response: Response object from Gmail API
        
    Returns:
        list: List of extracted emails
    """
    all_recipients = []
    
    if not gmail_response or 'ret' not in gmail_response:
        logger.warning("No results in Gmail response")
        return all_recipients
    
    messages = gmail_response.get('ret', [])
    logger.info(f"Processing {len(messages)} emails from Gmail")
    
    for msg in messages:
        try:
            # Extract basic info
            subject = msg.get('subject', '')
            snippet = msg.get('snippet', '')
            
            # Check for spam/automation
            if is_spam_email(subject, snippet):
                logger.debug(f"Skipping spam email: {subject}")
                continue
            
            # Extract header information
            headers = msg.get('payload', {}).get('headers', [])
            headers_dict = {}
            
            for header in headers:
                name = header.get('name', '')
                value = header.get('value', '')
                headers_dict[name] = value
            
            # Extract To recipients
            recipients = extract_to_recipients(headers_dict)
            
            for recipient in recipients:
                if recipient and '@' in recipient:
                    all_recipients.append(recipient.lower())
                    logger.debug(f"Found recipient: {recipient}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            continue
    
    return all_recipients

def process_gmail_json_file(json_file_path):
    """
    Load and process Gmail response from JSON file (for testing/replay).
    
    Args:
        json_file_path: Path to JSON file with Gmail response
        
    Returns:
        list: List of extracted emails
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return process_gmail_results(data)
    except Exception as e:
        logger.error(f"Error loading JSON file {json_file_path}: {e}")
        return []

def queue_new_contacts_for_enrichment(recipient_emails):
    """
    For each recipient email, check if profile exists.
    If new, create profile and schedule enrichment.
    
    Args:
        recipient_emails: List of email addresses
        
    Returns:
        dict: Summary of created profiles and scheduled jobs
    """
    summary = {
        'total_recipients': len(recipient_emails),
        'new_profiles': 0,
        'existing_profiles': 0,
        'enrichment_jobs': 0,
        'errors': 0
    }
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get unique recipients
    unique_emails = set(recipient_emails)
    logger.info(f"Processing {len(unique_emails)} unique recipient emails")
    
    for email in unique_emails:
        try:
            # Check if profile already exists
            c.execute("SELECT id FROM profiles WHERE email = ?", (email,))
            existing = c.fetchone()
            
            if existing:
                summary['existing_profiles'] += 1
                logger.debug(f"Profile already exists: {email}")
                continue
            
            # Create new profile
            name = email.split('@')[0].title()  # Use email prefix as name
            profile_id = get_or_create_profile(email, name, source='gmail_sent')
            summary['new_profiles'] += 1
            
            # Schedule enrichment job
            # 7 days from now, checkpoint_1 (priority 25)
            scheduled_for = (datetime.now(pytz.UTC) + timedelta(days=7)).isoformat()
            
            job_id = schedule_enrichment_job(
                profile_id=profile_id,
                scheduled_for=scheduled_for,
                checkpoint='checkpoint_1',
                priority=25,
                trigger_source='gmail_reply',
                trigger_metadata=json.dumps({'email': email})
            )
            
            summary['enrichment_jobs'] += 1
            logger.info(f"Created profile {profile_id} and scheduled job {job_id} for {email}")
        
        except Exception as e:
            summary['errors'] += 1
            logger.error(f"Error processing {email}: {e}")
            continue
    
    conn.close()
    return summary

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("Gmail Contact Discovery Job Started")
    logger.info("=" * 70)
    
    # Calculate search date
    et = pytz.timezone('America/New_York')
    yesterday = datetime.now(et) - timedelta(days=1)
    search_date_str = yesterday.strftime('%Y/%m/%d')
    
    logger.info(f"Searching for emails after: {search_date_str}")
    
    # Check if we have a test JSON file to process (for this scheduled run)
    test_gmail_json = '/tmp/gmail_response.json'
    
    if os.path.exists(test_gmail_json):
        logger.info(f"Using test Gmail response from {test_gmail_json}")
        recipient_emails = process_gmail_json_file(test_gmail_json)
    else:
        logger.warning("No Gmail response found - this would be called from Zo's use_app_gmail")
        logger.info("In actual workflow, Gmail results would be passed to this script")
        # For now, return empty results
        recipient_emails = []
    
    if not recipient_emails:
        logger.warning("No recipient emails found")
        summary = {
            'total_recipients': 0,
            'new_profiles': 0,
            'existing_profiles': 0,
            'enrichment_jobs': 0,
            'errors': 0
        }
    else:
        # Process and queue for enrichment
        summary = queue_new_contacts_for_enrichment(recipient_emails)
    
    # Log summary
    logger.info("=" * 70)
    logger.info("Job Summary:")
    logger.info(f"  Total recipients found: {summary['total_recipients']}")
    logger.info(f"  New profiles created: {summary['new_profiles']}")
    logger.info(f"  Existing profiles: {summary['existing_profiles']}")
    logger.info(f"  Enrichment jobs scheduled: {summary['enrichment_jobs']}")
    logger.info(f"  Errors: {summary['errors']}")
    logger.info("=" * 70)
    
    # Print summary to stdout
    print(json.dumps(summary, indent=2))
    
    return 0 if summary['errors'] == 0 else 1

if __name__ == '__main__':
    exit(main())


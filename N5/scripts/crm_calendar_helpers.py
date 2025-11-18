#!/usr/bin/env python3
"""
CRM Calendar Webhook Helpers
Shared utilities for Google Calendar webhook integration

Provides common functionality used by:
- crm_calendar_webhook_setup.py
- crm_calendar_webhook_handler.py
- crm_calendar_webhook_renewal.py
- crm_calendar_health_monitor.py
"""

import os
import sys
import yaml
import uuid
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# Google imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: Google API libraries not available", file=sys.stderr)

# Configuration
CONFIG_PATH = '/home/workspace/N5/config/calendar_webhook.yaml'
CREDENTIALS_PATH = '/home/workspace/N5/config/credentials/google_service_account.json'
DB_PATH = '/home/workspace/N5/data/crm_v3.db'
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']
WEBHOOK_METADATA_PATH = '/home/workspace/N5/data/webhook_metadata.json'

# Initialize logger
logger = logging.getLogger(__name__)


def load_config(config_path: str = CONFIG_PATH) -> dict:
    """Load webhook configuration from YAML file
    
    Args:
        config_path: Path to config file (default: N5/config/calendar_webhook.yaml)
        
    Returns:
        dict: Parsed configuration
    """
    if not os.path.exists(config_path):
        # Return default config if file doesn't exist
        return {
            'webhook': {
                'endpoint': 'https://va.zo.computer/webhooks/calendar'
            },
            'enrichment': {
                'checkpoint_1_days_before': 3,
                'checkpoint_1_priority': 75,
                'checkpoint_2_hour': 7,
                'checkpoint_2_priority': 100
            },
            'renewal': {
                'check_interval_hours': 24,
                'renew_threshold_days': 2,
                'retry_delay_seconds': 3600
            },
            'health': {
                'check_interval_hours': 1,
                'alert_on_errors_count': 5,
                'alert_on_no_notifications_hours': 24
            },
            'google': {
                'calendar_id': 'primary',
                'max_expiration_days': 7
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_google_credentials():
    """
    Load Google service account credentials from JSON file.
    
    Returns:
        dict: Parsed service account credentials
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        json.JSONDecodeError: If credentials file is invalid JSON
    """
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Credentials not found: {CREDENTIALS_PATH}")
    
    with open(CREDENTIALS_PATH, 'r') as f:
        credentials = json.load(f)
    
    return credentials


def generate_unique_channel_id():
    """
    Generate unique channel ID for webhook registration.
    
    Returns:
        str: Channel ID (UUID format)
    """
    return str(uuid.uuid4())


def calculate_expiration_ms(days=None):
    """
    Calculate webhook expiration timestamp in milliseconds.
    
    Args:
        days (int, optional): Days until expiration (default: 7, max: 7)
        
    Returns:
        int: Expiration timestamp in milliseconds
    """
    if days is None:
        config = load_config()
        days = config.get('google', {}).get('max_expiration_days', 7)
    
    # Max is 7 days per Google Calendar API
    days = min(days, 7)
    
    expiration = datetime.utcnow() + timedelta(days=days)
    return int(expiration.timestamp() * 1000)


def store_webhook_metadata(metadata):
    """
    Store webhook metadata to JSON file.
    
    Args:
        metadata (dict): Webhook metadata from Google API response
    """
    os.makedirs(os.path.dirname(WEBHOOK_METADATA_PATH), exist_ok=True)
    
    with open(WEBHOOK_METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.debug(f"Stored webhook metadata to {WEBHOOK_METADATA_PATH}")


def load_webhook_metadata():
    """
    Load webhook metadata from JSON file.
    
    Returns:
        dict: Webhook metadata
        
    Raises:
        FileNotFoundError: If metadata file doesn't exist
    """
    if not os.path.exists(WEBHOOK_METADATA_PATH):
        raise FileNotFoundError(f"Webhook metadata not found: {WEBHOOK_METADATA_PATH}")
    
    with open(WEBHOOK_METADATA_PATH, 'r') as f:
        return json.load(f)


def update_webhook_health(channel_id=None, resource_id=None, 
                         expiration_ms=None, last_received_at=None):
    """
    Update or create webhook health record in database.
    
    Args:
        channel_id (str): Channel ID from Google
        resource_id (str): Resource ID from Google
        expiration_ms (int): Expiration timestamp in milliseconds
        last_received_at (datetime): Last notification received time
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if record exists
        c.execute("""
            SELECT id FROM webhook_health
            WHERE service = 'google_calendar'
        """)
        result = c.fetchone()
        
        if result:
            # Update existing
            c.execute("""
                UPDATE webhook_health
                SET 
                    channel_id = COALESCE(?, channel_id),
                    resource_id = COALESCE(?, resource_id),
                    expiration_time = COALESCE(?, expiration_time),
                    last_received_at = COALESCE(?, last_received_at),
                    last_renewal_at = datetime('now'),
                    status = 'ACTIVE'
                WHERE service = 'google_calendar'
            """, (channel_id, resource_id, expiration_ms, last_received_at))
        else:
            # Insert new
            c.execute("""
                INSERT INTO webhook_health
                (service, channel_id, resource_id, expiration_time, 
                 last_received_at, last_renewal_at, status)
                VALUES ('google_calendar', ?, ?, ?, ?, datetime('now'), 'ACTIVE')
            """, (channel_id, resource_id, expiration_ms, last_received_at))
        
        conn.commit()
        logger.debug("Updated webhook health record")
        
    except Exception as e:
        logger.error(f"Failed to update webhook health: {e}")
        raise
    finally:
        conn.close()


def validate_webhook_endpoint(url):
    """
    Validate that webhook endpoint is accessible.
    
    Args:
        url (str): Webhook endpoint URL
        
    Returns:
        bool: True if endpoint is accessible, False otherwise
    """
    try:
        parsed = urlparse(url)
        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Try to access the webhook endpoint
        import requests
        response = requests.get(test_url, timeout=10, allow_redirects=False)
        
        # 405 Method Not Allowed is actually a good sign (means endpoint exists)
        if response.status_code == 405 or response.status_code == 404:
            logger.info(f"Webhook endpoint accessible: {test_url}")
            return True
        elif response.status_code >= 200 and response.status_code < 400:
            logger.info(f"Webhook endpoint accessible: {test_url}")
            return True
        else:
            logger.warning(f"Webhook endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"Could not validate webhook endpoint: {e}")
        return False


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


def send_sms_alert(message):
    """
    Send SMS alert to user.
    
    Args:
        message (str): Alert message
    """
    try:
        # Use the send_sms_to_user tool
        sys.path.append('/home/workspace')
        from scripts import send_sms_to_user
        send_sms_to_user(message=message)
        logger.info(f"SMS alert sent: {message[:50]}...")
    except Exception as e:
        logger.error(f"Failed to send SMS alert: {e}")
        # Don't raise - failures to send alerts shouldn't crash the system
        return False
    return True


def setup_logging(log_file: str):
    """Setup logging to specified file"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def display_instructions():
    """Display startup instructions"""
    print("=" * 70)
    print("CRM Calendar Webhook Component")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  • Config: {CONFIG_PATH}")
    print(f"  • Credentials: {CREDENTIALS_PATH}")
    print(f"  • Database: {DB_PATH}")
    print()
    print("Monitoring:")
    print("  • Check logs in /dev/shm/crm-*.log")
    print("  • Monitor service status at https://va.zo.computer/system")
    print()


def get_or_create_profile(email: str, name: str, source: str = 'calendar') -> int:
    """
    Get existing profile or create new one.
    
    Args:
        email: Contact email address
        name: Contact name
        source: Source system (default: 'calendar')
        
    Returns:
        int: profile_id
        
    Behavior:
        1. Query profiles table for existing email
        2. If found, return existing profile_id
        3. If not found:
           a. Generate yaml_path (N5/crm_v3/profiles/{Name}_{email_prefix}.yaml)
           b. Create stub YAML file with frontmatter
           c. INSERT INTO profiles
           d. Return new profile_id
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check for existing profile
        c.execute("SELECT id FROM profiles WHERE email = ?", (email,))
        result = c.fetchone()
        
        if result:
            profile_id = result[0]
            logger.debug(f"Found existing profile {profile_id} for {email}")
            return profile_id
        
        # Create new profile
        # Generate YAML path: FirstName_LastName_emailprefix.yaml
        name_parts = name.strip().split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        email_prefix = email.split('@')[0] if '@' in email else email[:20]
        
        # Sanitize filename parts
        first_clean = "".join(c for c in first_name if c.isalnum() or c in " -_")
        last_clean = "".join(c for c in last_name if c.isalnum() or c in " -_")
        prefix_clean = "".join(c for c in email_prefix if c.isalnum() or c in "-_")
        
        if last_clean:
            yaml_filename = f"{first_clean}_{last_clean}_{prefix_clean}.yaml"
        else:
            yaml_filename = f"{first_clean}_{prefix_clean}.yaml"
        
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
            (email, name, yaml_path, source, enrichment_status, profile_quality)
            VALUES (?, ?, ?, ?, 'pending', 'stub')
        """, (email, name, yaml_path, source))
        
        profile_id = c.lastrowid
        conn.commit()
        
        logger.info(f"Created new profile {profile_id} for {email}")
        return profile_id
        
    except Exception as e:
        logger.error(f"Failed to get/create profile for {email}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def schedule_enrichment_job(
    profile_id: int,
    scheduled_for: str,
    checkpoint: str,
    priority: int,
    trigger_source: str,
    trigger_metadata: str = None
) -> int:
    """
    Queue enrichment job for profile.
    
    Args:
        profile_id: Profile database ID
        scheduled_for: ISO datetime string (when to process)
        checkpoint: 'checkpoint_1' or 'checkpoint_2'
        priority: 1-100 (higher = sooner, 75 for checkpoint_1, 100 for checkpoint_2)
        trigger_source: 'calendar' | 'gmail' | 'manual'
        trigger_metadata: JSON string with additional context (optional)
        
    Returns:
        int: job_id (enrichment_queue.id)
        
    Behavior:
        1. Check if duplicate job exists (same profile_id, checkpoint, status='queued')
        2. If duplicate exists, return existing job_id (don't create duplicate)
        3. If no duplicate, INSERT new job and return job_id
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check for duplicate job
        c.execute("""
            SELECT id FROM enrichment_queue
            WHERE profile_id = ?
              AND checkpoint = ?
              AND status = 'queued'
        """, (profile_id, checkpoint))
        
        result = c.fetchone()
        
        if result:
            job_id = result[0]
            logger.debug(f"Duplicate job found: {job_id} for profile {profile_id}, checkpoint {checkpoint}")
            return job_id
        
        # Create new job
        c.execute("""
            INSERT INTO enrichment_queue
            (profile_id, scheduled_for, checkpoint, priority, trigger_source, trigger_metadata, status)
            VALUES (?, ?, ?, ?, ?, ?, 'queued')
        """, (profile_id, scheduled_for, checkpoint, priority, trigger_source, trigger_metadata))
        
        job_id = c.lastrowid
        conn.commit()
        
        logger.info(f"Scheduled enrichment job {job_id} for profile {profile_id}, checkpoint {checkpoint}")
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to schedule enrichment job for profile {profile_id}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def extract_event_id_from_uri(resource_uri: str) -> str:
    """
    Extract event ID from Google Calendar resource URI.
    
    Args:
        resource_uri: Full Google Calendar resource URI
                     (e.g., https://www.googleapis.com/calendar/v3/calendars/primary/events/abc123)
    
    Returns:
        str: Event ID extracted from URI
        
    Example:
        >>> extract_event_id_from_uri("https://www.googleapis.com/calendar/v3/calendars/primary/events/abc123")
        "abc123"
    """
    # Resource URI format: https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events/{eventId}
    parts = resource_uri.rstrip('/').split('/')
    if len(parts) >= 2 and 'events' in parts:
        # Get the part after 'events'
        events_idx = parts.index('events')
        if events_idx + 1 < len(parts):
            return parts[events_idx + 1]
    
    # Fallback: return last segment
    return parts[-1] if parts else resource_uri



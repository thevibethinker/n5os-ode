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

# Add workspace to path for N5 lib imports
sys.path.insert(0, '/home/workspace')
from N5.lib.db import get_crm_db, crm_transaction
from N5.lib.paths import CRM_DB
from crm_identity_resolver import CRMIdentityResolver
from crm_semantic_memory import sync_person_to_semantic_memory

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
DB_PATH = str(CRM_DB)  # Use centralized path
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']
WEBHOOK_METADATA_PATH = '/home/workspace/N5/data/webhook_metadata.json'

# Initialize logger
logger = logging.getLogger(__name__)
_identity_resolver = CRMIdentityResolver(auto_link_threshold=0.99)


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


def ensure_runtime_tables():
    """
    Ensure runtime tables exist in the CRM database.
    """
    with crm_transaction() as conn:
        c = conn.cursor()

        # Create webhook_health table if not exists
        c.execute("""
            CREATE TABLE IF NOT EXISTS webhook_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL UNIQUE,
                channel_id TEXT,
                resource_id TEXT,
                expiration_time INTEGER,
                last_received_at TEXT,
                last_renewal_at TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        """)

        # Create crm_enrichment_queue table if not exists
        c.execute("""
            CREATE TABLE IF NOT EXISTS crm_enrichment_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                scheduled_for TEXT NOT NULL,
                checkpoint TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 50,
                trigger_source TEXT,
                trigger_metadata TEXT,
                status TEXT NOT NULL DEFAULT 'queued',
                attempt_count INTEGER NOT NULL DEFAULT 0,
                last_attempt_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_crm_enrich_queue_status_sched
            ON crm_enrichment_queue (status, scheduled_for)
        """)
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_crm_enrich_queue_person_checkpoint
            ON crm_enrichment_queue (person_id, checkpoint)
        """)


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
    ensure_runtime_tables()
    with crm_transaction() as conn:
        c = conn.cursor()

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

        logger.debug("Updated webhook health record")


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
    """Get database connection (pooled - connection is reused)"""
    return get_crm_db()


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
    """Get existing person or create one in canonical n5_core people table."""
    email_norm = (email or '').strip().lower()
    if not email_norm:
        raise ValueError('email is required')

    resolved = _identity_resolver.auto_link(name=name, email=email_norm)
    if resolved.person_id is not None:
        person_id = int(resolved.person_id)
        sync_person_to_semantic_memory(
            person_id,
            trigger="calendar_identity_resolved",
            metadata={"source": source, "email": email_norm},
        )
        return person_id

    conn = get_crm_db()
    c = conn.cursor()
    c.execute("SELECT id FROM people WHERE lower(email) = ?", (email_norm,))
    result = c.fetchone()
    if result:
        person_id = int(result[0])
        logger.debug(f"Found existing person {person_id} for {email_norm}")
        sync_person_to_semantic_memory(
            person_id,
            trigger="calendar_identity_existing",
            metadata={"source": source, "email": email_norm},
        )
        return person_id

    base_name = (name or '').strip()
    if not base_name:
        base_name = email_norm.split('@')[0].replace('.', ' ').replace('_', ' ').title()

    slug_seed = base_name or email_norm.split('@')[0]
    slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in slug_seed)
    slug = '-'.join(part for part in slug.split('-') if part) or 'unknown-person'
    markdown_path = f"Personal/Knowledge/CRM/individuals/{slug}.md"

    with crm_transaction() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM people WHERE lower(email) = ?", (email_norm,))
        result = c.fetchone()
        if result:
            return int(result[0])

        c.execute(
            """
            INSERT INTO people (full_name, email, status, source_db, source_id, markdown_path)
            VALUES (?, ?, 'active', 'calendar_webhook', ?, ?)
            """,
            (base_name, email_norm, source, markdown_path),
        )
        person_id = int(c.lastrowid)
        logger.info(f"Created person {person_id} for {email_norm}")
        sync_person_to_semantic_memory(
            person_id,
            trigger="calendar_identity_created",
            metadata={"source": source, "email": email_norm, "name": base_name},
        )
        return person_id


def schedule_enrichment_job(
    profile_id: int,
    scheduled_for: str,
    checkpoint: str,
    priority: int,
    trigger_source: str,
    trigger_metadata: str = None
) -> int:
    """Queue enrichment job in canonical crm_enrichment_queue table."""
    ensure_runtime_tables()

    conn = get_crm_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT id FROM crm_enrichment_queue
        WHERE person_id = ? AND checkpoint = ? AND status = 'queued'
        """,
        (profile_id, checkpoint),
    )
    result = c.fetchone()
    if result:
        job_id = int(result[0])
        logger.debug(
            f"Duplicate job found: {job_id} for person {profile_id}, checkpoint {checkpoint}"
        )
        return job_id

    with crm_transaction() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT id FROM crm_enrichment_queue
            WHERE person_id = ? AND checkpoint = ? AND status = 'queued'
            """,
            (profile_id, checkpoint),
        )
        result = c.fetchone()
        if result:
            return int(result[0])

        c.execute(
            """
            INSERT INTO crm_enrichment_queue
            (person_id, scheduled_for, checkpoint, priority, trigger_source, trigger_metadata, status)
            VALUES (?, ?, ?, ?, ?, ?, 'queued')
            """,
            (profile_id, scheduled_for, checkpoint, priority, trigger_source, trigger_metadata),
        )
        job_id = int(c.lastrowid)
        logger.info(
            f"Scheduled enrichment job {job_id} for person {profile_id}, checkpoint {checkpoint}"
        )
        return job_id


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


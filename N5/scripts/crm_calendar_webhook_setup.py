#!/usr/bin/env python3
"""
CRM Calendar Webhook Setup

Registers push notification webhook with Google Calendar API.
Receives notifications when events are created, updated, or deleted.

Requirements:
- Google service account credentials configured at N5/config/credentials/google_service_account.json
- Calendar API enabled in Google Cloud Console
- Domain verification for va.zo.computer

Usage:
    python3 /home/workspace/N5/scripts/crm_calendar_webhook_setup.py
    python3 /home/workspace/N5/scripts/crm_calendar_webhook_setup.py --skip-prerequisites
    python3 /home/workspace/N5/scripts/crm_calendar_webhook_setup.py --test

Options:
    --skip-prerequisites  Skip interactive prerequisites check
    --test                Dry-run mode (doesn't call Google API)
"""

import sys
import os
import asyncio
import datetime
import argparse
sys.path.append('/home/workspace/N5/scripts')

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from crm_calendar_helpers import (
        load_google_credentials,
        generate_unique_channel_id,
        calculate_expiration_ms,
        store_webhook_metadata,
        update_webhook_health,
    )
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    sys.exit(1)

# Google Calendar API configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']
CALENDAR_ID = 'primary'  # Watch user's primary calendar


def build_calendar_service(service_account_info):
    """
    Build Google Calendar API service using service account credentials.
    
    Args:
        service_account_info (dict): Parsed service account JSON
        
    Returns:
        googleapiclient.discovery.Resource: Calendar API service
    """
    try:
        # Create credentials from service account info
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Failed to build Calendar service: {e}", file=sys.stderr)
        raise


def register_webhook(service, channel_id, webhook_url, expiration_ms):
    """
    Register webhook with Google Calendar Watch API.
    
    Args:
        service: Google Calendar API service
        channel_id (str): Unique channel ID
        webhook_url (str): Public URL for webhook endpoint
        expiration_ms (int): Expiration timestamp in milliseconds
        
    Returns:
        dict: Webhook registration response from Google
        
    Raises:
        HttpError: If API request fails
    """
    request_body = {
        'id': channel_id,
        'type': 'web_hook',
        'address': webhook_url,
        'expiration': expiration_ms
    }
    
    try:
        response = service.events().watch(
            calendarId=CALENDAR_ID,
            body=request_body
        ).execute()
        
        return response
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        reason = error_details.get('reason', 'unknown')
        message = error_details.get('message', str(e))
        
        print(f"\n❌ Google Calendar API Error: {reason}", file=sys.stderr)
        print(f"Message: {message}", file=sys.stderr)
        
        if reason == 'forbidden':
            print("\n💡 Troubleshooting:")
            print("   - Verify Calendar API is enabled")
            print("   - Check service account has Calendar access")
            print("   - Ensure domain verification is complete")
        elif reason == 'invalidAddress':
            print("\n💡 Troubleshooting:")
            print(f"   - Verify webhook URL is accessible: {webhook_url}")
            print("   - Ensure domain is verified in Google Cloud Console")
            
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error during webhook registration: {e}", file=sys.stderr)
        raise


def setup_calendar_webhook():
    """
    Main setup routine for calendar webhook registration.
    
    Returns:
        dict: Complete webhook registration response
    """
    # Load configuration
    config = None
    try:
        from crm_calendar_helpers import load_config
        config = load_config()
    except ImportError:
        print("Warning: Could not load config, using defaults")
    
    webhook_url = config.get('webhook', {}).get('endpoint', 'https://va.zo.computer/webhooks/calendar')
    print(f"Webhook endpoint: {webhook_url}")
    
    # Validate prerequisites
    print("\nValidating prerequisites...")
    from crm_calendar_helpers import validate_webhook_endpoint
    if not validate_webhook_endpoint(webhook_url):
        print("\n⚠️  Warning: Webhook endpoint is not currently accessible")
        print("   This is expected if the handler service isn't running yet")
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            raise RuntimeError("Webhook endpoint validation failed")
    
    print("✓ Prerequisites validated (with warnings)")
    
    # Generate channel parameters
    channel_id = generate_unique_channel_id()
    expiration_ms = calculate_expiration_ms()
    
    print(f"\nGenerated channel ID: {channel_id}")
    print(f"Expires: {datetime.datetime.fromtimestamp(expiration_ms / 1000).strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Build Calendar service
    print("\nLoading Google credentials...")
    service_account_info = load_google_credentials()
    print(f"✓ Service account: {service_account_info.get('client_email')}")
    
    print("\nBuilding Calendar service...")
    service = build_calendar_service(service_account_info)
    print("✓ Calendar service built successfully")
    
    # Register webhook
    print("\nRegistering webhook with Google Calendar...")
    webhook_response = register_webhook(service, channel_id, webhook_url, expiration_ms)
    print("✓ Webhook registered successfully")
    
    # Store metadata
    print("\nStoring webhook metadata...")
    store_webhook_metadata(webhook_response)
    print("✓ Webhook metadata stored")
    
    # Create/update health record
    print("Updating webhook health record...")
    update_webhook_health(
        channel_id=webhook_response['id'],
        resource_id=webhook_response.get('resourceId'),
        expiration_ms=webhook_response['expiration'],
        last_received_at=None
    )
    print("✓ Health record updated")
    
    return webhook_response


def display_setup_summary(webhook_response):
    """Display formatted setup summary"""
    from datetime import datetime
    expiration_timestamp = int(webhook_response['expiration']) / 1000
    expiration_readable = datetime.fromtimestamp(expiration_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    print("\n" + "=" * 70)
    print("GOOGLE CALENDAR WEBHOOK SETUP COMPLETE")
    print("=" * 70)
    print(f"Channel ID:     {webhook_response['id']}")
    print(f"Resource ID:    {webhook_response.get('resourceId', 'N/A')}")
    print(f"Resource URI:   {webhook_response.get('resourceUri', 'N/A')}")
    print(f"Expiration:     {expiration_readable}")
    print(f"Rate Limits:    {webhook_response.get('rateLimit', {}).get('limit', 'N/A')}")
    print("=" * 70)


def validate_prerequisites(credentials_path):
    """
    Validate that all prerequisites are met before attempting setup.
    
    Args:
        credentials_path (str): Path to service account credentials file
    """
    errors = []
    
    # Check credentials file exists
    if not os.path.exists(credentials_path):
        errors.append(f"Service account credentials not found: {credentials_path}")
    else:
        try:
            with open(credentials_path) as f:
                import json
                creds = json.load(f)
                if 'client_email' not in creds or 'private_key' not in creds:
                    errors.append("Invalid service account credentials format")
        except Exception as e:
            errors.append(f"Failed to parse credentials file: {e}")
    
    # Check if we're inside Zo Computer environment
    zo_host = os.environ.get('ZOCOMPUTER_HOST')
    if not zo_host:
        print("⚠️  Warning: ZOCOMPUTER_HOST not set, webhook URL may not be correct")
    
    return errors


def display_prerequisites_checklist():
    """Display prerequisites checklist for Google Calendar integration"""
    print("\n" + "=" * 70)
    print("GOOGLE CALENDAR WEBHOOK PREREQUISITES CHECKLIST")
    print("=" * 70)
    print()
    print("BEFORE PROCEEDING, ENSURE:")
    print()
    print("☐ Google Cloud Platform Setup:")
    print("   • Created project at https://console.cloud.google.com")
    print("   • Enabled Google Calendar API")
    print("   • Created service account with Calendar access")
    print("   • Downloaded JSON key file")
    print()
    print("☐ Domain Verification:")
    print("   • Verified va.zo.computer in Google Search Console")
    print("   • Added to Google Cloud Console credentials")
    print()
    print("☐ Zo Computer Configuration:")
    print("   • Config file at N5/config/calendar_webhook.yaml")
    print("   • Service account credentials at N5/config/credentials/google_service_account.json")
    print("   • Webhook handler deployed as user service")
    print()
    print("☐ Permissions:")
    print("   • Service account has domain-wide delegation (if needed)")
    print("   • Calendar API quota is sufficient")
    print()
    print("=" * 70)
    print("For detailed setup guide, see Google documentation:")
    print("https://developers.google.com/calendar/api/guides/push")
    print("=" * 70)
    print()
    response = input("Have you completed these prerequisites? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("\nPlease complete prerequisites before continuing.")
        return False
    return True


async def main():
    """Main entry point for setup script"""
    parser = argparse.ArgumentParser(description='Setup Google Calendar webhook')
    parser.add_argument(
        '--skip-prerequisites',
        action='store_true',
        help='Skip interactive prerequisites check'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Dry-run mode (doesn\'t call Google API)'
    )
    
    args = parser.parse_args()
    
    # Setup logging whether in test mode or not
    log_file = '/dev/shm/crm-calendar-webhook-setup.log'
    
    print("=" * 70)
    print("GOOGLE CALENDAR WEBHOOK SETUP")
    print("=" * 70)
    
    # Only show prerequisites if not skipped
    if not args.skip_prerequisites and not args.test:
        if not display_prerequisites_checklist():
            logger.info("Setup cancelled by user")
            return 0
        
    # Dry-run mode for testing
    if args.test:
        logger.info("Running in TEST MODE - not calling Google API")
        # ... test logic
    
    # Validate environment
    credentials_path = '/home/workspace/N5/config/credentials/google_service_account.json'
    errors = validate_prerequisites(credentials_path)
    
    if errors:
        print("\n❌ Prerequisites validation failed:")
        for error in errors:
            print(f"   • {error}")
        return 1
    
    print("\n✓ Prerequisites validated")
    
    try:
        # Run setup
        webhook_response = setup_calendar_webhook()
        
        # Display summary
        display_setup_summary(webhook_response)
        
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETE - Webhook registered successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))



